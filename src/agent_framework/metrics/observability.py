"""
Concrete implementations of observability interfaces.

This module provides implementations of the observability interfaces
for monitoring and alerting on agent behavior and performance.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Set, Union
from datetime import datetime, timedelta
from uuid import uuid4

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


class InMemoryAlertManager(AlertManager):
    """In-memory implementation of an alert manager."""
    
    def __init__(self):
        """Initialize the alert manager."""
        self.alerts = {}
        self.logger = logging.getLogger("alerts.manager")
    
    def add_alert(self, alert: Alert) -> None:
        """Add an alert to the manager."""
        self.alerts[alert.id] = alert
        self.logger.info(f"Alert {alert.id}: [{alert.get_severity()}] {alert.get_message()} - {alert.get_entity_id()}")
    
    def get_alerts(self, severity: Optional[str] = None,
                 entity_id: Optional[str] = None,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None) -> List[Alert]:
        """Get alerts matching specified criteria."""
        filtered_alerts = list(self.alerts.values())
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a.get_severity() == severity]
        
        if entity_id:
            filtered_alerts = [a for a in filtered_alerts if a.get_entity_id() == entity_id]
        
        if start_time:
            filtered_alerts = [a for a in filtered_alerts if a.get_timestamp() >= start_time]
        
        if end_time:
            filtered_alerts = [a for a in filtered_alerts if a.get_timestamp() <= end_time]
        
        return filtered_alerts
    
    def acknowledge_alert(self, alert_id: str) -> None:
        """Acknowledge an alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledged = True
            self.logger.info(f"Alert {alert_id} acknowledged")
    
    def resolve_alert(self, alert_id: str) -> None:
        """Resolve an alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            self.logger.info(f"Alert {alert_id} resolved")


class StandardAgentObserver(AgentObserver):
    """Standard implementation of an agent observer."""
    
    def __init__(self, alert_manager: Optional[AlertManager] = None):
        """
        Initialize the agent observer.
        
        Args:
            alert_manager: Optional alert manager for raising alerts
        """
        self.observations = []
        self.alert_manager = alert_manager
        self.logger = logging.getLogger("observer.agent")
        
        # Health thresholds
        self.thresholds = {
            "messages_queued": 100,
            "active_tasks": 50,
            "error_rate": 0.1
        }
    
    def observe(self, observable: Observable) -> None:
        """Observe an entity and collect metrics/state."""
        metrics = observable.get_metrics()
        state = observable.get_state()
        health = observable.get_health()
        
        observation = {
            "timestamp": datetime.now(),
            "entity_id": state.get("id"),
            "metrics": metrics,
            "state": state,
            "health": health
        }
        
        self.observations.append(observation)
        
        # Check for health issues
        if health.get("status") != "healthy" and self.alert_manager:
            self._raise_health_alert(observation)
    
    def _raise_health_alert(self, observation: Dict[str, Any]) -> None:
        """Raise an alert for health issues."""
        entity_id = observation["entity_id"]
        health = observation["health"]
        
        severity = "warning"
        if health.get("status") == "critical":
            severity = "critical"
        elif health.get("status") == "error":
            severity = "error"
        
        message = f"Health issue detected for {entity_id}: {health.get('status')}"
        if "issues" in health and health["issues"]:
            message += f" - {', '.join(health['issues'])}"
        
        alert = StandardAlert(
            entity_id=entity_id,
            severity=severity,
            message=message,
            context={
                "health": health,
                "metrics": observation["metrics"]
            }
        )
        
        self.alert_manager.add_alert(alert)
    
    def get_observations(self, entity_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get collected observations."""
        if entity_id:
            return [o for o in self.observations if o["entity_id"] == entity_id]
        return self.observations
    
    def observe_conversation(self, agent_id: str, conversation_id: str) -> None:
        """Observe a specific conversation."""
        # This would typically query the agent for conversation metrics
        # For now, just log that we're observing this conversation
        self.logger.info(f"Observing conversation {conversation_id} for agent {agent_id}")
    
    def observe_task(self, agent_id: str, task_id: str) -> None:
        """Observe a specific task."""
        # This would typically query the agent for task metrics
        # For now, just log that we're observing this task
        self.logger.info(f"Observing task {task_id} for agent {agent_id}")
    
    def get_agent_health(self, agent_id: str) -> Dict[str, Any]:
        """Get the health status of an agent."""
        # Get the most recent observation for this agent
        observations = self.get_observations(agent_id)
        
        if not observations:
            return {
                "status": "unknown",
                "last_updated": None,
                "issues": ["No observations available"]
            }
        
        # Return the health status from the most recent observation
        return observations[-1]["health"]


