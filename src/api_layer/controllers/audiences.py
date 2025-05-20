# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file handles requests about groups of people who might see our ads.
# It's like a teacher who keeps track of different groups of students for
# different activities.

# High School Explanation:
# This module implements the API endpoints for managing audience definitions
# used in targeting advertising campaigns. It provides functionality for
# creating, retrieving, and updating audience segments based on demographic,
# interest, behavioral, and geographic criteria.

"""
Audiences controller for the API layer.

This module provides the API endpoints for creating, retrieving,
updating, and deleting audience definitions, as well as estimating
audience sizes and retrieving audience insights.
"""

import logging
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path, status
from fastapi.responses import JSONResponse

from src.api_layer.core.responses import create_response, create_error_response
from src.api_layer.core.auth import User, get_current_active_user, has_role
from src.api_layer.core.agent_coordinator import coordinator
from src.api_layer.models.base import StandardRequest, StandardResponse, PaginatedResponse
from src.api_layer.models.audiences import (
    Audience,
    AudienceCreate,
    AudienceUpdate,
    AudienceFilterParams,
    AudienceStatus,
    AudienceType,
    AudienceSizeEstimateRequest,
    AudienceSizeEstimateResponse,
    AudienceSize
)

# Set up logging
logger = logging.getLogger("api.controllers.audiences")

# Create router
router = APIRouter(
    prefix="/audiences",
    tags=["Audiences"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
)

# In-memory storage for audiences (to be replaced with a database)
AUDIENCES = {}


@router.get(
    "",
    response_model=PaginatedResponse[Audience],
    summary="List audiences",
    description="Retrieve a paginated list of audiences with optional filtering"
)
async def list_audiences(
    # Pagination parameters
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    # Filter parameters
    status: Optional[List[AudienceStatus]] = Query(None, description="Filter by status"),
    type: Optional[List[AudienceType]] = Query(None, description="Filter by audience type"),
    campaign_id: Optional[uuid.UUID] = Query(None, description="Filter by associated campaign"),
    tag: Optional[List[str]] = Query(None, description="Filter by tags"),
    # Search parameters
    query: Optional[str] = Query(None, description="Search query"),
    # Time range parameters
    created_after: Optional[datetime] = Query(None, description="Filter by creation date after"),
    created_before: Optional[datetime] = Query(None, description="Filter by creation date before"),
    # Sort parameters
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc or desc)"),
    # Auth
    user: User = Depends(get_current_active_user)
):
    """
    List and filter audiences.
    
    Args:
        page: Page number for pagination
        per_page: Number of items per page
        status: Filter by audience status
        type: Filter by audience type
        campaign_id: Filter by associated campaign
        tag: Filter by tags
        query: Search query for audience name or description
        created_after: Filter by creation date after
        created_before: Filter by creation date before
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        user: Current authenticated user
        
    Returns:
        PaginatedResponse[Audience]: Paginated list of audiences
    """
    # Filter audiences (this would typically be done in a database query)
    filtered_audiences = list(AUDIENCES.values())
    
    # Apply filters
    if status:
        filtered_audiences = [a for a in filtered_audiences if a.status in status]
    
    if type:
        filtered_audiences = [a for a in filtered_audiences if a.type in type]
    
    if campaign_id:
        filtered_audiences = [a for a in filtered_audiences if campaign_id in a.campaign_ids]
    
    if tag:
        filtered_audiences = [a for a in filtered_audiences if any(t in a.tags for t in tag)]
    
    if query:
        query_lower = query.lower()
        filtered_audiences = [
            a for a in filtered_audiences 
            if query_lower in a.name.lower() or 
               (a.description and query_lower in a.description.lower())
        ]
    
    if created_after:
        filtered_audiences = [a for a in filtered_audiences if a.created_at >= created_after]
    
    if created_before:
        filtered_audiences = [a for a in filtered_audiences if a.created_at <= created_before]
    
    # Sort audiences
    reverse = sort_order.lower() == "desc"
    try:
        filtered_audiences.sort(key=lambda a: getattr(a, sort_by), reverse=reverse)
    except AttributeError:
        # Default to created_at if the sort field doesn't exist
        filtered_audiences.sort(key=lambda a: a.created_at, reverse=reverse)
    
    # Calculate pagination
    total_items = len(filtered_audiences)
    total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1
    
    # Ensure page is within bounds
    if page > total_pages:
        page = total_pages
    
    # Paginate results
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_audiences = filtered_audiences[start_idx:end_idx]
    
    # Create pagination metadata
    pagination_meta = {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "items_per_page": per_page
    }
    
    # Create pagination links
    base_url = f"/api/v1/audiences?per_page={per_page}"
    for param, value in {
        "status": status,
        "type": type,
        "campaign_id": campaign_id,
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
        "data": paginated_audiences,
        "meta": {
            "pagination": pagination_meta
        },
        "links": pagination_links
    }


