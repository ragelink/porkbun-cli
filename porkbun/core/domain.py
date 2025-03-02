"""Core domain functionality for Porkbun CLI."""

from typing import Dict, Optional
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from ..utils.exceptions import PorkbunAPIError

def format_domain(domain: str) -> str:
    """Format domain name by removing any internal periods except the TLD."""
    parts = domain.lower().split('.')
    if len(parts) >= 2:
        name = ''.join(parts[:-1])  # Join all parts except TLD
        return f"{name}.{parts[-1]}"
    return domain.lower()

def create_session() -> requests.Session:
    """Create a session with retry strategy for API requests."""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # number of retries
        backoff_factor=2,  # wait 2, 4, 8 seconds between retries
        status_forcelist=[429, 500, 502, 503, 504]  # HTTP status codes to retry on
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    return session

def check_domain_availability(
    domain: str,
    api_key: str,
    secret_key: str,
    session: Optional[requests.Session] = None
) -> Dict:
    """
    Check domain availability using Porkbun API.
    
    Args:
        domain: Domain name to check
        api_key: Porkbun API key
        secret_key: Porkbun secret API key
        session: Optional session object for making requests
        
    Returns:
        Dict containing status, availability, price, and any error messages
        
    Raises:
        PorkbunAPIError: If there's an error communicating with the API
    """
    if session is None:
        session = create_session()
        
    formatted_domain = format_domain(domain)
    api_endpoint = f'https://api.porkbun.com/api/json/v3/domain/checkDomain/{formatted_domain}'
    payload = {
        'apikey': api_key,
        'secretapikey': secret_key
    }
    
    result = {
        'domain': domain,
        'success': False,
        'available': False,
        'price': None,
        'error': None
    }
    
    try:
        response = session.post(api_endpoint, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'SUCCESS':
            result['success'] = True
            result['available'] = data['response'].get('avail') == 'yes'
            result['price'] = data['response'].get('price')
        else:
            result['error'] = data.get('message', 'Unknown API error')
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            result['error'] = 'Rate limit exceeded'
            time.sleep(30)  # Wait longer on rate limit
        else:
            result['error'] = f'HTTP error: {str(e)}'
    except requests.exceptions.RequestException as e:
        result['error'] = f'Network error: {str(e)}'
    except Exception as e:
        result['error'] = f'Unexpected error: {str(e)}'
    
    if result['error'] and not result['success']:
        raise PorkbunAPIError(result['error'])
        
    return result 