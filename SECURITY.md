# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

The AWS Athena MCP Server team takes security bugs seriously. We appreciate your efforts to responsibly disclose your findings, and will make every effort to acknowledge your contributions.

### How to Report Security Vulnerabilities

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via GitHub's private vulnerability reporting feature:

1. Go to the [Security tab](https://github.com/ColeMurray/aws-athena-mcp/security) of this repository
2. Click "Report a vulnerability"
3. Fill out the vulnerability report form with as much detail as possible

### What to Include

When reporting a vulnerability, please include:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

### Response Timeline

- **Initial Response**: Within 48 hours of receiving the report
- **Status Update**: Within 7 days with a more detailed response indicating next steps
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days

### Security Best Practices

When using the AWS Athena MCP Server, please follow these security best practices:

#### AWS Credentials
- **Use IAM roles** instead of access keys when possible
- **Rotate credentials** regularly
- **Use least privilege** - only grant necessary permissions
- **Never commit credentials** to version control

#### Network Security
- Use VPC endpoints for AWS services when possible
- Restrict network access to the MCP server
- Use TLS for all communications
- Monitor and log all network traffic

#### Query Security
- The server includes built-in SQL injection protection
- Input validation is performed on all user inputs
- Query size limits prevent resource exhaustion
- All queries are logged for audit purposes

#### Environment Security
- Use environment variables for configuration
- Never hardcode sensitive values
- Use secure secret management systems
- Regularly update dependencies

#### Monitoring and Auditing
- Enable CloudTrail logging for Athena
- Monitor query patterns for anomalies
- Set up alerts for suspicious activity
- Regularly review access logs

### Required AWS Permissions

The server requires these minimum AWS permissions:

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

### Security Features

The AWS Athena MCP Server includes several built-in security features:

- **SQL Injection Protection**: Validates queries for dangerous patterns
- **Input Sanitization**: Cleans and validates all user inputs
- **Query Size Limits**: Prevents resource exhaustion attacks
- **Audit Logging**: Comprehensive logging of all operations
- **Error Handling**: Secure error messages that don't leak sensitive information

### Contact

For questions about this security policy or to report non-security issues, please use [GitHub Issues](https://github.com/ColeMurray/aws-athena-mcp/issues). 