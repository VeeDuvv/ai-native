# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file handles requests about where to show our advertisements, like on
# websites or social media. It's like a manager who decides where to place
# posters and how much money to spend on each place.

# High School Explanation:
# This module implements the API endpoints for managing media planning and buying
# operations in the advertising platform. It provides functionality for creating,
# retrieving, and updating media channels, placements, and budgets to optimize
# ad delivery and performance.

"""
Media controller for the API layer.

This module provides the API endpoints for creating, retrieving,
updating, and deleting media channels, placements, and budgets,
as well as retrieving performance data.
"""

import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path, status
from fastapi.responses import JSONResponse

from src.api_layer.core.responses import create_response, create_error_response
from src.api_layer.core.auth import User, get_current_active_user, has_role
from src.api_layer.core.agent_coordinator import coordinator
from src.api_layer.models.base import StandardRequest, StandardResponse, PaginatedResponse
from src.api_layer.models.media import (
    MediaChannel,
    MediaChannelCreate,
    MediaChannelUpdate,
    MediaBudget,
    MediaBudgetCreate,
    MediaBudgetUpdate,
    MediaPlacement,
    MediaPlacementCreate,
    MediaPlacementUpdate,
    MediaChannelType,
    MediaPlacementStatus,
    BudgetType,
    MediaPacingStrategy,
    BiddingStrategy
)

# Set up logging
logger = logging.getLogger("api.controllers.media")

# Create router
router = APIRouter(
    prefix="/media",
    tags=["Media"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
)

# In-memory storage for media components (to be replaced with a database)
CHANNELS = {}
BUDGETS = {}
PLACEMENTS = {}


# --- CHANNELS ---

@router.get(
    "/channels",
    response_model=PaginatedResponse[MediaChannel],
    summary="List media channels",
    description="Retrieve a paginated list of media channels with optional filtering"
)
async def list_channels(
    # Pagination parameters
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    # Filter parameters
    type: Optional[List[MediaChannelType]] = Query(None, description="Filter by channel type"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    tag: Optional[List[str]] = Query(None, description="Filter by tags"),
    # Search parameters
    query: Optional[str] = Query(None, description="Search query"),
    # Sort parameters
    sort_by: Optional[str] = Query("name", description="Sort field"),
    sort_order: Optional[str] = Query("asc", description="Sort order (asc or desc)"),
    # Auth
    user: User = Depends(get_current_active_user)
):
    """
    List and filter media channels.
    
    Args:
        page: Page number for pagination
        per_page: Number of items per page
        type: Filter by channel type
        platform: Filter by platform
        active: Filter by active status
        tag: Filter by tags
        query: Search query for channel name or description
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        user: Current authenticated user
        
    Returns:
        PaginatedResponse[MediaChannel]: Paginated list of media channels
    """
    # Filter channels (this would typically be done in a database query)
    filtered_channels = list(CHANNELS.values())
    
    # Apply filters
    if type:
        filtered_channels = [c for c in filtered_channels if c.type in type]
    
    if platform:
        filtered_channels = [c for c in filtered_channels if platform.lower() in c.platform.lower()]
    
    if active is not None:
        filtered_channels = [c for c in filtered_channels if c.active == active]
    
    if tag:
        filtered_channels = [c for c in filtered_channels if any(t in c.tags for t in tag)]
    
    if query:
        query_lower = query.lower()
        filtered_channels = [
            c for c in filtered_channels 
            if query_lower in c.name.lower() or 
               (c.description and query_lower in c.description.lower()) or
               query_lower in c.platform.lower()
        ]
    
    # Sort channels
    reverse = sort_order.lower() == "desc"
    try:
        filtered_channels.sort(key=lambda c: getattr(c, sort_by), reverse=reverse)
    except AttributeError:
        # Default to name if the sort field doesn't exist
        filtered_channels.sort(key=lambda c: c.name, reverse=reverse)
    
    # Calculate pagination
    total_items = len(filtered_channels)
    total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1
    
    # Ensure page is within bounds
    if page > total_pages:
        page = total_pages
    
    # Paginate results
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_channels = filtered_channels[start_idx:end_idx]
    
    # Create pagination metadata
    pagination_meta = {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "items_per_page": per_page
    }
    
    # Create pagination links
    base_url = f"/api/v1/media/channels?per_page={per_page}"
    for param, value in {
        "type": type,
        "platform": platform,
        "active": active,
        "tag": tag,
        "query": query,
        "sort_by": sort_by,
        "sort_order": sort_order
    }.items():
        if value is not None:
            if isinstance(value, list):
                for item in value:
                    base_url += f"&{param}={item}"
            else:
                base_url += f"&{param}={value}"
    
    pagination_links = {
        "self": f"{base_url}&page={page}",
        "first": f"{base_url}&page=1",
        "last": f"{base_url}&page={total_pages}"
    }
    
    if page > 1:
        pagination_links["prev"] = f"{base_url}&page={page - 1}"
    
    if page < total_pages:
        pagination_links["next"] = f"{base_url}&page={page + 1}"
    
    return {
        "data": paginated_channels,
        "meta": {
            "pagination": pagination_meta
        },
        "links": pagination_links
    }


@router.post(
    "/channels",
    response_model=StandardResponse[MediaChannel],
    status_code=status.HTTP_201_CREATED,
    summary="Create media channel",
    description="Create a new media channel for ad placement"
)
async def create_channel(
    request: StandardRequest[MediaChannelCreate],
    user: User = Depends(has_role(["admin", "media_manager"]))
):
    """
    Create a new media channel.
    
    Args:
        request: Channel creation request
        user: Current authenticated user with appropriate role
        
    Returns:
        StandardResponse[MediaChannel]: Newly created media channel
    """
    channel_data = request.data
    
    # Generate a unique ID
    channel_id = uuid.uuid4()
    
    # Get current timestamp
    now = datetime.utcnow()
    
    # Create channel object
    channel = MediaChannel(
        id=channel_id,
        name=channel_data.name,
        type=channel_data.type,
        platform=channel_data.platform,
        description=channel_data.description,
        account_id=channel_data.account_id,
        capabilities=channel_data.capabilities,
        formats=channel_data.formats,
        targeting_options=channel_data.targeting_options,
        api_integration=channel_data.api_integration,
        active=channel_data.active,
        tags=channel_data.tags if channel_data.tags else [],
        metadata=channel_data.metadata,
        created_at=now,
        updated_at=now
    )
    
    # Store the channel
    CHANNELS[str(channel_id)] = channel
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/media/channels/{channel_id}",
        "related": {
            "placements": f"/api/v1/media/channels/{channel_id}/placements"
        }
    }
    
    return create_response(
        data=channel,
        links=links
    )


@router.get(
    "/channels/{channel_id}",
    response_model=StandardResponse[MediaChannel],
    summary="Get media channel",
    description="Retrieve details of a specific media channel"
)
async def get_channel(
    channel_id: uuid.UUID = Path(..., description="Channel ID"),
    user: User = Depends(get_current_active_user)
):
    """
    Get details of a specific media channel.
    
    Args:
        channel_id: Channel ID
        user: Current authenticated user
        
    Returns:
        StandardResponse[MediaChannel]: Media channel details
        
    Raises:
        HTTPException: If the channel does not exist
    """
    channel_id_str = str(channel_id)
    
    # Check if channel exists
    if channel_id_str not in CHANNELS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CHANNEL_NOT_FOUND",
                title="Channel not found",
                detail=f"Media channel with ID {channel_id} does not exist"
            )
        )
    
    channel = CHANNELS[channel_id_str]
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/media/channels/{channel_id}",
        "related": {
            "placements": f"/api/v1/media/channels/{channel_id}/placements"
        }
    }
    
    return create_response(
        data=channel,
        links=links
    )


