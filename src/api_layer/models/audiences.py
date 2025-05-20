# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file defines the different types of groups we want to show our ads to.
# It's like making lists of people who might like different types of toys.

# High School Explanation:
# This module implements data models for audience targeting used in advertising campaigns.
# It defines structures for different audience types, criteria, and segmentation methods
# used across the API layer for validation and serialization.

"""
Audience models for the API layer.

This module provides the Pydantic models for audience targeting and segmentation,
including demographic, interest, behavioral, and geographical audience criteria.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import uuid
from pydantic import BaseModel, Field

from src.api_layer.models.base import BaseAPIModel


class AudienceType(str, Enum):
    """Types of audience segmentation."""
    DEMOGRAPHIC = "demographic"
    INTEREST = "interest"
    BEHAVIORAL = "behavioral"
    GEOGRAPHIC = "geographic"
    CUSTOM = "custom"
    LOOKALIKE = "lookalike"
    RETARGETING = "retargeting"


class AudienceStatus(str, Enum):
    """Status of an audience definition."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class DemographicCriteria(BaseAPIModel):
    """Demographic criteria for audience targeting."""
    age_range: Optional[List[str]] = Field(None, description="Age range for targeting")
    gender: Optional[List[str]] = Field(None, description="Gender for targeting")
    income_level: Optional[List[str]] = Field(None, description="Income level for targeting")
    education_level: Optional[List[str]] = Field(None, description="Education level for targeting")
    marital_status: Optional[List[str]] = Field(None, description="Marital status for targeting")
    parental_status: Optional[List[str]] = Field(None, description="Parental status for targeting")
    employment_status: Optional[List[str]] = Field(None, description="Employment status for targeting")


class InterestCriteria(BaseAPIModel):
    """Interest-based criteria for audience targeting."""
    categories: Optional[List[str]] = Field(None, description="Interest categories")
    keywords: Optional[List[str]] = Field(None, description="Interest keywords")
    brands: Optional[List[str]] = Field(None, description="Brand affinities")
    hobbies: Optional[List[str]] = Field(None, description="Hobby interests")
    media_consumption: Optional[List[str]] = Field(None, description="Media consumption preferences")


class GeographicCriteria(BaseAPIModel):
    """Geographic criteria for audience targeting."""
    countries: Optional[List[str]] = Field(None, description="Countries for targeting")
    regions: Optional[List[str]] = Field(None, description="Regions for targeting")
    cities: Optional[List[str]] = Field(None, description="Cities for targeting")
    postal_codes: Optional[List[str]] = Field(None, description="Postal codes for targeting")
    radius: Optional[int] = Field(None, description="Radius in kilometers")
    latitude: Optional[float] = Field(None, description="Latitude for radius targeting")
    longitude: Optional[float] = Field(None, description="Longitude for radius targeting")


class BehavioralCriteria(BaseAPIModel):
    """Behavioral criteria for audience targeting."""
    online_behaviors: Optional[List[str]] = Field(None, description="Online behaviors")
    purchasing_behaviors: Optional[List[str]] = Field(None, description="Purchasing behaviors")
    app_usage: Optional[List[str]] = Field(None, description="App usage patterns")
    device_types: Optional[List[str]] = Field(None, description="Device types")
    browser_types: Optional[List[str]] = Field(None, description="Browser types")
    time_patterns: Optional[List[str]] = Field(None, description="Time patterns of activity")


class RetargetingCriteria(BaseAPIModel):
    """Retargeting criteria for audience targeting."""
    website_visitors: Optional[List[str]] = Field(None, description="Website visitors")
    product_viewers: Optional[List[str]] = Field(None, description="Product viewers")
    cart_abandoners: Optional[List[str]] = Field(None, description="Cart abandoners")
    past_purchasers: Optional[List[str]] = Field(None, description="Past purchasers")
    event_days: Optional[int] = Field(None, description="Days since event")


class AudienceCriteria(BaseAPIModel):
    """Combined criteria for audience targeting."""
    demographic: Optional[DemographicCriteria] = Field(None, description="Demographic criteria")
    interest: Optional[InterestCriteria] = Field(None, description="Interest criteria")
    geographic: Optional[GeographicCriteria] = Field(None, description="Geographic criteria")
    behavioral: Optional[BehavioralCriteria] = Field(None, description="Behavioral criteria")
    retargeting: Optional[RetargetingCriteria] = Field(None, description="Retargeting criteria")
    custom_attributes: Optional[Dict[str, Any]] = Field(None, description="Custom attributes")


