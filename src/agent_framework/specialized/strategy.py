# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file creates a special AI helper that's good at planning advertising campaigns.
# It's like the team captain who thinks about the big picture and helps coordinate
# everyone else's work.

# High School Explanation:
# This module implements the Strategy Agent, which is responsible for campaign planning
# and orchestration within the ad agency. It coordinates the campaign development
# process by integrating with knowledge sources, process frameworks, and other
# specialized agents.

"""
Strategy Agent implementation for campaign planning and orchestration.

The Strategy Agent is responsible for developing campaign strategies, creating
campaign plans, and coordinating the execution of campaigns across other
specialized agents in the advertising agency ecosystem.
"""

import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set

from ..core.base import (
    AbstractOperationalAgent, 
    AbstractCommunicatingAgent,
    AbstractObservableAgent,
    AbstractProcessAwareAgent
)
from ..core.interfaces import AgentExecutionError
from ..communication.protocol import (
    StandardCommunicationProtocol,
    DeliveryStatus,
    MessagePriority
)
from ...process_framework.interface import BaseProcessAwareAgent
from ...tisit.knowledge_graph import KnowledgeGraph
from ...tisit.entity import Entity

logger = logging.getLogger(__name__)

# Define message types specific to the strategy agent
class StrategyMessageType:
    """Message types for strategy agent communication."""
    
    # Campaign planning messages
    CAMPAIGN_REQUEST = "CAMPAIGN_REQUEST"
    CAMPAIGN_PLAN = "CAMPAIGN_PLAN"
    CAMPAIGN_APPROVAL = "CAMPAIGN_APPROVAL"
    CAMPAIGN_REJECTION = "CAMPAIGN_REJECTION"
    
    # Strategy development messages
    STRATEGY_REQUEST = "STRATEGY_REQUEST"
    STRATEGY_PROPOSAL = "STRATEGY_PROPOSAL"
    STRATEGY_FEEDBACK = "STRATEGY_FEEDBACK"
    
    # Coordination messages
    CREATIVE_BRIEF = "CREATIVE_BRIEF"
    AUDIENCE_BRIEF = "AUDIENCE_BRIEF"
    MEDIA_BRIEF = "MEDIA_BRIEF"
    
    # Status messages
    STATUS_UPDATE = "STATUS_UPDATE"
    STATUS_REQUEST = "STATUS_REQUEST"


