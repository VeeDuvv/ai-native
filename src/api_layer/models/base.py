# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file creates the basic building blocks for our computer program. It's like
# making the standard shapes of Lego pieces that we'll use to build our bigger Lego models.

# High School Explanation:
# This module defines the base Pydantic models used throughout the API layer.
# It provides standardized request and response formats, as well as common
# model behaviors and validation rules to ensure consistency across the API.

"""
Base Pydantic models for the API layer.

This module provides common models that are used throughout the API layer,
including standardized request and response formats, pagination models,
and base model classes with common functionality.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Any, Optional, Generic, TypeVar
from datetime import datetime

# Type variable for generic models
T = TypeVar("T")


class BaseAPIModel(BaseModel):
    """Base model for all API models with common configuration."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        json_schema_extra={
            "example": {}
        }
    )


class RequestMeta(BaseModel):
    """Standard metadata included in requests."""
    
    client_request_id: Optional[str] = Field(
        None, 
        description="Optional client-generated request identifier for tracking"
    )
    idempotency_key: Optional[str] = Field(
        None, 
        description="Key to ensure idempotent operations"
    )


class ResponseMeta(BaseModel):
    """Standard metadata included in responses."""
    
    request_id: Optional[str] = Field(
        None, 
        description="Server-generated request identifier"
    )
    timestamp: Optional[datetime] = Field(
        None, 
        description="Timestamp when the response was generated"
    )
    pagination: Optional[Dict[str, Any]] = Field(
        None,
        description="Pagination information for list responses"
    )
    location: Optional[str] = Field(
        None,
        description="Resource location for created resources"
    )


class ErrorSource(BaseAPIModel):
    """
    Source information for an error.
    
    This model provides information about the source of an error,
    such as the parameter or field that caused the error.
    """
    
    pointer: Optional[str] = Field(
        None,
        description="JSON Pointer to the source of the error",
    )
    parameter: Optional[str] = Field(
        None,
        description="Query parameter that caused the error",
    )


class Error(BaseAPIModel):
    """
    Error information.
    
    This model provides detailed information about an error that occurred
    during the processing of a request.
    """
    
    status: str = Field(
        ...,
        description="HTTP status code",
    )
    code: str = Field(
        ...,
        description="Application-specific error code",
    )
    title: str = Field(
        ...,
        description="Short, human-readable summary of the problem",
    )
    detail: Optional[str] = Field(
        None,
        description="Human-readable explanation of the error",
    )
    source: Optional[ErrorSource] = Field(
        None,
        description="Source of the error",
    )


class StandardRequest(Generic[T], BaseAPIModel):
    """Standard request structure for API endpoints."""
    
    data: T = Field(
        ..., 
        description="Request data payload"
    )
    meta: Optional[RequestMeta] = Field(
        None, 
        description="Request metadata"
    )


class StandardResponse(Generic[T], BaseAPIModel):
    """Standard response structure for API endpoints."""
    
    data: Optional[T] = Field(
        None, 
        description="Response data payload"
    )
    meta: Optional[ResponseMeta] = Field(
        {}, 
        description="Response metadata"
    )
    links: Optional[Dict[str, Any]] = Field(
        None, 
        description="HATEOAS links"
    )
    included: Optional[List[Any]] = Field(
        None, 
        description="Included related resources"
    )
    errors: Optional[List[Error]] = Field(
        None,
        description="Errors that occurred during request processing"
    )


class PaginatedResponse(Generic[T], BaseAPIModel):
    """Standard response structure for paginated collections."""
    
    data: List[T] = Field(
        ..., 
        description="List of resource objects"
    )
    meta: Dict[str, Any] = Field(
        ..., 
        description="Response metadata with pagination information"
    )
    links: Dict[str, Any] = Field(
        ..., 
        description="HATEOAS links for pagination"
    )
    included: Optional[List[Any]] = Field(
        None, 
        description="Included related resources"
    )


class HealthCheck(BaseAPIModel):
    """
    Health check response.
    
    This model provides information about the health status of the API.
    """
    
    status: str = Field(
        "ok",
        description="Health status (ok or error)",
    )
    version: str = Field(
        ...,
        description="API version",
    )
    timestamp: datetime = Field(
        ...,
        description="Health check timestamp",
    )
    uptime: float = Field(
        ...,
        description="API uptime in seconds",
    )
    services: Dict[str, Dict[str, Any]] = Field(
        ...,
        description="Status of dependent services",
    )