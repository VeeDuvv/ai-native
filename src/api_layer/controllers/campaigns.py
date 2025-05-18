# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file controls what happens when someone asks our computer to create
# or change an advertising campaign. It's like a traffic cop that takes requests
# from the internet and decides what to do with them.

# High School Explanation:
# This module implements the API controllers for campaign management. It handles
# HTTP requests related to campaigns, validates input data, coordinates with the
# agent framework to execute business logic, and formats responses according to
# API standards.

"""
Campaign controller for the API layer.

This module implements the RESTful API endpoints for creating, retrieving,
updating, and deleting advertising campaigns, as well as campaign-specific
actions like launching and pausing.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, Query, Path, Body, status, HTTPException
from fastapi.responses import JSONResponse

from src.api_layer.core.app import create_response, create_error_response
from src.api_layer.core.auth import User, get_current_active_user, has_role
from src.api_layer.core.agent_coordinator import coordinator
from src.api_layer.models.base import StandardRequest, StandardResponse
from src.api_layer.models.campaigns import (
    Campaign, 
    CampaignCreate, 
    CampaignUpdate, 
    CampaignStatus,
    CampaignType,
    CampaignObjective
)

# Create router
router = APIRouter(
    prefix="/api/v1/campaigns",
    tags=["Campaigns"],
)

# In-memory storage for campaigns (to be replaced with a database)
CAMPAIGNS = {}


@router.get("")
async def list_campaigns(
    status: Optional[CampaignStatus] = Query(None, description="Filter by campaign status"),
    type: Optional[CampaignType] = Query(None, description="Filter by campaign type"),
    objective: Optional[CampaignObjective] = Query(None, description="Filter by campaign objective"),
    tag: Optional[str] = Query(None, description="Filter by campaign tag"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: User = Depends(get_current_active_user)
):
    """
    List and filter campaigns.
    
    Returns a paginated list of campaigns, optionally filtered by status, type, objective, or tags.
    """
    # Apply filters
    filtered_campaigns = list(CAMPAIGNS.values())
    
    if status:
        filtered_campaigns = [c for c in filtered_campaigns if c.status == status]
    
    if type:
        filtered_campaigns = [c for c in filtered_campaigns if c.type == type]
    
    if objective:
        filtered_campaigns = [c for c in filtered_campaigns if c.objective == objective]
    
    if tag:
        filtered_campaigns = [c for c in filtered_campaigns if tag in c.tags]
    
    # Sort by updated_at (newest first)
    filtered_campaigns.sort(key=lambda c: c.updated_at, reverse=True)
    
    # Paginate
    paginated_campaigns = filtered_campaigns[offset:offset + limit]
    
    # Create response with pagination metadata
    return create_response(
        data=paginated_campaigns,
        meta={
            "pagination": {
                "total_items": len(filtered_campaigns),
                "offset": offset,
                "limit": limit,
                "count": len(paginated_campaigns)
            }
        },
        links={
            "self": f"/api/v1/campaigns?limit={limit}&offset={offset}",
            "next": f"/api/v1/campaigns?limit={limit}&offset={offset + limit}" if offset + limit < len(filtered_campaigns) else None,
            "prev": f"/api/v1/campaigns?limit={limit}&offset={max(0, offset - limit)}" if offset > 0 else None
        }
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_campaign(
    request: StandardRequest[CampaignCreate],
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new campaign.
    
    Takes campaign details and creates a new campaign in the system.
    """
    campaign_data = request.data
    
    # Generate a new UUID for the campaign
    campaign_id = uuid.uuid4()
    
    # Get current time for timestamps
    now = datetime.now()
    
    # Create campaign with default status (DRAFT)
    campaign = Campaign(
        id=campaign_id,
        status=CampaignStatus.DRAFT,
        created_at=now,
        updated_at=now,
        **campaign_data.dict(exclude_unset=True)
    )
    
    # Store the campaign
    CAMPAIGNS[str(campaign_id)] = campaign
    
    # Try to use agent coordinator if available
    try:
        # Find suitable agents for campaign creation
        agent_ids = coordinator.find_agents_for_capabilities(["campaign_creation"])
        
        if agent_ids:
            # Execute agent task asynchronously
            # We don't wait for the result here - it will run in the background
            coordinator.execute_task(
                agent_id=agent_ids[0],
                task_type="initialize_campaign",
                task_data={"campaign_id": str(campaign_id)}
            )
    except Exception as e:
        # Log the error but don't fail the API call
        print(f"Error coordinating with agents: {e}")
    
    # Create response with location header
    return create_response(
        data=campaign,
        meta={
            "location": f"/api/v1/campaigns/{campaign_id}"
        }
    )