@router.put(
    "/channels/{channel_id}",
    response_model=StandardResponse[MediaChannel],
    summary="Update media channel",
    description="Update details of a specific media channel"
)
async def update_channel(
    request: StandardRequest[MediaChannelUpdate],
    channel_id: uuid.UUID = Path(..., description="Channel ID"),
    user: User = Depends(has_role(["admin", "media_manager"]))
):
    """
    Update a media channel.
    
    Args:
        request: Channel update request
        channel_id: Channel ID
        user: Current authenticated user with appropriate role
        
    Returns:
        StandardResponse[MediaChannel]: Updated media channel
        
    Raises:
        HTTPException: If the channel does not exist
    """
    channel_id_str = str(channel_id)
    
    # Check if channel exists
    if channel_id_str not in CHANNELS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CHANNEL_NOT_FOUND",
                title="Channel not found",
                detail=f"Media channel with ID {channel_id} does not exist"
            )
        )
    
    channel = CHANNELS[channel_id_str]
    update_data = request.data
    
    # Update channel fields if provided
    if update_data.name is not None:
        channel.name = update_data.name
    
    if update_data.description is not None:
        channel.description = update_data.description
    
    if update_data.account_id is not None:
        channel.account_id = update_data.account_id
    
    if update_data.capabilities is not None:
        channel.capabilities = update_data.capabilities
    
    if update_data.formats is not None:
        channel.formats = update_data.formats
    
    if update_data.targeting_options is not None:
        channel.targeting_options = update_data.targeting_options
    
    if update_data.api_integration is not None:
        channel.api_integration = update_data.api_integration
    
    if update_data.active is not None:
        channel.active = update_data.active
    
    if update_data.tags is not None:
        channel.tags = update_data.tags
    
    if update_data.metadata is not None:
        channel.metadata = update_data.metadata
    
    # Update the timestamp
    channel.updated_at = datetime.utcnow()
    
    # Store the updated channel
    CHANNELS[channel_id_str] = channel
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/media/channels/{channel_id}",
        "related": {
            "placements": f"/api/v1/media/channels/{channel_id}/placements"
        }
    }
    
    return create_response(
        data=channel,
        links=links
    )


