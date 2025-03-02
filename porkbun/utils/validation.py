"""Validation utilities for Porkbun CLI."""

import re

def validate_domain(domain: str) -> bool:
    """
    Validate domain name format.
    
    Args:
        domain: Domain name to validate
        
    Returns:
        bool: True if domain is valid, False otherwise
    """
    if not domain:
        return False
        
    # Basic domain format validation
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    return bool(re.match(pattern, domain))

def validate_ip_address(ip: str) -> bool:
    """
    Validate IPv4 address format.
    
    Args:
        ip: IP address to validate
        
    Returns:
        bool: True if IP is valid, False otherwise
    """
    if not ip:
        return False
        
    # IPv4 format validation
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return bool(re.match(pattern, ip))

def validate_ttl(ttl: str) -> bool:
    """
    Validate TTL value.
    
    Args:
        ttl: TTL value to validate
        
    Returns:
        bool: True if TTL is valid, False otherwise
    """
    try:
        ttl_int = int(ttl)
        return ttl_int > 0
    except (ValueError, TypeError):
        return False

def validate_record_type(record_type: str) -> bool:
    """
    Validate DNS record type.
    
    Args:
        record_type: Record type to validate
        
    Returns:
        bool: True if record type is valid, False otherwise
    """
    valid_types = {'A', 'AAAA', 'CNAME', 'MX', 'TXT', 'NS', 'SRV', 'CAA'}
    return record_type.upper() in valid_types 