# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps us watch how our AI helpers are doing their jobs. It's like having 
# a security camera system that shows us when things are working well or if something 
# strange is happening.

# High School Explanation:
# This module implements the observability framework for monitoring agent behavior.
# It provides systems for real-time metric collection, anomaly detection, dashboards,
# and alerts to ensure proper agent operation and early detection of issues.

"""
Concrete implementations of observability interfaces.

This module provides implementations of the observability interfaces
for monitoring and alerting on agent behavior and performance.
"""

import logging
import time
import json
import statistics
import threading
import uuid
import math
from typing import Dict, List, Any, Optional, Set, Union, Tuple, Callable
from datetime import datetime, timedelta
from uuid import uuid4
from collections import defaultdict, deque

from ..core.observability import (
    Observable,
    ObservableAgent,
    Observer,
    AgentObserver,
    Alert,
    AlertManager,
    SystemMonitor
)
from .collectors import InMemoryMetricsCollector, AgentMetricsCollector
from .storage import InMemoryMetricsStorage, SQLiteMetricsStorage


# Set up logging
logger = logging.getLogger("agent_framework.observability")


class StandardAlert(Alert):
    """Standard implementation of an alert."""
    
    def __init__(self, entity_id: str, severity: str, message: str,
                context: Optional[Dict[str, Any]] = None):
        """
        Initialize a standard alert.
        
        Args:
            entity_id: The ID of the entity that triggered the alert
            severity: The severity level (info, warning, error, critical)
            message: The alert message
            context: Additional context for the alert
        """
        self.id = str(uuid4())
        self.entity_id = entity_id
        self.severity = severity
        self.message = message
        self.context = context or {}
        self.timestamp = datetime.now()
        self.acknowledged = False
        self.resolved = False
        self.resolution_message = None
        self.resolution_timestamp = None
    
    def get_severity(self) -> str:
        """Get the severity of the alert."""
        return self.severity
    
    def get_message(self) -> str:
        """Get the alert message."""
        return self.message
    
    def get_timestamp(self) -> datetime:
        """Get the alert timestamp."""
        return self.timestamp
    
    def get_entity_id(self) -> str:
        """Get the ID of the entity that triggered the alert."""
        return self.entity_id
    
    def get_context(self) -> Dict[str, Any]:
        """Get additional context for the alert."""
        return self.context
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the alert to a dictionary."""
        result = {
            "id": self.id,
            "severity": self.severity,
            "message": self.message,
            "entity_id": self.entity_id,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "resolved": self.resolved
        }
        
        if self.resolved and self.resolution_timestamp:
            result["resolution_timestamp"] = self.resolution_timestamp.isoformat()
            result["resolution_message"] = self.resolution_message
        
        return result


class InMemoryAlertManager(AlertManager):
    """In-memory implementation of an alert manager."""
    
    def __init__(self):
        """Initialize the alert manager."""
        self.alerts = {}
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        self.logger = logging.getLogger("alerts.manager")
    
    def add_alert(self, alert: Alert) -> None:
        """
        Add an alert to the manager.
        
        Args:
            alert: The alert to add
        """
        alert_id = getattr(alert, "id", str(uuid4()))
        self.alerts[alert_id] = alert
        
        # Log the alert
        self.logger.log(
            logging.CRITICAL if alert.get_severity() == "critical" else
            logging.ERROR if alert.get_severity() == "error" else
            logging.WARNING if alert.get_severity() == "warning" else
            logging.INFO,
            f"Alert {alert_id}: [{alert.get_severity()}] {alert.get_message()} - {alert.get_entity_id()}"
        )
        
        # Call any registered callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")
    
    def get_alerts(self, severity: Optional[str] = None,
                 entity_id: Optional[str] = None,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None) -> List[Alert]:
        """
        Get alerts matching specified criteria.
        
        Args:
            severity: Optional filter for severity level
            entity_id: Optional filter for entity ID
            start_time: Optional filter for start time
            end_time: Optional filter for end time
            
        Returns:
            A list of alerts matching the criteria
        """
        filtered_alerts = list(self.alerts.values())
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a.get_severity() == severity]
        
        if entity_id:
            filtered_alerts = [a for a in filtered_alerts if a.get_entity_id() == entity_id]
        
        if start_time:
            filtered_alerts = [a for a in filtered_alerts if a.get_timestamp() >= start_time]
        
        if end_time:
            filtered_alerts = [a for a in filtered_alerts if a.get_timestamp() <= end_time]
        
        # Sort by timestamp, newest first
        filtered_alerts.sort(key=lambda a: a.get_timestamp(), reverse=True)
        
        return filtered_alerts
    
    def acknowledge_alert(self, alert_id: str) -> None:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: The ID of the alert to acknowledge
        """
        if alert_id in self.alerts:
            if hasattr(self.alerts[alert_id], "acknowledge"):
                self.alerts[alert_id].acknowledge()
            self.logger.info(f"Alert {alert_id} acknowledged")
    
    def resolve_alert(self, alert_id: str, resolution_message: Optional[str] = None) -> None:
        """
        Resolve an alert.
        
        Args:
            alert_id: The ID of the alert to resolve
            resolution_message: Optional message describing the resolution
        """
        if alert_id in self.alerts:
            if hasattr(self.alerts[alert_id], "resolve"):
                self.alerts[alert_id].resolve(resolution_message)
            elif hasattr(self.alerts[alert_id], "resolved"):
                self.alerts[alert_id].resolved = True
                if hasattr(self.alerts[alert_id], "resolution_message"):
                    self.alerts[alert_id].resolution_message = resolution_message
                if hasattr(self.alerts[alert_id], "resolution_timestamp"):
                    self.alerts[alert_id].resolution_timestamp = datetime.now()
            self.logger.info(f"Alert {alert_id} resolved")
    
    def register_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """
        Register a callback to be called when an alert is added.
        
        Args:
            callback: The callback function
        """
        self.alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """
        Remove a previously registered callback.
        
        Args:
            callback: The callback function to remove
        """
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)


