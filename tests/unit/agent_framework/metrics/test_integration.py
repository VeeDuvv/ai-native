"""
Tests for the metrics integration with the communication protocol.
"""

import pytest
import time
from datetime import datetime

from src.agent_framework.core.message import MessageType
from src.agent_framework.metrics.collectors import InMemoryMetricsCollector, AgentMetricsCollector
from src.agent_framework.metrics.storage import InMemoryMetricsStorage
from src.agent_framework.metrics.integration import (
    ObservableCommunicatingAgent,
    ObservableCommunicationProtocol,
    CampaignMetricsTracker
)


# Define test message types
class TestMessageType(MessageType):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"


@pytest.fixture
def metrics_storage():
    """Create a fresh metrics storage instance."""
    return InMemoryMetricsStorage()


@pytest.fixture
def protocol_metrics(metrics_storage):
    """Create a metrics collector for the protocol."""
    return InMemoryMetricsCollector(metrics_storage)


@pytest.fixture
def observable_protocol(protocol_metrics):
    """Create an observable communication protocol."""
    return ObservableCommunicationProtocol(protocol_metrics)


@pytest.fixture
def agent_metrics(metrics_storage):
    """Create metrics collectors for agents."""
    return {
        "agent_a": AgentMetricsCollector("agent-a", metrics_storage),
        "agent_b": AgentMetricsCollector("agent-b", metrics_storage)
    }


@pytest.fixture
def observable_agents(observable_protocol, agent_metrics):
    """Create observable communicating agents."""
    agent_a = ObservableCommunicatingAgent(
        "agent-a", "Test Agent A", observable_protocol, agent_metrics["agent_a"]
    )
    
    agent_b = ObservableCommunicatingAgent(
        "agent-b", "Test Agent B", observable_protocol, agent_metrics["agent_b"]
    )
    
    return {
        "agent_a": agent_a,
        "agent_b": agent_b
    }


def test_observable_agent_send_message(observable_agents, protocol_metrics):
    """Test sending messages with an observable agent."""
    agent_a = observable_agents["agent_a"]
    agent_b = observable_agents["agent_b"]
    
    # Send a message
    agent_a.send_message(
        recipient_id=agent_b.id,
        message_type=TestMessageType.REQUEST,
        content={"test": "data"}
    )
    
    # Check message metrics
    assert protocol_metrics.get_counter("messages_queued") == 1
    assert agent_metrics["agent_a"].get_counter("messages_sent", {"agent_id": "agent-a"}) == 1
    
    # Process messages
    observable_protocol = agent_a._protocol
    observable_protocol.process_message_queue()
    
    # Check processed message metrics
    assert protocol_metrics.get_counter("messages_processed") == 1
    assert agent_metrics["agent_b"].get_counter("messages_received", {"agent_id": "agent-b"}) == 1


def test_observable_agent_health(observable_agents):
    """Test getting health information from an observable agent."""
    agent_a = observable_agents["agent_a"]
    
    # Get health information
    health = agent_a.get_health()
    
    # Check health structure
    assert "status" in health
    assert "metrics" in health
    assert "issues" in health
    assert "last_updated" in health
    
    # Status should be healthy initially
    assert health["status"] == "healthy"
    
    # Metrics should include basic agent stats
    assert "active_tasks" in health["metrics"]
    assert "received_messages" in health["metrics"]
    assert "sent_messages" in health["metrics"]


def test_observable_agent_state(observable_agents):
    """Test getting state information from an observable agent."""
    agent_a = observable_agents["agent_a"]
    
    # Get state information
    state = agent_a.get_state()
    
    # Check state structure
    assert state["id"] == "agent-a"
    assert state["name"] == "Test Agent A"
    assert "received_messages_count" in state
    assert "sent_messages_count" in state
    assert "message_handlers" in state


def test_observable_protocol_metrics(observable_protocol):
    """Test getting metrics from the observable protocol."""
    # Get protocol metrics
    metrics = observable_protocol.get_protocol_metrics()
    
    # Check metrics structure
    assert "registered_agents" in metrics
    assert "active_conversations" in metrics
    assert "message_queue_size" in metrics
    
    # Register some agents to see metrics change
    class DummyAgent:
        def __init__(self, agent_id):
            self.id = agent_id
    
    observable_protocol.register_agent(DummyAgent("dummy-1"))
    observable_protocol.register_agent(DummyAgent("dummy-2"))
    
    # Get updated metrics
    updated_metrics = observable_protocol.get_protocol_metrics()
    
    # Check that registered_agents was updated
    assert updated_metrics["registered_agents"] == 2


def test_campaign_metrics_tracker(metrics_storage):
    """Test the campaign metrics tracker."""
    # Create a collector and tracker
    collector = AgentMetricsCollector("test-agent", metrics_storage)
    tracker = CampaignMetricsTracker("campaign-1", collector)
    
    # Record various metrics
    tracker.record_impression(1000)
    tracker.record_click(50)
    tracker.record_conversion(5, 500)  # 5 conversions worth $500
    tracker.record_spend(200)
    tracker.record_revenue(1000)
    
    # Get campaign metrics
    metrics = tracker.get_campaign_metrics()
    
    # Check metric values
    assert metrics["impressions"] == 1000
    assert metrics["clicks"] == 50
    assert metrics["conversions"] == 5
    assert metrics["spend"] == 200
    assert metrics["revenue"] == 1000
    
    # Check calculated metrics
    assert metrics["ctr"] == 0.05  # 50/1000
    assert metrics["cvr"] == 0.1   # 5/50
    assert metrics["cpa"] == 40    # 200/5
    assert metrics["roas"] == 5    # 1000/200
    
    # Record a custom metric
    tracker.record_custom_metric("video_views", 75)
    
    # Check the custom metric
    assert collector.get_counter("campaign_video_views", 
                              {"agent_id": "test-agent", "campaign_id": "campaign-1"}) == 75