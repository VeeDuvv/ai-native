"""
Tests for the advertising agency communication examples.
"""

import pytest
from datetime import datetime, timedelta

from src.agent_framework.core.message import MessagePriority
from src.agent_framework.communication.protocol import StandardCommunicationProtocol
from src.agent_framework.communication.ad_agency_example import (
    CampaignManagerAgent, 
    CreativeAgent,
    AgencyMessageType
)


@pytest.fixture
def communication_protocol():
    """Create a fresh communication protocol instance for testing."""
    return StandardCommunicationProtocol()


@pytest.fixture
def agency_agents(communication_protocol):
    """Create test agents for the ad agency example."""
    campaign_manager = CampaignManagerAgent("test-campaign-mgr", communication_protocol)
    creative_agent = CreativeAgent("test-creative", communication_protocol)
    
    # Set up agent relationships
    campaign_manager.set_collaborator_agents(
        creative_id="test-creative",
        audience_id="test-audience",  
        media_id="test-media",
        analytics_id="test-analytics"
    )
    
    return {
        "campaign_manager": campaign_manager,
        "creative_agent": creative_agent
    }


@pytest.fixture
def sample_campaign():
    """Create a sample campaign for testing."""
    return {
        "name": "Test Campaign",
        "brief": "Test campaign brief for unit testing",
        "target_audience": "Test audience",
        "objectives": ["Test objective 1", "Test objective 2"],
        "budget": 100000,
        "start_date": (datetime.now() + timedelta(days=10)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=40)).isoformat(),
        "required_assets": ["headlines", "body_copy"],
        "key_messages": ["Test message 1", "Test message 2"],
        "brand_guidelines": "Test brand guidelines",
        "client_id": "test-client"
    }


def test_campaign_initiation(agency_agents, sample_campaign, communication_protocol):
    """Test initiating a campaign."""
    campaign_manager = agency_agents["campaign_manager"]
    
    # Initiate campaign
    campaign_id = campaign_manager.initiate_campaign(sample_campaign)
    
    # Check that campaign was created
    assert campaign_id in campaign_manager.active_campaigns
    assert campaign_manager.active_campaigns[campaign_id]["status"] == "initiated"
    
    # Should have sent a message to audience agent
    assert len(campaign_manager.sent_messages) == 1
    assert campaign_manager.sent_messages[0].recipient_id == "test-audience"
    assert campaign_manager.sent_messages[0].message_type == AgencyMessageType.AUDIENCE_REQUEST


def test_audience_delivery(agency_agents, sample_campaign, communication_protocol):
    """Test handling audience delivery."""
    campaign_manager = agency_agents["campaign_manager"]
    
    # Initiate campaign
    campaign_id = campaign_manager.initiate_campaign(sample_campaign)
    conversation_id = campaign_manager.active_campaigns[campaign_id]["conversation_id"]
    
    # Simulate audience agent response
    audience_message = {
        "id": "test-message-id",
        "sender_id": "test-audience",
        "recipient_id": campaign_manager.id,
        "message_type": AgencyMessageType.AUDIENCE_DELIVERY,
        "content": {
            "campaign_id": campaign_id,
            "audience_data": {
                "demographics": {
                    "age_range": "25-45",
                    "gender_split": {"male": 0.5, "female": 0.5}
                },
                "psychographics": {
                    "interests": ["test interest 1", "test interest 2"]
                }
            }
        },
        "conversation_id": conversation_id,
        "priority": MessagePriority.HIGH,
        "timestamp": datetime.now().isoformat()
    }
    
    campaign_manager.receive_message(audience_message)
    
    # Check campaign was updated
    assert campaign_manager.active_campaigns[campaign_id]["components"]["audience"]["status"] == "completed"
    
    # Should have sent a message to creative agent
    assert len(campaign_manager.sent_messages) == 2  # 1 audience request + 1 creative request
    assert campaign_manager.sent_messages[1].recipient_id == "test-creative"
    assert campaign_manager.sent_messages[1].message_type == AgencyMessageType.CREATIVE_REQUEST


def test_creative_request_handling(agency_agents, communication_protocol):
    """Test handling creative requests."""
    campaign_manager = agency_agents["campaign_manager"]
    creative_agent = agency_agents["creative_agent"]
    
    # Send a creative request
    creative_request = {
        "id": "test-creative-request",
        "sender_id": campaign_manager.id,
        "recipient_id": creative_agent.id,
        "message_type": AgencyMessageType.CREATIVE_REQUEST,
        "content": {
            "campaign_id": "test-campaign",
            "campaign_name": "Test Campaign",
            "campaign_brief": "Test brief",
            "brand_guidelines": "Test guidelines",
            "target_audience": {"demographics": {"age_range": "25-45"}},
            "required_assets": ["headlines", "body_copy"]
        },
        "conversation_id": "test-conversation",
        "priority": MessagePriority.HIGH,
        "timestamp": datetime.now().isoformat()
    }
    
    creative_agent.receive_message(creative_request)
    
    # Check project was created
    assert "test-campaign" in creative_agent.active_projects
    assert creative_agent.active_projects["test-campaign"]["status"] == "delivered"
    
    # Should have sent a message with creative assets
    assert len(creative_agent.sent_messages) == 1
    assert creative_agent.sent_messages[0].recipient_id == campaign_manager.id
    assert creative_agent.sent_messages[0].message_type == AgencyMessageType.CREATIVE_DELIVERY


