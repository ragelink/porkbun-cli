"""Custom exceptions for Porkbun CLI."""

class PorkbunError(Exception):
    """Base exception for all Porkbun CLI errors."""
    pass

class PorkbunAPIError(PorkbunError):
    """Exception raised for API errors."""
    pass

class ConfigError(PorkbunError):
    """Exception raised for configuration errors."""
    pass

class ValidationError(PorkbunError):
    """Exception raised for validation errors."""
    pass

class RateLimitError(PorkbunError):
    """Exception raised when API rate limit is exceeded."""
    pass

class APIError(PorkbunError):
    """Exception raised for API errors."""
    pass

class PorkbunConfigError(PorkbunError):
    """Raised when there's an error with the configuration."""
    pass

class PorkbunAuthError(PorkbunError):
    """Raised when there's an authentication error."""
    pass 