@router.delete(
    "/channels/{channel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete media channel",
    description="Delete a specific media channel"
)
async def delete_channel(
    channel_id: uuid.UUID = Path(..., description="Channel ID"),
    user: User = Depends(has_role(["admin", "media_manager"]))
):
    """
    Delete a media channel.
    
    Args:
        channel_id: Channel ID
        user: Current authenticated user with appropriate role
        
    Returns:
        None
        
    Raises:
        HTTPException: If the channel does not exist or has active placements
    """
    channel_id_str = str(channel_id)
    
    # Check if channel exists
    if channel_id_str not in CHANNELS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CHANNEL_NOT_FOUND",
                title="Channel not found",
                detail=f"Media channel with ID {channel_id} does not exist"
            )
        )
    
    # Check if channel has active placements
    has_active_placements = any(
        p.channel_id == channel_id and p.status in [MediaPlacementStatus.ACTIVE, MediaPlacementStatus.PENDING_APPROVAL]
        for p in PLACEMENTS.values()
    )
    
    if has_active_placements:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_error_response(
                status_code=400,
                error_code="CHANNEL_HAS_ACTIVE_PLACEMENTS",
                title="Channel has active placements",
                detail=f"Media channel with ID {channel_id} has active placements and cannot be deleted"
            )
        )
    
    # Remove the channel
    del CHANNELS[channel_id_str]
    
    # No content response
    return None


# --- BUDGETS ---

