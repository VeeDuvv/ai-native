# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file stores all the settings for our web service. It's like the control panel
# where we can adjust things like security, how long people can stay logged in,
# and who can connect to our service.

# High School Explanation:
# This module defines the configuration settings for the API layer using Pydantic models.
# It includes security parameters (JWT secrets, token expiration), CORS settings,
# and other application-level configurations that can be adjusted without code changes.

"""
Configuration module for the API layer.

This module provides configuration settings for the API, including security
settings, CORS configuration, and other application parameters. It uses
Pydantic models for validation and type safety.
"""

import os
from typing import List, Optional, Set

from pydantic import BaseModel, SecretStr, Field


class SecurityConfig(BaseModel):
    """Security configuration settings."""
    
    jwt_secret: SecretStr = Field(
        SecretStr("test-secret-do-not-use-in-production"),
        description="Secret key for JWT token signing"
    )
    jwt_algorithm: str = Field(
        "HS256",
        description="Algorithm used for JWT signing"
    )
    access_token_expire_minutes: int = Field(
        60,
        description="Access token expiration time in minutes",
        ge=1,
        le=1440  # Max 24 hours
    )
    refresh_token_expire_days: int = Field(
        7,
        description="Refresh token expiration time in days",
        ge=1,
        le=30  # Max 30 days
    )
    password_reset_expire_minutes: int = Field(
        15,
        description="Password reset token expiration time in minutes",
        ge=5,
        le=60  # Max 1 hour
    )


class CORSConfig(BaseModel):
    """CORS configuration settings."""
    
    allow_origins: List[str] = Field(
        ["*"],
        description="List of origins that are allowed to make cross-origin requests"
    )
    allow_methods: List[str] = Field(
        ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        description="HTTP methods that are allowed for cross-origin requests"
    )
    allow_headers: List[str] = Field(
        ["*"],
        description="HTTP headers that are allowed for cross-origin requests"
    )
    allow_credentials: bool = Field(
        True,
        description="Whether cookies should be included in cross-origin requests"
    )
    expose_headers: List[str] = Field(
        ["Content-Length", "Content-Type"],
        description="Headers that browsers are allowed to access"
    )
    max_age: int = Field(
        600,
        description="Maximum time (in seconds) to cache CORS preflight requests",
        ge=0
    )


class DatabaseConfig(BaseModel):
    """Database configuration settings."""
    
    url: SecretStr = Field(
        SecretStr("sqlite:///./test.db"),
        description="Database connection URL"
    )
    echo: bool = Field(
        False,
        description="Whether to echo SQL queries"
    )
    pool_size: int = Field(
        5,
        description="Connection pool size",
        ge=1,
        le=100
    )
    max_overflow: int = Field(
        10,
        description="Maximum overflow connections",
        ge=0
    )
    pool_recycle: int = Field(
        3600,
        description="Connection recycle time in seconds",
        ge=0
    )


class APIConfig(BaseModel):
    """API configuration settings."""
    
    version: str = Field(
        "0.1.0",
        description="API version"
    )
    title: str = Field(
        "AI-Native Ad Agency API",
        description="API title for documentation"
    )
    description: str = Field(
        "API for the AI-Native Ad Agency platform",
        description="API description for documentation"
    )
    docs_url: str = Field(
        "/api/docs",
        description="URL for API documentation"
    )
    redoc_url: str = Field(
        "/api/redoc",
        description="URL for ReDoc API documentation"
    )
    openapi_url: str = Field(
        "/api/openapi.json",
        description="URL for OpenAPI schema"
    )
    root_path: str = Field(
        "",
        description="API root path for reverse proxy configurations"
    )


class LoggingConfig(BaseModel):
    """Logging configuration settings."""
    
    level: str = Field(
        "INFO",
        description="Logging level"
    )
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    filename: Optional[str] = Field(
        None,
        description="Log file path (if None, logs to console)"
    )


class Config(BaseModel):
    """Main application configuration."""
    
    debug: bool = Field(
        True,
        description="Debug mode flag"
    )
    environment: str = Field(
        "development",
        description="Application environment (development, staging, production)"
    )
    security: SecurityConfig = Field(
        SecurityConfig(),
        description="Security configuration"
    )
    cors: CORSConfig = Field(
        CORSConfig(),
        description="CORS configuration"
    )
    database: DatabaseConfig = Field(
        DatabaseConfig(),
        description="Database configuration"
    )
    api: APIConfig = Field(
        APIConfig(),
        description="API configuration"
    )
    logging: LoggingConfig = Field(
        LoggingConfig(),
        description="Logging configuration"
    )


# Load configuration from environment variables
def load_from_env(config_model: BaseModel) -> BaseModel:
    """
    Update configuration fields from environment variables.
    
    Environment variables are expected to follow the pattern:
    AINADAGENCY_SECTION_FIELD (e.g., AINADAGENCY_SECURITY_JWT_SECRET)
    
    Args:
        config_model: The configuration model to update
        
    Returns:
        Updated configuration model
    """
    prefix = "AINADAGENCY_"
    
    for var_name, var_value in os.environ.items():
        if not var_name.startswith(prefix):
            continue
            
        parts = var_name[len(prefix):].lower().split('_')
        
        if len(parts) < 2:
            continue
            
        section, field = parts[0], '_'.join(parts[1:])
        
        # Skip if section doesn't exist in config
        if not hasattr(config_model, section):
            continue
            
        section_model = getattr(config_model, section)
        
        # Skip if field doesn't exist in section
        if not hasattr(section_model, field):
            continue
            
        # Update field
        if isinstance(getattr(section_model, field), SecretStr):
            setattr(section_model, field, SecretStr(var_value))
        elif isinstance(getattr(section_model, field), bool):
            setattr(section_model, field, var_value.lower() in ('true', 'yes', '1'))
        elif isinstance(getattr(section_model, field), int):
            try:
                setattr(section_model, field, int(var_value))
            except ValueError:
                pass
        elif isinstance(getattr(section_model, field), float):
            try:
                setattr(section_model, field, float(var_value))
            except ValueError:
                pass
        elif isinstance(getattr(section_model, field), list):
            setattr(section_model, field, var_value.split(','))
        else:
            setattr(section_model, field, var_value)
    
    return config_model


# Create global config instance
config = Config()

# Load configuration from environment variables
config = load_from_env(config)