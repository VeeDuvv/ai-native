#!/usr/bin/env python3
"""
Example demonstrating the observability system.

This module provides a complete example of how to set up and use
the observability framework with the agent communication protocol.
"""

import os
import sys
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any

# Add the project root to sys.path to allow running this script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.agent_framework.core.message import MessageType
from src.agent_framework.communication.protocol import StandardCommunicationProtocol
from src.agent_framework.metrics.collectors import InMemoryMetricsCollector, AgentMetricsCollector
from src.agent_framework.metrics.storage import InMemoryMetricsStorage
from src.agent_framework.metrics.integration import (
    ObservableCommunicatingAgent,
    ObservableCommunicationProtocol,
    CampaignMetricsTracker
)
from src.agent_framework.metrics.observability import (
    StandardAlert,
    InMemoryAlertManager,
    StandardAgentObserver,
    BasicSystemMonitor
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Define test message types
class DemoMessageType(MessageType):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    NOTIFICATION = "NOTIFICATION"
    ERROR = "ERROR"


class ObservableDemoAgent(ObservableCommunicatingAgent):
    """Demo agent implementation with observability features."""
    
    def __init__(self, agent_id: str, protocol, metrics_collector=None):
        super().__init__(agent_id, f"Demo Agent {agent_id}", protocol, metrics_collector)
        
        # Register message handlers
        self.register_message_handler(DemoMessageType.REQUEST, self._handle_request)
        self.register_message_handler(DemoMessageType.RESPONSE, self._handle_response)
        self.register_message_handler(DemoMessageType.NOTIFICATION, self._handle_notification)
        self.register_message_handler(DemoMessageType.ERROR, self._handle_error)
        
        # Internal state for testing
        self.success_rate = 0.9  # For simulating task success/failure
        self.error_count = 0
        self.active_task_count = 0
    
    def _handle_request(self, message):
        """Handle request messages."""
        with self.metrics_collector.measure_task("handle_request", message.id):
            logger.info(f"Agent {self.id} handling request: {message.id}")
            
            # Simulate task processing
            time.sleep(0.1)
            
            # Send a response
            self.send_message(
                recipient_id=message.sender_id,
                message_type=DemoMessageType.RESPONSE,
                content={"response_to": message.id, "status": "success"},
                conversation_id=message.conversation_id
            )
    
    def _handle_response(self, message):
        """Handle response messages."""
        logger.info(f"Agent {self.id} received response: {message.id}")
    
    def _handle_notification(self, message):
        """Handle notification messages."""
        logger.info(f"Agent {self.id} received notification: {message.id}")
    
    def _handle_error(self, message):
        """Handle error messages."""
        logger.info(f"Agent {self.id} received error: {message.id}")
        self.error_count += 1
    
    def get_conversation_metrics(self, conversation_id):
        """Get metrics for a specific conversation."""
        messages = self.get_received_messages(conversation_id=conversation_id)
        sent_messages = [m for m in self.sent_messages if m.conversation_id == conversation_id]
        
        return {
            "conversation_id": conversation_id,
            "messages_received": len(messages),
            "messages_sent": len(sent_messages),
            "message_types_received": {
                str(m.message_type): len([msg for msg in messages if msg.message_type == m.message_type])
                for m in messages
            }
        }
    
    def get_task_metrics(self, task_type=None):
        """Get metrics for agent tasks."""
        if isinstance(self.metrics_collector, AgentMetricsCollector):
            tasks_started = self.metrics_collector.get_counter(
                "tasks_started", 
                {"agent_id": self.id} if not task_type else {"agent_id": self.id, "task_type": task_type}
            )
            
            tasks_completed = self.metrics_collector.get_counter(
                "tasks_completed", 
                {"agent_id": self.id} if not task_type else {"agent_id": self.id, "task_type": task_type}
            )
            
            tasks_succeeded = self.metrics_collector.get_counter(
                "tasks_succeeded", 
                {"agent_id": self.id} if not task_type else {"agent_id": self.id, "task_type": task_type}
            )
            
            tasks_failed = self.metrics_collector.get_counter(
                "tasks_failed", 
                {"agent_id": self.id} if not task_type else {"agent_id": self.id, "task_type": task_type}
            )
            
            task_durations = self.metrics_collector.get_histogram_values(
                "task_duration",
                {"agent_id": self.id} if not task_type else {"agent_id": self.id, "task_type": task_type}
            )
            
            return {
                "tasks_started": tasks_started,
                "tasks_completed": tasks_completed,
                "tasks_succeeded": tasks_succeeded,
                "tasks_failed": tasks_failed,
                "active_tasks": tasks_started - tasks_completed,
                "success_rate": tasks_succeeded / max(1, tasks_completed),
                "avg_duration": sum(task_durations) / max(1, len(task_durations)) if task_durations else 0
            }
        
        return {
            "tasks_started": 0,
            "tasks_completed": 0,
            "tasks_succeeded": 0,
            "tasks_failed": 0,
            "active_tasks": 0,
            "success_rate": 0,
            "avg_duration": 0
        }
    
    def get_health(self):
        """Get health status with simulated issues for testing."""
        status = "healthy"
        issues = []
        
        # Simulate health issues based on metrics
        task_metrics = self.get_task_metrics()
        
        # Too many active tasks
        if task_metrics["active_tasks"] > 10:
            status = "warning"
            issues.append(f"High number of active tasks: {task_metrics['active_tasks']}")
        
        # Too many errors
        if self.error_count > 3:
            status = "error"
            issues.append(f"High error count: {self.error_count}")
        
        # Poor success rate
        if task_metrics["success_rate"] < 0.8 and task_metrics["tasks_completed"] > 5:
            status = "warning"
            issues.append(f"Low task success rate: {task_metrics['success_rate']:.2%}")
        
        return {
            "status": status,
            "last_updated": datetime.now().isoformat(),
            "issues": issues,
            "metrics": {
                "active_tasks": task_metrics["active_tasks"],
                "success_rate": task_metrics["success_rate"],
                "error_count": self.error_count
            }
        }
    
    def simulate_task(self, task_type, will_succeed=None):
        """Simulate running a task with success/failure."""
        task_id = f"task-{self.id}-{int(time.time())}"
        
        # Determine if task will succeed (if not specified)
        if will_succeed is None:
            will_succeed = self.success_rate > 0.9
        
        # Start measuring the task
        with self.metrics_collector.measure_task(task_type, task_id):
            logger.info(f"Agent {self.id} running task {task_id} of type {task_type}")
            
            # Simulate work
            time.sleep(0.1)
            
            # Simulate failure if needed
            if not will_succeed:
                logger.warning(f"Agent {self.id} task {task_id} failed")
                raise RuntimeError("Simulated task failure")
            
            logger.info(f"Agent {self.id} task {task_id} succeeded")
        
        return {"task_id": task_id, "success": will_succeed}


def run_observability_example():
    """
    Run a complete example of the observability system.
    
    This function sets up an observable communication protocol with
    agents, metrics collection, and monitoring.
    """
    # Set up metrics storage
    storage = InMemoryMetricsStorage()
    
    # Set up alert manager
    alert_manager = InMemoryAlertManager()
    
    # Set up agent observer
    agent_observer = StandardAgentObserver(alert_manager)
    
    # Set up system monitor
    system_monitor = BasicSystemMonitor(storage)
    system_monitor.register_observer(agent_observer)
    system_monitor.register_alert_manager(alert_manager)
    
    # Set up protocol with metrics
    protocol_metrics = InMemoryMetricsCollector(storage)
    protocol = ObservableCommunicationProtocol(protocol_metrics)
    
    # Create agents with metrics
    agents = {}
    for i in range(3):
        agent_id = f"agent-{i+1}"
        metrics = AgentMetricsCollector(agent_id, storage)
        agent = ObservableDemoAgent(agent_id, protocol, metrics)
        agents[agent_id] = agent
    
    # Run the simulation
    logger.info("Starting observability simulation")
    
    # Monitor initial state
    for agent_id, agent in agents.items():
        system_monitor.monitor_entity(agent)
    
    # Check for alerts
    system_monitor.check_for_alerts()
    
    # Simulate some agent activity
    for _ in range(5):
        # Each agent sends requests to other agents
        for agent_id, agent in agents.items():
            # Choose a recipient
            for recipient_id, recipient in agents.items():
                if recipient_id != agent_id:
                    # Send a request
                    agent.send_message(
                        recipient_id=recipient_id,
                        message_type=DemoMessageType.REQUEST,
                        content={"action": "do_something"}
                    )
            
            # Simulate some tasks
            for i in range(3):
                try:
                    agent.simulate_task("background_process")
                except Exception:
                    # Task failure is expected in some cases
                    pass
        
        # Process messages
        protocol.process_message_queue()
        
        # Monitor agents after activity
        for agent_id, agent in agents.items():
            system_monitor.monitor_entity(agent)
        
        # Check for alerts
        system_monitor.check_for_alerts()
        
        # Short delay to spread out the simulation
        time.sleep(0.2)
    
    # Simulate an agent with health issues
    problem_agent = agents["agent-1"]
    problem_agent.error_count = 5  # Simulate errors
    
    # Simulate failed tasks
    for _ in range(5):
        try:
            problem_agent.simulate_task("critical_process", False)
        except Exception:
            # Task failure is expected
            pass
    
    # Monitor the problematic agent
    system_monitor.monitor_entity(problem_agent)
    
    # Check for alerts
    system_monitor.check_for_alerts()
    
    # Get system metrics and health
    system_metrics = system_monitor.get_system_metrics()
    system_health = system_monitor.get_system_health()
    
    # Get alerts
    alerts = alert_manager.get_alerts()
    
    # Print summary
    logger.info("Simulation complete")
    logger.info(f"System health: {system_health['status']}")
    
    if system_health["issues"]:
        logger.info(f"System issues: {', '.join(system_health['issues'])}")
    
    logger.info(f"Total entities: {len(system_monitor.entities)}")
    logger.info(f"Total alerts: {len(alerts)}")
    
    for alert in alerts:
        logger.info(f"Alert: [{alert.get_severity()}] {alert.get_message()}")
    
    return {
        "storage": storage,
        "protocol": protocol,
        "agents": agents,
        "alert_manager": alert_manager,
        "agent_observer": agent_observer,
        "system_monitor": system_monitor,
        "system_health": system_health,
        "alerts": alerts
    }


if __name__ == "__main__":
    run_observability_example()