class BasicSystemMonitor(SystemMonitor):
    """Basic implementation of a system monitor."""
    
    def __init__(self, storage: Optional[Union[InMemoryMetricsStorage, SQLiteMetricsStorage]] = None):
        """
        Initialize the system monitor.
        
        Args:
            storage: Optional metrics storage for system metrics
        """
        self.observers = []
        self.alert_managers = []
        self.storage = storage or InMemoryMetricsStorage()
        self.collector = InMemoryMetricsCollector(self.storage)
        self.logger = logging.getLogger("monitor.system")
        
        # Track observed entities
        self.entities: Set[str] = set()
        
        # Last observations for quick access
        self.last_observations = {}
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system-wide metrics."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "entity_count": len(self.entities),
            "observer_count": len(self.observers),
            "alert_manager_count": len(self.alert_managers)
        }
        
        # Add collected metrics if available
        if self.collector:
            metrics.update({
                "messages_total": self.collector.get_counter("messages_total"),
                "tasks_total": self.collector.get_counter("tasks_total"),
                "tasks_succeeded": self.collector.get_counter("tasks_succeeded"),
                "tasks_failed": self.collector.get_counter("tasks_failed"),
                "error_rate": self.collector.get_counter("tasks_failed") / 
                           max(1, self.collector.get_counter("tasks_total"))
            })
        
        return metrics
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get the overall system health status."""
        # Collect entity health statuses
        entity_health = {}
        for entity_id in self.entities:
            if entity_id in self.last_observations:
                entity_health[entity_id] = self.last_observations[entity_id]["health"]
        
        # Determine overall health
        status = "healthy"
        issues = []
        
        # Check for unhealthy entities
        unhealthy_entities = [
            entity_id for entity_id, health in entity_health.items()
            if health.get("status") != "healthy"
        ]
        
        if unhealthy_entities:
            status = "warning"
            issues.append(f"{len(unhealthy_entities)} entities reporting issues")
        
        # Check system metrics
        system_metrics = self.get_system_metrics()
        
        # Example check: error rate too high
        error_rate = system_metrics.get("error_rate", 0)
        if error_rate > 0.1:
            status = "error" if error_rate > 0.3 else "warning"
            issues.append(f"High error rate: {error_rate:.2%}")
        
        return {
            "status": status,
            "last_updated": datetime.now().isoformat(),
            "issues": issues,
            "entity_health": entity_health
        }
    
    def register_observer(self, observer: Observer) -> None:
        """Register an observer with the system monitor."""
        self.observers.append(observer)
        self.logger.info(f"Registered observer: {observer.__class__.__name__}")
    
    def register_alert_manager(self, alert_manager: AlertManager) -> None:
        """Register an alert manager with the system monitor."""
        self.alert_managers.append(alert_manager)
        self.logger.info(f"Registered alert manager: {alert_manager.__class__.__name__}")
    
    def monitor_entity(self, entity: Observable) -> None:
        """
        Monitor an entity.
        
        This method observes the entity and updates system metrics.
        
        Args:
            entity: The entity to monitor
        """
        entity_state = entity.get_state()
        entity_id = entity_state.get("id")
        
        if entity_id:
            self.entities.add(entity_id)
        
        # Collect observations from all observers
        for observer in self.observers:
            observer.observe(entity)
            
            # Get the observation and store it
            observations = observer.get_observations(entity_id)
            if observations:
                self.last_observations[entity_id] = observations[-1]
        
        # Update system metrics
        self._update_system_metrics(entity)
    
    def _update_system_metrics(self, entity: Observable) -> None:
        """Update system metrics based on entity metrics."""
        entity_metrics = entity.get_metrics()
        entity_state = entity.get_state()
        entity_id = entity_state.get("id", "unknown")
        
        # Example: aggregate message counts
        messages_sent = entity_metrics.get("messages_sent", 0)
        messages_received = entity_metrics.get("messages_received", 0)
        
        if messages_sent or messages_received:
            self.collector.record_counter("messages_total", messages_sent + messages_received)
        
        # Example: aggregate task counts
        tasks_started = entity_metrics.get("tasks_started", 0)
        tasks_completed = entity_metrics.get("tasks_completed", 0)
        tasks_succeeded = entity_metrics.get("tasks_succeeded", 0)
        tasks_failed = entity_metrics.get("tasks_failed", 0)
        
        if tasks_started:
            self.collector.record_counter("tasks_total", tasks_started)
        
        if tasks_succeeded:
            self.collector.record_counter("tasks_succeeded", tasks_succeeded)
        
        if tasks_failed:
            self.collector.record_counter("tasks_failed", tasks_failed)
    
    def check_for_alerts(self) -> None:
        """
        Check for conditions that should trigger alerts.
        
        This method evaluates system health and raises alerts for any issues.
        """
        health = self.get_system_health()
        
        if health["status"] != "healthy" and self.alert_managers:
            # Create an alert for system health issues
            severity = "warning"
            if health["status"] == "critical":
                severity = "critical"
            elif health["status"] == "error":
                severity = "error"
            
            message = f"System health issue: {health['status']}"
            if health["issues"]:
                message += f" - {', '.join(health['issues'])}"
            
            alert = StandardAlert(
                entity_id="system",
                severity=severity,
                message=message,
                context={"health": health}
            )
            
            # Send to all alert managers
            for alert_manager in self.alert_managers:
                alert_manager.add_alert(alert)