class AudienceSize(BaseAPIModel):
    """Size estimate for an audience."""
    estimated_size: int = Field(..., description="Estimated audience size")
    precision: float = Field(..., description="Precision of the estimate (0-1)")
    reach_percentage: float = Field(..., description="Percentage of total potential reach")
    data_source: str = Field(..., description="Source of the estimate data")
    last_updated: datetime = Field(..., description="When the estimate was last updated")


class Audience(BaseAPIModel):
    """An audience definition for campaign targeting."""
    id: uuid.UUID = Field(..., description="Unique identifier")
    name: str = Field(..., description="Audience name")
    description: Optional[str] = Field(None, description="Audience description")
    type: AudienceType = Field(..., description="Audience type")
    status: AudienceStatus = Field(..., description="Audience status")
    criteria: AudienceCriteria = Field(..., description="Targeting criteria")
    size_estimate: Optional[AudienceSize] = Field(None, description="Audience size estimate")
    campaign_ids: List[uuid.UUID] = Field(default_factory=list, description="Associated campaign IDs")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class AudienceCreate(BaseAPIModel):
    """Request model for creating an audience."""
    name: str = Field(..., description="Audience name")
    description: Optional[str] = Field(None, description="Audience description")
    type: AudienceType = Field(..., description="Audience type")
    criteria: AudienceCriteria = Field(..., description="Targeting criteria")
    campaign_ids: Optional[List[uuid.UUID]] = Field(None, description="Associated campaign IDs")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AudienceUpdate(BaseAPIModel):
    """Request model for updating an audience."""
    name: Optional[str] = Field(None, description="Audience name")
    description: Optional[str] = Field(None, description="Audience description")
    status: Optional[AudienceStatus] = Field(None, description="Audience status")
    criteria: Optional[AudienceCriteria] = Field(None, description="Targeting criteria")
    campaign_ids: Optional[List[uuid.UUID]] = Field(None, description="Associated campaign IDs")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AudienceFilterParams(BaseAPIModel):
    """Filter parameters for listing audiences."""
    status: Optional[List[AudienceStatus]] = Field(None, description="Filter by status")
    type: Optional[List[AudienceType]] = Field(None, description="Filter by audience type")
    campaign_id: Optional[uuid.UUID] = Field(None, description="Filter by associated campaign")
    tag: Optional[List[str]] = Field(None, description="Filter by tags")
    query: Optional[str] = Field(None, description="Search query for name or description")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date after")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date before")


class AudienceSizeEstimateRequest(BaseAPIModel):
    """Request model for estimating audience size."""
    criteria: AudienceCriteria = Field(..., description="Targeting criteria")
    platform: Optional[str] = Field(None, description="Platform to estimate for (e.g., facebook, google)")
    include_breakdown: Optional[bool] = Field(False, description="Include demographic breakdown")


class AudienceSizeEstimateResponse(BaseAPIModel):
    """Response model for audience size estimation."""
    size: AudienceSize = Field(..., description="Audience size estimate")
    breakdown: Optional[Dict[str, Any]] = Field(None, description="Demographic breakdown")
    recommendations: Optional[List[str]] = Field(None, description="Targeting recommendations")


class AudienceInsights(BaseAPIModel):
    """Insights and analytics about an audience."""
    audience_id: uuid.UUID = Field(..., description="Audience ID")
    total_impressions: int = Field(..., description="Total impressions")
    total_clicks: int = Field(..., description="Total clicks")
    click_through_rate: float = Field(..., description="Click-through rate")
    conversion_rate: Optional[float] = Field(None, description="Conversion rate")
    engagement_rate: Optional[float] = Field(None, description="Engagement rate")
    cost_per_click: Optional[float] = Field(None, description="Average cost per click")
    cost_per_acquisition: Optional[float] = Field(None, description="Average cost per acquisition")
    top_performing_creatives: List[uuid.UUID] = Field(default_factory=list, description="Top performing creatives")
    growth_rate: Optional[float] = Field(None, description="Audience growth rate")
    churn_rate: Optional[float] = Field(None, description="Audience churn rate")
    last_updated: datetime = Field(..., description="Last update timestamp")