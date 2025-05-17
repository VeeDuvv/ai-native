"""
Example implementations using the agent communication protocol.

This module provides concrete examples of how to implement and use
the communication protocol between agents.
"""

from typing import Dict, Any, Optional
import logging

from ..core.message import MessageType, MessagePriority
from .protocol import StandardCommunicationProtocol, CommunicatingAgentImpl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define custom message types
class AdAgencyMessageType(MessageType):
    CAMPAIGN_REQUEST = "CAMPAIGN_REQUEST"
    CREATIVE_REVIEW = "CREATIVE_REVIEW"
    AUDIENCE_ANALYSIS = "AUDIENCE_ANALYSIS"
    MEDIA_PLACEMENT = "MEDIA_PLACEMENT"
    PERFORMANCE_REPORT = "PERFORMANCE_REPORT"


class CampaignManagerAgent(CommunicatingAgentImpl):
    """Example agent that manages advertising campaigns."""
    
    def __init__(self, agent_id: str, protocol: StandardCommunicationProtocol):
        super().__init__(agent_id, "Campaign Manager", protocol)
        
        # Register message handlers
        self.register_message_handler(
            AdAgencyMessageType.CAMPAIGN_REQUEST, 
            self._handle_campaign_request
        )
        self.register_message_handler(
            AdAgencyMessageType.PERFORMANCE_REPORT,
            self._handle_performance_report
        )
    
    def create_campaign(self, creative_agent_id: str, campaign_details: Dict[str, Any]) -> str:
        """Create a new campaign and request creative development."""
        logger.info(f"Creating new campaign: {campaign_details.get('name', 'Unnamed')}")
        
        # Send message to creative agent
        return self.send_message(
            recipient_id=creative_agent_id,
            message_type=AdAgencyMessageType.CAMPAIGN_REQUEST,
            content={
                "campaign_id": campaign_details.get("id"),
                "campaign_name": campaign_details.get("name"),
                "campaign_brief": campaign_details.get("brief"),
                "target_audience": campaign_details.get("target_audience"),
                "required_assets": campaign_details.get("required_assets", [])
            },
            priority=MessagePriority.HIGH
        )
    
    def _handle_campaign_request(self, message: Dict[str, Any]) -> None:
        """Handle incoming campaign requests."""
        logger.info(f"Received campaign request from {message.sender_id}")
        # Implementation for handling campaign requests
        
    def _handle_performance_report(self, message: Dict[str, Any]) -> None:
        """Handle incoming performance reports."""
        logger.info(f"Received performance report from {message.sender_id}")
        # Implementation for processing performance reports


class CreativeAgent(CommunicatingAgentImpl):
    """Example agent that produces creative assets."""
    
    def __init__(self, agent_id: str, protocol: StandardCommunicationProtocol):
        super().__init__(agent_id, "Creative Producer", protocol)
        
        # Register message handlers
        self.register_message_handler(
            AdAgencyMessageType.CAMPAIGN_REQUEST, 
            self._handle_campaign_request
        )
        self.register_message_handler(
            AdAgencyMessageType.CREATIVE_REVIEW,
            self._handle_creative_review
        )
    
    def _handle_campaign_request(self, message: Dict[str, Any]) -> None:
        """Handle incoming campaign requests by creating creative assets."""
        logger.info(f"Received creative request for campaign: {message.content.get('campaign_name')}")
        
        # Process the creative request
        # ...
        
        # Send creative assets back to the requester
        self.send_message(
            recipient_id=message.sender_id,
            message_type=AdAgencyMessageType.CREATIVE_REVIEW,
            content={
                "campaign_id": message.content.get("campaign_id"),
                "assets": [
                    {
                        "type": "headline",
                        "content": "Generated headline based on brief"
                    },
                    {
                        "type": "body_copy",
                        "content": "Generated body copy based on brief"
                    }
                ],
                "notes": "Creative assets generated based on campaign brief"
            },
            conversation_id=message.conversation_id
        )
    
    def _handle_creative_review(self, message: Dict[str, Any]) -> None:
        """Handle feedback on creative assets."""
        logger.info(f"Received feedback on creative assets from {message.sender_id}")
        # Implementation for handling creative review feedback


# Example usage
def run_example():
    """Run an example of agent communication."""
    # Create the communication protocol
    protocol = StandardCommunicationProtocol()
    
    # Create agents
    campaign_manager = CampaignManagerAgent("campaign-agent-1", protocol)
    creative_agent = CreativeAgent("creative-agent-1", protocol)
    
    # Initiate a campaign request
    campaign_details = {
        "id": "camp-001",
        "name": "Summer Sale 2023",
        "brief": "Promote summer products with a focus on outdoor activities",
        "target_audience": "Adults 25-45 interested in outdoor activities",
        "required_assets": ["headlines", "body_copy", "social_media_posts"]
    }
    
    campaign_manager.create_campaign(creative_agent.id, campaign_details)
    
    # Process messages
    processed_count = protocol.process_message_queue()
    logger.info(f"Processed {processed_count} messages")
    
    # Process any response messages
    processed_count = protocol.process_message_queue()
    logger.info(f"Processed {processed_count} response messages")
    
    return campaign_manager, creative_agent, protocol


if __name__ == "__main__":
    run_example()