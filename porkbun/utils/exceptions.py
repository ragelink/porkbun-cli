"""Custom exceptions for Porkbun CLI."""

class PorkbunError(Exception):
    """Base exception for all Porkbun CLI errors."""
    pass

class PorkbunAPIError(PorkbunError):
    """Raised when there's an error communicating with the Porkbun API."""
    pass

class PorkbunConfigError(PorkbunError):
    """Raised when there's an error with the configuration."""
    pass

class PorkbunAuthError(PorkbunError):
    """Raised when there's an authentication error."""
    pass 