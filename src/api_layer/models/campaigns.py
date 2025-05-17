"""
Campaign models for the API layer.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator

from src.api_layer.models.base import BaseAPIModel


class CampaignStatus(str, Enum):
    """Status values for a campaign."""
    
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CampaignType(str, Enum):
    """Types of advertising campaigns."""
    
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    CONVERSION = "conversion"
    RETENTION = "retention"
    CUSTOM = "custom"


class CampaignObjective(str, Enum):
    """Campaign objectives."""
    
    BRAND_AWARENESS = "brand_awareness"
    REACH = "reach"
    TRAFFIC = "traffic"
    ENGAGEMENT = "engagement"
    APP_INSTALLS = "app_installs"
    VIDEO_VIEWS = "video_views"
    LEAD_GENERATION = "lead_generation"
    CONVERSIONS = "conversions"
    CATALOG_SALES = "catalog_sales"
    STORE_TRAFFIC = "store_traffic"
    CUSTOMER_ACQUISITION = "customer_acquisition"
    CUSTOMER_RETENTION = "customer_retention"
    CUSTOM = "custom"


class CampaignBudgetType(str, Enum):
    """Budget types for campaigns."""
    
    DAILY = "daily"
    LIFETIME = "lifetime"
    MONTHLY = "monthly"


class TargetingCriteria(BaseAPIModel):
    """Targeting criteria for a campaign."""
    
    demographics: Optional[Dict[str, Any]] = Field(
        None,
        description="Demographic targeting parameters"
    )
    interests: Optional[List[str]] = Field(
        None,
        description="Interest-based targeting"
    )
    behaviors: Optional[List[str]] = Field(
        None,
        description="Behavior-based targeting"
    )
    locations: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Geographic targeting"
    )
    exclusions: Optional[Dict[str, Any]] = Field(
        None,
        description="Targeting exclusions"
    )
    custom_audiences: Optional[List[UUID]] = Field(
        None,
        description="Custom audience IDs to target"
    )


class CampaignBudget(BaseAPIModel):
    """Budget configuration for a campaign."""
    
    amount: float = Field(
        ...,
        description="Budget amount in the specified currency",
        gt=0
    )
    currency: str = Field(
        ...,
        description="Currency code (ISO 4217)",
        min_length=3,
        max_length=3
    )
    type: CampaignBudgetType = Field(
        ...,
        description="Type of budget allocation"
    )
    
    @validator("currency")
    def currency_must_be_uppercase(cls, v):
        return v.upper()


class CampaignPerformanceMetrics(BaseAPIModel):
    """Performance metrics for a campaign."""
    
    impressions: int = Field(
        0,
        description="Number of impressions"
    )
    clicks: int = Field(
        0,
        description="Number of clicks"
    )
    ctr: float = Field(
        0.0,
        description="Click-through rate (percentage)"
    )
    spend: float = Field(
        0.0,
        description="Amount spent"
    )
    conversions: int = Field(
        0,
        description="Number of conversions"
    )
    cpa: Optional[float] = Field(
        None,
        description="Cost per acquisition"
    )
    roas: Optional[float] = Field(
        None,
        description="Return on ad spend"
    )
    reach: Optional[int] = Field(
        None,
        description="Unique users reached"
    )
    frequency: Optional[float] = Field(
        None,
        description="Average frequency of impressions per user"
    )
    engagement_rate: Optional[float] = Field(
        None,
        description="Engagement rate (percentage)"
    )


class Campaign(BaseAPIModel):
    """Full campaign model with all fields."""
    
    id: UUID = Field(
        ...,
        description="Unique identifier for the campaign"
    )
    name: str = Field(
        ...,
        description="Campaign name",
        max_length=100
    )
    description: Optional[str] = Field(
        None,
        description="Campaign description",
        max_length=2000
    )
    status: CampaignStatus = Field(
        ...,
        description="Current campaign status"
    )
    type: CampaignType = Field(
        ...,
        description="Campaign type"
    )
    objective: CampaignObjective = Field(
        ...,
        description="Campaign objective"
    )
    start_date: datetime = Field(
        ...,
        description="Scheduled start date and time"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="Scheduled end date and time"
    )
    budget: CampaignBudget = Field(
        ...,
        description="Campaign budget configuration"
    )
    targeting: TargetingCriteria = Field(
        ...,
        description="Targeting criteria"
    )
    creatives: List[UUID] = Field(
        [],
        description="Associated creative IDs"
    )
    performance: Optional[CampaignPerformanceMetrics] = Field(
        None,
        description="Campaign performance metrics"
    )
    tags: List[str] = Field(
        [],
        description="Tags for categorizing the campaign"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional campaign metadata"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the campaign was created"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the campaign was last updated"
    )


class CampaignCreate(BaseAPIModel):
    """Model for creating a new campaign."""
    
    name: str = Field(
        ...,
        description="Campaign name",
        max_length=100
    )
    description: Optional[str] = Field(
        None,
        description="Campaign description",
        max_length=2000
    )
    type: CampaignType = Field(
        ...,
        description="Campaign type"
    )
    objective: CampaignObjective = Field(
        ...,
        description="Campaign objective"
    )
    start_date: datetime = Field(
        ...,
        description="Scheduled start date and time"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="Scheduled end date and time"
    )
    budget: CampaignBudget = Field(
        ...,
        description="Campaign budget configuration"
    )
    targeting: TargetingCriteria = Field(
        ...,
        description="Targeting criteria"
    )
    creatives: Optional[List[UUID]] = Field(
        None,
        description="Associated creative IDs"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Tags for categorizing the campaign"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional campaign metadata"
    )
    
    @validator("end_date")
    def end_date_after_start_date(cls, v, values):
        if v and "start_date" in values and v <= values["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class CampaignUpdate(BaseAPIModel):
    """Model for updating an existing campaign."""
    
    name: Optional[str] = Field(
        None,
        description="Campaign name",
        max_length=100
    )
    description: Optional[str] = Field(
        None,
        description="Campaign description",
        max_length=2000
    )
    status: Optional[CampaignStatus] = Field(
        None,
        description="Current campaign status"
    )
    type: Optional[CampaignType] = Field(
        None,
        description="Campaign type"
    )
    objective: Optional[CampaignObjective] = Field(
        None,
        description="Campaign objective"
    )
    start_date: Optional[datetime] = Field(
        None,
        description="Scheduled start date and time"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="Scheduled end date and time"
    )
    budget: Optional[CampaignBudget] = Field(
        None,
        description="Campaign budget configuration"
    )
    targeting: Optional[TargetingCriteria] = Field(
        None,
        description="Targeting criteria"
    )
    creatives: Optional[List[UUID]] = Field(
        None,
        description="Associated creative IDs"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Tags for categorizing the campaign"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional campaign metadata"
    )
    
    @validator("end_date")
    def end_date_after_start_date(cls, v, values):
        if v is not None:
            start_date = values.get("start_date")
            if start_date is not None and v <= start_date:
                raise ValueError("end_date must be after start_date")
        return v
