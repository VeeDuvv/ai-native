# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file shows how to use our agent monitoring tools. It's like a demo that shows
# how we can watch what our AI helpers are doing and get alerts if they run into problems.

# High School Explanation:
# This module provides example code demonstrating how to implement and use the agent
# observability framework. It shows how to set up monitoring, anomaly detection, 
# dashboards, and alerts for a simple agent-based system.

"""
Example demonstrating the observability system.

This module provides a complete example of how to set up and use
the observability framework with the agent communication protocol.
"""

import os
import sys
import logging
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Add the project root to sys.path to allow running this script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from src.agent_framework.core.message import MessageType
from src.agent_framework.core.observability import Observable, ObservableAgent
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
    EnhancedSystemMonitor,
    AnomalyDetector,
    Dashboard,
    create_observability_system
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
        self.cpu_usage = 30  # Simulated CPU usage (%)
        self.memory_usage = 40  # Simulated memory usage (%)
    
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
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get the current metrics for the agent."""
        task_metrics = self.get_task_metrics()
        
        return {
            "tasks_started": task_metrics.get("tasks_started", 0),
            "tasks_completed": task_metrics.get("tasks_completed", 0),
            "tasks_succeeded": task_metrics.get("tasks_succeeded", 0),
            "tasks_failed": task_metrics.get("tasks_failed", 0),
            "active_tasks": task_metrics.get("active_tasks", 0),
            "success_rate": task_metrics.get("success_rate", 1.0),
            "messages_sent": len(self.sent_messages),
            "messages_received": len(self.received_messages),
            "error_count": self.error_count,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the agent."""
        return {
            "id": self.id,
            "name": self.name,
            "type": "demo",
            "status": "busy" if self.active_task_count > 0 else "idle",
            "last_activity": datetime.now().isoformat()
        }
    
    def get_conversation_metrics(self, conversation_id: str) -> Dict[str, Any]:
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
            } if messages else {}
        }
    
    def get_task_metrics(self, task_type: Optional[str] = None) -> Dict[str, Any]:
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
    
    def get_health(self) -> Dict[str, Any]:
        """Get health status with simulated issues for testing."""
        status = "healthy"
        issues = []
        
        # Simulate health issues based on metrics
        task_metrics = self.get_task_metrics()
        
        # Too many active tasks
        if task_metrics.get("active_tasks", 0) > 10:
            status = "warning"
            issues.append(f"High number of active tasks: {task_metrics.get('active_tasks', 0)}")
        
        # Too many errors
        if self.error_count > 3:
            status = "error"
            issues.append(f"High error count: {self.error_count}")
        
        # Poor success rate
        if task_metrics.get("success_rate", 1.0) < 0.8 and task_metrics.get("tasks_completed", 0) > 5:
            status = "warning"
            issues.append(f"Low task success rate: {task_metrics.get('success_rate', 1.0):.2%}")
        
        # High resource usage
        if self.cpu_usage > 80:
            status = "warning"
            issues.append(f"High CPU usage: {self.cpu_usage}%")
            
            if self.cpu_usage > 90:
                status = "error"
        
        if self.memory_usage > 80:
            status = "warning"
            issues.append(f"High memory usage: {self.memory_usage}%")
            
            if self.memory_usage > 90:
                status = "error"
        
        return {
            "status": status,
            "last_updated": datetime.now().isoformat(),
            "issues": issues,
            "metrics": {
                "active_tasks": task_metrics.get("active_tasks", 0),
                "success_rate": task_metrics.get("success_rate", 1.0),
                "error_count": self.error_count,
                "cpu_usage": self.cpu_usage,
                "memory_usage": self.memory_usage
            }
        }
    
    def simulate_task(self, task_type: str, will_succeed: Optional[bool] = None) -> Dict[str, Any]:
        """Simulate running a task with success/failure."""
        task_id = f"task-{self.id}-{int(time.time())}"
        self.active_task_count += 1
        
        # Randomly update resource usage
        self.cpu_usage = min(95, max(5, self.cpu_usage + random.randint(-10, 15)))
        self.memory_usage = min(95, max(5, self.memory_usage + random.randint(-5, 10)))
        
        # Determine if task will succeed (if not specified)
        if will_succeed is None:
            will_succeed = random.random() < self.success_rate
        
        try:
            # Start measuring the task
            with self.metrics_collector.measure_task(task_type, task_id):
                logger.info(f"Agent {self.id} running task {task_id} of type {task_type}")
                
                # Simulate work
                time.sleep(random.uniform(0.05, 0.2))
                
                # Simulate failure if needed
                if not will_succeed:
                    logger.warning(f"Agent {self.id} task {task_id} failed")
                    raise RuntimeError("Simulated task failure")
                
                logger.info(f"Agent {self.id} task {task_id} succeeded")
            
            return {"task_id": task_id, "success": True}
        except Exception as e:
            return {"task_id": task_id, "success": False, "error": str(e)}
        finally:
            self.active_task_count -= 1