class AnomalyDetector:
    """Detects anomalies in agent metrics."""
    
    def __init__(self, alert_manager: AlertManager):
        """
        Initialize the anomaly detector.
        
        Args:
            alert_manager: The alert manager to send anomalies to
        """
        self.alert_manager = alert_manager
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.thresholds: Dict[str, Dict[str, float]] = {}
        self.logger = logging.getLogger("agent_framework.anomaly")
    
    def set_threshold(self, metric_name: str, critical: Optional[float] = None,
                    error: Optional[float] = None, warning: Optional[float] = None,
                    direction: str = "above") -> None:
        """
        Set threshold values for a metric.
        
        Args:
            metric_name: The name of the metric
            critical: Critical threshold value
            error: Error threshold value
            warning: Warning threshold value
            direction: "above" if values above threshold are anomalous,
                       "below" if values below threshold are anomalous
        """
        if direction not in ["above", "below"]:
            raise ValueError('Direction must be "above" or "below"')
        
        self.thresholds[metric_name] = {
            "critical": critical,
            "error": error,
            "warning": warning,
            "direction": direction
        }
    
    def set_statistical_thresholds(self, metric_name: str, std_dev_warning: float = 2.0,
                                std_dev_error: float = 3.0, std_dev_critical: float = 4.0) -> None:
        """
        Set statistical thresholds for a metric.
        
        Args:
            metric_name: The name of the metric
            std_dev_warning: Number of standard deviations for warning threshold
            std_dev_error: Number of standard deviations for error threshold
            std_dev_critical: Number of standard deviations for critical threshold
        """
        self.thresholds[metric_name] = {
            "std_dev_warning": std_dev_warning,
            "std_dev_error": std_dev_error,
            "std_dev_critical": std_dev_critical,
            "statistical": True
        }
    
    def add_metric_value(self, metric_name: str, value: Union[int, float], entity_id: str,
                       tags: Optional[Dict[str, str]] = None) -> None:
        """
        Add a metric value to be evaluated for anomalies.
        
        Args:
            metric_name: The name of the metric
            value: The metric value
            entity_id: The ID of the entity being monitored
            tags: Additional tags for the metric
        """
        # Create a key that includes tags
        key = metric_name
        if tags:
            sorted_tags = sorted((k, v) for k, v in tags.items())
            key = f"{metric_name}:{json.dumps(sorted_tags)}"
        
        # Store the value in history
        self.metrics_history[key].append(value)
        
        # Check for anomalies
        if metric_name in self.thresholds:
            self._check_anomaly(metric_name, key, value, entity_id, tags or {})
    
    def _check_anomaly(self, metric_name: str, key: str, value: Union[int, float],
                     entity_id: str, tags: Dict[str, str]) -> None:
        """
        Check if a metric value is anomalous.
        
        Args:
            metric_name: The name of the metric
            key: The history key for the metric
            value: The metric value
            entity_id: The ID of the entity being monitored
            tags: Additional tags for the metric
        """
        threshold = self.thresholds[metric_name]
        
        # Statistical thresholds
        if threshold.get("statistical", False):
            self._check_statistical_anomaly(metric_name, key, value, entity_id, tags, threshold)
            return
        
        # Fixed thresholds
        direction = threshold.get("direction", "above")
        
        for level, threshold_value in [
            ("critical", threshold.get("critical")),
            ("error", threshold.get("error")),
            ("warning", threshold.get("warning"))
        ]:
            if threshold_value is None:
                continue
            
            is_anomaly = (
                direction == "above" and value > threshold_value or
                direction == "below" and value < threshold_value
            )
            
            if is_anomaly:
                self._report_anomaly(level, metric_name, value, threshold_value, 
                                   direction, entity_id, tags)
                break  # Only report the highest severity
    
    def _check_statistical_anomaly(self, metric_name: str, key: str, value: Union[int, float],
                                entity_id: str, tags: Dict[str, str], 
                                threshold: Dict[str, Any]) -> None:
        """
        Check if a metric value is statistically anomalous.
        
        Args:
            metric_name: The name of the metric
            key: The history key for the metric
            value: The metric value
            entity_id: The ID of the entity being monitored
            tags: Additional tags for the metric
            threshold: The threshold settings
        """
        history = self.metrics_history[key]
        
        # Need enough data points for statistical analysis
        if len(history) < 10:
            return
        
        try:
            mean = statistics.mean(history)
            stdev = statistics.stdev(history)
            
            # Avoid division by zero
            if stdev == 0:
                return
            
            z_score = abs((value - mean) / stdev)
            
            for level, std_dev in [
                ("critical", threshold.get("std_dev_critical")),
                ("error", threshold.get("std_dev_error")),
                ("warning", threshold.get("std_dev_warning"))
            ]:
                if std_dev is None:
                    continue
                
                if z_score > std_dev:
                    self._report_statistical_anomaly(level, metric_name, value, 
                                                 mean, stdev, z_score, entity_id, tags)
                    break  # Only report the highest severity
        except Exception as e:
            self.logger.error(f"Error calculating statistical anomaly: {e}")
    
    def _report_anomaly(self, severity: str, metric_name: str, value: Union[int, float],
                      threshold_value: float, direction: str, entity_id: str,
                      tags: Dict[str, str]) -> None:
        """
        Report a threshold anomaly.
        
        Args:
            severity: The severity level
            metric_name: The name of the metric
            value: The metric value
            threshold_value: The threshold value
            direction: The threshold direction
            entity_id: The ID of the entity being monitored
            tags: Additional tags for the metric
        """
        message = (
            f"Metric {metric_name} is {severity}: value is {value}, which is "
            f"{direction} threshold of {threshold_value}"
        )
        
        context = {
            "metric_name": metric_name,
            "value": value,
            "threshold": threshold_value,
            "direction": direction,
            "tags": tags
        }
        
        alert = StandardAlert(entity_id, severity, message, context)
        self.alert_manager.add_alert(alert)
    
    def _report_statistical_anomaly(self, severity: str, metric_name: str, 
                                 value: Union[int, float], mean: float, stdev: float,
                                 z_score: float, entity_id: str, 
                                 tags: Dict[str, str]) -> None:
        """
        Report a statistical anomaly.
        
        Args:
            severity: The severity level
            metric_name: The name of the metric
            value: The metric value
            mean: The mean value
            stdev: The standard deviation
            z_score: The z-score of the value
            entity_id: The ID of the entity being monitored
            tags: Additional tags for the metric
        """
        message = (
            f"Metric {metric_name} is {severity}: value {value} is {z_score:.2f} "
            f"standard deviations from mean {mean:.2f} (std dev {stdev:.2f})"
        )
        
        context = {
            "metric_name": metric_name,
            "value": value,
            "mean": mean,
            "stdev": stdev,
            "z_score": z_score,
            "tags": tags
        }
        
        alert = StandardAlert(entity_id, severity, message, context)
        self.alert_manager.add_alert(alert)


