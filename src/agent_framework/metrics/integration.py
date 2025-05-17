"""
Integration of the metrics system with other framework components.

This module provides classes and functions to integrate the metrics
system with the communication protocol, agents, and other components.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..core.interfaces import CommunicatingAgent, ObservableAgent
from ..core.message import Message, MessageType
from ..communication.protocol import CommunicatingAgentImpl, StandardCommunicationProtocol
from .interfaces import MetricsCollector, MetricsStorage, MetricValue
from .collectors import AgentMetricsCollector


class ObservableCommunicatingAgent(CommunicatingAgentImpl, ObservableAgent):
    """
    A communicating agent with observability capabilities.
    
    This class extends the standard communicating agent with metrics
    collection and observability features.
    """
    
    def __init__(self, agent_id: str, name: str, protocol: StandardCommunicationProtocol,
                metrics_collector: Optional[MetricsCollector] = None):
        """
        Initialize the observable communicating agent.
        
        Args:
            agent_id: The ID of the agent
            name: The name of the agent
            protocol: The communication protocol to use
            metrics_collector: Optional metrics collector
        """
        super().__init__(agent_id, name, protocol)
        
        # Set up metrics collector if provided, otherwise create a new one
        self.metrics_collector = metrics_collector or AgentMetricsCollector(agent_id)
        self.logger = logging.getLogger(f"agent.{agent_id}")
    
    def send_message(self, recipient_id: str, message_type: MessageType, 
                    content: Dict[str, Any], conversation_id: Optional[str] = None,
                    priority=None, ttl: Optional[int] = None) -> str:
        """
        Send a message with metrics tracking.
        
        Records metrics about the sent message before delegating to the
        parent implementation.
        """
        # Record metrics about the message being sent
        if isinstance(self.metrics_collector, AgentMetricsCollector):
            self.metrics_collector.record_message_sent(
                str(message_type), recipient_id, conversation_id
            )
        else:
            self.metrics_collector.record_counter(
                "messages_sent", 1,
                {
                    "agent_id": self.id,
                    "message_type": str(message_type),
                    "recipient_id": recipient_id
                }
            )
        
        # Call the parent implementation to send the message
        return super().send_message(recipient_id, message_type, content, 
                                  conversation_id, priority, ttl)
    
    def receive_message(self, message: Message) -> bool:
        """
        Receive a message with metrics tracking.
        
        Records metrics about the received message before delegating to the
        parent implementation.
        """
        # Record metrics about the message being received
        if isinstance(self.metrics_collector, AgentMetricsCollector):
            self.metrics_collector.record_message_received(
                str(message.message_type), message.sender_id, message.conversation_id
            )
        else:
            self.metrics_collector.record_counter(
                "messages_received", 1,
                {
                    "agent_id": self.id,
                    "message_type": str(message.message_type),
                    "sender_id": message.sender_id
                }
            )
        
        # Call the parent implementation to process the message
        return super().receive_message(message)
    
    def get_metrics(self) -> Dict[str, MetricValue]:
        """Get the current metrics for the agent."""
        # Get metrics from the collector
        if isinstance(self.metrics_collector, AgentMetricsCollector):
            return {
                "messages_sent": MetricValue(
                    self.metrics_collector.get_counter("messages_sent", {"agent_id": self.id})
                ),
                "messages_received": MetricValue(
                    self.metrics_collector.get_counter("messages_received", {"agent_id": self.id})
                ),
                "active_tasks": MetricValue(
                    self.metrics_collector.get_gauge("active_tasks", {"agent_id": self.id})
                )
            }
        else:
            return {}
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the agent."""
        return {
            "id": self.id,
            "name": self.name,
            "received_messages_count": len(self.received_messages),
            "sent_messages_count": len(self.sent_messages),
            "message_handlers": list(self.message_handlers.keys())
        }
    
    def get_health(self) -> Dict[str, Any]:
        """Get the health status of the agent."""
        # Collect any relevant health metrics
        active_tasks = 0
        if isinstance(self.metrics_collector, AgentMetricsCollector):
            active_tasks = self.metrics_collector.get_gauge("active_tasks", {"agent_id": self.id})
        
        # Determine health status based on metrics
        status = "healthy"
        issues = []
        
        # Example health check: too many active tasks might indicate a problem
        if active_tasks > 100:
            status = "warning"
            issues.append("High number of active tasks")
        
        # Example health check: large message backlog might indicate a problem
        if len(self.received_messages) > 1000:
            status = "warning"
            issues.append("Large message backlog")
        
        return {
            "status": status,
            "last_updated": datetime.now().isoformat(),
            "issues": issues,
            "metrics": {
                "active_tasks": active_tasks,
                "received_messages": len(self.received_messages),
                "sent_messages": len(self.sent_messages)
            }
        }


