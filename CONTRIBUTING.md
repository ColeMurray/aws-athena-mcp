# Contributing to AWS Athena MCP Server

Thank you for your interest in contributing to the AWS Athena MCP Server! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- AWS CLI configured with appropriate permissions
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/aws-athena-mcp.git
   cd aws-athena-mcp
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up environment variables**
   ```bash
   export ATHENA_S3_OUTPUT_LOCATION=s3://your-test-bucket/results/
   export AWS_REGION=us-east-1
   ```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=athena_mcp --cov-report=html

# Run type checking
python -m mypy src/athena_mcp --ignore-missing-imports
```

### Test Requirements

- All new features must include tests
- Maintain minimum 80% test coverage
- Tests must pass on Python 3.9, 3.10, 3.11, and 3.12
- Use pytest for all tests

## 📝 Code Standards

### Code Style

- Follow PEP 8 style guidelines
- Use Black for code formatting: `black src/ tests/`
- Use isort for import sorting: `isort src/ tests/`
- Maximum line length: 100 characters

### Type Hints

- All public functions must have type hints
- Use `typing` module for complex types
- Run mypy with no errors: `mypy src/athena_mcp`

### Documentation

- All public functions must have docstrings
- Use Google-style docstrings
- Include examples in docstrings where helpful

## 🔧 Development Workflow

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

### Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(query): add support for parameterized queries`
- `fix(config): handle missing environment variables gracefully`
- `docs(readme): update installation instructions`

### Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** following the code standards
3. **Add tests** for new functionality
4. **Update documentation** if needed
5. **Run the full test suite** and ensure it passes
6. **Submit a pull request** with:
   - Clear description of changes
   - Link to any related issues
   - Screenshots/examples if applicable

### Pull Request Requirements

- [ ] All tests pass
- [ ] Code coverage maintained (≥80%)
- [ ] Type checking passes (mypy)
- [ ] Code formatting applied (black, isort)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (for significant changes)

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment information**
   - Python version
   - Operating system
   - AWS region
   - Package version

2. **Steps to reproduce**
   - Minimal code example
   - Expected behavior
   - Actual behavior

3. **Error messages**
   - Full stack trace
   - Relevant log output

## 💡 Feature Requests

For new features:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** and motivation
3. **Propose an implementation** approach
4. **Consider backward compatibility**

## 🔒 Security

- **Do not commit** AWS credentials or sensitive data
- **Report security vulnerabilities** privately via email
- **Follow AWS security best practices**

## 📋 Code Review Guidelines

### For Reviewers

- Check for code quality and adherence to standards
- Verify test coverage and quality
- Ensure documentation is updated
- Test the changes locally when possible
- Be constructive and respectful in feedback

### For Contributors

- Respond to feedback promptly
- Make requested changes in separate commits
- Ask questions if feedback is unclear
- Be open to suggestions and improvements

## 🏗️ Architecture Guidelines

### Design Principles

- **Simplicity**: Keep the codebase simple and readable
- **Modularity**: Separate concerns into distinct modules
- **Type Safety**: Use type hints throughout
- **Error Handling**: Provide clear, actionable error messages
- **Performance**: Consider AWS API rate limits and costs

### Adding New Tools

When adding new MCP tools:

1. Create the tool function in appropriate module
2. Add comprehensive error handling
3. Include input validation
4. Return JSON responses consistently
5. Add tests for all scenarios
6. Update documentation

## 📚 Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [AWS Athena Documentation](https://docs.aws.amazon.com/athena/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check the README and inline documentation

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AWS Athena MCP Server! 🎉 