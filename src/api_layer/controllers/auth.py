# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file handles letting people log in to our web service. It's like the security
# desk at a building where you show your ID and get a special badge that lets you
# into different areas.

# High School Explanation:
# This module implements the authentication endpoints for the API, handling user
# login, token generation, token refresh, and token revocation. It provides the
# necessary routes for clients to authenticate and maintain their sessions.

"""
Authentication controller for the API layer.

This module provides the API endpoints for user authentication,
including login, token refresh, and token revocation.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from jose import JWTError, jwt

from src.api_layer.core.auth import (
    Token, User, create_access_token, create_refresh_token,
    get_current_active_user, verify_password
)
from src.api_layer.core.config import config
from src.api_layer.core.responses import create_response, create_error_response
from src.api_layer.models.base import StandardRequest, StandardResponse


# Create router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized"},
    },
)


class LoginRequest(BaseModel):
    """Login request data."""
    
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class LoginResponse(BaseModel):
    """Login response data."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type (always 'bearer')")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    refresh_token: str = Field(..., description="JWT refresh token for obtaining new access tokens")
    user: User = Field(..., description="User information")


class RefreshRequest(BaseModel):
    """Token refresh request data."""
    
    refresh_token: str = Field(..., description="JWT refresh token")


class RefreshResponse(BaseModel):
    """Token refresh response data."""
    
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(..., description="Token type (always 'bearer')")
    expires_at: datetime = Field(..., description="Token expiration timestamp")


class RevokeRequest(BaseModel):
    """Token revocation request data."""
    
    token: str = Field(..., description="JWT token to revoke")


class RevokeResponse(BaseModel):
    """Token revocation response data."""
    
    success: bool = Field(..., description="Whether the token was successfully revoked")


# Placeholder for user storage
# In a real implementation, this would be a database
USERS = {
    "admin": {
        "id": "user-1",
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
        "roles": ["admin"]
    },
    "user": {
        "id": "user-2",
        "username": "user",
        "email": "user@example.com",
        "full_name": "Regular User",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "secret"
        "disabled": False,
        "roles": ["user"]
    }
}


def get_user(username: str) -> Optional[Dict[str, Any]]:
    """
    Get a user by username.
    
    Args:
        username: Username to look up
        
    Returns:
        Optional[Dict[str, Any]]: User data or None if not found
    """
    return USERS.get(username)


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username and password.
    
    Args:
        username: Username
        password: Password
        
    Returns:
        Optional[User]: Authenticated user or None if authentication failed
    """
    user_data = get_user(username)
    if not user_data:
        return None
    if not verify_password(password, user_data["hashed_password"]):
        return None
    
    return User(
        id=user_data["id"],
        username=user_data["username"],
        email=user_data.get("email"),
        full_name=user_data.get("full_name"),
        disabled=user_data.get("disabled", False),
        roles=user_data.get("roles", [])
    )


@router.post(
    "/token", 
    response_model=StandardResponse[LoginResponse],
    summary="Login to get access token",
    description="Authenticate with username and password to get JWT access token"
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and provide access token.
    
    Args:
        form_data: OAuth2 password request form
        
    Returns:
        Token: Access token and related information
        
    Raises:
        HTTPException: If authentication fails
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=create_error_response(
                status_code=401,
                error_code="INVALID_CREDENTIALS",
                title="Invalid credentials",
                detail="Incorrect username or password"
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token expiration time
    access_token_expires = timedelta(seconds=config.security.jwt_expiration)
    refresh_token_expires = timedelta(seconds=config.security.jwt_refresh_expiration)
    
    # Create tokens
    access_token = create_access_token(
        data={
            "sub": user.id,
            "name": user.full_name,
            "roles": user.roles,
            "scopes": form_data.scopes or []
        },
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={
            "sub": user.id,
            "token_type": "refresh"
        },
        expires_delta=refresh_token_expires
    )
    
    # Calculate expiration timestamp
    expires_at = datetime.utcnow() + access_token_expires
    
    # Create response
    login_response = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at,
        refresh_token=refresh_token,
        user=user
    )
    
    return create_response(
        data=login_response
    )


@router.post(
    "/refresh", 
    response_model=StandardResponse[RefreshResponse],
    summary="Refresh access token",
    description="Use a refresh token to get a new access token"
)
async def refresh_token(request: StandardRequest[RefreshRequest]):
    """
    Refresh an access token using a refresh token.
    
    Args:
        request: Refresh token request
        
    Returns:
        Token: New access token
        
    Raises:
        HTTPException: If the refresh token is invalid
    """
    refresh_token = request.data.refresh_token
    
    try:
        # Decode refresh token
        payload = jwt.decode(
            refresh_token, 
            config.security.jwt_secret.get_secret_value(), 
            algorithms=[config.security.jwt_algorithm]
        )
        
        # Verify it's a refresh token
        token_type = payload.get("token_type")
        if token_type != "refresh":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=create_error_response(
                    status_code=401,
                    error_code="INVALID_TOKEN",
                    title="Invalid token",
                    detail="Not a valid refresh token"
                ),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract user ID
        user_id = payload.get("sub")
        if not user_id:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=create_error_response(
                    status_code=401,
                    error_code="INVALID_TOKEN",
                    title="Invalid token",
                    detail="Token does not contain user ID"
                ),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Find user
        user = None
        for u in USERS.values():
            if u["id"] == user_id:
                user = User(
                    id=u["id"],
                    username=u["username"],
                    email=u.get("email"),
                    full_name=u.get("full_name"),
                    disabled=u.get("disabled", False),
                    roles=u.get("roles", [])
                )
                break
        
        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=create_error_response(
                    status_code=401,
                    error_code="INVALID_TOKEN",
                    title="Invalid token",
                    detail="User not found"
                ),
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new access token
        access_token_expires = timedelta(seconds=config.security.jwt_expiration)
        access_token = create_access_token(
            data={
                "sub": user.id,
                "name": user.full_name,
                "roles": user.roles
            },
            expires_delta=access_token_expires
        )
        
        # Calculate expiration timestamp
        expires_at = datetime.utcnow() + access_token_expires
        
        # Create response
        refresh_response = RefreshResponse(
            access_token=access_token,
            token_type="bearer",
            expires_at=expires_at
        )
        
        return create_response(
            data=refresh_response
        )
    except JWTError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=create_error_response(
                status_code=401,
                error_code="INVALID_TOKEN",
                title="Invalid token",
                detail="Could not validate refresh token"
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/revoke", 
    response_model=StandardResponse[RevokeResponse],
    summary="Revoke token",
    description="Revoke an access or refresh token"
)
async def revoke_token(
    request: StandardRequest[RevokeRequest],
    user: User = Depends(get_current_active_user)
):
    """
    Revoke a token.
    
    Note: In a real implementation, this would add the token to a blacklist
    or otherwise invalidate it. This is a simplified implementation.
    
    Args:
        request: Token revocation request
        user: Current authenticated user
        
    Returns:
        Dict[str, bool]: Success status
    """
    # In a real implementation, we would add the token to a blacklist
    # or otherwise invalidate it.
    
    return create_response(
        data=RevokeResponse(success=True)
    )


@router.get(
    "/me", 
    response_model=StandardResponse[User],
    summary="Get current user",
    description="Get information about the currently authenticated user"
)
async def get_me(user: User = Depends(get_current_active_user)):
    """
    Get the current authenticated user.
    
    Args:
        user: Current authenticated user
        
    Returns:
        User: Current user information
    """
    return create_response(
        data=user
    )