class ObservableCommunicationProtocol(StandardCommunicationProtocol):
    """
    A communication protocol with observability capabilities.
    
    This class extends the standard communication protocol with metrics
    collection and performance tracking.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        """
        Initialize the observable communication protocol.
        
        Args:
            metrics_collector: Optional metrics collector
        """
        super().__init__()
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger("protocol.observable")
    
    def register_agent(self, agent: CommunicatingAgent) -> None:
        """Register an agent with metrics tracking."""
        super().register_agent(agent)
        
        if self.metrics_collector:
            self.metrics_collector.record_counter(
                "agents_registered", 1,
                {"agent_id": agent.id}
            )
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent with metrics tracking."""
        super().unregister_agent(agent_id)
        
        if self.metrics_collector:
            self.metrics_collector.record_counter(
                "agents_unregistered", 1,
                {"agent_id": agent_id}
            )
    
    def send_message(self, message: Message) -> str:
        """Send a message with metrics tracking."""
        if self.metrics_collector:
            with self.metrics_collector.start_timer("message_queuing_time", 
                                                  {"sender_id": message.sender_id}):
                message_id = super().send_message(message)
            
            self.metrics_collector.record_counter(
                "messages_queued", 1,
                {
                    "sender_id": message.sender_id,
                    "recipient_id": message.recipient_id,
                    "message_type": str(message.message_type)
                }
            )
            
            # Track queue size
            self.metrics_collector.record_gauge(
                "message_queue_size",
                len(self.message_broker.message_queue),
                {}
            )
            
            return message_id
        else:
            return super().send_message(message)
    
    def process_message_queue(self) -> int:
        """Process the message queue with metrics tracking."""
        if self.metrics_collector:
            queue_size_before = len(self.message_broker.message_queue)
            
            with self.metrics_collector.start_timer("message_processing_time"):
                processed_count = super().process_message_queue()
            
            queue_size_after = len(self.message_broker.message_queue)
            
            self.metrics_collector.record_counter(
                "messages_processed", processed_count
            )
            
            self.metrics_collector.record_gauge(
                "message_queue_size",
                queue_size_after,
                {}
            )
            
            # If we processed messages but the queue isn't empty, it may indicate
            # that some messages couldn't be delivered
            if processed_count > 0 and queue_size_after > 0:
                self.metrics_collector.record_counter(
                    "undeliverable_messages",
                    queue_size_after,
                    {}
                )
            
            return processed_count
        else:
            return super().process_message_queue()
    
    def get_protocol_metrics(self) -> Dict[str, Any]:
        """Get metrics about the protocol's operation."""
        metrics = {
            "registered_agents": len(self.registered_agents),
            "active_conversations": len(self.conversations),
            "message_queue_size": len(self.message_broker.message_queue)
        }
        
        if self.metrics_collector:
            metrics.update({
                "messages_queued": self.metrics_collector.get_counter("messages_queued"),
                "messages_processed": self.metrics_collector.get_counter("messages_processed"),
                "undeliverable_messages": self.metrics_collector.get_counter("undeliverable_messages")
            })
        
        return metrics


