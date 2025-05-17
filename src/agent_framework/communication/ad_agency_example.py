"""
Advanced example implementation for an AI-native advertising agency.

This module demonstrates how the agent communication protocol can be used
to create a network of specialized agents that collaborate on advertising campaigns.
"""

import logging
from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime, timedelta

from ..core.message import MessageType, MessagePriority
from .protocol import StandardCommunicationProtocol, CommunicatingAgentImpl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define agency-specific message types
class AgencyMessageType(MessageType):
    # Campaign management
    CAMPAIGN_REQUEST = "CAMPAIGN_REQUEST"
    CAMPAIGN_APPROVED = "CAMPAIGN_APPROVED"
    CAMPAIGN_REJECTED = "CAMPAIGN_REJECTED"
    CAMPAIGN_UPDATE = "CAMPAIGN_UPDATE"
    
    # Creative production
    CREATIVE_REQUEST = "CREATIVE_REQUEST"
    CREATIVE_DELIVERY = "CREATIVE_DELIVERY"
    CREATIVE_FEEDBACK = "CREATIVE_FEEDBACK"
    CREATIVE_REVISION = "CREATIVE_REVISION"
    
    # Audience targeting
    AUDIENCE_REQUEST = "AUDIENCE_REQUEST"
    AUDIENCE_DELIVERY = "AUDIENCE_DELIVERY"
    
    # Media planning and buying
    MEDIA_PLAN_REQUEST = "MEDIA_PLAN_REQUEST"
    MEDIA_PLAN_DELIVERY = "MEDIA_PLAN_DELIVERY"
    MEDIA_BUY_EXECUTION = "MEDIA_BUY_EXECUTION"
    MEDIA_BUY_CONFIRMATION = "MEDIA_BUY_CONFIRMATION"
    
    # Performance reporting
    PERFORMANCE_REQUEST = "PERFORMANCE_REQUEST"
    PERFORMANCE_REPORT = "PERFORMANCE_REPORT"
    OPTIMIZATION_SUGGESTION = "OPTIMIZATION_SUGGESTION"
    
    # Knowledge sharing
    INSIGHT_SHARING = "INSIGHT_SHARING"
    KNOWLEDGE_REQUEST = "KNOWLEDGE_REQUEST"
    KNOWLEDGE_RESPONSE = "KNOWLEDGE_RESPONSE"


