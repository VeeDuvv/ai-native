# Agent Framework Metrics and Observability

This module provides a comprehensive metrics and observability system for the agent framework, enabling monitoring, measurement, and alerting for agent communications and performance.

## Overview

The metrics and observability system includes:

1. **Metrics Collection**: Track agent activity, message flow, and task performance
2. **Metrics Storage**: Persist metrics for historical analysis and reporting
3. **Performance Reporting**: Generate reports and visualizations from metrics
4. **Observability**: Monitor agent health and system status
5. **Alerting**: Detect and notify about issues in the system

## Key Components

### Metrics Collection

The metrics collection system provides:

- Counter metrics for cumulative values (messages sent, tasks completed)
- Gauge metrics for current values (active tasks, queue size)
- Histogram metrics for value distributions (task duration, response time)
- Event recording for discrete occurrences
- Timing measurements for performance tracking

```python
# Example: Using the metrics collector
from src.agent_framework.metrics.collectors import AgentMetricsCollector

# Create a collector for an agent
collector = AgentMetricsCollector("agent-1")

# Record counter metrics
collector.record_counter("messages_sent", 1, {"message_type": "REQUEST"})

# Record gauge metrics
collector.record_gauge("queue_depth", 5)

# Measure task duration
with collector.measure_task("process_campaign", "campaign-123"):
    # The task being measured
    process_campaign("campaign-123")
```

### Metrics Storage

The metrics storage system provides:

- In-memory storage for testing and small-scale deployments
- SQLite storage for persistent metrics with efficient querying
- Query capabilities for retrieving and analyzing metrics

```python
# Example: Using metrics storage
from src.agent_framework.metrics.storage import SQLiteMetricsStorage
from src.agent_framework.metrics.collectors import AgentMetricsCollector

# Create a storage backend
storage = SQLiteMetricsStorage("metrics.db")

# Create a collector that uses the storage
collector = AgentMetricsCollector("agent-1", storage)

# Record metrics (they will be stored in the database)
collector.record_counter("messages_processed", 1)

# Query metrics from storage
from datetime import datetime, timedelta
end_time = datetime.now()
start_time = end_time - timedelta(hours=1)

metrics = storage.get_metrics("messages_processed", start_time, end_time)
```

### Campaign Performance Metrics

The system includes specialized support for tracking advertising campaign performance:

- Impression, click, conversion tracking
- Spend and revenue tracking
- Performance metrics (CTR, CVR, CPA, ROAS)
- Campaign-specific reporting

```python
# Example: Tracking campaign metrics
from src.agent_framework.metrics.integration import CampaignMetricsTracker

# Create a tracker for a campaign
tracker = CampaignMetricsTracker("campaign-123", collector)

# Record various campaign metrics
tracker.record_impression(1000)
tracker.record_click(50)
tracker.record_conversion(5, 500)  # 5 conversions worth $500
tracker.record_spend(200)
tracker.record_revenue(1000)

# Get campaign performance metrics
metrics = tracker.get_campaign_metrics()
print(f"CTR: {metrics['ctr']:.2%}")
print(f"CVR: {metrics['cvr']:.2%}")
print(f"CPA: ${metrics['cpa']:.2f}")
print(f"ROAS: {metrics['roas']:.2f}x")
```

### Metrics Reporting

The reporting system provides:

- Generation of metric summaries and reports
- Export capabilities for different formats (JSON, CSV)
- Campaign performance reporting with derived metrics
- Time series analysis for trend identification

```python
# Example: Generating reports
from src.agent_framework.metrics.reporting import CampaignPerformanceReporter
from datetime import datetime, timedelta

# Create a reporter
reporter = CampaignPerformanceReporter(storage)

# Generate a campaign report
end_time = datetime.now()
start_time = end_time - timedelta(days=7)

report = reporter.generate_campaign_report("campaign-123", start_time, end_time)

# Export metrics as JSON
metrics_json = reporter.export_metrics(
    ["campaign_impressions", "campaign_clicks"],
    start_time, end_time, "json",
    {"campaign_id": "campaign-123"}
)
```

