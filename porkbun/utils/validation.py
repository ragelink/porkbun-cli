"""Validation utilities for Porkbun CLI."""

import re
from typing import Union, Optional, Pattern, Callable, Any

def _validate_with_pattern(value: Optional[str], pattern: Union[str, Pattern]) -> bool:
    """
    Validate a value against a regex pattern.
    
    Args:
        value: Value to validate
        pattern: Regex pattern to match against
        
    Returns:
        bool: True if value matches pattern, False otherwise
    """
    if not value:
        return False
        
    if isinstance(pattern, str):
        pattern = re.compile(pattern)
        
    return bool(pattern.match(value))

def validate_domain(domain: Optional[str]) -> bool:
    """
    Validate domain name format.
    
    Args:
        domain: Domain name to validate
        
    Returns:
        bool: True if domain is valid, False otherwise
    """
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return _validate_with_pattern(domain, pattern)

def validate_ip_address(ip: Optional[str]) -> bool:
    """
    Validate IPv4 address format.
    
    Args:
        ip: IP address to validate
        
    Returns:
        bool: True if IP is valid, False otherwise
    """
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return _validate_with_pattern(ip, pattern)

def validate_ttl(ttl: Optional[str]) -> bool:
    """
    Validate TTL value.
    
    Args:
        ttl: TTL value to validate
        
    Returns:
        bool: True if TTL is valid, False otherwise
    """
    if not ttl:
        return False
        
    try:
        ttl_int = int(ttl)
        return ttl_int > 0
    except (ValueError, TypeError):
        return False

def validate_record_type(record_type: Optional[str]) -> bool:
    """
    Validate DNS record type.
    
    Args:
        record_type: Record type to validate
        
    Returns:
        bool: True if record type is valid, False otherwise
    """
    if not record_type:
        return False
        
    valid_types = {'A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS', 'SRV', 'CAA'}
    return record_type.upper() in valid_types

def validate_email(email: Optional[str]) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    # Email format validation - RFC 5322 compliant pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return _validate_with_pattern(email, pattern)

def validate_url(url: Optional[str]) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    # URL format validation - basic HTTP/HTTPS URL pattern
    pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?::\d+)?(?:/[-\w%!$&\'()*+,;=:@/~]+)*(?:\?[-\w%!$&\'()*+,;=:@/~]*)?(?:#[-\w%!$&\'()*+,;=:@/~]*)?$'
    return _validate_with_pattern(url, pattern)

def validate_with_custom_message(
    value: Any, 
    validator: Callable[[Any], bool], 
    error_message: str = "Invalid value"
) -> tuple[bool, Optional[str]]:
    """
    Validate a value with a custom error message.
    
    Args:
        value: Value to validate
        validator: Validation function that returns boolean
        error_message: Error message if validation fails
        
    Returns:
        tuple: (is_valid, error_message or None)
    """
    is_valid = validator(value)
    return is_valid, None if is_valid else error_message 