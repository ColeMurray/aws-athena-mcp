# API Reference

This document provides detailed information about the MCP tools available in the AWS Athena MCP Server.

## Query Execution Tools

### `run_query`

Execute SQL queries against AWS Athena.

**Parameters:**
- `database` (string, required): The Athena database name
- `query` (string, required): The SQL query to execute
- `max_rows` (integer, optional): Maximum number of rows to return (default: 1000)

**Returns:**
- On success: `QueryResult` object with query results
- On timeout: String containing the query execution ID for later retrieval

**Example:**
```json
{
  "database": "default",
  "query": "SELECT * FROM my_table LIMIT 10",
  "max_rows": 10
}
```

### `get_status`

Check the execution status of a query.

**Parameters:**
- `query_execution_id` (string, required): The query execution ID returned by `run_query`

**Returns:**
- String describing the current query status (QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELLED)

**Example:**
```json
{
  "query_execution_id": "12345678-1234-1234-1234-123456789012"
}
```

### `get_result`

Retrieve results for a completed query.

**Parameters:**
- `query_execution_id` (string, required): The query execution ID
- `max_rows` (integer, optional): Maximum number of rows to return (default: 1000)

**Returns:**
- `QueryResult` object with query results

**Example:**
```json
{
  "query_execution_id": "12345678-1234-1234-1234-123456789012",
  "max_rows": 1000
}
```

## Schema Discovery Tools

### `list_tables`

List all tables in a specified database with optional search filtering.

**Parameters:**
- `database` (string, required): The Athena database name
- `search` (string, optional): Optional search string to filter table names

**Returns:**
- JSON string containing a `DatabaseInfo` object with table information

**Example:**
```json
{
  "database": "default"
}
```

**Example with search filter:**
```json
{
  "database": "analytics",
  "search": "user"
}
```

### `describe_table`

Get detailed schema information for a specific table.

**Parameters:**
- `database` (string, required): The Athena database name
- `table_name` (string, required): The name of the table to describe

**Returns:**
- JSON string containing a `TableInfo` object with detailed table schema

**Example:**
```json
{
  "database": "default",
  "table_name": "my_table"
}
```

## Data Models

### QueryResult

The `QueryResult` object returned by successful queries contains:

```json
{
  "query_execution_id": "string",
  "columns": ["col1", "col2", "..."],
  "rows": [
    {"col1": "value1", "col2": "value2", "..."}
  ],
  "bytes_scanned": 0,
  "execution_time_ms": 0
}
```

### QueryStatus

The `QueryStatus` object returned by status checks contains:

```json
{
  "query_execution_id": "string",
  "state": "QUEUED|RUNNING|SUCCEEDED|FAILED|CANCELLED",
  "state_change_reason": "string",
  "bytes_scanned": 0,
  "execution_time_ms": 0
}
```

### DatabaseInfo

The `DatabaseInfo` object returned by `list_tables` contains:

```json
{
  "database": "string",
  "tables": ["table1", "table2", "..."],
  "table_count": 0
}
```

### TableInfo

The `TableInfo` object returned by `describe_table` contains:

```json
{
  "database": "string",
  "table_name": "string",
  "columns": [
    {
      "name": "string",
      "type": "string",
      "comment": "string"
    }
  ]
}
```

### ErrorResponse

Error responses follow this standard format:

```json
{
  "error": "string",
  "code": "string",
  "query_execution_id": "string"
}
```

## Error Handling

All tools may return error messages in case of failures:

- **Configuration errors**: Missing or invalid configuration
- **AWS credential errors**: Invalid or insufficient AWS permissions
- **Query errors**: SQL syntax errors or execution failures
- **Timeout errors**: Queries that exceed the configured timeout
- **Validation errors**: Invalid database or table names

Error responses are returned as JSON objects with descriptive error messages and error codes.

## Rate Limits and Quotas

Be aware of AWS Athena service limits:

- **Query concurrency**: Default limit of 20 concurrent queries per workgroup
- **Query timeout**: Configurable via `ATHENA_TIMEOUT_SECONDS` (default: 60 seconds)
- **Result size**: Large result sets may be truncated based on `max_rows` parameter
- **S3 permissions**: Ensure proper permissions for the output location
- **Glue API limits**: Schema discovery tools use AWS Glue APIs which have their own rate limits

For more information, see the [AWS Athena Service Quotas](https://docs.aws.amazon.com/athena/latest/ug/service-limits.html) and [AWS Glue Service Quotas](https://docs.aws.amazon.com/glue/latest/dg/service-limits.html) documentation. 