@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: uuid.UUID = Path(..., description="The ID of the campaign to retrieve"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a campaign by ID.
    
    Returns the details of a specific campaign.
    """
    campaign_id_str = str(campaign_id)
    
    # Check if campaign exists
    if campaign_id_str not in CAMPAIGNS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CAMPAIGN_NOT_FOUND",
                title="Campaign not found",
                detail=f"Campaign with ID {campaign_id} does not exist"
            )
        )
    
    campaign = CAMPAIGNS[campaign_id_str]
    
    # Create response with HATEOAS links
    links = {
        "self": f"/api/v1/campaigns/{campaign_id}",
        "related": {
            "creatives": f"/api/v1/campaigns/{campaign_id}/creatives",
            "performance": f"/api/v1/campaigns/{campaign_id}/performance"
        },
        "actions": {
            "update": f"/api/v1/campaigns/{campaign_id}",
            "delete": f"/api/v1/campaigns/{campaign_id}",
            "launch": f"/api/v1/campaigns/{campaign_id}/actions/launch",
            "pause": f"/api/v1/campaigns/{campaign_id}/actions/pause"
        }
    }
    
    return create_response(
        data=campaign,
        links=links
    )


@router.put("/{campaign_id}")
async def update_campaign(
    request: StandardRequest[CampaignUpdate],
    campaign_id: uuid.UUID = Path(..., description="The ID of the campaign to update"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a campaign.
    
    Updates the details of an existing campaign.
    """
    campaign_id_str = str(campaign_id)
    
    # Check if campaign exists
    if campaign_id_str not in CAMPAIGNS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CAMPAIGN_NOT_FOUND",
                title="Campaign not found",
                detail=f"Campaign with ID {campaign_id} does not exist"
            )
        )
    
    # Get existing campaign
    campaign = CAMPAIGNS[campaign_id_str]
    
    # Update the fields that are provided
    update_data = request.data.dict(exclude_unset=True)
    
    # Convert model to dict for updating
    campaign_dict = campaign.dict()
    campaign_dict.update(update_data)
    campaign_dict["updated_at"] = datetime.now()
    
    # Convert back to model
    updated_campaign = Campaign(**campaign_dict)
    
    # Store the updated campaign
    CAMPAIGNS[campaign_id_str] = updated_campaign
    
    # Try to use agent coordinator if available
    try:
        # Find suitable agents for campaign updates
        agent_ids = coordinator.find_agents_for_capabilities(["campaign_management"])
        
        if agent_ids:
            # Execute agent task asynchronously
            coordinator.execute_task(
                agent_id=agent_ids[0],
                task_type="update_campaign",
                task_data={"campaign_id": campaign_id_str, "updates": update_data}
            )
    except Exception as e:
        # Log the error but don't fail the API call
        print(f"Error coordinating with agents: {e}")
    
    return create_response(data=updated_campaign)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: uuid.UUID = Path(..., description="The ID of the campaign to delete"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a campaign.
    
    Removes a campaign from the system.
    """
    campaign_id_str = str(campaign_id)
    
    # Check if campaign exists
    if campaign_id_str not in CAMPAIGNS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CAMPAIGN_NOT_FOUND",
                title="Campaign not found",
                detail=f"Campaign with ID {campaign_id} does not exist"
            )
        )
    
    # Remove campaign
    del CAMPAIGNS[campaign_id_str]
    
    # Try to use agent coordinator if available
    try:
        # Find suitable agents for campaign deletion cleanup
        agent_ids = coordinator.find_agents_for_capabilities(["campaign_management"])
        
        if agent_ids:
            # Execute agent task asynchronously
            coordinator.execute_task(
                agent_id=agent_ids[0],
                task_type="cleanup_campaign",
                task_data={"campaign_id": campaign_id_str}
            )
    except Exception as e:
        # Log the error but don't fail the API call
        print(f"Error coordinating with agents: {e}")
    
    # Return no content
    return None


@router.post("/{campaign_id}/actions/launch")
async def launch_campaign(
    campaign_id: uuid.UUID = Path(..., description="The ID of the campaign to launch"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Launch a campaign.
    
    Changes the status of a campaign from DRAFT or PAUSED to ACTIVE.
    """
    campaign_id_str = str(campaign_id)
    
    # Check if campaign exists
    if campaign_id_str not in CAMPAIGNS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CAMPAIGN_NOT_FOUND",
                title="Campaign not found",
                detail=f"Campaign with ID {campaign_id} does not exist"
            )
        )
    
    # Get campaign
    campaign = CAMPAIGNS[campaign_id_str]
    
    # Check if campaign can be launched
    if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.PAUSED, CampaignStatus.SCHEDULED]:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=create_error_response(
                status_code=422,
                error_code="INVALID_CAMPAIGN_STATUS",
                title="Invalid campaign status",
                detail=f"Cannot launch campaign with status {campaign.status}. Campaign must be in DRAFT, SCHEDULED, or PAUSED status."
            )
        )
    
    # Update campaign status
    campaign_dict = campaign.dict()
    campaign_dict["status"] = CampaignStatus.ACTIVE
    campaign_dict["updated_at"] = datetime.now()
    
    # Convert back to model
    updated_campaign = Campaign(**campaign_dict)
    
    # Store the updated campaign
    CAMPAIGNS[campaign_id_str] = updated_campaign
    
    # Try to use agent coordinator if available
    try:
        # Find suitable agents for campaign launch
        agent_ids = coordinator.find_agents_for_capabilities(["campaign_execution"])
        
        if agent_ids:
            # Execute agent task asynchronously
            coordinator.execute_task(
                agent_id=agent_ids[0],
                task_type="launch_campaign",
                task_data={"campaign_id": campaign_id_str}
            )
    except Exception as e:
        # Log the error but don't fail the API call
        print(f"Error coordinating with agents: {e}")
    
    return create_response(data=updated_campaign)


