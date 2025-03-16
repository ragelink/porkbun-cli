# Testing Guide

This guide explains the testing approach for the Porkbun CLI project and how to write and run tests.

## Testing Framework

We use pytest for testing. The test suite is organized as follows:

- `tests/unit/`: Unit tests for individual components
- `tests/integration/`: Integration tests that interact with the Porkbun API

## Running Tests

### All Tests

```bash
pytest
```

### Unit Tests Only

```bash
pytest tests/unit/
```

### Test Coverage

To generate a test coverage report:

```bash
pytest --cov=porkbun tests/
```

For a detailed HTML coverage report:

```bash
pytest --cov=porkbun --cov-report=html tests/
```

## Writing Tests

### Unit Tests

Unit tests should be isolated and not make actual API calls. Use mocking to simulate API responses:

```python
import pytest
from unittest.mock import patch, MagicMock

from porkbun.commands.domains import check_domain

@patch('porkbun.commands.domains.make_request')
def test_check_domain(mock_make_request):
    # Set up mock response
    mock_response = {
        "status": "SUCCESS",
        "available": True,
        "tld": "com",
        "domain": "example.com",
        "price": 9.98
    }
    mock_make_request.return_value = mock_response
    
    # Call the function
    result = check_domain("example.com")
    
    # Assert the result
    assert result["available"] is True
    assert result["domain"] == "example.com"
    
    # Verify the mock was called correctly
    mock_make_request.assert_called_once_with(
        endpoint="check",
        method="post",
        data={"domain": "example.com"}
    )
```

### Integration Tests

Integration tests make actual API calls and should be skipped by default to prevent accidental charges:

```python
import pytest
import os
from porkbun.commands.domains import check_domain

@pytest.mark.skipif(
    "PORKBUN_RUN_INTEGRATION_TESTS" not in os.environ,
    reason="Integration tests are disabled. Set PORKBUN_RUN_INTEGRATION_TESTS=1 to run."
)
def test_check_domain_integration():
    result = check_domain("example1234567890.com")
    assert "available" in result
    assert "domain" in result
```

To run integration tests:

```bash
PORKBUN_RUN_INTEGRATION_TESTS=1 pytest tests/integration/
```

## Test Fixtures

We use pytest fixtures for common setup tasks:

```python
import pytest
import json
from pathlib import Path

@pytest.fixture
def sample_dns_records():
    """Load sample DNS records from a test fixture file."""
    fixture_path = Path(__file__).parent / "fixtures" / "dns_records.json"
    with open(fixture_path, "r") as f:
        return json.load(f)
```

## Test Environment

For consistent testing, make sure to:

1. Set up a test config with test API credentials:
   ```bash
   mkdir -p ~/.porkbun
   # Add test credentials to ~/.porkbun/config.ini
   ```

2. Use test domains that you own for integration tests, never real customer domains

## Mocking Techniques

### Mocking API Responses

```python
@patch('porkbun.utils.api.make_request')
def test_function(mock_make_request):
    mock_make_request.return_value = {"status": "SUCCESS", "data": {...}}
    # Test code
```

### Mocking File Operations

```python
@patch('builtins.open', new_callable=mock_open, read_data='test data')
def test_file_reading(mock_file):
    # Test code that reads files
```

## Continuous Integration

Tests are automatically run on GitHub Actions for each pull request and push to main. The workflow configuration is in `.github/workflows/test.yml`. 