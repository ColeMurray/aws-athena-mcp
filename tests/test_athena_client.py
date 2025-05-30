"""
Tests for AthenaClient class.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from athena_mcp.athena import AthenaClient, AthenaError, QueryValidator
from athena_mcp.config import Config
from athena_mcp.models import QueryRequest, QueryState


class TestQueryValidator:
    """Test SQL query validation and sanitization."""
    
    def test_validate_query_success(self):
        """Test successful query validation."""
        valid_queries = [
            "SELECT * FROM table1",
            "SELECT col1, col2 FROM table1 WHERE col1 = 'value'",
            "SELECT COUNT(*) FROM table1 GROUP BY col1",
        ]
        
        for query in valid_queries:
            # Should not raise any exception
            QueryValidator.validate_query(query)
    
    def test_validate_query_empty(self):
        """Test validation of empty queries."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            QueryValidator.validate_query("")
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            QueryValidator.validate_query("   ")
    
    def test_validate_query_dangerous_patterns(self):
        """Test detection of dangerous SQL patterns."""
        dangerous_queries = [
            "SELECT * FROM table1; DROP TABLE table2;",
            "SELECT * FROM table1 -- comment",
            "SELECT * FROM table1 /* comment */",
            "SELECT * FROM table1 UNION SELECT * FROM users",
            "SELECT * FROM information_schema.tables",
            "SELECT * FROM sys.tables",
        ]
        
        for query in dangerous_queries:
            with pytest.raises(ValueError, match="dangerous pattern"):
                QueryValidator.validate_query(query)
    
    def test_validate_query_too_large(self):
        """Test validation of oversized queries."""
        large_query = "SELECT * FROM table1 WHERE col1 = '" + "x" * 100000 + "'"
        
        with pytest.raises(ValueError, match="Query is too large"):
            QueryValidator.validate_query(large_query)
    
    def test_sanitize_identifier_success(self):
        """Test successful identifier sanitization."""
        test_cases = [
            ("valid_table", "valid_table"),
            ("table-name", "table-name"),
            ("table123", "table123"),
            ("  table_name  ", "table_name"),
            ("table@#$%name", "tablename"),
        ]
        
        for input_id, expected in test_cases:
            result = QueryValidator.sanitize_identifier(input_id)
            assert result == expected
    
    def test_sanitize_identifier_empty(self):
        """Test sanitization of empty identifiers."""
        with pytest.raises(ValueError, match="Identifier cannot be empty"):
            QueryValidator.sanitize_identifier("")
        
        with pytest.raises(ValueError, match="Identifier cannot be empty"):
            QueryValidator.sanitize_identifier("   ")
    
    def test_sanitize_identifier_invalid_chars(self):
        """Test sanitization of identifiers with only invalid characters."""
        with pytest.raises(ValueError, match="only invalid characters"):
            QueryValidator.sanitize_identifier("@#$%")
    
    def test_sanitize_identifier_too_long(self):
        """Test sanitization of oversized identifiers."""
        long_identifier = "x" * 256
        
        with pytest.raises(ValueError, match="too long"):
            QueryValidator.sanitize_identifier(long_identifier)


