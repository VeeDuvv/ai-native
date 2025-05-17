"""
Base Pydantic models for the API layer.
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
    
    request_id: str = Field(
        ..., 
        description="Server-generated request identifier"
    )
    timestamp: datetime = Field(
        ..., 
        description="Timestamp when the response was generated"
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
    
    data: T = Field(
        ..., 
        description="Response data payload"
    )
    meta: ResponseMeta = Field(
        ..., 
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
