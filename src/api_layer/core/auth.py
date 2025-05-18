"""
Authentication and authorization for the API layer.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from src.api_layer.core.config import config


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


class Token(BaseModel):
    """Token response model."""
    
    access_token: str
    token_type: str
    expires_at: datetime
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    """Token payload model."""
    
    sub: str  # User ID
    name: Optional[str] = None
    roles: List[str] = []
    exp: datetime
    scopes: List[str] = []


class User(BaseModel):
    """User model."""
    
    id: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False
    roles: List[str] = []


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    
    # Encode token
    encoded_jwt = jwt.encode(
        to_encode, 
        config.security.jwt_secret.get_secret_value(), 
        algorithm=config.security.jwt_algorithm
    )
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    
    # Set a longer expiration time for refresh tokens
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
        
    to_encode.update({"exp": expire, "token_type": "refresh"})
    
    # Encode token
    encoded_jwt = jwt.encode(
        to_encode, 
        config.security.jwt_secret.get_secret_value(), 
        algorithm=config.security.jwt_algorithm
    )
    
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current user from a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = jwt.decode(
            token, 
            config.security.jwt_secret.get_secret_value(), 
            algorithms=[config.security.jwt_algorithm]
        )
        
        # Extract user ID
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Extract token expiration
        token_exp = payload.get("exp")
        if token_exp is None:
            raise credentials_exception
        
        # Check if token is a refresh token
        token_type = payload.get("token_type")
        if token_type == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot use refresh token for authentication",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create token data
        token_data = TokenData(
            sub=user_id,
            name=payload.get("name"),
            roles=payload.get("roles", []),
            exp=datetime.fromtimestamp(token_exp),
            scopes=payload.get("scopes", [])
        )
    except JWTError:
        raise credentials_exception
    
    # For testing, just return a user based on the token data
    user = User(
        id=token_data.sub,
        username="user",
        email="user@example.com",
        full_name=token_data.name,
        roles=token_data.roles,
    )
        
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return current_user


def has_role(roles: Union[str, List[str]]):
    """Create a dependency to check if the current user has one of the specified roles."""
    if isinstance(roles, str):
        roles = [roles]
        
    async def has_role_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if not any(role in current_user.roles for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(roles)}",
            )
        return current_user
        
    return has_role_dependency


def has_scope(scopes: Union[str, List[str]]):
    """Create a dependency to check if the current token has one of the specified scopes."""
    if isinstance(scopes, str):
        scopes = [scopes]
        
    async def has_scope_dependency(token: str = Depends(oauth2_scheme)) -> str:
        try:
            # Decode token
            payload = jwt.decode(
                token, 
                config.security.jwt_secret.get_secret_value(), 
                algorithms=[config.security.jwt_algorithm]
            )
            
            # Extract scopes
            token_scopes = payload.get("scopes", [])
            
            # Check if the token has any of the required scopes
            if not any(scope in token_scopes for scope in scopes):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required scopes: {', '.join(scopes)}",
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return token
        
    return has_scope_dependency
