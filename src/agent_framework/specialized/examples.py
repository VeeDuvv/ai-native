# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file shows examples of how our special AI helpers work together to create
# advertising campaigns, like a team of people who each have different jobs but
# need to work together to make advertisements.

# High School Explanation:
# This module demonstrates the interaction between specialized agents in the
# advertising agency ecosystem. It shows how strategy, creative, and other agents
# collaborate on campaign development through structured communication patterns.

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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_campaign_planning_example():
    """
    Run an example of campaign planning with specialized agents.
    
    This example demonstrates how the Strategy Agent plans a campaign and
    briefs the Creative Agent, showing the full communication flow.
    
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
    
    # Set up agent collaboration
    strategy_agent.set_collaborator_agents(
        creative_id=creative_agent.id
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
            "age_group": "25-45",
            "interests": ["home decor", "premium brands", "online shopping"],
            "geography": "National",
            "income_level": "Upper middle"
        },
        "budget": 350000,
        "start_date": (datetime.now() + timedelta(days=45)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=90)).isoformat(),
        "required_assets": [
            "headlines",
            "email_templates",
            "social_media_posts",
            "display_ads"
        ],
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
    time.sleep(2)
    
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
        "protocol": protocol,
        "campaign_status": campaign_status
    }

def run_process_integration_example():
    """
    Run an example demonstrating process framework integration.
    
    This example shows how agents execute activities defined in the process
    framework to complete a campaign planning process.
    
    Returns:
        Dict: Results of the example execution
    """
    logger.info("Starting process integration example")
    
    # Create communication protocol
    protocol = StandardCommunicationProtocol()
    
    # Create specialized agents
    strategy_agent = StrategyAgent("strategy-process-agent", protocol)
    creative_agent = CreativeAgent("creative-process-agent", protocol)
    
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
    
    # Set collaborators
    strategy_agent.set_collaborator_agents(
        creative_id=creative_agent.id
    )
    
    # Execute a process activity to create a campaign
    activity_context = {
        "campaign_name": "Summer Sale Process-Driven Campaign",
        "objectives": ["Increase sales", "Promote new products"],
        "target_audience": {
            "age_group": "18-30",
            "interests": ["fashion", "technology"]
        },
        "budget": 150000,
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=30)).isoformat()
    }
    
    # Execute the activity
    logger.info("Executing campaign planning activity")
    result = strategy_agent.execute_activity("plan_advertising_campaign", activity_context)
    
    if result["success"]:
        campaign_id = result["campaign_id"]
        logger.info(f"Campaign created with ID: {campaign_id}")
        
        # Execute a briefing activity
        brief_result = strategy_agent.execute_activity(
            "brief_specialized_agents", 
            {"campaign_id": campaign_id}
        )
        
        if brief_result["success"]:
            logger.info(f"Successfully briefed agents: {brief_result['briefed_agents']}")
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
        "strategy_agent": strategy_agent,
        "creative_agent": creative_agent,
        "campaign_status": campaign_status
    }

if __name__ == "__main__":
    # Run the communication-based example
    logger.info("\n===== RUNNING COMMUNICATION EXAMPLE =====\n")
    comm_result = run_campaign_planning_example()
    
    # Wait a moment between examples
    time.sleep(1)
    
    # Run the process-based example
    logger.info("\n\n===== RUNNING PROCESS INTEGRATION EXAMPLE =====\n")
    process_result = run_process_integration_example()
    
    # Print summary
    logger.info("\n\n===== EXAMPLES COMPLETED =====")
    logger.info(f"Communication example campaign: {comm_result['campaign_id']}")
    logger.info(f"Process integration example campaign: {process_result.get('campaign_id', 'Failed')}")