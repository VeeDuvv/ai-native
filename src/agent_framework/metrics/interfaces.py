"""
Interfaces for the metrics and measurement system.

This module defines the interfaces for collecting, storing, and retrieving
metrics across the agent framework.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime


class MetricValue:
    """
    Represents a metric value with metadata.
    
    This class encapsulates a metric value along with its timestamp and
    any additional metadata.
    """
    
    def __init__(self, value: Union[int, float, str, bool], 
                timestamp: Optional[datetime] = None,
                metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a metric value.
        
        Args:
            value: The actual metric value (number, string, or boolean)
            timestamp: When the metric was collected (defaults to now)
            metadata: Additional context about the metric value
        """
        self.value = value
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert the metric value to a dictionary."""
        return {
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class MetricsCollector(ABC):
    """
    Interface for collecting metrics.
    
    This interface defines methods for recording metrics from various
    parts of the system.
    """
    
    @abstractmethod
    def record_counter(self, name: str, value: int = 1, 
                      tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a counter metric.
        
        Args:
            name: The name of the metric
            value: The increment value (defaults to 1)
            tags: Additional tags for the metric
        """
        pass
    
    @abstractmethod
    def record_gauge(self, name: str, value: float,
                    tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a gauge metric.
        
        Args:
            name: The name of the metric
            value: The current value
            tags: Additional tags for the metric
        """
        pass
    
    @abstractmethod
    def record_histogram(self, name: str, value: float,
                        tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a histogram metric.
        
        Args:
            name: The name of the metric
            value: The value to add to the histogram
            tags: Additional tags for the metric
        """
        pass
    
    @abstractmethod
    def start_timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> Any:
        """
        Start a timer for measuring durations.
        
        Args:
            name: The name of the timer
            tags: Additional tags for the timer
            
        Returns:
            A timer context that can be used to stop the timer
        """
        pass
    
    @abstractmethod
    def record_event(self, name: str, value: Any = None,
                   tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record an event metric.
        
        Args:
            name: The name of the event
            value: The event value or description
            tags: Additional tags for the event
        """
        pass


class MetricsStorage(ABC):
    """
    Interface for storing and retrieving metrics.
    
    This interface defines methods for persisting metrics and retrieving
    them for analysis and reporting.
    """
    
    @abstractmethod
    def store_metric(self, name: str, value: MetricValue,
                    tags: Optional[Dict[str, str]] = None) -> None:
        """
        Store a metric value.
        
        Args:
            name: The name of the metric
            value: The metric value object
            tags: Additional tags for the metric
        """
        pass
    
    @abstractmethod
    def get_metrics(self, name: str, start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  tags: Optional[Dict[str, str]] = None) -> List[MetricValue]:
        """
        Retrieve metric values.
        
        Args:
            name: The name of the metric
            start_time: The start of the time range (inclusive)
            end_time: The end of the time range (inclusive)
            tags: Filter metrics by tags
            
        Returns:
            A list of metric values matching the criteria
        """
        pass
    
    @abstractmethod
    def get_metrics_summary(self, name: str, start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None,
                         tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Get a summary of metric values.
        
        Args:
            name: The name of the metric
            start_time: The start of the time range (inclusive)
            end_time: The end of the time range (inclusive)
            tags: Filter metrics by tags
            
        Returns:
            A dictionary with summary statistics (min, max, avg, count, etc.)
        """
        pass


class MetricsReporter(ABC):
    """
    Interface for reporting metrics.
    
    This interface defines methods for generating reports and visualizations
    from collected metrics.
    """
    
    @abstractmethod
    def generate_report(self, metrics: List[str], start_time: datetime,
                      end_time: datetime, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Generate a report for specified metrics.
        
        Args:
            metrics: The list of metric names to include
            start_time: The start of the time range (inclusive)
            end_time: The end of the time range (inclusive)
            tags: Filter metrics by tags
            
        Returns:
            A dictionary with the report data
        """
        pass
    
    @abstractmethod
    def export_metrics(self, metrics: List[str], start_time: datetime,
                     end_time: datetime, format: str,
                     tags: Optional[Dict[str, str]] = None) -> bytes:
        """
        Export metrics in a specified format.
        
        Args:
            metrics: The list of metric names to include
            start_time: The start of the time range (inclusive)
            end_time: The end of the time range (inclusive)
            format: The export format (csv, json, etc.)
            tags: Filter metrics by tags
            
        Returns:
            The exported data as bytes
        """
        pass


class ObservableAgent(ABC):
    """
    Interface for agents that can be observed.
    
    This interface defines methods for agents to expose their internal
    state and metrics for monitoring and debugging.
    """
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, MetricValue]:
        """
        Get the current metrics for the agent.
        
        Returns:
            A dictionary of metric names and their current values
        """
        pass
    
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current state of the agent.
        
        Returns:
            A dictionary representing the agent's internal state
        """
        pass
    
    @abstractmethod
    def get_health(self) -> Dict[str, Any]:
        """
        Get the health status of the agent.
        
        Returns:
            A dictionary with health information (status, issues, etc.)
        """
        pass