@router.get(
    "/budgets",
    response_model=PaginatedResponse[MediaBudget],
    summary="List media budgets",
    description="Retrieve a paginated list of media budgets with optional filtering"
)
async def list_budgets(
    # Pagination parameters
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    # Filter parameters
    campaign_id: Optional[uuid.UUID] = Query(None, description="Filter by campaign ID"),
    channel_id: Optional[uuid.UUID] = Query(None, description="Filter by channel ID"),
    type: Optional[List[BudgetType]] = Query(None, description="Filter by budget type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    # Date range parameters
    start_after: Optional[date] = Query(None, description="Filter by start date after"),
    start_before: Optional[date] = Query(None, description="Filter by start date before"),
    end_after: Optional[date] = Query(None, description="Filter by end date after"),
    end_before: Optional[date] = Query(None, description="Filter by end date before"),
    # Search parameters
    query: Optional[str] = Query(None, description="Search query"),
    # Sort parameters
    sort_by: Optional[str] = Query("start_date", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc or desc)"),
    # Auth
    user: User = Depends(get_current_active_user)
):
    """
    List and filter media budgets.
    
    Args:
        page: Page number for pagination
        per_page: Number of items per page
        campaign_id: Filter by campaign ID
        channel_id: Filter by channel ID
        type: Filter by budget type
        status: Filter by status
        start_after: Filter by start date after
        start_before: Filter by start date before
        end_after: Filter by end date after
        end_before: Filter by end date before
        query: Search query for budget name
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        user: Current authenticated user
        
    Returns:
        PaginatedResponse[MediaBudget]: Paginated list of media budgets
    """
    # Filter budgets (this would typically be done in a database query)
    filtered_budgets = list(BUDGETS.values())
    
    # Apply filters
    if campaign_id:
        filtered_budgets = [b for b in filtered_budgets if b.campaign_id == campaign_id]
    
    if channel_id:
        filtered_budgets = [b for b in filtered_budgets if b.channel_id == channel_id]
    
    if type:
        filtered_budgets = [b for b in filtered_budgets if b.type in type]
    
    if status:
        filtered_budgets = [b for b in filtered_budgets if b.status.lower() == status.lower()]
    
    if start_after:
        filtered_budgets = [b for b in filtered_budgets if b.start_date >= start_after]
    
    if start_before:
        filtered_budgets = [b for b in filtered_budgets if b.start_date <= start_before]
    
    if end_after:
        filtered_budgets = [b for b in filtered_budgets if b.end_date and b.end_date >= end_after]
    
    if end_before:
        filtered_budgets = [b for b in filtered_budgets if b.end_date and b.end_date <= end_before]
    
    if query:
        query_lower = query.lower()
        filtered_budgets = [
            b for b in filtered_budgets 
            if query_lower in b.name.lower()
        ]
    
    # Sort budgets
    reverse = sort_order.lower() == "desc"
    try:
        filtered_budgets.sort(key=lambda b: getattr(b, sort_by), reverse=reverse)
    except AttributeError:
        # Default to start_date if the sort field doesn't exist
        filtered_budgets.sort(key=lambda b: b.start_date, reverse=reverse)
    
    # Calculate pagination
    total_items = len(filtered_budgets)
    total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1
    
    # Ensure page is within bounds
    if page > total_pages:
        page = total_pages
    
    # Paginate results
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_budgets = filtered_budgets[start_idx:end_idx]
    
    # Create pagination metadata
    pagination_meta = {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "items_per_page": per_page
    }
    
    # Create pagination links
    base_url = f"/api/v1/media/budgets?per_page={per_page}"
    for param, value in {
        "campaign_id": campaign_id,
        "channel_id": channel_id,
        "type": type,
        "status": status,
        "start_after": start_after,
        "start_before": start_before,
        "end_after": end_after,
        "end_before": end_before,
        "query": query,
        "sort_by": sort_by,
        "sort_order": sort_order
    }.items():
        if value is not None:
            if isinstance(value, list):
                for item in value:
                    base_url += f"&{param}={item}"
            else:
                base_url += f"&{param}={value}"
    
    pagination_links = {
        "self": f"{base_url}&page={page}",
        "first": f"{base_url}&page=1",
        "last": f"{base_url}&page={total_pages}"
    }
    
    if page > 1:
        pagination_links["prev"] = f"{base_url}&page={page - 1}"
    
    if page < total_pages:
        pagination_links["next"] = f"{base_url}&page={page + 1}"
    
    return {
        "data": paginated_budgets,
        "meta": {
            "pagination": pagination_meta
        },
        "links": pagination_links
    }


@router.post(
    "/budgets",
    response_model=StandardResponse[MediaBudget],
    status_code=status.HTTP_201_CREATED,
    summary="Create media budget",
    description="Create a new media budget for ad spend"
)
async def create_budget(
    request: StandardRequest[MediaBudgetCreate],
    user: User = Depends(has_role(["admin", "media_manager", "budget_manager"]))
):
    """
    Create a new media budget.
    
    Args:
        request: Budget creation request
        user: Current authenticated user with appropriate role
        
    Returns:
        StandardResponse[MediaBudget]: Newly created media budget
    """
    budget_data = request.data
    
    # Generate a unique ID
    budget_id = uuid.uuid4()
    
    # Get current timestamp
    now = datetime.utcnow()
    
    # Create budget object
    budget = MediaBudget(
        id=budget_id,
        name=budget_data.name,
        campaign_id=budget_data.campaign_id,
        channel_id=budget_data.channel_id,
        amount=budget_data.amount,
        currency=budget_data.currency,
        type=budget_data.type,
        start_date=budget_data.start_date,
        end_date=budget_data.end_date,
        pacing_strategy=budget_data.pacing_strategy,
        pacing_schedule=budget_data.pacing_schedule,
        spend_to_date=0.0,
        status="active",  # New budgets start as active
        created_at=now,
        updated_at=now
    )
    
    # Store the budget
    BUDGETS[str(budget_id)] = budget
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/media/budgets/{budget_id}",
        "related": {
            "placements": f"/api/v1/media/budgets/{budget_id}/placements"
        }
    }
    
    return create_response(
        data=budget,
        links=links
    )


@router.get(
    "/budgets/{budget_id}",
    response_model=StandardResponse[MediaBudget],
    summary="Get media budget",
    description="Retrieve details of a specific media budget"
)
async def get_budget(
    budget_id: uuid.UUID = Path(..., description="Budget ID"),
    user: User = Depends(get_current_active_user)
):
    """
    Get details of a specific media budget.
    
    Args:
        budget_id: Budget ID
        user: Current authenticated user
        
    Returns:
        StandardResponse[MediaBudget]: Media budget details
        
    Raises:
        HTTPException: If the budget does not exist
    """
    budget_id_str = str(budget_id)
    
    # Check if budget exists
    if budget_id_str not in BUDGETS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="BUDGET_NOT_FOUND",
                title="Budget not found",
                detail=f"Media budget with ID {budget_id} does not exist"
            )
        )
    
    budget = BUDGETS[budget_id_str]
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/media/budgets/{budget_id}",
        "related": {
            "placements": f"/api/v1/media/budgets/{budget_id}/placements"
        }
    }
    
    return create_response(
        data=budget,
        links=links
    )


