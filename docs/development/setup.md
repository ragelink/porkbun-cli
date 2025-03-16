# Development Setup

This guide explains how to set up your development environment for contributing to the Porkbun CLI.

## Prerequisites

- Python 3.8 or higher
- Git
- A Porkbun account with API access (for testing)

## Setting Up the Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ragelink/porkbun-cli.git
   cd porkbun-cli
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   pip install -e .
   ```

   This installs the package in development mode, so changes to the code will be immediately available without reinstalling.

## Project Structure

- `porkbun/`: Main package directory
  - `commands/`: Command modules for the CLI
  - `utils/`: Utility functions and helpers
  - `templates/`: Template files
  - `cli.py`: Main CLI entry point
- `examples/`: Example scripts and configurations
- `tests/`: Test files
  - `unit/`: Unit tests
  - `integration/`: Integration tests
- `docs/`: Documentation files
- `.github/workflows/`: GitHub Actions workflows for CI/CD

## Configuration for Development

1. **Create a test API configuration**:
   ```bash
   mkdir -p ~/.porkbun
   ```

2. **Add a test profile to `~/.porkbun/config.ini`**:
   ```ini
   [default]
   api_key = YOUR_TEST_API_KEY
   secret_key = YOUR_TEST_SECRET_KEY
   ```

   For running integration tests, you'll need a real Porkbun API key.

## Running Tests

- **Run all tests**:
  ```bash
  pytest
  ```

- **Run unit tests only**:
  ```bash
  pytest tests/unit/
  ```

- **Run with coverage**:
  ```bash
  pytest --cov=porkbun tests/
  ```

## Code Style

We follow PEP 8 guidelines. Use `flake8` to check your code:

```bash
flake8 porkbun/
```

## Building Documentation

We use MkDocs with the Material theme for documentation:

1. **Preview documentation locally**:
   ```bash
   mkdocs serve
   ```

2. **Build documentation**:
   ```bash
   mkdocs build
   ```

## Submitting Changes

1. Create a new branch for your feature or bugfix
2. Make your changes
3. Add tests for your changes
4. Run tests to ensure they pass
5. Update documentation if necessary
6. Submit a pull request

See the [Contributing Guide](contributing.md) for more details on the contribution process. 