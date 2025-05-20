# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file defines different types of advertisement pieces like images and text.
# It's like having different shaped containers to organize our art supplies.

# High School Explanation:
# This module implements data models for creative assets used in advertising campaigns.
# It defines structures for various creative types, formats, and metadata that are
# used across the API layer for validation and serialization.

"""
Creative models for the API layer.

This module provides the Pydantic models for creative assets, including
text, image, and video creatives, as well as variation tracking and performance data.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, HttpUrl

from src.api_layer.models.base import BaseAPIModel


class CreativeType(str, Enum):
    """Types of creative assets."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    HTML = "html"


class CreativeStatus(str, Enum):
    """Status of a creative asset."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class CreativeFormat(str, Enum):
    """Format/dimension category of a creative asset."""
    SQUARE = "square"           # 1:1 ratio
    PORTRAIT = "portrait"       # Vertical (e.g., 4:5, 9:16)
    LANDSCAPE = "landscape"     # Horizontal (e.g., 16:9, 4:3)
    STORY = "story"             # Mobile stories format
    BANNER = "banner"           # Banner ad format
    CAROUSEL = "carousel"       # Multi-image carousel


class Dimensions(BaseAPIModel):
    """Dimensions of a creative asset."""
    width: int = Field(..., description="Width in pixels")
    height: int = Field(..., description="Height in pixels")


class PerformanceMetrics(BaseAPIModel):
    """Performance metrics for a creative asset."""
    impressions: int = Field(0, description="Number of impressions")
    clicks: int = Field(0, description="Number of clicks")
    click_through_rate: float = Field(0.0, description="Click-through rate")
    conversions: int = Field(0, description="Number of conversions")
    conversion_rate: float = Field(0.0, description="Conversion rate")
    engagement_rate: Optional[float] = Field(None, description="Engagement rate")
    cost_per_click: Optional[float] = Field(None, description="Cost per click")
    cost_per_acquisition: Optional[float] = Field(None, description="Cost per acquisition")
    ad_recall: Optional[float] = Field(None, description="Ad recall lift")
    last_updated: datetime = Field(..., description="Timestamp of last metrics update")


class CreativeVariation(BaseAPIModel):
    """A variation of a creative asset for A/B testing."""
    id: uuid.UUID = Field(..., description="Unique identifier")
    name: str = Field(..., description="Variation name")
    type: CreativeType = Field(..., description="Creative type")
    content: Dict[str, Any] = Field(..., description="Creative content data")
    status: CreativeStatus = Field(..., description="Variation status")
    performance: Optional[PerformanceMetrics] = Field(None, description="Performance metrics")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class Creative(BaseAPIModel):
    """A creative asset used in advertising campaigns."""
    id: uuid.UUID = Field(..., description="Unique identifier")
    name: str = Field(..., description="Creative name")
    description: Optional[str] = Field(None, description="Creative description")
    type: CreativeType = Field(..., description="Creative type")
    format: CreativeFormat = Field(..., description="Creative format")
    content: Dict[str, Any] = Field(..., description="Creative content data")
    dimensions: Optional[Dimensions] = Field(None, description="Creative dimensions")
    status: CreativeStatus = Field(..., description="Creative status")
    variations: List[CreativeVariation] = Field(default_factory=list, description="A/B testing variations")
    campaign_ids: List[uuid.UUID] = Field(default_factory=list, description="Associated campaign IDs")
    target_url: Optional[HttpUrl] = Field(None, description="Target URL for the creative")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class CreativeCreate(BaseAPIModel):
    """Request model for creating a creative asset."""
    name: str = Field(..., description="Creative name")
    description: Optional[str] = Field(None, description="Creative description")
    type: CreativeType = Field(..., description="Creative type")
    format: CreativeFormat = Field(..., description="Creative format")
    content: Dict[str, Any] = Field(..., description="Creative content data")
    dimensions: Optional[Dimensions] = Field(None, description="Creative dimensions")
    campaign_ids: Optional[List[uuid.UUID]] = Field(None, description="Associated campaign IDs")
    target_url: Optional[HttpUrl] = Field(None, description="Target URL for the creative")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CreativeUpdate(BaseAPIModel):
    """Request model for updating a creative asset."""
    name: Optional[str] = Field(None, description="Creative name")
    description: Optional[str] = Field(None, description="Creative description")
    status: Optional[CreativeStatus] = Field(None, description="Creative status")
    format: Optional[CreativeFormat] = Field(None, description="Creative format")
    content: Optional[Dict[str, Any]] = Field(None, description="Creative content data")
    dimensions: Optional[Dimensions] = Field(None, description="Creative dimensions")
    campaign_ids: Optional[List[uuid.UUID]] = Field(None, description="Associated campaign IDs")
    target_url: Optional[HttpUrl] = Field(None, description="Target URL for the creative")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CreativeFilterParams(BaseAPIModel):
    """Filter parameters for listing creatives."""
    status: Optional[List[CreativeStatus]] = Field(None, description="Filter by status")
    type: Optional[List[CreativeType]] = Field(None, description="Filter by creative type")
    format: Optional[List[CreativeFormat]] = Field(None, description="Filter by creative format")
    campaign_id: Optional[uuid.UUID] = Field(None, description="Filter by associated campaign")
    tag: Optional[List[str]] = Field(None, description="Filter by tags")
    query: Optional[str] = Field(None, description="Search query for name or description")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date after")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date before")


class GenerateVariationsRequest(BaseAPIModel):
    """Request model for generating creative variations."""
    variation_count: int = Field(..., ge=1, le=10, description="Number of variations to generate")
    variation_strength: float = Field(0.5, ge=0.1, le=1.0, description="Degree of variation from original (0.1-1.0)")
    focus_elements: Optional[List[str]] = Field(None, description="Elements to focus on varying")
    target_audience: Optional[str] = Field(None, description="Target audience to optimize for")
    optimization_goal: Optional[str] = Field(None, description="Optimization goal (e.g., CTR, conversions)")