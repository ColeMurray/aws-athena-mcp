# Changelog

All notable changes to the AWS Athena MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive test suite for configuration module
- Type annotations throughout codebase
- Security policy and vulnerability reporting process
- Contributing guidelines for open source development
- MIT license for open source distribution

### Changed
- Improved error message consistency in configuration validation
- Enhanced documentation with security best practices

### Security
- Added input validation for all query parameters
- Implemented SQL injection prevention measures
- Added security guidelines and best practices documentation

## [1.0.0] - 2025-05-31

### Added
- Initial release of AWS Athena MCP Server
- Core MCP tools for query execution:
  - `run_query` - Execute SQL queries against Athena
  - `get_status` - Check query execution status  
  - `get_result` - Get results for completed queries
- Schema discovery tools:
  - `list_tables` - List all tables in a database
  - `describe_table` - Get detailed table schema
- Configuration management with environment variables
- AWS credentials validation
- Comprehensive error handling with structured responses
- Type-safe data models using Pydantic
- Async/await support for non-blocking operations
- Timeout handling for long-running queries
- JSON response formatting for all tools

### Technical Details
- Built on FastMCP framework for MCP protocol compliance
- Uses boto3 for AWS Athena integration
- Supports Python 3.10+ with full type hints
- Modular architecture with clean separation of concerns
- Comprehensive input validation and error handling

### Configuration
- `ATHENA_S3_OUTPUT_LOCATION` - Required S3 path for query results
- `AWS_REGION` - AWS region (default: us-east-1)
- `ATHENA_WORKGROUP` - Optional Athena workgroup
- `ATHENA_TIMEOUT_SECONDS` - Query timeout (default: 60)

### Dependencies
- `fastmcp>=0.1.0` - MCP protocol implementation
- `boto3>=1.26.0` - AWS SDK for Python
- `pydantic>=2.0.0` - Data validation and settings management

---

## Release Process

### Version Numbering
- **Major** (X.0.0): Breaking changes, major new features
- **Minor** (1.X.0): New features, backwards compatible
- **Patch** (1.0.X): Bug fixes, security updates

### Release Checklist
- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` with release notes
- [ ] Run full test suite
- [ ] Update documentation if needed
- [ ] Create GitHub release with changelog
- [ ] Publish to PyPI (when ready)

### Security Releases
Security fixes will be released as patch versions and clearly marked in the changelog with a **Security** section. 