class Dashboard:
    """Base class for agent dashboards."""
    
    def __init__(self, title: str, description: str):
        """
        Initialize a dashboard.
        
        Args:
            title: The dashboard title
            description: The dashboard description
        """
        self.id = str(uuid4())
        self.title = title
        self.description = description
        self.panels: List[Dict[str, Any]] = []
        self.last_updated = datetime.now()
    
    def add_panel(self, panel_type: str, title: str, description: str,
                metrics: List[str], panel_id: Optional[str] = None,
                options: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a panel to the dashboard.
        
        Args:
            panel_type: The type of panel (line, bar, gauge, table, etc.)
            title: The panel title
            description: The panel description
            metrics: The metrics to display in the panel
            panel_id: Optional panel ID (generated if not provided)
            options: Additional panel options
            
        Returns:
            The panel ID
        """
        panel_id = panel_id or str(uuid4())
        
        panel = {
            "id": panel_id,
            "type": panel_type,
            "title": title,
            "description": description,
            "metrics": metrics,
            "options": options or {}
        }
        
        self.panels.append(panel)
        self.last_updated = datetime.now()
        
        return panel_id
    
    def update_panel(self, panel_id: str, **kwargs) -> None:
        """
        Update a panel in the dashboard.
        
        Args:
            panel_id: The ID of the panel to update
            **kwargs: The panel attributes to update
        """
        for panel in self.panels:
            if panel["id"] == panel_id:
                panel.update(kwargs)
                self.last_updated = datetime.now()
                break
    
    def remove_panel(self, panel_id: str) -> None:
        """
        Remove a panel from the dashboard.
        
        Args:
            panel_id: The ID of the panel to remove
        """
        self.panels = [p for p in self.panels if p["id"] != panel_id]
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the dashboard to a dictionary.
        
        Returns:
            A dictionary representation of the dashboard
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "panels": self.panels,
            "last_updated": self.last_updated.isoformat()
        }


class DashboardManager:
    """Manages agent dashboards."""
    
    def __init__(self, metrics_collector: InMemoryMetricsCollector,
               alert_manager: Optional[AlertManager] = None):
        """
        Initialize the dashboard manager.
        
        Args:
            metrics_collector: The metrics collector to get data from
            alert_manager: Optional alert manager for dashboard alerts
        """
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager
        self.dashboards: Dict[str, Dashboard] = {}
        self.logger = logging.getLogger("agent_framework.dashboards")
    
    def create_dashboard(self, title: str, description: str) -> Dashboard:
        """
        Create a new dashboard.
        
        Args:
            title: The dashboard title
            description: The dashboard description
            
        Returns:
            The new dashboard
        """
        dashboard = Dashboard(title, description)
        self.dashboards[dashboard.id] = dashboard
        return dashboard
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """
        Get a dashboard by ID.
        
        Args:
            dashboard_id: The dashboard ID
            
        Returns:
            The dashboard or None if not found
        """
        return self.dashboards.get(dashboard_id)
    
    def list_dashboards(self) -> List[Dict[str, Any]]:
        """
        List all dashboards.
        
        Returns:
            A list of dashboard summaries
        """
        return [
            {
                "id": d.id,
                "title": d.title,
                "description": d.description,
                "panel_count": len(d.panels),
                "last_updated": d.last_updated.isoformat()
            }
            for d in self.dashboards.values()
        ]
    
    def delete_dashboard(self, dashboard_id: str) -> bool:
        """
        Delete a dashboard.
        
        Args:
            dashboard_id: The dashboard ID
            
        Returns:
            True if the dashboard was deleted, False otherwise
        """
        if dashboard_id in self.dashboards:
            del self.dashboards[dashboard_id]
            return True
        return False
    
    def get_panel_data(self, dashboard_id: str, panel_id: str,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get data for a dashboard panel.
        
        Args:
            dashboard_id: The dashboard ID
            panel_id: The panel ID
            start_time: Optional start time for data range
            end_time: Optional end time for data range
            
        Returns:
            The panel data
        """
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            raise ValueError(f"Dashboard not found: {dashboard_id}")
        
        panel = next((p for p in dashboard.panels if p["id"] == panel_id), None)
        if not panel:
            raise ValueError(f"Panel not found: {panel_id}")
        
        # This is a simplified implementation that would be expanded in a real system
        # to query metrics based on the panel type and metrics
        
        result = {
            "panel": panel,
            "data": {}
        }
        
        # For demonstration, just return the most recent values
        for metric_name in panel["metrics"]:
            if hasattr(self.metrics_collector, "get_gauge"):
                # If it's our in-memory collector, we can get values directly
                if panel["type"] == "gauge":
                    result["data"][metric_name] = self.metrics_collector.get_gauge(metric_name)
                elif panel["type"] == "counter":
                    result["data"][metric_name] = self.metrics_collector.get_counter(metric_name)
                elif panel["type"] in ["line", "bar"] and hasattr(self.metrics_collector, "get_histogram_values"):
                    result["data"][metric_name] = self.metrics_collector.get_histogram_values(metric_name)
        
        return result
    
    def create_agent_dashboard(self, agent_id: str, title: Optional[str] = None) -> Dashboard:
        """
        Create a standard agent dashboard.
        
        Args:
            agent_id: The ID of the agent
            title: Optional dashboard title
            
        Returns:
            The new dashboard
        """
        title = title or f"Agent Dashboard: {agent_id}"
        dashboard = self.create_dashboard(
            title,
            f"Standard monitoring dashboard for agent {agent_id}"
        )
        
        # Messages panel
        dashboard.add_panel(
            "counter",
            "Message Statistics",
            "Count of messages sent and received",
            [
                "messages_sent",
                "messages_received"
            ],
            options={
                "display": "bar",
                "tags": {"agent_id": agent_id}
            }
        )
        
        # Tasks panel
        dashboard.add_panel(
            "counter",
            "Task Statistics",
            "Count of tasks started, completed, succeeded, and failed",
            [
                "tasks_started",
                "tasks_completed",
                "tasks_succeeded",
                "tasks_failed"
            ],
            options={
                "display": "bar",
                "tags": {"agent_id": agent_id}
            }
        )
        
        # Active tasks gauge
        dashboard.add_panel(
            "gauge",
            "Active Tasks",
            "Number of currently active tasks",
            ["active_tasks"],
            options={
                "min": 0,
                "max": 10,
                "thresholds": [
                    {"value": 5, "color": "yellow"},
                    {"value": 8, "color": "red"}
                ],
                "tags": {"agent_id": agent_id}
            }
        )
        
        # Task durations
        dashboard.add_panel(
            "line",
            "Task Durations",
            "Distribution of task durations",
            ["task_duration"],
            options={
                "aggregation": "histogram",
                "tags": {"agent_id": agent_id}
            }
        )
        
        return dashboard
    
    def create_system_dashboard(self) -> Dashboard:
        """
        Create a system-wide dashboard.
        
        Returns:
            The new dashboard
        """
        dashboard = self.create_dashboard(
            "System Overview",
            "System-wide metrics and status"
        )
        
        # Agent count
        dashboard.add_panel(
            "gauge",
            "Active Agents",
            "Number of active agents in the system",
            ["active_agents"],
            options={
                "min": 0,
                "max": 100
            }
        )
        
        # System performance
        dashboard.add_panel(
            "line",
            "System Performance",
            "Key system performance metrics",
            [
                "system_cpu_usage",
                "system_memory_usage",
                "system_latency"
            ],
            options={
                "yaxis": {"min": 0}
            }
        )
        
        # Message throughput
        dashboard.add_panel(
            "line",
            "Message Throughput",
            "Number of messages per minute",
            ["message_throughput"],
            options={
                "aggregation": "rate",
                "timeUnit": "minute"
            }
        )
        
        # Task success rate
        dashboard.add_panel(
            "gauge",
            "Task Success Rate",
            "Percentage of tasks completed successfully",
            ["task_success_rate"],
            options={
                "min": 0,
                "max": 100,
                "unit": "%",
                "thresholds": [
                    {"value": 50, "color": "red"},
                    {"value": 80, "color": "yellow"},
                    {"value": 95, "color": "green"}
                ]
            }
        )
        
        # Recent alerts
        dashboard.add_panel(
            "table",
            "Recent Alerts",
            "Most recent system alerts",
            ["alerts"],
            options={
                "limit": 10,
                "columns": [
                    {"field": "timestamp", "title": "Time"},
                    {"field": "severity", "title": "Severity"},
                    {"field": "message", "title": "Message"},
                    {"field": "entity_id", "title": "Entity"}
                ]
            }
        )
        
        return dashboard


class StandardAgentObserver(AgentObserver):
    """Standard implementation of an agent observer."""
    
    def __init__(self, collector: InMemoryMetricsCollector, 
                alert_manager: Optional[AlertManager] = None,
                anomaly_detector: Optional[AnomalyDetector] = None):
        """
        Initialize the agent observer.
        
        Args:
            collector: The metrics collector to use
            alert_manager: Optional alert manager for observer alerts
            anomaly_detector: Optional anomaly detector for observer metrics
        """
        self.collector = collector
        self.alert_manager = alert_manager
        self.anomaly_detector = anomaly_detector
        self.observations: Dict[str, List[Dict[str, Any]]] = {}
        self.logger = logging.getLogger("agent_framework.observer")
        
        # Health thresholds
        self.thresholds = {
            "messages_queued": 100,
            "active_tasks": 50,
            "error_rate": 0.1
        }
    
    def observe(self, observable: Observable) -> None:
        """
        Observe an entity and collect metrics/state.
        
        Args:
            observable: The entity to observe
        """
        try:
            # Get entity ID if available
            entity_id = getattr(observable, "id", str(id(observable)))
            
            # Collect metrics
            metrics = observable.get_metrics()
            state = observable.get_state()
            health = observable.get_health()
            
            # Create observation record
            observation = {
                "timestamp": datetime.now(),
                "metrics": metrics,
                "state": state,
                "health": health
            }
            
            # Store observation
            if entity_id not in self.observations:
                self.observations[entity_id] = []
            
            self.observations[entity_id].append(observation)
            
            # Limit observation history
            self.observations[entity_id] = self.observations[entity_id][-100:]
            
            # Record metrics
            for name, value in metrics.items():
                # Determine metric type and record appropriately
                if isinstance(value, (int, float)):
                    if name.startswith("count_") or name.endswith("_count"):
                        self.collector.record_counter(name, value, {"entity_id": entity_id})
                    else:
                        self.collector.record_gauge(name, value, {"entity_id": entity_id})
                    
                    # Feed to anomaly detector if available
                    if self.anomaly_detector:
                        self.anomaly_detector.add_metric_value(
                            name, value, entity_id, {"entity_id": entity_id}
                        )
            
            # Check health
            if health.get("status") != "healthy" and self.alert_manager:
                severity = "info"
                if health.get("status") == "warning":
                    severity = "warning"
                elif health.get("status") == "error":
                    severity = "error"
                elif health.get("status") == "critical":
                    severity = "critical"
                
                message = health.get("message", f"Entity {entity_id} health status: {health.get('status')}")
                
                alert = StandardAlert(entity_id, severity, message, health)
                self.alert_manager.add_alert(alert)
                
        except Exception as e:
            self.logger.error(f"Error observing entity {getattr(observable, 'id', id(observable))}: {e}")
    
    def get_observations(self, entity_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get collected observations.
        
        Args:
            entity_id: Optional filter for entity ID
            
        Returns:
            A list of observations
        """
        if entity_id:
            return self.observations.get(entity_id, [])
        
        # Combine all observations, newest first
        all_observations = []
        for entity_observations in self.observations.values():
            all_observations.extend(entity_observations)
        
        all_observations.sort(key=lambda o: o["timestamp"], reverse=True)
        
        return all_observations
    
    def observe_conversation(self, agent_id: str, conversation_id: str) -> None:
        """
        Observe a specific conversation.
        
        Args:
            agent_id: The ID of the agent
            conversation_id: The ID of the conversation
        """
        # This implementation would be expanded in a real system to
        # observe conversation-specific metrics and state
        
        # Log the observation
        self.logger.debug(f"Observing conversation {conversation_id} for agent {agent_id}")
        
        # For now, just record an event
        self.collector.record_event(
            "conversation_observed",
            {"agent_id": agent_id, "conversation_id": conversation_id},
            {"agent_id": agent_id, "conversation_id": conversation_id}
        )
    
    def observe_task(self, agent_id: str, task_id: str) -> None:
        """
        Observe a specific task.
        
        Args:
            agent_id: The ID of the agent
            task_id: The ID of the task
        """
        # This implementation would be expanded in a real system to
        # observe task-specific metrics and state
        
        # Log the observation
        self.logger.debug(f"Observing task {task_id} for agent {agent_id}")
        
        # For now, just record an event
        self.collector.record_event(
            "task_observed",
            {"agent_id": agent_id, "task_id": task_id},
            {"agent_id": agent_id, "task_id": task_id}
        )
    
    def get_agent_health(self, agent_id: str) -> Dict[str, Any]:
        """
        Get the health status of an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            A dictionary with health information
        """
        # Get the most recent observation for the agent
        observations = self.observations.get(agent_id, [])
        if not observations:
            return {"status": "unknown", "message": "No observations available"}
        
        latest = observations[-1]
        
        # Return the health information
        return latest.get("health", {"status": "unknown", "message": "Health information not available"})


class EnhancedSystemMonitor(SystemMonitor):
    """Enhanced implementation of the SystemMonitor interface."""
    
    def __init__(self, metrics_collector: Optional[InMemoryMetricsCollector] = None, 
                alert_manager: Optional[AlertManager] = None):
        """
        Initialize the system monitor.
        
        Args:
            metrics_collector: Optional metrics collector for system metrics
            alert_manager: Optional alert manager for system alerts
        """
        self.metrics_collector = metrics_collector or InMemoryMetricsCollector()
        self.alert_manager = alert_manager or InMemoryAlertManager()
        self.observers: List[Observer] = []
        self.start_time = datetime.now()
        self.logger = logging.getLogger("agent_framework.system_monitor")
        
        # Create anomaly detector
        self.anomaly_detector = AnomalyDetector(self.alert_manager)
        self._setup_default_thresholds()
        
        # Create dashboard manager
        self.dashboard_manager = DashboardManager(self.metrics_collector, self.alert_manager)
        self._create_default_dashboards()
        
        # Track observed entities
        self.entities: Set[str] = set()
        
        # Start monitoring thread
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def _setup_default_thresholds(self) -> None:
        """Set up default anomaly detection thresholds."""
        # System metrics
        self.anomaly_detector.set_threshold("system_cpu_usage", 
                                         critical=90, error=80, warning=70)
        self.anomaly_detector.set_threshold("system_memory_usage", 
                                         critical=90, error=80, warning=70)
        self.anomaly_detector.set_threshold("system_latency", 
                                         critical=1000, error=500, warning=200)
        
        # Task metrics
        self.anomaly_detector.set_threshold("task_error_rate", 
                                         critical=20, error=10, warning=5)
        self.anomaly_detector.set_threshold("task_success_rate", 
                                         critical=50, error=70, warning=90, 
                                         direction="below")
        
        # Statistical thresholds
        self.anomaly_detector.set_statistical_thresholds("active_tasks")
        self.anomaly_detector.set_statistical_thresholds("task_duration")
        self.anomaly_detector.set_statistical_thresholds("message_throughput")
    
    def _create_default_dashboards(self) -> None:
        """Create default system dashboards."""
        self.dashboard_manager.create_system_dashboard()
    
    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self.running:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Calculate derived metrics
                self._calculate_derived_metrics()
                
                # Check health and raise alerts if needed
                health = self.get_system_health()
                if health["status"] != "healthy":
                    self._check_health_alerts(health)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
            
            # Sleep before next collection
            time.sleep(10)  # 10-second monitoring interval
    
    def _collect_system_metrics(self) -> None:
        """Collect system-level metrics."""
        # This is a simplified implementation - a real implementation would
        # collect actual system metrics from the OS, agents, etc.
        
        # For demonstration, we'll generate some random metrics
        import random
        
        # System metrics
        self.metrics_collector.record_gauge(
            "system_cpu_usage", 
            50 + random.uniform(-10, 30),  # 40% to 80%
            {"source": "monitor"}
        )
        
        self.metrics_collector.record_gauge(
            "system_memory_usage", 
            60 + random.uniform(-15, 25),  # 45% to 85%
            {"source": "monitor"}
        )
        
        self.metrics_collector.record_gauge(
            "system_latency", 
            100 + random.uniform(-50, 150),  # 50ms to 250ms
            {"source": "monitor"}
        )
        
        # Agent metrics
        self.metrics_collector.record_gauge(
            "active_agents", 
            max(1, round(10 + random.uniform(-3, 5))),  # 7 to 15
            {"source": "monitor"}
        )
        
        self.metrics_collector.record_gauge(
            "message_throughput", 
            max(1, round(100 + random.uniform(-30, 50))),  # 70 to 150
            {"source": "monitor"}
        )
    
    def _calculate_derived_metrics(self) -> None:
        """Calculate derived metrics from raw metrics."""
        try:
            # Task success rate
            if hasattr(self.metrics_collector, "get_counter"):
                tasks_succeeded = self.metrics_collector.get_counter("tasks_succeeded", {"source": "monitor"})
                tasks_completed = self.metrics_collector.get_counter("tasks_completed", {"source": "monitor"})
                
                if tasks_completed > 0:
                    success_rate = (tasks_succeeded / tasks_completed) * 100
                    self.metrics_collector.record_gauge(
                        "task_success_rate", 
                        success_rate,
                        {"source": "monitor"}
                    )
                    
                    error_rate = ((tasks_completed - tasks_succeeded) / tasks_completed) * 100
                    self.metrics_collector.record_gauge(
                        "task_error_rate", 
                        error_rate,
                        {"source": "monitor"}
                    )
            
        except Exception as e:
            self.logger.error(f"Error calculating derived metrics: {e}")
    
    def _check_health_alerts(self, health: Dict[str, Any]) -> None:
        """
        Check health status and raise alerts if needed.
        
        Args:
            health: The health status dictionary
        """
        if not self.alert_manager:
            return
        
        severity = "warning"
        if health["status"] == "critical":
            severity = "critical"
        elif health["status"] == "error":
            severity = "error"
        
        message = f"System health issue: {health['status']}"
        if "message" in health:
            message += f" - {health['message']}"
        elif "issues" in health and health["issues"]:
            message += f" - {', '.join(health['issues'])}"
        
        alert = StandardAlert(
            entity_id="system",
            severity=severity,
            message=message,
            context={"health": health}
        )
        
        self.alert_manager.add_alert(alert)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get current system-wide metrics.
        
        Returns:
            A dictionary of system metrics
        """
        metrics = {
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "start_time": self.start_time.isoformat()
        }
        
        # Add collector metrics
        if hasattr(self.metrics_collector, "get_gauge"):
            for metric_name in [
                "system_cpu_usage", "system_memory_usage", "system_latency",
                "active_agents", "message_throughput", "task_success_rate",
                "task_error_rate"
            ]:
                metrics[metric_name] = self.metrics_collector.get_gauge(
                    metric_name, {"source": "monitor"}
                )
        
        return metrics
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get the overall system health status.
        
        Returns:
            A dictionary with health information
        """
        # Get metrics
        metrics = self.get_system_metrics()
        
        # Check for critical issues
        issues = []
        
        # Check CPU usage
        cpu_usage = metrics.get("system_cpu_usage", 0)
        if cpu_usage > 80:
            issues.append(f"High CPU usage: {cpu_usage:.1f}%")
        
        # Check memory usage
        memory_usage = metrics.get("system_memory_usage", 0)
        if memory_usage > 80:
            issues.append(f"High memory usage: {memory_usage:.1f}%")
        
        # Check system latency
        latency = metrics.get("system_latency", 0)
        if latency > 200:
            issues.append(f"High system latency: {latency:.1f}ms")
        
        # Check task success rate
        task_success_rate = metrics.get("task_success_rate", 100)
        if task_success_rate < 90:
            issues.append(f"Low task success rate: {task_success_rate:.1f}%")
        
        # Determine status based on issues
        status = "healthy"
        if issues:
            status = "warning"
            
            # Check severity of issues
            if any("High CPU usage" in issue and cpu_usage > 90 for issue in issues) or \
               any("High memory usage" in issue and memory_usage > 90 for issue in issues) or \
               any("High system latency" in issue and latency > 500 for issue in issues) or \
               any("Low task success rate" in issue and task_success_rate < 70 for issue in issues):
                status = "error"
            
            if any("High CPU usage" in issue and cpu_usage > 95 for issue in issues) or \
               any("High memory usage" in issue and memory_usage > 95 for issue in issues) or \
               any("High system latency" in issue and latency > 1000 for issue in issues) or \
               any("Low task success rate" in issue and task_success_rate < 50 for issue in issues):
                status = "critical"
        
        # Message based on status
        message = "System is healthy" if status == "healthy" else f"System has {len(issues)} issues"
        
        return {
            "status": status,
            "message": message,
            "issues": issues,
            "metrics": {
                "active_agents": metrics.get("active_agents", 0),
                "uptime_seconds": metrics.get("uptime_seconds", 0),
                "cpu_usage": metrics.get("system_cpu_usage", 0),
                "memory_usage": metrics.get("system_memory_usage", 0),
                "latency": metrics.get("system_latency", 0),
                "task_success_rate": metrics.get("task_success_rate", 100)
            }
        }
    
    def register_observer(self, observer: Observer) -> None:
        """
        Register an observer with the system monitor.
        
        Args:
            observer: The observer to register
        """
        if observer not in self.observers:
            self.observers.append(observer)
            self.logger.info(f"Registered observer: {observer.__class__.__name__}")
    
    def register_alert_manager(self, alert_manager: AlertManager) -> None:
        """
        Register an alert manager with the system monitor.
        
        Args:
            alert_manager: The alert manager to register
        """
        self.alert_manager = alert_manager
        self.logger.info(f"Registered alert manager: {alert_manager.__class__.__name__}")
    
    def monitor_entity(self, entity: Observable) -> None:
        """
        Monitor an entity.
        
        Observe the entity using all registered observers.
        
        Args:
            entity: The entity to monitor
        """
        entity_id = getattr(entity, "id", str(id(entity)))
        self.entities.add(entity_id)
        
        for observer in self.observers:
            observer.observe(entity)
    
    def get_dashboards(self) -> List[Dict[str, Any]]:
        """
        Get all system dashboards.
        
        Returns:
            A list of dashboard summaries
        """
        return self.dashboard_manager.list_dashboards()
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a dashboard by ID.
        
        Args:
            dashboard_id: The dashboard ID
            
        Returns:
            The dashboard or None if not found
        """
        dashboard = self.dashboard_manager.get_dashboard(dashboard_id)
        return dashboard.to_dict() if dashboard else None
    
    def get_alerts(self, severity: Optional[str] = None,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get system alerts.
        
        Args:
            severity: Optional filter for severity level
            start_time: Optional filter for start time
            end_time: Optional filter for end time
            
        Returns:
            A list of alerts
        """
        alerts = self.alert_manager.get_alerts(
            severity=severity,
            start_time=start_time,
            end_time=end_time
        )
        
        return [
            alert.to_dict() if hasattr(alert, "to_dict") else {
                "severity": alert.get_severity(),
                "message": alert.get_message(),
                "entity_id": alert.get_entity_id(),
                "timestamp": alert.get_timestamp().isoformat(),
                "context": alert.get_context()
            }
            for alert in alerts
        ]
    
    def shutdown(self) -> None:
        """Shutdown the system monitor."""
        self.running = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        self.logger.info("System monitor shut down")


def create_observability_system() -> Tuple[SystemMonitor, AlertManager, InMemoryMetricsCollector]:
    """
    Create a complete observability system.
    
    Returns:
        A tuple of (system_monitor, alert_manager, metrics_collector)
    """
    # Create metrics collector
    metrics_collector = InMemoryMetricsCollector()
    
    # Create alert manager
    alert_manager = InMemoryAlertManager()
    
    # Create system monitor
    system_monitor = EnhancedSystemMonitor(metrics_collector, alert_manager)
    
    # Create and register agent observer
    agent_observer = StandardAgentObserver(
        metrics_collector,
        alert_manager,
        AnomalyDetector(alert_manager)
    )
    system_monitor.register_observer(agent_observer)
    
    return system_monitor, alert_manager, metrics_collector