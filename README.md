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
# From PyPI with uv (recommended for Claude Desktop)
uv tool install aws-athena-mcp

# From PyPI with pip
pip install aws-athena-mcp

# Or from source
git clone https://github.com/ColeMurray/aws-athena-mcp
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
# Start the MCP server (if installed with uv tool install)
aws-athena-mcp

# Or run directly with uv (without installing)
uv tool run aws-athena-mcp

# Or run directly with uvx (without installing)
uvx aws-athena-mcp

# Or run directly with Python
python -m athena_mcp.server
```

That's it! The server is now running and ready to accept MCP connections.

## 🤖 Claude Desktop Integration

To use this MCP server with Claude Desktop:

### 1. Install Claude Desktop
Download and install [Claude Desktop](https://claude.ai/download) if you haven't already.

### 2. Configure Claude Desktop
Add the following configuration to your `claude_desktop_config.json`:

**Location of config file:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration (Option 1 - Using uvx - Recommended):**
```json
{
  "mcpServers": {
    "aws-athena-mcp": {
      "command": "uvx",
      "args": [
        "aws-athena-mcp"
      ],
      "env": {
        "ATHENA_S3_OUTPUT_LOCATION": "s3://your-bucket/athena-results/",
        "AWS_REGION": "us-east-1",
        "ATHENA_WORKGROUP": "primary",
        "ATHENA_TIMEOUT_SECONDS": "60"
      }
    }
  }
}
```

**Configuration (Option 2 - Using installed tool):**
```json
{
  "mcpServers": {
    "aws-athena-mcp": {
      "command": "aws-athena-mcp",
      "env": {
        "ATHENA_S3_OUTPUT_LOCATION": "s3://your-bucket/athena-results/",
        "AWS_REGION": "us-east-1",
        "ATHENA_WORKGROUP": "primary",
        "ATHENA_TIMEOUT_SECONDS": "60"
      }
    }
  }
}
```

**Configuration (Option 3 - Using uv tool run):**
```json
{
  "mcpServers": {
    "aws-athena-mcp": {
      "command": "uv",
      "args": [
        "tool",
        "run",
        "aws-athena-mcp"
      ],
      "env": {
        "ATHENA_S3_OUTPUT_LOCATION": "s3://your-bucket/athena-results/",
        "AWS_REGION": "us-east-1",
        "ATHENA_WORKGROUP": "primary",
        "ATHENA_TIMEOUT_SECONDS": "60"
      }
    }
  }
}
```

**Recommended approach:** Use Option 1 (uvx) for the most common MCP setup pattern. Option 2 (installed tool) offers better performance as it avoids package resolution on each startup.

### 3. Set AWS Credentials
Configure your AWS credentials using one of these methods:

```bash
# Method 1: Environment variables (add to your shell profile)
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key

# Method 2: AWS CLI
aws configure

# Method 3: AWS Profile
export AWS_PROFILE=your-profile
```

### 4. Restart Claude Desktop
Restart Claude Desktop to load the new MCP server configuration.

### 5. Verify Connection
In Claude Desktop, you should now be able to:
- Execute SQL queries against your Athena databases
- List tables and describe schemas
- Get query results and status

**Example conversation:**
```
You: "List all tables in my 'analytics' database"
Claude: I'll help you list the tables in your analytics database using the Athena MCP server.
[Uses list_tables tool]
```

### 🛠️ Automated Setup (Alternative)

For easier setup, you can use the included setup script:

```bash
# Clone the repository
git clone https://github.com/ColeMurray/aws-athena-mcp
cd aws-athena-mcp

# Run the setup script
python scripts/setup_claude_desktop.py
```

The script will:
- Check if uv is installed
- Guide you through configuration
- Update your Claude Desktop config file
- Verify AWS credentials
- Provide next steps

You can also copy the example configuration:
```bash
cp examples/claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
# Then edit the file to add your S3 bucket and AWS settings
```

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

## 🔒 Security

### Environment Variables

**⚠️ NEVER commit credentials to version control!**

Use the provided example file to set up your environment:

```bash
# Copy the example file
cp examples/environment_variables.example .env

# Edit with your values
nano .env

# Make sure .env is in .gitignore (it already is)
echo ".env" >> .gitignore
```

### AWS Credentials Best Practices

1. **Use IAM Roles** (recommended for production):
   ```bash
   # No credentials needed - uses instance/container role
   export ATHENA_S3_OUTPUT_LOCATION=s3://your-bucket/results/
   ```

2. **Use AWS CLI profiles** (recommended for development):
   ```bash
   aws configure --profile athena-mcp
   export AWS_PROFILE=athena-mcp
   ```

3. **Use temporary credentials** when possible:
   ```bash
   aws sts assume-role --role-arn arn:aws:iam::123456789012:role/AthenaRole \
     --role-session-name athena-mcp-session
   ```

4. **Avoid long-term access keys** in environment variables

### Required AWS Permissions

Your AWS credentials need these minimum permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "athena:StartQueryExecution",
        "athena:GetQueryExecution", 
        "athena:GetQueryResults",
        "athena:ListWorkGroups",
        "athena:GetWorkGroup"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket/athena-results/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::your-bucket"
    },
    {
      "Effect": "Allow",
      "Action": [
        "glue:GetDatabase",
        "glue:GetDatabases",
        "glue:GetTable",
        "glue:GetTables"
      ],
      "Resource": "*"
    }
  ]
}
```

### SQL Injection Protection

The server includes built-in SQL injection protection:

- **Query validation** - Dangerous patterns are blocked
- **Input sanitization** - Database/table names are validated
- **Query size limits** - Prevents resource exhaustion
- **Parameterized queries** - When possible

### Network Security

For production deployments:

- Use VPC endpoints for AWS services
- Restrict network access to the MCP server
- Use TLS for all communications
- Monitor and log all queries

### Monitoring and Auditing

Enable CloudTrail logging for Athena:

```json
{
  "eventVersion": "1.05",
  "userIdentity": {...},
  "eventTime": "2024-01-01T12:00:00Z",
  "eventSource": "athena.amazonaws.com",
  "eventName": "StartQueryExecution",
  "resources": [...]
}
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
git clone https://github.com/ColeMurray/aws-athena-mcp
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

- **Issues**: [GitHub Issues](https://github.com/ColeMurray/aws-athena-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ColeMurray/aws-athena-mcp/discussions)
- **Documentation**: [docs/](docs/)

---

**Made with ❤️ for the MCP community**