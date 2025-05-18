# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file creates a special AI helper that makes the pictures, videos, and words 
# for advertisements. It's like an artist and writer who makes things that get people 
# excited about products.

# High School Explanation:
# This module implements the Creative Agent, which is responsible for developing
# advertising creative assets based on campaign briefs. It handles the generation
# of headlines, copy, visual concepts, and other creative elements required for campaigns.

"""
Creative Agent implementation for advertising asset development.

The Creative Agent is responsible for generating creative assets for advertising
campaigns, including headlines, body copy, visual concepts, and specialized
assets for different media channels.
"""

import logging
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set

from ..core.base import AbstractOperationalAgent, AbstractCommunicatingAgent
from ..communication.protocol import (
    StandardCommunicationProtocol,
    MessagePriority,
    MessageType
)
from ...process_framework.interface import BaseProcessAwareAgent
from ..specialized.strategy import StrategyMessageType

logger = logging.getLogger(__name__)

# Define creative asset types
class CreativeAssetType:
    """Types of creative assets the agent can produce."""
    HEADLINE = "headline"
    BODY_COPY = "body_copy"
    DISPLAY_AD = "display_ad"
    SOCIAL_POST = "social_post"
    VIDEO_SCRIPT = "video_script"
    EMAIL = "email"
    LANDING_PAGE = "landing_page"
    BANNER = "banner"


