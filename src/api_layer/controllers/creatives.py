# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file handles requests about the pictures, videos, and text we use in
# advertisements. It's like a librarian who keeps track of all our advertisement
# pieces and helps find and create new ones.

# High School Explanation:
# This module implements the API endpoints for managing creative assets used in
# advertising campaigns. It provides functionality for creating, retrieving,
# updating, and generating variations of different types of creative content such
# as text, images, and videos.

"""
Creatives controller for the API layer.

This module provides the API endpoints for creating, retrieving,
updating, and deleting creative assets, as well as generating variations
and retrieving performance data.
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
from src.api_layer.models.creatives import (
    Creative,
    CreativeCreate,
    CreativeUpdate,
    CreativeFilterParams,
    CreativeStatus,
    CreativeType,
    CreativeFormat,
    CreativeVariation,
    GenerateVariationsRequest
)

# Set up logging
logger = logging.getLogger("api.controllers.creatives")

# Create router
router = APIRouter(
    prefix="/creatives",
    tags=["Creatives"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
)

# In-memory storage for creatives (to be replaced with a database)
CREATIVES = {}


@router.get(
    "",
    response_model=PaginatedResponse[Creative],
    summary="List creatives",
    description="Retrieve a paginated list of creatives with optional filtering"
)
async def list_creatives(
    # Pagination parameters
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    # Filter parameters
    status: Optional[List[CreativeStatus]] = Query(None, description="Filter by status"),
    type: Optional[List[CreativeType]] = Query(None, description="Filter by creative type"),
    format: Optional[List[CreativeFormat]] = Query(None, description="Filter by creative format"),
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
    List and filter creatives.
    
    Args:
        page: Page number for pagination
        per_page: Number of items per page
        status: Filter by creative status
        type: Filter by creative type
        format: Filter by creative format
        campaign_id: Filter by associated campaign
        tag: Filter by tags
        query: Search query for creative name or description
        created_after: Filter by creation date after
        created_before: Filter by creation date before
        sort_by: Field to sort by
        sort_order: Sort order (asc or desc)
        user: Current authenticated user
        
    Returns:
        PaginatedResponse[Creative]: Paginated list of creatives
    """
    # Filter creatives (this would typically be done in a database query)
    filtered_creatives = list(CREATIVES.values())
    
    # Apply filters
    if status:
        filtered_creatives = [c for c in filtered_creatives if c.status in status]
    
    if type:
        filtered_creatives = [c for c in filtered_creatives if c.type in type]
    
    if format:
        filtered_creatives = [c for c in filtered_creatives if c.format in format]
    
    if campaign_id:
        filtered_creatives = [c for c in filtered_creatives if campaign_id in c.campaign_ids]
    
    if tag:
        filtered_creatives = [c for c in filtered_creatives if any(t in c.tags for t in tag)]
    
    if query:
        query_lower = query.lower()
        filtered_creatives = [
            c for c in filtered_creatives 
            if query_lower in c.name.lower() or 
               (c.description and query_lower in c.description.lower())
        ]
    
    if created_after:
        filtered_creatives = [c for c in filtered_creatives if c.created_at >= created_after]
    
    if created_before:
        filtered_creatives = [c for c in filtered_creatives if c.created_at <= created_before]
    
    # Sort creatives
    reverse = sort_order.lower() == "desc"
    try:
        filtered_creatives.sort(key=lambda c: getattr(c, sort_by), reverse=reverse)
    except AttributeError:
        # Default to created_at if the sort field doesn't exist
        filtered_creatives.sort(key=lambda c: c.created_at, reverse=reverse)
    
    # Calculate pagination
    total_items = len(filtered_creatives)
    total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1
    
    # Ensure page is within bounds
    if page > total_pages:
        page = total_pages
    
    # Paginate results
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_creatives = filtered_creatives[start_idx:end_idx]
    
    # Create pagination metadata
    pagination_meta = {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "items_per_page": per_page
    }
    
    # Create pagination links
    base_url = f"/api/v1/creatives?per_page={per_page}"
    for param, value in {
        "status": status,
        "type": type,
        "format": format,
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
        "data": paginated_creatives,
        "meta": {
            "pagination": pagination_meta
        },
        "links": pagination_links
    }


