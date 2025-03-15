import keyring
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional, Tuple
import os
import json

from porkbun.utils.logging import logger

class SecurityManager:
    def __init__(self):
        self.service_name = 'porkbun-cli'
        self.salt_username = 'salt'
        self._fernet = None
        
    @property
    def fernet(self) -> Fernet:
        """Get or create Fernet instance for encryption."""
        if self._fernet is None:
            # Get or generate salt
            salt = self._get_or_create_salt()
            
            # Derive key from machine-specific data
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self._get_machine_key()))
            self._fernet = Fernet(key)
            
        return self._fernet
        
    def _get_machine_key(self) -> bytes:
        """Get machine-specific key material."""
        # Use hardware identifiers or system-specific data
        try:
            import uuid
            machine_id = str(uuid.getnode()).encode()
            return machine_id
        except:
            # Fallback to hostname if uuid not available
            return os.uname().nodename.encode()
            
    def _get_or_create_salt(self) -> bytes:
        """Get or create salt for key derivation."""
        salt = keyring.get_password(self.service_name, self.salt_username)
        if not salt:
            salt = base64.b64encode(os.urandom(16)).decode()
            keyring.set_password(self.service_name, self.salt_username, salt)
        return base64.b64decode(salt)
        
    def store_api_keys(self, profile: str, api_key: str, secret_key: str) -> None:
        """Securely store API keys for a profile."""
        try:
            # Encrypt keys
            data = {
                'api_key': api_key,
                'secret_key': secret_key
            }
            encrypted = self.fernet.encrypt(json.dumps(data).encode())
            
            # Store in keyring
            keyring.set_password(
                self.service_name,
                f"profile_{profile}",
                base64.b64encode(encrypted).decode()
            )
            logger.debug(f"Stored API keys for profile: {profile}")
            
        except Exception as e:
            logger.error(f"Failed to store API keys: {e}")
            raise
            
    def get_api_keys(self, profile: str) -> Optional[Tuple[str, str]]:
        """Retrieve API keys for a profile."""
        try:
            # Get from keyring
            encrypted = keyring.get_password(self.service_name, f"profile_{profile}")
            if not encrypted:
                return None
                
            # Decrypt keys
            decrypted = self.fernet.decrypt(base64.b64decode(encrypted))
            data = json.loads(decrypted)
            
            return data['api_key'], data['secret_key']
            
        except Exception as e:
            logger.error(f"Failed to retrieve API keys: {e}")
            return None
            
    def delete_api_keys(self, profile: str) -> None:
        """Delete stored API keys for a profile."""
        try:
            keyring.delete_password(self.service_name, f"profile_{profile}")
            logger.debug(f"Deleted API keys for profile: {profile}")
        except Exception as e:
            logger.error(f"Failed to delete API keys: {e}")
            raise
            
    def rotate_encryption_key(self) -> None:
        """Rotate the encryption key and re-encrypt all stored keys."""
        try:
            # Get all profiles
            profiles = []
            for item in keyring.get_credential(self.service_name, None) or []:
                if item.username.startswith('profile_'):
                    profiles.append(item.username[8:])  # Remove 'profile_' prefix
                    
            if not profiles:
                return
                
            # Create new salt and Fernet instance
            old_fernet = self._fernet
            keyring.delete_password(self.service_name, self.salt_username)
            self._fernet = None  # Force new Fernet creation
            
            # Re-encrypt all keys
            for profile in profiles:
                # Decrypt with old key
                encrypted = keyring.get_password(self.service_name, f"profile_{profile}")
                if encrypted:
                    decrypted = old_fernet.decrypt(base64.b64decode(encrypted))
                    data = json.loads(decrypted)
                    
                    # Re-encrypt with new key
                    self.store_api_keys(profile, data['api_key'], data['secret_key'])
                    
            logger.info("Successfully rotated encryption key")
            
        except Exception as e:
            logger.error(f"Failed to rotate encryption key: {e}")
            raise

# Global security instance
security_manager = SecurityManager() 