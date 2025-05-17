"""
Tests for the metrics collectors.
"""

import pytest
import time
from datetime import datetime

from src.agent_framework.metrics.collectors import (
    InMemoryMetricsCollector,
    AgentMetricsCollector,
    TimerContext
)


@pytest.fixture
def memory_collector():
    """Create a fresh in-memory metrics collector."""
    return InMemoryMetricsCollector()


@pytest.fixture
def agent_collector():
    """Create a fresh agent metrics collector."""
    return AgentMetricsCollector("test-agent-1")


def test_record_counter(memory_collector):
    """Test recording counter metrics."""
    # Record a counter
    memory_collector.record_counter("test_counter", 1)
    
    # Check the value
    assert memory_collector.get_counter("test_counter") == 1
    
    # Increment the counter
    memory_collector.record_counter("test_counter", 2)
    
    # Check the updated value
    assert memory_collector.get_counter("test_counter") == 3
    
    # Test with tags
    memory_collector.record_counter("test_counter", 5, {"tag1": "value1"})
    
    # The original counter should be unchanged
    assert memory_collector.get_counter("test_counter") == 3
    
    # The tagged counter should have the new value
    assert memory_collector.get_counter("test_counter", {"tag1": "value1"}) == 5


def test_record_gauge(memory_collector):
    """Test recording gauge metrics."""
    # Record a gauge
    memory_collector.record_gauge("test_gauge", 42.5)
    
    # Check the value
    assert memory_collector.get_gauge("test_gauge") == 42.5
    
    # Update the gauge
    memory_collector.record_gauge("test_gauge", 100)
    
    # Check the updated value
    assert memory_collector.get_gauge("test_gauge") == 100
    
    # Test with tags
    memory_collector.record_gauge("test_gauge", 200, {"tag1": "value1"})
    
    # The original gauge should be unchanged
    assert memory_collector.get_gauge("test_gauge") == 100
    
    # The tagged gauge should have the new value
    assert memory_collector.get_gauge("test_gauge", {"tag1": "value1"}) == 200


def test_record_histogram(memory_collector):
    """Test recording histogram metrics."""
    # Record histogram values
    memory_collector.record_histogram("test_histogram", 10)
    memory_collector.record_histogram("test_histogram", 20)
    memory_collector.record_histogram("test_histogram", 30)
    
    # Check the values
    values = memory_collector.get_histogram_values("test_histogram")
    assert len(values) == 3
    assert 10 in values
    assert 20 in values
    assert 30 in values
    
    # Get histogram stats
    stats = memory_collector.get_histogram_stats("test_histogram")
    
    assert stats["count"] == 3
    assert stats["min"] == 10
    assert stats["max"] == 30
    assert stats["mean"] == 20
    assert stats["p50"] == 20
    
    # Test with tags
    memory_collector.record_histogram("test_histogram", 100, {"tag1": "value1"})
    memory_collector.record_histogram("test_histogram", 200, {"tag1": "value1"})
    
    # The original histogram should be unchanged
    assert len(memory_collector.get_histogram_values("test_histogram")) == 3
    
    # The tagged histogram should have the new values
    tagged_values = memory_collector.get_histogram_values("test_histogram", {"tag1": "value1"})
    assert len(tagged_values) == 2
    assert 100 in tagged_values
    assert 200 in tagged_values


def test_start_timer(memory_collector):
    """Test timing operations."""
    # Use timer as context manager
    with memory_collector.start_timer("test_timer"):
        time.sleep(0.1)
    
    # Check that a histogram value was recorded
    values = memory_collector.get_histogram_values("test_timer_duration")
    assert len(values) == 1
    assert values[0] >= 0.1  # Timing should be at least the sleep duration
    
    # Test with tags
    with memory_collector.start_timer("test_timer", {"tag1": "value1"}):
        time.sleep(0.1)
    
    # The original timer should be unchanged
    assert len(memory_collector.get_histogram_values("test_timer_duration")) == 1
    
    # The tagged timer should have a new value
    tagged_values = memory_collector.get_histogram_values("test_timer_duration", {"tag1": "value1"})
    assert len(tagged_values) == 1


def test_record_event(memory_collector):
    """Test recording event metrics."""
    # Record an event
    memory_collector.record_event("test_event", "something happened")
    
    # Check the events
    events = memory_collector.get_events("test_event")
    assert len(events) == 1
    assert events[0]["name"] == "test_event"
    assert events[0]["value"] == "something happened"
    
    # Record another event with tags
    memory_collector.record_event("test_event", "another thing", {"tag1": "value1"})
    
    # Check all events
    all_events = memory_collector.get_events("test_event")
    assert len(all_events) == 2
    
    # Filter by tags
    tagged_events = memory_collector.get_events("test_event", tags={"tag1": "value1"})
    assert len(tagged_events) == 1
    assert tagged_events[0]["value"] == "another thing"