@router.put(
    "/budgets/{budget_id}",
    response_model=StandardResponse[MediaBudget],
    summary="Update media budget",
    description="Update details of a specific media budget"
)
async def update_budget(
    request: StandardRequest[MediaBudgetUpdate],
    budget_id: uuid.UUID = Path(..., description="Budget ID"),
    user: User = Depends(has_role(["admin", "media_manager", "budget_manager"]))
):
    """
    Update a media budget.
    
    Args:
        request: Budget update request
        budget_id: Budget ID
        user: Current authenticated user with appropriate role
        
    Returns:
        StandardResponse[MediaBudget]: Updated media budget
        
    Raises:
        HTTPException: If the budget does not exist
    """
    budget_id_str = str(budget_id)
    
    # Check if budget exists
    if budget_id_str not in BUDGETS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="BUDGET_NOT_FOUND",
                title="Budget not found",
                detail=f"Media budget with ID {budget_id} does not exist"
            )
        )
    
    budget = BUDGETS[budget_id_str]
    update_data = request.data
    
    # Update budget fields if provided
    if update_data.name is not None:
        budget.name = update_data.name
    
    if update_data.amount is not None:
        budget.amount = update_data.amount
    
    if update_data.type is not None:
        budget.type = update_data.type
    
    if update_data.end_date is not None:
        budget.end_date = update_data.end_date
    
    if update_data.pacing_strategy is not None:
        budget.pacing_strategy = update_data.pacing_strategy
    
    if update_data.pacing_schedule is not None:
        budget.pacing_schedule = update_data.pacing_schedule
    
    if update_data.status is not None:
        budget.status = update_data.status
    
    # Update the timestamp
    budget.updated_at = datetime.utcnow()
    
    # Store the updated budget
    BUDGETS[budget_id_str] = budget
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/media/budgets/{budget_id}",
        "related": {
            "placements": f"/api/v1/media/budgets/{budget_id}/placements"
        }
    }
    
    return create_response(
        data=budget,
        links=links
    )


@router.delete(
    "/budgets/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete media budget",
    description="Delete a specific media budget"
)
async def delete_budget(
    budget_id: uuid.UUID = Path(..., description="Budget ID"),
    user: User = Depends(has_role(["admin", "media_manager", "budget_manager"]))
):
    """
    Delete a media budget.
    
    Args:
        budget_id: Budget ID
        user: Current authenticated user with appropriate role
        
    Returns:
        None
        
    Raises:
        HTTPException: If the budget does not exist or is in use by active placements
    """
    budget_id_str = str(budget_id)
    
    # Check if budget exists
    if budget_id_str not in BUDGETS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="BUDGET_NOT_FOUND",
                title="Budget not found",
                detail=f"Media budget with ID {budget_id} does not exist"
            )
        )
    
    # Check if budget is in use by active placements
    has_active_placements = any(
        p.budget_id == budget_id and p.status in [MediaPlacementStatus.ACTIVE, MediaPlacementStatus.PENDING_APPROVAL]
        for p in PLACEMENTS.values()
    )
    
    if has_active_placements:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_error_response(
                status_code=400,
                error_code="BUDGET_IN_USE",
                title="Budget in use",
                detail=f"Media budget with ID {budget_id} is in use by active placements and cannot be deleted"
            )
        )
    
    # Remove the budget
    del BUDGETS[budget_id_str]
    
    # No content response
    return None


# --- PLACEMENTS ---

