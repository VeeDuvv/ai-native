"""
Implementations of metrics collectors.

This module provides concrete implementations of the metrics collection
interfaces for monitoring agent activity.
"""

import time
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from contextlib import contextmanager

from .interfaces import MetricsCollector, MetricValue, MetricsStorage


class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, collector: MetricsCollector, name: str, 
                tags: Optional[Dict[str, str]] = None):
        """
        Initialize a timer context.
        
        Args:
            collector: The metrics collector to record the timing
            name: The name of the timer
            tags: Additional tags for the timer
        """
        self.collector = collector
        self.name = name
        self.tags = tags or {}
        self.start_time = None
    
    def __enter__(self):
        """Start the timer when entering the context."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Record the elapsed time when exiting the context."""
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.collector.record_histogram(f"{self.name}_duration", elapsed, self.tags)


class InMemoryMetricsCollector(MetricsCollector):
    """
    In-memory implementation of a metrics collector.
    
    This implementation stores metrics in memory and can forward them
    to a metrics storage backend.
    """
    
    def __init__(self, storage: Optional[MetricsStorage] = None):
        """
        Initialize the metrics collector.
        
        Args:
            storage: Optional metrics storage backend
        """
        self.storage = storage
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
        self.events = []
        self.logger = logging.getLogger("metrics.collector")
    
    def record_counter(self, name: str, value: int = 1, 
                     tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a counter metric.
        
        Counters are cumulative and increment-only.
        """
        tags = tags or {}
        key = (name, tuple(sorted(tags.items())))
        
        if key in self.counters:
            self.counters[key] += value
        else:
            self.counters[key] = value
        
        metric_value = MetricValue(self.counters[key], metadata={"type": "counter"})
        
        if self.storage:
            self.storage.store_metric(name, metric_value, tags)
        
        self.logger.debug(f"Counter {name} = {self.counters[key]} {tags}")
    
    def record_gauge(self, name: str, value: float,
                   tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a gauge metric.
        
        Gauges represent a current value that can go up or down.
        """
        tags = tags or {}
        key = (name, tuple(sorted(tags.items())))
        
        self.gauges[key] = value
        
        metric_value = MetricValue(value, metadata={"type": "gauge"})
        
        if self.storage:
            self.storage.store_metric(name, metric_value, tags)
        
        self.logger.debug(f"Gauge {name} = {value} {tags}")
    
    def record_histogram(self, name: str, value: float,
                       tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a histogram metric.
        
        Histograms track the distribution of values.
        """
        tags = tags or {}
        key = (name, tuple(sorted(tags.items())))
        
        if key not in self.histograms:
            self.histograms[key] = []
        
        self.histograms[key].append(value)
        
        metric_value = MetricValue(value, metadata={"type": "histogram"})
        
        if self.storage:
            self.storage.store_metric(name, metric_value, tags)
        
        self.logger.debug(f"Histogram {name} = {value} {tags}")
    
    def start_timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> TimerContext:
        """
        Start a timer for measuring durations.
        
        Returns a context manager that will record the duration when exited.
        """
        return TimerContext(self, name, tags)
    
    def record_event(self, name: str, value: Any = None,
                  tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record an event metric.
        
        Events represent discrete occurrences.
        """
        tags = tags or {}
        timestamp = datetime.now()
        
        event = {
            "name": name,
            "value": value,
            "tags": tags,
            "timestamp": timestamp
        }
        
        self.events.append(event)
        
        metric_value = MetricValue(
            str(value) if value is not None else "occurred", 
            timestamp, 
            {"type": "event"}
        )
        
        if self.storage:
            self.storage.store_metric(name, metric_value, tags)
        
        self.logger.debug(f"Event {name} = {value} {tags}")
    
    def get_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> int:
        """Get the current value of a counter."""
        tags = tags or {}
        key = (name, tuple(sorted(tags.items())))
        return self.counters.get(key, 0)
    
    def get_gauge(self, name: str, tags: Optional[Dict[str, str]] = None) -> float:
        """Get the current value of a gauge."""
        tags = tags or {}
        key = (name, tuple(sorted(tags.items())))
        return self.gauges.get(key, 0.0)
    
    def get_histogram_values(self, name: str, tags: Optional[Dict[str, str]] = None) -> List[float]:
        """Get all values recorded for a histogram."""
        tags = tags or {}
        key = (name, tuple(sorted(tags.items())))
        return self.histograms.get(key, [])
    
    def get_histogram_stats(self, name: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """Get summary statistics for a histogram."""
        values = self.get_histogram_values(name, tags)
        
        if not values:
            return {
                "count": 0,
                "min": 0,
                "max": 0,
                "mean": 0,
                "p50": 0,
                "p90": 0,
                "p95": 0,
                "p99": 0
            }
        
        values.sort()
        count = len(values)
        
        return {
            "count": count,
            "min": values[0],
            "max": values[-1],
            "mean": sum(values) / count,
            "p50": values[count // 2],
            "p90": values[int(count * 0.9)],
            "p95": values[int(count * 0.95)],
            "p99": values[int(count * 0.99)]
        }
    
    def get_events(self, name: Optional[str] = None, 
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None,
                 tags: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Get events matching the specified criteria."""
        filtered_events = self.events
        
        if name:
            filtered_events = [e for e in filtered_events if e["name"] == name]
        
        if start_time:
            filtered_events = [e for e in filtered_events if e["timestamp"] >= start_time]
        
        if end_time:
            filtered_events = [e for e in filtered_events if e["timestamp"] <= end_time]
        
        if tags:
            filtered_events = [
                e for e in filtered_events 
                if all(e["tags"].get(k) == v for k, v in tags.items())
            ]
        
        return filtered_events
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
        self.events = []


class AgentMetricsCollector(InMemoryMetricsCollector):
    """
    Metrics collector specialized for agent monitoring.
    
    This collector adds agent-specific metrics and convenience methods.
    """
    
    def __init__(self, agent_id: str, storage: Optional[MetricsStorage] = None):
        """
        Initialize the agent metrics collector.
        
        Args:
            agent_id: The ID of the agent being monitored
            storage: Optional metrics storage backend
        """
        super().__init__(storage)
        self.agent_id = agent_id
        self.base_tags = {"agent_id": agent_id}
    
    def record_message_sent(self, message_type: str, recipient_id: str, 
                          conversation_id: Optional[str] = None) -> None:
        """Record a message sent by the agent."""
        tags = {
            **self.base_tags,
            "message_type": message_type,
            "recipient_id": recipient_id
        }
        
        if conversation_id:
            tags["conversation_id"] = conversation_id
        
        self.record_counter("messages_sent", 1, tags)
        self.record_event("message_sent", {
            "message_type": message_type,
            "recipient_id": recipient_id,
            "conversation_id": conversation_id
        }, tags)
    
    def record_message_received(self, message_type: str, sender_id: str,
                             conversation_id: Optional[str] = None) -> None:
        """Record a message received by the agent."""
        tags = {
            **self.base_tags,
            "message_type": message_type,
            "sender_id": sender_id
        }
        
        if conversation_id:
            tags["conversation_id"] = conversation_id
        
        self.record_counter("messages_received", 1, tags)
        self.record_event("message_received", {
            "message_type": message_type,
            "sender_id": sender_id,
            "conversation_id": conversation_id
        }, tags)
    
    def record_task_started(self, task_type: str, task_id: str) -> None:
        """Record a task started by the agent."""
        tags = {
            **self.base_tags,
            "task_type": task_type,
            "task_id": task_id
        }
        
        self.record_counter("tasks_started", 1, tags)
        self.record_gauge("active_tasks", self.get_counter("tasks_started", {"agent_id": self.agent_id}) -
                      self.get_counter("tasks_completed", {"agent_id": self.agent_id}),
                      {"agent_id": self.agent_id})
        
        self.record_event("task_started", {
            "task_type": task_type,
            "task_id": task_id
        }, tags)
    
    def record_task_completed(self, task_type: str, task_id: str, 
                           duration: float, success: bool) -> None:
        """Record a task completed by the agent."""
        tags = {
            **self.base_tags,
            "task_type": task_type,
            "task_id": task_id,
            "success": "true" if success else "false"
        }
        
        self.record_counter("tasks_completed", 1, tags)
        self.record_histogram("task_duration", duration, tags)
        
        if success:
            self.record_counter("tasks_succeeded", 1, tags)
        else:
            self.record_counter("tasks_failed", 1, tags)
        
        self.record_gauge("active_tasks", self.get_counter("tasks_started", {"agent_id": self.agent_id}) -
                      self.get_counter("tasks_completed", {"agent_id": self.agent_id}),
                      {"agent_id": self.agent_id})
        
        self.record_event("task_completed", {
            "task_type": task_type,
            "task_id": task_id,
            "duration": duration,
            "success": success
        }, tags)
    
    def measure_task(self, task_type: str, task_id: str):
        """
        Context manager for measuring task execution.
        
        Example:
            ```
            with agent_metrics.measure_task("process_campaign", campaign_id):
                # Do work
                process_campaign(campaign_id)
            ```
        """
        class TaskContext:
            def __init__(self, collector, task_type, task_id):
                self.collector = collector
                self.task_type = task_type
                self.task_id = task_id
                self.start_time = None
                self.success = True
            
            def __enter__(self):
                self.start_time = time.time()
                self.collector.record_task_started(self.task_type, self.task_id)
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                duration = time.time() - self.start_time
                self.success = exc_type is None
                self.collector.record_task_completed(
                    self.task_type, self.task_id, duration, self.success
                )
                return False  # Don't suppress exceptions
        
        return TaskContext(self, task_type, task_id)
    
    def record_campaign_metric(self, campaign_id: str, metric_name: str, 
                            value: Union[int, float], tags: Optional[Dict[str, str]] = None) -> None:
        """Record a campaign-specific metric."""
        metric_tags = {
            **self.base_tags,
            "campaign_id": campaign_id
        }
        
        if tags:
            metric_tags.update(tags)
        
        if isinstance(value, int):
            self.record_counter(f"campaign_{metric_name}", value, metric_tags)
        else:
            self.record_gauge(f"campaign_{metric_name}", value, metric_tags)
        
        self.record_event(f"campaign_{metric_name}_recorded", {
            "campaign_id": campaign_id,
            "metric_name": metric_name,
            "value": value
        }, metric_tags)