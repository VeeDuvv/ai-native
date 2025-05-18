# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file shows examples of how our special AI helpers work together to create
# advertising campaigns, like a team of people who each have different jobs but
# need to work together to make advertisements.

# High School Explanation:
# This module demonstrates the interaction between specialized agents in the
# advertising agency ecosystem. It shows how strategy, creative, media planning,
# analytics, and client communication agents collaborate on campaign development
# through structured communication patterns.

"""
Examples demonstrating specialized agent interactions.

This module contains examples that show how the specialized advertising agents
work together to plan and execute campaigns, demonstrating the agent communication
protocol, process framework integration, and knowledge graph utilization.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any

from ..communication.protocol import StandardCommunicationProtocol
from .strategy import StrategyAgent, StrategyMessageType
from .creative import CreativeAgent
from .media import MediaPlanningAgent
from .analytics import AnalyticsAgent
from .client import ClientCommunicationAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_campaign_planning_example():
    """
    Run an example of campaign planning with specialized agents.
    
    This example demonstrates how the Strategy Agent plans a campaign,
    briefs the Creative Agent for asset development, and works with the
    Media Planning Agent to optimize channel distribution.
    
    Returns:
        Dict: Results of the example execution
    """
    logger.info("Starting campaign planning example")
    
    # Create communication protocol
    protocol = StandardCommunicationProtocol()
    
    # Start background message processing
    protocol.start_background_processing(interval=0.1)
    logger.info("Started background message processing")
    
    # Create specialized agents
    strategy_agent = StrategyAgent("strategy-agent-1", protocol)
    creative_agent = CreativeAgent("creative-agent-1", protocol)
    media_agent = MediaPlanningAgent("media-agent-1", protocol)
    
    # Initialize agents
    strategy_agent.initialize({
        "name": "Campaign Strategy Agent",
        "description": "Plans and coordinates advertising campaigns",
        "enabled": True
    })
    
    creative_agent.initialize({
        "name": "Creative Producer Agent",
        "description": "Develops creative assets for campaigns",
        "enabled": True
    })
    
    media_agent.initialize({
        "name": "Media Planning Agent",
        "description": "Optimizes channel selection and budget allocation",
        "enabled": True
    })
    
    # Set up agent collaboration
    strategy_agent.set_collaborator_agents(
        creative_id=creative_agent.id,
        media_id=media_agent.id
    )
    
    # Define a test campaign
    campaign_details = {
        "name": "Holiday Season Promotion 2025",
        "objectives": [
            "Increase online sales by 30%",
            "Build brand awareness for new product line",
            "Generate email list signups"
        ],
        "target_audience": {
            "age_range": "25-45",
            "interests": ["home decor", "premium brands", "online shopping"],
            "geography": "National",
            "income_level": "Upper middle"
        },
        "budget": 350000,
        "media_budget": 250000,  # Portion of budget allocated to media
        "start_date": (datetime.now() + timedelta(days=45)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=90)).isoformat(),
        "required_assets": [
            "headlines",
            "email_templates",
            "social_media_posts",
            "display_ads"
        ],
        "primary_objective": "conversion",  # For media planning: awareness, consideration, conversion
        "brand_guidelines": {
            "tone": "Sophisticated, warm, and inviting",
            "colors": ["#8B4513", "#F5F5DC", "#228B22"],
            "logo_usage": "Prominently displayed in all assets"
        }
    }
    
    # Create the campaign
    logger.info("Creating campaign via Strategy Agent")
    campaign_id = strategy_agent.create_campaign(campaign_details)
    
    # Allow time for background processing to deliver messages
    logger.info("Waiting for message processing")
    time.sleep(3)  # Extended to allow for media planning messages
    
    # Get campaign status
    campaign_status = strategy_agent.get_campaign_status(campaign_id)
    logger.info(f"Campaign status: {campaign_status['status']}")
    
    # Print component statuses
    for component, status in campaign_status["components"].items():
        logger.info(f"  {component}: {status}")
    
    # Print messages processed
    logger.info(f"Messages in history: {len(protocol.message_history)}")
    
    # Get topics with subscribers
    topics = protocol.list_topics()
    for topic in topics:
        logger.info(f"Topic '{topic['name']}' has {topic['subscribers']} subscribers")
    
    # Stop background processing
    protocol.stop_background_processing()
    logger.info("Stopped background message processing")
    
    # Return example results
    return {
        "campaign_id": campaign_id,
        "strategy_agent": strategy_agent,
        "creative_agent": creative_agent,
        "media_agent": media_agent,
        "protocol": protocol,
        "campaign_status": campaign_status
    }

def run_media_optimization_example():
    """
    Run a specific example of media planning and optimization.
    
    This example focuses on the Media Planning Agent's capabilities
    for channel selection, budget allocation, and optimization.
    
    Returns:
        Dict: Results of the example execution
    """
    logger.info("Starting media optimization example")
    
    # Create communication protocol
    protocol = StandardCommunicationProtocol()
    
    # Create media agent
    media_agent = MediaPlanningAgent("media-optimization-agent", protocol)
    
    # Initialize the agent
    media_agent.initialize({
        "name": "Media Optimization Agent",
        "description": "Optimizes media plans for maximum performance",
        "enabled": True
    })
    
    # Create a test media brief
    media_brief = {
        "message_type": "MEDIA_BRIEF",
        "campaign_id": "test-campaign-123",
        "media_budget": 150000,
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=60)).isoformat(),
        "primary_objective": "awareness",  # awareness, consideration, conversion
        "target_audience": {
            "age_range": "18-34",
            "gender": "all",
            "interests": ["sports", "fitness", "health"],
            "geography": "US",
            "income": "middle",
            "behaviors": ["mobile_users", "gym_members"]
        }
    }
    
    # Send the media brief directly to the agent
    # Note: In a real scenario, this would come from the Strategy Agent
    # but for this example, we'll simulate it directly
    brief_message = protocol.create_message(
        message_type="REQUEST",
        sender="test-strategy-agent",
        recipient=media_agent.id,
        content=media_brief
    )
    
    protocol.send_message(brief_message)
    logger.info(f"Sent media brief for campaign {media_brief['campaign_id']}")
    
    # Allow time for processing
    time.sleep(1)
    
    # Request the media plan
    request_message = protocol.create_message(
        message_type="REQUEST",
        sender="test-strategy-agent",
        recipient=media_agent.id,
        content={
            "message_type": "MEDIA_PLAN_REQUEST",
            "campaign_id": media_brief["campaign_id"]
        }
    )
    
    protocol.send_message(request_message)
    logger.info("Requested media plan")
    
    # Allow time for processing
    time.sleep(1)
    
    # Request an update to the media plan with a budget change
    update_message = protocol.create_message(
        message_type="REQUEST",
        sender="test-strategy-agent",
        recipient=media_agent.id,
        content={
            "message_type": "UPDATE_MEDIA_PLAN",
            "campaign_id": media_brief["campaign_id"],
            "update_type": "budget",
            "update_data": {
                "new_budget": 180000  # 20% budget increase
            }
        }
    )
    
    protocol.send_message(update_message)
    logger.info("Requested media plan budget update")
    
    # Allow time for processing
    time.sleep(1)
    
    # Check the active plans in the media agent
    active_plans = media_agent.active_plans
    if media_brief["campaign_id"] in active_plans:
        plan = active_plans[media_brief["campaign_id"]]
        logger.info(f"Active media plan found for campaign {media_brief['campaign_id']}")
        logger.info(f"Total budget: ${plan.total_budget:,.2f}")
        logger.info(f"Channels: {', '.join(plan.channel_allocations.keys())}")
        
        # Print channel allocations
        logger.info("Channel allocations:")
        for channel, allocation in plan.channel_allocations.items():
            budget_amount = allocation["budget_amount"]
            percentage = allocation["budget_percentage"]
            impressions = allocation.get("expected_impressions", 0)
            logger.info(f"  {channel}: ${budget_amount:,.2f} ({percentage}%) - Expected impressions: {impressions:,}")
    else:
        logger.warning(f"No active media plan found for campaign {media_brief['campaign_id']}")
    
    return {
        "media_agent": media_agent,
        "protocol": protocol,
        "campaign_id": media_brief["campaign_id"],
        "active_plans": active_plans
    }

def run_analytics_example():
    """
    Run an example demonstrating the Analytics Agent functionality.
    
    This example shows how the Analytics Agent monitors campaign performance,
    detects anomalies, and generates insights and recommendations.
    
    Returns:
        Dict: Results of the example execution
    """
    logger.info("Starting analytics agent example")
    
    # Create communication protocol
    protocol = StandardCommunicationProtocol()
    
    # Create specialized agents
    strategy_agent = StrategyAgent("strategy-analytics-agent", protocol)
    analytics_agent = AnalyticsAgent("analytics-agent", protocol)
    
    # Initialize agents
    strategy_agent.initialize({
        "name": "Strategy Agent",
        "description": "Plans and coordinates advertising campaigns",
        "enabled": True
    })
    
    analytics_agent.initialize({
        "name": "Analytics Agent",
        "description": "Monitors campaign performance and generates insights",
        "enabled": True
    })
    
    # Start background data collection for analytics
    analytics_agent.start_background_collection(interval=2)
    logger.info("Started background data collection")
    
    # Create test campaign via strategy agent
    campaign_details = {
        "name": "Performance Analytics Test Campaign",
        "objectives": [
            "Increase online sales by 20%",
            "Build brand awareness in new markets"
        ],
        "target_audience": {
            "age_range": "25-45",
            "interests": ["fitness", "outdoor activities", "wellness"],
            "geography": "US",
            "income": "upper-middle"
        },
        "budget": 100000,
        "media_budget": 70000,
        "conversion_value": 65,  # Average value of a conversion
        "start_date": (datetime.now() - timedelta(days=7)).isoformat(),  # Campaign already started
        "end_date": (datetime.now() + timedelta(days=23)).isoformat(),
        "primary_objective": "conversion",
        "performance_goals": {
            "impressions": 1500000,
            "clicks": 30000,
            "ctr": 0.02,
            "conversions": 3000,
            "conversion_rate": 0.1,
            "cpa": 23.33  # Cost per acquisition
        }
    }
    
    # Create campaign
    logger.info("Creating campaign via Strategy Agent")
    campaign_id = strategy_agent.create_campaign(campaign_details)
    logger.info(f"Created campaign with ID: {campaign_id}")
    
    # Register campaign with analytics agent
    analytics_request = {
        "message_type": "ANALYTICS_REQUEST",
        "request_type": "register_campaign",
        "campaign_id": campaign_id,
        "campaign_details": {
            "name": campaign_details["name"],
            "objectives": campaign_details["objectives"],
            "start_date": campaign_details["start_date"],
            "end_date": campaign_details["end_date"],
            "budget": campaign_details["budget"],
            "performance_goals": campaign_details["performance_goals"],
            "conversion_value": campaign_details["conversion_value"],
            "strategy_agent_id": strategy_agent.id
        }
    }
    
    # Send registration request
    message = protocol.create_message(
        message_type="REQUEST",
        sender=strategy_agent.id,
        recipient=analytics_agent.id,
        content=analytics_request
    )
    
    protocol.send_message(message)
    logger.info(f"Registered campaign {campaign_id} with analytics agent")
    
    # Wait for some data collection
    logger.info("Waiting for data collection...")
    time.sleep(3)
    
    # Generate a performance report
    report_request = {
        "message_type": "ANALYTICS_REQUEST",
        "request_type": "generate_report",
        "campaign_id": campaign_id,
        "time_period": {
            "start": (datetime.now() - timedelta(days=7)).isoformat(),
            "end": datetime.now().isoformat()
        }
    }
    
    # Send report request
    message = protocol.create_message(
        message_type="REQUEST",
        sender=strategy_agent.id,
        recipient=analytics_agent.id,
        content=report_request
    )
    
    protocol.send_message(message)
    logger.info("Requested performance report")
    
    # Wait for report generation
    time.sleep(2)
    
    # Get the report
    get_report_request = {
        "message_type": "ANALYTICS_REQUEST",
        "request_type": "get_report",
        "campaign_id": campaign_id
    }
    
    # Send get report request
    message = protocol.create_message(
        message_type="REQUEST",
        sender=strategy_agent.id,
        recipient=analytics_agent.id,
        content=get_report_request
    )
    
    protocol.send_message(message)
    logger.info("Requested report details")
    
    # Wait for response
    time.sleep(1)
    
    # Process activities example
    # Use the process activities to perform analytics tasks
    logger.info("Executing analytics process activities")
    
    # Generate a performance report through the process activity
    report_result = analytics_agent.execute_activity(
        "generate_performance_report",
        {
            "campaign_id": campaign_id,
            "time_period": {
                "start": (datetime.now() - timedelta(days=7)).isoformat(),
                "end": datetime.now().isoformat()
            }
        }
    )
    
    if report_result["success"]:
        report = report_result["report"]
        logger.info(f"Generated report with {len(report['metrics'])} metrics")
        logger.info(f"Found {len(report['insights'])} insights")
        logger.info(f"Generated {len(report['recommendations'])} recommendations")
        
        # Print top insights
        if report['insights']:
            logger.info(f"Top insight: {report['insights'][0]['description']}")
        
        # Print top recommendation
        if report['recommendations']:
            logger.info(f"Top recommendation: {report['recommendations'][0]['description']}")
    
    # Detect anomalies through the process activity
    anomaly_result = analytics_agent.execute_activity(
        "detect_anomalies",
        {
            "campaign_id": campaign_id,
            "sensitivity": "high"  # More sensitive detection
        }
    )
    
    if anomaly_result["success"]:
        anomalies = anomaly_result.get("anomalies_detected", 0)
        logger.info(f"Detected {anomalies} anomalies")
        
        if anomalies > 0 and "alerts" in anomaly_result:
            logger.info(f"Example anomaly: {anomaly_result['alerts'][0]['description']}")
    
    # Generate optimization recommendations
    recommendations_result = analytics_agent.execute_activity(
        "generate_optimization_recommendations",
        {
            "campaign_id": campaign_id,
            "focus_areas": ["budget", "creative"]  # Focus on budget and creative recommendations
        }
    )
    
    if recommendations_result["success"]:
        recommendation_count = recommendations_result.get("recommendations_count", 0)
        logger.info(f"Generated {recommendation_count} focused recommendations")
        
        if recommendation_count > 0:
            recommendations = recommendations_result.get("recommendations", [])
            for i, rec in enumerate(recommendations[:2]):
                logger.info(f"Recommendation {i+1}: {rec['description']} ({rec['priority']})")
    
    # Stop background data collection
    analytics_agent.stop_background_collection()
    logger.info("Stopped background data collection")
    
    return {
        "campaign_id": campaign_id,
        "strategy_agent": strategy_agent,
        "analytics_agent": analytics_agent,
        "protocol": protocol
    }

def run_client_communication_example():
    """
    Run an example demonstrating the Client Communication Agent functionality.
    
    This example shows how the Client Communication Agent manages client interactions,
    approval workflows, and campaign updates.
    
    Returns:
        Dict: Results of the example execution
    """
    logger.info("Starting client communication example")
    
    # Create communication protocol
    protocol = StandardCommunicationProtocol()
    
    # Create specialized agents
    strategy_agent = StrategyAgent("strategy-client-agent", protocol)
    creative_agent = CreativeAgent("creative-client-agent", protocol)
    client_agent = ClientCommunicationAgent("client-agent", protocol)
    
    # Initialize agents
    strategy_agent.initialize({
        "name": "Strategy Agent",
        "description": "Plans and coordinates advertising campaigns",
        "enabled": True
    })
    
    creative_agent.initialize({
        "name": "Creative Agent",
        "description": "Develops creative assets for campaigns",
        "enabled": True
    })
    
    client_agent.initialize({
        "name": "Client Communication Agent",
        "description": "Manages client interactions and approvals",
        "enabled": True
    })
    
    # Start notification processing for client agent
    client_agent.start_notification_processing(interval=2)
    logger.info("Started client notification processing")
    
    # Register a test client
    client_data = {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "company": "Acme Corporation",
        "role": "Marketing Director",
        "preferences": {
            "communication_frequency": "weekly",
            "notification_channels": ["email"],
            "update_types": ["performance", "approvals", "milestones"],
            "approval_reminders": True,
            "report_format": "detailed"
        }
    }
    
    # Register client via client agent
    client_request = {
        "message_type": "CLIENT_REQUEST",
        "request_type": "register_client",
        "client_data": client_data
    }
    
    # Send registration request
    message = protocol.create_message(
        message_type="REQUEST",
        sender=strategy_agent.id,
        recipient=client_agent.id,
        content=client_request
    )
    
    protocol.send_message(message)
    logger.info("Sent client registration request")
    
    # Wait for processing
    time.sleep(1)
    
    # Create a test campaign via strategy agent
    campaign_details = {
        "name": "Summer Product Launch 2025",
        "objectives": [
            "Introduce new product line to market",
            "Generate product awareness and interest",
            "Drive initial sales"
        ],
        "target_audience": {
            "age_range": "25-45",
            "interests": ["fashion", "lifestyle", "technology"],
            "geography": "National",
            "income_level": "Middle to upper-middle"
        },
        "budget": 250000,
        "start_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=90)).isoformat(),
        "required_assets": [
            "product_photos",
            "social_media_posts",
            "email_campaign",
            "landing_page"
        ],
        "brand_guidelines": {
            "tone": "Modern, innovative, and premium",
            "colors": ["#1A5F7A", "#FFC107", "#FFFFFF"],
            "logo_usage": "Standard logo placement required on all assets"
        }
    }
    
    # Create campaign
    logger.info("Creating campaign via Strategy Agent")
    campaign_id = strategy_agent.create_campaign(campaign_details)
    logger.info(f"Created campaign with ID: {campaign_id}")
    
    # Associate campaign with client
    client_id = None
    for msg in protocol.message_history:
        if msg.get("content", {}).get("request_type") == "register_client" and msg.get("recipient") == client_agent.id:
            # Find the response with client_id
            for response in protocol.message_history:
                if response.get("content", {}).get("client_id") and response.get("sender") == client_agent.id:
                    client_id = response["content"]["client_id"]
                    break
            break
    
    if client_id:
        # Associate campaign with client
        associate_request = {
            "message_type": "CLIENT_REQUEST",
            "request_type": "associate_campaign",
            "client_id": client_id,
            "campaign_id": campaign_id,
            "campaign_data": {
                "name": campaign_details["name"],
                "status": "planning",
                "budget": campaign_details["budget"],
                "start_date": campaign_details["start_date"],
                "end_date": campaign_details["end_date"]
            }
        }
        
        # Send association request
        message = protocol.create_message(
            message_type="REQUEST",
            sender=strategy_agent.id,
            recipient=client_agent.id,
            content=associate_request
        )
        
        protocol.send_message(message)
        logger.info(f"Associated campaign {campaign_id} with client {client_id}")
        
        # Wait for processing
        time.sleep(1)
        
        # Create an approval request for creative assets
        approval_request = {
            "message_type": "APPROVAL_REQUEST",
            "client_id": client_id,
            "campaign_id": campaign_id,
            "request_type": "creative",
            "title": "Summer Product Launch - Initial Concepts",
            "description": "Please review these initial creative concepts for the Summer Product Launch campaign",
            "items_for_approval": [
                {
                    "item_id": "concept-1",
                    "type": "creative_concept",
                    "title": "Modern Minimalist Approach",
                    "description": "Clean, minimalist design focusing on product features",
                    "preview_url": "https://example.com/previews/concept1.jpg"
                },
                {
                    "item_id": "concept-2",
                    "type": "creative_concept",
                    "title": "Lifestyle Integration Approach",
                    "description": "Showing products in aspirational lifestyle settings",
                    "preview_url": "https://example.com/previews/concept2.jpg"
                },
                {
                    "item_id": "concept-3",
                    "type": "creative_concept",
                    "title": "Technical Excellence Approach",
                    "description": "Highlighting technical innovations and specifications",
                    "preview_url": "https://example.com/previews/concept3.jpg"
                }
            ],
            "deadline": (datetime.now() + timedelta(days=5)).isoformat(),
            "priority": "high"
        }
        
        # Send approval request via creative agent
        message = protocol.create_message(
            message_type="REQUEST",
            sender=creative_agent.id,
            recipient=client_agent.id,
            content=approval_request
        )
        
        protocol.send_message(message)
        logger.info("Sent creative approval request to client")
        
        # Wait for processing
        time.sleep(1)
        
        # Get request ID from message history for demonstration purposes
        request_id = None
        for msg in protocol.message_history:
            if msg.get("content", {}).get("message_type") == "APPROVAL_REQUEST" and msg.get("recipient") == client_agent.id:
                # Find the response with request_id
                for response in protocol.message_history:
                    if response.get("content", {}).get("request_id") and response.get("sender") == client_agent.id:
                        request_id = response["content"]["request_id"]
                        break
                break
        
        # Simulate client response to approval request
        if request_id:
            # Process client response
            response_data = {
                "client_id": client_id,
                "request_id": request_id,
                "decision": "approved",
                "decision_details": {
                    "approved_items": ["concept-1", "concept-3"],
                    "rejected_items": ["concept-2"]
                },
                "feedback": "I like concepts 1 and 3. Concept 1 should be our primary direction, using elements from concept 3 to highlight the technical features. Let's not pursue concept 2 as it doesn't align with our current brand direction."
            }
            
            # Send client response
            client_response = {
                "message_type": "CLIENT_RESPONSE",
                "response_data": response_data
            }
            
            message = protocol.create_message(
                message_type="REQUEST",
                sender="client-interface",  # Simulated client interface
                recipient=client_agent.id,
                content=client_response
            )
            
            protocol.send_message(message)
            logger.info("Sent client response to approval request")
            
            # Wait for processing
            time.sleep(1)
            
            # Send a campaign update to client
            update_request = {
                "message_type": "CAMPAIGN_UPDATE",
                "client_id": client_id,
                "campaign_id": campaign_id,
                "update_type": "milestone",
                "title": "Campaign Planning Phase Completed",
                "content": "We've completed the planning phase of your Summer Product Launch campaign. Creative concepts have been approved and we're now moving into the production phase. Production timeline is on track for launch on the planned date.",
                "importance": "medium"
            }
            
            # Send update via strategy agent
            message = protocol.create_message(
                message_type="REQUEST",
                sender=strategy_agent.id,
                recipient=client_agent.id,
                content=update_request
            )
            
            protocol.send_message(message)
            logger.info("Sent campaign update to client")
        
        # Get client summary
        summary_request = {
            "message_type": "CLIENT_REQUEST",
            "request_type": "client_summary",
            "client_id": client_id
        }
        
        # Send summary request
        message = protocol.create_message(
            message_type="REQUEST",
            sender=strategy_agent.id,
            recipient=client_agent.id,
            content=summary_request
        )
        
        protocol.send_message(message)
        logger.info("Requested client summary")
        
        # Wait for processing
        time.sleep(1)
        
        # Process activities example
        # Use the process activities to perform client communication tasks
        logger.info("Executing client communication process activities")
        
        # Send a performance update through the process activity
        update_result = client_agent.execute_activity(
            "send_client_update",
            {
                "client_id": client_id,
                "campaign_id": campaign_id,
                "update_type": "planning",
                "title": "Campaign Planning Update",
                "content": "We're making great progress on the campaign planning. Creative concepts have been approved and we're now working on the detailed execution plan."
            }
        )
        
        if update_result["success"]:
            logger.info(f"Sent client update with ID: {update_result.get('update_id')}")
        
        # Generate a client summary through the process activity
        summary_result = client_agent.execute_activity(
            "generate_client_summary",
            {
                "client_id": client_id
            }
        )
        
        if summary_result["success"]:
            summary = summary_result["summary"]
            logger.info(f"Generated client summary for {summary['name']}")
            logger.info(f"Client has {summary['active_campaigns']} active campaigns")
            logger.info(f"Communication stats: {summary['communication']}")
    else:
        logger.error("Failed to get client ID from message history")
    
    # Stop notification processing
    client_agent.stop_notification_processing()
    logger.info("Stopped client notification processing")
    
    return {
        "client_agent": client_agent,
        "strategy_agent": strategy_agent,
        "creative_agent": creative_agent,
        "client_id": client_id,
        "campaign_id": campaign_id,
        "protocol": protocol
    }

def run_process_integration_example():
    """
    Run an example demonstrating process framework integration.
    
    This example shows how agents execute activities defined in the process
    framework to complete a campaign planning process, including strategy,
    creative, and media planning.
    
    Returns:
        Dict: Results of the example execution
    """
    logger.info("Starting process integration example")
    
    # Create communication protocol
    protocol = StandardCommunicationProtocol()
    
    # Create specialized agents
    strategy_agent = StrategyAgent("strategy-process-agent", protocol)
    creative_agent = CreativeAgent("creative-process-agent", protocol)
    media_agent = MediaPlanningAgent("media-process-agent", protocol)
    analytics_agent = AnalyticsAgent("analytics-process-agent", protocol)
    client_agent = ClientCommunicationAgent("client-process-agent", protocol)
    
    # Initialize agents
    strategy_agent.initialize({
        "name": "Process-driven Strategy Agent",
        "description": "Plans campaigns through process activities",
        "enabled": True
    })
    
    creative_agent.initialize({
        "name": "Process-driven Creative Agent",
        "description": "Creates assets through process activities",
        "enabled": True
    })
    
    media_agent.initialize({
        "name": "Process-driven Media Agent",
        "description": "Plans media through process activities",
        "enabled": True
    })
    
    analytics_agent.initialize({
        "name": "Process-driven Analytics Agent",
        "description": "Monitors performance through process activities",
        "enabled": True
    })
    
    client_agent.initialize({
        "name": "Process-driven Client Agent",
        "description": "Manages client communications through process activities",
        "enabled": True
    })
    
    # Set collaborators
    strategy_agent.set_collaborator_agents(
        creative_id=creative_agent.id,
        media_id=media_agent.id
    )
    
    # Register a test client
    client_id = client_agent.register_client({
        "name": "Process Example Client",
        "email": "process.client@example.com",
        "company": "Process Corp",
        "role": "Marketing Manager"
    })
    
    # Execute a process activity to create a campaign
    activity_context = {
        "campaign_name": "Summer Sale Process-Driven Campaign",
        "objectives": ["Increase sales", "Promote new products"],
        "target_audience": {
            "age_range": "18-30",
            "interests": ["fashion", "technology"],
            "geography": "US",
            "income": "middle"
        },
        "budget": 150000,
        "media_budget": 100000,
        "primary_objective": "consideration",
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=30)).isoformat()
    }
    
    # Execute the activity
    logger.info("Executing campaign planning activity")
    result = strategy_agent.execute_activity("plan_advertising_campaign", activity_context)
    
    if result["success"]:
        campaign_id = result["campaign_id"]
        logger.info(f"Campaign created with ID: {campaign_id}")
        
        # Associate campaign with client
        client_agent.associate_campaign(client_id, campaign_id, {
            "name": activity_context["campaign_name"],
            "status": "planning",
            "budget": activity_context["budget"]
        })
        
        # Execute a briefing activity
        brief_result = strategy_agent.execute_activity(
            "brief_specialized_agents", 
            {"campaign_id": campaign_id}
        )
        
        if brief_result["success"]:
            logger.info(f"Successfully briefed agents: {brief_result['briefed_agents']}")
            
            # Execute media planning activity
            media_result = media_agent.execute_activity(
                "develop_media_plan",
                {
                    "campaign_id": campaign_id,
                    "campaign_data": {
                        "campaign_id": campaign_id,
                        "media_budget": activity_context["media_budget"],
                        "start_date": activity_context["start_date"],
                        "end_date": activity_context["end_date"],
                        "primary_objective": activity_context["primary_objective"],
                        "target_audience": activity_context["target_audience"]
                    }
                }
            )
            
            if media_result.get("status") == "completed":
                logger.info("Media plan developed successfully")
                
                # Get details about the media plan
                media_plan = media_result.get("media_plan", {})
                channel_allocations = media_plan.get("channel_allocations", {})
                
                logger.info(f"Media plan has {len(channel_allocations)} channels")
                for channel, allocation in channel_allocations.items():
                    budget = allocation.get("budget_amount", 0)
                    logger.info(f"  {channel}: ${budget:,.2f}")
                    
            # Register with analytics agent
            analytics_agent.register_campaign(campaign_id, activity_context)
            logger.info(f"Registered campaign {campaign_id} with analytics agent")
            
            # Generate some test metrics
            for source_id in analytics_agent.data_sources:
                analytics_agent._collect_data_from_source(source_id)
                
            # Generate a basic performance report
            analytics_result = analytics_agent.execute_activity(
                "generate_performance_report",
                {"campaign_id": campaign_id}
            )
            
            if analytics_result["success"]:
                logger.info("Analytics report generated successfully")
                report = analytics_result["report"]
                logger.info(f"Report has {len(report['insights'])} insights and {len(report['recommendations'])} recommendations")
                
                # Send a client update with performance data
                update_result = client_agent.execute_activity(
                    "send_client_update",
                    {
                        "client_id": client_id,
                        "campaign_id": campaign_id,
                        "update_type": "performance",
                        "title": "Initial Campaign Performance Update",
                        "content": "Here's the initial performance data for your campaign.",
                        "metrics": report["metrics"][:3]  # First few metrics
                    }
                )
                
                if update_result["success"]:
                    logger.info(f"Sent performance update to client with ID: {update_result.get('update_id')}")
        else:
            logger.error(f"Failed to brief agents: {brief_result.get('error', 'Unknown error')}")
            
        # Get campaign status
        status_result = strategy_agent.execute_activity(
            "generate_campaign_status_report",
            {"campaign_id": campaign_id, "detail_level": "detailed"}
        )
        
        campaign_status = status_result.get("report", {})
    else:
        logger.error(f"Failed to create campaign: {result.get('error', 'Unknown error')}")
        campaign_id = None
        campaign_status = None
    
    return {
        "success": result["success"],
        "campaign_id": campaign_id,
        "client_id": client_id,
        "strategy_agent": strategy_agent,
        "creative_agent": creative_agent,
        "media_agent": media_agent,
        "analytics_agent": analytics_agent,
        "client_agent": client_agent,
        "campaign_status": campaign_status
    }

def run_full_agency_example():
    """
    Run a comprehensive example of the complete ad agency with all specialized agents.
    
    This example demonstrates the full workflow of the AI-native ad agency including
    strategy planning, creative development, media planning, performance analytics,
    and client communication.
    
    Returns:
        Dict: Results of the example execution
    """
    logger.info("Starting full agency example")
    
    # Create communication protocol
    protocol = StandardCommunicationProtocol()
    
    # Start background message processing
    protocol.start_background_processing(interval=0.1)
    
    # Create all specialized agents
    strategy_agent = StrategyAgent("full-strategy-agent", protocol)
    creative_agent = CreativeAgent("full-creative-agent", protocol)
    media_agent = MediaPlanningAgent("full-media-agent", protocol)
    analytics_agent = AnalyticsAgent("full-analytics-agent", protocol)
    client_agent = ClientCommunicationAgent("full-client-agent", protocol)
    
    # Initialize all agents
    strategy_agent.initialize({
        "name": "Campaign Strategy Agent",
        "description": "Plans and coordinates advertising campaigns",
        "enabled": True
    })
    
    creative_agent.initialize({
        "name": "Creative Producer Agent",
        "description": "Develops creative assets for campaigns",
        "enabled": True
    })
    
    media_agent.initialize({
        "name": "Media Planning Agent",
        "description": "Optimizes channel selection and budget allocation",
        "enabled": True
    })
    
    analytics_agent.initialize({
        "name": "Analytics Agent",
        "description": "Monitors campaign performance and generates insights",
        "enabled": True
    })
    
    client_agent.initialize({
        "name": "Client Communication Agent",
        "description": "Manages client interactions and approvals",
        "enabled": True
    })
    
    # Set up agent collaboration
    strategy_agent.set_collaborator_agents(
        creative_id=creative_agent.id,
        media_id=media_agent.id
    )
    
    # Start background processes
    analytics_agent.start_background_collection(interval=2)
    client_agent.start_notification_processing(interval=2)
    
    # Register a client
    client_id = client_agent.register_client({
        "name": "Full Agency Example Client",
        "email": "client@example.com",
        "company": "Example Enterprises",
        "role": "Chief Marketing Officer"
    })
    
    # Define a comprehensive campaign
    campaign_details = {
        "name": "Q4 Product Launch Campaign",
        "objectives": [
            "Launch new flagship product",
            "Establish brand leadership in the category",
            "Drive 5000 pre-orders within first month"
        ],
        "target_audience": {
            "age_range": "25-55",
            "interests": ["technology", "innovation", "productivity"],
            "geography": "Global",
            "income_level": "Middle to upper"
        },
        "budget": 500000,
        "media_budget": 350000,
        "start_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=120)).isoformat(),
        "required_assets": [
            "product_videos",
            "social_media_campaign",
            "website_landing_pages",
            "email_sequences",
            "digital_ads",
            "press_kit"
        ],
        "primary_objective": "conversion",
        "secondary_objective": "awareness",
        "brand_guidelines": {
            "tone": "Innovative, professional, and forward-thinking",
            "colors": ["#0A2463", "#3E92CC", "#FFFAFF"],
            "logo_usage": "Logo must appear prominently in all materials"
        }
    }
    
    # Create the campaign via strategy agent
    logger.info("Creating comprehensive campaign")
    campaign_id = strategy_agent.create_campaign(campaign_details)
    
    # Associate campaign with client
    client_agent.associate_campaign(client_id, campaign_id, {
        "name": campaign_details["name"],
        "status": "planning",
        "budget": campaign_details["budget"],
        "start_date": campaign_details["start_date"],
        "end_date": campaign_details["end_date"]
    })
    
    # Wait for message processing
    logger.info("Waiting for message processing")
    time.sleep(3)
    
    # Register campaign with analytics agent
    analytics_agent.register_campaign(campaign_id, {
        "name": campaign_details["name"],
        "objectives": campaign_details["objectives"],
        "budget": campaign_details["budget"],
        "start_date": campaign_details["start_date"],
        "end_date": campaign_details["end_date"]
    })
    
    # Generate sample data for the campaign
    for source_id in analytics_agent.data_sources:
        analytics_agent._collect_data_from_source(source_id)
    
    # Step 1: Create approval request for creative concept
    creative_approval = {
        "message_type": "APPROVAL_REQUEST",
        "client_id": client_id,
        "campaign_id": campaign_id,
        "request_type": "creative_concept",
        "title": "Q4 Product Launch - Creative Direction",
        "description": "Please review and approve the creative direction for the Q4 Product Launch campaign.",
        "items_for_approval": [
            {
                "item_id": "concept-a",
                "type": "creative_direction",
                "title": "Technical Excellence",
                "description": "Focus on product specifications and technical advantages"
            },
            {
                "item_id": "concept-b",
                "type": "creative_direction",
                "title": "Lifestyle Integration",
                "description": "Show how the product integrates into users' daily lives"
            },
            {
                "item_id": "concept-c",
                "type": "creative_direction",
                "title": "Innovation Spotlight",
                "description": "Highlight the innovative features and industry-first capabilities"
            }
        ]
    }
    
    # Send approval request
    message = protocol.create_message(
        message_type="REQUEST",
        sender=creative_agent.id,
        recipient=client_agent.id,
        content=creative_approval
    )
    
    protocol.send_message(message)
    logger.info("Sent creative concept approval request")
    
    # Wait for processing
    time.sleep(1)
    
    # Step 2: Create a media plan
    media_brief = {
        "message_type": "MEDIA_BRIEF",
        "campaign_id": campaign_id,
        "media_budget": campaign_details["media_budget"],
        "start_date": campaign_details["start_date"],
        "end_date": campaign_details["end_date"],
        "primary_objective": campaign_details["primary_objective"],
        "secondary_objective": campaign_details["secondary_objective"],
        "target_audience": campaign_details["target_audience"]
    }
    
    # Send media brief
    message = protocol.create_message(
        message_type="REQUEST",
        sender=strategy_agent.id,
        recipient=media_agent.id,
        content=media_brief
    )
    
    protocol.send_message(message)
    logger.info("Sent media brief for channel planning")
    
    # Wait for processing
    time.sleep(2)
    
    # Step 3: Generate a performance projection
    report_request = {
        "message_type": "ANALYTICS_REQUEST",
        "request_type": "generate_report",
        "campaign_id": campaign_id
    }
    
    # Send report request
    message = protocol.create_message(
        message_type="REQUEST",
        sender=strategy_agent.id,
        recipient=analytics_agent.id,
        content=report_request
    )
    
    protocol.send_message(message)
    logger.info("Requested performance projection")
    
    # Wait for processing
    time.sleep(2)
    
    # Step 4: Send campaign plan to client
    update_request = {
        "message_type": "CAMPAIGN_UPDATE",
        "client_id": client_id,
        "campaign_id": campaign_id,
        "update_type": "planning",
        "title": "Q4 Product Launch - Campaign Plan",
        "content": "We've finalized the campaign plan for your Q4 Product Launch. The strategy includes a multi-channel approach focusing on digital media with supporting traditional channels. Creative concepts are ready for your approval, and we've developed a comprehensive media plan to reach your target audience effectively.",
        "importance": "high"
    }
    
    # Send update
    message = protocol.create_message(
        message_type="REQUEST",
        sender=strategy_agent.id,
        recipient=client_agent.id,
        content=update_request
    )
    
    protocol.send_message(message)
    logger.info("Sent campaign plan update to client")
    
    # Wait for processing
    time.sleep(1)
    
    # Generate client summary
    summary = client_agent.generate_client_summary(client_id)
    
    if summary["success"]:
        logger.info(f"Generated summary for {summary['summary']['name']}")
        logger.info(f"Client has {summary['summary']['active_campaigns']} active campaigns")
        logger.info(f"Client communication stats: {summary['summary']['communication']}")
    
    # Stop background processes
    protocol.stop_background_processing()
    analytics_agent.stop_background_collection()
    client_agent.stop_notification_processing()
    
    return {
        "campaign_id": campaign_id,
        "client_id": client_id,
        "strategy_agent": strategy_agent,
        "creative_agent": creative_agent,
        "media_agent": media_agent,
        "analytics_agent": analytics_agent,
        "client_agent": client_agent,
        "protocol": protocol
    }

if __name__ == "__main__":
    # Run the communication-based example
    logger.info("\n===== RUNNING COMMUNICATION EXAMPLE =====\n")
    comm_result = run_campaign_planning_example()
    
    # Wait a moment between examples
    time.sleep(1)
    
    # Run the media optimization example
    logger.info("\n\n===== RUNNING MEDIA OPTIMIZATION EXAMPLE =====\n")
    media_result = run_media_optimization_example()
    
    # Wait a moment between examples
    time.sleep(1)
    
    # Run the analytics example
    logger.info("\n\n===== RUNNING ANALYTICS EXAMPLE =====\n")
    analytics_result = run_analytics_example()
    
    # Wait a moment between examples
    time.sleep(1)
    
    # Run the client communication example
    logger.info("\n\n===== RUNNING CLIENT COMMUNICATION EXAMPLE =====\n")
    client_result = run_client_communication_example()
    
    # Wait a moment between examples
    time.sleep(1)
    
    # Run the process-based example
    logger.info("\n\n===== RUNNING PROCESS INTEGRATION EXAMPLE =====\n")
    process_result = run_process_integration_example()
    
    # Wait a moment between examples
    time.sleep(1)
    
    # Run the full agency example
    logger.info("\n\n===== RUNNING FULL AGENCY EXAMPLE =====\n")
    full_result = run_full_agency_example()
    
    # Print summary
    logger.info("\n\n===== EXAMPLES COMPLETED =====")
    logger.info(f"Communication example campaign: {comm_result['campaign_id']}")
    logger.info(f"Media optimization example campaign: {media_result['campaign_id']}")
    logger.info(f"Analytics example campaign: {analytics_result['campaign_id']}")
    logger.info(f"Client communication example campaign: {client_result['campaign_id']}")
    logger.info(f"Process integration example campaign: {process_result.get('campaign_id', 'Failed')}")
    logger.info(f"Full agency example campaign: {full_result.get('campaign_id', 'Failed')}")