class CampaignManagerAgent(CommunicatingAgentImpl):
    """
    Agent responsible for managing the overall campaign lifecycle.
    
    This agent coordinates between clients, creative teams, audience specialists,
    and media planners to execute integrated advertising campaigns.
    """
    
    def __init__(self, agent_id: str, protocol: StandardCommunicationProtocol):
        super().__init__(agent_id, "Campaign Manager", protocol)
        self.active_campaigns = {}
        self.creative_agent_id = None
        self.audience_agent_id = None
        self.media_agent_id = None
        self.analytics_agent_id = None
        
        # Register message handlers
        self.register_message_handler(
            AgencyMessageType.CAMPAIGN_REQUEST, 
            self._handle_campaign_request
        )
        self.register_message_handler(
            AgencyMessageType.CREATIVE_DELIVERY,
            self._handle_creative_delivery
        )
        self.register_message_handler(
            AgencyMessageType.AUDIENCE_DELIVERY,
            self._handle_audience_delivery
        )
        self.register_message_handler(
            AgencyMessageType.MEDIA_PLAN_DELIVERY,
            self._handle_media_plan_delivery
        )
        self.register_message_handler(
            AgencyMessageType.PERFORMANCE_REPORT,
            self._handle_performance_report
        )
    
    def set_collaborator_agents(self, creative_id: str, audience_id: str, 
                               media_id: str, analytics_id: str) -> None:
        """Set the IDs of collaborator agents."""
        self.creative_agent_id = creative_id
        self.audience_agent_id = audience_id
        self.media_agent_id = media_id
        self.analytics_agent_id = analytics_id
    
    def initiate_campaign(self, campaign_details: Dict[str, Any]) -> str:
        """
        Start a new advertising campaign.
        
        Args:
            campaign_details: Dictionary containing campaign information
            
        Returns:
            str: The campaign ID
        """
        # Generate campaign ID if not provided
        campaign_id = campaign_details.get("id", f"camp-{str(uuid4())[:8]}")
        
        # Store campaign in active campaigns
        self.active_campaigns[campaign_id] = {
            "details": campaign_details,
            "status": "initiated",
            "created_at": datetime.now(),
            "components": {
                "creative": {"status": "pending"},
                "audience": {"status": "pending"},
                "media_plan": {"status": "pending"}
            },
            "conversation_id": None
        }
        
        logger.info(f"Initiating new campaign: {campaign_details.get('name')} (ID: {campaign_id})")
        
        # Request audience analysis
        audience_msg_id = self._request_audience_analysis(campaign_id, campaign_details)
        
        # Start tracking the conversation
        conversation_id = self.get_received_messages(message_id=audience_msg_id)[0].conversation_id
        self.active_campaigns[campaign_id]["conversation_id"] = conversation_id
        
        return campaign_id
    
    def _request_audience_analysis(self, campaign_id: str, campaign_details: Dict[str, Any]) -> str:
        """Request audience analysis for the campaign."""
        if not self.audience_agent_id:
            logger.error("No audience agent set for campaign manager")
            return None
            
        logger.info(f"Requesting audience analysis for campaign {campaign_id}")
        
        return self.send_message(
            recipient_id=self.audience_agent_id,
            message_type=AgencyMessageType.AUDIENCE_REQUEST,
            content={
                "campaign_id": campaign_id,
                "campaign_name": campaign_details.get("name"),
                "target_description": campaign_details.get("target_audience"),
                "campaign_objectives": campaign_details.get("objectives"),
                "product_category": campaign_details.get("product_category")
            },
            priority=MessagePriority.HIGH
        )
    
    def _request_creative_development(self, campaign_id: str, campaign_details: Dict[str, Any],
                                     audience_data: Dict[str, Any]) -> str:
        """Request creative development for the campaign."""
        if not self.creative_agent_id:
            logger.error("No creative agent set for campaign manager")
            return None
            
        logger.info(f"Requesting creative development for campaign {campaign_id}")
        
        return self.send_message(
            recipient_id=self.creative_agent_id,
            message_type=AgencyMessageType.CREATIVE_REQUEST,
            content={
                "campaign_id": campaign_id,
                "campaign_name": campaign_details.get("name"),
                "campaign_brief": campaign_details.get("brief"),
                "brand_guidelines": campaign_details.get("brand_guidelines"),
                "target_audience": audience_data,
                "required_assets": campaign_details.get("required_assets", []),
                "key_messages": campaign_details.get("key_messages", []),
                "tone_of_voice": campaign_details.get("tone_of_voice", "Professional")
            },
            conversation_id=self.active_campaigns[campaign_id]["conversation_id"],
            priority=MessagePriority.HIGH
        )
    
    def _request_media_plan(self, campaign_id: str, campaign_details: Dict[str, Any],
                           audience_data: Dict[str, Any], creative_data: Dict[str, Any]) -> str:
        """Request media planning for the campaign."""
        if not self.media_agent_id:
            logger.error("No media agent set for campaign manager")
            return None
            
        logger.info(f"Requesting media plan for campaign {campaign_id}")
        
        return self.send_message(
            recipient_id=self.media_agent_id,
            message_type=AgencyMessageType.MEDIA_PLAN_REQUEST,
            content={
                "campaign_id": campaign_id,
                "campaign_name": campaign_details.get("name"),
                "campaign_objectives": campaign_details.get("objectives"),
                "target_audience": audience_data,
                "creative_formats": [asset["type"] for asset in creative_data.get("assets", [])],
                "budget": campaign_details.get("budget"),
                "start_date": campaign_details.get("start_date"),
                "end_date": campaign_details.get("end_date"),
                "geography": campaign_details.get("geography", "National")
            },
            conversation_id=self.active_campaigns[campaign_id]["conversation_id"],
            priority=MessagePriority.HIGH
        )
    
    def _request_performance_tracking(self, campaign_id: str, campaign_details: Dict[str, Any],
                                    media_plan: Dict[str, Any]) -> str:
        """Request performance tracking for the campaign."""
        if not self.analytics_agent_id:
            logger.error("No analytics agent set for campaign manager")
            return None
            
        logger.info(f"Setting up performance tracking for campaign {campaign_id}")
        
        return self.send_message(
            recipient_id=self.analytics_agent_id,
            message_type=AgencyMessageType.PERFORMANCE_REQUEST,
            content={
                "campaign_id": campaign_id,
                "campaign_name": campaign_details.get("name"),
                "media_channels": media_plan.get("channels", []),
                "campaign_objectives": campaign_details.get("objectives"),
                "start_date": campaign_details.get("start_date"),
                "end_date": campaign_details.get("end_date"),
                "kpis": campaign_details.get("kpis", ["impressions", "clicks", "conversions"])
            },
            conversation_id=self.active_campaigns[campaign_id]["conversation_id"],
            priority=MessagePriority.MEDIUM
        )
    
    def _handle_campaign_request(self, message: Dict[str, Any]) -> None:
        """Handle incoming campaign requests from clients."""
        logger.info(f"Received campaign request from {message.sender_id}")
        campaign_details = message.content
        
        # Initiate the campaign
        campaign_id = self.initiate_campaign(campaign_details)
        
        # Acknowledge receipt
        self.send_message(
            recipient_id=message.sender_id,
            message_type=AgencyMessageType.CAMPAIGN_APPROVED,
            content={
                "campaign_id": campaign_id,
                "status": "initiated",
                "next_steps": "Performing audience analysis and creative development",
                "estimated_completion": (datetime.now() + timedelta(days=5)).isoformat()
            },
            conversation_id=message.conversation_id,
            priority=MessagePriority.HIGH
        )
    
    def _handle_audience_delivery(self, message: Dict[str, Any]) -> None:
        """Handle audience analysis delivery."""
        campaign_id = message.content.get("campaign_id")
        logger.info(f"Received audience analysis for campaign {campaign_id}")
        
        if campaign_id not in self.active_campaigns:
            logger.warning(f"Received audience for unknown campaign: {campaign_id}")
            return
            
        # Update campaign status
        campaign = self.active_campaigns[campaign_id]
        campaign["components"]["audience"] = {
            "status": "completed",
            "data": message.content.get("audience_data"),
            "completed_at": datetime.now()
        }
        
        # Request creative development with audience insights
        self._request_creative_development(
            campaign_id, 
            campaign["details"],
            message.content.get("audience_data")
        )
    
    def _handle_creative_delivery(self, message: Dict[str, Any]) -> None:
        """Handle creative assets delivery."""
        campaign_id = message.content.get("campaign_id")
        logger.info(f"Received creative assets for campaign {campaign_id}")
        
        if campaign_id not in self.active_campaigns:
            logger.warning(f"Received creative for unknown campaign: {campaign_id}")
            return
            
        # Update campaign status
        campaign = self.active_campaigns[campaign_id]
        campaign["components"]["creative"] = {
            "status": "completed",
            "data": message.content,
            "completed_at": datetime.now()
        }
        
        # If audience is also ready, request media plan
        if campaign["components"]["audience"]["status"] == "completed":
            self._request_media_plan(
                campaign_id,
                campaign["details"],
                campaign["components"]["audience"]["data"],
                message.content
            )
    
    def _handle_media_plan_delivery(self, message: Dict[str, Any]) -> None:
        """Handle media plan delivery."""
        campaign_id = message.content.get("campaign_id")
        logger.info(f"Received media plan for campaign {campaign_id}")
        
        if campaign_id not in self.active_campaigns:
            logger.warning(f"Received media plan for unknown campaign: {campaign_id}")
            return
            
        # Update campaign status
        campaign = self.active_campaigns[campaign_id]
        campaign["components"]["media_plan"] = {
            "status": "completed",
            "data": message.content.get("media_plan"),
            "completed_at": datetime.now()
        }
        
        # Set up performance tracking
        self._request_performance_tracking(
            campaign_id,
            campaign["details"],
            message.content.get("media_plan")
        )
        
        # Update overall campaign status
        campaign["status"] = "ready_for_launch"
        
        # Notify the client that campaign is ready
        if "client_id" in campaign["details"]:
            self.send_message(
                recipient_id=campaign["details"]["client_id"],
                message_type=AgencyMessageType.CAMPAIGN_UPDATE,
                content={
                    "campaign_id": campaign_id,
                    "status": "ready_for_launch",
                    "components_ready": ["audience", "creative", "media_plan"],
                    "next_steps": "Review and approve for launch"
                },
                conversation_id=campaign["conversation_id"],
                priority=MessagePriority.HIGH
            )
    
    def _handle_performance_report(self, message: Dict[str, Any]) -> None:
        """Handle performance reports."""
        campaign_id = message.content.get("campaign_id")
        logger.info(f"Received performance report for campaign {campaign_id}")
        
        # Forward performance report to client
        campaign = self.active_campaigns.get(campaign_id, {})
        if campaign and "client_id" in campaign.get("details", {}):
            self.send_message(
                recipient_id=campaign["details"]["client_id"],
                message_type=AgencyMessageType.PERFORMANCE_REPORT,
                content=message.content,
                conversation_id=campaign["conversation_id"]
            )


