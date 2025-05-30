# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

The AWS Athena MCP Server team takes security bugs seriously. We appreciate your efforts to responsibly disclose your findings, and will make every effort to acknowledge your contributions.

### How to Report a Security Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@your-org.com**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the following information in your report:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours
- **Initial Assessment**: We will provide an initial assessment within 5 business days
- **Regular Updates**: We will keep you informed of our progress throughout the process
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days
- **Disclosure**: We will work with you on coordinated disclosure timing

## Security Best Practices

### For Users

1. **AWS Credentials**
   - Never commit AWS credentials to version control
   - Use IAM roles when possible (EC2, Lambda, ECS)
   - Rotate credentials regularly
   - Follow the principle of least privilege

2. **Environment Variables**
   - Store sensitive configuration in environment variables
   - Use AWS Secrets Manager or Parameter Store for production
   - Never log sensitive environment variables

3. **Network Security**
   - Use VPC endpoints when running in AWS
   - Implement proper security groups and NACLs
   - Consider using AWS PrivateLink for enhanced security

4. **Query Security**
   - Validate and sanitize all SQL inputs
   - Use parameterized queries when possible
   - Implement query complexity limits
   - Monitor for suspicious query patterns

### For Developers

1. **Input Validation**
   - Validate all user inputs
   - Sanitize SQL queries to prevent injection
   - Implement rate limiting
   - Use type hints and validation libraries

2. **Error Handling**
   - Don't expose sensitive information in error messages
   - Log security events appropriately
   - Implement proper exception handling

3. **Dependencies**
   - Keep dependencies up to date
   - Regularly scan for known vulnerabilities
   - Use dependency pinning in production

4. **Testing**
   - Include security tests in your test suite
   - Test error conditions and edge cases
   - Perform regular security audits

## Known Security Considerations

### SQL Injection Prevention

This project implements several measures to prevent SQL injection:

- Input validation on all query parameters
- Query sanitization before execution
- Use of AWS Athena's built-in protections
- Parameterized query support (where applicable)

### AWS Permissions

The service requires the following AWS permissions:

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
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": "*"
        }
    ]
}
```

### Data Privacy

- Query results may contain sensitive data
- Implement appropriate access controls
- Consider data encryption at rest and in transit
- Follow your organization's data governance policies

## Security Updates

Security updates will be released as patch versions and announced through:

- GitHub Security Advisories
- Release notes
- Email notifications (if you've subscribed)

## Acknowledgments

We would like to thank the following individuals for their responsible disclosure of security vulnerabilities:

- (None yet - be the first!)

## Contact

For any security-related questions or concerns, please contact:

- **Email**: security@your-org.com
- **PGP Key**: [Link to public key if available]

---

This security policy is based on industry best practices and will be updated as needed to reflect the current threat landscape and project requirements. 