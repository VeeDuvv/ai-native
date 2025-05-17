"""
Metrics and measurement system for the agent framework.

This package provides components for collecting, storing, and reporting
metrics about agent activity and campaign performance.
"""

from .interfaces import (
    MetricValue, 
    MetricsCollector, 
    MetricsStorage, 
    MetricsReporter,
    ObservableAgent
)

from .collectors import (
    InMemoryMetricsCollector,
    AgentMetricsCollector,
    TimerContext
)

from .storage import (
    InMemoryMetricsStorage,
    SQLiteMetricsStorage
)

from .reporting import (
    BasicMetricsReporter,
    CampaignPerformanceReporter
)

from .integration import (
    ObservableCommunicatingAgent,
    ObservableCommunicationProtocol,
    CampaignMetricsTracker
)

from .observability import (
    StandardAlert,
    InMemoryAlertManager,
    StandardAgentObserver,
    BasicSystemMonitor
)

__all__ = [
    # Interfaces
    'MetricValue',
    'MetricsCollector',
    'MetricsStorage',
    'MetricsReporter',
    'ObservableAgent',
    
    # Collectors
    'InMemoryMetricsCollector',
    'AgentMetricsCollector',
    'TimerContext',
    
    # Storage
    'InMemoryMetricsStorage',
    'SQLiteMetricsStorage',
    
    # Reporting
    'BasicMetricsReporter',
    'CampaignPerformanceReporter',
    
    # Integration
    'ObservableCommunicatingAgent',
    'ObservableCommunicationProtocol',
    'CampaignMetricsTracker',
    
    # Observability
    'StandardAlert',
    'InMemoryAlertManager',
    'StandardAgentObserver',
    'BasicSystemMonitor'
]