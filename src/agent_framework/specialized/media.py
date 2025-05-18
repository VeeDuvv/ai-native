# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file is like a party planner for advertisements. It decides which TV channels,
# websites, or apps are best to show your ads, and how much money to spend on each one.

# High School Explanation:
# This module implements a Media Planning Agent that optimizes advertising channel
# selection and budget allocation. It analyzes audience data, channel performance,
# and campaign objectives to create effective media distribution plans that maximize
# reach and engagement within budget constraints.

import logging
import json
from typing import Dict, List, Any, Optional
import threading
import time

from src.agent_framework.core.base import BaseProcessAwareAgent
from src.agent_framework.core.message import Message, MessageType
from src.agent_framework.core.process import ProcessActivity, ProcessContext
from src.agent_framework.communication.protocol import StandardCommunicationProtocol, DeliveryStatus

logger = logging.getLogger(__name__)

class MediaChannel:
    """Represents an advertising channel with performance metrics."""
    
    def __init__(self, 
                 name: str, 
                 channel_type: str,
                 cpm: float,  # Cost per mille (thousand impressions)
                 average_ctr: float,  # Average click-through rate
                 audience_reach: int,  # Estimated audience reach
                 targeting_options: List[str]):
        self.name = name
        self.channel_type = channel_type  # digital, tv, print, outdoor, etc.
        self.cpm = cpm
        self.average_ctr = average_ctr
        self.audience_reach = audience_reach
        self.targeting_options = targeting_options
        
    def to_dict(self) -> Dict:
        """Convert channel to dictionary representation."""
        return {
            "name": self.name,
            "channel_type": self.channel_type,
            "cpm": self.cpm,
            "average_ctr": self.average_ctr,
            "audience_reach": self.audience_reach,
            "targeting_options": self.targeting_options
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'MediaChannel':
        """Create a MediaChannel instance from dictionary data."""
        return cls(
            name=data["name"],
            channel_type=data["channel_type"],
            cpm=data["cpm"],
            average_ctr=data["average_ctr"],
            audience_reach=data["audience_reach"],
            targeting_options=data["targeting_options"]
        )


class MediaPlan:
    """Represents a complete media plan for a campaign."""
    
    def __init__(self, 
                 campaign_id: str,
                 total_budget: float,
                 start_date: str,
                 end_date: str,
                 primary_objective: str,
                 secondary_objective: Optional[str] = None):
        self.campaign_id = campaign_id
        self.total_budget = total_budget
        self.start_date = start_date
        self.end_date = end_date
        self.primary_objective = primary_objective  # awareness, consideration, conversion
        self.secondary_objective = secondary_objective
        self.channel_allocations: Dict[str, Dict] = {}  # Channel name -> allocation details
        
    def add_channel_allocation(self, 
                              channel: MediaChannel,
                              budget_percentage: float,
                              expected_impressions: int,
                              expected_engagements: int,
                              flight_dates: Dict[str, str],
                              targeting_parameters: Dict[str, Any]):
        """Add a channel allocation to the media plan."""
        self.channel_allocations[channel.name] = {
            "channel": channel.to_dict(),
            "budget_percentage": budget_percentage,
            "budget_amount": self.total_budget * (budget_percentage / 100),
            "expected_impressions": expected_impressions,
            "expected_engagements": expected_engagements,
            "flight_dates": flight_dates,
            "targeting_parameters": targeting_parameters
        }
        
    def get_total_allocated_percentage(self) -> float:
        """Get the total percentage of budget allocated across all channels."""
        return sum(allocation["budget_percentage"] for allocation in self.channel_allocations.values())
    
    def to_dict(self) -> Dict:
        """Convert media plan to dictionary representation."""
        return {
            "campaign_id": self.campaign_id,
            "total_budget": self.total_budget,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "primary_objective": self.primary_objective,
            "secondary_objective": self.secondary_objective,
            "channel_allocations": self.channel_allocations
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'MediaPlan':
        """Create a MediaPlan instance from dictionary data."""
        plan = cls(
            campaign_id=data["campaign_id"],
            total_budget=data["total_budget"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            primary_objective=data["primary_objective"],
            secondary_objective=data.get("secondary_objective")
        )
        
        for channel_name, allocation in data.get("channel_allocations", {}).items():
            channel = MediaChannel.from_dict(allocation["channel"])
            plan.channel_allocations[channel_name] = allocation
            
        return plan


class MediaPlanningAgent(BaseProcessAwareAgent):
    """Agent responsible for optimizing media channel selection and budget allocation."""
    
    def __init__(self, agent_id: str = "media_agent", **kwargs):
        super().__init__(agent_id=agent_id, **kwargs)
        self.communication_protocol = StandardCommunicationProtocol()
        self.active_plans: Dict[str, MediaPlan] = {}  # campaign_id -> MediaPlan
        self.available_channels: Dict[str, MediaChannel] = self._initialize_available_channels()
        
        # Register message handlers
        self.register_message_handler("MEDIA_BRIEF", self._handle_media_brief)
        self.register_message_handler("MEDIA_PLAN_REQUEST", self._handle_media_plan_request)
        self.register_message_handler("UPDATE_MEDIA_PLAN", self._handle_update_media_plan)
        
        # Register process activities
        self.register_activity("develop_media_plan", self._activity_develop_media_plan)
        self.register_activity("optimize_channel_mix", self._activity_optimize_channel_mix)
        self.register_activity("adjust_media_plan", self._activity_adjust_media_plan)
        
    def _initialize_available_channels(self) -> Dict[str, MediaChannel]:
        """Initialize a set of available media channels with default values.
        
        In a production system, this would likely pull from a database or API.
        """
        channels = {}
        
        # Digital channels
        channels["search_ads"] = MediaChannel(
            name="search_ads",
            channel_type="digital",
            cpm=2.5,
            average_ctr=0.0175,
            audience_reach=1000000,
            targeting_options=["keyword", "geography", "device", "demographics"]
        )
        
        channels["social_media"] = MediaChannel(
            name="social_media",
            channel_type="digital",
            cpm=7.0,
            average_ctr=0.011,
            audience_reach=2500000,
            targeting_options=["demographics", "interests", "behaviors", "lookalike"]
        )
        
        channels["display_ads"] = MediaChannel(
            name="display_ads",
            channel_type="digital",
            cpm=3.8,
            average_ctr=0.005,
            audience_reach=3000000,
            targeting_options=["contextual", "demographics", "retargeting"]
        )
        
        channels["video_ads"] = MediaChannel(
            name="video_ads",
            channel_type="digital",
            cpm=12.5,
            average_ctr=0.018,
            audience_reach=1800000,
            targeting_options=["demographics", "interests", "placement", "topic"]
        )
        
        # Traditional channels
        channels["tv"] = MediaChannel(
            name="tv",
            channel_type="traditional",
            cpm=35.0,
            average_ctr=0.0,  # Not applicable for TV
            audience_reach=5000000,
            targeting_options=["program", "daypart", "network"]
        )
        
        channels["radio"] = MediaChannel(
            name="radio",
            channel_type="traditional",
            cpm=15.0,
            average_ctr=0.0,  # Not applicable for radio
            audience_reach=1200000,
            targeting_options=["station", "daypart", "program"]
        )
        
        channels["print"] = MediaChannel(
            name="print",
            channel_type="traditional",
            cpm=22.0,
            average_ctr=0.0,  # Not applicable for print
            audience_reach=800000,
            targeting_options=["publication", "section", "ad size"]
        )
        
        channels["outdoor"] = MediaChannel(
            name="outdoor",
            channel_type="traditional",
            cpm=5.0,
            average_ctr=0.0,  # Not applicable for outdoor
            audience_reach=1500000,
            targeting_options=["location", "format", "duration"]
        )
        
        return channels
    
    def _handle_media_brief(self, message: Message) -> None:
        """Handle incoming media brief from a strategy agent."""
        logger.info(f"Received media brief for campaign {message.content.get('campaign_id')}")
        
        try:
            campaign_id = message.content.get("campaign_id")
            if not campaign_id:
                self._send_error_response(message, "Missing campaign_id in media brief")
                return
                
            # Create a media plan based on the brief
            media_plan = self._create_media_plan(message.content)
            self.active_plans[campaign_id] = media_plan
            
            # Send a delivery confirmation
            self.communication_protocol.send_delivery_confirmation(
                message_id=message.message_id,
                status=DeliveryStatus.PROCESSED,
                agent_id=self.agent_id
            )
            
            # Send media plan to the strategy agent
            response = Message(
                message_type=MessageType.RESPONSE,
                sender=self.agent_id,
                recipient=message.sender,
                content={
                    "message_type": "MEDIA_PLAN",
                    "campaign_id": campaign_id,
                    "media_plan": media_plan.to_dict()
                }
            )
            
            self.communication_protocol.send_message(response)
            logger.info(f"Sent media plan for campaign {campaign_id} to {message.sender}")
            
        except Exception as e:
            logger.error(f"Error processing media brief: {str(e)}")
            self._send_error_response(message, f"Error processing media brief: {str(e)}")
    
    def _handle_media_plan_request(self, message: Message) -> None:
        """Handle request for an existing media plan."""
        campaign_id = message.content.get("campaign_id")
        if not campaign_id:
            self._send_error_response(message, "Missing campaign_id in media plan request")
            return
            
        if campaign_id not in self.active_plans:
            self._send_error_response(message, f"No media plan found for campaign {campaign_id}")
            return
            
        media_plan = self.active_plans[campaign_id]
        
        # Send the media plan
        response = Message(
            message_type=MessageType.RESPONSE,
            sender=self.agent_id,
            recipient=message.sender,
            content={
                "message_type": "MEDIA_PLAN",
                "campaign_id": campaign_id,
                "media_plan": media_plan.to_dict()
            }
        )
        
        self.communication_protocol.send_message(response)
        logger.info(f"Sent requested media plan for campaign {campaign_id} to {message.sender}")
    
    def _handle_update_media_plan(self, message: Message) -> None:
        """Handle request to update an existing media plan."""
        campaign_id = message.content.get("campaign_id")
        if not campaign_id:
            self._send_error_response(message, "Missing campaign_id in update request")
            return
            
        if campaign_id not in self.active_plans:
            self._send_error_response(message, f"No media plan found for campaign {campaign_id}")
            return
        
        update_type = message.content.get("update_type")
        update_data = message.content.get("update_data", {})
        
        try:
            if update_type == "budget":
                self._update_plan_budget(campaign_id, update_data)
            elif update_type == "timeline":
                self._update_plan_timeline(campaign_id, update_data)
            elif update_type == "channel_mix":
                self._update_channel_mix(campaign_id, update_data)
            else:
                self._send_error_response(message, f"Unknown update type: {update_type}")
                return
                
            # Send updated plan
            media_plan = self.active_plans[campaign_id]
            response = Message(
                message_type=MessageType.RESPONSE,
                sender=self.agent_id,
                recipient=message.sender,
                content={
                    "message_type": "UPDATED_MEDIA_PLAN",
                    "campaign_id": campaign_id,
                    "media_plan": media_plan.to_dict()
                }
            )
            
            self.communication_protocol.send_message(response)
            logger.info(f"Sent updated media plan for campaign {campaign_id} to {message.sender}")
            
        except Exception as e:
            logger.error(f"Error updating media plan: {str(e)}")
            self._send_error_response(message, f"Error updating media plan: {str(e)}")
    
    def _create_media_plan(self, brief_data: Dict) -> MediaPlan:
        """Create a new media plan based on campaign brief data."""
        campaign_id = brief_data["campaign_id"]
        total_budget = brief_data.get("media_budget", 0)
        start_date = brief_data.get("start_date", "")
        end_date = brief_data.get("end_date", "")
        primary_objective = brief_data.get("primary_objective", "awareness")
        secondary_objective = brief_data.get("secondary_objective")
        target_audience = brief_data.get("target_audience", {})
        
        # Create the base media plan
        media_plan = MediaPlan(
            campaign_id=campaign_id,
            total_budget=total_budget,
            start_date=start_date,
            end_date=end_date,
            primary_objective=primary_objective,
            secondary_objective=secondary_objective
        )
        
        # Allocate budget based on campaign objective
        if primary_objective == "awareness":
            self._allocate_for_awareness(media_plan, target_audience)
        elif primary_objective == "consideration":
            self._allocate_for_consideration(media_plan, target_audience)
        elif primary_objective == "conversion":
            self._allocate_for_conversion(media_plan, target_audience)
        else:
            # Default to balanced allocation
            self._allocate_balanced(media_plan, target_audience)
            
        return media_plan
    
    def _allocate_for_awareness(self, media_plan: MediaPlan, target_audience: Dict) -> None:
        """Allocate budget optimized for awareness objectives."""
        # For awareness, prioritize reach and frequency over direct response
        allocations = {
            "video_ads": 30,     # Video has high impact for awareness
            "tv": 25,            # TV remains strong for mass awareness
            "social_media": 20,  # Social for younger audiences
            "outdoor": 15,       # Outdoor for general awareness
            "display_ads": 10    # Display for additional impressions
        }
        
        # Adjust based on audience demographics
        age_group = target_audience.get("age_range", "18-34")
        if "18-34" in age_group:
            # Younger audience - increase digital, decrease traditional
            allocations["social_media"] += 10
            allocations["video_ads"] += 5
            allocations["tv"] -= 10
            allocations["outdoor"] -= 5
        elif "55+" in age_group:
            # Older audience - increase traditional, decrease digital
            allocations["tv"] += 10
            allocations["print"] = 10  # Add print
            allocations["social_media"] -= 10
            allocations["video_ads"] -= 5
            allocations["outdoor"] -= 5
            
        self._apply_allocations(media_plan, allocations, target_audience)
    
    def _allocate_for_consideration(self, media_plan: MediaPlan, target_audience: Dict) -> None:
        """Allocate budget optimized for consideration objectives."""
        # For consideration, balance awareness with engagement
        allocations = {
            "social_media": 30,  # Social for engagement and content
            "video_ads": 25,     # Video for storytelling
            "display_ads": 15,   # Display for retargeting
            "search_ads": 15,    # Search for active researchers
            "tv": 15             # TV for credibility and reach
        }
        
        # Adjust based on industry/vertical
        industry = target_audience.get("industry", "").lower()
        if "technology" in industry or "software" in industry:
            # Tech products - more digital
            allocations["search_ads"] += 10
            allocations["display_ads"] += 5
            allocations["tv"] -= 15
        elif "luxury" in industry or "fashion" in industry:
            # Luxury products - more premium placements
            allocations["print"] = 15  # Add print
            allocations["video_ads"] += 5
            allocations["search_ads"] -= 10
            allocations["display_ads"] -= 10
            
        self._apply_allocations(media_plan, allocations, target_audience)
    
    def _allocate_for_conversion(self, media_plan: MediaPlan, target_audience: Dict) -> None:
        """Allocate budget optimized for conversion objectives."""
        # For conversion, prioritize direct response channels
        allocations = {
            "search_ads": 35,    # Search for high intent
            "display_ads": 25,   # Display for retargeting
            "social_media": 25,  # Social for targeted conversions
            "video_ads": 15      # Video for consideration to conversion
        }
        
        # Adjust based on product price point
        price_point = target_audience.get("price_point", "").lower()
        if "high" in price_point:
            # Higher consideration products need more touchpoints
            allocations["video_ads"] += 10
            allocations["search_ads"] -= 10
        elif "low" in price_point:
            # Low price point products need direct response
            allocations["search_ads"] += 5
            allocations["display_ads"] += 5
            allocations["video_ads"] -= 10
            
        self._apply_allocations(media_plan, allocations, target_audience)
    
    def _allocate_balanced(self, media_plan: MediaPlan, target_audience: Dict) -> None:
        """Create a balanced allocation across channels."""
        # Balanced approach for general campaigns
        allocations = {
            "social_media": 25,
            "search_ads": 20,
            "display_ads": 15,
            "video_ads": 15,
            "tv": 15,
            "radio": 5,
            "outdoor": 5
        }
        
        self._apply_allocations(media_plan, allocations, target_audience)
    
    def _apply_allocations(self, media_plan: MediaPlan, allocations: Dict[str, float], 
                          target_audience: Dict) -> None:
        """Apply the channel allocations to the media plan."""
        for channel_name, percentage in allocations.items():
            if channel_name not in self.available_channels:
                logger.warning(f"Channel {channel_name} not found in available channels")
                continue
                
            channel = self.available_channels[channel_name]
            budget_amount = media_plan.total_budget * (percentage / 100)
            
            # Calculate expected performance
            if channel.cpm > 0:
                expected_impressions = int((budget_amount / channel.cpm) * 1000)
            else:
                expected_impressions = 0
                
            expected_engagements = int(expected_impressions * channel.average_ctr)
            
            # Create targeting parameters based on audience
            targeting_parameters = self._create_targeting_parameters(channel, target_audience)
            
            # Set flight dates (default to campaign dates)
            flight_dates = {
                "start_date": media_plan.start_date,
                "end_date": media_plan.end_date
            }
            
            # Add the channel allocation
            media_plan.add_channel_allocation(
                channel=channel,
                budget_percentage=percentage,
                expected_impressions=expected_impressions,
                expected_engagements=expected_engagements,
                flight_dates=flight_dates,
                targeting_parameters=targeting_parameters
            )
    
    def _create_targeting_parameters(self, channel: MediaChannel, target_audience: Dict) -> Dict:
        """Create channel-specific targeting parameters based on target audience."""
        targeting = {}
        
        # Apply relevant targeting based on channel options
        if "demographics" in channel.targeting_options:
            targeting["demographics"] = {
                "age_range": target_audience.get("age_range", "18-54"),
                "gender": target_audience.get("gender", "all"),
                "income": target_audience.get("income", "all")
            }
            
        if "geography" in channel.targeting_options:
            targeting["geography"] = {
                "countries": target_audience.get("countries", ["US"]),
                "regions": target_audience.get("regions", []),
                "cities": target_audience.get("cities", [])
            }
            
        if "interests" in channel.targeting_options:
            targeting["interests"] = target_audience.get("interests", [])
            
        if "behaviors" in channel.targeting_options:
            targeting["behaviors"] = target_audience.get("behaviors", [])
            
        if "keyword" in channel.targeting_options:
            targeting["keywords"] = target_audience.get("keywords", [])
            
        # Add channel-specific targeting
        if channel.name == "tv":
            targeting["programs"] = target_audience.get("tv_programs", [])
            targeting["dayparts"] = target_audience.get("tv_dayparts", ["prime"])
            
        elif channel.name == "radio":
            targeting["stations"] = target_audience.get("radio_stations", [])
            targeting["dayparts"] = target_audience.get("radio_dayparts", ["morning", "evening"])
            
        return targeting
    
    def _update_plan_budget(self, campaign_id: str, update_data: Dict) -> None:
        """Update the budget for an existing media plan."""
        media_plan = self.active_plans[campaign_id]
        new_budget = update_data.get("new_budget")
        
        if not new_budget:
            raise ValueError("Missing new_budget in update data")
            
        # Calculate budget change ratio
        budget_ratio = new_budget / media_plan.total_budget
        
        # Update the plan total budget
        media_plan.total_budget = new_budget
        
        # Update each channel allocation proportionally
        for channel_name, allocation in media_plan.channel_allocations.items():
            # Update budget amount while maintaining percentage
            allocation["budget_amount"] = allocation["budget_amount"] * budget_ratio
            
            # Recalculate expected performance
            channel = self.available_channels.get(channel_name)
            if channel and channel.cpm > 0:
                allocation["expected_impressions"] = int((allocation["budget_amount"] / channel.cpm) * 1000)
                allocation["expected_engagements"] = int(allocation["expected_impressions"] * channel.average_ctr)
    
    def _update_plan_timeline(self, campaign_id: str, update_data: Dict) -> None:
        """Update the timeline for an existing media plan."""
        media_plan = self.active_plans[campaign_id]
        new_start_date = update_data.get("start_date")
        new_end_date = update_data.get("end_date")
        
        if new_start_date:
            media_plan.start_date = new_start_date
            
        if new_end_date:
            media_plan.end_date = new_end_date
            
        # Update flight dates for all channels
        for allocation in media_plan.channel_allocations.values():
            if new_start_date:
                allocation["flight_dates"]["start_date"] = new_start_date
            if new_end_date:
                allocation["flight_dates"]["end_date"] = new_end_date
    
    def _update_channel_mix(self, campaign_id: str, update_data: Dict) -> None:
        """Update the channel mix for an existing media plan."""
        media_plan = self.active_plans[campaign_id]
        new_allocations = update_data.get("channel_allocations", {})
        
        if not new_allocations:
            raise ValueError("Missing channel_allocations in update data")
            
        # Validate that percentages sum to 100
        total_percentage = sum(alloc.get("percentage", 0) for alloc in new_allocations.values())
        if abs(total_percentage - 100) > 0.1:  # Allow small rounding errors
            raise ValueError(f"Channel allocation percentages must sum to 100%. Got {total_percentage}%")
        
        # First remove any channels that are no longer in the mix
        current_channels = set(media_plan.channel_allocations.keys())
        new_channels = set(new_allocations.keys())
        
        for removed_channel in current_channels - new_channels:
            del media_plan.channel_allocations[removed_channel]
            
        # Next update or add channels
        for channel_name, alloc_data in new_allocations.items():
            percentage = alloc_data.get("percentage", 0)
            budget_amount = media_plan.total_budget * (percentage / 100)
            
            if channel_name in self.available_channels:
                channel = self.available_channels[channel_name]
                
                # Calculate expected performance
                if channel.cpm > 0:
                    expected_impressions = int((budget_amount / channel.cpm) * 1000)
                else:
                    expected_impressions = 0
                    
                expected_engagements = int(expected_impressions * channel.average_ctr)
                
                # Get targeting parameters
                targeting_parameters = alloc_data.get("targeting_parameters", {})
                if not targeting_parameters and channel_name in media_plan.channel_allocations:
                    # Keep existing targeting if not provided
                    targeting_parameters = media_plan.channel_allocations[channel_name].get("targeting_parameters", {})
                
                # Get flight dates
                flight_dates = alloc_data.get("flight_dates", {})
                if not flight_dates:
                    # Default to campaign dates
                    flight_dates = {
                        "start_date": media_plan.start_date,
                        "end_date": media_plan.end_date
                    }
                
                # Update or add the channel allocation
                if channel_name in media_plan.channel_allocations:
                    # Update existing
                    media_plan.channel_allocations[channel_name].update({
                        "budget_percentage": percentage,
                        "budget_amount": budget_amount,
                        "expected_impressions": expected_impressions,
                        "expected_engagements": expected_engagements,
                        "flight_dates": flight_dates,
                        "targeting_parameters": targeting_parameters
                    })
                else:
                    # Add new allocation
                    media_plan.channel_allocations[channel_name] = {
                        "channel": channel.to_dict(),
                        "budget_percentage": percentage,
                        "budget_amount": budget_amount,
                        "expected_impressions": expected_impressions,
                        "expected_engagements": expected_engagements,
                        "flight_dates": flight_dates,
                        "targeting_parameters": targeting_parameters
                    }
    
    def _send_error_response(self, original_message: Message, error_text: str) -> None:
        """Send an error response for a message."""
        response = Message(
            message_type=MessageType.ERROR,
            sender=self.agent_id,
            recipient=original_message.sender,
            content={
                "error": error_text,
                "original_message_id": original_message.message_id
            }
        )
        
        self.communication_protocol.send_message(response)
        logger.error(f"Sent error response to {original_message.sender}: {error_text}")
        
        # Also send a delivery confirmation if needed
        self.communication_protocol.send_delivery_confirmation(
            message_id=original_message.message_id,
            status=DeliveryStatus.FAILED,
            agent_id=self.agent_id,
            details=error_text
        )
    
    def _activity_develop_media_plan(self, context: ProcessContext) -> Dict:
        """Process activity to develop a media plan."""
        campaign_id = context.get_parameter("campaign_id")
        if not campaign_id:
            raise ValueError("Missing campaign_id parameter")
            
        campaign_data = context.get_parameter("campaign_data", {})
        if not campaign_data:
            raise ValueError("Missing campaign_data parameter")
            
        # Create a media plan based on the campaign data
        media_plan = self._create_media_plan(campaign_data)
        self.active_plans[campaign_id] = media_plan
        
        # Return the media plan
        return {
            "media_plan": media_plan.to_dict(),
            "campaign_id": campaign_id,
            "status": "completed"
        }
    
    def _activity_optimize_channel_mix(self, context: ProcessContext) -> Dict:
        """Process activity to optimize the channel mix for an existing plan."""
        campaign_id = context.get_parameter("campaign_id")
        if not campaign_id:
            raise ValueError("Missing campaign_id parameter")
            
        if campaign_id not in self.active_plans:
            raise ValueError(f"No media plan found for campaign {campaign_id}")
            
        performance_data = context.get_parameter("performance_data", {})
        optimization_goal = context.get_parameter("optimization_goal", "balanced")
        
        # Optimize the channel mix based on performance data
        media_plan = self.active_plans[campaign_id]
        
        # Implement optimization logic (simplified for this example)
        if optimization_goal == "maximize_reach":
            self._optimize_for_reach(media_plan, performance_data)
        elif optimization_goal == "maximize_engagement":
            self._optimize_for_engagement(media_plan, performance_data)
        elif optimization_goal == "maximize_conversions":
            self._optimize_for_conversions(media_plan, performance_data)
        else:
            # Balanced optimization
            self._optimize_balanced(media_plan, performance_data)
        
        return {
            "optimized_media_plan": media_plan.to_dict(),
            "campaign_id": campaign_id,
            "status": "completed"
        }
    
    def _activity_adjust_media_plan(self, context: ProcessContext) -> Dict:
        """Process activity to make adjustments to an existing media plan."""
        campaign_id = context.get_parameter("campaign_id")
        if not campaign_id:
            raise ValueError("Missing campaign_id parameter")
            
        if campaign_id not in self.active_plans:
            raise ValueError(f"No media plan found for campaign {campaign_id}")
            
        adjustment_type = context.get_parameter("adjustment_type")
        adjustment_data = context.get_parameter("adjustment_data", {})
        
        if adjustment_type == "budget":
            self._update_plan_budget(campaign_id, adjustment_data)
        elif adjustment_type == "timeline":
            self._update_plan_timeline(campaign_id, adjustment_data)
        elif adjustment_type == "channel_mix":
            self._update_channel_mix(campaign_id, adjustment_data)
        else:
            raise ValueError(f"Unknown adjustment type: {adjustment_type}")
            
        return {
            "adjusted_media_plan": self.active_plans[campaign_id].to_dict(),
            "campaign_id": campaign_id,
            "adjustment_type": adjustment_type,
            "status": "completed"
        }
    
    def _optimize_for_reach(self, media_plan: MediaPlan, performance_data: Dict) -> None:
        """Optimize channel mix to maximize audience reach."""
        # Implementation would shift budget to channels with highest reach per dollar
        pass
    
    def _optimize_for_engagement(self, media_plan: MediaPlan, performance_data: Dict) -> None:
        """Optimize channel mix to maximize engagement."""
        # Implementation would shift budget to channels with highest engagement rates
        pass
    
    def _optimize_for_conversions(self, media_plan: MediaPlan, performance_data: Dict) -> None:
        """Optimize channel mix to maximize conversions."""
        # Implementation would shift budget to channels with highest conversion rates
        pass
    
    def _optimize_balanced(self, media_plan: MediaPlan, performance_data: Dict) -> None:
        """Optimize channel mix for balanced performance across metrics."""
        # Implementation would balance reach, engagement, and conversions
        pass