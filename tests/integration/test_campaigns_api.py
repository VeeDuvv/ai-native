"""
Integration tests for the campaigns API endpoints.
"""

import pytest
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from src.api_layer.controllers.campaigns import CAMPAIGNS
from src.api_layer.models.campaigns import CampaignStatus


@pytest.mark.integration
class TestCampaignsAPI:
    """Integration tests for the campaigns API."""

    def setup_method(self):
        """Set up test data before each test."""
        # Clear the campaigns dict
        CAMPAIGNS.clear()

    def test_list_campaigns_empty(self, client, auth_headers):
        """Test listing campaigns when none exist."""
        response = client.get("/api/v1/campaigns", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 0
        assert data["meta"]["pagination"]["total_items"] == 0

    def test_create_and_get_campaign(self, client, auth_headers, mock_datetime):
        """Test creating a campaign and then retrieving it."""
        # Campaign data
        campaign_data = {
            "data": {
                "name": "Test Campaign",
                "description": "Test campaign description",
                "type": "awareness",
                "objective": "brand_awareness",
                "start_date": mock_datetime.isoformat(),
                "end_date": (mock_datetime + timedelta(days=30)).isoformat(),
                "budget": {
                    "amount": 1000.0,
                    "currency": "USD",
                    "type": "daily"
                },
                "targeting": {
                    "demographics": {
                        "age_ranges": ["18-24", "25-34"],
                        "genders": ["male", "female"]
                    },
                    "locations": [
                        {"country": "US", "state": "CA"}
                    ]
                },
                "tags": ["test", "brand"]
            }
        }
        
        # Create the campaign
        create_response = client.post(
            "/api/v1/campaigns",
            json=campaign_data,
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        created_campaign = create_response.json()["data"]
        campaign_id = created_campaign["id"]
        
        # Verify the created campaign
        assert created_campaign["name"] == "Test Campaign"
        assert created_campaign["status"] == "draft"
        
        # Get the campaign by ID
        get_response = client.get(
            f"/api/v1/campaigns/{campaign_id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == 200
        retrieved_campaign = get_response.json()["data"]
        
        # Verify the retrieved campaign
        assert retrieved_campaign["id"] == campaign_id
        assert retrieved_campaign["name"] == "Test Campaign"
        assert retrieved_campaign["description"] == "Test campaign description"
        
    def test_update_campaign(self, client, auth_headers, mock_datetime, sample_campaign):
        """Test updating a campaign."""
        # Add the sample campaign to the storage
        CAMPAIGNS[str(sample_campaign.id)] = sample_campaign
        campaign_id = str(sample_campaign.id)
        
        # Update data
        update_data = {
            "data": {
                "name": "Updated Campaign Name",
                "status": "active"
            }
        }
        
        # Update the campaign
        update_response = client.put(
            f"/api/v1/campaigns/{campaign_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert update_response.status_code == 200
        updated_campaign = update_response.json()["data"]
        
        # Verify the updated campaign
        assert updated_campaign["name"] == "Updated Campaign Name"
        assert updated_campaign["status"] == "active"
        assert updated_campaign["description"] == sample_campaign.description
        
    def test_delete_campaign(self, client, auth_headers, sample_campaign):
        """Test deleting a campaign."""
        # Add the sample campaign to the storage
        CAMPAIGNS[str(sample_campaign.id)] = sample_campaign
        campaign_id = str(sample_campaign.id)
        
        # Delete the campaign
        delete_response = client.delete(
            f"/api/v1/campaigns/{campaign_id}",
            headers=auth_headers
        )
        
        assert delete_response.status_code == 204
        
        # Verify the campaign is deleted
        get_response = client.get(
            f"/api/v1/campaigns/{campaign_id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == 404
        
    def test_launch_campaign(self, client, auth_headers, sample_campaign):
        """Test launching a campaign."""
        # Add the sample campaign to the storage
        CAMPAIGNS[str(sample_campaign.id)] = sample_campaign
        campaign_id = str(sample_campaign.id)
        
        # Launch the campaign
        launch_response = client.post(
            f"/api/v1/campaigns/{campaign_id}/actions/launch",
            headers=auth_headers
        )
        
        assert launch_response.status_code == 200
        launched_campaign = launch_response.json()["data"]
        
        # Verify the campaign is active
        assert launched_campaign["status"] == "active"
        
    def test_pause_campaign(self, client, auth_headers, sample_campaign):
        """Test pausing a campaign."""
        # Set campaign to active so it can be paused
        sample_campaign.status = CampaignStatus.ACTIVE
        
        # Add the sample campaign to the storage
        CAMPAIGNS[str(sample_campaign.id)] = sample_campaign
        campaign_id = str(sample_campaign.id)
        
        # Pause the campaign
        pause_response = client.post(
            f"/api/v1/campaigns/{campaign_id}/actions/pause",
            headers=auth_headers
        )
        
        assert pause_response.status_code == 200
        paused_campaign = pause_response.json()["data"]
        
        # Verify the campaign is paused
        assert paused_campaign["status"] == "paused"