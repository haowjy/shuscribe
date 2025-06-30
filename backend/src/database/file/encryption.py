"""
File-Based Encryption for API Keys

Handles encryption and decryption of API keys for file-based storage.
Supports both encrypted and plaintext storage based on configuration.
"""

import os
import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class FileEncryption:
    """File-based encryption for API keys"""
    
    def __init__(self, encryption_enabled: bool = True, master_key: Optional[str] = None):
        self.encryption_enabled = encryption_enabled
        self._fernet: Optional[Fernet] = None
        
        if encryption_enabled:
            self._fernet = self._initialize_encryption(master_key)
    
    def _initialize_encryption(self, master_key: Optional[str] = None) -> Fernet:
        """Initialize encryption with master key or generate one"""
        if master_key:
            # Use provided master key
            key = base64.urlsafe_b64encode(master_key.encode()[:32].ljust(32, b'0'))
        else:
            # Generate or load key from environment/file
            key = self._get_or_create_encryption_key()
        
        return Fernet(key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get encryption key from environment or create new one"""
        # Try environment variable first
        env_key = os.getenv('SHUSCRIBE_ENCRYPTION_KEY')
        if env_key:
            return base64.urlsafe_b64encode(env_key.encode()[:32].ljust(32, b'0'))
        
        # Generate new key for local development
        return Fernet.generate_key()
    
    def encrypt(self, data: str) -> str:
        """Encrypt data string"""
        if not self.encryption_enabled or not self._fernet:
            return data  # Store as plaintext if encryption disabled
        
        return self._fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data string"""
        if not self.encryption_enabled or not self._fernet:
            return encrypted_data  # Return as-is if encryption disabled
        
        try:
            return self._fernet.decrypt(encrypted_data.encode()).decode()
        except Exception:
            # If decryption fails, assume it's plaintext (backward compatibility)
            return encrypted_data


class FileStorageConfig:
    """Configuration for file-based storage security"""
    
    def __init__(self):
        # For local development, encryption can be optional
        self.encrypt_api_keys = os.getenv('SHUSCRIBE_ENCRYPT_API_KEYS', 'true').lower() == 'true'
        
        # For shared/production file storage, encryption should be required
        self.require_encryption = os.getenv('SHUSCRIBE_REQUIRE_ENCRYPTION', 'false').lower() == 'true'
        
        # Master key for encryption (optional for local dev)
        self.master_key = os.getenv('SHUSCRIBE_MASTER_KEY')
        
        # API key storage location
        self.secure_storage_path = os.getenv('SHUSCRIBE_SECURE_PATH', './.shuscribe_secure')
        
        # Validate configuration
        if self.require_encryption and not self.encrypt_api_keys:
            raise ValueError("SHUSCRIBE_REQUIRE_ENCRYPTION=true but SHUSCRIBE_ENCRYPT_API_KEYS=false")


def create_encryption_manager(config: Optional[FileStorageConfig] = None) -> FileEncryption:
    """Factory function to create encryption manager"""
    if config is None:
        config = FileStorageConfig()
    
    return FileEncryption(
        encryption_enabled=config.encrypt_api_keys,
        master_key=config.master_key
    ) 


# # backend/src/core/encryption.py
# """
# Encryption utilities for sensitive data (e.g., API keys)
# """
# import base64
# from cryptography.fernet import Fernet
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
# from cryptography.hazmat.backends import default_backend

# from src.config import settings
# from src.core.exceptions import ShuScribeException

# # Derive a key from the provided ENCRYPTION_KEY for Fernet
# # This ensures the key is exactly 32 URL-safe base64-encoded bytes
# def _derive_fernet_key(master_key: str) -> bytes:
#     """Derive a Fernet key from the master encryption key."""
#     # Using a fixed salt for deterministic key derivation for simplicity in this context.
#     # For production, a unique salt per encryption operation is generally more secure,
#     # but here we need to always derive the same key for decryption.
#     salt = b"shuscribe_salt_" * 2  # Needs to be at least 16 bytes.
#     kdf = PBKDF2HMAC(
#         algorithm=hashes.SHA256(),
#         length=32,
#         salt=salt,
#         iterations=100000, # Use a high iteration count
#         backend=default_backend()
#     )
#     return base64.urlsafe_b64encode(kdf.derive(master_key.encode('utf-8')))


# _fernet_key = None
# _fernet_instance = None

# def _get_fernet_instance() -> Fernet:
#     """Get the singleton Fernet instance."""
#     global _fernet_key, _fernet_instance
#     if _fernet_instance is None:
#         if not settings.ENCRYPTION_KEY or len(settings.ENCRYPTION_KEY) < 32:
#             raise ShuScribeException(
#                 "ENCRYPTION_KEY must be at least 32 characters long in .env"
#             )
#         _fernet_key = _derive_fernet_key(settings.ENCRYPTION_KEY)
#         _fernet_instance = Fernet(_fernet_key)
#     return _fernet_instance

# def encrypt_api_key(api_key: str) -> str:
#     """Encrypts an API key."""
#     f = _get_fernet_instance()
#     encrypted_token = f.encrypt(api_key.encode('utf-8'))
#     return encrypted_token.decode('utf-8')

# def decrypt_api_key(encrypted_key: str) -> str:
#     """Decrypts an API key."""
#     f = _get_fernet_instance()
#     try:
#         decrypted_token = f.decrypt(encrypted_key.encode('utf-8'))
#         return decrypted_token.decode('utf-8')
#     except Exception as e:
#         raise ShuScribeException(f"Failed to decrypt API key: {e}")