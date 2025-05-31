"""
Query execution tools for AWS Athena MCP Server.

Simple tools for executing queries and getting results.
"""

import json
from typing import Union

from ..athena import AthenaClient, AthenaError
from ..models import QueryRequest, QueryResult


def register_query_tools(mcp, athena_client: AthenaClient):
    """Register query-related MCP tools."""

    @mcp.tool()
    async def run_query(database: str, query: str, max_rows: int = 1000) -> str:
        """
        Execute a SQL query against AWS Athena.

        Args:
            database: The Athena database to query
            query: SQL query to execute
            max_rows: Maximum number of rows to return (1-10000)

        Returns:
            JSON string with query results or execution ID if timeout
        """
        try:
            # Validate inputs
            if not database.strip():
                raise ValueError("Database name cannot be empty")
            if not query.strip():
                raise ValueError("Query cannot be empty")
            if max_rows < 1 or max_rows > 10000:
                raise ValueError("max_rows must be between 1 and 10000")

            request = QueryRequest(database=database, query=query, max_rows=max_rows)

            result = await athena_client.execute_query(request)

            if isinstance(result, QueryResult):
                return json.dumps(result.dict(), indent=2)
            else:
                # Timeout - return execution ID
                return json.dumps(
                    {
                        "query_execution_id": result,
                        "status": "timeout",
                        "message": "Query timed out, use get_status to check progress",
                    },
                    indent=2,
                )

        except AthenaError as e:
            return json.dumps(
                {"error": e.message, "code": e.code, "query_execution_id": e.query_execution_id},
                indent=2,
            )
        except Exception as e:
            return json.dumps({"error": str(e), "code": "INVALID_REQUEST"}, indent=2)

    @mcp.tool()
    async def get_status(query_execution_id: str) -> str:
        """
        Get the current status of a query execution.

        Args:
            query_execution_id: The query execution ID

        Returns:
            JSON string with status information
        """
        try:
            if not query_execution_id.strip():
                raise ValueError("Query execution ID cannot be empty")

            status = await athena_client.get_query_status(query_execution_id)
            return json.dumps(status.dict(), indent=2)

        except AthenaError as e:
            return json.dumps(
                {"error": e.message, "code": e.code, "query_execution_id": e.query_execution_id},
                indent=2,
            )
        except Exception as e:
            return json.dumps({"error": str(e), "code": "INVALID_REQUEST"}, indent=2)

    @mcp.tool()
    async def get_result(query_execution_id: str, max_rows: int = 1000) -> str:
        """
        Get results for a completed query.

        Args:
            query_execution_id: The query execution ID
            max_rows: Maximum number of rows to return (1-10000)

        Returns:
            JSON string with query results
        """
        try:
            if not query_execution_id.strip():
                raise ValueError("Query execution ID cannot be empty")
            if max_rows < 1 or max_rows > 10000:
                raise ValueError("max_rows must be between 1 and 10000")

            result = await athena_client.get_query_results(query_execution_id, max_rows)
            return json.dumps(result.dict(), indent=2)

        except AthenaError as e:
            return json.dumps(
                {"error": e.message, "code": e.code, "query_execution_id": e.query_execution_id},
                indent=2,
            )
        except Exception as e:
            return json.dumps({"error": str(e), "code": "INVALID_REQUEST"}, indent=2)