class CampaignMetricsTracker:
    """
    Tracker for campaign performance metrics.
    
    This class provides methods for recording and retrieving metrics
    about advertising campaign performance.
    """
    
    def __init__(self, campaign_id: str, metrics_collector: MetricsCollector):
        """
        Initialize the campaign metrics tracker.
        
        Args:
            campaign_id: The ID of the campaign being tracked
            metrics_collector: The metrics collector to use
        """
        self.campaign_id = campaign_id
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger(f"campaign.{campaign_id}.metrics")
    
    def record_impression(self, count: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """Record campaign impressions."""
        metric_tags = {"campaign_id": self.campaign_id}
        if tags:
            metric_tags.update(tags)
        
        self.metrics_collector.record_counter("campaign_impressions", count, metric_tags)
        self.logger.debug(f"Recorded {count} impressions for campaign {self.campaign_id}")
    
    def record_click(self, count: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """Record campaign clicks."""
        metric_tags = {"campaign_id": self.campaign_id}
        if tags:
            metric_tags.update(tags)
        
        self.metrics_collector.record_counter("campaign_clicks", count, metric_tags)
        self.logger.debug(f"Recorded {count} clicks for campaign {self.campaign_id}")
    
    def record_conversion(self, count: int = 1, value: Optional[float] = None, 
                        tags: Optional[Dict[str, str]] = None) -> None:
        """Record campaign conversions."""
        metric_tags = {"campaign_id": self.campaign_id}
        if tags:
            metric_tags.update(tags)
        
        self.metrics_collector.record_counter("campaign_conversions", count, metric_tags)
        
        if value is not None:
            self.metrics_collector.record_counter("campaign_conversion_value", value, metric_tags)
        
        self.logger.debug(f"Recorded {count} conversions for campaign {self.campaign_id}")
    
    def record_spend(self, amount: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record campaign spend."""
        metric_tags = {"campaign_id": self.campaign_id}
        if tags:
            metric_tags.update(tags)
        
        self.metrics_collector.record_counter("campaign_spend", amount, metric_tags)
        self.logger.debug(f"Recorded ${amount:.2f} spend for campaign {self.campaign_id}")
    
    def record_revenue(self, amount: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Record campaign revenue."""
        metric_tags = {"campaign_id": self.campaign_id}
        if tags:
            metric_tags.update(tags)
        
        self.metrics_collector.record_counter("campaign_revenue", amount, metric_tags)
        self.logger.debug(f"Recorded ${amount:.2f} revenue for campaign {self.campaign_id}")
    
    def record_custom_metric(self, name: str, value: Any, 
                          is_counter: bool = True,
                          tags: Optional[Dict[str, str]] = None) -> None:
        """Record a custom campaign metric."""
        metric_tags = {"campaign_id": self.campaign_id}
        if tags:
            metric_tags.update(tags)
        
        metric_name = f"campaign_{name}"
        
        if is_counter and isinstance(value, (int, float)):
            self.metrics_collector.record_counter(metric_name, value, metric_tags)
        else:
            self.metrics_collector.record_gauge(metric_name, value, metric_tags)
        
        self.logger.debug(f"Recorded custom metric {name}={value} for campaign {self.campaign_id}")
    
    def get_campaign_metrics(self) -> Dict[str, Any]:
        """Get a summary of the campaign's metrics."""
        metrics = {}
        
        for metric_name in [
            "impressions", "clicks", "conversions", 
            "spend", "revenue", "conversion_value"
        ]:
            counter_name = f"campaign_{metric_name}"
            value = self.metrics_collector.get_counter(
                counter_name, {"campaign_id": self.campaign_id}
            )
            metrics[metric_name] = value
        
        # Calculate derived metrics
        if metrics["impressions"] > 0:
            metrics["ctr"] = metrics["clicks"] / metrics["impressions"]
        else:
            metrics["ctr"] = 0
        
        if metrics["clicks"] > 0:
            metrics["cvr"] = metrics["conversions"] / metrics["clicks"]
        else:
            metrics["cvr"] = 0
        
        if metrics["spend"] > 0:
            metrics["cpa"] = metrics["spend"] / metrics["conversions"] if metrics["conversions"] > 0 else 0
            metrics["roas"] = metrics["revenue"] / metrics["spend"]
        else:
            metrics["cpa"] = 0
            metrics["roas"] = 0
        
        return metrics