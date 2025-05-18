# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file is like a special lock box for important information. It turns regular 
# information into scrambled code that only people with the right key can read.

# High School Explanation:
# This module implements data encryption services for protecting sensitive information.
# It provides symmetric and asymmetric encryption capabilities, key management, 
# secure storage of encryption keys, and a simple interface for encrypting and 
# decrypting data in various formats.

import os
import base64
import json
import logging
from typing import Dict, Any, Optional, Union, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
    BestAvailableEncryption,
)
from cryptography.hazmat.backends import default_backend

# Configure logging
logger = logging.getLogger(__name__)


class KeyNotFoundException(Exception):
    """Exception raised when a key is not found."""
    pass


class EncryptionError(Exception):
    """Exception raised when encryption fails."""
    pass


class DecryptionError(Exception):
    """Exception raised when decryption fails."""
    pass


class EncryptionService:
    """
    Service for encrypting and decrypting sensitive data.
    
    This service provides methods for symmetric and asymmetric encryption,
    key management, and secure storage of encryption keys.
    """
    
    def __init__(self, key_dir: Optional[Union[str, Path]] = None, 
                 master_password: Optional[str] = None):
        """
        Initialize the encryption service.
        
        Args:
            key_dir: Directory to store encryption keys. If None, keys will be stored in memory only.
            master_password: Password to protect stored keys. Required if key_dir is provided.
        """
        self.key_dir = Path(key_dir) if key_dir else None
        self.master_password = master_password
        
        # In-memory key store
        self._symmetric_keys = {}
        self._asymmetric_keys = {}
        
        # Initialize the key directory if provided
        if self.key_dir:
            if not self.master_password:
                raise ValueError("Master password is required when key_dir is provided")
            
            self.key_dir.mkdir(parents=True, exist_ok=True)
            self._load_keys()
    
    def _derive_key_from_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Derive a encryption key from a password using PBKDF2.
        
        Args:
            password: The password to derive the key from
            salt: Optional salt for key derivation. If None, a new salt will be generated.
            
        Returns:
            Tuple of (key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def _load_keys(self):
        """Load keys from the key directory."""
        if not self.key_dir:
            return
        
        # Load symmetric keys
        sym_key_dir = self.key_dir / 'symmetric'
        if sym_key_dir.exists():
            for key_file in sym_key_dir.glob('*.key'):
                key_name = key_file.stem
                try:
                    with open(key_file, 'rb') as f:
                        encrypted_key = f.read()
                    
                    # Decrypt the key using the master password
                    with open(key_file.with_suffix('.salt'), 'rb') as f:
                        salt = f.read()
                    
                    master_key, _ = self._derive_key_from_password(self.master_password, salt)
                    fernet = Fernet(master_key)
                    key = fernet.decrypt(encrypted_key)
                    
                    self._symmetric_keys[key_name] = key
                    logger.debug(f"Loaded symmetric key: {key_name}")
                except Exception as e:
                    logger.error(f"Failed to load symmetric key {key_name}: {e}")
        
        # Load asymmetric keys
        asym_key_dir = self.key_dir / 'asymmetric'
        if asym_key_dir.exists():
            for key_folder in asym_key_dir.glob('*'):
                if key_folder.is_dir():
                    key_name = key_folder.name
                    try:
                        # Load private key
                        private_key_file = key_folder / 'private.pem'
                        if private_key_file.exists():
                            with open(private_key_file, 'rb') as f:
                                private_key_data = f.read()
                            
                            private_key = load_pem_private_key(
                                private_key_data,
                                password=self.master_password.encode() if self.master_password else None,
                                backend=default_backend()
                            )
                        else:
                            private_key = None
                        
                        # Load public key
                        public_key_file = key_folder / 'public.pem'
                        if public_key_file.exists():
                            with open(public_key_file, 'rb') as f:
                                public_key_data = f.read()
                            
                            public_key = load_pem_public_key(
                                public_key_data,
                                backend=default_backend()
                            )
                        else:
                            public_key = None
                        
                        if private_key or public_key:
                            self._asymmetric_keys[key_name] = (private_key, public_key)
                            logger.debug(f"Loaded asymmetric key pair: {key_name}")
                    except Exception as e:
                        logger.error(f"Failed to load asymmetric key {key_name}: {e}")
    
    def _save_symmetric_key(self, key_name: str, key: bytes):
        """Save a symmetric key to the key directory."""
        if not self.key_dir:
            return
        
        sym_key_dir = self.key_dir / 'symmetric'
        sym_key_dir.mkdir(parents=True, exist_ok=True)
        
        # Encrypt the key using the master password
        master_key, salt = self._derive_key_from_password(self.master_password)
        fernet = Fernet(master_key)
        encrypted_key = fernet.encrypt(key)
        
        # Save the encrypted key
        with open(sym_key_dir / f"{key_name}.key", 'wb') as f:
            f.write(encrypted_key)
        
        # Save the salt
        with open(sym_key_dir / f"{key_name}.salt", 'wb') as f:
            f.write(salt)
        
        logger.debug(f"Saved symmetric key: {key_name}")
    
    def _save_asymmetric_key_pair(self, key_name: str, private_key: RSAPrivateKey, public_key: RSAPublicKey):
        """Save an asymmetric key pair to the key directory."""
        if not self.key_dir:
            return
        
        asym_key_dir = self.key_dir / 'asymmetric' / key_name
        asym_key_dir.mkdir(parents=True, exist_ok=True)
        
        # Serialize and save the private key with password protection
        private_key_data = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=BestAvailableEncryption(self.master_password.encode()) 
                if self.master_password else NoEncryption()
        )
        
        with open(asym_key_dir / 'private.pem', 'wb') as f:
            f.write(private_key_data)
        
        # Serialize and save the public key
        public_key_data = public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(asym_key_dir / 'public.pem', 'wb') as f:
            f.write(public_key_data)
        
        logger.debug(f"Saved asymmetric key pair: {key_name}")
    
    def create_symmetric_key(self, key_name: str) -> bytes:
        """
        Create a new symmetric encryption key.
        
        Args:
            key_name: Name to identify the key
            
        Returns:
            The generated key
        """
        key = Fernet.generate_key()
        self._symmetric_keys[key_name] = key
        
        if self.key_dir:
            self._save_symmetric_key(key_name, key)
        
        return key
    
    def get_symmetric_key(self, key_name: str) -> bytes:
        """
        Get a symmetric key by name.
        
        Args:
            key_name: Name of the key to retrieve
            
        Returns:
            The encryption key
            
        Raises:
            KeyNotFoundException: If the key is not found
        """
        if key_name not in self._symmetric_keys:
            raise KeyNotFoundException(f"Symmetric key '{key_name}' not found")
        
        return self._symmetric_keys[key_name]
    
    def create_asymmetric_key_pair(self, key_name: str, key_size: int = 2048) -> Tuple[RSAPrivateKey, RSAPublicKey]:
        """
        Create a new asymmetric encryption key pair.
        
        Args:
            key_name: Name to identify the key pair
            key_size: Size of the key in bits
            
        Returns:
            Tuple of (private_key, public_key)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        self._asymmetric_keys[key_name] = (private_key, public_key)
        
        if self.key_dir:
            self._save_asymmetric_key_pair(key_name, private_key, public_key)
        
        return private_key, public_key
    
    def get_asymmetric_key_pair(self, key_name: str) -> Tuple[Optional[RSAPrivateKey], Optional[RSAPublicKey]]:
        """
        Get an asymmetric key pair by name.
        
        Args:
            key_name: Name of the key pair to retrieve
            
        Returns:
            Tuple of (private_key, public_key)
            
        Raises:
            KeyNotFoundException: If the key pair is not found
        """
        if key_name not in self._asymmetric_keys:
            raise KeyNotFoundException(f"Asymmetric key pair '{key_name}' not found")
        
        return self._asymmetric_keys[key_name]
    
    def encrypt_with_symmetric_key(self, data: Union[str, bytes, Dict[str, Any]], key_name: str) -> bytes:
        """
        Encrypt data using a symmetric key.
        
        Args:
            data: Data to encrypt (string, bytes, or dictionary)
            key_name: Name of the key to use for encryption
            
        Returns:
            Encrypted data as bytes
            
        Raises:
            KeyNotFoundException: If the key is not found
            EncryptionError: If encryption fails
        """
        try:
            key = self.get_symmetric_key(key_name)
            fernet = Fernet(key)
            
            if isinstance(data, dict):
                data = json.dumps(data).encode()
            elif isinstance(data, str):
                data = data.encode()
            
            return fernet.encrypt(data)
        except KeyNotFoundException:
            raise
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt data: {e}")
    
    def decrypt_with_symmetric_key(self, encrypted_data: bytes, key_name: str) -> bytes:
        """
        Decrypt data using a symmetric key.
        
        Args:
            encrypted_data: Data to decrypt
            key_name: Name of the key to use for decryption
            
        Returns:
            Decrypted data as bytes
            
        Raises:
            KeyNotFoundException: If the key is not found
            DecryptionError: If decryption fails
        """
        try:
            key = self.get_symmetric_key(key_name)
            fernet = Fernet(key)
            
            return fernet.decrypt(encrypted_data)
        except KeyNotFoundException:
            raise
        except Exception as e:
            raise DecryptionError(f"Failed to decrypt data: {e}")
    
    def encrypt_with_asymmetric_key(self, data: Union[str, bytes], key_name: str) -> bytes:
        """
        Encrypt data using an asymmetric public key.
        
        Args:
            data: Data to encrypt (string or bytes)
            key_name: Name of the key pair to use for encryption
            
        Returns:
            Encrypted data as bytes
            
        Raises:
            KeyNotFoundException: If the key is not found
            EncryptionError: If encryption fails
        """
        try:
            _, public_key = self.get_asymmetric_key_pair(key_name)
            
            if public_key is None:
                raise EncryptionError(f"Public key for '{key_name}' not found")
            
            if isinstance(data, str):
                data = data.encode()
            
            # RSA can only encrypt small amounts of data, so we need to chunk it
            # For larger data, a hybrid approach with symmetric encryption would be better
            chunk_size = 190  # Maximum size for RSA-2048 with OAEP padding
            chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
            
            encrypted_chunks = []
            for chunk in chunks:
                encrypted_chunk = public_key.encrypt(
                    chunk,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                encrypted_chunks.append(encrypted_chunk)
            
            # Encode the chunks for storage
            return base64.b64encode(json.dumps([base64.b64encode(c).decode() for c in encrypted_chunks]).encode())
        except KeyNotFoundException:
            raise
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt data: {e}")
    
    def decrypt_with_asymmetric_key(self, encrypted_data: bytes, key_name: str) -> bytes:
        """
        Decrypt data using an asymmetric private key.
        
        Args:
            encrypted_data: Data to decrypt
            key_name: Name of the key pair to use for decryption
            
        Returns:
            Decrypted data as bytes
            
        Raises:
            KeyNotFoundException: If the key is not found
            DecryptionError: If decryption fails
        """
        try:
            private_key, _ = self.get_asymmetric_key_pair(key_name)
            
            if private_key is None:
                raise DecryptionError(f"Private key for '{key_name}' not found")
            
            # Decode the chunks
            encrypted_chunks = json.loads(base64.b64decode(encrypted_data).decode())
            encrypted_chunks = [base64.b64decode(c) for c in encrypted_chunks]
            
            decrypted_chunks = []
            for chunk in encrypted_chunks:
                decrypted_chunk = private_key.decrypt(
                    chunk,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                decrypted_chunks.append(decrypted_chunk)
            
            return b''.join(decrypted_chunks)
        except KeyNotFoundException:
            raise
        except Exception as e:
            raise DecryptionError(f"Failed to decrypt data: {e}")
    
    def encrypt_json(self, data: Dict[str, Any], key_name: str, use_asymmetric: bool = False) -> str:
        """
        Encrypt a JSON object and return a base64-encoded string.
        
        Args:
            data: JSON object to encrypt
            key_name: Name of the key to use for encryption
            use_asymmetric: Whether to use asymmetric encryption
            
        Returns:
            Base64-encoded encrypted data as a string
        """
        json_str = json.dumps(data)
        
        if use_asymmetric:
            encrypted = self.encrypt_with_asymmetric_key(json_str, key_name)
        else:
            encrypted = self.encrypt_with_symmetric_key(json_str, key_name)
        
        return base64.b64encode(encrypted).decode()
    
    def decrypt_json(self, encrypted_data: str, key_name: str, use_asymmetric: bool = False) -> Dict[str, Any]:
        """
        Decrypt a base64-encoded string and parse it as JSON.
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            key_name: Name of the key to use for decryption
            use_asymmetric: Whether to use asymmetric decryption
            
        Returns:
            Decrypted JSON object
        """
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        if use_asymmetric:
            decrypted = self.decrypt_with_asymmetric_key(encrypted_bytes, key_name)
        else:
            decrypted = self.decrypt_with_symmetric_key(encrypted_bytes, key_name)
        
        return json.loads(decrypted.decode())
    
    def rotate_symmetric_key(self, key_name: str) -> bytes:
        """
        Rotate a symmetric key by creating a new one with the same name.
        
        Args:
            key_name: Name of the key to rotate
            
        Returns:
            The new key
        """
        # Check if the key exists
        if key_name not in self._symmetric_keys:
            raise KeyNotFoundException(f"Symmetric key '{key_name}' not found")
        
        # Create a new key
        return self.create_symmetric_key(key_name)
    
    def rotate_asymmetric_key_pair(self, key_name: str, key_size: int = 2048) -> Tuple[RSAPrivateKey, RSAPublicKey]:
        """
        Rotate an asymmetric key pair by creating a new one with the same name.
        
        Args:
            key_name: Name of the key pair to rotate
            key_size: Size of the key in bits
            
        Returns:
            Tuple of (private_key, public_key)
        """
        # Check if the key pair exists
        if key_name not in self._asymmetric_keys:
            raise KeyNotFoundException(f"Asymmetric key pair '{key_name}' not found")
        
        # Create a new key pair
        return self.create_asymmetric_key_pair(key_name, key_size)


# Global encryption service instance
_encryption_service = None


def get_encryption_service(key_dir: Optional[Union[str, Path]] = None, 
                          master_password: Optional[str] = None) -> EncryptionService:
    """
    Get the global encryption service instance.
    
    Args:
        key_dir: Directory to store encryption keys. If None, keys will be stored in memory only.
        master_password: Password to protect stored keys. Required if key_dir is provided.
        
    Returns:
        Global encryption service instance
    """
    global _encryption_service
    
    if _encryption_service is None:
        _encryption_service = EncryptionService(key_dir, master_password)
    
    return _encryption_service


def encrypt_data(data: Union[str, bytes, Dict[str, Any]], key_name: str = "default", use_asymmetric: bool = False) -> bytes:
    """
    Encrypt data using the global encryption service.
    
    Args:
        data: Data to encrypt
        key_name: Name of the key to use for encryption
        use_asymmetric: Whether to use asymmetric encryption
        
    Returns:
        Encrypted data as bytes
    """
    service = get_encryption_service()
    
    # Create the key if it doesn't exist
    try:
        if use_asymmetric:
            service.get_asymmetric_key_pair(key_name)
        else:
            service.get_symmetric_key(key_name)
    except KeyNotFoundException:
        if use_asymmetric:
            service.create_asymmetric_key_pair(key_name)
        else:
            service.create_symmetric_key(key_name)
    
    # Encrypt the data
    if use_asymmetric:
        return service.encrypt_with_asymmetric_key(data, key_name)
    else:
        return service.encrypt_with_symmetric_key(data, key_name)


def decrypt_data(encrypted_data: bytes, key_name: str = "default", use_asymmetric: bool = False) -> bytes:
    """
    Decrypt data using the global encryption service.
    
    Args:
        encrypted_data: Data to decrypt
        key_name: Name of the key to use for decryption
        use_asymmetric: Whether to use asymmetric decryption
        
    Returns:
        Decrypted data as bytes
    """
    service = get_encryption_service()
    
    # Decrypt the data
    if use_asymmetric:
        return service.decrypt_with_asymmetric_key(encrypted_data, key_name)
    else:
        return service.decrypt_with_symmetric_key(encrypted_data, key_name)