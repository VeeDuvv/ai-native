# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file defines the different places where we can show our ads, like
# social media or websites, and how we plan to spend money on these ads.

# High School Explanation:
# This module implements data models for media planning and buying in advertising
# campaigns. It defines structures for channels, placements, budgets, and bidding
# strategies used across the API layer for validation and serialization.

"""
Media models for the API layer.

This module provides the Pydantic models for media planning and buying,
including channels, placements, budgets, and targeting parameters.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
import uuid
from pydantic import BaseModel, Field, HttpUrl, PositiveFloat

from src.api_layer.models.base import BaseAPIModel


class MediaChannelType(str, Enum):
    """Types of media channels."""
    SOCIAL = "social"
    DISPLAY = "display"
    SEARCH = "search"
    VIDEO = "video"
    AUDIO = "audio"
    NATIVE = "native"
    EMAIL = "email"
    MOBILE = "mobile"
    OOH = "out_of_home"
    PRINT = "print"
    TV = "television"
    CONNECTED_TV = "connected_tv"


class MediaChannelPlatform(str, Enum):
    """Media channel platforms."""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    GOOGLE = "google"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    PINTEREST = "pinterest"
    AMAZON = "amazon"
    SPOTIFY = "spotify"
    OTHER = "other"


class MediaPlacementStatus(str, Enum):
    """Status of a media placement."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class BudgetType(str, Enum):
    """Types of budget allocations."""
    DAILY = "daily"
    LIFETIME = "lifetime"
    MONTHLY = "monthly"
    WEEKLY = "weekly"


class MediaPacingStrategy(str, Enum):
    """Strategies for pacing budget spending."""
    EVEN = "even"
    ACCELERATED = "accelerated"
    FRONT_LOADED = "front_loaded"
    BACK_LOADED = "back_loaded"
    DAYPARTED = "dayparted"


class BiddingStrategy(str, Enum):
    """Bidding strategies for media buying."""
    CPM = "cpm"
    CPC = "cpc"
    CPA = "cpa"
    CPV = "cpv"
    CPL = "cpl"
    OPTIMIZE_FOR_CONVERSIONS = "optimize_for_conversions"
    OPTIMIZE_FOR_CLICKS = "optimize_for_clicks"
    OPTIMIZE_FOR_IMPRESSIONS = "optimize_for_impressions"
    TARGET_ROAS = "target_roas"
    MANUAL = "manual"