@router.post(
    "",
    response_model=StandardResponse[Audience],
    status_code=status.HTTP_201_CREATED,
    summary="Create audience",
    description="Create a new audience definition"
)
async def create_audience(
    request: StandardRequest[AudienceCreate],
    user: User = Depends(has_role(["admin", "audience_manager"]))
):
    """
    Create a new audience.
    
    Args:
        request: Audience creation request
        user: Current authenticated user with appropriate role
        
    Returns:
        StandardResponse[Audience]: Newly created audience
    """
    audience_data = request.data
    
    # Generate a unique ID
    audience_id = uuid.uuid4()
    
    # Get current timestamp
    now = datetime.utcnow()
    
    # Create audience object
    audience = Audience(
        id=audience_id,
        name=audience_data.name,
        description=audience_data.description,
        type=audience_data.type,
        status=AudienceStatus.DRAFT,  # New audiences start as drafts
        criteria=audience_data.criteria,
        size_estimate=None,  # Will be calculated later
        campaign_ids=audience_data.campaign_ids if audience_data.campaign_ids else [],
        tags=audience_data.tags if audience_data.tags else [],
        metadata=audience_data.metadata,
        created_at=now,
        updated_at=now
    )
    
    # Store the audience
    AUDIENCES[str(audience_id)] = audience
    
    # In a real implementation, we would delegate audience size estimation to an agent
    # try:
    #     size_estimate = await coordinator.execute_task(
    #         agent_id="audience_analytics_agent",
    #         task_type="estimate_audience_size",
    #         task_data={"audience_id": str(audience_id)}
    #     )
    #     
    #     audience.size_estimate = AudienceSize(**size_estimate)
    #     AUDIENCES[str(audience_id)] = audience
    # except Exception as e:
    #     logger.warning(f"Error estimating audience size: {e}")
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/audiences/{audience_id}",
        "related": {
            "size-estimate": f"/api/v1/audiences/{audience_id}/size-estimate",
            "campaigns": f"/api/v1/audiences/{audience_id}/campaigns"
        }
    }
    
    return create_response(
        data=audience,
        links=links
    )


@router.get(
    "/{audience_id}",
    response_model=StandardResponse[Audience],
    summary="Get audience",
    description="Retrieve details of a specific audience"
)
async def get_audience(
    audience_id: uuid.UUID = Path(..., description="Audience ID"),
    user: User = Depends(get_current_active_user)
):
    """
    Get details of a specific audience.
    
    Args:
        audience_id: Audience ID
        user: Current authenticated user
        
    Returns:
        StandardResponse[Audience]: Audience details
        
    Raises:
        HTTPException: If the audience does not exist
    """
    audience_id_str = str(audience_id)
    
    # Check if audience exists
    if audience_id_str not in AUDIENCES:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="AUDIENCE_NOT_FOUND",
                title="Audience not found",
                detail=f"Audience with ID {audience_id} does not exist"
            )
        )
    
    audience = AUDIENCES[audience_id_str]
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/audiences/{audience_id}",
        "related": {
            "size-estimate": f"/api/v1/audiences/{audience_id}/size-estimate",
            "campaigns": f"/api/v1/audiences/{audience_id}/campaigns"
        }
    }
    
    return create_response(
        data=audience,
        links=links
    )


