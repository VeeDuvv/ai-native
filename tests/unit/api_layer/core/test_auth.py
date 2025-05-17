"""
Unit tests for the authentication module.
"""

import pytest
from unittest.mock import patch, MagicMock
import jwt
from datetime import datetime, timedelta

from src.api_layer.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_current_active_user,
    has_role,
    has_scope
)
from src.api_layer.core.config import config


@pytest.mark.unit
@pytest.mark.core
class TestAuth:
    """Tests for the auth module."""

    def test_password_hashing(self):
        """Test that password hashing and verification work correctly."""
        password = "testpassword"
        hashed = get_password_hash(password)
        
        # Hashed password should be different from original
        assert hashed != password
        
        # Verification should work
        assert verify_password(password, hashed)
        
        # Incorrect password should not verify
        assert not verify_password("wrongpassword", hashed)

    def test_create_access_token(self):
        """Test creating an access token."""
        data = {"sub": "user123", "name": "Test User", "roles": ["admin"]}
        expires_delta = timedelta(minutes=15)
        
        token = create_access_token(data, expires_delta)
        
        # Token should be a string
        assert isinstance(token, str)
        
        # Decode and verify the token
        decoded = jwt.decode(
            token,
            config.security.jwt_secret.get_secret_value(),
            algorithms=[config.security.jwt_algorithm]
        )
        
        # Check token contents
        assert decoded["sub"] == "user123"
        assert decoded["name"] == "Test User"
        assert decoded["roles"] == ["admin"]
        assert "exp" in decoded

    def test_create_refresh_token(self):
        """Test creating a refresh token."""
        data = {"sub": "user123"}
        expires_delta = timedelta(days=7)
        
        token = create_refresh_token(data, expires_delta)
        
        # Token should be a string
        assert isinstance(token, str)
        
        # Decode and verify the token
        decoded = jwt.decode(
            token,
            config.security.jwt_secret.get_secret_value(),
            algorithms=[config.security.jwt_algorithm]
        )
        
        # Check token contents
        assert decoded["sub"] == "user123"
        assert decoded["token_type"] == "refresh"
        assert "exp" in decoded

    @patch("src.api_layer.core.auth.jwt")
    async def test_get_current_user_valid(self, mock_jwt):
        """Test getting the current user with a valid token."""
        # Mock the jwt.decode function
        mock_decoded = {
            "sub": "user123",
            "name": "Test User",
            "roles": ["admin"],
            "exp": (datetime.utcnow() + timedelta(minutes=15)).timestamp()
        }
        mock_jwt.decode.return_value = mock_decoded
        
        # Call the function with a mock token
        user = await get_current_user("valid_token")
        
        # Check the result
        assert user.id == "user123"
        assert user.full_name == "Test User"
        assert user.roles == ["admin"]

    @patch("src.api_layer.core.auth.jwt.decode")
    async def test_get_current_user_invalid(self, mock_decode):
        """Test getting the current user with an invalid token."""
        # Mock the jwt.decode function to raise an exception
        mock_decode.side_effect = jwt.PyJWTError("Invalid token")
        
        # Call the function and check it raises an HTTPException
        with pytest.raises(Exception) as exc_info:
            await get_current_user("invalid_token")
        
        assert "Could not validate credentials" in str(exc_info.value)

    async def test_get_current_active_user_active(self):
        """Test getting an active user."""
        # Create a mock user
        mock_user = MagicMock()
        mock_user.disabled = False
        
        # Call the function
        active_user = await get_current_active_user(mock_user)
        
        # Check the result
        assert active_user == mock_user

    async def test_get_current_active_user_disabled(self):
        """Test getting a disabled user raises an exception."""
        # Create a mock user
        mock_user = MagicMock()
        mock_user.disabled = True
        
        # Call the function and check it raises an HTTPException
        with pytest.raises(Exception) as exc_info:
            await get_current_active_user(mock_user)
        
        assert "Inactive user" in str(exc_info.value)

    async def test_has_role_matching(self):
        """Test role-based access control with matching roles."""
        # Create the dependency
        admin_only = has_role("admin")
        
        # Create a mock user with admin role
        mock_user = MagicMock()
        mock_user.roles = ["admin"]
        
        # Call the dependency
        result = await admin_only(mock_user)
        
        # Check it returns the user
        assert result == mock_user

    async def test_has_role_non_matching(self):
        """Test role-based access control with non-matching roles."""
        # Create the dependency
        admin_only = has_role("admin")
        
        # Create a mock user without admin role
        mock_user = MagicMock()
        mock_user.roles = ["user"]
        
        # Call the dependency and check it raises an HTTPException
        with pytest.raises(Exception) as exc_info:
            await admin_only(mock_user)
        
        assert "Insufficient permissions" in str(exc_info.value)

    @patch("src.api_layer.core.auth.jwt")
    async def test_has_scope_matching(self, mock_jwt):
        """Test scope-based access control with matching scopes."""
        # Mock the jwt.decode function
        mock_decoded = {
            "sub": "user123",
            "scopes": ["read:users", "write:users"]
        }
        mock_jwt.decode.return_value = mock_decoded
        
        # Create the dependency
        read_users = has_scope("read:users")
        
        # Call the dependency
        result = await read_users("valid_token")
        
        # Check it returns the token
        assert result == "valid_token"

    @patch("src.api_layer.core.auth.jwt")
    async def test_has_scope_non_matching(self, mock_jwt):
        """Test scope-based access control with non-matching scopes."""
        # Mock the jwt.decode function
        mock_decoded = {
            "sub": "user123",
            "scopes": ["read:users"]
        }
        mock_jwt.decode.return_value = mock_decoded
        
        # Create the dependency
        write_users = has_scope("write:campaigns")
        
        # Call the dependency and check it raises an HTTPException
        with pytest.raises(Exception) as exc_info:
            await write_users("valid_token")
        
        assert "Insufficient permissions" in str(exc_info.value)