class CreativeAgent(BaseProcessAwareAgent):
    """
    Agent responsible for creative asset development.
    
    The Creative Agent receives campaign briefs and strategy information,
    then produces creative assets that align with the campaign objectives
    and target audience.
    """
    
    def __init__(
        self, 
        agent_id: str, 
        protocol: StandardCommunicationProtocol
    ):
        """Initialize the creative agent.
        
        Args:
            agent_id: Unique identifier for this agent
            protocol: Communication protocol for inter-agent messaging
        """
        super().__init__(agent_id, "Creative Agent")
        self.protocol = protocol
        
        # Register with communication protocol
        self.protocol.register_agent(self)
        
        # Track active projects and their status
        self.active_projects: Dict[str, Dict[str, Any]] = {}
        
        # Asset library
        self.asset_library: Dict[str, Dict[str, Any]] = {}
        
        # Register message handlers
        self.register_message_handler(
            StrategyMessageType.CREATIVE_BRIEF,
            self._handle_creative_brief
        )
        self.register_message_handler(
            StrategyMessageType.CREATIVE_FEEDBACK,
            self._handle_creative_feedback
        )
        
        # Subscribe to relevant topics
        self.subscribe_to_topic("campaign_updates")
        self.subscribe_to_topic("audience_insights", {"relevance": "creative"})
        
        # Register process activities
        self._register_process_activities()
        
        logger.info(f"Creative Agent initialized with ID: {agent_id}")
    
    def _handle_creative_brief(self, message: Dict[str, Any]) -> None:
        """Handle incoming creative brief messages.
        
        Args:
            message: The message containing the creative brief
        """
        logger.info(f"Received creative brief from {message.sender_id}")
        
        # Extract information from the brief
        campaign_id = message.content.get("campaign_id")
        campaign_name = message.content.get("campaign_name")
        
        # Store project information
        self.active_projects[campaign_id] = {
            "campaign_name": campaign_name,
            "brief": message.content,
            "status": "received",
            "received_at": datetime.now().isoformat(),
            "conversation_id": message.conversation_id,
            "assets": [],
            "feedback": []
        }
        
        # Acknowledge receipt
        self.send_message(
            recipient_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content={
                "success": True,
                "campaign_id": campaign_id,
                "message": f"Creative brief received for campaign: {campaign_name}",
                "estimated_delivery": (datetime.now() + timedelta(days=3)).isoformat()
            },
            conversation_id=message.conversation_id,
            priority=MessagePriority.MEDIUM
        )
        
        # Start working on assets
        self._start_creative_development(campaign_id)
    
    def _start_creative_development(self, campaign_id: str) -> None:
        """Start the creative development process for a campaign.
        
        Args:
            campaign_id: ID of the campaign
        """
        if campaign_id not in self.active_projects:
            logger.warning(f"Cannot start creative development for unknown campaign: {campaign_id}")
            return
            
        # Update project status
        self.active_projects[campaign_id]["status"] = "in_progress"
        self.active_projects[campaign_id]["development_started"] = datetime.now().isoformat()
        
        logger.info(f"Starting creative development for campaign {campaign_id}")
        
        # In a real implementation, this would be a more complex and possibly async process
        # For demonstration, we'll simulate a development process
        
        # Extract information from brief
        brief = self.active_projects[campaign_id]["brief"]
        key_messages = brief.get("key_messages", [])
        target_audience = brief.get("target_audience", {})
        creative_approach = brief.get("creative_approach", {})
        required_assets = brief.get("required_assets", [])
        
        # Create assets based on requirements
        assets = []
        conversation_id = self.active_projects[campaign_id]["conversation_id"]
        sender_id = None
        
        # Find sender of the brief
        for message_id in self.protocol.message_history:
            if message_id.conversation_id == conversation_id and message_id.message_type == StrategyMessageType.CREATIVE_BRIEF:
                sender_id = message_id.sender_id
                break
        
        # Publish update about starting work
        self.publish_to_topic(
            "creative_deliverables",
            {
                "event": "creative_development_started",
                "campaign_id": campaign_id,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # This would be implemented as a proper creative generation process
        # For now, we'll just create placeholder assets
        
        # Create sample assets with "Creative not yet implemented" message
        assets.append({
            "id": f"asset-{campaign_id}-headline-{int(time.time())}",
            "type": CreativeAssetType.HEADLINE,
            "content": "Creative asset generation not yet implemented",
            "variations": 1,
            "metadata": {
                "placeholder": True,
                "created_at": datetime.now().isoformat()
            }
        })
        
        # Store the assets
        self.active_projects[campaign_id]["assets"] = assets
        for asset in assets:
            self.asset_library[asset["id"]] = asset
        
        # Update project status
        self.active_projects[campaign_id]["status"] = "completed"
        self.active_projects[campaign_id]["completed_at"] = datetime.now().isoformat()
        
        # Send delivery message if we know the sender
        if sender_id:
            self._deliver_creative_assets(campaign_id, sender_id)
    
    def _deliver_creative_assets(self, campaign_id: str, recipient_id: str) -> None:
        """Deliver creative assets to the recipient.
        
        Args:
            campaign_id: ID of the campaign
            recipient_id: ID of the recipient (usually strategy agent)
        """
        if campaign_id not in self.active_projects:
            logger.warning(f"Cannot deliver assets for unknown campaign: {campaign_id}")
            return
            
        project = self.active_projects[campaign_id]
        assets = project["assets"]
        conversation_id = project["conversation_id"]
        
        # Send message with assets
        self.send_message(
            recipient_id=recipient_id,
            message_type=MessageType.RESPONSE,
            content={
                "campaign_id": campaign_id,
                "assets": assets,
                "message": "Creative assets delivery",
                "status": "completed",
                "delivered_at": datetime.now().isoformat()
            },
            conversation_id=conversation_id,
            priority=MessagePriority.HIGH
        )
        
        # Publish delivery information
        self.publish_to_topic(
            "creative_deliverables",
            {
                "event": "creative_assets_delivered",
                "campaign_id": campaign_id,
                "asset_count": len(assets),
                "asset_types": list(set(asset["type"] for asset in assets)),
                "timestamp": datetime.now().isoformat()
            }
        )
        
        logger.info(f"Delivered {len(assets)} creative assets for campaign {campaign_id}")
    
    def _handle_creative_feedback(self, message: Dict[str, Any]) -> None:
        """Handle feedback on delivered creative assets.
        
        Args:
            message: Message containing feedback
        """
        logger.info(f"Received creative feedback from {message.sender_id}")
        
        # Extract information
        campaign_id = message.content.get("campaign_id")
        feedback = message.content.get("feedback", {})
        
        if campaign_id not in self.active_projects:
            logger.warning(f"Received feedback for unknown campaign: {campaign_id}")
            return
            
        # Store feedback
        self.active_projects[campaign_id]["feedback"].append({
            "sender_id": message.sender_id,
            "feedback": feedback,
            "received_at": datetime.now().isoformat()
        })
        
        # Update project status
        self.active_projects[campaign_id]["status"] = "revision_needed"
        
        # Acknowledge receipt
        self.send_message(
            recipient_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content={
                "success": True,
                "campaign_id": campaign_id,
                "message": "Creative feedback received and being processed",
                "estimated_delivery": (datetime.now() + timedelta(days=1)).isoformat()
            },
            conversation_id=message.conversation_id,
            priority=MessagePriority.MEDIUM
        )
        
        # Start revisions
        # This would be implemented in a full version
        logger.info(f"Revisions for campaign {campaign_id} would start here in a full implementation")
    
    def _register_process_activities(self) -> None:
        """Register process activities that this agent can perform."""
        
        # Register activity for developing creative assets
        self.register_activity_handler(
            "develop_creative_assets",
            self._activity_develop_creative_assets,
            {
                "required_inputs": ["campaign_id", "asset_types"],
                "optional_inputs": ["brief", "audience", "tone"],
                "description": "Develop creative assets for a campaign"
            }
        )
        
        # Other activities would be added in a full implementation
        
        logger.info(f"Registered {len(self._activity_handlers)} process activities")
    
    def _activity_develop_creative_assets(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process activity implementation for developing creative assets.
        
        Args:
            context: Activity context containing inputs
            
        Returns:
            Activity result
        """
        try:
            # Extract inputs
            campaign_id = context.get("campaign_id")
            asset_types = context.get("asset_types", [])
            brief = context.get("brief", {})
            audience = context.get("audience", {})
            tone = context.get("tone", "professional")
            
            # Create placeholder result
            result = {
                "success": True,
                "message": "Creative asset development not fully implemented",
                "assets": []
            }
            
            # In a full implementation, this would generate the requested assets
            
            return result
            
        except Exception as e:
            logger.error(f"Error in develop_creative_assets activity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_message(self, recipient_id: str, message_type: str, content: Dict[str, Any], 
                    conversation_id: Optional[str] = None, priority: MessagePriority = MessagePriority.MEDIUM) -> str:
        """Send a message to another agent.
        
        Args:
            recipient_id: ID of the recipient agent
            message_type: Type of message being sent
            content: Message content
            conversation_id: Optional conversation ID for threading
            priority: Message priority
            
        Returns:
            str: Message ID
        """
        return self.protocol.send_message(
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            conversation_id=conversation_id,
            priority=priority
        )

# Create example function to demonstrate the agent
def create_creative_agent(agent_id: str = "creative-agent") -> CreativeAgent:
    """Create a creative agent with default configuration.
    
    Args:
        agent_id: ID for the agent
        
    Returns:
        CreativeAgent: Initialized creative agent
    """
    # Create communication protocol
    protocol = StandardCommunicationProtocol()
    
    # Create creative agent
    agent = CreativeAgent(agent_id, protocol)
    
    # Initialize the agent
    agent.initialize({
        "name": "Creative Producer Agent",
        "description": "Responsible for developing creative assets for campaigns",
        "enabled": True
    })
    
    return agent