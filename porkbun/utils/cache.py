from diskcache import Cache
from pathlib import Path
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import json
import hashlib

from porkbun.utils.logging import logger

class CacheManager:
    def __init__(self):
        self.cache_dir = Path.home() / '.porkbun' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache = Cache(directory=str(self.cache_dir))
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.cache.get(key)
            if value is not None:
                logger.debug(f"Cache hit for key: {key}")
            return value
        except Exception as e:
            logger.debug(f"Cache get error: {e}")
            return None
            
    def set(self, key: str, value: Any, expire: int = 3600) -> None:
        """Set value in cache with expiration in seconds."""
        try:
            self.cache.set(key, value, expire=expire)
            logger.debug(f"Cached value for key: {key}")
        except Exception as e:
            logger.debug(f"Cache set error: {e}")
            
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        try:
            self.cache.delete(key)
            logger.debug(f"Deleted cache for key: {key}")
        except Exception as e:
            logger.debug(f"Cache delete error: {e}")
            
    def clear(self) -> None:
        """Clear all cached values."""
        try:
            self.cache.clear()
            logger.debug("Cleared all cache")
        except Exception as e:
            logger.debug(f"Cache clear error: {e}")
            
    def get_api_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key for API request."""
        # Sort params to ensure consistent keys
        sorted_params = json.dumps(params, sort_keys=True)
        key_data = f"{endpoint}:{sorted_params}"
        return hashlib.sha256(key_data.encode()).hexdigest()
        
    def get_api_response(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached API response."""
        cache_key = self.get_api_cache_key(endpoint, params)
        return self.get(cache_key)
        
    def set_api_response(self, endpoint: str, params: Dict[str, Any],
                        response: Dict[str, Any], expire: int = 3600) -> None:
        """Cache API response."""
        cache_key = self.get_api_cache_key(endpoint, params)
        self.set(cache_key, response, expire=expire)
        
    def invalidate_api_cache(self, endpoint: Optional[str] = None) -> None:
        """Invalidate API cache for endpoint or all endpoints."""
        if endpoint:
            # Delete specific endpoint cache
            pattern = f"*{endpoint}*"
            keys = self.cache.glob(pattern)
            for key in keys:
                self.delete(key)
        else:
            # Clear all API cache
            self.clear()

# Global cache instance
cache_manager = CacheManager() 