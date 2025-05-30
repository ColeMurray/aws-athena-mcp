# AWS Athena MCP Server

A simple, clean MCP (Model Context Protocol) server for AWS Athena integration. Execute SQL queries, discover schemas, and manage query executions through a standardized interface.

## ✨ Features

- **Simple Setup** - Get running in under 5 minutes
- **Clean Architecture** - Modular, well-tested, easy to understand
- **Essential Tools** - Query execution and schema discovery
- **Type Safe** - Full type hints and Pydantic models
- **Async Support** - Built for performance with async/await
- **Good Defaults** - Works out of the box with minimal configuration

## 🚀 Quick Start

### 1. Install

```bash
# From PyPI (when published)
pip install aws-athena-mcp

# Or from source
git clone https://github.com/your-org/aws-athena-mcp
cd aws-athena-mcp
pip install -e .
```

### 2. Configure

Set the required environment variables:

```bash
# Required
export ATHENA_S3_OUTPUT_LOCATION=s3://your-bucket/athena-results/

# Optional (with defaults)
export AWS_REGION=us-east-1
export ATHENA_WORKGROUP=primary
export ATHENA_TIMEOUT_SECONDS=60
```

### 3. Run

```bash
# Start the MCP server
athena-mcp-server

# Or run directly
python -m athena_mcp.server
```

That's it! The server is now running and ready to accept MCP connections.

## 🔧 Configuration

The server uses environment variables for configuration:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ATHENA_S3_OUTPUT_LOCATION` | ✅ | - | S3 path for query results |
| `AWS_REGION` | ❌ | `us-east-1` | AWS region |
| `ATHENA_WORKGROUP` | ❌ | `None` | Athena workgroup |
| `ATHENA_TIMEOUT_SECONDS` | ❌ | `60` | Query timeout |

### AWS Credentials

Configure AWS credentials using any of these methods:

```bash
# Method 1: Environment variables
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key

# Method 2: AWS CLI
aws configure

# Method 3: AWS Profile
export AWS_PROFILE=your-profile

# Method 4: IAM roles (for EC2/Lambda)
# No configuration needed
```

## 🛠️ Available Tools

The server provides these MCP tools:

### Query Execution

- **`run_query`** - Execute SQL queries against Athena
- **`get_status`** - Check query execution status
- **`get_result`** - Get results for completed queries

### Schema Discovery

- **`list_tables`** - List all tables in a database
- **`describe_table`** - Get detailed table schema

## 📖 Usage Examples

### Basic Query Execution

```python
# Using the MCP client (pseudo-code)
result = await mcp_client.call_tool("run_query", {
    "database": "default",
    "query": "SELECT * FROM my_table LIMIT 10",
    "max_rows": 10
})
```

### Schema Discovery

```python
# List tables
tables = await mcp_client.call_tool("list_tables", {
    "database": "default"
})

# Describe a table
schema = await mcp_client.call_tool("describe_table", {
    "database": "default",
    "table_name": "my_table"
})
```

### Handling Timeouts

```python
# Long-running query
result = await mcp_client.call_tool("run_query", {
    "database": "default",
    "query": "SELECT COUNT(*) FROM large_table"
})

if "query_execution_id" in result:
    # Query timed out, check status later
    status = await mcp_client.call_tool("get_status", {
        "query_execution_id": result["query_execution_id"]
    })
```

## 🧪 Testing

Test your configuration:

```bash
# Test configuration and AWS connection
python scripts/test_connection.py

# Run the test suite
pytest

# Run with coverage
pytest --cov=athena_mcp
```

## 🏗️ Development

### Setup Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/your-org/aws-athena-mcp
cd aws-athena-mcp
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests
isort src tests

# Type checking
mypy src
```

### Project Structure

```
aws-athena-mcp/
├── src/athena_mcp/          # Main package
│   ├── server.py            # MCP server
│   ├── athena.py            # AWS Athena client
│   ├── config.py            # Configuration
│   └── models.py            # Data models
├── src/tools/               # MCP tools
│   ├── query.py             # Query tools
│   └── schema.py            # Schema tools
├── tests/                   # Test suite
├── examples/                # Usage examples
├── scripts/                 # Utility scripts
└── docs/                    # Documentation
```

### Adding New Tools

1. Create tool functions in `src/tools/`
2. Register them in the appropriate module
3. Add tests in `tests/`
4. Update documentation

Example:

```python
# In src/tools/query.py
def register_query_tools(mcp, athena_client):
    @mcp.tool()
    async def my_new_tool(param: str) -> str:
        """My new tool description."""
        # Implementation here
        return result
```

## 🔍 Troubleshooting

### Common Issues

**Configuration Error**
```
❌ Configuration error: ATHENA_S3_OUTPUT_LOCATION environment variable is required
```
**Solution**: Set the required environment variable:
```bash
export ATHENA_S3_OUTPUT_LOCATION=s3://your-bucket/results/
```

**AWS Credentials Error**
```
❌ AWS credentials error: AWS credentials not found
```
**Solution**: Configure AWS credentials (see Configuration section)

**Permission Denied**
```
❌ AWS credentials error: AWS credentials are invalid or insufficient permissions
```
**Solution**: Ensure your AWS credentials have these permissions:
- `athena:StartQueryExecution`
- `athena:GetQueryExecution`
- `athena:GetQueryResults`
- `athena:ListWorkGroups`
- `s3:GetObject`, `s3:PutObject` on your S3 bucket

### Debug Mode

Enable debug logging:

```bash
export PYTHONPATH=src
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from athena_mcp.server import main
main()
"
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions welcome! Please read our [contributing guidelines](CONTRIBUTING.md) and:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/aws-athena-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/aws-athena-mcp/discussions)
- **Documentation**: [docs/](docs/)

---

**Made with ❤️ for the MCP community** 