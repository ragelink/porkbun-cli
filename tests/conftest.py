"""Test configuration and fixtures for porkbun-cli."""

import os
import pytest
import requests
from unittest.mock import Mock

@pytest.fixture
def mock_session():
    """Create a mock requests session."""
    session = Mock(spec=requests.Session)
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "status": "SUCCESS",
        "response": {
            "avail": "yes",
            "price": "10.00"
        }
    }
    session.post.return_value = response
    return session

@pytest.fixture
def mock_env(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv("PORKBUN_API_KEY", "test_api_key")
    monkeypatch.setenv("PORKBUN_SECRET_API_KEY", "test_secret_key")

@pytest.fixture
def sample_domain():
    """Return a sample domain name."""
    return "example.com"

@pytest.fixture
def sample_domains():
    """Return a list of sample domain names."""
    return ["example.com", "test.org", "sample.net"]

@pytest.fixture
def sample_dns_record():
    """Return a sample DNS record."""
    return {
        "id": "123456",
        "name": "www",
        "type": "A",
        "content": "192.0.2.1",
        "ttl": "600",
        "prio": "0"
    }

@pytest.fixture
def sample_ssl_cert():
    """Return a sample SSL certificate response."""
    return {
        "status": "SUCCESS",
        "certificateDetails": {
            "status": "active",
            "type": "standard",
            "expires": "2025-03-02",
            "chain": ["CERT1", "CERT2"],
            "installationInstructions": "Sample instructions"
        }
    }

@pytest.fixture
def api_error_response():
    """Return a sample API error response."""
    return {
        "status": "ERROR",
        "message": "Sample error message"
    }

@pytest.fixture
def rate_limit_response():
    """Return a sample rate limit response."""
    response = Mock()
    response.status_code = 429
    response.json.return_value = {
        "status": "ERROR",
        "message": "Rate limit exceeded"
    }
    return response