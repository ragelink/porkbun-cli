import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from rich.prompt import Prompt, Confirm

from porkbun.utils.exceptions import ConfigError
from porkbun.utils.logging import logger

@dataclass
class Profile:
    name: str
    api_key: str
    secret_key: str
    base_url: str = "https://porkbun.com/api/json/v3"
    default: bool = False

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / '.porkbun'
        self.config_file = self.config_dir / 'config.json'
        self.current_profile: Optional[str] = None
        self._config: Dict[str, Any] = {}
        
    def load(self) -> None:
        """Load configuration from file and environment."""
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load from file
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    self._config = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse config file: {e}")
                raise ConfigError(f"Invalid configuration file format: {e}")
        
        # Load from environment
        self._load_from_env()
        
        # Validate configuration
        self._validate_config()
        
        # Set current profile
        self.current_profile = self._config.get('current_profile')
        if not self.current_profile:
            # Use default profile or first available
            profiles = self._config.get('profiles', {})
            self.current_profile = next(
                (name for name, profile in profiles.items() if profile.get('default')),
                next(iter(profiles), None)
            )
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise ConfigError(f"Failed to save configuration: {e}")
    
    def get_profile(self, name: Optional[str] = None) -> Profile:
        """Get a profile by name or current profile."""
        profile_name = name or self.current_profile
        if not profile_name:
            raise ConfigError("No profile selected")
            
        profile_data = self._config.get('profiles', {}).get(profile_name)
        if not profile_data:
            raise ConfigError(f"Profile not found: {profile_name}")
            
        return Profile(
            name=profile_name,
            api_key=profile_data['api_key'],
            secret_key=profile_data['secret_key'],
            base_url=profile_data.get('base_url', "https://porkbun.com/api/json/v3"),
            default=profile_data.get('default', False)
        )
    
    def list_profiles(self) -> List[Profile]:
        """List all available profiles."""
        return [
            Profile(
                name=name,
                api_key=data['api_key'],
                secret_key=data['secret_key'],
                base_url=data.get('base_url', "https://porkbun.com/api/json/v3"),
                default=data.get('default', False)
            )
            for name, data in self._config.get('profiles', {}).items()
        ]
    
    def add_profile(self, name: str, api_key: str, secret_key: str,
                   base_url: Optional[str] = None, make_default: bool = False) -> None:
        """Add a new profile."""
        if name in self._config.get('profiles', {}):
            raise ConfigError(f"Profile already exists: {name}")
            
        profiles = self._config.setdefault('profiles', {})
        profiles[name] = {
            'api_key': api_key,
            'secret_key': secret_key,
            'base_url': base_url or "https://porkbun.com/api/json/v3",
            'default': make_default
        }
        
        if make_default:
            # Unset default flag for other profiles
            for profile in profiles.values():
                if profile is not profiles[name]:
                    profile['default'] = False
        
        self.save()
    
    def remove_profile(self, name: str) -> None:
        """Remove a profile."""
        if name not in self._config.get('profiles', {}):
            raise ConfigError(f"Profile not found: {name}")
            
        del self._config['profiles'][name]
        if self.current_profile == name:
            self.current_profile = None
            
        self.save()
    
    def set_current_profile(self, name: str) -> None:
        """Set the current profile."""
        if name not in self._config.get('profiles', {}):
            raise ConfigError(f"Profile not found: {name}")
            
        self._config['current_profile'] = name
        self.current_profile = name
        self.save()
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_profile = os.environ.get('PORKBUN_PROFILE')
        env_api_key = os.environ.get('PORKBUN_API_KEY')
        env_secret_key = os.environ.get('PORKBUN_SECRET_KEY')
        env_base_url = os.environ.get('PORKBUN_BASE_URL')
        
        if env_api_key and env_secret_key:
            # Create or update environment profile
            profile_name = env_profile or 'env'
            profiles = self._config.setdefault('profiles', {})
            profiles[profile_name] = {
                'api_key': env_api_key,
                'secret_key': env_secret_key,
                'base_url': env_base_url or "https://porkbun.com/api/json/v3",
                'default': not profiles  # Make default if no other profiles exist
            }
    
    def _validate_config(self) -> None:
        """Validate configuration format and data."""
        if not isinstance(self._config, dict):
            raise ConfigError("Invalid configuration format")
            
        profiles = self._config.get('profiles', {})
        if not isinstance(profiles, dict):
            raise ConfigError("Invalid profiles format")
            
        for name, profile in profiles.items():
            if not isinstance(profile, dict):
                raise ConfigError(f"Invalid profile format: {name}")
                
            required_keys = {'api_key', 'secret_key'}
            missing_keys = required_keys - set(profile.keys())
            if missing_keys:
                raise ConfigError(f"Missing required keys in profile {name}: {missing_keys}")
                
            if not isinstance(profile.get('default', False), bool):
                raise ConfigError(f"Invalid default flag in profile {name}")
            
        # Ensure exactly one default profile if any profiles exist
        if profiles:
            default_profiles = [name for name, p in profiles.items() if p.get('default')]
            if not default_profiles:
                # Make the first profile default
                first_profile = next(iter(profiles))
                profiles[first_profile]['default'] = True
            elif len(default_profiles) > 1:
                # Keep only the first default profile
                for name in default_profiles[1:]:
                    profiles[name]['default'] = False 