@router.put(
    "/{audience_id}",
    response_model=StandardResponse[Audience],
    summary="Update audience",
    description="Update details of a specific audience"
)
async def update_audience(
    request: StandardRequest[AudienceUpdate],
    audience_id: uuid.UUID = Path(..., description="Audience ID"),
    user: User = Depends(has_role(["admin", "audience_manager"]))
):
    """
    Update an audience.
    
    Args:
        request: Audience update request
        audience_id: Audience ID
        user: Current authenticated user with appropriate role
        
    Returns:
        StandardResponse[Audience]: Updated audience
        
    Raises:
        HTTPException: If the audience does not exist
    """
    audience_id_str = str(audience_id)
    
    # Check if audience exists
    if audience_id_str not in AUDIENCES:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="AUDIENCE_NOT_FOUND",
                title="Audience not found",
                detail=f"Audience with ID {audience_id} does not exist"
            )
        )
    
    audience = AUDIENCES[audience_id_str]
    update_data = request.data
    
    # Update audience fields if provided
    if update_data.name is not None:
        audience.name = update_data.name
    
    if update_data.description is not None:
        audience.description = update_data.description
    
    if update_data.status is not None:
        audience.status = update_data.status
    
    if update_data.criteria is not None:
        audience.criteria = update_data.criteria
        audience.size_estimate = None  # Reset size estimate when criteria changes
    
    if update_data.campaign_ids is not None:
        audience.campaign_ids = update_data.campaign_ids
    
    if update_data.tags is not None:
        audience.tags = update_data.tags
    
    if update_data.metadata is not None:
        audience.metadata = update_data.metadata
    
    # Update the timestamp
    audience.updated_at = datetime.utcnow()
    
    # Store the updated audience
    AUDIENCES[audience_id_str] = audience
    
    # In a real implementation, we would re-calculate size estimate if criteria changed
    # if update_data.criteria is not None:
    #     try:
    #         size_estimate = await coordinator.execute_task(
    #             agent_id="audience_analytics_agent",
    #             task_type="estimate_audience_size",
    #             task_data={"audience_id": audience_id_str}
    #         )
    #         
    #         audience.size_estimate = AudienceSize(**size_estimate)
    #         AUDIENCES[audience_id_str] = audience
    #     except Exception as e:
    #         logger.warning(f"Error re-estimating audience size: {e}")
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/audiences/{audience_id}",
        "related": {
            "size-estimate": f"/api/v1/audiences/{audience_id}/size-estimate",
            "campaigns": f"/api/v1/audiences/{audience_id}/campaigns"
        }
    }
    
    return create_response(
        data=audience,
        links=links
    )


@router.delete(
    "/{audience_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete audience",
    description="Delete a specific audience"
)
async def delete_audience(
    audience_id: uuid.UUID = Path(..., description="Audience ID"),
    user: User = Depends(has_role(["admin", "audience_manager"]))
):
    """
    Delete an audience.
    
    Args:
        audience_id: Audience ID
        user: Current authenticated user with appropriate role
        
    Returns:
        None
        
    Raises:
        HTTPException: If the audience does not exist
    """
    audience_id_str = str(audience_id)
    
    # Check if audience exists
    if audience_id_str not in AUDIENCES:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="AUDIENCE_NOT_FOUND",
                title="Audience not found",
                detail=f"Audience with ID {audience_id} does not exist"
            )
        )
    
    # Remove the audience
    del AUDIENCES[audience_id_str]
    
    # No content response
    return None


