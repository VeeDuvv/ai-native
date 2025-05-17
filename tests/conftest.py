"""
Pytest configuration file with fixtures shared across all tests.
"""

import pytest
import uuid
from datetime import datetime, date, timedelta
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api_layer.core.app import app
from src.api_layer.models.campaigns import Campaign, CampaignStatus, CampaignType, CampaignObjective, CampaignBudget, CampaignBudgetType, TargetingCriteria
from src.api_layer.models.creatives import Creative, CreativeType, CreativeStatus, CreativeFormat
from src.api_layer.models.audiences import Audience, AudienceType, AudienceStatus, AudienceCriteria
from src.api_layer.models.media import MediaChannel, MediaBudget, MediaPlacement, MediaChannelType, MediaPlacementStatus, BudgetType, MediaPacingStrategy, BiddingStrategy


@pytest.fixture
def test_app():
    """
    Create a FastAPI test app.
    """
    return app


@pytest.fixture
def client(test_app):
    """
    Create a FastAPI TestClient.
    """
    return TestClient(test_app)


@pytest.fixture
def mock_uuid():
    """
    Return a fixed UUID for testing.
    """
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def mock_datetime():
    """
    Return a fixed datetime for testing.
    """
    return datetime(2025, 1, 1, 12, 0, 0)


@pytest.fixture
def mock_date():
    """
    Return a fixed date for testing.
    """
    return date(2025, 1, 1)


@pytest.fixture
def sample_campaign(mock_uuid, mock_datetime):
    """
    Create a sample campaign for testing.
    """
    return Campaign(
        id=mock_uuid,
        name="Test Campaign",
        description="Test campaign description",
        status=CampaignStatus.DRAFT,
        type=CampaignType.AWARENESS,
        objective=CampaignObjective.BRAND_AWARENESS,
        start_date=mock_datetime,
        end_date=mock_datetime + timedelta(days=30),
        budget=CampaignBudget(
            amount=1000.0,
            currency="USD",
            type=CampaignBudgetType.DAILY
        ),
        targeting=TargetingCriteria(
            demographics={
                "age_ranges": ["18-24", "25-34"],
                "genders": ["male", "female"]
            },
            locations=[
                {"country": "US", "state": "CA"}
            ]
        ),
        creatives=[],
        performance=None,
        tags=["test", "brand"],
        metadata={"source": "test"},
        created_at=mock_datetime,
        updated_at=mock_datetime
    )


@pytest.fixture
def sample_creative(mock_uuid, mock_datetime):
    """
    Create a sample creative for testing.
    """
    return Creative(
        id=mock_uuid,
        name="Test Creative",
        description="Test creative description",
        type=CreativeType.IMAGE,
        format=CreativeFormat.SQUARE,
        content={
            "url": "https://example.com/image.jpg",
            "alt_text": "Sample image",
            "width": 1200,
            "height": 1200,
            "format": "jpg"
        },
        dimensions={
            "width": 1200,
            "height": 1200,
            "aspect_ratio": "1:1"
        },
        status=CreativeStatus.DRAFT,
        variations=[],
        campaign_ids=[],
        target_url=None,
        performance=None,
        tags=["test", "image"],
        metadata={"source": "test"},
        created_at=mock_datetime,
        updated_at=mock_datetime
    )


@pytest.fixture
def sample_audience(mock_uuid, mock_datetime):
    """
    Create a sample audience for testing.
    """
    return Audience(
        id=mock_uuid,
        name="Test Audience",
        description="Test audience description",
        type=AudienceType.DEMOGRAPHIC,
        status=AudienceStatus.DRAFT,
        criteria=AudienceCriteria(
            demographic={
                "age_ranges": ["18-24", "25-34"],
                "genders": ["male", "female"]
            }
        ),
        size_estimate=None,
        campaign_ids=[],
        tags=["test", "demographic"],
        metadata={"source": "test"},
        created_at=mock_datetime,
        updated_at=mock_datetime
    )


@pytest.fixture
def sample_media_channel(mock_uuid, mock_datetime):
    """
    Create a sample media channel for testing.
    """
    return MediaChannel(
        id=mock_uuid,
        name="Test Channel",
        type=MediaChannelType.SOCIAL,
        platform="Instagram",
        description="Test channel description",
        account_id="account123",
        capabilities=["image", "video", "carousel"],
        formats=["square", "portrait"],
        targeting_options={
            "demographics": ["age", "gender"],
            "interests": ["fashion", "technology"]
        },
        api_integration=True,
        active=True,
        tags=["test", "social"],
        metadata={"source": "test"},
        created_at=mock_datetime,
        updated_at=mock_datetime
    )


@pytest.fixture
def sample_media_budget(mock_uuid, mock_datetime, mock_date):
    """
    Create a sample media budget for testing.
    """
    return MediaBudget(
        id=mock_uuid,
        name="Test Budget",
        campaign_id=mock_uuid,
        channel_id=mock_uuid,
        amount=1000.0,
        currency="USD",
        type=BudgetType.DAILY,
        start_date=mock_date,
        end_date=mock_date + timedelta(days=30),
        pacing_strategy=MediaPacingStrategy.EVEN,
        pacing_schedule=None,
        spend_to_date=0.0,
        status="active",
        created_at=mock_datetime,
        updated_at=mock_datetime
    )


@pytest.fixture
def sample_media_placement(mock_uuid, mock_datetime):
    """
    Create a sample media placement for testing.
    """
    return MediaPlacement(
        id=mock_uuid,
        name="Test Placement",
        description="Test placement description",
        campaign_id=mock_uuid,
        channel_id=mock_uuid,
        creative_ids=[mock_uuid],
        budget_id=mock_uuid,
        status=MediaPlacementStatus.DRAFT,
        targeting={"audience_ids": [str(mock_uuid)]},
        bid_config={
            "strategy": BiddingStrategy.CPM,
            "amount": 5.0
        },
        delivery_settings={
            "delivery_pacing": "standard",
            "ad_rotation": "optimize",
            "start_date": mock_datetime.date()
        },
        performance=None,
        external_id=None,
        tags=["test", "placement"],
        metadata={"source": "test"},
        created_at=mock_datetime,
        updated_at=mock_datetime
    )


@pytest.fixture
def auth_headers():
    """
    Return authorization headers for API requests.
    
    In a real test, this would generate a valid JWT token.
    For now, we'll use a mock token.
    """
    return {
        "Authorization": "Bearer mock_token"
    }