@router.post(
    "",
    response_model=StandardResponse[Creative],
    status_code=status.HTTP_201_CREATED,
    summary="Create creative",
    description="Create a new creative asset"
)
async def create_creative(
    request: StandardRequest[CreativeCreate],
    user: User = Depends(has_role(["admin", "creative_manager"]))
):
    """
    Create a new creative.
    
    Args:
        request: Creative creation request
        user: Current authenticated user with appropriate role
        
    Returns:
        StandardResponse[Creative]: Newly created creative
    """
    creative_data = request.data
    
    # Generate a unique ID
    creative_id = uuid.uuid4()
    
    # Get current timestamp
    now = datetime.utcnow()
    
    # Create creative object
    creative = Creative(
        id=creative_id,
        name=creative_data.name,
        description=creative_data.description,
        type=creative_data.type,
        format=creative_data.format,
        content=creative_data.content,
        dimensions=creative_data.dimensions,
        status=CreativeStatus.DRAFT,  # New creatives start as drafts
        variations=[],
        campaign_ids=creative_data.campaign_ids if creative_data.campaign_ids else [],
        target_url=creative_data.target_url,
        tags=creative_data.tags if creative_data.tags else [],
        metadata=creative_data.metadata,
        created_at=now,
        updated_at=now
    )
    
    # Store the creative
    CREATIVES[str(creative_id)] = creative
    
    # In a real implementation, we would delegate creative generation to an agent
    # try:
    #     await coordinator.execute_task(
    #         agent_id="creative_generation_agent",
    #         task_type="process_creative",
    #         task_data={"creative_id": str(creative_id)}
    #     )
    # except Exception as e:
    #     logger.warning(f"Error processing creative: {e}")
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/creatives/{creative_id}",
        "related": {
            "variations": f"/api/v1/creatives/{creative_id}/variations",
            "campaigns": f"/api/v1/creatives/{creative_id}/campaigns"
        }
    }
    
    return create_response(
        data=creative,
        links=links
    )


@router.get(
    "/{creative_id}",
    response_model=StandardResponse[Creative],
    summary="Get creative",
    description="Retrieve details of a specific creative"
)
async def get_creative(
    creative_id: uuid.UUID = Path(..., description="Creative ID"),
    user: User = Depends(get_current_active_user)
):
    """
    Get details of a specific creative.
    
    Args:
        creative_id: Creative ID
        user: Current authenticated user
        
    Returns:
        StandardResponse[Creative]: Creative details
        
    Raises:
        HTTPException: If the creative does not exist
    """
    creative_id_str = str(creative_id)
    
    # Check if creative exists
    if creative_id_str not in CREATIVES:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CREATIVE_NOT_FOUND",
                title="Creative not found",
                detail=f"Creative with ID {creative_id} does not exist"
            )
        )
    
    creative = CREATIVES[creative_id_str]
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/creatives/{creative_id}",
        "related": {
            "variations": f"/api/v1/creatives/{creative_id}/variations",
            "campaigns": f"/api/v1/creatives/{creative_id}/campaigns"
        }
    }
    
    return create_response(
        data=creative,
        links=links
    )


@router.put(
    "/{creative_id}",
    response_model=StandardResponse[Creative],
    summary="Update creative",
    description="Update details of a specific creative"
)
async def update_creative(
    request: StandardRequest[CreativeUpdate],
    creative_id: uuid.UUID = Path(..., description="Creative ID"),
    user: User = Depends(has_role(["admin", "creative_manager"]))
):
    """
    Update a creative.
    
    Args:
        request: Creative update request
        creative_id: Creative ID
        user: Current authenticated user with appropriate role
        
    Returns:
        StandardResponse[Creative]: Updated creative
        
    Raises:
        HTTPException: If the creative does not exist
    """
    creative_id_str = str(creative_id)
    
    # Check if creative exists
    if creative_id_str not in CREATIVES:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CREATIVE_NOT_FOUND",
                title="Creative not found",
                detail=f"Creative with ID {creative_id} does not exist"
            )
        )
    
    creative = CREATIVES[creative_id_str]
    update_data = request.data
    
    # Update creative fields if provided
    if update_data.name is not None:
        creative.name = update_data.name
    
    if update_data.description is not None:
        creative.description = update_data.description
    
    if update_data.status is not None:
        creative.status = update_data.status
    
    if update_data.format is not None:
        creative.format = update_data.format
    
    if update_data.content is not None:
        creative.content = update_data.content
    
    if update_data.dimensions is not None:
        creative.dimensions = update_data.dimensions
    
    if update_data.campaign_ids is not None:
        creative.campaign_ids = update_data.campaign_ids
    
    if update_data.target_url is not None:
        creative.target_url = update_data.target_url
    
    if update_data.tags is not None:
        creative.tags = update_data.tags
    
    if update_data.metadata is not None:
        creative.metadata = update_data.metadata
    
    # Update the timestamp
    creative.updated_at = datetime.utcnow()
    
    # Store the updated creative
    CREATIVES[creative_id_str] = creative
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/creatives/{creative_id}",
        "related": {
            "variations": f"/api/v1/creatives/{creative_id}/variations",
            "campaigns": f"/api/v1/creatives/{creative_id}/campaigns"
        }
    }
    
    return create_response(
        data=creative,
        links=links
    )


@router.delete(
    "/{creative_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete creative",
    description="Delete a specific creative"
)
async def delete_creative(
    creative_id: uuid.UUID = Path(..., description="Creative ID"),
    user: User = Depends(has_role(["admin", "creative_manager"]))
):
    """
    Delete a creative.
    
    Args:
        creative_id: Creative ID
        user: Current authenticated user with appropriate role
        
    Returns:
        None
        
    Raises:
        HTTPException: If the creative does not exist
    """
    creative_id_str = str(creative_id)
    
    # Check if creative exists
    if creative_id_str not in CREATIVES:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CREATIVE_NOT_FOUND",
                title="Creative not found",
                detail=f"Creative with ID {creative_id} does not exist"
            )
        )
    
    # Remove the creative
    del CREATIVES[creative_id_str]
    
    # No content response
    return None


