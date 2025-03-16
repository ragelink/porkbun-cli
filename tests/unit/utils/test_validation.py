"""Unit tests for validation utilities."""

import pytest
from porkbun.utils.validation import (
    validate_domain,
    validate_ip_address,
    validate_ttl,
    validate_record_type,
    validate_email,
)

@pytest.mark.parametrize("domain,expected", [
    ("example.com", True),
    ("subdomain.example.com", True),
    ("test-domain.co.uk", True),
    ("127.0.0.1", False),
    ("example..com", False),
    ("example.c", False),
    ("example", False),
    ("", False),
    (None, False),
])
def test_validate_domain(domain, expected):
    """Test domain validation with various inputs."""
    assert validate_domain(domain) == expected

@pytest.mark.parametrize("ip,expected", [
    ("192.168.1.1", True),
    ("127.0.0.1", True),
    ("255.255.255.255", True),
    ("0.0.0.0", True),
    ("256.0.0.1", False),
    ("192.168.1", False),
    ("192.168.1.1.5", False),
    ("example.com", False),
    ("", False),
    (None, False),
])
def test_validate_ip_address(ip, expected):
    """Test IP address validation with various inputs."""
    assert validate_ip_address(ip) == expected

@pytest.mark.parametrize("ttl,expected", [
    ("600", True),
    ("1", True),
    ("86400", True),
    ("0", False),
    ("-1", False),
    ("not-a-number", False),
    ("", False),
    (None, False),
])
def test_validate_ttl(ttl, expected):
    """Test TTL validation with various inputs."""
    assert validate_ttl(ttl) == expected

@pytest.mark.parametrize("record_type,expected", [
    ("A", True),
    ("AAAA", True),
    ("CNAME", True),
    ("MX", True),
    ("TXT", True),
    ("NS", True),
    ("SRV", True),
    ("CAA", True),
    ("a", True),  # Should be case-insensitive
    ("cname", True),
    ("invalid", False),
    ("", False),
    (None, False),
])
def test_validate_record_type(record_type, expected):
    """Test record type validation with various inputs."""
    assert validate_record_type(record_type) == expected

@pytest.mark.parametrize("email,expected", [
    ("user@example.com", True),
    ("first.last@example.com", True),
    ("user+tag@example.com", True),
    ("user@subdomain.example.com", True),
    ("user@example.co.uk", True),
    ("user@localhost", False),  # Missing TLD
    ("user@", False),
    ("@example.com", False),
    ("user@.com", False),
    ("user@example.", False),
    ("user.example.com", False),  # Missing @
    ("user@@example.com", False),  # Double @
    ("", False),
    (None, False),
])
def test_validate_email(email, expected):
    """Test email validation with various inputs."""
    assert validate_email(email) == expected 