@router.get(
    "/placements",
    response_model=PaginatedResponse[MediaPlacement],
    summary="List media placements",
    description="Retrieve a paginated list of media placements with optional filtering"
)
async def list_placements(
    # Pagination parameters
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    # Filter parameters
    campaign_id: Optional[uuid.UUID] = Query(None, description="Filter by campaign ID"),
    channel_id: Optional[uuid.UUID] = Query(None, description="Filter by channel ID"),
    budget_id: Optional[uuid.UUID] = Query(None, description="Filter by budget ID"),
    creative_id: Optional[uuid.UUID] = Query(None, description="Filter by creative ID"),
    status: Optional[List[MediaPlacementStatus]] = Query(None, description="Filter by placement status"),
    tag: Optional[List[str]] = Query(None, description="Filter by tags"),
    # Search parameters
    query: Optional[str] = Query(None, description="Search query"),
    # Date range parameters
    created_after: Optional[datetime] = Query(None, description="Filter by creation date after"),
    created_before: Optional[datetime] = Query(None, description="Filter by creation date before"),
    # Sort parameters
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc or desc)"),
    # Auth
    user: User = Depends(get_current_active_user)
):
    """
    List and filter media placements.
    
    Args:
        page: Page number for pagination
        per_page: Number of items per page
        campaign_id: Filter by campaign ID
        channel_id: Filter by channel ID
        budget_id: Filter by budget ID
        creative_id: Filter by creative ID
        status: Filter by placement status
        tag: Filter by tags
        query: Search query for placement name or description
        created_after: Filter by creation date after
        created_before: Filter by creation date before
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        user: Current authenticated user
        
    Returns:
        PaginatedResponse[MediaPlacement]: Paginated list of media placements
    """
    # Filter placements (this would typically be done in a database query)
    filtered_placements = list(PLACEMENTS.values())
    
    # Apply filters
    if campaign_id:
        filtered_placements = [p for p in filtered_placements if p.campaign_id == campaign_id]
    
    if channel_id:
        filtered_placements = [p for p in filtered_placements if p.channel_id == channel_id]
    
    if budget_id:
        filtered_placements = [p for p in filtered_placements if p.budget_id == budget_id]
    
    if creative_id:
        filtered_placements = [p for p in filtered_placements if creative_id in p.creative_ids]
    
    if status:
        filtered_placements = [p for p in filtered_placements if p.status in status]
    
    if tag:
        filtered_placements = [p for p in filtered_placements if any(t in p.tags for t in tag)]
    
    if query:
        query_lower = query.lower()
        filtered_placements = [
            p for p in filtered_placements 
            if query_lower in p.name.lower() or 
               (p.description and query_lower in p.description.lower())
        ]
    
    if created_after:
        filtered_placements = [p for p in filtered_placements if p.created_at >= created_after]
    
    if created_before:
        filtered_placements = [p for p in filtered_placements if p.created_at <= created_before]
    
    # Sort placements
    reverse = sort_order.lower() == "desc"
    try:
        filtered_placements.sort(key=lambda p: getattr(p, sort_by), reverse=reverse)
    except AttributeError:
        # Default to created_at if the sort field doesn't exist
        filtered_placements.sort(key=lambda p: p.created_at, reverse=reverse)
    
    # Calculate pagination
    total_items = len(filtered_placements)
    total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1
    
    # Ensure page is within bounds
    if page > total_pages:
        page = total_pages
    
    # Paginate results
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_placements = filtered_placements[start_idx:end_idx]
    
    # Create pagination metadata
    pagination_meta = {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "items_per_page": per_page
    }
    
    # Create pagination links
    base_url = f"/api/v1/media/placements?per_page={per_page}"
    for param, value in {
        "campaign_id": campaign_id,
        "channel_id": channel_id,
        "budget_id": budget_id,
        "creative_id": creative_id,
        "status": status,
        "tag": tag,
        "query": query,
        "created_after": created_after,
        "created_before": created_before,
        "sort_by": sort_by,
        "sort_order": sort_order
    }.items():
        if value is not None:
            if isinstance(value, list):
                for item in value:
                    base_url += f"&{param}={item}"
            else:
                base_url += f"&{param}={value}"
    
    pagination_links = {
        "self": f"{base_url}&page={page}",
        "first": f"{base_url}&page=1",
        "last": f"{base_url}&page={total_pages}"
    }
    
    if page > 1:
        pagination_links["prev"] = f"{base_url}&page={page - 1}"
    
    if page < total_pages:
        pagination_links["next"] = f"{base_url}&page={page + 1}"
    
    return {
        "data": paginated_placements,
        "meta": {
            "pagination": pagination_meta
        },
        "links": pagination_links
    }


@router.post(
    "/placements",
    response_model=StandardResponse[MediaPlacement],
    status_code=status.HTTP_201_CREATED,
    summary="Create media placement",
    description="Create a new media placement for ad delivery"
)
async def create_placement(
    request: StandardRequest[MediaPlacementCreate],
    user: User = Depends(has_role(["admin", "media_manager"]))
):
    """
    Create a new media placement.
    
    Args:
        request: Placement creation request
        user: Current authenticated user with appropriate role
        
    Returns:
        StandardResponse[MediaPlacement]: Newly created media placement
    """
    placement_data = request.data
    
    # Generate a unique ID
    placement_id = uuid.uuid4()
    
    # Get current timestamp
    now = datetime.utcnow()
    
    # Verify channel exists
    channel_id_str = str(placement_data.channel_id)
    if channel_id_str not in CHANNELS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CHANNEL_NOT_FOUND",
                title="Channel not found",
                detail=f"Media channel with ID {placement_data.channel_id} does not exist"
            )
        )
    
    # Verify budget exists
    budget_id_str = str(placement_data.budget_id)
    if budget_id_str not in BUDGETS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="BUDGET_NOT_FOUND",
                title="Budget not found",
                detail=f"Media budget with ID {placement_data.budget_id} does not exist"
            )
        )
    
    # Create placement object
    placement = MediaPlacement(
        id=placement_id,
        name=placement_data.name,
        description=placement_data.description,
        campaign_id=placement_data.campaign_id,
        channel_id=placement_data.channel_id,
        creative_ids=placement_data.creative_ids,
        budget_id=placement_data.budget_id,
        status=MediaPlacementStatus.DRAFT,  # New placements start as drafts
        targeting=placement_data.targeting,
        bid_config=placement_data.bid_config,
        delivery_settings=placement_data.delivery_settings,
        performance=None,  # Will be updated as the placement runs
        external_id=placement_data.external_id,
        tags=placement_data.tags if placement_data.tags else [],
        metadata=placement_data.metadata,
        created_at=now,
        updated_at=now
    )
    
    # Store the placement
    PLACEMENTS[str(placement_id)] = placement
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/media/placements/{placement_id}",
        "related": {
            "channel": f"/api/v1/media/channels/{placement_data.channel_id}",
            "budget": f"/api/v1/media/budgets/{placement_data.budget_id}",
            "campaign": f"/api/v1/campaigns/{placement_data.campaign_id}"
        }
    }
    
    return create_response(
        data=placement,
        links=links
    )


