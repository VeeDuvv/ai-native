# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file shows how our AI helpers can talk to each other. It's like a
# demonstration that lets you see messages being sent between different helpers
# and watch how they work together to complete tasks.

# High School Explanation:
# This module provides a demonstration interface for the agent communication
# protocol. It showcases different examples of agent interaction, including
# basic communication, ad agency workflow, and enhanced features like pub/sub
# messaging, delivery confirmations, and background processing.

"""
Demonstration script for the agent communication protocol.

This script showcases how to initialize and use the communication protocol
with various agents for the AI-native advertising agency, including enhanced
features like pub/sub messaging, delivery confirmations, and background processing.
"""

import os
import sys
import logging
import json
import time
import threading
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from uuid import uuid4

# Add the project root to sys.path to allow running this script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.agent_framework.communication.protocol import (
    StandardCommunicationProtocol, 
    CommunicatingAgentImpl,
    DeliveryStatus,
    DeliveryConfirmation,
    MessagePriority,
    MessageType
)
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


# Define demo topics for pub/sub example
class DemoTopics:
    NEWS = "news"
    WEATHER = "weather"
    SPORTS = "sports"
    FINANCE = "finance"
    TECH = "tech"
    ALERTS = "alerts"


class PublisherAgent(CommunicatingAgentImpl):
    """Agent that publishes messages to various topics."""
    
    def __init__(self, agent_id: str, protocol: StandardCommunicationProtocol):
        super().__init__(agent_id, "Publisher", protocol)
        self.publish_count = 0
        self.successful_deliveries = 0
        self.failed_deliveries = 0
        self.delivery_statuses: Dict[str, Dict[str, Any]] = {}
        
        # Register message handlers
        self.register_message_handler(
            MessageType.RESPONSE,
            self._handle_response
        )
        
        logger.info(f"{self.name} agent initialized with ID: {self.id}")
    
    def start_publishing(self, interval: float = 1.0, duration: float = 10.0) -> None:
        """Start publishing messages to various topics periodically.
        
        Args:
            interval: Time between publications in seconds
            duration: How long to run the publisher in seconds
        """
        logger.info(f"Starting to publish messages every {interval} seconds for {duration} seconds")
        
        start_time = time.time()
        end_time = start_time + duration
        
        def publishing_loop():
            while time.time() < end_time:
                self.publish_to_random_topic()
                time.sleep(interval)
            
            logger.info(f"Publisher finished. Published {self.publish_count} messages "
                      f"({self.successful_deliveries} delivered, {self.failed_deliveries} failed)")
        
        # Start publishing in a separate thread
        threading.Thread(target=publishing_loop).start()
    
    def publish_to_random_topic(self) -> Tuple[str, int, List[str]]:
        """Publish a message to a randomly selected topic."""
        # Choose a random topic
        topic = random.choice([
            DemoTopics.NEWS,
            DemoTopics.WEATHER,
            DemoTopics.SPORTS,
            DemoTopics.FINANCE,
            DemoTopics.TECH,
            DemoTopics.ALERTS
        ])
        
        # Generate content based on topic
        content = self._generate_content_for_topic(topic)
        
        # Choose a random priority
        priority = random.choice([
            MessagePriority.LOW,
            MessagePriority.MEDIUM,
            MessagePriority.HIGH
        ])
        
        logger.info(f"Publishing message to topic '{topic}' with priority {priority.value}")
        
        # Publish to topic
        subscribers_count, message_ids = self.publish_to_topic(
            topic=topic,
            content=content,
            priority=priority
        )
        
        # Register callbacks for delivery confirmations
        for message_id in message_ids:
            confirmation = self.protocol.get_delivery_status(message_id)
            
            # Store initial status
            self.delivery_statuses[message_id] = {
                "topic": topic,
                "initial_status": confirmation.status.value if confirmation else "unknown",
                "recipient_id": confirmation.recipient_id if confirmation else "unknown",
                "created_at": time.time()
            }
            
            # Register callback with the protocol
            def make_callback(msg_id):
                def callback(confirmation):
                    self._handle_delivery_confirmation(msg_id, confirmation)
                return callback
            
            self.protocol.delivery_callbacks[message_id] = make_callback(message_id)
        
        self.publish_count += 1
        logger.info(f"Published to topic '{topic}' with {subscribers_count} subscribers, message IDs: {message_ids}")
        
        return topic, subscribers_count, message_ids
    
    def _generate_content_for_topic(self, topic: str) -> Dict[str, Any]:
        """Generate relevant content for a topic."""
        timestamp = time.time()
        
        if topic == DemoTopics.NEWS:
            return {
                "headline": f"Breaking News #{int(timestamp % 1000)}",
                "category": random.choice(["politics", "business", "entertainment", "technology"]),
                "importance": random.choice(["low", "medium", "high", "critical"]),
                "timestamp": timestamp
            }
        elif topic == DemoTopics.WEATHER:
            return {
                "condition": random.choice(["sunny", "cloudy", "rainy", "stormy", "snowy"]),
                "temperature": random.randint(0, 35),
                "location": random.choice(["New York", "London", "Tokyo", "Sydney", "Paris"]),
                "timestamp": timestamp
            }
        elif topic == DemoTopics.SPORTS:
            return {
                "sport": random.choice(["football", "basketball", "tennis", "golf", "soccer"]),
                "event": f"Game #{int(timestamp % 100)}",
                "result": f"Team A {random.randint(0, 10)} - Team B {random.randint(0, 10)}",
                "timestamp": timestamp
            }
        elif topic == DemoTopics.FINANCE:
            return {
                "market": random.choice(["stocks", "forex", "crypto", "commodities"]),
                "change": random.uniform(-5.0, 5.0),
                "volume": random.randint(1000, 10000),
                "timestamp": timestamp
            }
        elif topic == DemoTopics.TECH:
            return {
                "product": f"Product #{int(timestamp % 100)}",
                "category": random.choice(["hardware", "software", "mobile", "AI", "VR"]),
                "rating": random.randint(1, 5),
                "timestamp": timestamp
            }
        elif topic == DemoTopics.ALERTS:
            return {
                "level": random.choice(["info", "warning", "error", "critical"]),
                "system": random.choice(["database", "network", "security", "application"]),
                "message": f"Alert #{int(timestamp % 1000)}",
                "timestamp": timestamp
            }
        else:
            return {
                "message": f"Generic message for topic {topic}",
                "timestamp": timestamp
            }
    
    def _handle_delivery_confirmation(self, message_id: str, confirmation: DeliveryConfirmation) -> None:
        """Handle delivery confirmation for a message."""
        if message_id in self.delivery_statuses:
            status_info = self.delivery_statuses[message_id]
            status_info["final_status"] = confirmation.status.value
            status_info["delivery_time"] = time.time()
            status_info["delivery_duration"] = status_info["delivery_time"] - status_info["created_at"]
            
            if confirmation.status == DeliveryStatus.DELIVERED:
                self.successful_deliveries += 1
                logger.info(f"Message {message_id} delivered successfully to {confirmation.recipient_id} "
                          f"in {status_info['delivery_duration']:.3f}s")
            else:
                self.failed_deliveries += 1
                logger.warning(f"Message {message_id} delivery failed with status {confirmation.status.value}: "
                             f"{confirmation.error_message}")
                
                # Implement retry logic for failed messages
                if status_info.get("retries", 0) < 3:  # Maximum 3 retries
                    self._retry_message_delivery(message_id, status_info)
    
    def _retry_message_delivery(self, message_id: str, status_info: Dict[str, Any]) -> None:
        """Retry sending a failed message."""
        topic = status_info["topic"]
        retries = status_info.get("retries", 0) + 1
        status_info["retries"] = retries
        
        logger.info(f"Retrying message delivery for {message_id} (attempt {retries}/3) to topic {topic}")
        
        # Wait before retry with exponential backoff
        time.sleep(1.0 * (2 ** (retries - 1)))
        
        # Republish with same topic but new content
        content = self._generate_content_for_topic(topic)
        content["is_retry"] = True
        content["original_message_id"] = message_id
        content["retry_attempt"] = retries
        
        # Publish with higher priority for retries
        subscribers_count, message_ids = self.publish_to_topic(
            topic=topic,
            content=content,
            priority=MessagePriority.HIGH
        )
        
        logger.info(f"Retry published to topic '{topic}' with {subscribers_count} subscribers, message IDs: {message_ids}")
    
    def _handle_response(self, message: Dict[str, Any]) -> None:
        """Handle response messages."""
        logger.info(f"Received response from {message.sender_id}: {message.content}")