@router.get(
    "/{audience_id}/size-estimate",
    response_model=StandardResponse[AudienceSizeEstimateResponse],
    summary="Get audience size estimate",
    description="Retrieve the estimated size of a specific audience"
)
async def get_audience_size_estimate(
    audience_id: uuid.UUID = Path(..., description="Audience ID"),
    refresh: bool = Query(False, description="Force recalculation of the estimate"),
    user: User = Depends(get_current_active_user)
):
    """
    Get the estimated size of an audience.
    
    Args:
        audience_id: Audience ID
        refresh: Whether to force recalculation of the estimate
        user: Current authenticated user
        
    Returns:
        StandardResponse[AudienceSizeEstimateResponse]: Audience size estimate
        
    Raises:
        HTTPException: If the audience does not exist
    """
    audience_id_str = str(audience_id)
    
    # Check if audience exists
    if audience_id_str not in AUDIENCES:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="AUDIENCE_NOT_FOUND",
                title="Audience not found",
                detail=f"Audience with ID {audience_id} does not exist"
            )
        )
    
    audience = AUDIENCES[audience_id_str]
    
    # Check if we need to calculate or refresh the estimate
    if audience.size_estimate is None or refresh:
        # In a real implementation, we would calculate the size estimate
        # Here we'll just provide a placeholder
        now = datetime.utcnow()
        audience.size_estimate = AudienceSize(
            min_size=10000,
            max_size=20000,
            precision="medium",
            reach_percent=0.5,
            last_updated=now
        )
        
        # Update the audience
        AUDIENCES[audience_id_str] = audience
    
    # Create response
    response = AudienceSizeEstimateResponse(
        size=audience.size_estimate,
        breakdowns={
            "age": {
                "18-24": 3000,
                "25-34": 5000,
                "35-44": 2000
            },
            "gender": {
                "male": 5500,
                "female": 4500
            }
        },
        overlaps={
            "similar_audiences": {
                "high_value_customers": 0.75,
                "brand_enthusiasts": 0.45
            }
        }
    )
    
    return create_response(
        data=response
    )


@router.post(
    "/estimate-size",
    response_model=StandardResponse[AudienceSizeEstimateResponse],
    summary="Estimate audience size",
    description="Estimate the size of an audience based on provided criteria without creating it"
)
async def estimate_audience_size(
    request: StandardRequest[AudienceSizeEstimateRequest],
    user: User = Depends(get_current_active_user)
):
    """
    Estimate the size of an audience based on provided criteria.
    
    Args:
        request: Audience size estimation request
        user: Current authenticated user
        
    Returns:
        StandardResponse[AudienceSizeEstimateResponse]: Estimated audience size
    """
    criteria = request.data.criteria
    
    # In a real implementation, we would calculate the size estimate based on the criteria
    # Here we'll just provide a placeholder
    now = datetime.utcnow()
    size_estimate = AudienceSize(
        min_size=15000,
        max_size=25000,
        precision="low",  # Lower precision for estimates of unsaved audiences
        reach_percent=0.7,
        last_updated=now
    )
    
    # Create response
    response = AudienceSizeEstimateResponse(
        size=size_estimate,
        breakdowns={
            "age": {
                "18-24": 4000,
                "25-34": 8000,
                "35-44": 3000
            },
            "gender": {
                "male": 7500,
                "female": 7500
            }
        },
        overlaps=None  # No overlaps for unsaved audiences
    )
    
    return create_response(
        data=response
    )


@router.get(
    "/{audience_id}/campaigns",
    response_model=PaginatedResponse[Any],  # This would be a Campaign model in a real implementation
    summary="List campaigns using audience",
    description="Retrieve a paginated list of campaigns that use this audience"
)
async def list_audience_campaigns(
    audience_id: uuid.UUID = Path(..., description="Audience ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    user: User = Depends(get_current_active_user)
):
    """
    List campaigns associated with an audience.
    
    Args:
        audience_id: Audience ID
        page: Page number for pagination
        per_page: Number of items per page
        user: Current authenticated user
        
    Returns:
        PaginatedResponse: Paginated list of campaigns
        
    Raises:
        HTTPException: If the audience does not exist
    """
    audience_id_str = str(audience_id)
    
    # Check if audience exists
    if audience_id_str not in AUDIENCES:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="AUDIENCE_NOT_FOUND",
                title="Audience not found",
                detail=f"Audience with ID {audience_id} does not exist"
            )
        )
    
    audience = AUDIENCES[audience_id_str]
    
    # In a real implementation, we would fetch campaigns from a database
    # For now, we'll return an empty list
    campaigns = []
    
    # Calculate pagination
    total_items = len(campaigns)
    total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1
    
    # Ensure page is within bounds
    if page > total_pages:
        page = total_pages
    
    # Paginate results
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_campaigns = campaigns[start_idx:end_idx]
    
    # Create pagination metadata
    pagination_meta = {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "items_per_page": per_page
    }
    
    # Create pagination links
    base_url = f"/api/v1/audiences/{audience_id}/campaigns?per_page={per_page}"
    
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
        "data": paginated_campaigns,
        "meta": {
            "pagination": pagination_meta
        },
        "links": pagination_links
    }