@router.get(
    "/placements/{placement_id}",
    response_model=StandardResponse[MediaPlacement],
    summary="Get media placement",
    description="Retrieve details of a specific media placement"
)
async def get_placement(
    placement_id: uuid.UUID = Path(..., description="Placement ID"),
    user: User = Depends(get_current_active_user)
):
    """
    Get details of a specific media placement.
    
    Args:
        placement_id: Placement ID
        user: Current authenticated user
        
    Returns:
        StandardResponse[MediaPlacement]: Media placement details
        
    Raises:
        HTTPException: If the placement does not exist
    """
    placement_id_str = str(placement_id)
    
    # Check if placement exists
    if placement_id_str not in PLACEMENTS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="PLACEMENT_NOT_FOUND",
                title="Placement not found",
                detail=f"Media placement with ID {placement_id} does not exist"
            )
        )
    
    placement = PLACEMENTS[placement_id_str]
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/media/placements/{placement_id}",
        "related": {
            "channel": f"/api/v1/media/channels/{placement.channel_id}",
            "budget": f"/api/v1/media/budgets/{placement.budget_id}",
            "campaign": f"/api/v1/campaigns/{placement.campaign_id}"
        }
    }
    
    return create_response(
        data=placement,
        links=links
    )


@router.put(
    "/placements/{placement_id}",
    response_model=StandardResponse[MediaPlacement],
    summary="Update media placement",
    description="Update details of a specific media placement"
)
async def update_placement(
    request: StandardRequest[MediaPlacementUpdate],
    placement_id: uuid.UUID = Path(..., description="Placement ID"),
    user: User = Depends(has_role(["admin", "media_manager"]))
):
    """
    Update a media placement.
    
    Args:
        request: Placement update request
        placement_id: Placement ID
        user: Current authenticated user with appropriate role
        
    Returns:
        StandardResponse[MediaPlacement]: Updated media placement
        
    Raises:
        HTTPException: If the placement does not exist
    """
    placement_id_str = str(placement_id)
    
    # Check if placement exists
    if placement_id_str not in PLACEMENTS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="PLACEMENT_NOT_FOUND",
                title="Placement not found",
                detail=f"Media placement with ID {placement_id} does not exist"
            )
        )
    
    placement = PLACEMENTS[placement_id_str]
    update_data = request.data
    
    # Verify budget exists if provided
    if update_data.budget_id is not None:
        budget_id_str = str(update_data.budget_id)
        if budget_id_str not in BUDGETS:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=create_error_response(
                    status_code=404,
                    error_code="BUDGET_NOT_FOUND",
                    title="Budget not found",
                    detail=f"Media budget with ID {update_data.budget_id} does not exist"
                )
            )
    
    # Update placement fields if provided
    if update_data.name is not None:
        placement.name = update_data.name
    
    if update_data.description is not None:
        placement.description = update_data.description
    
    if update_data.status is not None:
        placement.status = update_data.status
    
    if update_data.creative_ids is not None:
        placement.creative_ids = update_data.creative_ids
    
    if update_data.budget_id is not None:
        placement.budget_id = update_data.budget_id
    
    if update_data.targeting is not None:
        placement.targeting = update_data.targeting
    
    if update_data.bid_config is not None:
        placement.bid_config = update_data.bid_config
    
    if update_data.delivery_settings is not None:
        placement.delivery_settings = update_data.delivery_settings
    
    if update_data.external_id is not None:
        placement.external_id = update_data.external_id
    
    if update_data.tags is not None:
        placement.tags = update_data.tags
    
    if update_data.metadata is not None:
        placement.metadata = update_data.metadata
    
    # Update the timestamp
    placement.updated_at = datetime.utcnow()
    
    # Store the updated placement
    PLACEMENTS[placement_id_str] = placement
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/media/placements/{placement_id}",
        "related": {
            "channel": f"/api/v1/media/channels/{placement.channel_id}",
            "budget": f"/api/v1/media/budgets/{placement.budget_id}",
            "campaign": f"/api/v1/campaigns/{placement.campaign_id}"
        }
    }
    
    return create_response(
        data=placement,
        links=links
    )


