#!/usr/bin/env python3
"""
Demonstration script for the agent communication protocol.

This script showcases how to initialize and use the communication protocol
with various agents for the AI-native advertising agency.
"""

import os
import sys
import logging
import json
from datetime import datetime, timedelta
from uuid import uuid4

# Add the project root to sys.path to allow running this script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.agent_framework.communication.protocol import StandardCommunicationProtocol
from src.agent_framework.communication.examples import run_example
from src.agent_framework.communication.ad_agency_example import (
    run_ad_agency_example,
    CampaignManagerAgent,
    CreativeAgent,
    AgencyMessageType
)


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('demo')


def basic_example():
    """Run the basic communication example."""
    logger.info("Running basic communication example...")
    
    # Run the example from the examples module
    campaign_manager, creative_agent, protocol = run_example()
    
    logger.info("Basic example completed.")
    logger.info(f"Sent messages: {len(campaign_manager.sent_messages)}")
    logger.info(f"Received messages: {len(creative_agent.received_messages)}")
    
    return campaign_manager, creative_agent, protocol


def ad_agency_example():
    """Run the advertising agency example."""
    logger.info("Running advertising agency example...")
    
    # Run the example from the ad_agency_example module
    result = run_ad_agency_example()
    
    logger.info("Ad agency example completed.")
    logger.info(f"Campaign ID: {result['campaign_id']}")
    logger.info(f"Campaign status: {result['campaign_manager'].active_campaigns[result['campaign_id']]['status']}")
    
    # Print campaign components status
    components = result['campaign_manager'].active_campaigns[result['campaign_id']]['components']
    for component, data in components.items():
        logger.info(f"Component '{component}' status: {data['status']}")
    
    return result


def custom_example():
    """Create a custom example with additional agent types."""
    logger.info("Running custom example...")
    
    # Create communication protocol
    protocol = StandardCommunicationProtocol()
    
    # Create campaign manager
    campaign_manager = CampaignManagerAgent("custom-campaign-mgr", protocol)
    
    # Create multiple creative agents (specializing in different media)
    digital_creative = CreativeAgent("digital-creative", protocol)
    print_creative = CreativeAgent("print-creative", protocol)
    
    # Set up campaign manager with multiple creative agents
    # In a real implementation, we'd have a more sophisticated agent routing system
    campaign_manager.set_collaborator_agents(
        creative_id="digital-creative",  # Default to digital creative
        audience_id="audience-1",
        media_id="media-1",
        analytics_id="analytics-1"
    )
    
    # Create sample campaigns
    digital_campaign = {
        "id": f"camp-digital-{str(uuid4())[:6]}",
        "name": "Digital Brand Campaign",
        "brief": "Increase online brand awareness through digital channels",
        "target_audience": "Tech-savvy professionals, 30-45",
        "objectives": ["Brand awareness", "Website traffic"],
        "budget": 150000,
        "start_date": (datetime.now() + timedelta(days=15)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=75)).isoformat(),
        "required_assets": ["display_ads", "social_media_posts", "video_ads"],
        "key_messages": ["Innovation", "Reliability", "Expert support"],
        "brand_guidelines": "Professional, technological, forward-thinking",
        "client_id": "client-tech"
    }
    
    # Initiate campaign
    campaign_id = campaign_manager.initiate_campaign(digital_campaign)
    
    logger.info(f"Initiated campaign: {campaign_id}")
    
    # Process messages
    processed = protocol.process_message_queue()
    logger.info(f"Processed {processed} messages")
    
    # Simulate audience response
    campaign_manager.receive_message({
        "id": str(uuid4()),
        "sender_id": "audience-1",
        "recipient_id": campaign_manager.id,
        "message_type": AgencyMessageType.AUDIENCE_DELIVERY,
        "content": {
            "campaign_id": campaign_id,
            "audience_data": {
                "demographics": {
                    "age_range": "30-45",
                    "occupation": "Technology professionals",
                    "income_level": "upper-middle"
                },
                "psychographics": {
                    "interests": ["technology", "innovation", "efficiency"],
                    "values": ["quality", "expertise", "time-saving"]
                },
                "online_behavior": {
                    "platforms": ["linkedin", "tech news sites", "youtube tech channels"]
                }
            }
        },
        "conversation_id": campaign_manager.active_campaigns[campaign_id]["conversation_id"],
        "timestamp": datetime.now().isoformat()
    })
    
    # Process messages again
    processed = protocol.process_message_queue()
    logger.info(f"Processed {processed} messages")
    
    # Display campaign status
    logger.info("Custom example completed.")
    logger.info(f"Campaign components status:")
    components = campaign_manager.active_campaigns[campaign_id]['components']
    for component, data in components.items():
        logger.info(f"Component '{component}' status: {data['status']}")
    
    return {
        "campaign_manager": campaign_manager,
        "digital_creative": digital_creative,
        "print_creative": print_creative,
        "protocol": protocol,
        "campaign_id": campaign_id
    }


def save_example_results(result, filename):
    """Save the results of an example run to a JSON file."""
    # Extract serializable data
    serializable_data = {
        "campaign_id": result.get("campaign_id", ""),
        "campaign_manager": {
            "id": result.get("campaign_manager", {}).id,
            "name": result.get("campaign_manager", {}).name,
            "active_campaigns": {}
        }
    }
    
    # Add campaign data if available
    campaign_manager = result.get("campaign_manager")
    if campaign_manager and hasattr(campaign_manager, "active_campaigns"):
        campaign_id = result.get("campaign_id")
        if campaign_id and campaign_id in campaign_manager.active_campaigns:
            campaign_data = campaign_manager.active_campaigns[campaign_id]
            
            # Convert non-serializable objects to strings
            for key, value in campaign_data.items():
                if isinstance(value, datetime):
                    campaign_data[key] = value.isoformat()
            
            serializable_data["campaign_manager"]["active_campaigns"][campaign_id] = campaign_data
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(serializable_data, f, indent=2)
    
    logger.info(f"Results saved to {filename}")


if __name__ == "__main__":
    # Run examples
    print("\n" + "="*50)
    print("AGENT COMMUNICATION PROTOCOL DEMONSTRATION")
    print("="*50 + "\n")
    
    while True:
        print("\nSelect an example to run:")
        print("1. Basic Communication Example")
        print("2. Ad Agency Example")
        print("3. Custom Example")
        print("4. Run All Examples")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-4): ")
        
        if choice == "1":
            result = basic_example()
            save_example_results(result, "basic_example_results.json")
        elif choice == "2":
            result = ad_agency_example()
            save_example_results(result, "ad_agency_example_results.json")
        elif choice == "3":
            result = custom_example()
            save_example_results(result, "custom_example_results.json")
        elif choice == "4":
            print("\nRunning all examples sequentially...\n")
            result1 = basic_example()
            result2 = ad_agency_example()
            result3 = custom_example()
            save_example_results(result1, "basic_example_results.json")
            save_example_results(result2, "ad_agency_example_results.json")
            save_example_results(result3, "custom_example_results.json")
            print("\nAll examples completed successfully.")
        elif choice == "0":
            print("\nExiting demonstration.\n")
            break
        else:
            print("\nInvalid choice. Please enter a number between 0 and 4.")
    
    print("Thank you for exploring the agent communication protocol.")
    print("="*50)