class StandaloneObservableAgent(ObservableAgent):
    """A simple standalone agent for observability demonstration."""
    
    def __init__(self, agent_id: str, agent_type: str):
        """
        Initialize an example agent.
        
        Args:
            agent_id: The agent ID
            agent_type: The type of agent (strategy, creative, media, etc.)
        """
        self.id = agent_id
        self.type = agent_type
        self.status = "initializing"
        self.tasks_started = 0
        self.tasks_completed = 0
        self.tasks_succeeded = 0
        self.tasks_failed = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.active_tasks = 0
        self.last_activity = datetime.now()
        self.metrics_collector = AgentMetricsCollector(agent_id)
        
        # Agent-specific metrics
        self.latency_ms = 100  # Simulated processing latency
        self.memory_usage = 50  # Simulated memory usage (MB)
        self.cpu_usage = 30     # Simulated CPU usage (%)
        
        logger.info(f"Agent {agent_id} ({agent_type}) initialized")
        self.status = "idle"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get the current metrics for the agent."""
        return {
            "tasks_started": self.tasks_started,
            "tasks_completed": self.tasks_completed,
            "tasks_succeeded": self.tasks_succeeded,
            "tasks_failed": self.tasks_failed,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "active_tasks": self.active_tasks,
            "latency_ms": self.latency_ms,
            "memory_usage": self.memory_usage,
            "cpu_usage": self.cpu_usage,
            "idle_time_seconds": (datetime.now() - self.last_activity).total_seconds()
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the agent."""
        return {
            "id": self.id,
            "type": self.type,
            "status": self.status,
            "last_activity": self.last_activity.isoformat()
        }
    
    def get_health(self) -> Dict[str, Any]:
        """Get the health status of the agent."""
        issues = []
        
        # Check various health indicators
        if self.active_tasks > 10:
            issues.append("High number of active tasks")
        
        if self.latency_ms > 500:
            issues.append("High processing latency")
        
        if self.memory_usage > 80:
            issues.append("High memory usage")
            
        if self.cpu_usage > 80:
            issues.append("High CPU usage")
        
        if (datetime.now() - self.last_activity).total_seconds() > 300:
            issues.append("Agent inactive for too long")
        
        # Determine overall status
        if any(issue in ["High memory usage", "High CPU usage"] for issue in issues):
            status = "critical"
        elif issues:
            status = "warning"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "issues": issues,
            "last_checked": datetime.now().isoformat()
        }
    
    def get_conversation_metrics(self, conversation_id: str) -> Dict[str, Any]:
        """Get metrics for a specific conversation."""
        # This is a simplified implementation
        return {
            "messages_count": random.randint(1, 10),
            "started_at": (datetime.now() - timedelta(hours=1)).isoformat(),
            "last_message_at": datetime.now().isoformat()
        }
    
    def get_task_metrics(self, task_type: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics for agent tasks."""
        # This is a simplified implementation
        return {
            "average_duration_ms": random.randint(50, 500),
            "success_rate": (self.tasks_succeeded / max(1, self.tasks_completed)) * 100
        }
    
    def simulate_task(self, task_type: str, succeed: bool = True) -> None:
        """
        Simulate a task execution.
        
        Args:
            task_type: The type of task
            succeed: Whether the task should succeed or fail
        """
        self.status = "busy"
        self.last_activity = datetime.now()
        self.tasks_started += 1
        self.active_tasks += 1
        
        # Record in metrics collector
        self.metrics_collector.record_task_started(task_type, f"task-{self.tasks_started}")
        
        # Simulate processing
        duration = random.uniform(0.1, 0.5)  # 100-500ms
        time.sleep(duration)
        
        # Update metrics
        self.tasks_completed += 1
        self.active_tasks -= 1
        
        if succeed:
            self.tasks_succeeded += 1
            logger.info(f"Agent {self.id} completed task {task_type} successfully")
        else:
            self.tasks_failed += 1
            logger.warning(f"Agent {self.id} failed task {task_type}")
        
        # Record in metrics collector
        self.metrics_collector.record_task_completed(
            task_type, 
            f"task-{self.tasks_started}", 
            duration, 
            succeed
        )
        
        # Update simulated metrics
        self.latency_ms = int(duration * 1000)  # Convert to ms
        self.memory_usage += random.randint(-10, 20)  # Simulate memory fluctuation
        self.memory_usage = max(10, min(95, self.memory_usage))  # Keep within reasonable range
        self.cpu_usage += random.randint(-5, 15)  # Simulate CPU fluctuation
        self.cpu_usage = max(5, min(95, self.cpu_usage))  # Keep within reasonable range
        
        self.status = "idle"
    
    def simulate_message(self, direction: str, message_type: str) -> None:
        """
        Simulate message sending or receiving.
        
        Args:
            direction: "send" or "receive"
            message_type: The type of message
        """
        self.last_activity = datetime.now()
        
        if direction == "send":
            self.messages_sent += 1
            self.metrics_collector.record_message_sent(
                message_type, 
                f"agent-{random.randint(1, 10)}",
                f"conversation-{random.randint(1, 5)}"
            )
            logger.info(f"Agent {self.id} sent {message_type} message")
        else:
            self.messages_received += 1
            self.metrics_collector.record_message_received(
                message_type, 
                f"agent-{random.randint(1, 10)}",
                f"conversation-{random.randint(1, 5)}"
            )
            logger.info(f"Agent {self.id} received {message_type} message")


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
    
    # Set up system monitor with metrics collector
    system_metrics = InMemoryMetricsCollector(storage)
    system_monitor = EnhancedSystemMonitor(system_metrics, alert_manager)
    
    # Set up agent observer with anomaly detection
    anomaly_detector = AnomalyDetector(alert_manager)
    agent_observer = StandardAgentObserver(system_metrics, alert_manager, anomaly_detector)
    system_monitor.register_observer(agent_observer)
    
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
        
        # Create dashboard for this agent
        system_monitor.dashboard_manager.create_agent_dashboard(agent_id)
    
    # Run the simulation
    logger.info("Starting observability simulation")
    
    # Monitor initial state
    for agent_id, agent in agents.items():
        system_monitor.monitor_entity(agent)
    
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
        
        # Short delay to spread out the simulation
        time.sleep(0.2)
    
    # Simulate an agent with health issues
    problem_agent = agents["agent-1"]
    problem_agent.error_count = 5  # Simulate errors
    problem_agent.cpu_usage = 92    # Simulate high CPU
    problem_agent.memory_usage = 88 # Simulate high memory
    
    # Simulate failed tasks
    for _ in range(5):
        problem_agent.simulate_task("critical_process", False)
    
    # Monitor the problematic agent
    system_monitor.monitor_entity(problem_agent)
    
    # Get system metrics and health
    system_metrics = system_monitor.get_system_metrics()
    system_health = system_monitor.get_system_health()
    
    # Get alerts
    alerts = system_monitor.get_alerts()
    
    # Get dashboards
    dashboards = system_monitor.get_dashboards()
    
    # Print summary
    logger.info("Simulation complete")
    logger.info(f"System health: {system_health['status']}")
    
    if "issues" in system_health and system_health["issues"]:
        logger.info(f"System issues: {', '.join(system_health['issues'])}")
    
    logger.info(f"Total dashboards: {len(dashboards)}")
    logger.info(f"Total alerts: {len(alerts)}")
    
    for alert in alerts[:5]:  # Just show first 5 alerts
        logger.info(f"Alert: [{alert['severity']}] {alert['message']}")
    
    return {
        "storage": storage,
        "protocol": protocol,
        "agents": agents,
        "alert_manager": alert_manager,
        "agent_observer": agent_observer,
        "system_monitor": system_monitor,
        "system_health": system_health,
        "alerts": alerts,
        "dashboards": dashboards
    }


def demonstrate_standalone_agents():
    """Demonstrate monitoring of standalone agents (without communication protocol)."""
    # Create complete observability system
    system_monitor, alert_manager, metrics_collector = create_observability_system()
    
    # Create some standalone agents
    agents = [
        StandaloneObservableAgent("strategy-agent-1", "strategy"),
        StandaloneObservableAgent("creative-agent-1", "creative"),
        StandaloneObservableAgent("media-agent-1", "media"),
        StandaloneObservableAgent("analytics-agent-1", "analytics")
    ]
    
    # Register a callback for alerts
    def alert_callback(alert):
        logger.warning(f"Alert received: {alert.get_severity()} - {alert.get_message()}")
    
    if isinstance(alert_manager, InMemoryAlertManager):
        alert_manager.register_alert_callback(alert_callback)
    
    # Run a simulation
    logger.info("Starting standalone agent monitoring demonstration")
    
    try:
        # Run for 30 iterations
        for i in range(30):
            # Randomly select an agent to perform an action
            agent = random.choice(agents)
            
            # Random action selection
            action = random.choice(["task", "message", "idle"])
            
            if action == "task":
                # Simulate a task with a 10% chance of failure
                agent.simulate_task(
                    random.choice(["process", "analyze", "create", "optimize"]),
                    succeed=random.random() > 0.1
                )
            elif action == "message":
                # Simulate a message
                agent.simulate_message(
                    random.choice(["send", "receive"]),
                    random.choice(["request", "response", "notification"])
                )
            
            # Monitor the agent
            system_monitor.monitor_entity(agent)
            
            # Wait a bit
            time.sleep(0.2)
            
            # Every 5 iterations, display some system information
            if i % 5 == 0:
                metrics = system_monitor.get_system_metrics()
                health = system_monitor.get_system_health()
                
                logger.info(f"System health: {health['status']}")
                
                if "issues" in health and health["issues"]:
                    logger.info(f"Issues: {', '.join(health['issues'])}")
                
                # Get dashboard information
                dashboards = system_monitor.get_dashboards()
                logger.info(f"Available dashboards: {len(dashboards)}")
                
                # Get alerts
                alerts = system_monitor.get_alerts()
                if alerts:
                    logger.info(f"Active alerts: {len(alerts)}")
                    for alert in alerts[:3]:  # Show just a few
                        logger.info(f"  {alert['severity']} - {alert['message']}")
        
        # Simulate some anomalous behavior
        logger.info("Simulating anomalous agent behavior...")
        problem_agent = agents[0]
        problem_agent.memory_usage = 90
        problem_agent.cpu_usage = 95
        problem_agent.latency_ms = 800
        system_monitor.monitor_entity(problem_agent)
        
        # Print final summary
        metrics = system_monitor.get_system_metrics()
        health = system_monitor.get_system_health()
        alerts = system_monitor.get_alerts()
        dashboards = system_monitor.get_dashboards()
        
        logger.info("Demonstration complete")
        logger.info(f"Final system health: {health['status']}")
        logger.info(f"Total alerts: {len(alerts)}")
        logger.info(f"Total dashboards: {len(dashboards)}")
    
    finally:
        # Shut down the system monitor
        system_monitor.shutdown()


if __name__ == "__main__":
    # First run the original example
    logger.info("RUNNING PROTOCOL-BASED EXAMPLE")
    run_observability_example()
    
    logger.info("\n" + "="*80 + "\n")
    
    # Then run the standalone agent example
    logger.info("RUNNING STANDALONE AGENT EXAMPLE")
    demonstrate_standalone_agents()