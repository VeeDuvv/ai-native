"""
Examples demonstrating the metrics and measurement framework.

This module provides concrete examples of how to use the metrics system
with the agent communication protocol.
"""

import os
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any

from ..core.message import MessageType
from ..communication.protocol import StandardCommunicationProtocol
from ..communication.examples import AdAgencyMessageType

from .interfaces import MetricsCollector, MetricsStorage
from .collectors import InMemoryMetricsCollector, AgentMetricsCollector
from .storage import InMemoryMetricsStorage, SQLiteMetricsStorage
from .reporting import BasicMetricsReporter, CampaignPerformanceReporter
from .integration import (
    ObservableCommunicatingAgent,
    ObservableCommunicationProtocol,
    CampaignMetricsTracker
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ObservableCampaignManager(ObservableCommunicatingAgent):
    """Example campaign manager with observability features."""
    
    def __init__(self, agent_id: str, protocol, metrics_collector: MetricsCollector = None):
        super().__init__(agent_id, "Observable Campaign Manager", protocol, metrics_collector)
        self.active_campaigns = {}
        
        # Register message handlers
        self.register_message_handler(
            AdAgencyMessageType.CAMPAIGN_REQUEST, 
            self._handle_campaign_request
        )
        self.register_message_handler(
            AdAgencyMessageType.CREATIVE_DELIVERY,
            self._handle_creative_delivery
        )
    
    def create_campaign(self, creative_agent_id: str, campaign_details: Dict[str, Any]) -> str:
        """Create a new campaign with metrics tracking."""
        campaign_id = campaign_details.get("id", f"campaign-{len(self.active_campaigns) + 1}")
        
        # Start tracking metrics for this task
        with self.metrics_collector.measure_task("create_campaign", campaign_id):
            # Store campaign details
            self.active_campaigns[campaign_id] = campaign_details
            
            # Send message to creative agent
            self.send_message(
                recipient_id=creative_agent_id,
                message_type=AdAgencyMessageType.CAMPAIGN_REQUEST,
                content={
                    "campaign_id": campaign_id,
                    "campaign_name": campaign_details.get("name"),
                    "campaign_brief": campaign_details.get("brief")
                }
            )
        
        return campaign_id
    
    def _handle_campaign_request(self, message: Dict[str, Any]) -> None:
        """Handle campaign request with metrics tracking."""
        campaign_id = message.content.get("campaign_id")
        
        # Track this operation
        with self.metrics_collector.measure_task("handle_campaign_request", campaign_id):
            logger.info(f"Received campaign request for {campaign_id}")
            
            # Record campaign metrics
            campaign_tracker = CampaignMetricsTracker(campaign_id, self.metrics_collector)
            campaign_tracker.record_custom_metric("request_received", 1)
    
    def _handle_creative_delivery(self, message: Dict[str, Any]) -> None:
        """Handle creative delivery with metrics tracking."""
        campaign_id = message.content.get("campaign_id")
        
        # Track this operation
        with self.metrics_collector.measure_task("handle_creative_delivery", campaign_id):
            logger.info(f"Received creative assets for {campaign_id}")
            
            # Record campaign metrics
            campaign_tracker = CampaignMetricsTracker(campaign_id, self.metrics_collector)
            campaign_tracker.record_custom_metric("creative_received", 1)


class ObservableCreativeAgent(ObservableCommunicatingAgent):
    """Example creative agent with observability features."""
    
    def __init__(self, agent_id: str, protocol, metrics_collector: MetricsCollector = None):
        super().__init__(agent_id, "Observable Creative Agent", protocol, metrics_collector)
        
        # Register message handlers
        self.register_message_handler(
            AdAgencyMessageType.CAMPAIGN_REQUEST, 
            self._handle_campaign_request
        )
    
    def _handle_campaign_request(self, message: Dict[str, Any]) -> None:
        """Handle campaign request with metrics tracking."""
        campaign_id = message.content.get("campaign_id")
        
        # Track this operation
        with self.metrics_collector.measure_task("handle_campaign_request", campaign_id):
            logger.info(f"Processing creative request for {campaign_id}")
            
            # Simulate work
            time.sleep(0.1)
            
            # Send creative assets back
            self.send_message(
                recipient_id=message.sender_id,
                message_type=AdAgencyMessageType.CREATIVE_DELIVERY,
                content={
                    "campaign_id": campaign_id,
                    "assets": [
                        {"type": "headline", "content": "Generated headline"},
                        {"type": "body", "content": "Generated body copy"}
                    ]
                },
                conversation_id=message.conversation_id
            )


def run_observable_agents_example():
    """Run an example with observable agents."""
    # Create metrics storage
    storage = InMemoryMetricsStorage()
    
    # Create protocol with metrics
    protocol_metrics = InMemoryMetricsCollector(storage)
    protocol = ObservableCommunicationProtocol(protocol_metrics)
    
    # Create agents with metrics
    campaign_manager_metrics = AgentMetricsCollector("campaign-mgr", storage)
    campaign_manager = ObservableCampaignManager("campaign-mgr", protocol, campaign_manager_metrics)
    
    creative_agent_metrics = AgentMetricsCollector("creative-agent", storage)
    creative_agent = ObservableCreativeAgent("creative-agent", protocol, creative_agent_metrics)
    
    # Create campaigns
    for i in range(5):
        campaign_details = {
            "id": f"campaign-{i+1}",
            "name": f"Test Campaign {i+1}",
            "brief": f"Test brief for campaign {i+1}"
        }
        
        campaign_manager.create_campaign("creative-agent", campaign_details)
    
    # Process messages
    processed = protocol.process_message_queue()
    logger.info(f"Processed {processed} messages")
    
    # Process responses
    processed = protocol.process_message_queue()
    logger.info(f"Processed {processed} response messages")
    
    # Get agent metrics
    campaign_manager_health = campaign_manager.get_health()
    creative_agent_health = creative_agent.get_health()
    
    logger.info(f"Campaign Manager Health: {campaign_manager_health['status']}")
    logger.info(f"Creative Agent Health: {creative_agent_health['status']}")
    
    # Generate a basic report
    reporter = BasicMetricsReporter(storage)
    metrics_list = [
        "messages_sent",
        "messages_received",
        "tasks_started",
        "tasks_completed"
    ]
    
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    
    report = reporter.generate_report(metrics_list, start_time, end_time)
    
    logger.info("Metrics Report:")
    for metric_name, metric_data in report["metrics"].items():
        logger.info(f"{metric_name}: count={metric_data['count']}, last={metric_data['last']}")
    
    return {
        "protocol": protocol,
        "campaign_manager": campaign_manager,
        "creative_agent": creative_agent,
        "storage": storage,
        "reporter": reporter
    }


def run_campaign_metrics_example():
    """Run an example with campaign performance metrics."""
    # Create metrics storage with SQLite
    db_path = "campaign_metrics.db"
    storage = SQLiteMetricsStorage(db_path)
    
    # Create a campaign metrics tracker
    collector = AgentMetricsCollector("performance-agent", storage)
    campaign_tracker = CampaignMetricsTracker("campaign-perf-1", collector)
    
    # Record campaign performance metrics
    campaign_tracker.record_impression(1000)
    campaign_tracker.record_click(50)
    campaign_tracker.record_conversion(5, 500)
    campaign_tracker.record_spend(200)
    campaign_tracker.record_revenue(1000)
    
    # Wait a bit and record more metrics
    time.sleep(0.5)
    
    campaign_tracker.record_impression(2000)
    campaign_tracker.record_click(100)
    campaign_tracker.record_conversion(10, 1000)
    campaign_tracker.record_spend(400)
    campaign_tracker.record_revenue(2000)
    
    # Generate a campaign performance report
    reporter = CampaignPerformanceReporter(storage)
    
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)
    
    report = reporter.generate_campaign_report("campaign-perf-1", start_time, end_time)
    
    logger.info("Campaign Performance Report:")
    logger.info(f"Impressions: {report['metrics']['campaign_impressions']['last']}")
    logger.info(f"Clicks: {report['metrics']['campaign_clicks']['last']}")
    logger.info(f"Conversions: {report['metrics']['campaign_conversions']['last']}")
    logger.info(f"Spend: ${report['metrics']['campaign_spend']['last']}")
    logger.info(f"Revenue: ${report['metrics']['campaign_revenue']['last']}")
    logger.info(f"CTR: {report['performance']['ctr'] * 100:.2f}%")
    logger.info(f"CVR: {report['performance']['cvr'] * 100:.2f}%")
    logger.info(f"CPA: ${report['performance']['cpa']:.2f}")
    logger.info(f"ROAS: {report['performance']['roas']:.2f}x")
    
    return {
        "storage": storage,
        "tracker": campaign_tracker,
        "reporter": reporter,
        "report": report
    }


if __name__ == "__main__":
    logger.info("Running observable agents example...")
    run_observable_agents_example()
    
    logger.info("\nRunning campaign metrics example...")
    run_campaign_metrics_example()