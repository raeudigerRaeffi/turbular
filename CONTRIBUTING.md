# Contributing to Turbular

First off, thank you for considering contributing to Turbular! It's people like you that make Turbular such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct. Please report unacceptable behavior to support@turbular.dev.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include any error messages

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Include screenshots and animated GIFs in your pull request whenever possible
* Follow the Python style guide
* Include thoughtfully-worded, well-structured tests
* Document new code
* End all files with a newline

## Development Process

1. Fork the repo
2. Create a new branch from `main`
3. Make your changes
4. Run the tests
5. Push to your fork and submit a pull request

### Setting Up Development Environment

```bash
# Clone your fork
git clone git@github.com:raeudigerRaeffi/turbular.git

# Add upstream remote
git remote add upstream https://github.com/original/turbular.git

# Create development environment
docker-compose -f docker-compose.dev.yml up --build
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_file.py

# Run with coverage
pytest --cov=app tests/
```

### Code Style

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* Use meaningful variable names
* Comment your code when necessary
* Keep functions focused and small
* Use type hints

## Database Connector Development

When adding support for a new database:

1. Create a new connector class in `app/data_oracle/connectors/`
2. Implement all required methods from the base connector
3. Add connection type to `app/fastapitypes/sql_connection.py`
4. Add tests in `tests/data_oracle/connectors/`
5. Update documentation

### Connector Checklist

- [ ] Basic connection functionality
- [ ] Schema retrieval
- [ ] Query execution
- [ ] Error handling
- [ ] Tests
- [ ] Documentation

## Documentation

* Use docstrings for all public modules, functions, classes, and methods
* Update README.md if necessary
* Add examples for new features
* Keep API documentation up to date

## Questions?

Feel free to contact the project maintainers if you have any questions. 