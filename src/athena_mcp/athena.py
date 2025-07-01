"""
AWS Athena client wrapper.

Simple, clean wrapper around boto3 Athena client with async support.
"""

import asyncio
import logging
import re
import time
from typing import Optional, Union

import boto3
from botocore.exceptions import ClientError

from .config import Config
from .models import DatabaseInfo, QueryRequest, QueryResult, QueryState, QueryStatus, TableInfo

# Set up logging
logger = logging.getLogger(__name__)


class AthenaError(Exception):
    """Simple Athena error with code."""

    def __init__(
        self, message: str, code: str = "ATHENA_ERROR", query_execution_id: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.query_execution_id = query_execution_id


class QueryValidator:
    """Validates and sanitizes SQL queries to prevent injection attacks."""

    # Dangerous SQL patterns that should be blocked
    DANGEROUS_PATTERNS = [
        r";\s*(drop|delete|truncate|alter|create|insert|update)\s+",
        r"--\s*",  # SQL comments
        r"/\*.*?\*/",  # Multi-line comments
        r"xp_cmdshell",  # Command execution
        r"sp_executesql",  # Dynamic SQL execution
        r"exec\s*\(",  # Execute statements
        r"union\s+.*select",  # Union-based injection
        r"information_schema",  # Schema information access
        r"sys\.",  # System table access
    ]

    @classmethod
    def validate_query(cls, query: str) -> None:
        """
        Validate SQL query for potential injection attacks.

        Args:
            query: SQL query to validate

        Raises:
            ValueError: If query contains dangerous patterns
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        query_lower = query.lower()

        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE | re.DOTALL):
                logger.warning(f"Potentially dangerous SQL pattern detected: {pattern}")
                raise ValueError(f"Query contains potentially dangerous pattern: {pattern}")

        # Additional validation
        if len(query) > 100000:  # 100KB limit
            raise ValueError("Query is too large (max 100KB)")

        logger.debug(f"Query validation passed for query of length {len(query)}")

    @classmethod
    def sanitize_identifier(cls, identifier: str) -> str:
        """
        Sanitize database/table identifiers.

        Args:
            identifier: Database or table name

        Returns:
            Sanitized identifier

        Raises:
            ValueError: If identifier is invalid
        """
        if not identifier or not identifier.strip():
            raise ValueError("Identifier cannot be empty")

        # Remove any non-alphanumeric characters except underscores and hyphens
        sanitized = re.sub(r"[^a-zA-Z0-9_-]", "", identifier.strip())

        if not sanitized:
            raise ValueError("Identifier contains only invalid characters")

        if len(sanitized) > 255:
            raise ValueError("Identifier is too long (max 255 characters)")

        logger.debug(f"Sanitized identifier: {identifier} -> {sanitized}")
        return sanitized


class AthenaClient:
    """Simple AWS Athena client wrapper."""

    def __init__(self, config: Config):
        self.config = config

        # Initialize boto3 client
        session = boto3.Session(region_name=config.aws_region)
        self.client = session.client("athena")

        logger.info(f"Initialized Athena client for region: {config.aws_region}")

    async def execute_query(self, request: QueryRequest) -> Union[QueryResult, str]:
        """
        Execute a query and return results or execution ID if timeout.

        Returns:
            QueryResult if completed within timeout, otherwise query_execution_id string
        """
        logger.info(f"Executing query in database: {request.database}")
        logger.debug(f"Query: {request.query[:200]}...")  # Log first 200 chars

        try:
            # Validate and sanitize inputs
            QueryValidator.validate_query(request.query)
            sanitized_database = QueryValidator.sanitize_identifier(request.database)

            # Start query execution
            start_params = {
                "QueryString": request.query,
                "QueryExecutionContext": {"Database": sanitized_database},
                "ResultConfiguration": {"OutputLocation": self.config.s3_output_location},
            }

            if self.config.athena_workgroup:
                start_params["WorkGroup"] = self.config.athena_workgroup
                logger.debug(f"Using workgroup: {self.config.athena_workgroup}")

            response = self.client.start_query_execution(**start_params)
            query_execution_id = response["QueryExecutionId"]

            logger.info(f"Started query execution: {query_execution_id}")

            # Wait for completion with timeout
            if await self._wait_for_completion(query_execution_id):
                logger.info(f"Query completed successfully: {query_execution_id}")
                query_result: QueryResult = await self.get_query_results(
                    query_execution_id, request.max_rows
                )
                return query_result
            else:
                # Timeout - return execution ID for later retrieval
                logger.warning(f"Query timed out: {query_execution_id}")
                execution_id: str = query_execution_id
                return execution_id

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "UNKNOWN")
            logger.error(f"AWS Athena error: {error_code} - {str(e)}")
            raise AthenaError(str(e), error_code)
        except Exception as e:
            logger.error(f"Unexpected error during query execution: {str(e)}")
            raise

    async def get_query_status(self, query_execution_id: str) -> QueryStatus:
        """Get the status of a query execution."""
        logger.debug(f"Getting status for query: {query_execution_id}")

        try:
            response = self.client.get_query_execution(QueryExecutionId=query_execution_id)
            execution = response.get("QueryExecution", {})

            status = execution.get("Status", {})
            statistics = execution.get("Statistics", {})

            query_status = QueryStatus(
                query_execution_id=query_execution_id,
                state=QueryState(status.get("State", "UNKNOWN")),
                state_change_reason=status.get("StateChangeReason"),
                bytes_scanned=statistics.get("DataScannedInBytes", 0),
                execution_time_ms=statistics.get("EngineExecutionTimeInMillis", 0),
            )

            logger.debug(f"Query {query_execution_id} status: {query_status.state}")
            return query_status

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "UNKNOWN")
            logger.error(f"Error getting query status: {error_code} - {str(e)}")
            raise AthenaError(str(e), error_code, query_execution_id)

    async def get_query_results(self, query_execution_id: str, max_rows: int = 1000) -> QueryResult:
        """Get results for a completed query."""
        logger.info(f"Getting results for query: {query_execution_id}, max_rows: {max_rows}")

        try:
            # Check status first
            status = await self.get_query_status(query_execution_id)

            if status.state in [QueryState.RUNNING, QueryState.QUEUED]:
                raise AthenaError("Query is still running", "QUERY_RUNNING", query_execution_id)

            if status.state == QueryState.FAILED:
                reason = status.state_change_reason or "Query failed"
                logger.error(f"Query failed: {query_execution_id} - {reason}")
                raise AthenaError(reason, "QUERY_FAILED", query_execution_id)

            if status.state != QueryState.SUCCEEDED:
                logger.error(f"Query in unexpected state: {status.state}")
                raise AthenaError(
                    f"Query in unexpected state: {status.state}",
                    "UNEXPECTED_STATE",
                    query_execution_id,
                )

            # Get results
            response = self.client.get_query_results(
                QueryExecutionId=query_execution_id, MaxResults=max_rows
            )

            result_set = response.get("ResultSet", {})

            # Extract columns
            column_info = result_set.get("ResultSetMetadata", {}).get("ColumnInfo", [])
            columns = [col.get("Name", "") for col in column_info]

            # Extract rows (skip header for SELECT queries)
            rows_data = result_set.get("Rows", [])
            start_index = 1 if len(rows_data) > 0 and columns else 0

            rows = []
            for row_data in rows_data[start_index:]:
                row = {}
                data_list = row_data.get("Data", [])
                for i, data in enumerate(data_list):
                    if i < len(columns):
                        row[columns[i]] = data.get("VarCharValue")
                rows.append(row)

            result = QueryResult(
                query_execution_id=query_execution_id,
                columns=columns,
                rows=rows,
                bytes_scanned=status.bytes_scanned,
                execution_time_ms=status.execution_time_ms,
            )

            logger.info(f"Retrieved {len(rows)} rows for query: {query_execution_id}")
            return result

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "UNKNOWN")
            logger.error(f"Error getting query results: {error_code} - {str(e)}")
            raise AthenaError(str(e), error_code, query_execution_id)

    async def list_tables(self, database: str, search: Optional[str] = None) -> DatabaseInfo:
        """List all tables in a database."""
        logger.info(f"Listing tables in database: {database}")

        sanitized_database = QueryValidator.sanitize_identifier(database)

        if search:
            search_str = f"LIKE '*{search.lower()}*'"
        else:
            search_str = ""

        request = QueryRequest(
            database=sanitized_database, query=f"SHOW TABLES {search_str}", max_rows=1000
        )

        result = await self.execute_query(request)

        if isinstance(result, str):
            # Query timed out
            logger.error(f"SHOW TABLES query timed out for database: {database}")
            raise AthenaError("SHOW TABLES query timed out", "TIMEOUT", result)

        # Extract table names
        tables = [row.get("tab_name", "") for row in result.rows if "tab_name" in row]

        database_info = DatabaseInfo(
            database=sanitized_database, tables=tables, table_count=len(tables)
        )

        logger.info(f"Found {len(tables)} tables in database: {database}")
        return database_info

    async def describe_table(self, database: str, table_name: str) -> TableInfo:
        """Get schema information for a specific table."""
        logger.info(f"Describing table: {database}.{table_name}")

        sanitized_database = QueryValidator.sanitize_identifier(database)
        sanitized_table = QueryValidator.sanitize_identifier(table_name)

        request = QueryRequest(
            database=sanitized_database, query=f"DESCRIBE {sanitized_table}", max_rows=1000
        )

        result = await self.execute_query(request)

        if isinstance(result, str):
            # Query timed out
            logger.error(f"DESCRIBE query timed out for table: {database}.{table_name}")
            raise AthenaError(f"DESCRIBE {table_name} query timed out", "TIMEOUT", result)

        # Extract column information
        columns = []
        for row in result.rows:
            columns.append(
                {
                    "name": row.get("col_name", ""),
                    "type": row.get("data_type", ""),
                    "comment": row.get("comment", ""),
                }
            )

        table_info = TableInfo(
            database=sanitized_database, table_name=sanitized_table, columns=columns
        )

        logger.info(f"Described table {database}.{table_name} with {len(columns)} columns")
        return table_info

    async def _wait_for_completion(self, query_execution_id: str) -> bool:
        """
        Wait for query completion with timeout.

        Returns:
            True if completed successfully, False if timed out
        """
        timeout_seconds = self.config.timeout_seconds
        start_time = time.time()

        logger.debug(
            f"Waiting for query completion: {query_execution_id}, timeout: {timeout_seconds}s"
        )

        while time.time() - start_time < timeout_seconds:
            try:
                response = self.client.get_query_execution(QueryExecutionId=query_execution_id)
                state = response.get("QueryExecution", {}).get("Status", {}).get("State")

                if state == QueryState.SUCCEEDED:
                    logger.debug(f"Query completed successfully: {query_execution_id}")
                    return True

                if state in [QueryState.FAILED, QueryState.CANCELLED]:
                    reason = (
                        response.get("QueryExecution", {})
                        .get("Status", {})
                        .get("StateChangeReason", "Query failed")
                    )
                    logger.error(f"Query failed: {query_execution_id} - {reason}")
                    raise AthenaError(reason, "QUERY_FAILED", query_execution_id)

                # Wait before checking again
                await asyncio.sleep(1)

            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code", "UNKNOWN")
                logger.error(f"Error waiting for query completion: {error_code} - {str(e)}")
                raise AthenaError(str(e), error_code, query_execution_id)

        # Timeout reached
        logger.warning(f"Query timed out after {timeout_seconds}s: {query_execution_id}")
        return False