def test_agent_metrics_collector(agent_collector):
    """Test the agent-specific metrics collector."""
    # Record a message sent
    agent_collector.record_message_sent("TEST_TYPE", "recipient-1", "conv-1")
    
    # Check counters
    assert agent_collector.get_counter("messages_sent", {"agent_id": "test-agent-1"}) == 1
    
    # Check events
    events = agent_collector.get_events("message_sent")
    assert len(events) == 1
    assert events[0]["tags"]["agent_id"] == "test-agent-1"
    assert events[0]["tags"]["message_type"] == "TEST_TYPE"
    assert events[0]["tags"]["recipient_id"] == "recipient-1"
    
    # Record a message received
    agent_collector.record_message_received("RESPONSE_TYPE", "sender-1", "conv-1")
    
    # Check counters
    assert agent_collector.get_counter("messages_received", {"agent_id": "test-agent-1"}) == 1
    
    # Record task started and completed
    agent_collector.record_task_started("test_task", "task-1")
    
    # Check active tasks
    assert agent_collector.get_gauge("active_tasks", {"agent_id": "test-agent-1"}) == 1
    
    # Complete the task (success)
    agent_collector.record_task_completed("test_task", "task-1", 0.5, True)
    
    # Check counters and gauges
    assert agent_collector.get_counter("tasks_completed", {"agent_id": "test-agent-1"}) == 1
    assert agent_collector.get_counter("tasks_succeeded", {"agent_id": "test-agent-1"}) == 1
    assert agent_collector.get_gauge("active_tasks", {"agent_id": "test-agent-1"}) == 0
    
    # Check histogram
    duration_values = agent_collector.get_histogram_values(
        "task_duration",
        {"agent_id": "test-agent-1", "task_type": "test_task", "success": "true"}
    )
    assert len(duration_values) == 1
    assert duration_values[0] == 0.5


def test_measure_task(agent_collector):
    """Test the task measurement context manager."""
    # Use the context manager to measure a task
    with agent_collector.measure_task("test_task", "task-1"):
        # Simulate work
        time.sleep(0.1)
    
    # Check counters
    assert agent_collector.get_counter("tasks_started", {"agent_id": "test-agent-1"}) == 1
    assert agent_collector.get_counter("tasks_completed", {"agent_id": "test-agent-1"}) == 1
    assert agent_collector.get_counter("tasks_succeeded", {"agent_id": "test-agent-1"}) == 1
    
    # Check task duration
    duration_values = agent_collector.get_histogram_values(
        "task_duration",
        {"agent_id": "test-agent-1", "task_type": "test_task"}
    )
    assert len(duration_values) == 1
    assert duration_values[0] >= 0.1
    
    # Test with exception
    try:
        with agent_collector.measure_task("test_task", "task-2"):
            # Simulate work that fails
            time.sleep(0.1)
            raise ValueError("Test exception")
    except ValueError:
        pass
    
    # Check failure counter
    assert agent_collector.get_counter("tasks_failed", {"agent_id": "test-agent-1"}) == 1
    
    # Check task duration with failure tag
    failure_duration_values = agent_collector.get_histogram_values(
        "task_duration",
        {"agent_id": "test-agent-1", "task_type": "test_task", "success": "false"}
    )
    assert len(failure_duration_values) == 1
    assert failure_duration_values[0] >= 0.1


def test_record_campaign_metric(agent_collector):
    """Test recording campaign-specific metrics."""
    # Record a campaign metric
    agent_collector.record_campaign_metric("campaign-1", "impressions", 1000)
    
    # Check counter
    assert agent_collector.get_counter("campaign_impressions", 
                                    {"agent_id": "test-agent-1", "campaign_id": "campaign-1"}) == 1000
    
    # Record another metric
    agent_collector.record_campaign_metric("campaign-1", "clicks", 50)
    
    # Check counter
    assert agent_collector.get_counter("campaign_clicks", 
                                    {"agent_id": "test-agent-1", "campaign_id": "campaign-1"}) == 50
    
    # Record a gauge metric
    agent_collector.record_campaign_metric("campaign-1", "ctr", 0.05, {"is_gauge": "true"})
    
    # Check gauge
    assert agent_collector.get_gauge("campaign_ctr", 
                                   {"agent_id": "test-agent-1", "campaign_id": "campaign-1", "is_gauge": "true"}) == 0.05