@router.delete(
    "/placements/{placement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete media placement",
    description="Delete a specific media placement"
)
async def delete_placement(
    placement_id: uuid.UUID = Path(..., description="Placement ID"),
    user: User = Depends(has_role(["admin", "media_manager"]))
):
    """
    Delete a media placement.
    
    Args:
        placement_id: Placement ID
        user: Current authenticated user with appropriate role
        
    Returns:
        None
        
    Raises:
        HTTPException: If the placement does not exist or is active
    """
    placement_id_str = str(placement_id)
    
    # Check if placement exists
    if placement_id_str not in PLACEMENTS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="PLACEMENT_NOT_FOUND",
                title="Placement not found",
                detail=f"Media placement with ID {placement_id} does not exist"
            )
        )
    
    placement = PLACEMENTS[placement_id_str]
    
    # Check if placement is active
    if placement.status == MediaPlacementStatus.ACTIVE:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_error_response(
                status_code=400,
                error_code="PLACEMENT_ACTIVE",
                title="Placement is active",
                detail=f"Media placement with ID {placement_id} is active and cannot be deleted. Please pause or complete it first."
            )
        )
    
    # Remove the placement
    del PLACEMENTS[placement_id_str]
    
    # No content response
    return None


@router.post(
    "/placements/{placement_id}/actions/activate",
    response_model=StandardResponse[MediaPlacement],
    summary="Activate placement",
    description="Activate a placement that is in draft or paused status"
)
async def activate_placement(
    placement_id: uuid.UUID = Path(..., description="Placement ID"),
    user: User = Depends(has_role(["admin", "media_manager"]))
):
    """
    Activate a media placement.
    
    Args:
        placement_id: Placement ID
        user: Current authenticated user with appropriate role
        
    Returns:
        StandardResponse[MediaPlacement]: Updated media placement
        
    Raises:
        HTTPException: If the placement does not exist or cannot be activated
    """
    placement_id_str = str(placement_id)
    
    # Check if placement exists
    if placement_id_str not in PLACEMENTS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="PLACEMENT_NOT_FOUND",
                title="Placement not found",
                detail=f"Media placement with ID {placement_id} does not exist"
            )
        )
    
    placement = PLACEMENTS[placement_id_str]
    
    # Check if the placement can be activated
    if placement.status not in [MediaPlacementStatus.DRAFT, MediaPlacementStatus.PAUSED]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_error_response(
                status_code=400,
                error_code="INVALID_PLACEMENT_STATUS",
                title="Invalid placement status",
                detail=f"Placement with status '{placement.status}' cannot be activated. Only draft or paused placements can be activated."
            )
        )
    
    # Update placement status
    placement.status = MediaPlacementStatus.ACTIVE
    placement.updated_at = datetime.utcnow()
    
    # Store the updated placement
    PLACEMENTS[placement_id_str] = placement
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/media/placements/{placement_id}",
        "related": {
            "channel": f"/api/v1/media/channels/{placement.channel_id}",
            "budget": f"/api/v1/media/budgets/{placement.budget_id}",
            "campaign": f"/api/v1/campaigns/{placement.campaign_id}"
        }
    }
    
    return create_response(
        data=placement,
        links=links
    )


@router.post(
    "/placements/{placement_id}/actions/pause",
    response_model=StandardResponse[MediaPlacement],
    summary="Pause placement",
    description="Pause an active placement"
)
async def pause_placement(
    placement_id: uuid.UUID = Path(..., description="Placement ID"),
    user: User = Depends(has_role(["admin", "media_manager"]))
):
    """
    Pause a media placement.
    
    Args:
        placement_id: Placement ID
        user: Current authenticated user with appropriate role
        
    Returns:
        StandardResponse[MediaPlacement]: Updated media placement
        
    Raises:
        HTTPException: If the placement does not exist or cannot be paused
    """
    placement_id_str = str(placement_id)
    
    # Check if placement exists
    if placement_id_str not in PLACEMENTS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="PLACEMENT_NOT_FOUND",
                title="Placement not found",
                detail=f"Media placement with ID {placement_id} does not exist"
            )
        )
    
    placement = PLACEMENTS[placement_id_str]
    
    # Check if the placement can be paused
    if placement.status != MediaPlacementStatus.ACTIVE:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_error_response(
                status_code=400,
                error_code="INVALID_PLACEMENT_STATUS",
                title="Invalid placement status",
                detail=f"Placement with status '{placement.status}' cannot be paused. Only active placements can be paused."
            )
        )
    
    # Update placement status
    placement.status = MediaPlacementStatus.PAUSED
    placement.updated_at = datetime.utcnow()
    
    # Store the updated placement
    PLACEMENTS[placement_id_str] = placement
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/media/placements/{placement_id}",
        "related": {
            "channel": f"/api/v1/media/channels/{placement.channel_id}",
            "budget": f"/api/v1/media/budgets/{placement.budget_id}",
            "campaign": f"/api/v1/campaigns/{placement.campaign_id}"
        }
    }
    
    return create_response(
        data=placement,
        links=links
    )