class SubscriberAgent(CommunicatingAgentImpl):
    """Agent that subscribes to topics and processes messages."""
    
    def __init__(self, agent_id: str, protocol: StandardCommunicationProtocol, 
                 interests: List[str], filter_condition: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, f"Subscriber-{agent_id}", protocol)
        self.interests = interests
        self.filter_condition = filter_condition
        self.received_messages_count = 0
        self.topic_counts: Dict[str, int] = {}
        self.processing_times: List[float] = []
        
        # Subscribe to interested topics
        for topic in interests:
            self.subscribe_to_topic(topic, filter_condition)
            logger.info(f"Agent {self.id} subscribed to topic '{topic}'" + 
                      (f" with filter {filter_condition}" if filter_condition else ""))
            
            # Initialize counter
            self.topic_counts[topic] = 0
        
        # Register message handlers
        self.register_message_handler(
            MessageType.NOTIFICATION,
            self._handle_notification
        )
        
        logger.info(f"{self.name} agent initialized with ID: {self.id}")
    
    def _handle_notification(self, message: Dict[str, Any]) -> None:
        """Handle notification messages."""
        start_time = time.time()
        
        # Extract topic from message
        topic = message.content.get("topic", "unknown")
        
        # Update counters
        self.received_messages_count += 1
        if topic in self.topic_counts:
            self.topic_counts[topic] += 1
        
        # Simulate message processing with random duration
        processing_time = random.uniform(0.01, 0.2)  # 10-200ms
        time.sleep(processing_time)
        
        # Process message based on topic
        if topic == DemoTopics.ALERTS and message.content.get("level") == "critical":
            logger.warning(f"CRITICAL ALERT received by {self.id}: {message.content.get('message')}")
            
            # Send acknowledgment
            self.send_message(
                recipient_id=message.sender_id,
                message_type=MessageType.RESPONSE,
                content={
                    "status": "acknowledged",
                    "alert_id": message.message_id,
                    "message": f"Critical alert acknowledged by {self.id}"
                },
                conversation_id=message.conversation_id,
                priority=MessagePriority.HIGH
            )
        else:
            # Standard processing
            logger.info(f"Agent {self.id} received {topic} notification: {message.content}")
        
        # Record processing time
        total_time = time.time() - start_time
        self.processing_times.append(total_time)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about received messages."""
        return {
            "agent_id": self.id,
            "total_received": self.received_messages_count,
            "by_topic": self.topic_counts.copy(),
            "avg_processing_time": sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0,
            "max_processing_time": max(self.processing_times) if self.processing_times else 0,
            "min_processing_time": min(self.processing_times) if self.processing_times else 0
        }


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


def pubsub_example():
    """Run a demonstration of the pub/sub messaging system with delivery confirmations."""
    logger.info("Running pub/sub messaging example...")
    
    # Create the communication protocol
    protocol = StandardCommunicationProtocol()
    
    # Register topics with descriptions
    protocol.register_topic(DemoTopics.NEWS, "Latest news updates from various categories")
    protocol.register_topic(DemoTopics.WEATHER, "Weather forecasts and conditions for different locations")
    protocol.register_topic(DemoTopics.SPORTS, "Sports results, events, and updates")
    protocol.register_topic(DemoTopics.FINANCE, "Financial market updates and analysis")
    protocol.register_topic(DemoTopics.TECH, "Technology news, product releases, and reviews")
    protocol.register_topic(DemoTopics.ALERTS, "System and service alerts of varying importance")
    
    # Create subscriber agents with different interests
    subscribers = [
        # News enthusiast interested in all news
        SubscriberAgent("news", protocol, [DemoTopics.NEWS]),
        
        # Weather watcher interested in specific locations
        SubscriberAgent("weather", protocol, [DemoTopics.WEATHER], 
                      {"location": "London"}),
        
        # Sports fan interested in specific sports
        SubscriberAgent("sports", protocol, [DemoTopics.SPORTS], 
                      {"sport": "basketball"}),
        
        # Financial analyst interested in stocks and crypto
        SubscriberAgent("finance", protocol, [DemoTopics.FINANCE], 
                      {"market": "stocks"}),
        
        # Tech enthusiast interested in all tech news
        SubscriberAgent("tech", protocol, [DemoTopics.TECH]),
        
        # Operations agent interested in system alerts
        SubscriberAgent("ops", protocol, [DemoTopics.ALERTS]),
        
        # Manager interested in critical alerts and financial updates
        SubscriberAgent("manager", protocol, 
                      [DemoTopics.ALERTS, DemoTopics.FINANCE], 
                      {"level": "critical"}),
        
        # General subscriber interested in multiple topics
        SubscriberAgent("general", protocol, 
                      [DemoTopics.NEWS, DemoTopics.WEATHER, DemoTopics.TECH])
    ]
    
    # Create a publisher agent
    publisher = PublisherAgent("publisher-1", protocol)
    
    # Start background message processing
    protocol.start_background_processing(interval=0.05)
    logger.info("Started background message processing")
    
    # Start the publisher
    publisher.start_publishing(interval=0.2, duration=5.0)
    
    # Wait for publisher to finish and messages to be processed
    time.sleep(7.0)  # Extra time to ensure all messages are processed
    
    # Display statistics
    logger.info("\n----- Pub/Sub Statistics -----")
    logger.info(f"Total messages published: {publisher.publish_count}")
    logger.info(f"Successful deliveries: {publisher.successful_deliveries}")
    logger.info(f"Failed deliveries: {publisher.failed_deliveries}")
    
    logger.info("\n----- Subscriber Statistics -----")
    for subscriber in subscribers:
        stats = subscriber.get_stats()
        logger.info(f"Agent {stats['agent_id']}: received {stats['total_received']} messages")
        logger.info(f"  By topic: {stats['by_topic']}")
        logger.info(f"  Avg processing time: {stats['avg_processing_time']:.3f}s")
    
    logger.info("\n----- Topic Statistics -----")
    for topic in protocol.list_topics():
        logger.info(f"Topic: {topic['name']} - Subscribers: {topic['subscribers']}")
        logger.info(f"  Description: {topic['description']}")
    
    # Stop background processing
    protocol.stop_background_processing()
    logger.info("Stopped background message processing")
    logger.info("Pub/sub example completed successfully.")
    
    return {
        "protocol": protocol,
        "publisher": publisher,
        "subscribers": subscribers
    }


def save_example_results(result, filename):
    """Save the results of an example run to a JSON file."""
    # Extract serializable data
    serializable_data = {
        "campaign_id": result.get("campaign_id", ""),
        "campaign_manager": {
            "id": result.get("campaign_manager", {}).id if hasattr(result.get("campaign_manager", {}), "id") else "",
            "name": result.get("campaign_manager", {}).name if hasattr(result.get("campaign_manager", {}), "name") else "",
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
    
    # Add special data for pub/sub example
    if "publisher" in result:
        publisher = result.get("publisher")
        serializable_data["publisher"] = {
            "id": publisher.id,
            "name": publisher.name,
            "publish_count": publisher.publish_count,
            "successful_deliveries": publisher.successful_deliveries,
            "failed_deliveries": publisher.failed_deliveries
        }
        
        serializable_data["subscribers"] = []
        for subscriber in result.get("subscribers", []):
            stats = subscriber.get_stats()
            serializable_data["subscribers"].append(stats)
    
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
        print("4. Enhanced Pub/Sub Messaging Example")
        print("5. Run All Examples")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-5): ")
        
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
            result = pubsub_example()
            save_example_results(result, "pubsub_example_results.json")
        elif choice == "5":
            print("\nRunning all examples sequentially...\n")
            result1 = basic_example()
            result2 = ad_agency_example()
            result3 = custom_example()
            result4 = pubsub_example()
            save_example_results(result1, "basic_example_results.json")
            save_example_results(result2, "ad_agency_example_results.json")
            save_example_results(result3, "custom_example_results.json")
            save_example_results(result4, "pubsub_example_results.json")
            print("\nAll examples completed successfully.")
        elif choice == "0":
            print("\nExiting demonstration.\n")
            break
        else:
            print("\nInvalid choice. Please enter a number between 0 and 5.")
    
    print("Thank you for exploring the agent communication protocol.")
    print("="*50)