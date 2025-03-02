"""Unit tests for core domain functionality."""

import pytest
import requests
from unittest.mock import Mock, patch

from porkbun.core.domain import format_domain, create_session, check_domain_availability
from porkbun.utils.exceptions import PorkbunAPIError

@pytest.mark.unit
class TestDomainFormatting:
    """Test domain name formatting functionality."""
    
    @pytest.mark.parametrize("input_domain,expected", [
        ("example.com", "example.com"),
        ("sub.domain.com", "subdomain.com"),
        ("test..domain.org", "testdomain.org"),
        ("UPPER.COM", "upper.com"),
        ("single", "single"),
    ])
    def test_format_domain(self, input_domain, expected):
        """Test domain formatting with various inputs."""
        assert format_domain(input_domain) == expected

@pytest.mark.unit
class TestSessionCreation:
    """Test session creation and configuration."""
    
    def test_create_session(self):
        """Test that session is created with proper retry configuration."""
        session = create_session()
        
        assert isinstance(session, requests.Session)
        adapter = session.get_adapter('https://')
        assert adapter.max_retries.total == 3
        assert adapter.max_retries.backoff_factor == 2
        assert set(adapter.max_retries.status_forcelist) == {429, 500, 502, 503, 504}

@pytest.mark.unit
class TestDomainAvailability:
    """Test domain availability checking functionality."""
    
    def test_successful_check(self, mock_session, sample_domain):
        """Test successful domain availability check."""
        result = check_domain_availability(
            sample_domain,
            "test_api_key",
            "test_secret_key",
            mock_session
        )
        
        assert result["success"] is True
        assert result["available"] is True
        assert result["price"] == "10.00"
        assert result["error"] is None
        
        mock_session.post.assert_called_once()
        
    def test_unavailable_domain(self, mock_session, sample_domain):
        """Test checking an unavailable domain."""
        mock_session.post.return_value.json.return_value = {
            "status": "SUCCESS",
            "response": {
                "avail": "no",
                "price": None
            }
        }
        
        result = check_domain_availability(
            sample_domain,
            "test_api_key",
            "test_secret_key",
            mock_session
        )
        
        assert result["success"] is True
        assert result["available"] is False
        assert result["price"] is None
        assert result["error"] is None
        
    def test_api_error(self, mock_session, sample_domain, api_error_response):
        """Test handling of API errors."""
        mock_session.post.return_value.json.return_value = api_error_response
        
        with pytest.raises(PorkbunAPIError, match="Sample error message"):
            check_domain_availability(
                sample_domain,
                "test_api_key",
                "test_secret_key",
                mock_session
            )
            
    def test_rate_limit(self, mock_session, sample_domain, rate_limit_response):
        """Test handling of rate limit responses."""
        mock_session.post.return_value = rate_limit_response
        
        with pytest.raises(PorkbunAPIError, match="Rate limit exceeded"):
            check_domain_availability(
                sample_domain,
                "test_api_key",
                "test_secret_key",
                mock_session
            )
            
    def test_network_error(self, mock_session, sample_domain):
        """Test handling of network errors."""
        mock_session.post.side_effect = requests.exceptions.ConnectionError("Network error")
        
        with pytest.raises(PorkbunAPIError, match="Network error"):
            check_domain_availability(
                sample_domain,
                "test_api_key",
                "test_secret_key",
                mock_session
            ) 