class TestAthenaClient:
    """Test AthenaClient functionality."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return Config(
            s3_output_location="s3://test-bucket/results/",
            aws_region="us-east-1",
            athena_workgroup="test-workgroup",
            timeout_seconds=30
        )
    
    @pytest.fixture
    def mock_boto3_client(self):
        """Create mock boto3 client."""
        with patch('boto3.Session') as mock_session:
            mock_client = MagicMock()
            mock_session.return_value.client.return_value = mock_client
            yield mock_client
    
    def test_athena_client_init(self, config, mock_boto3_client):
        """Test AthenaClient initialization."""
        client = AthenaClient(config)
        
        assert client.config == config
        assert client.client == mock_boto3_client
    
    @pytest.mark.asyncio
    async def test_execute_query_success(self, config, mock_boto3_client):
        """Test successful query execution."""
        # Mock AWS responses
        mock_boto3_client.start_query_execution.return_value = {
            "QueryExecutionId": "test-execution-id"
        }
        
        mock_boto3_client.get_query_execution.return_value = {
            "QueryExecution": {
                "Status": {"State": "SUCCEEDED"},
                "Statistics": {
                    "DataScannedInBytes": 1024,
                    "EngineExecutionTimeInMillis": 5000
                }
            }
        }
        
        mock_boto3_client.get_query_results.return_value = {
            "ResultSet": {
                "ResultSetMetadata": {
                    "ColumnInfo": [
                        {"Name": "col1"},
                        {"Name": "col2"}
                    ]
                },
                "Rows": [
                    {"Data": [{"VarCharValue": "col1"}, {"VarCharValue": "col2"}]},  # Header
                    {"Data": [{"VarCharValue": "value1"}, {"VarCharValue": "value2"}]},
                ]
            }
        }
        
        client = AthenaClient(config)
        request = QueryRequest(
            database="test_db",
            query="SELECT * FROM test_table",
            max_rows=100
        )
        
        result = await client.execute_query(request)
        
        # Verify result
        assert hasattr(result, 'query_execution_id')
        assert result.query_execution_id == "test-execution-id"
        assert len(result.rows) == 1
        assert result.rows[0]["col1"] == "value1"
        assert result.rows[0]["col2"] == "value2"
    
    @pytest.mark.asyncio
    async def test_execute_query_timeout(self, config, mock_boto3_client):
        """Test query execution timeout."""
        # Mock AWS responses for timeout scenario
        mock_boto3_client.start_query_execution.return_value = {
            "QueryExecutionId": "test-execution-id"
        }
        
        # Always return RUNNING state to simulate timeout
        mock_boto3_client.get_query_execution.return_value = {
            "QueryExecution": {
                "Status": {"State": "RUNNING"},
                "Statistics": {}
            }
        }
        
        # Use a very short timeout to speed up the test
        config.timeout_seconds = 1
        
        client = AthenaClient(config)
        request = QueryRequest(
            database="test_db",
            query="SELECT * FROM test_table",
            max_rows=100
        )
        
        # Mock asyncio.sleep to speed up the test
        with patch('asyncio.sleep', return_value=None):
            result = await client.execute_query(request)
        
        # Should return execution ID on timeout
        assert result == "test-execution-id"
    
    @pytest.mark.asyncio
    async def test_execute_query_validation_error(self, config, mock_boto3_client):
        """Test query execution with validation error."""
        client = AthenaClient(config)
        
        # Test dangerous query
        request = QueryRequest(
            database="test_db",
            query="SELECT * FROM table1; DROP TABLE table2;",
            max_rows=100
        )
        
        with pytest.raises(ValueError, match="dangerous pattern"):
            await client.execute_query(request)
    
    @pytest.mark.asyncio
    async def test_get_query_status(self, config, mock_boto3_client):
        """Test getting query status."""
        mock_boto3_client.get_query_execution.return_value = {
            "QueryExecution": {
                "Status": {
                    "State": "SUCCEEDED",
                    "StateChangeReason": "Query completed successfully"
                },
                "Statistics": {
                    "DataScannedInBytes": 2048,
                    "EngineExecutionTimeInMillis": 3000
                }
            }
        }
        
        client = AthenaClient(config)
        status = await client.get_query_status("test-execution-id")
        
        assert status.query_execution_id == "test-execution-id"
        assert status.state == QueryState.SUCCEEDED
        assert status.bytes_scanned == 2048
        assert status.execution_time_ms == 3000
    
    @pytest.mark.asyncio
    async def test_list_tables(self, config, mock_boto3_client):
        """Test listing tables in a database."""
        # Mock the SHOW TABLES query execution
        mock_boto3_client.start_query_execution.return_value = {
            "QueryExecutionId": "test-execution-id"
        }
        
        mock_boto3_client.get_query_execution.return_value = {
            "QueryExecution": {
                "Status": {"State": "SUCCEEDED"},
                "Statistics": {}
            }
        }
        
        mock_boto3_client.get_query_results.return_value = {
            "ResultSet": {
                "ResultSetMetadata": {
                    "ColumnInfo": [{"Name": "tab_name"}]
                },
                "Rows": [
                    {"Data": [{"VarCharValue": "tab_name"}]},  # Header
                    {"Data": [{"VarCharValue": "table1"}]},
                    {"Data": [{"VarCharValue": "table2"}]},
                ]
            }
        }
        
        client = AthenaClient(config)
        database_info = await client.list_tables("test_db")
        
        assert database_info.database == "test_db"
        assert database_info.table_count == 2
        assert "table1" in database_info.tables
        assert "table2" in database_info.tables
    
    @pytest.mark.asyncio
    async def test_describe_table(self, config, mock_boto3_client):
        """Test describing a table schema."""
        # Mock the DESCRIBE query execution
        mock_boto3_client.start_query_execution.return_value = {
            "QueryExecutionId": "test-execution-id"
        }
        
        mock_boto3_client.get_query_execution.return_value = {
            "QueryExecution": {
                "Status": {"State": "SUCCEEDED"},
                "Statistics": {}
            }
        }
        
        mock_boto3_client.get_query_results.return_value = {
            "ResultSet": {
                "ResultSetMetadata": {
                    "ColumnInfo": [
                        {"Name": "col_name"},
                        {"Name": "data_type"},
                        {"Name": "comment"}
                    ]
                },
                "Rows": [
                    {"Data": [{"VarCharValue": "col_name"}, {"VarCharValue": "data_type"}, {"VarCharValue": "comment"}]},  # Header
                    {"Data": [{"VarCharValue": "id"}, {"VarCharValue": "bigint"}, {"VarCharValue": "Primary key"}]},
                    {"Data": [{"VarCharValue": "name"}, {"VarCharValue": "string"}, {"VarCharValue": "User name"}]},
                ]
            }
        }
        
        client = AthenaClient(config)
        table_info = await client.describe_table("test_db", "test_table")
        
        assert table_info.database == "test_db"
        assert table_info.table_name == "test_table"
        assert len(table_info.columns) == 2
        assert table_info.columns[0]["name"] == "id"
        assert table_info.columns[0]["type"] == "bigint"
        assert table_info.columns[1]["name"] == "name"
        assert table_info.columns[1]["type"] == "string" 