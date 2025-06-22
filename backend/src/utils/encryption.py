# backend/src/utils/encryption.py
"""
Encryption utilities for sensitive data (e.g., API keys)
"""
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os

from src.config import settings
from src.core.exceptions import ShuScribeException

# Derive a key from the provided ENCRYPTION_KEY for Fernet
# This ensures the key is exactly 32 URL-safe base64-encoded bytes
def _derive_fernet_key(master_key: str) -> bytes:
    """Derive a Fernet key from the master encryption key."""
    # Using a fixed salt for deterministic key derivation for simplicity in this context.
    # For production, a unique salt per encryption operation is generally more secure,
    # but here we need to always derive the same key for decryption.
    salt = b"shuscribe_salt_" * 2  # Needs to be at least 16 bytes.
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000, # Use a high iteration count
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(master_key.encode('utf-8')))


_fernet_key = None
_fernet_instance = None

def _get_fernet_instance() -> Fernet:
    """Get the singleton Fernet instance."""
    global _fernet_key, _fernet_instance
    if _fernet_instance is None:
        if not settings.ENCRYPTION_KEY or len(settings.ENCRYPTION_KEY) < 32:
            raise ShuScribeException(
                "ENCRYPTION_KEY must be at least 32 characters long in .env"
            )
        _fernet_key = _derive_fernet_key(settings.ENCRYPTION_KEY)
        _fernet_instance = Fernet(_fernet_key)
    return _fernet_instance

def encrypt_api_key(api_key: str) -> str:
    """Encrypts an API key."""
    f = _get_fernet_instance()
    encrypted_token = f.encrypt(api_key.encode('utf-8'))
    return encrypted_token.decode('utf-8')

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypts an API key."""
    f = _get_fernet_instance()
    try:
        decrypted_token = f.decrypt(encrypted_key.encode('utf-8'))
        return decrypted_token.decode('utf-8')
    except Exception as e:
        raise ShuScribeException(f"Failed to decrypt API key: {e}")