### Observable Agents

The system includes integration with the agent communication protocol, providing observable agents that:

- Track message flow and processing
- Measure task execution time and success rate
- Expose health and state information
- Enable monitoring and alerting

```python
# Example: Creating observable agents
from src.agent_framework.metrics.integration import ObservableCommunicatingAgent
from src.agent_framework.metrics.collectors import AgentMetricsCollector

# Create an observable agent
agent = ObservableCommunicatingAgent(
    "agent-1", "Example Agent", protocol, AgentMetricsCollector("agent-1")
)

# Get agent health information
health = agent.get_health()
print(f"Agent health: {health['status']}")

# Get agent metrics
metrics = agent.get_metrics()
print(f"Messages sent: {metrics['messages_sent'].value}")
print(f"Active tasks: {metrics['active_tasks'].value}")
```

### System Monitoring and Alerting

The observability system provides:

- Agent observers for collecting observations
- System monitoring for overall health tracking
- Alert generation and management
- Health status determination and issue detection

```python
# Example: System monitoring and alerting
from src.agent_framework.metrics.observability import (
    InMemoryAlertManager,
    StandardAgentObserver,
    BasicSystemMonitor
)

# Set up the observability stack
alert_manager = InMemoryAlertManager()
agent_observer = StandardAgentObserver(alert_manager)
system_monitor = BasicSystemMonitor()

# Register components
system_monitor.register_observer(agent_observer)
system_monitor.register_alert_manager(alert_manager)

# Monitor agents
system_monitor.monitor_entity(agent)

# Check for health issues and generate alerts
system_monitor.check_for_alerts()

# Get any alerts that were generated
alerts = alert_manager.get_alerts()
for alert in alerts:
    print(f"Alert: [{alert.get_severity()}] {alert.get_message()}")
```

## Usage Examples

The module includes several example scripts demonstrating how to use the metrics and observability system:

1. **examples.py**: Basic examples of using metrics collection and reporting
2. **observability_example.py**: Complete example of the observability system

Run these examples to see the system in action:

```bash
python src/agent_framework/metrics/examples.py
python src/agent_framework/metrics/observability_example.py
```

## Integration with Communication Protocol

The metrics system integrates with the agent communication protocol to provide:

- Message flow tracking
- Task performance measurement
- Health monitoring
- System-wide observability

```python
# Example: Setting up an observable protocol
from src.agent_framework.metrics.integration import ObservableCommunicationProtocol
from src.agent_framework.metrics.collectors import InMemoryMetricsCollector

# Create a protocol with metrics
protocol = ObservableCommunicationProtocol(InMemoryMetricsCollector())

# Use the protocol with observable agents
agent1 = ObservableCommunicatingAgent("agent-1", "Agent 1", protocol, AgentMetricsCollector("agent-1"))
agent2 = ObservableCommunicatingAgent("agent-2", "Agent 2", protocol, AgentMetricsCollector("agent-2"))

# Send messages between agents
agent1.send_message(agent2.id, MessageType.REQUEST, {"action": "do_something"})

# Process messages with metrics tracking
protocol.process_message_queue()

# Get protocol metrics
metrics = protocol.get_protocol_metrics()
print(f"Messages queued: {metrics['messages_queued']}")
print(f"Messages processed: {metrics['messages_processed']}")
```

## Testing

The module includes comprehensive unit tests:

- `test_collectors.py`: Tests for metrics collection
- `test_integration.py`: Tests for integration with the communication protocol

Run the tests using pytest:

```bash
pytest tests/unit/agent_framework/metrics/
```

## Future Enhancements

Planned enhancements for the metrics and observability system:

1. **Distributed Metrics**: Support for collecting metrics across distributed nodes
2. **Real-time Dashboards**: Web-based visualization of metrics and health status
3. **Anomaly Detection**: Automatic detection of unusual patterns in metrics
4. **Predictive Alerting**: Alerting based on trend prediction
5. **Integration with External Systems**: Export metrics to systems like Prometheus, Grafana