class CreativeAgent(CommunicatingAgentImpl):
    """
    Agent responsible for creative development.
    
    This agent creates advertising assets based on campaign briefs and
    audience insights.
    """
    
    def __init__(self, agent_id: str, protocol: StandardCommunicationProtocol):
        super().__init__(agent_id, "Creative Developer", protocol)
        self.active_projects = {}
        
        # Register message handlers
        self.register_message_handler(
            AgencyMessageType.CREATIVE_REQUEST, 
            self._handle_creative_request
        )
        self.register_message_handler(
            AgencyMessageType.CREATIVE_FEEDBACK,
            self._handle_creative_feedback
        )
    
    def _handle_creative_request(self, message: Dict[str, Any]) -> None:
        """Handle incoming creative requests."""
        campaign_id = message.content.get("campaign_id")
        logger.info(f"Received creative request for campaign {campaign_id}")
        
        # Store project information
        self.active_projects[campaign_id] = {
            "brief": message.content,
            "status": "in_progress",
            "started_at": datetime.now(),
            "conversation_id": message.conversation_id
        }
        
        # In a real implementation, this would trigger AI-driven creative generation
        # For this example, we'll simulate completed creative assets
        
        # Prepare creative assets
        creative_assets = {
            "campaign_id": campaign_id,
            "assets": [
                {
                    "type": "headline",
                    "content": f"Generated headline for {message.content.get('campaign_name')}",
                    "variations": 3
                },
                {
                    "type": "body_copy",
                    "content": f"Generated body copy that speaks to {message.content.get('target_audience', {}).get('demographics', 'all audiences')}",
                    "variations": 2
                },
                {
                    "type": "social_post",
                    "platform": "instagram",
                    "content": "Instagram post copy with relevant hashtags",
                    "visual_description": "Visual featuring product with lifestyle backdrop"
                }
            ],
            "rationale": "Creative assets designed to appeal to target audience demographics and psychographics, while adhering to brand guidelines."
        }
        
        # Deliver creative assets
        self.send_message(
            recipient_id=message.sender_id,
            message_type=AgencyMessageType.CREATIVE_DELIVERY,
            content=creative_assets,
            conversation_id=message.conversation_id,
            priority=MessagePriority.HIGH
        )
        
        # Update project status
        self.active_projects[campaign_id]["status"] = "delivered"
        self.active_projects[campaign_id]["completed_at"] = datetime.now()
    
    def _handle_creative_feedback(self, message: Dict[str, Any]) -> None:
        """Handle feedback on delivered creative assets."""
        campaign_id = message.content.get("campaign_id")
        logger.info(f"Received feedback for campaign {campaign_id} creative")
        
        if campaign_id not in self.active_projects:
            logger.warning(f"Received feedback for unknown campaign: {campaign_id}")
            return
        
        # Update project status
        self.active_projects[campaign_id]["status"] = "revision_required"
        self.active_projects[campaign_id]["feedback"] = message.content.get("feedback")
        
        # In a real implementation, this would trigger revisions to the creative
        # For this example, we'll simulate revised creative assets
        
        # Prepare revised creative assets
        revised_assets = {
            "campaign_id": campaign_id,
            "assets": [
                {
                    "type": "headline",
                    "content": f"Revised headline based on feedback for {self.active_projects[campaign_id]['brief'].get('campaign_name')}",
                    "variations": 2
                },
                {
                    "type": "body_copy",
                    "content": "Revised body copy addressing feedback points",
                    "variations": 1
                }
            ],
            "revision_notes": "Changes made in response to specific feedback points."
        }
        
        # Deliver revised creative assets
        self.send_message(
            recipient_id=message.sender_id,
            message_type=AgencyMessageType.CREATIVE_REVISION,
            content=revised_assets,
            conversation_id=message.conversation_id,
            priority=MessagePriority.HIGH
        )
        
        # Update project status
        self.active_projects[campaign_id]["status"] = "revision_delivered"
        self.active_projects[campaign_id]["revised_at"] = datetime.now()