class MediaBudget(BaseAPIModel):
    """Budget allocation for media spending."""
    id: uuid.UUID = Field(..., description="Unique identifier")
    campaign_id: uuid.UUID = Field(..., description="Associated campaign ID")
    channel_id: Optional[uuid.UUID] = Field(None, description="Associated channel ID if channel-specific")
    name: str = Field(..., description="Budget name")
    amount: PositiveFloat = Field(..., description="Budget amount")
    currency: str = Field("USD", description="Currency code")
    type: BudgetType = Field(..., description="Budget type")
    pacing_strategy: MediaPacingStrategy = Field(..., description="Pacing strategy")
    start_date: date = Field(..., description="Budget start date")
    end_date: Optional[date] = Field(None, description="Budget end date")
    spent_amount: PositiveFloat = Field(0.0, description="Amount spent so far")
    daily_caps: Optional[Dict[str, PositiveFloat]] = Field(None, description="Daily spending caps by date")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class MediaChannel(BaseAPIModel):
    """A media channel for advertising."""
    id: uuid.UUID = Field(..., description="Unique identifier")
    campaign_id: uuid.UUID = Field(..., description="Associated campaign ID")
    name: str = Field(..., description="Channel name")
    description: Optional[str] = Field(None, description="Channel description")
    type: MediaChannelType = Field(..., description="Channel type")
    platform: MediaChannelPlatform = Field(..., description="Channel platform")
    external_account_id: Optional[str] = Field(None, description="External platform account ID")
    external_account_name: Optional[str] = Field(None, description="External platform account name")
    budget_id: Optional[uuid.UUID] = Field(None, description="Associated budget ID")
    placements: List[uuid.UUID] = Field(default_factory=list, description="Associated placement IDs")
    audience_ids: List[uuid.UUID] = Field(default_factory=list, description="Associated audience IDs")
    creative_ids: List[uuid.UUID] = Field(default_factory=list, description="Associated creative IDs")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Channel performance metrics")
    status: MediaPlacementStatus = Field(MediaPlacementStatus.DRAFT, description="Channel status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class MediaPlacement(BaseAPIModel):
    """A media placement within a channel."""
    id: uuid.UUID = Field(..., description="Unique identifier")
    channel_id: uuid.UUID = Field(..., description="Associated channel ID")
    campaign_id: uuid.UUID = Field(..., description="Associated campaign ID")
    name: str = Field(..., description="Placement name")
    description: Optional[str] = Field(None, description="Placement description")
    external_placement_id: Optional[str] = Field(None, description="External platform placement ID")
    audience_id: Optional[uuid.UUID] = Field(None, description="Associated audience ID")
    creative_ids: List[uuid.UUID] = Field(default_factory=list, description="Associated creative IDs")
    start_date: datetime = Field(..., description="Placement start date")
    end_date: Optional[datetime] = Field(None, description="Placement end date")
    bidding_strategy: BiddingStrategy = Field(..., description="Bidding strategy")
    bid_amount: Optional[PositiveFloat] = Field(None, description="Bid amount")
    budget_allocation: Optional[PositiveFloat] = Field(None, description="Budget allocation amount")
    status: MediaPlacementStatus = Field(MediaPlacementStatus.DRAFT, description="Placement status")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Placement performance metrics")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class MediaBudgetCreate(BaseAPIModel):
    """Request model for creating a media budget."""
    campaign_id: uuid.UUID = Field(..., description="Associated campaign ID")
    channel_id: Optional[uuid.UUID] = Field(None, description="Associated channel ID if channel-specific")
    name: str = Field(..., description="Budget name")
    amount: PositiveFloat = Field(..., description="Budget amount")
    currency: str = Field("USD", description="Currency code")
    type: BudgetType = Field(..., description="Budget type")
    pacing_strategy: MediaPacingStrategy = Field(..., description="Pacing strategy")
    start_date: date = Field(..., description="Budget start date")
    end_date: Optional[date] = Field(None, description="Budget end date")
    daily_caps: Optional[Dict[str, PositiveFloat]] = Field(None, description="Daily spending caps by date")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MediaBudgetUpdate(BaseAPIModel):
    """Request model for updating a media budget."""
    name: Optional[str] = Field(None, description="Budget name")
    amount: Optional[PositiveFloat] = Field(None, description="Budget amount")
    currency: Optional[str] = Field(None, description="Currency code")
    type: Optional[BudgetType] = Field(None, description="Budget type")
    pacing_strategy: Optional[MediaPacingStrategy] = Field(None, description="Pacing strategy")
    start_date: Optional[date] = Field(None, description="Budget start date")
    end_date: Optional[date] = Field(None, description="Budget end date")
    spent_amount: Optional[PositiveFloat] = Field(None, description="Amount spent so far")
    daily_caps: Optional[Dict[str, PositiveFloat]] = Field(None, description="Daily spending caps by date")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MediaChannelCreate(BaseAPIModel):
    """Request model for creating a media channel."""
    campaign_id: uuid.UUID = Field(..., description="Associated campaign ID")
    name: str = Field(..., description="Channel name")
    description: Optional[str] = Field(None, description="Channel description")
    type: MediaChannelType = Field(..., description="Channel type")
    platform: MediaChannelPlatform = Field(..., description="Channel platform")
    external_account_id: Optional[str] = Field(None, description="External platform account ID")
    external_account_name: Optional[str] = Field(None, description="External platform account name")
    budget_id: Optional[uuid.UUID] = Field(None, description="Associated budget ID")
    audience_ids: Optional[List[uuid.UUID]] = Field(None, description="Associated audience IDs")
    creative_ids: Optional[List[uuid.UUID]] = Field(None, description="Associated creative IDs")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MediaChannelUpdate(BaseAPIModel):
    """Request model for updating a media channel."""
    name: Optional[str] = Field(None, description="Channel name")
    description: Optional[str] = Field(None, description="Channel description")
    external_account_id: Optional[str] = Field(None, description="External platform account ID")
    external_account_name: Optional[str] = Field(None, description="External platform account name")
    budget_id: Optional[uuid.UUID] = Field(None, description="Associated budget ID")
    audience_ids: Optional[List[uuid.UUID]] = Field(None, description="Associated audience IDs")
    creative_ids: Optional[List[uuid.UUID]] = Field(None, description="Associated creative IDs")
    status: Optional[MediaPlacementStatus] = Field(None, description="Channel status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MediaPlacementCreate(BaseAPIModel):
    """Request model for creating a media placement."""
    channel_id: uuid.UUID = Field(..., description="Associated channel ID")
    campaign_id: uuid.UUID = Field(..., description="Associated campaign ID")
    name: str = Field(..., description="Placement name")
    description: Optional[str] = Field(None, description="Placement description")
    external_placement_id: Optional[str] = Field(None, description="External platform placement ID")
    audience_id: Optional[uuid.UUID] = Field(None, description="Associated audience ID")
    creative_ids: Optional[List[uuid.UUID]] = Field(None, description="Associated creative IDs")
    start_date: datetime = Field(..., description="Placement start date")
    end_date: Optional[datetime] = Field(None, description="Placement end date")
    bidding_strategy: BiddingStrategy = Field(..., description="Bidding strategy")
    bid_amount: Optional[PositiveFloat] = Field(None, description="Bid amount")
    budget_allocation: Optional[PositiveFloat] = Field(None, description="Budget allocation amount")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MediaPlacementUpdate(BaseAPIModel):
    """Request model for updating a media placement."""
    name: Optional[str] = Field(None, description="Placement name")
    description: Optional[str] = Field(None, description="Placement description")
    external_placement_id: Optional[str] = Field(None, description="External platform placement ID")
    audience_id: Optional[uuid.UUID] = Field(None, description="Associated audience ID")
    creative_ids: Optional[List[uuid.UUID]] = Field(None, description="Associated creative IDs")
    start_date: Optional[datetime] = Field(None, description="Placement start date")
    end_date: Optional[datetime] = Field(None, description="Placement end date")
    bidding_strategy: Optional[BiddingStrategy] = Field(None, description="Bidding strategy")
    bid_amount: Optional[PositiveFloat] = Field(None, description="Bid amount")
    budget_allocation: Optional[PositiveFloat] = Field(None, description="Budget allocation amount")
    status: Optional[MediaPlacementStatus] = Field(None, description="Placement status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")