@router.post(
    "/{audience_id}/actions/activate",
    response_model=StandardResponse[Audience],
    summary="Activate audience",
    description="Activate an audience that is in draft status"
)
async def activate_audience(
    audience_id: uuid.UUID = Path(..., description="Audience ID"),
    user: User = Depends(has_role(["admin", "audience_manager"]))
):
    """
    Activate an audience.
    
    Args:
        audience_id: Audience ID
        user: Current authenticated user with appropriate role
        
    Returns:
        StandardResponse[Audience]: Updated audience
        
    Raises:
        HTTPException: If the audience does not exist or cannot be activated
    """
    audience_id_str = str(audience_id)
    
    # Check if audience exists
    if audience_id_str not in AUDIENCES:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="AUDIENCE_NOT_FOUND",
                title="Audience not found",
                detail=f"Audience with ID {audience_id} does not exist"
            )
        )
    
    audience = AUDIENCES[audience_id_str]
    
    # Check if the audience can be activated
    if audience.status != AudienceStatus.DRAFT:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_error_response(
                status_code=400,
                error_code="INVALID_AUDIENCE_STATUS",
                title="Invalid audience status",
                detail=f"Audience with status '{audience.status}' cannot be activated. Only draft audiences can be activated."
            )
        )
    
    # Update audience status
    audience.status = AudienceStatus.ACTIVE
    audience.updated_at = datetime.utcnow()
    
    # Store the updated audience
    AUDIENCES[audience_id_str] = audience
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/audiences/{audience_id}",
        "related": {
            "size-estimate": f"/api/v1/audiences/{audience_id}/size-estimate",
            "campaigns": f"/api/v1/audiences/{audience_id}/campaigns"
        }
    }
    
    return create_response(
        data=audience,
        links=links
    )


@router.post(
    "/{audience_id}/actions/archive",
    response_model=StandardResponse[Audience],
    summary="Archive audience",
    description="Archive an audience that is in active status"
)
async def archive_audience(
    audience_id: uuid.UUID = Path(..., description="Audience ID"),
    user: User = Depends(has_role(["admin", "audience_manager"]))
):
    """
    Archive an audience.
    
    Args:
        audience_id: Audience ID
        user: Current authenticated user with appropriate role
        
    Returns:
        StandardResponse[Audience]: Updated audience
        
    Raises:
        HTTPException: If the audience does not exist or cannot be archived
    """
    audience_id_str = str(audience_id)
    
    # Check if audience exists
    if audience_id_str not in AUDIENCES:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="AUDIENCE_NOT_FOUND",
                title="Audience not found",
                detail=f"Audience with ID {audience_id} does not exist"
            )
        )
    
    audience = AUDIENCES[audience_id_str]
    
    # Check if the audience can be archived
    if audience.status != AudienceStatus.ACTIVE:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_error_response(
                status_code=400,
                error_code="INVALID_AUDIENCE_STATUS",
                title="Invalid audience status",
                detail=f"Audience with status '{audience.status}' cannot be archived. Only active audiences can be archived."
            )
        )
    
    # Update audience status
    audience.status = AudienceStatus.ARCHIVED
    audience.updated_at = datetime.utcnow()
    
    # Store the updated audience
    AUDIENCES[audience_id_str] = audience
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/audiences/{audience_id}",
        "related": {
            "size-estimate": f"/api/v1/audiences/{audience_id}/size-estimate",
            "campaigns": f"/api/v1/audiences/{audience_id}/campaigns"
        }
    }
    
    return create_response(
        data=audience,
        links=links
    )