# Example function to demonstrate the communication flow
def run_ad_agency_example():
    """Run an example of the ad agency agent communication."""
    # Create the communication protocol
    protocol = StandardCommunicationProtocol()
    
    # Create agents
    campaign_manager = CampaignManagerAgent("campaign-mgr-1", protocol)
    creative_agent = CreativeAgent("creative-1", protocol)
    
    # Set up agent relationships
    campaign_manager.set_collaborator_agents(
        creative_id="creative-1",
        audience_id="audience-1",  # These would be actual agent IDs in a full implementation
        media_id="media-1",
        analytics_id="analytics-1"
    )
    
    # Create a sample campaign
    campaign_details = {
        "name": "Summer Product Launch 2023",
        "brief": "Launch our new summer product line with focus on outdoor activities",
        "target_audience": "Adults 25-45 interested in outdoor activities and sustainability",
        "objectives": ["Brand awareness", "Product trial", "Online sales"],
        "budget": 250000,
        "start_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=90)).isoformat(),
        "required_assets": ["headlines", "body_copy", "social_media_posts"],
        "key_messages": ["Sustainable materials", "Perfect for summer activities", "Limited edition"],
        "brand_guidelines": "Modern, vibrant, environmentally conscious",
        "client_id": "client-1"
    }
    
    # Initiate campaign
    campaign_id = campaign_manager.initiate_campaign(campaign_details)
    
    # Process messages - in a real system this would be done by a message processing service
    processed = protocol.process_message_queue()
    logger.info(f"Processed {processed} messages")
    
    # In a full implementation, this example would include audience and media agents
    # For demonstration, we'll simulate the audience delivery directly
    
    # Simulate audience agent response
    campaign_manager.receive_message({
        "id": str(uuid4()),
        "sender_id": "audience-1",
        "recipient_id": campaign_manager.id,
        "message_type": AgencyMessageType.AUDIENCE_DELIVERY,
        "content": {
            "campaign_id": campaign_id,
            "audience_data": {
                "demographics": {
                    "age_range": "25-45",
                    "gender_split": {"male": 0.48, "female": 0.51, "other": 0.01},
                    "income_level": "middle to upper-middle",
                    "education": "college degree or higher"
                },
                "psychographics": {
                    "interests": ["outdoor activities", "sustainability", "fitness", "travel"],
                    "values": ["environmental consciousness", "active lifestyle", "quality"],
                    "behaviors": ["researches products online", "influenced by social media"]
                },
                "media_consumption": {
                    "platforms": ["instagram", "youtube", "podcasts", "outdoor"],
                    "peak_times": ["weekday evenings", "weekend mornings"]
                },
                "segments": [
                    {"name": "Eco Warriors", "size": 0.35, "description": "Highly environmentally conscious consumers"},
                    {"name": "Active Adventurers", "size": 0.45, "description": "Outdoor enthusiasts seeking quality gear"},
                    {"name": "Trend Followers", "size": 0.2, "description": "Fashion-focused consumers interested in limited editions"}
                ]
            }
        },
        "conversation_id": campaign_manager.active_campaigns[campaign_id]["conversation_id"],
        "priority": MessagePriority.HIGH,
        "timestamp": datetime.now().isoformat()
    })
    
    # Process messages again
    processed = protocol.process_message_queue()
    logger.info(f"Processed {processed} messages")
    
    # Simulate media agent response after creative is delivered
    campaign_manager.receive_message({
        "id": str(uuid4()),
        "sender_id": "media-1",
        "recipient_id": campaign_manager.id,
        "message_type": AgencyMessageType.MEDIA_PLAN_DELIVERY,
        "content": {
            "campaign_id": campaign_id,
            "media_plan": {
                "channels": [
                    {"name": "Instagram", "format": "Stories + Feed", "budget_allocation": 0.3, "rationale": "High engagement with target audience"},
                    {"name": "YouTube", "format": "Pre-roll + Influencer", "budget_allocation": 0.25, "rationale": "Video showcases product benefits"},
                    {"name": "Podcasts", "format": "Host-read ads", "budget_allocation": 0.2, "rationale": "Authentic endorsements for credibility"},
                    {"name": "Outdoor", "format": "Urban billboards", "budget_allocation": 0.15, "rationale": "Visibility in active lifestyle locations"},
                    {"name": "Paid Search", "format": "Google Ads", "budget_allocation": 0.1, "rationale": "Capture intent-based traffic"}
                ],
                "phasing": {
                    "phase1": {"name": "Teaser", "duration": "2 weeks", "channels": ["Instagram", "YouTube"]},
                    "phase2": {"name": "Launch", "duration": "4 weeks", "channels": ["All channels"]},
                    "phase3": {"name": "Sustain", "duration": "6 weeks", "channels": ["Podcasts", "Paid Search", "Instagram"]}
                },
                "estimated_reach": 2500000,
                "estimated_frequency": 3.5,
                "estimated_cpm": 28.50
            }
        },
        "conversation_id": campaign_manager.active_campaigns[campaign_id]["conversation_id"],
        "priority": MessagePriority.HIGH,
        "timestamp": datetime.now().isoformat()
    })
    
    # Process messages again
    processed = protocol.process_message_queue()
    logger.info(f"Processed {processed} messages")
    
    return {
        "campaign_manager": campaign_manager,
        "creative_agent": creative_agent,
        "protocol": protocol,
        "campaign_id": campaign_id
    }


if __name__ == "__main__":
    run_ad_agency_example()