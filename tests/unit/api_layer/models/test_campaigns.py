"""
Unit tests for campaign models.
"""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from src.api_layer.models.campaigns import (
    Campaign, 
    CampaignCreate, 
    CampaignUpdate,
    CampaignStatus,
    CampaignType,
    CampaignObjective,
    CampaignBudget,
    CampaignBudgetType,
    TargetingCriteria
)


@pytest.mark.unit
@pytest.mark.models
class TestCampaignModel:
    """Tests for the Campaign model."""

    def test_campaign_create_valid(self, mock_datetime):
        """Test creating a valid campaign."""
        campaign_data = {
            "name": "Test Campaign",
            "description": "Test campaign description",
            "type": CampaignType.AWARENESS,
            "objective": CampaignObjective.BRAND_AWARENESS,
            "start_date": mock_datetime,
            "end_date": mock_datetime + timedelta(days=30),
            "budget": {
                "amount": 1000.0,
                "currency": "USD",
                "type": CampaignBudgetType.DAILY
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
        
        campaign = CampaignCreate(**campaign_data)
        
        assert campaign.name == "Test Campaign"
        assert campaign.description == "Test campaign description"
        assert campaign.type == CampaignType.AWARENESS
        assert campaign.objective == CampaignObjective.BRAND_AWARENESS
        assert campaign.start_date == mock_datetime
        assert campaign.end_date == mock_datetime + timedelta(days=30)
        assert campaign.budget.amount == 1000.0
        assert campaign.budget.currency == "USD"
        assert campaign.budget.type == CampaignBudgetType.DAILY
        assert campaign.targeting.demographics["age_ranges"] == ["18-24", "25-34"]
        assert campaign.targeting.demographics["genders"] == ["male", "female"]
        assert campaign.targeting.locations[0]["country"] == "US"
        assert campaign.tags == ["test", "brand"]

    def test_campaign_create_missing_required_fields(self):
        """Test validation errors when required fields are missing."""
        # Missing name
        campaign_data = {
            "type": CampaignType.AWARENESS,
            "objective": CampaignObjective.BRAND_AWARENESS,
            "start_date": datetime.now(),
            "budget": {
                "amount": 1000.0,
                "currency": "USD",
                "type": CampaignBudgetType.DAILY
            },
            "targeting": {}
        }
        
        with pytest.raises(ValidationError) as exc_info:
            CampaignCreate(**campaign_data)
        
        assert "name" in str(exc_info.value)

    def test_campaign_create_invalid_date_range(self, mock_datetime):
        """Test validation error when end_date is before start_date."""
        campaign_data = {
            "name": "Test Campaign",
            "type": CampaignType.AWARENESS,
            "objective": CampaignObjective.BRAND_AWARENESS,
            "start_date": mock_datetime,
            "end_date": mock_datetime - timedelta(days=1),  # End date before start date
            "budget": {
                "amount": 1000.0,
                "currency": "USD",
                "type": CampaignBudgetType.DAILY
            },
            "targeting": {}
        }
        
        with pytest.raises(ValidationError) as exc_info:
            CampaignCreate(**campaign_data)
        
        assert "end_date must be after start_date" in str(exc_info.value)

    def test_campaign_update_partial(self):
        """Test partial update of a campaign."""
        update_data = {
            "name": "Updated Campaign Name",
            "status": CampaignStatus.ACTIVE
        }
        
        update = CampaignUpdate(**update_data)
        
        assert update.name == "Updated Campaign Name"
        assert update.status == CampaignStatus.ACTIVE
        assert update.description is None
        assert update.type is None
        assert update.budget is None

    def test_campaign_budget_currency_uppercase(self):
        """Test that currency code is converted to uppercase."""
        budget_data = {
            "amount": 1000.0,
            "currency": "usd",  # Lowercase
            "type": CampaignBudgetType.DAILY
        }
        
        budget = CampaignBudget(**budget_data)
        
        assert budget.currency == "USD"  # Should be converted to uppercase