@router.get(
    "/{creative_id}/variations",
    response_model=PaginatedResponse[CreativeVariation],
    summary="List creative variations",
    description="Retrieve a paginated list of variations for a creative"
)
async def list_creative_variations(
    creative_id: uuid.UUID = Path(..., description="Creative ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    user: User = Depends(get_current_active_user)
):
    """
    List variations for a creative.
    
    Args:
        creative_id: Creative ID
        page: Page number for pagination
        per_page: Number of items per page
        user: Current authenticated user
        
    Returns:
        PaginatedResponse[CreativeVariation]: Paginated list of variations
        
    Raises:
        HTTPException: If the creative does not exist
    """
    creative_id_str = str(creative_id)
    
    # Check if creative exists
    if creative_id_str not in CREATIVES:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CREATIVE_NOT_FOUND",
                title="Creative not found",
                detail=f"Creative with ID {creative_id} does not exist"
            )
        )
    
    creative = CREATIVES[creative_id_str]
    variations = creative.variations
    
    # Calculate pagination
    total_items = len(variations)
    total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1
    
    # Ensure page is within bounds
    if page > total_pages:
        page = total_pages
    
    # Paginate results
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_items)
    paginated_variations = variations[start_idx:end_idx]
    
    # Create pagination metadata
    pagination_meta = {
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "items_per_page": per_page
    }
    
    # Create pagination links
    base_url = f"/api/v1/creatives/{creative_id}/variations?per_page={per_page}"
    
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
        "data": paginated_variations,
        "meta": {
            "pagination": pagination_meta
        },
        "links": pagination_links
    }


@router.post(
    "/{creative_id}/actions/generate-variations",
    response_model=StandardResponse[List[CreativeVariation]],
    summary="Generate variations",
    description="Generate variations of a creative for A/B testing or optimization"
)
async def generate_variations(
    request: StandardRequest[GenerateVariationsRequest],
    creative_id: uuid.UUID = Path(..., description="Creative ID"),
    user: User = Depends(has_role(["admin", "creative_manager"]))
):
    """
    Generate variations of a creative.
    
    Args:
        request: Variation generation request
        creative_id: Creative ID
        user: Current authenticated user with appropriate role
        
    Returns:
        StandardResponse[List[CreativeVariation]]: List of generated variations
        
    Raises:
        HTTPException: If the creative does not exist
    """
    creative_id_str = str(creative_id)
    
    # Check if creative exists
    if creative_id_str not in CREATIVES:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CREATIVE_NOT_FOUND",
                title="Creative not found",
                detail=f"Creative with ID {creative_id} does not exist"
            )
        )
    
    creative = CREATIVES[creative_id_str]
    generation_params = request.data
    
    # In a real implementation, we would delegate variation generation to an AI agent
    # Here we'll just create placeholder variations
    now = datetime.utcnow()
    new_variations = []
    
    for i in range(generation_params.variation_count):
        variation_id = uuid.uuid4()
        variation = CreativeVariation(
            id=variation_id,
            name=f"{creative.name} - Variation {i+1}",
            type=creative.type,
            content=creative.content,  # In real implementation, this would be a variation
            status=CreativeStatus.DRAFT,
            performance=None,
            created_at=now,
            updated_at=now
        )
        new_variations.append(variation)
    
    # Add variations to the creative
    creative.variations.extend(new_variations)
    creative.updated_at = now
    
    # Store the updated creative
    CREATIVES[creative_id_str] = creative
    
    return create_response(
        data=new_variations,
        links={
            "self": f"/api/v1/creatives/{creative_id}/variations",
            "parent": f"/api/v1/creatives/{creative_id}"
        }
    )


@router.get(
    "/{creative_id}/campaigns",
    response_model=PaginatedResponse[Any],  # This would be a Campaign model in a real implementation
    summary="List campaigns using creative",
    description="Retrieve a paginated list of campaigns that use this creative"
)
async def list_creative_campaigns(
    creative_id: uuid.UUID = Path(..., description="Creative ID"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    user: User = Depends(get_current_active_user)
):
    """
    List campaigns associated with a creative.
    
    Args:
        creative_id: Creative ID
        page: Page number for pagination
        per_page: Number of items per page
        user: Current authenticated user
        
    Returns:
        PaginatedResponse: Paginated list of campaigns
        
    Raises:
        HTTPException: If the creative does not exist
    """
    creative_id_str = str(creative_id)
    
    # Check if creative exists
    if creative_id_str not in CREATIVES:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CREATIVE_NOT_FOUND",
                title="Creative not found",
                detail=f"Creative with ID {creative_id} does not exist"
            )
        )
    
    creative = CREATIVES[creative_id_str]
    
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
    base_url = f"/api/v1/creatives/{creative_id}/campaigns?per_page={per_page}"
    
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