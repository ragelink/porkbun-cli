# Contributing to Porkbun CLI

Thank you for your interest in contributing to Porkbun CLI! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to be respectful and considerate to other contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with the following information:

1. A clear, descriptive title
2. Steps to reproduce the bug
3. Expected behavior
4. Actual behavior
5. Screenshots (if applicable)
6. Environment information (OS, Python version, etc.)

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:

1. A clear, descriptive title
2. Detailed description of the feature
3. Why this feature would be useful
4. Any implementation ideas you have

### Pull Requests

Follow these steps to submit a pull request:

1. Fork the repository
2. Create a new branch with a descriptive name: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests: `pytest`
5. Ensure code style compliance: `flake8`
6. Commit your changes with a descriptive message
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a pull request against the `main` branch

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ragelink/porkbun-cli.git
   cd porkbun-cli
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   pip install -e .
   ```

## Testing

Run the test suite:
```bash
pytest
```

Run linting:
```bash
flake8 porkbun/
```

## Documentation

When adding new features, please update the documentation in the `docs/` directory. We use MkDocs with the Material theme.

Build and preview documentation:
```bash
mkdocs serve
```

## Release Process

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Create a new GitHub release
4. The GitHub Actions workflow will automatically publish to PyPI

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](../LICENSE). 