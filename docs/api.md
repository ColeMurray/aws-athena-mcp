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

List all tables in a specified database.

**Parameters:**
- `database` (string, required): The Athena database name

**Returns:**
- JSON string containing an array of table names

**Example:**
```json
{
  "database": "default"
}
```

### `describe_table`

Get detailed schema information for a specific table.

**Parameters:**
- `database` (string, required): The Athena database name
- `table_name` (string, required): The name of the table to describe

**Returns:**
- JSON string containing table schema details including column names, types, and comments

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
  "query": "string",
  "database": "string",
  "state": "string",
  "state_change_reason": "string",
  "submission_date_time": "datetime",
  "completion_date_time": "datetime",
  "data_scanned_in_bytes": "integer",
  "execution_time_in_millis": "integer",
  "result_configuration": {
    "output_location": "string"
  },
  "columns": [
    {
      "name": "string",
      "type": "string"
    }
  ],
  "rows": [
    ["value1", "value2", "..."]
  ],
  "row_count": "integer"
}
```

## Error Handling

All tools may return error messages in case of failures:

- **Configuration errors**: Missing or invalid configuration
- **AWS credential errors**: Invalid or insufficient AWS permissions
- **Query errors**: SQL syntax errors or execution failures
- **Timeout errors**: Queries that exceed the configured timeout

Error responses are returned as descriptive string messages explaining the issue and potential solutions.

## Rate Limits and Quotas

Be aware of AWS Athena service limits:

- **Query concurrency**: Default limit of 20 concurrent queries per workgroup
- **Query timeout**: Configurable via `ATHENA_TIMEOUT_SECONDS` (default: 60 seconds)
- **Result size**: Large result sets may be truncated based on `max_rows` parameter
- **S3 permissions**: Ensure proper permissions for the output location

For more information, see the [AWS Athena Service Quotas](https://docs.aws.amazon.com/athena/latest/ug/service-limits.html) documentation. 