class StrategyAgent(BaseProcessAwareAgent):
    """
    Agent responsible for campaign planning and strategic coordination.
    
    The Strategy Agent is the central coordinator for campaign development,
    creating campaign strategies, briefing specialized agents, and managing
    the overall campaign execution process.
    """
    
    def __init__(
        self, 
        agent_id: str, 
        protocol: StandardCommunicationProtocol,
        knowledge_graph: Optional[KnowledgeGraph] = None
    ):
        """Initialize the strategy agent.
        
        Args:
            agent_id: Unique identifier for this agent
            protocol: Communication protocol for inter-agent messaging
            knowledge_graph: Optional knowledge graph for domain knowledge
        """
        super().__init__(agent_id, "Strategy Agent")
        self.protocol = protocol
        self.knowledge_graph = knowledge_graph
        
        # Register with communication protocol
        self.protocol.register_agent(self)
        
        # Track active campaigns and their states
        self.active_campaigns: Dict[str, Dict[str, Any]] = {}
        
        # Track specialized agent IDs
        self.creative_agent_id = None
        self.audience_agent_id = None
        self.media_agent_id = None
        self.analytics_agent_id = None
        
        # Register message handlers
        self.register_message_handler(
            StrategyMessageType.CAMPAIGN_REQUEST,
            self._handle_campaign_request
        )
        self.register_message_handler(
            StrategyMessageType.STRATEGY_FEEDBACK,
            self._handle_strategy_feedback
        )
        self.register_message_handler(
            StrategyMessageType.STATUS_REQUEST,
            self._handle_status_request
        )
        
        # Subscribe to relevant topics
        if protocol is not None:
            self.subscribe_to_topic("campaign_updates")
            self.subscribe_to_topic("creative_deliverables")
            self.subscribe_to_topic("audience_insights")
            self.subscribe_to_topic("media_performance")
            
        # Register process activities
        self._register_process_activities()
        
        logger.info(f"Strategy Agent initialized with ID: {agent_id}")
    
    def set_collaborator_agents(
        self,
        creative_id: Optional[str] = None,
        audience_id: Optional[str] = None,
        media_id: Optional[str] = None,
        analytics_id: Optional[str] = None
    ) -> None:
        """Set the IDs of collaborator agents.
        
        Args:
            creative_id: ID of the creative agent
            audience_id: ID of the audience agent
            media_id: ID of the media agent
            analytics_id: ID of the analytics agent
        """
        if creative_id:
            self.creative_agent_id = creative_id
            logger.info(f"Set creative agent ID to {creative_id}")
            
        if audience_id:
            self.audience_agent_id = audience_id
            logger.info(f"Set audience agent ID to {audience_id}")
            
        if media_id:
            self.media_agent_id = media_id
            logger.info(f"Set media agent ID to {media_id}")
            
        if analytics_id:
            self.analytics_agent_id = analytics_id
            logger.info(f"Set analytics agent ID to {analytics_id}")
    
    def create_campaign(self, campaign_details: Dict[str, Any]) -> str:
        """Create a new campaign plan.
        
        Args:
            campaign_details: Dictionary containing campaign information
            
        Returns:
            str: The campaign ID
            
        Raises:
            AgentExecutionError: If campaign creation fails
        """
        try:
            # Start a trace for observability
            if hasattr(self, 'start_trace'):
                self.start_trace("create_campaign", campaign_details)
            
            # Generate campaign ID if not provided
            campaign_id = campaign_details.get("id", f"camp-{str(uuid.uuid4())[:8]}")
            
            # Log the campaign creation
            logger.info(f"Creating new campaign: {campaign_details.get('name')} (ID: {campaign_id})")
            
            # Create conversation ID for tracking all campaign-related messages
            conversation_id = str(uuid.uuid4())
            
            # Store campaign in active campaigns
            self.active_campaigns[campaign_id] = {
                "details": campaign_details,
                "status": "planning",
                "created_at": datetime.now().isoformat(),
                "conversation_id": conversation_id,
                "strategy": None,
                "components": {
                    "creative": {"status": "pending"},
                    "audience": {"status": "pending"},
                    "media": {"status": "pending"}
                },
                "milestones": [],
                "messages": []
            }
            
            # Create campaign strategy
            strategy = self._develop_campaign_strategy(campaign_id, campaign_details)
            self.active_campaigns[campaign_id]["strategy"] = strategy
            
            # Add to knowledge graph if available
            if self.knowledge_graph:
                self._add_campaign_to_knowledge_graph(campaign_id, campaign_details, strategy)
            
            # Record milestone
            self._add_campaign_milestone(
                campaign_id, 
                "Campaign Created", 
                "Campaign initialized with basic details and strategy development"
            )
            
            # If specialized agents are set, begin briefing them
            if any([self.creative_agent_id, self.audience_agent_id, self.media_agent_id]):
                self._send_campaign_briefs(campaign_id)
            
            # For observability
            if hasattr(self, 'add_trace_step'):
                self.add_trace_step("campaign_created", 
                                  campaign_id=campaign_id, 
                                  status=self.active_campaigns[campaign_id]["status"])
                
            if hasattr(self, 'end_trace'):
                self.end_trace({
                    "success": True,
                    "campaign_id": campaign_id,
                    "status": self.active_campaigns[campaign_id]["status"]
                })
            
            return campaign_id
            
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            
            if hasattr(self, 'end_trace'):
                self.end_trace({
                    "success": False,
                    "error": str(e)
                }, "failed")
                
            raise AgentExecutionError(f"Campaign creation failed: {str(e)}")
    
    def get_campaign_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get the current status of a campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Dict: Current campaign status information
            
        Raises:
            ValueError: If campaign ID is not found
        """
        # Check if campaign exists
        if campaign_id not in self.active_campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")
            
        campaign = self.active_campaigns[campaign_id]
        
        # Prepare status report
        status_report = {
            "campaign_id": campaign_id,
            "name": campaign["details"].get("name", "Unnamed Campaign"),
            "status": campaign["status"],
            "created_at": campaign["created_at"],
            "components": {k: v["status"] for k, v in campaign["components"].items()},
            "milestones": campaign["milestones"],
            "strategy_summary": self._get_strategy_summary(campaign["strategy"]) if campaign["strategy"] else None
        }
        
        return status_report
    
    def update_campaign_status(self, campaign_id: str, new_status: str) -> bool:
        """Update the status of a campaign.
        
        Args:
            campaign_id: ID of the campaign
            new_status: New status to set
            
        Returns:
            bool: True if update was successful, False otherwise
            
        Raises:
            ValueError: If campaign ID is not found
        """
        # Check if campaign exists
        if campaign_id not in self.active_campaigns:
            raise ValueError(f"Campaign {campaign_id} not found")
            
        # Update status
        old_status = self.active_campaigns[campaign_id]["status"]
        self.active_campaigns[campaign_id]["status"] = new_status
        
        # Log status change
        logger.info(f"Campaign {campaign_id} status changed from {old_status} to {new_status}")
        
        # Add milestone for significant status changes
        if new_status in ["planning", "developing", "reviewing", "approved", "active", "completed"]:
            self._add_campaign_milestone(
                campaign_id,
                f"Status: {new_status.capitalize()}",
                f"Campaign status changed to {new_status}"
            )
            
            # Publish status update
            self.publish_to_topic(
                "campaign_updates",
                {
                    "event": "status_change",
                    "campaign_id": campaign_id,
                    "old_status": old_status,
                    "new_status": new_status,
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        return True
    
    def _develop_campaign_strategy(self, campaign_id: str, campaign_details: Dict[str, Any]) -> Dict[str, Any]:
        """Develop a strategic plan for the campaign.
        
        Args:
            campaign_id: ID of the campaign
            campaign_details: Campaign details
            
        Returns:
            Dict: Campaign strategy
        """
        logger.info(f"Developing strategy for campaign {campaign_id}")
        
        # Extract key information
        objectives = campaign_details.get("objectives", [])
        target_audience = campaign_details.get("target_audience", {})
        budget = campaign_details.get("budget", 0)
        start_date = campaign_details.get("start_date")
        end_date = campaign_details.get("end_date")
        
        # Calculate campaign duration
        duration_days = 30  # Default to 30 days
        if start_date and end_date:
            try:
                start = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
                end = datetime.fromisoformat(end_date) if isinstance(end_date, str) else end_date
                duration_days = (end - start).days
            except:
                logger.warning("Could not parse campaign dates, using default duration")
        
        # Develop strategy components
        
        # 1. Key messages based on objectives
        key_messages = self._generate_key_messages(objectives, target_audience)
        
        # 2. Budget allocation across channels
        budget_allocation = self._generate_budget_allocation(budget, objectives, target_audience)
        
        # 3. Campaign timeline
        timeline = self._generate_campaign_timeline(duration_days, objectives)
        
        # 4. Success metrics
        success_metrics = self._generate_success_metrics(objectives)
        
        # Assemble strategy
        strategy = {
            "key_messages": key_messages,
            "budget_allocation": budget_allocation,
            "timeline": timeline,
            "success_metrics": success_metrics,
            "creative_approach": self._generate_creative_approach(objectives, target_audience),
            "media_strategy": self._generate_media_strategy(objectives, target_audience, budget),
            "risk_assessment": self._generate_risk_assessment(objectives, budget, duration_days),
            "created_at": datetime.now().isoformat()
        }
        
        # Add a milestone
        self._add_campaign_milestone(
            campaign_id,
            "Strategy Developed",
            "Campaign strategy has been developed and is ready for review"
        )
        
        return strategy
    
    def _generate_key_messages(self, objectives: List[str], target_audience: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate key messages based on campaign objectives and target audience.
        
        Args:
            objectives: Campaign objectives
            target_audience: Target audience information
            
        Returns:
            List of key messages
        """
        messages = []
        
        # Check for brand awareness objective
        if any("brand" in obj.lower() for obj in objectives):
            messages.append({
                "type": "brand",
                "message": "Establish brand credibility and recognition",
                "rationale": "Building brand recognition is essential for long-term growth"
            })
            
        # Check for sales/conversion objective
        if any(keyword in " ".join(objectives).lower() for keyword in ["sale", "conversion", "purchase"]):
            messages.append({
                "type": "conversion",
                "message": "Drive immediate action with compelling offers",
                "rationale": "Direct response messaging to generate sales"
            })
            
        # Check for engagement objective
        if any(keyword in " ".join(objectives).lower() for keyword in ["engage", "interaction"]):
            messages.append({
                "type": "engagement",
                "message": "Create meaningful interactions with the brand",
                "rationale": "Building relationship through engagement increases loyalty"
            })
        
        # Add a general message if none were generated
        if not messages:
            messages.append({
                "type": "general",
                "message": "Communicate product value clearly and concisely",
                "rationale": "General purpose messaging focusing on product benefits"
            })
            
        return messages
    
    def _generate_budget_allocation(self, budget: float, objectives: List[str], target_audience: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate budget allocation across channels.
        
        Args:
            budget: Campaign budget
            objectives: Campaign objectives
            target_audience: Target audience information
            
        Returns:
            List of budget allocations
        """
        allocations = []
        
        # Digital allocation (always present, but varies by objectives)
        digital_percent = 0.5  # Default to 50%
        
        # Adjust based on objectives
        if any("digital" in obj.lower() for obj in objectives):
            digital_percent = 0.7  # Increase for digital-focused campaigns
            
        if any("brand" in obj.lower() for obj in objectives):
            digital_percent = 0.4  # Lower for brand campaigns which might use traditional media
        
        # Calculate digital budget
        digital_budget = budget * digital_percent
        allocations.append({
            "channel": "Digital",
            "percentage": digital_percent * 100,
            "amount": digital_budget,
            "rationale": "Digital channels provide targeting precision and measurable ROI"
        })
        
        # Traditional media allocation
        traditional_percent = 0.3
        traditional_budget = budget * traditional_percent
        allocations.append({
            "channel": "Traditional",
            "percentage": traditional_percent * 100,
            "amount": traditional_budget,
            "rationale": "Traditional media builds broad awareness and reaches offline audiences"
        })
        
        # Production allocation
        production_percent = 0.2
        production_budget = budget * production_percent
        allocations.append({
            "channel": "Production",
            "percentage": production_percent * 100,
            "amount": production_budget,
            "rationale": "Content production including creative development and assets"
        })
        
        return allocations
    
    def _generate_campaign_timeline(self, duration_days: int, objectives: List[str]) -> List[Dict[str, Any]]:
        """Generate a campaign timeline with key phases.
        
        Args:
            duration_days: Campaign duration in days
            objectives: Campaign objectives
            
        Returns:
            List of timeline phases
        """
        timeline = []
        
        # Calculate phase durations based on total campaign length
        prep_days = max(7, int(duration_days * 0.1))
        launch_days = max(3, int(duration_days * 0.1))
        main_days = int(duration_days * 0.7)
        final_days = duration_days - prep_days - launch_days - main_days
        
        # Set up the basis for the timeline with today as start
        today = datetime.now()
        prep_start = today
        prep_end = today + timedelta(days=prep_days)
        launch_start = prep_end
        launch_end = launch_start + timedelta(days=launch_days)
        main_start = launch_end
        main_end = main_start + timedelta(days=main_days)
        final_start = main_end
        final_end = final_start + timedelta(days=final_days)
        
        # Add preparation phase
        timeline.append({
            "phase": "Preparation",
            "start_date": prep_start.isoformat(),
            "end_date": prep_end.isoformat(),
            "duration_days": prep_days,
            "key_activities": [
                "Finalize creative assets",
                "Set up tracking and measurement",
                "Brief all stakeholders",
                "Prepare media placements"
            ]
        })
        
        # Add launch phase
        timeline.append({
            "phase": "Launch",
            "start_date": launch_start.isoformat(),
            "end_date": launch_end.isoformat(),
            "duration_days": launch_days,
            "key_activities": [
                "Initial media rollout",
                "Press and PR activities",
                "Social media announcement",
                "Monitor initial performance"
            ]
        })
        
        # Add main campaign phase
        timeline.append({
            "phase": "Main Campaign",
            "start_date": main_start.isoformat(),
            "end_date": main_end.isoformat(),
            "duration_days": main_days,
            "key_activities": [
                "Full media execution",
                "Ongoing performance optimization",
                "A/B testing of creative variations",
                "Regular performance reporting"
            ]
        })
        
        # Add final phase
        timeline.append({
            "phase": "Finalization",
            "start_date": final_start.isoformat(),
            "end_date": final_end.isoformat(),
            "duration_days": final_days,
            "key_activities": [
                "Final performance push",
                "Data collection for reporting",
                "Begin post-campaign analysis",
                "Preparation for follow-up activities"
            ]
        })
        
        return timeline
    
    def _generate_success_metrics(self, objectives: List[str]) -> List[Dict[str, Any]]:
        """Generate success metrics based on campaign objectives.
        
        Args:
            objectives: Campaign objectives
            
        Returns:
            List of success metrics
        """
        metrics = []
        
        # Add metrics based on objectives
        for objective in objectives:
            objective_lower = objective.lower()
            
            # Brand awareness metrics
            if "brand" in objective_lower or "awareness" in objective_lower:
                metrics.append({
                    "name": "Brand Awareness Lift",
                    "target": "15-20%",
                    "measurement_method": "Pre/post campaign surveys",
                    "priority": "High"
                })
                metrics.append({
                    "name": "Reach",
                    "target": "70% of target audience",
                    "measurement_method": "Media platform analytics",
                    "priority": "Medium"
                })
                
            # Engagement metrics
            if "engagement" in objective_lower or "interaction" in objective_lower:
                metrics.append({
                    "name": "Engagement Rate",
                    "target": "Above industry benchmark by 25%",
                    "measurement_method": "Social and digital platform analytics",
                    "priority": "High"
                })
                metrics.append({
                    "name": "Average Time Spent",
                    "target": "30+ seconds",
                    "measurement_method": "Website/content analytics",
                    "priority": "Medium"
                })
                
            # Conversion metrics
            if "conversion" in objective_lower or "sale" in objective_lower or "revenue" in objective_lower:
                metrics.append({
                    "name": "Conversion Rate",
                    "target": "3-5%",
                    "measurement_method": "Website analytics and tracking",
                    "priority": "High"
                })
                metrics.append({
                    "name": "Cost Per Acquisition",
                    "target": "Below industry average by 20%",
                    "measurement_method": "Campaign performance data",
                    "priority": "High"
                })
                metrics.append({
                    "name": "ROI",
                    "target": "3:1 or better",
                    "measurement_method": "Sales data compared to campaign spend",
                    "priority": "High"
                })
        
        # Always include some standard metrics
        if not any("impression" in m["name"].lower() for m in metrics):
            metrics.append({
                "name": "Impressions",
                "target": "Based on media plan reach goals",
                "measurement_method": "Media platform analytics",
                "priority": "Medium"
            })
            
        if not any("click" in m["name"].lower() for m in metrics):
            metrics.append({
                "name": "Click-Through Rate",
                "target": "Industry benchmark +10%",
                "measurement_method": "Digital platform analytics",
                "priority": "Medium"
            })
        
        return metrics
    
    def _generate_creative_approach(self, objectives: List[str], target_audience: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a creative approach based on objectives and target audience.
        
        Args:
            objectives: Campaign objectives
            target_audience: Target audience information
            
        Returns:
            Creative approach details
        """
        # Default creative approach
        approach = {
            "tone": "Professional and aspirational",
            "style": "Contemporary with branded elements",
            "themes": ["Value proposition", "Product benefits"],
            "visual_elements": ["Product imagery", "Brand colors and typography"],
            "content_strategy": "Focus on clear communication of benefits"
        }
        
        # Adjust based on audience demographics if available
        if isinstance(target_audience, dict):
            age_group = target_audience.get("age_group", "")
            if "18-24" in str(age_group) or "young" in str(age_group).lower():
                approach["tone"] = "Authentic and conversational"
                approach["style"] = "Bold and contemporary"
                approach["themes"].append("Cultural relevance")
                approach["content_strategy"] = "Engaging and shareable content for social platforms"
            
            elif "55+" in str(age_group) or "senior" in str(age_group).lower():
                approach["tone"] = "Trustworthy and straightforward"
                approach["style"] = "Classic and clear"
                approach["themes"].append("Reliability and quality")
                approach["content_strategy"] = "Detailed information with clear value proposition"
        
        # Adjust based on objectives
        if any("brand" in obj.lower() for obj in objectives):
            approach["focus"] = "Brand storytelling"
            approach["themes"].append("Brand values and mission")
        
        elif any("conversion" in obj.lower() or "sale" in obj.lower() for obj in objectives):
            approach["focus"] = "Direct response"
            approach["themes"].append("Limited-time offers")
            approach["content_strategy"] = "Clear calls to action with compelling offers"
            
        return approach
    
    def _generate_media_strategy(self, objectives: List[str], target_audience: Dict[str, Any], budget: float) -> Dict[str, Any]:
        """Generate a media strategy based on objectives, audience and budget.
        
        Args:
            objectives: Campaign objectives
            target_audience: Target audience information
            budget: Campaign budget
            
        Returns:
            Media strategy details
        """
        # Determine budget tier
        budget_tier = "low"
        if budget > 100000:
            budget_tier = "medium"
        if budget > 500000:
            budget_tier = "high"
            
        # Default channels mix
        channels_mix = {
            "digital": {
                "percentage": 60,
                "channels": ["Social media", "Display", "Search"]
            },
            "traditional": {
                "percentage": 30,
                "channels": ["Print", "Radio"]
            },
            "other": {
                "percentage": 10,
                "channels": ["PR", "Content marketing"]
            }
        }
        
        # Adjust based on budget tier
        if budget_tier == "low":
            channels_mix["digital"]["percentage"] = 80
            channels_mix["traditional"]["percentage"] = 10
            channels_mix["other"]["percentage"] = 10
            channels_mix["digital"]["channels"] = ["Social media", "Search"]
            channels_mix["traditional"]["channels"] = ["Local print"]
            
        elif budget_tier == "high":
            channels_mix["digital"]["percentage"] = 50
            channels_mix["traditional"]["percentage"] = 40
            channels_mix["other"]["percentage"] = 10
            channels_mix["digital"]["channels"].append("Video")
            channels_mix["traditional"]["channels"].extend(["TV", "Outdoor"])
        
        # Targeting approach based on available audience data
        targeting_approach = ["Demographics", "Interest-based"]
        if isinstance(target_audience, dict) and "behaviors" in target_audience:
            targeting_approach.append("Behavioral")
            
        if isinstance(target_audience, dict) and "existing_customers" in target_audience:
            targeting_approach.append("CRM-based")
        
        # Assemble media strategy
        media_strategy = {
            "budget_tier": budget_tier,
            "channels_mix": channels_mix,
            "targeting_approach": targeting_approach,
            "frequency": "3-5 exposures per target audience member",
            "pacing": "Even distribution with emphasis on launch period",
            "testing_approach": "A/B testing of creative variations and targeting options"
        }
        
        return media_strategy
    
    def _generate_risk_assessment(self, objectives: List[str], budget: float, duration_days: int) -> List[Dict[str, Any]]:
        """Generate a risk assessment for the campaign.
        
        Args:
            objectives: Campaign objectives
            budget: Campaign budget
            duration_days: Campaign duration in days
            
        Returns:
            List of risk assessments
        """
        risks = []
        
        # Budget-related risk
        if budget < 50000:
            risks.append({
                "type": "budget",
                "description": "Limited budget may restrict reach and frequency",
                "severity": "Medium",
                "mitigation": "Focus on highly targeted channels with lower CPM/CPC"
            })
        
        # Timeline-related risk
        if duration_days < 14:
            risks.append({
                "type": "timeline",
                "description": "Short campaign duration limits optimization opportunities",
                "severity": "Medium",
                "mitigation": "Front-load creative testing before campaign launch"
            })
        
        # Competition risk
        risks.append({
            "type": "competition",
            "description": "Competitor activity may impact campaign performance",
            "severity": "Medium",
            "mitigation": "Monitor competitive activity and be prepared to adjust messaging or media"
        })
        
        # Performance risk
        risks.append({
            "type": "performance",
            "description": "Campaign may not meet all objectives simultaneously",
            "severity": "Medium",
            "mitigation": "Prioritize objectives and optimize toward top priorities"
        })
        
        return risks
    
    def _get_strategy_summary(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of the strategy for reporting.
        
        Args:
            strategy: Full campaign strategy
            
        Returns:
            Strategy summary
        """
        if not strategy:
            return None
            
        return {
            "key_messages": [msg["message"] for msg in strategy.get("key_messages", [])],
            "budget_allocation": {alloc["channel"]: alloc["percentage"] for alloc in strategy.get("budget_allocation", [])},
            "timeline_phases": [phase["phase"] for phase in strategy.get("timeline", [])],
            "primary_metrics": [metric["name"] for metric in strategy.get("success_metrics", [])[:3]],
            "creative_tone": strategy.get("creative_approach", {}).get("tone", ""),
            "primary_channels": strategy.get("media_strategy", {}).get("channels_mix", {}).get("digital", {}).get("channels", [])
        }
    
    def _add_campaign_to_knowledge_graph(self, campaign_id: str, campaign_details: Dict[str, Any], strategy: Dict[str, Any]) -> None:
        """Add campaign information to the knowledge graph.
        
        Args:
            campaign_id: Campaign ID
            campaign_details: Campaign details
            strategy: Campaign strategy
        """
        if not self.knowledge_graph:
            return
            
        try:
            # Create campaign entity
            campaign_entity = Entity(
                entity_id=campaign_id,
                name=campaign_details.get("name", f"Campaign {campaign_id}"),
                description=campaign_details.get("brief", ""),
                entity_type="Campaign"
            )
            
            # Add attributes
            campaign_entity.add_attributes({
                "objectives": campaign_details.get("objectives", []),
                "target_audience": campaign_details.get("target_audience", {}),
                "budget": campaign_details.get("budget", 0),
                "start_date": campaign_details.get("start_date", ""),
                "end_date": campaign_details.get("end_date", ""),
                "status": "planning"
            })
            
            # Add strategy as linked entity
            strategy_entity = Entity(
                entity_id=f"{campaign_id}-strategy",
                name=f"Strategy for {campaign_details.get('name', campaign_id)}",
                description="Campaign strategy",
                entity_type="Strategy"
            )
            
            # Add strategy attributes
            strategy_entity.add_attributes({
                "key_messages": [msg["message"] for msg in strategy.get("key_messages", [])],
                "creative_approach": strategy.get("creative_approach", {}),
                "media_strategy": strategy.get("media_strategy", {})
            })
            
            # Add entities to knowledge graph
            self.knowledge_graph.add_entity(campaign_entity)
            self.knowledge_graph.add_entity(strategy_entity)
            
            # Link entities
            self.knowledge_graph.add_relationship(
                from_entity_id=campaign_id,
                to_entity_id=f"{campaign_id}-strategy",
                relationship_type="has_strategy"
            )
            
            logger.info(f"Added campaign {campaign_id} to knowledge graph")
            
        except Exception as e:
            logger.error(f"Error adding campaign to knowledge graph: {str(e)}")
    
    def _add_campaign_milestone(self, campaign_id: str, title: str, description: str) -> None:
        """Add a milestone to the campaign timeline.
        
        Args:
            campaign_id: Campaign ID
            title: Milestone title
            description: Milestone description
        """
        if campaign_id not in self.active_campaigns:
            logger.warning(f"Cannot add milestone to unknown campaign {campaign_id}")
            return
            
        milestone = {
            "title": title,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        
        self.active_campaigns[campaign_id]["milestones"].append(milestone)
        logger.info(f"Added milestone '{title}' to campaign {campaign_id}")
    
    def _send_campaign_briefs(self, campaign_id: str) -> None:
        """Send briefs to specialized agents for a campaign.
        
        Args:
            campaign_id: Campaign ID
        """
        if campaign_id not in self.active_campaigns:
            logger.warning(f"Cannot send briefs for unknown campaign {campaign_id}")
            return
            
        campaign = self.active_campaigns[campaign_id]
        strategy = campaign["strategy"]
        conversation_id = campaign["conversation_id"]
        
        # Send brief to audience agent if available
        if self.audience_agent_id:
            self._send_audience_brief(campaign_id, self.audience_agent_id, conversation_id)
            
        # Send brief to creative agent if available
        if self.creative_agent_id:
            self._send_creative_brief(campaign_id, self.creative_agent_id, conversation_id)
            
        # Send brief to media agent if available
        if self.media_agent_id:
            self._send_media_brief(campaign_id, self.media_agent_id, conversation_id)
    
    def _send_audience_brief(self, campaign_id: str, audience_agent_id: str, conversation_id: str) -> None:
        """Send audience brief to the audience agent.
        
        Args:
            campaign_id: Campaign ID
            audience_agent_id: Audience agent ID
            conversation_id: Conversation ID for tracking
        """
        campaign = self.active_campaigns[campaign_id]
        strategy = campaign["strategy"]
        
        # Create audience brief
        audience_brief = {
            "campaign_id": campaign_id,
            "campaign_name": campaign["details"].get("name", ""),
            "campaign_objectives": campaign["details"].get("objectives", []),
            "target_audience_description": campaign["details"].get("target_audience", {}),
            "strategy_highlights": {
                "key_messages": [msg["message"] for msg in strategy.get("key_messages", [])],
                "success_metrics": [metric for metric in strategy.get("success_metrics", []) 
                                  if "audience" in metric.get("name", "").lower()]
            }
        }
        
        # Send message to audience agent
        message_id = self.send_message(
            recipient_id=audience_agent_id,
            message_type=StrategyMessageType.AUDIENCE_BRIEF,
            content=audience_brief,
            conversation_id=conversation_id,
            priority=MessagePriority.HIGH
        )
        
        # Update campaign status
        self.active_campaigns[campaign_id]["components"]["audience"]["status"] = "briefed"
        self.active_campaigns[campaign_id]["components"]["audience"]["brief_sent_at"] = datetime.now().isoformat()
        self.active_campaigns[campaign_id]["components"]["audience"]["brief_message_id"] = message_id
        
        # Add milestone
        self._add_campaign_milestone(
            campaign_id,
            "Audience Brief Sent",
            f"Audience analysis brief sent to agent {audience_agent_id}"
        )
        
        logger.info(f"Sent audience brief for campaign {campaign_id} to agent {audience_agent_id}")
    
    def _send_creative_brief(self, campaign_id: str, creative_agent_id: str, conversation_id: str) -> None:
        """Send creative brief to the creative agent.
        
        Args:
            campaign_id: Campaign ID
            creative_agent_id: Creative agent ID
            conversation_id: Conversation ID for tracking
        """
        campaign = self.active_campaigns[campaign_id]
        strategy = campaign["strategy"]
        
        # Create creative brief
        creative_brief = {
            "campaign_id": campaign_id,
            "campaign_name": campaign["details"].get("name", ""),
            "campaign_objectives": campaign["details"].get("objectives", []),
            "target_audience": campaign["details"].get("target_audience", {}),
            "key_messages": strategy.get("key_messages", []),
            "creative_approach": strategy.get("creative_approach", {}),
            "required_assets": campaign["details"].get("required_assets", []),
            "brand_guidelines": campaign["details"].get("brand_guidelines", {})
        }
        
        # Send message to creative agent
        message_id = self.send_message(
            recipient_id=creative_agent_id,
            message_type=StrategyMessageType.CREATIVE_BRIEF,
            content=creative_brief,
            conversation_id=conversation_id,
            priority=MessagePriority.HIGH
        )
        
        # Update campaign status
        self.active_campaigns[campaign_id]["components"]["creative"]["status"] = "briefed"
        self.active_campaigns[campaign_id]["components"]["creative"]["brief_sent_at"] = datetime.now().isoformat()
        self.active_campaigns[campaign_id]["components"]["creative"]["brief_message_id"] = message_id
        
        # Add milestone
        self._add_campaign_milestone(
            campaign_id,
            "Creative Brief Sent",
            f"Creative brief sent to agent {creative_agent_id}"
        )
        
        logger.info(f"Sent creative brief for campaign {campaign_id} to agent {creative_agent_id}")
    
    def _send_media_brief(self, campaign_id: str, media_agent_id: str, conversation_id: str) -> None:
        """Send media brief to the media agent.
        
        Args:
            campaign_id: Campaign ID
            media_agent_id: Media agent ID
            conversation_id: Conversation ID for tracking
        """
        campaign = self.active_campaigns[campaign_id]
        strategy = campaign["strategy"]
        
        # Create media brief
        media_brief = {
            "campaign_id": campaign_id,
            "campaign_name": campaign["details"].get("name", ""),
            "campaign_objectives": campaign["details"].get("objectives", []),
            "target_audience": campaign["details"].get("target_audience", {}),
            "budget": campaign["details"].get("budget", 0),
            "start_date": campaign["details"].get("start_date", ""),
            "end_date": campaign["details"].get("end_date", ""),
            "media_strategy": strategy.get("media_strategy", {}),
            "success_metrics": [metric for metric in strategy.get("success_metrics", [])
                              if any(word in metric.get("name", "").lower() for word in ["impression", "reach", "frequency", "cpm"])]
        }
        
        # Send message to media agent
        message_id = self.send_message(
            recipient_id=media_agent_id,
            message_type=StrategyMessageType.MEDIA_BRIEF,
            content=media_brief,
            conversation_id=conversation_id,
            priority=MessagePriority.HIGH
        )
        
        # Update campaign status
        self.active_campaigns[campaign_id]["components"]["media"]["status"] = "briefed"
        self.active_campaigns[campaign_id]["components"]["media"]["brief_sent_at"] = datetime.now().isoformat()
        self.active_campaigns[campaign_id]["components"]["media"]["brief_message_id"] = message_id
        
        # Add milestone
        self._add_campaign_milestone(
            campaign_id,
            "Media Brief Sent",
            f"Media brief sent to agent {media_agent_id}"
        )
        
        logger.info(f"Sent media brief for campaign {campaign_id} to agent {media_agent_id}")
    
    def _handle_campaign_request(self, message: Dict[str, Any]) -> None:
        """Handle incoming campaign request messages.
        
        Args:
            message: Message dictionary
        """
        logger.info(f"Received campaign request from {message.sender_id}")
        
        try:
            # Extract campaign details from message
            campaign_details = message.content
            
            # Create campaign
            campaign_id = self.create_campaign(campaign_details)
            
            # Send response with campaign ID and initial status
            self.send_message(
                recipient_id=message.sender_id,
                message_type=StrategyMessageType.CAMPAIGN_PLAN,
                content={
                    "campaign_id": campaign_id,
                    "status": self.active_campaigns[campaign_id]["status"],
                    "strategy_summary": self._get_strategy_summary(self.active_campaigns[campaign_id]["strategy"]),
                    "next_steps": "Campaign planning in progress. Specialized agents will be briefed shortly."
                },
                conversation_id=message.conversation_id,
                priority=MessagePriority.HIGH
            )
            
        except Exception as e:
            logger.error(f"Error handling campaign request: {str(e)}")
            
            # Send error response
            self.send_message(
                recipient_id=message.sender_id,
                message_type=MessageType.ERROR,
                content={
                    "error": f"Failed to create campaign: {str(e)}",
                    "status": "failed"
                },
                conversation_id=message.conversation_id,
                priority=MessagePriority.HIGH
            )
    
    def _handle_strategy_feedback(self, message: Dict[str, Any]) -> None:
        """Handle feedback on campaign strategy.
        
        Args:
            message: Message dictionary
        """
        logger.info(f"Received strategy feedback from {message.sender_id}")
        
        # Extract information from message
        campaign_id = message.content.get("campaign_id")
        feedback = message.content.get("feedback", {})
        
        if not campaign_id or campaign_id not in self.active_campaigns:
            logger.warning(f"Received feedback for unknown campaign: {campaign_id}")
            return
            
        # Store feedback in campaign record
        campaign = self.active_campaigns[campaign_id]
        if "feedback" not in campaign:
            campaign["feedback"] = []
            
        campaign["feedback"].append({
            "sender_id": message.sender_id,
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback
        })
        
        # Add milestone
        self._add_campaign_milestone(
            campaign_id,
            "Strategy Feedback Received",
            f"Received feedback on strategy from {message.sender_id}"
        )
        
        # Determine if strategy needs revision
        needs_revision = feedback.get("needs_revision", False)
        
        if needs_revision:
            # Update strategy with revisions
            self._revise_campaign_strategy(campaign_id, feedback)
            
            # Notify sender of revision
            self.send_message(
                recipient_id=message.sender_id,
                message_type=StrategyMessageType.STRATEGY_PROPOSAL,
                content={
                    "campaign_id": campaign_id,
                    "status": "revised",
                    "message": "Strategy has been revised based on feedback",
                    "strategy_summary": self._get_strategy_summary(campaign["strategy"])
                },
                conversation_id=message.conversation_id,
                priority=MessagePriority.HIGH
            )
        else:
            # Acknowledge feedback
            self.send_message(
                recipient_id=message.sender_id,
                message_type=MessageType.RESPONSE,
                content={
                    "campaign_id": campaign_id,
                    "status": "acknowledged",
                    "message": "Thank you for your feedback on the campaign strategy"
                },
                conversation_id=message.conversation_id,
                priority=MessagePriority.MEDIUM
            )
    
    def _revise_campaign_strategy(self, campaign_id: str, feedback: Dict[str, Any]) -> None:
        """Revise campaign strategy based on feedback.
        
        Args:
            campaign_id: Campaign ID
            feedback: Feedback information
        """
        if campaign_id not in self.active_campaigns:
            logger.warning(f"Cannot revise strategy for unknown campaign {campaign_id}")
            return
            
        campaign = self.active_campaigns[campaign_id]
        strategy = campaign["strategy"]
        
        # Apply revisions based on feedback components
        revision_notes = []
        
        # Handle key messages revisions
        if "key_messages" in feedback:
            key_messages_feedback = feedback["key_messages"]
            
            if "add" in key_messages_feedback and key_messages_feedback["add"]:
                for new_message in key_messages_feedback["add"]:
                    strategy["key_messages"].append({
                        "type": new_message.get("type", "additional"),
                        "message": new_message.get("message", ""),
                        "rationale": new_message.get("rationale", "Added based on feedback")
                    })
                revision_notes.append("Added new key messages")
                
            if "remove" in key_messages_feedback and key_messages_feedback["remove"]:
                for remove_idx in sorted(key_messages_feedback["remove"], reverse=True):
                    if 0 <= remove_idx < len(strategy["key_messages"]):
                        strategy["key_messages"].pop(remove_idx)
                revision_notes.append("Removed specified key messages")
                
            if "modify" in key_messages_feedback and key_messages_feedback["modify"]:
                for mod in key_messages_feedback["modify"]:
                    idx = mod.get("index", -1)
                    if 0 <= idx < len(strategy["key_messages"]):
                        if "message" in mod:
                            strategy["key_messages"][idx]["message"] = mod["message"]
                        if "rationale" in mod:
                            strategy["key_messages"][idx]["rationale"] = mod["rationale"]
                revision_notes.append("Modified existing key messages")
        
        # Handle budget allocation revisions
        if "budget_allocation" in feedback:
            budget_feedback = feedback["budget_allocation"]
            
            if "new_allocation" in budget_feedback and budget_feedback["new_allocation"]:
                strategy["budget_allocation"] = budget_feedback["new_allocation"]
                revision_notes.append("Updated budget allocation")
                
            elif "adjustments" in budget_feedback and budget_feedback["adjustments"]:
                for adj in budget_feedback["adjustments"]:
                    channel = adj.get("channel", "")
                    change = adj.get("change", 0)
                    
                    # Find the channel in existing allocations
                    for alloc in strategy["budget_allocation"]:
                        if alloc["channel"].lower() == channel.lower():
                            alloc["percentage"] += change
                            alloc["amount"] = campaign["details"].get("budget", 0) * (alloc["percentage"] / 100)
                
                # Normalize percentages to ensure they sum to 100%
                total_pct = sum(alloc["percentage"] for alloc in strategy["budget_allocation"])
                if total_pct != 100:
                    scale_factor = 100 / total_pct
                    for alloc in strategy["budget_allocation"]:
                        alloc["percentage"] *= scale_factor
                        alloc["amount"] = campaign["details"].get("budget", 0) * (alloc["percentage"] / 100)
                        
                revision_notes.append("Adjusted budget allocation percentages")
                
        # Handle creative approach revisions
        if "creative_approach" in feedback:
            creative_feedback = feedback["creative_approach"]
            
            for key, value in creative_feedback.items():
                if key in strategy["creative_approach"]:
                    strategy["creative_approach"][key] = value
                    
            revision_notes.append("Updated creative approach")
        
        # Handle media strategy revisions
        if "media_strategy" in feedback:
            media_feedback = feedback["media_strategy"]
            
            for key, value in media_feedback.items():
                if key in strategy["media_strategy"]:
                    strategy["media_strategy"][key] = value
                    
            revision_notes.append("Updated media strategy")
        
        # Update the strategy with revision metadata
        strategy["last_revised"] = datetime.now().isoformat()
        strategy["revision_notes"] = revision_notes
        
        # Add milestone
        self._add_campaign_milestone(
            campaign_id,
            "Strategy Revised",
            f"Campaign strategy revised based on feedback: {', '.join(revision_notes)}"
        )
        
        logger.info(f"Revised strategy for campaign {campaign_id}: {', '.join(revision_notes)}")
        
        # Update knowledge graph if available
        if self.knowledge_graph:
            try:
                # Update strategy entity
                strategy_entity_id = f"{campaign_id}-strategy"
                strategy_entity = self.knowledge_graph.get_entity(strategy_entity_id)
                
                if strategy_entity:
                    # Update attributes
                    strategy_entity.add_attributes({
                        "key_messages": [msg["message"] for msg in strategy.get("key_messages", [])],
                        "creative_approach": strategy.get("creative_approach", {}),
                        "media_strategy": strategy.get("media_strategy", {}),
                        "last_revised": strategy["last_revised"],
                        "revision_notes": strategy["revision_notes"]
                    })
                    
                    # Update entity in knowledge graph
                    self.knowledge_graph.update_entity(strategy_entity)
                    
                    logger.info(f"Updated strategy entity {strategy_entity_id} in knowledge graph")
            except Exception as e:
                logger.error(f"Error updating strategy in knowledge graph: {str(e)}")
    
    def _handle_status_request(self, message: Dict[str, Any]) -> None:
        """Handle requests for campaign status updates.
        
        Args:
            message: Message dictionary
        """
        logger.info(f"Received status request from {message.sender_id}")
        
        # Extract campaign ID from message
        campaign_id = message.content.get("campaign_id")
        
        if not campaign_id:
            # Provide summary of all campaigns
            campaigns_summary = [{
                "campaign_id": cid,
                "name": campaign["details"].get("name", ""),
                "status": campaign["status"],
                "components": {k: v["status"] for k, v in campaign["components"].items()}
            } for cid, campaign in self.active_campaigns.items()]
            
            self.send_message(
                recipient_id=message.sender_id,
                message_type=StrategyMessageType.STATUS_UPDATE,
                content={
                    "active_campaigns": len(self.active_campaigns),
                    "campaigns": campaigns_summary
                },
                conversation_id=message.conversation_id,
                priority=MessagePriority.MEDIUM
            )
            return
            
        # Check if campaign exists
        if campaign_id not in self.active_campaigns:
            self.send_message(
                recipient_id=message.sender_id,
                message_type=MessageType.ERROR,
                content={
                    "error": f"Campaign {campaign_id} not found",
                    "campaign_id": campaign_id
                },
                conversation_id=message.conversation_id,
                priority=MessagePriority.MEDIUM
            )
            return
            
        # Get campaign status
        status_report = self.get_campaign_status(campaign_id)
        
        # Send status update
        self.send_message(
            recipient_id=message.sender_id,
            message_type=StrategyMessageType.STATUS_UPDATE,
            content=status_report,
            conversation_id=message.conversation_id,
            priority=MessagePriority.MEDIUM
        )
    
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
        # Create message
        message_id = str(uuid.uuid4())
        
        # Find campaign ID from conversation ID
        campaign_id = None
        for cid, campaign in self.active_campaigns.items():
            if campaign.get("conversation_id") == conversation_id:
                campaign_id = cid
                break
                
        # Track message if associated with a campaign
        if campaign_id:
            self.active_campaigns[campaign_id]["messages"].append({
                "message_id": message_id,
                "timestamp": datetime.now().isoformat(),
                "sender_id": self.agent_id,
                "recipient_id": recipient_id,
                "message_type": message_type,
                "direction": "outgoing"
            })
        
        # Use protocol to send message
        return self.protocol.send_message(
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            conversation_id=conversation_id,
            priority=priority
        )
        
    def receive_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a received message.
        
        Args:
            message: The message to process
            
        Returns:
            Dict: Processing result
        """
        # Track message if associated with a campaign
        campaign_id = None
        conversation_id = message.get("conversation_id")
        
        if conversation_id:
            for cid, campaign in self.active_campaigns.items():
                if campaign.get("conversation_id") == conversation_id:
                    campaign_id = cid
                    break
        
        if campaign_id:
            self.active_campaigns[campaign_id]["messages"].append({
                "message_id": message.get("message_id", str(uuid.uuid4())),
                "timestamp": datetime.now().isoformat(),
                "sender_id": message.get("sender_id"),
                "recipient_id": self.agent_id,
                "message_type": message.get("message_type"),
                "direction": "incoming"
            })
        
        # Process message using handlers
        message_type = message.get("message_type")
        if message_type in self.message_handlers:
            handler = self.message_handlers[message_type]
            try:
                return handler(message)
            except Exception as e:
                logger.error(f"Error handling message {message.get('message_id')}: {str(e)}")
                return {"success": False, "error": str(e)}
        else:
            logger.warning(f"No handler for message type: {message_type}")
            return {"success": False, "message": f"No handler for message type: {message_type}"}
    
    def publish_to_topic(self, topic: str, content: Dict[str, Any], priority: MessagePriority = MessagePriority.MEDIUM) -> Tuple[int, List[str]]:
        """Publish a message to a topic.
        
        Args:
            topic: Topic to publish to
            content: Message content
            priority: Message priority
            
        Returns:
            Tuple[int, List[str]]: Number of subscribers and list of message IDs
        """
        return self.protocol.publish(
            sender_id=self.agent_id,
            topic=topic,
            content=content,
            priority=priority
        )
    
    def _register_process_activities(self) -> None:
        """Register process activities that this agent can perform."""
        
        # Register campaign planning activity
        self.register_activity_handler(
            "plan_advertising_campaign",
            self._activity_plan_campaign,
            {
                "required_inputs": ["campaign_name", "objectives", "target_audience"],
                "optional_inputs": ["budget", "start_date", "end_date", "brand_guidelines"],
                "description": "Plan a comprehensive advertising campaign"
            }
        )
        
        # Register strategy development activity
        self.register_activity_handler(
            "develop_campaign_strategy",
            self._activity_develop_strategy,
            {
                "required_inputs": ["campaign_id"],
                "optional_inputs": ["strategy_focus", "constraints"],
                "description": "Develop a detailed campaign strategy for an existing campaign"
            }
        )
        
        # Register strategy revision activity
        self.register_activity_handler(
            "revise_campaign_strategy",
            self._activity_revise_strategy,
            {
                "required_inputs": ["campaign_id", "feedback"],
                "optional_inputs": ["priority_areas"],
                "description": "Revise a campaign strategy based on feedback"
            }
        )
        
        # Register briefing activity
        self.register_activity_handler(
            "brief_specialized_agents",
            self._activity_brief_agents,
            {
                "required_inputs": ["campaign_id"],
                "optional_inputs": ["agent_types"],
                "description": "Brief specialized agents on a campaign"
            }
        )
        
        # Register campaign status reporting activity
        self.register_activity_handler(
            "generate_campaign_status_report",
            self._activity_generate_status_report,
            {
                "required_inputs": ["campaign_id"],
                "optional_inputs": ["detail_level", "components"],
                "description": "Generate a comprehensive campaign status report"
            }
        )
        
        logger.info(f"Registered {len(self._activity_handlers)} process activities")
    
    def _activity_plan_campaign(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process activity implementation for planning a campaign.
        
        Args:
            context: Activity context containing inputs
            
        Returns:
            Activity result
        """
        try:
            # Extract inputs
            campaign_name = context.get("campaign_name")
            objectives = context.get("objectives", [])
            target_audience = context.get("target_audience", {})
            budget = context.get("budget", 0)
            start_date = context.get("start_date")
            end_date = context.get("end_date")
            brand_guidelines = context.get("brand_guidelines", {})
            
            # Create campaign details
            campaign_details = {
                "name": campaign_name,
                "objectives": objectives,
                "target_audience": target_audience,
                "budget": budget,
                "start_date": start_date,
                "end_date": end_date,
                "brand_guidelines": brand_guidelines
            }
            
            # Create campaign
            campaign_id = self.create_campaign(campaign_details)
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "status": self.active_campaigns[campaign_id]["status"],
                "strategy_summary": self._get_strategy_summary(self.active_campaigns[campaign_id]["strategy"])
            }
            
        except Exception as e:
            logger.error(f"Error in plan_campaign activity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _activity_develop_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process activity implementation for developing a campaign strategy.
        
        Args:
            context: Activity context containing inputs
            
        Returns:
            Activity result
        """
        try:
            # Extract inputs
            campaign_id = context.get("campaign_id")
            strategy_focus = context.get("strategy_focus", [])
            constraints = context.get("constraints", {})
            
            # Check if campaign exists
            if campaign_id not in self.active_campaigns:
                return {
                    "success": False,
                    "error": f"Campaign {campaign_id} not found"
                }
                
            campaign = self.active_campaigns[campaign_id]
            
            # Develop strategy
            strategy = self._develop_campaign_strategy(campaign_id, campaign["details"])
            
            # Update campaign
            self.active_campaigns[campaign_id]["strategy"] = strategy
            
            # Add to knowledge graph if available
            if self.knowledge_graph:
                self._add_campaign_to_knowledge_graph(campaign_id, campaign["details"], strategy)
            
            # Add milestone
            self._add_campaign_milestone(
                campaign_id,
                "Strategy Developed (Process Activity)",
                "Campaign strategy has been developed via process activity"
            )
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "strategy_summary": self._get_strategy_summary(strategy)
            }
            
        except Exception as e:
            logger.error(f"Error in develop_strategy activity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _activity_revise_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process activity implementation for revising a campaign strategy.
        
        Args:
            context: Activity context containing inputs
            
        Returns:
            Activity result
        """
        try:
            # Extract inputs
            campaign_id = context.get("campaign_id")
            feedback = context.get("feedback", {})
            priority_areas = context.get("priority_areas", [])
            
            # Check if campaign exists
            if campaign_id not in self.active_campaigns:
                return {
                    "success": False,
                    "error": f"Campaign {campaign_id} not found"
                }
                
            # Revise strategy
            self._revise_campaign_strategy(campaign_id, feedback)
            
            # Get revised strategy
            strategy = self.active_campaigns[campaign_id]["strategy"]
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "revision_notes": strategy.get("revision_notes", []),
                "strategy_summary": self._get_strategy_summary(strategy)
            }
            
        except Exception as e:
            logger.error(f"Error in revise_strategy activity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _activity_brief_agents(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process activity implementation for briefing specialized agents.
        
        Args:
            context: Activity context containing inputs
            
        Returns:
            Activity result
        """
        try:
            # Extract inputs
            campaign_id = context.get("campaign_id")
            agent_types = context.get("agent_types", ["creative", "audience", "media"])
            
            # Check if campaign exists
            if campaign_id not in self.active_campaigns:
                return {
                    "success": False,
                    "error": f"Campaign {campaign_id} not found"
                }
                
            campaign = self.active_campaigns[campaign_id]
            
            # Track briefed agents
            briefed_agents = []
            
            # Brief creative agent if requested and available
            if "creative" in agent_types and self.creative_agent_id:
                self._send_creative_brief(
                    campaign_id, 
                    self.creative_agent_id, 
                    campaign["conversation_id"]
                )
                briefed_agents.append(f"creative ({self.creative_agent_id})")
                
            # Brief audience agent if requested and available
            if "audience" in agent_types and self.audience_agent_id:
                self._send_audience_brief(
                    campaign_id, 
                    self.audience_agent_id, 
                    campaign["conversation_id"]
                )
                briefed_agents.append(f"audience ({self.audience_agent_id})")
                
            # Brief media agent if requested and available
            if "media" in agent_types and self.media_agent_id:
                self._send_media_brief(
                    campaign_id, 
                    self.media_agent_id, 
                    campaign["conversation_id"]
                )
                briefed_agents.append(f"media ({self.media_agent_id})")
            
            if not briefed_agents:
                return {
                    "success": False,
                    "message": "No agents were briefed. Ensure agent types are valid and agents are available."
                }
                
            return {
                "success": True,
                "campaign_id": campaign_id,
                "briefed_agents": briefed_agents,
                "message": f"Successfully briefed {len(briefed_agents)} agent(s)"
            }
            
        except Exception as e:
            logger.error(f"Error in brief_agents activity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _activity_generate_status_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process activity implementation for generating a campaign status report.
        
        Args:
            context: Activity context containing inputs
            
        Returns:
            Activity result
        """
        try:
            # Extract inputs
            campaign_id = context.get("campaign_id")
            detail_level = context.get("detail_level", "standard")  # standard, detailed, summary
            components = context.get("components", ["all"])
            
            # Check if campaign exists
            if campaign_id not in self.active_campaigns:
                return {
                    "success": False,
                    "error": f"Campaign {campaign_id} not found"
                }
                
            # Generate status report
            status_report = self.get_campaign_status(campaign_id)
            
            # Add additional information for detailed reports
            if detail_level == "detailed":
                campaign = self.active_campaigns[campaign_id]
                
                # Add detailed strategy information
                if "all" in components or "strategy" in components:
                    status_report["detailed_strategy"] = campaign["strategy"]
                
                # Add message history
                if "all" in components or "messages" in components:
                    status_report["recent_messages"] = campaign["messages"][-10:] if campaign["messages"] else []
                
                # Add all milestones
                status_report["all_milestones"] = campaign["milestones"]
            
            # Remove detail for summary reports
            elif detail_level == "summary":
                # Keep only essential information
                summary_report = {
                    "campaign_id": status_report["campaign_id"],
                    "name": status_report["name"],
                    "status": status_report["status"],
                    "components": status_report["components"],
                    "recent_milestone": status_report["milestones"][-1] if status_report["milestones"] else None
                }
                status_report = summary_report
            
            return {
                "success": True,
                "report": status_report
            }
            
        except Exception as e:
            logger.error(f"Error in generate_status_report activity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Create example function to demonstrate the agent
def create_strategy_agent(agent_id: str = "strategy-agent") -> StrategyAgent:
    """Create a strategy agent with default configuration.
    
    Args:
        agent_id: ID for the agent
        
    Returns:
        StrategyAgent: Initialized strategy agent
    """
    # Create communication protocol
    protocol = StandardCommunicationProtocol()
    
    # Create knowledge graph if available
    knowledge_graph = None
    try:
        from ...tisit.knowledge_graph import KnowledgeGraph
        knowledge_graph = KnowledgeGraph()
    except ImportError:
        logger.warning("TISIT knowledge graph module not available")
    
    # Create strategy agent
    agent = StrategyAgent(agent_id, protocol, knowledge_graph)
    
    # Initialize the agent
    agent.initialize({
        "name": "Campaign Strategy Agent",
        "description": "Responsible for campaign planning and coordination",
        "enabled": True
    })
    
    return agent

# Example usage
def run_strategy_example():
    """Run an example of the strategy agent functionality."""
    # Create strategy agent
    strategy_agent = create_strategy_agent()
    
    # Create other agents
    from ..communication.protocol import CommunicatingAgentImpl
    
    creative_agent = CommunicatingAgentImpl("creative-agent", "Creative Agent", strategy_agent.protocol)
    audience_agent = CommunicatingAgentImpl("audience-agent", "Audience Agent", strategy_agent.protocol)
    media_agent = CommunicatingAgentImpl("media-agent", "Media Agent", strategy_agent.protocol)
    
    # Set up collaborators
    strategy_agent.set_collaborator_agents(
        creative_id=creative_agent.id,
        audience_id=audience_agent.id,
        media_id=media_agent.id
    )
    
    # Create test campaign
    campaign_details = {
        "name": "Summer Product Launch 2025",
        "objectives": [
            "Increase brand awareness",
            "Drive online sales",
            "Generate product trial"
        ],
        "target_audience": {
            "age_group": "25-45",
            "interests": ["outdoor activities", "technology", "sustainability"],
            "geography": "National"
        },
        "budget": 250000,
        "start_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=90)).isoformat(),
        "brand_guidelines": {
            "tone": "Professional, innovative, and approachable",
            "colors": ["#1A5F7A", "#FFC107", "#FFFFFF"],
            "logo_usage": "Standard logo placement required on all assets"
        }
    }
    
    # Create campaign
    campaign_id = strategy_agent.create_campaign(campaign_details)
    
    # Process messages to ensure delivery
    strategy_agent.protocol.process_message_queue()
    
    # Get campaign status
    status = strategy_agent.get_campaign_status(campaign_id)
    
    return {
        "strategy_agent": strategy_agent,
        "creative_agent": creative_agent,
        "audience_agent": audience_agent,
        "media_agent": media_agent,
        "campaign_id": campaign_id,
        "status": status
    }

if __name__ == "__main__":
    run_strategy_example()