def test_creative_delivery_handling(agency_agents, sample_campaign, communication_protocol):
    """Test handling creative delivery."""
    campaign_manager = agency_agents["campaign_manager"]
    
    # Initiate campaign
    campaign_id = campaign_manager.initiate_campaign(sample_campaign)
    conversation_id = campaign_manager.active_campaigns[campaign_id]["conversation_id"]
    
    # Simulate audience delivery first
    campaign_manager.active_campaigns[campaign_id]["components"]["audience"] = {
        "status": "completed",
        "data": {"demographics": {"age_range": "25-45"}},
        "completed_at": datetime.now()
    }
    
    # Simulate creative delivery
    creative_message = {
        "id": "test-creative-delivery",
        "sender_id": "test-creative",
        "recipient_id": campaign_manager.id,
        "message_type": AgencyMessageType.CREATIVE_DELIVERY,
        "content": {
            "campaign_id": campaign_id,
            "assets": [
                {
                    "type": "headline",
                    "content": "Test headline",
                    "variations": 2
                }
            ]
        },
        "conversation_id": conversation_id,
        "priority": MessagePriority.HIGH,
        "timestamp": datetime.now().isoformat()
    }
    
    campaign_manager.receive_message(creative_message)
    
    # Check campaign was updated
    assert campaign_manager.active_campaigns[campaign_id]["components"]["creative"]["status"] == "completed"
    
    # Should have sent a message to media agent
    assert campaign_manager.sent_messages[-1].recipient_id == "test-media"
    assert campaign_manager.sent_messages[-1].message_type == AgencyMessageType.MEDIA_PLAN_REQUEST


def test_full_campaign_flow(agency_agents, sample_campaign, communication_protocol):
    """Test the full campaign workflow."""
    campaign_manager = agency_agents["campaign_manager"]
    
    # Initiate campaign
    campaign_id = campaign_manager.initiate_campaign(sample_campaign)
    conversation_id = campaign_manager.active_campaigns[campaign_id]["conversation_id"]
    
    # Simulate audience delivery
    audience_message = {
        "id": "test-message-id-1",
        "sender_id": "test-audience",
        "recipient_id": campaign_manager.id,
        "message_type": AgencyMessageType.AUDIENCE_DELIVERY,
        "content": {
            "campaign_id": campaign_id,
            "audience_data": {
                "demographics": {"age_range": "25-45"}
            }
        },
        "conversation_id": conversation_id,
        "timestamp": datetime.now().isoformat()
    }
    campaign_manager.receive_message(audience_message)
    
    # Process messages
    communication_protocol.process_message_queue()
    
    # Simulate creative delivery
    creative_message = {
        "id": "test-message-id-2",
        "sender_id": "test-creative",
        "recipient_id": campaign_manager.id,
        "message_type": AgencyMessageType.CREATIVE_DELIVERY,
        "content": {
            "campaign_id": campaign_id,
            "assets": [{"type": "headline", "content": "Test headline"}]
        },
        "conversation_id": conversation_id,
        "timestamp": datetime.now().isoformat()
    }
    campaign_manager.receive_message(creative_message)
    
    # Simulate media plan delivery
    media_message = {
        "id": "test-message-id-3",
        "sender_id": "test-media",
        "recipient_id": campaign_manager.id,
        "message_type": AgencyMessageType.MEDIA_PLAN_DELIVERY,
        "content": {
            "campaign_id": campaign_id,
            "media_plan": {
                "channels": [{"name": "Test Channel", "budget_allocation": 1.0}]
            }
        },
        "conversation_id": conversation_id,
        "timestamp": datetime.now().isoformat()
    }
    campaign_manager.receive_message(media_message)
    
    # Check final campaign status
    assert campaign_manager.active_campaigns[campaign_id]["status"] == "ready_for_launch"
    assert campaign_manager.active_campaigns[campaign_id]["components"]["audience"]["status"] == "completed"
    assert campaign_manager.active_campaigns[campaign_id]["components"]["creative"]["status"] == "completed"
    assert campaign_manager.active_campaigns[campaign_id]["components"]["media_plan"]["status"] == "completed"
    
    # Should have sent a message to client
    client_messages = [msg for msg in campaign_manager.sent_messages 
                    if msg.recipient_id == "test-client"]
    assert len(client_messages) == 1
    assert client_messages[0].message_type == AgencyMessageType.CAMPAIGN_UPDATE
    assert client_messages[0].content["status"] == "ready_for_launch"