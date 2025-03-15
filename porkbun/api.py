import os
import json
import requests
import httpx
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
import time
from functools import wraps

from porkbun.utils.exceptions import PorkbunAPIError, ConfigError
from porkbun.utils.logging import logger, log_api_request
from porkbun.utils.config import ConfigManager
from porkbun.utils.cache import cache_manager
from porkbun.utils.exceptions import APIError, RateLimitError

config_manager = ConfigManager()
config_manager.load()

def load_config() -> Dict[str, str]:
    """Load API configuration from file."""
    config_file = Path.home() / '.porkbun' / 'config.json'
    
    if not config_file.exists():
        logger.error(f"Config file not found: {config_file}")
        raise ConfigError("API configuration not found. Please run 'porkbun config init' first.")
    
    try:
        with open(config_file) as f:
            config = json.load(f)
            
        required_keys = ['apikey', 'secretapikey']
        if not all(key in config for key in required_keys):
            logger.error("Missing required keys in config file")
            raise ConfigError("Invalid configuration. Please run 'porkbun config init' to set up your API keys.")
            
        return config
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse config file: {e}")
        raise ConfigError(f"Invalid configuration file format: {e}")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise ConfigError(f"Failed to load configuration: {e}")

def make_request(endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Make an API request to Porkbun.
    
    Args:
        endpoint: API endpoint
        data: Request data
        
    Returns:
        API response
        
    Raises:
        PorkbunAPIError: If the API request fails
    """
    config = load_config()
    
    # Add API keys to request data
    data.update({
        'apikey': config['apikey'],
        'secretapikey': config['secretapikey']
    })
    
    base_url = 'https://porkbun.com/api/json/v3'
    url = f"{base_url}/{endpoint}"
    
    try:
        logger.debug(f"Making API request to {endpoint}")
        response = requests.post(url, json=data)
        response_data = response.json()
        
        # Log the request and response
        sanitized_data = data.copy()
        sanitized_data.update({
            'apikey': '***',
            'secretapikey': '***'
        })
        log_api_request(endpoint, sanitized_data, response_data)
        
        if response.status_code != 200 or response_data.get('status') != 'SUCCESS':
            error_msg = response_data.get('message', 'Unknown error')
            logger.error(f"API request failed: {error_msg}")
            raise PorkbunAPIError(f"API request failed: {error_msg}")
            
        return response_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise PorkbunAPIError(f"Failed to connect to Porkbun API: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse API response: {e}")
        raise PorkbunAPIError(f"Invalid response from Porkbun API: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise PorkbunAPIError(f"Unexpected error: {e}")

def rate_limit(calls: int = 10, period: int = 60):
    """Rate limiting decorator."""
    def decorator(func):
        last_reset = time.time()
        calls_made = 0
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_reset, calls_made
            
            current_time = time.time()
            if current_time - last_reset >= period:
                calls_made = 0
                last_reset = current_time
                
            if calls_made >= calls:
                wait_time = period - (current_time - last_reset)
                if wait_time > 0:
                    logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    calls_made = 0
                    last_reset = time.time()
                    
            calls_made += 1
            return await func(*args, **kwargs)
            
        return wrapper
    return decorator

class APIClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
        
    @rate_limit()
    async def request(self, endpoint: str, data: Dict[str, Any] = None,
                     method: str = 'POST', use_cache: bool = True) -> Dict[str, Any]:
        """Make an async API request."""
        try:
            profile = config_manager.get_profile()
            base_url = profile.base_url.rstrip('/')
            url = f"{base_url}/{endpoint}"
            
            # Check cache for GET requests
            if method == 'GET' and use_cache:
                cached = cache_manager.get_api_response(endpoint, data or {})
                if cached:
                    return cached
                    
            # Prepare request data
            request_data = {
                'apikey': profile.api_key,
                'secretapikey': profile.secret_key,
                **(data or {})
            }
            
            # Make request
            response = await self.client.request(
                method=method,
                url=url,
                json=request_data
            )
            
            # Handle response
            if response.status_code == 429:
                raise RateLimitError("API rate limit exceeded")
                
            response.raise_for_status()
            result = response.json()
            
            # Cache successful GET responses
            if method == 'GET' and use_cache:
                cache_manager.set_api_response(endpoint, data or {}, result)
                
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            # Check for specific error message about domain not opted in to API access
            error_text = e.response.text.lower()
            if "domain is not opted in to api access" in error_text:
                # Extract domain from URL path
                domain = url.split('/')[-1]
                error_message = (
                    f"Domain {domain} is not opted in to API access.\n\n"
                    f"To fix this issue:\n"
                    f"1. Log in to your Porkbun dashboard at https://porkbun.com/account/login\n"
                    f"2. Navigate to the domain management page for {domain}\n"
                    f"3. Look for the 'API Access' option and enable it\n"
                    f"4. Try this command again after enabling API access"
                )
                raise APIError(error_message)
            raise APIError(f"API request failed: {e}")
        except Exception as e:
            logger.error(f"API error: {e}")
            raise APIError(f"API request failed: {e}")
            
    async def bulk_request(self, requests: List[Dict[str, Any]],
                          parallel: int = 3) -> List[Dict[str, Any]]:
        """Execute multiple API requests in parallel."""
        semaphore = asyncio.Semaphore(parallel)
        
        async def bounded_request(req: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                return await self.request(**req)
                
        return await asyncio.gather(
            *(bounded_request(req) for req in requests),
            return_exceptions=True
        )

async def make_request(endpoint: str, data: Dict[str, Any] = None,
                      method: str = 'POST', use_cache: bool = True) -> Dict[str, Any]:
    """Helper function for making a single API request."""
    async with APIClient() as client:
        return await client.request(endpoint, data, method, use_cache)

async def make_bulk_requests(requests: List[Dict[str, Any]],
                           parallel: int = 3) -> List[Dict[str, Any]]:
    """Helper function for making multiple API requests."""
    async with APIClient() as client:
        return await client.bulk_request(requests, parallel)
