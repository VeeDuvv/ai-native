"""
Configuration module for the API layer.
"""

from pydantic import BaseModel, SecretStr


class SecurityConfig(BaseModel):
    """Security configuration."""
    
    jwt_secret: SecretStr = SecretStr("test-secret-do-not-use-in-production")
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 1 hour
    jwt_refresh_expiration: int = 604800  # 7 days


class Config(BaseModel):
    """Application configuration."""
    
    debug: bool = True
    security: SecurityConfig = SecurityConfig()


# Create global config instance
config = Config()
