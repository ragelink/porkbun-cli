"""Unit tests for custom exceptions."""

import pytest
from porkbun.utils.exceptions import (
    PorkbunError,
    PorkbunAPIError,
    PorkbunConfigError,
    PorkbunAuthError
)

@pytest.mark.unit
class TestExceptions:
    """Test custom exception classes."""
    
    def test_base_exception(self):
        """Test PorkbunError base exception."""
        with pytest.raises(PorkbunError) as exc_info:
            raise PorkbunError("Base error")
        assert str(exc_info.value) == "Base error"
        assert isinstance(exc_info.value, Exception)
    
    def test_api_error(self):
        """Test PorkbunAPIError exception."""
        with pytest.raises(PorkbunAPIError) as exc_info:
            raise PorkbunAPIError("API error")
        assert str(exc_info.value) == "API error"
        assert isinstance(exc_info.value, PorkbunError)
    
    def test_config_error(self):
        """Test PorkbunConfigError exception."""
        with pytest.raises(PorkbunConfigError) as exc_info:
            raise PorkbunConfigError("Config error")
        assert str(exc_info.value) == "Config error"
        assert isinstance(exc_info.value, PorkbunError)
    
    def test_auth_error(self):
        """Test PorkbunAuthError exception."""
        with pytest.raises(PorkbunAuthError) as exc_info:
            raise PorkbunAuthError("Auth error")
        assert str(exc_info.value) == "Auth error"
        assert isinstance(exc_info.value, PorkbunError)
    
    def test_exception_hierarchy(self):
        """Test exception class hierarchy."""
        api_error = PorkbunAPIError("API error")
        config_error = PorkbunConfigError("Config error")
        auth_error = PorkbunAuthError("Auth error")
        
        assert isinstance(api_error, PorkbunError)
        assert isinstance(config_error, PorkbunError)
        assert isinstance(auth_error, PorkbunError)
        assert isinstance(api_error, Exception)
        assert isinstance(config_error, Exception)
        assert isinstance(auth_error, Exception) 