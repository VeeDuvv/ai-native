"""
Unit tests for the campaigns controller.
"""

import pytest
import uuid
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from src.api_layer.controllers.campaigns import (
    list_campaigns,
    create_campaign,
    get_campaign,
    update_campaign,
    delete_campaign,
    launch_campaign,
    pause_campaign
)
from src.api_layer.models.campaigns import (
    Campaign,
    CampaignStatus,
    CampaignCreate,
    CampaignUpdate
)
from src.api_layer.models.base import StandardRequest


@pytest.mark.unit
@pytest.mark.controllers
class TestCampaignsController:
    """Tests for the campaigns controller functions."""

    @patch("src.api_layer.controllers.campaigns.CAMPAIGNS")
    async def test_get_campaign_success(self, mock_campaigns, sample_campaign):
        """Test getting a campaign successfully."""
        # Set up the mock
        campaign_id = str(sample_campaign.id)
        mock_campaigns.__getitem__.return_value = sample_campaign
        mock_campaigns.__contains__.return_value = True
        
        # Create a mock request
        mock_user = MagicMock()
        
        # Call the function
        response = await get_campaign(campaign_id=sample_campaign.id, user=mock_user)
        
        # Assert the result
        assert response["data"] == sample_campaign
        
    @patch("src.api_layer.controllers.campaigns.CAMPAIGNS")
    async def test_get_campaign_not_found(self, mock_campaigns):
        """Test getting a campaign that doesn't exist."""
        # Set up the mock
        mock_campaigns.__contains__.return_value = False
        
        # Create a mock request
        mock_user = MagicMock()
        
        # Call the function
        response = await get_campaign(campaign_id=uuid.uuid4(), user=mock_user)
        
        # Assert the result
        assert response.status_code == 404
        assert "CAMPAIGN_NOT_FOUND" in response.body.decode()

    @patch("src.api_layer.controllers.campaigns.uuid.uuid4")
    @patch("src.api_layer.controllers.campaigns.datetime")
    @patch("src.api_layer.controllers.campaigns.CAMPAIGNS")
    async def test_create_campaign(self, mock_campaigns, mock_datetime, mock_uuid, mock_uuid):
        """Test creating a campaign."""
        # Set up the mocks
        mock_uuid.return_value = mock_uuid
        now = datetime.now()
        mock_datetime.utcnow.return_value = now
        
        # Create test data
        campaign_data = CampaignCreate(
            name="Test Campaign",
            description="Test description",
            type="awareness",
            objective="brand_awareness",
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=30),
            budget={
                "amount": 1000.0,
                "currency": "USD",
                "type": "daily"
            },
            targeting={}
        )
        
        # Create a mock request
        mock_request = StandardRequest(data=campaign_data)
        mock_user = MagicMock()
        
        # Call the function
        response = await create_campaign(request=mock_request, user=mock_user)
        
        # Assert the result
        assert response["data"].name == "Test Campaign"
        assert response["data"].status == CampaignStatus.DRAFT
        assert response["data"].created_at == now
        assert mock_campaigns.__setitem__.called
        
    @patch("src.api_layer.controllers.campaigns.CAMPAIGNS")
    async def test_update_campaign(self, mock_campaigns, sample_campaign, mock_uuid):
        """Test updating a campaign."""
        # Set up the mock
        campaign_id = str(sample_campaign.id)
        mock_campaigns.__getitem__.return_value = sample_campaign
        mock_campaigns.__contains__.return_value = True
        
        # Create test data
        update_data = CampaignUpdate(
            name="Updated Campaign",
            status=CampaignStatus.ACTIVE
        )
        
        # Create a mock request
        mock_request = StandardRequest(data=update_data)
        mock_user = MagicMock()
        
        # Call the function
        response = await update_campaign(
            request=mock_request,
            campaign_id=mock_uuid,
            user=mock_user
        )
        
        # Assert the result
        assert response["data"].name == "Updated Campaign"
        assert response["data"].status == CampaignStatus.ACTIVE
        assert mock_campaigns.__setitem__.called
        
    @patch("src.api_layer.controllers.campaigns.CAMPAIGNS")
    async def test_delete_campaign(self, mock_campaigns, mock_uuid):
        """Test deleting a campaign."""
        # Set up the mock
        mock_campaigns.__contains__.return_value = True
        
        # Create a mock request
        mock_user = MagicMock()
        
        # Call the function
        response = await delete_campaign(campaign_id=mock_uuid, user=mock_user)
        
        # Assert the result
        assert response is None
        assert mock_campaigns.__delitem__.called
        
    @patch("src.api_layer.controllers.campaigns.CAMPAIGNS")
    async def test_launch_campaign(self, mock_campaigns, sample_campaign, mock_uuid):
        """Test launching a campaign."""
        # Set up the mock
        campaign_id = str(sample_campaign.id)
        mock_campaigns.__getitem__.return_value = sample_campaign
        mock_campaigns.__contains__.return_value = True
        
        # Create a mock request
        mock_user = MagicMock()
        
        # Call the function
        response = await launch_campaign(campaign_id=mock_uuid, user=mock_user)
        
        # Assert the result
        assert response["data"].status == CampaignStatus.ACTIVE
        assert mock_campaigns.__setitem__.called
        
    @patch("src.api_layer.controllers.campaigns.CAMPAIGNS")
    async def test_pause_campaign(self, mock_campaigns, sample_campaign, mock_uuid):
        """Test pausing a campaign."""
        # Set up the mock
        campaign_id = str(sample_campaign.id)
        sample_campaign.status = CampaignStatus.ACTIVE  # Set to active so it can be paused
        mock_campaigns.__getitem__.return_value = sample_campaign
        mock_campaigns.__contains__.return_value = True
        
        # Create a mock request
        mock_user = MagicMock()
        
        # Call the function
        response = await pause_campaign(campaign_id=mock_uuid, user=mock_user)
        
        # Assert the result
        assert response["data"].status == CampaignStatus.PAUSED
        assert mock_campaigns.__setitem__.called