@router.post("/{campaign_id}/actions/pause")
async def pause_campaign(
    campaign_id: uuid.UUID = Path(..., description="The ID of the campaign to pause"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Pause a campaign.
    
    Changes the status of a campaign from ACTIVE to PAUSED.
    """
    campaign_id_str = str(campaign_id)
    
    # Check if campaign exists
    if campaign_id_str not in CAMPAIGNS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CAMPAIGN_NOT_FOUND",
                title="Campaign not found",
                detail=f"Campaign with ID {campaign_id} does not exist"
            )
        )
    
    # Get campaign
    campaign = CAMPAIGNS[campaign_id_str]
    
    # Check if campaign can be paused
    if campaign.status != CampaignStatus.ACTIVE:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=create_error_response(
                status_code=422,
                error_code="INVALID_CAMPAIGN_STATUS",
                title="Invalid campaign status",
                detail=f"Cannot pause campaign with status {campaign.status}. Campaign must be in ACTIVE status."
            )
        )
    
    # Update campaign status
    campaign_dict = campaign.dict()
    campaign_dict["status"] = CampaignStatus.PAUSED
    campaign_dict["updated_at"] = datetime.now()
    
    # Convert back to model
    updated_campaign = Campaign(**campaign_dict)
    
    # Store the updated campaign
    CAMPAIGNS[campaign_id_str] = updated_campaign
    
    # Try to use agent coordinator if available
    try:
        # Find suitable agents for campaign pause
        agent_ids = coordinator.find_agents_for_capabilities(["campaign_execution"])
        
        if agent_ids:
            # Execute agent task asynchronously
            coordinator.execute_task(
                agent_id=agent_ids[0],
                task_type="pause_campaign",
                task_data={"campaign_id": campaign_id_str}
            )
    except Exception as e:
        # Log the error but don't fail the API call
        print(f"Error coordinating with agents: {e}")
    
    return create_response(data=updated_campaign)


@router.get("/{campaign_id}/performance")
async def get_campaign_performance(
    campaign_id: uuid.UUID = Path(..., description="The ID of the campaign"),
    start_date: Optional[datetime] = Query(None, description="Filter metrics from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter metrics until this date"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get campaign performance metrics.
    
    Returns performance data for a specific campaign, optionally filtered by date range.
    """
    campaign_id_str = str(campaign_id)
    
    # Check if campaign exists
    if campaign_id_str not in CAMPAIGNS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CAMPAIGN_NOT_FOUND",
                title="Campaign not found",
                detail=f"Campaign with ID {campaign_id} does not exist"
            )
        )
    
    # Get campaign
    campaign = CAMPAIGNS[campaign_id_str]
    
    # Check if campaign has performance data
    if not campaign.performance:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="PERFORMANCE_DATA_NOT_FOUND",
                title="Performance data not found",
                detail=f"No performance data available for campaign with ID {campaign_id}"
            )
        )
    
    # For now, return the existing performance data
    # In a real implementation, we would filter by date and possibly aggregate data
    return create_response(
        data=campaign.performance,
        meta={
            "campaign_id": str(campaign_id),
            "campaign_name": campaign.name,
            "date_range": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            }
        }
    )


@router.get("/{campaign_id}/creatives")
async def list_campaign_creatives(
    campaign_id: uuid.UUID = Path(..., description="The ID of the campaign"),
    current_user: User = Depends(get_current_active_user)
):
    """
    List creatives for a campaign.
    
    Returns all creative assets associated with a specific campaign.
    """
    campaign_id_str = str(campaign_id)
    
    # Check if campaign exists
    if campaign_id_str not in CAMPAIGNS:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                status_code=404,
                error_code="CAMPAIGN_NOT_FOUND",
                title="Campaign not found",
                detail=f"Campaign with ID {campaign_id} does not exist"
            )
        )
    
    # Get campaign
    campaign = CAMPAIGNS[campaign_id_str]
    
    # We would normally fetch the creatives from a database
    # For this stub implementation, just return the IDs
    return create_response(
        data=campaign.creatives,
        meta={
            "campaign_id": str(campaign_id),
            "campaign_name": campaign.name,
            "total_creatives": len(campaign.creatives)
        }
    )