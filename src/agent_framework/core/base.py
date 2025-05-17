# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file provides the starting point for all our AI helpers. It's like a 
# template that has the basic parts filled in so we don't have to start from 
# scratch every time we make a new helper.

# High School Explanation:
# This module implements the abstract base classes for our agent framework. These
# classes provide default implementations of common functionality while still
# requiring agent-specific logic to be implemented in derived classes.

"""
Base implementations for the Agent Framework.

This module provides abstract base classes that implement common functionality
for the interfaces defined in the framework. These classes serve as a foundation
for building concrete agent implementations.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

from .interfaces import (
    BaseAgent, SetupAgent, OperationalAgent, CommunicatingAgent,
    ObservableAgent, ConfigurableAgent, ProcessAwareAgent,
    AgentInitializationError, AgentExecutionError, AgentConfigurationError
)

# Set up logging
logger = logging.getLogger(__name__)


class AbstractBaseAgent(BaseAgent):
    """
    Abstract base implementation of the BaseAgent interface.
    
    This class provides common functionality for all agents, including
    basic initialization, status tracking, and capability management.
    """
    
    def __init__(self, agent_id: str, name: str):
        """
        Initialize the abstract base agent.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name for this agent
        """
        self.agent_id = agent_id
        self.name = name
        self.config = {}
        self.status = {
            "health": "uninitialized",
            "state": "idle",
            "start_time": None,
            "last_executed": None
        }
        self.capabilities = []
        self.initialized = False
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the agent with the provided configuration.
        
        Args:
            config: Dictionary containing agent configuration parameters
            
        Returns:
            bool: True if initialization succeeded, False otherwise
        """
        try:
            # Store configuration
            self.config = config
            
            # Set status
            self.status["health"] = "healthy"
            self.status["start_time"] = datetime.now().isoformat()
            
            # Mark as initialized
            self.initialized = True
            
            # Log initialization
            logger.info(f"Agent {self.agent_id} ({self.name}) initialized successfully")
            
            return True
        except Exception as e:
            logger.error(f"Agent {self.agent_id} initialization failed: {str(e)}")
            self.status["health"] = "error"
            raise AgentInitializationError(f"Failed to initialize agent: {str(e)}")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's primary function with the given context.
        
        This method should be overridden by subclasses to implement
        agent-specific logic.
        
        Args:
            context: Dictionary containing execution context information
            
        Returns:
            Dict[str, Any]: Results of the agent's execution
        """
        if not self.initialized:
            raise AgentExecutionError("Agent not initialized")
        
        # Update status
        self.status["state"] = "executing"
        self.status["last_executed"] = datetime.now().isoformat()
        
        try:
            # Default implementation (to be overridden)
            result = {"success": False, "message": "Method not implemented"}
            
            # Update status
            self.status["state"] = "idle"
            
            return result
        except Exception as e:
            logger.error(f"Agent {self.agent_id} execution failed: {str(e)}")
            self.status["state"] = "error"
            raise AgentExecutionError(f"Execution failed: {str(e)}")
    
    def shutdown(self) -> bool:
        """
        Perform cleanup and resource release operations.
        
        Returns:
            bool: True if shutdown succeeded, False otherwise
        """
        try:
            # Update status
            self.status["health"] = "shutdown"
            self.status["state"] = "terminated"
            
            # Log shutdown
            logger.info(f"Agent {self.agent_id} ({self.name}) shutdown successfully")
            
            return True
        except Exception as e:
            logger.error(f"Agent {self.agent_id} shutdown failed: {str(e)}")
            return False
    
    def get_capabilities(self) -> List[str]:
        """
        Return a list of this agent's advertised capabilities.
        
        Returns:
            List[str]: Capability identifiers this agent supports
        """
        return self.capabilities
    
    def get_status(self) -> Dict[str, Any]:
        """
        Return the current status of the agent.
        
        Returns:
            Dict[str, Any]: Status information including health, state, and metrics
        """
        return {
            **self.status,
            "agent_id": self.agent_id,
            "name": self.name,
            "initialized": self.initialized,
            "uptime": self._calculate_uptime() if self.status["start_time"] else "Not started"
        }
    
    def _calculate_uptime(self) -> str:
        """
        Calculate the agent's uptime.
        
        Returns:
            str: Uptime in a human-readable format
        """
        if not self.status["start_time"]:
            return "Not started"
        
        start = datetime.fromisoformat(self.status["start_time"])
        now = datetime.now()
        delta = now - start
        
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"{days}d {hours}h {minutes}m {seconds}s"


class AbstractSetupAgent(AbstractBaseAgent, SetupAgent):
    """
    Abstract base implementation of the SetupAgent interface.
    
    This class extends AbstractBaseAgent with functionality specific
    to setup agents, including prerequisite checking and rollback.
    """
    
    def __init__(self, agent_id: str, name: str):
        """
        Initialize the abstract setup agent.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name for this agent
        """
        super().__init__(agent_id, name)
        self.prerequisites_checked = False
        self.setup_validated = False
        self.changes_made = []
    
    def check_prerequisites(self) -> Dict[str, Any]:
        """
        Check if all prerequisites for setup are satisfied.
        
        Returns:
            Dict[str, Any]: Status of prerequisites with any missing dependencies
        """
        # Default implementation (to be overridden)
        self.prerequisites_checked = True
        return {
            "satisfied": True,
            "missing": []
        }
    
    def validate_setup(self) -> Dict[str, Any]:
        """
        Validate that setup was completed successfully.
        
        Returns:
            Dict[str, Any]: Validation results including any issues found
        """
        # Default implementation (to be overridden)
        self.setup_validated = True
        return {
            "valid": True,
            "issues": []
        }
    
    def rollback(self) -> bool:
        """
        Roll back changes if setup fails midway.
        
        Returns:
            bool: True if rollback succeeded, False otherwise
        """
        # Default implementation (to be overridden)
        logger.info(f"Rolling back changes for agent {self.agent_id}")
        self.changes_made = []
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the setup operation.
        
        This implementation adds prerequisite checking and validation
        around the actual setup operation.
        
        Args:
            context: Dictionary containing execution context information
            
        Returns:
            Dict[str, Any]: Results of the setup operation
        """
        if not self.initialized:
            raise AgentExecutionError("Agent not initialized")
        
        # Update status
        self.status["state"] = "executing"
        self.status["last_executed"] = datetime.now().isoformat()
        
        try:
            # Check prerequisites
            prereq_result = self.check_prerequisites()
            if not prereq_result["satisfied"]:
                return {
                    "success": False,
                    "stage": "prerequisites",
                    "message": "Prerequisites not satisfied",
                    "details": prereq_result
                }
            
            # Perform setup (to be implemented by subclass)
            result = self._perform_setup(context)
            
            # Add to changes made
            if result.get("success", False):
                if "changes" in result:
                    self.changes_made.extend(result["changes"])
            
            # Validate setup if successful
            if result.get("success", False):
                validation = self.validate_setup()
                if not validation["valid"]:
                    # Attempt rollback
                    rollback_success = self.rollback()
                    return {
                        "success": False,
                        "stage": "validation",
                        "message": "Setup validation failed",
                        "validation": validation,
                        "rollback_success": rollback_success
                    }
                result["validation"] = validation
            
            # Update status
            self.status["state"] = "idle"
            
            return result
        except Exception as e:
            logger.error(f"Setup agent {self.agent_id} execution failed: {str(e)}")
            self.status["state"] = "error"
            
            # Attempt rollback
            try:
                rollback_success = self.rollback()
            except Exception as re:
                rollback_success = False
                logger.error(f"Rollback also failed: {str(re)}")
            
            raise AgentExecutionError(f"Setup failed: {str(e)}, Rollback successful: {rollback_success}")
    
    def _perform_setup(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform the actual setup operation.
        
        This method should be overridden by subclasses to implement
        the specific setup logic.
        
        Args:
            context: Dictionary containing execution context information
            
        Returns:
            Dict[str, Any]: Results of the setup operation
        """
        # Default implementation (to be overridden)
        return {
            "success": False,
            "message": "Setup not implemented"
        }


class AbstractOperationalAgent(AbstractBaseAgent, OperationalAgent):
    """
    Abstract base implementation of the OperationalAgent interface.
    
    This class extends AbstractBaseAgent with functionality specific
    to operational agents, including pause/resume capabilities.
    """
    
    def __init__(self, agent_id: str, name: str):
        """
        Initialize the abstract operational agent.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name for this agent
        """
        super().__init__(agent_id, name)
        self.paused = False
    
    def pause(self) -> bool:
        """
        Temporarily pause the agent's operations.
        
        Returns:
            bool: True if successfully paused, False otherwise
        """
        logger.info(f"Pausing agent {self.agent_id}")
        self.paused = True
        self.status["state"] = "paused"
        return True
    
    def resume(self) -> bool:
        """
        Resume the agent's operations after being paused.
        
        Returns:
            bool: True if successfully resumed, False otherwise
        """
        logger.info(f"Resuming agent {self.agent_id}")
        self.paused = False
        self.status["state"] = "idle"
        return True
    
    def should_execute(self, context: Dict[str, Any]) -> bool:
        """
        Determine if the agent should execute based on the context.
        
        Args:
            context: Dictionary containing execution context information
            
        Returns:
            bool: True if the agent should execute, False otherwise
        """
        # Don't execute if paused
        if self.paused:
            return False
        
        # Default implementation (to be overridden)
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's primary function with the given context.
        
        This implementation checks if execution should proceed before
        delegating to the actual operation.
        
        Args:
            context: Dictionary containing execution context information
            
        Returns:
            Dict[str, Any]: Results of the agent's execution
        """
        if not self.initialized:
            raise AgentExecutionError("Agent not initialized")
        
        # Check if should execute
        if not self.should_execute(context):
            return {
                "success": False,
                "message": "Execution skipped",
                "reason": "Agent determined execution should be skipped"
            }
        
        # Update status
        self.status["state"] = "executing"
        self.status["last_executed"] = datetime.now().isoformat()
        
        try:
            # Perform operation (to be implemented by subclass)
            result = self._perform_operation(context)
            
            # Update status
            self.status["state"] = "idle"
            
            return result
        except Exception as e:
            logger.error(f"Operational agent {self.agent_id} execution failed: {str(e)}")
            self.status["state"] = "error"
            raise AgentExecutionError(f"Operation failed: {str(e)}")
    
    def _perform_operation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform the actual operation.
        
        This method should be overridden by subclasses to implement
        the specific operational logic.
        
        Args:
            context: Dictionary containing execution context information
            
        Returns:
            Dict[str, Any]: Results of the operation
        """
        # Default implementation (to be overridden)
        return {
            "success": False,
            "message": "Operation not implemented"
        }


class AbstractCommunicatingAgent(AbstractBaseAgent, CommunicatingAgent):
    """
    Abstract base implementation of the CommunicatingAgent interface.
    
    This class extends AbstractBaseAgent with messaging capabilities
    for inter-agent communication.
    """
    
    def __init__(self, agent_id: str, name: str, message_broker=None):
        """
        Initialize the abstract communicating agent.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name for this agent
            message_broker: Optional message broker for sending messages
        """
        super().__init__(agent_id, name)
        self.message_broker = message_broker
        self.subscribed_topics = []
        self.message_handlers = {}
        self.sent_messages = []
        self.received_messages = []
    
    def send_message(self, recipient_id: str, message_type: str, content: Dict[str, Any]) -> str:
        """
        Send a message to another agent.
        
        Args:
            recipient_id: Identifier of the recipient agent
            message_type: Type of message being sent
            content: Dictionary containing the message content
            
        Returns:
            str: Message ID for tracking/reference
        """
        # Generate message ID
        message_id = str(uuid.uuid4())
        
        # Create message
        message = {
            "message_id": message_id,
            "sender_id": self.agent_id,
            "recipient_id": recipient_id,
            "timestamp": datetime.now().isoformat(),
            "message_type": message_type,
            "content": content
        }
        
        # Store in sent messages
        self.sent_messages.append(message)
        
        # Send via broker if available
        if self.message_broker:
            self.message_broker.send_message(message)
            logger.debug(f"Message {message_id} sent to {recipient_id} via broker")
        else:
            logger.warning(f"No message broker available, message {message_id} not sent")
        
        return message_id
    
    def receive_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a received message.
        
        Args:
            message: Dictionary containing the message data
            
        Returns:
            Dict[str, Any]: Processing result or response
        """
        # Store in received messages
        self.received_messages.append(message)
        
        # Log message receipt
        logger.debug(f"Message {message.get('message_id', 'unknown')} received from {message.get('sender_id', 'unknown')}")
        
        # Process based on message type
        message_type = message.get("message_type")
        if message_type in self.message_handlers:
            return self.message_handlers[message_type](message)
        else:
            logger.warning(f"No handler for message type: {message_type}")
            return {
                "success": False,
                "message": f"No handler for message type: {message_type}"
            }
    
    def list_subscribed_topics(self) -> List[str]:
        """
        List message topics this agent is subscribed to.
        
        Returns:
            List[str]: Topic identifiers
        """
        return self.subscribed_topics.copy()
    
    def register_message_handler(self, message_type: str, handler_func):
        """
        Register a handler function for a specific message type.
        
        Args:
            message_type: Type of message to handle
            handler_func: Function to call for this message type
        """
        self.message_handlers[message_type] = handler_func
        logger.debug(f"Registered handler for message type: {message_type}")
    
    def subscribe_to_topic(self, topic: str):
        """
        Subscribe to a message topic.
        
        Args:
            topic: Topic identifier
        """
        if topic not in self.subscribed_topics:
            self.subscribed_topics.append(topic)
            
            # Subscribe via broker if available
            if self.message_broker:
                self.message_broker.subscribe(self.agent_id, topic)
            
            logger.debug(f"Subscribed to topic: {topic}")


class AbstractObservableAgent(AbstractBaseAgent, ObservableAgent):
    """
    Abstract base implementation of the ObservableAgent interface.
    
    This class extends AbstractBaseAgent with monitoring capabilities
    for metrics, logs, and traces.
    """
    
    def __init__(self, agent_id: str, name: str):
        """
        Initialize the abstract observable agent.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name for this agent
        """
        super().__init__(agent_id, name)
        self.metrics = {}
        self.logs = []
        self.traces = {}
        self.current_trace_id = None
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance and operational metrics.
        
        Returns:
            Dict[str, Any]: Metrics keyed by metric name
        """
        return self.metrics.copy()
    
    def get_logs(self, start_time: datetime, end_time: datetime, 
                level: str = "INFO") -> List[Dict[str, Any]]:
        """
        Retrieve logs for a specific time period and level.
        
        Args:
            start_time: Start of the time period
            end_time: End of the time period
            level: Minimum log level to retrieve
            
        Returns:
            List[Dict[str, Any]]: Log entries matching criteria
        """
        # Filter logs by time and level
        level_order = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
        min_level = level_order.get(level.upper(), 0)
        
        filtered_logs = []
        for log in self.logs:
            log_time = datetime.fromisoformat(log["timestamp"])
            log_level = level_order.get(log["level"].upper(), 0)
            
            if (start_time <= log_time <= end_time and log_level >= min_level):
                filtered_logs.append(log)
        
        return filtered_logs
    
    def get_traces(self, trace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get execution traces for debugging and performance analysis.
        
        Args:
            trace_id: Optional specific trace to retrieve
            
        Returns:
            List[Dict[str, Any]]: Trace data
        """
        if trace_id:
            # Return specific trace if it exists
            return [self.traces[trace_id]] if trace_id in self.traces else []
        else:
            # Return all traces
            return list(self.traces.values())
    
    def log(self, level: str, message: str, **kwargs):
        """
        Add a log entry.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            **kwargs: Additional log data
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "agent_id": self.agent_id,
            "message": message,
            "data": kwargs
        }
        
        # Add to internal logs
        self.logs.append(log_entry)
        
        # Also log to Python's logging system
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(f"[{self.agent_id}] {message}")
    
    def start_trace(self, operation: str, context: Dict[str, Any]) -> str:
        """
        Start a new execution trace.
        
        Args:
            operation: Name of the operation being traced
            context: Context information for the trace
            
        Returns:
            str: Trace ID
        """
        trace_id = str(uuid.uuid4())
        
        trace = {
            "trace_id": trace_id,
            "agent_id": self.agent_id,
            "operation": operation,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_ms": None,
            "context": context,
            "steps": [],
            "result": None,
            "status": "in_progress"
        }
        
        self.traces[trace_id] = trace
        self.current_trace_id = trace_id
        
        return trace_id
    
    def add_trace_step(self, description: str, **kwargs):
        """
        Add a step to the current trace.
        
        Args:
            description: Description of the step
            **kwargs: Additional step data
        """
        if not self.current_trace_id:
            logger.warning("No active trace to add step to")
            return
        
        step = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "data": kwargs
        }
        
        self.traces[self.current_trace_id]["steps"].append(step)
    
    def end_trace(self, result: Dict[str, Any], status: str = "completed"):
        """
        End the current trace.
        
        Args:
            result: Result of the traced operation
            status: Final status (completed, failed, aborted)
        """
        if not self.current_trace_id:
            logger.warning("No active trace to end")
            return
        
        trace = self.traces[self.current_trace_id]
        
        # Record end time and calculate duration
        end_time = datetime.now()
        start_time = datetime.fromisoformat(trace["start_time"])
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Update trace
        trace["end_time"] = end_time.isoformat()
        trace["duration_ms"] = duration_ms
        trace["result"] = result
        trace["status"] = status
        
        # Clear current trace
        self.current_trace_id = None


class AbstractConfigurableAgent(AbstractBaseAgent, ConfigurableAgent):
    """
    Abstract base implementation of the ConfigurableAgent interface.
    
    This class extends AbstractBaseAgent with configuration management
    capabilities for dynamic behavior modification.
    """
    
    def __init__(self, agent_id: str, name: str):
        """
        Initialize the abstract configurable agent.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name for this agent
        """
        super().__init__(agent_id, name)
        self.config_schema = self._get_default_config_schema()
        self.config_history = []
    
    def update_config(self, config_updates: Dict[str, Any]) -> bool:
        """
        Update agent configuration dynamically.
        
        Args:
            config_updates: Dictionary containing configuration updates
            
        Returns:
            bool: True if update succeeded, False otherwise
        """
        # Validate updates against schema
        valid, errors = self.validate_config({**self.config, **config_updates})
        if not valid:
            logger.error(f"Invalid configuration updates: {errors}")
            return False
        
        # Store current config in history
        self.config_history.append({
            "timestamp": datetime.now().isoformat(),
            "config": self.config.copy()
        })
        
        # Apply updates
        self.config.update(config_updates)
        
        # Apply configuration changes
        try:
            self._apply_config_changes(config_updates)
            logger.info(f"Configuration updated for agent {self.agent_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply configuration changes: {str(e)}")
            # Rollback to previous config
            if self.config_history:
                self.config = self.config_history[-1]["config"].copy()
            return False
    
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema defining valid configuration options.
        
        Returns:
            Dict[str, Any]: JSON schema for agent configuration
        """
        return self.config_schema
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a configuration against the agent's schema.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        # Basic validation implementation (schema-based validation would be more robust)
        errors = []
        
        # Check required fields
        for field in self.config_schema.get("required", []):
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Check field types (very basic)
        properties = self.config_schema.get("properties", {})
        for field, value in config.items():
            if field in properties:
                field_type = properties[field].get("type")
                if field_type == "string" and not isinstance(value, str):
                    errors.append(f"Field {field} should be a string")
                elif field_type == "number" and not isinstance(value, (int, float)):
                    errors.append(f"Field {field} should be a number")
                elif field_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"Field {field} should be a boolean")
                elif field_type == "array" and not isinstance(value, list):
                    errors.append(f"Field {field} should be an array")
                elif field_type == "object" and not isinstance(value, dict):
                    errors.append(f"Field {field} should be an object")
        
        # Add custom validation (to be overridden by subclasses)
        custom_errors = self._custom_config_validation(config)
        errors.extend(custom_errors)
        
        return len(errors) == 0, errors
    
    def _get_default_config_schema(self) -> Dict[str, Any]:
        """
        Get the default configuration schema for this agent.
        
        Returns:
            Dict[str, Any]: Default JSON schema
        """
        # Default schema (to be overridden by subclasses)
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "enabled": {"type": "boolean"}
            },
            "required": ["name", "enabled"]
        }
    
    def _apply_config_changes(self, config_updates: Dict[str, Any]):
        """
        Apply configuration changes to the agent.
        
        This method should be overridden by subclasses to implement
        agent-specific configuration handling.
        
        Args:
            config_updates: Dictionary containing configuration updates
        """
        # Default implementation does nothing
        pass
    
    def _custom_config_validation(self, config: Dict[str, Any]) -> List[str]:
        """
        Perform custom validation on configuration.
        
        This method should be overridden by subclasses to implement
        agent-specific validation logic.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List[str]: List of validation errors
        """
        # Default implementation returns no errors
        return []


class AbstractProcessAwareAgent(AbstractOperationalAgent, ProcessAwareAgent):
    """
    Abstract base implementation of the ProcessAwareAgent interface.
    
    This class extends AbstractOperationalAgent with capabilities for
    executing activities defined in standard process frameworks like
    APQC or eTOM.
    """
    
    def __init__(self, agent_id: str, name: str):
        """
        Initialize the abstract process-aware agent.
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name for this agent
        """
        super().__init__(agent_id, name)
        self.supported_activities = {}
        self.process_repository = None
    
    def get_supported_activities(self) -> List[Dict[str, Any]]:
        """
        Returns activities this agent can perform from the process framework.
        
        Returns:
            List[Dict[str, Any]]: List of supported activities with framework identifiers
        """
        return [
            {
                "activity_id": activity_id,
                "framework": info["framework"],
                "name": info["name"],
                "description": info["description"]
            }
            for activity_id, info in self.supported_activities.items()
        ]
    
    def execute_activity(self, activity_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific activity from the process framework.
        
        Args:
            activity_id: Framework-specific activity identifier
            context: Activity execution context
            
        Returns:
            Dict[str, Any]: Activity execution results
        """
        # Check if activity is supported
        if activity_id not in self.supported_activities:
            logger.warning(f"Activity {activity_id} not supported by agent {self.agent_id}")
            return {
                "success": False,
                "message": f"Activity {activity_id} not supported",
                "activity_id": activity_id
            }
        
        # Update status
        self.status["state"] = f"executing_activity:{activity_id}"
        self.status["last_executed"] = datetime.now().isoformat()
        
        try:
            # Get activity implementation
            activity_impl = self.supported_activities[activity_id].get("implementation")
            if not activity_impl:
                return {
                    "success": False,
                    "message": f"No implementation for activity {activity_id}",
                    "activity_id": activity_id
                }
            
            # Execute activity
            result = activity_impl(context)
            
            # Update status
            self.status["state"] = "idle"
            
            # Add activity metadata to result
            result["activity_id"] = activity_id
            result["framework"] = self.supported_activities[activity_id]["framework"]
            
            return result
        except Exception as e:
            logger.error(f"Activity {activity_id} execution failed: {str(e)}")
            self.status["state"] = "error"
            raise AgentExecutionError(f"Activity execution failed: {str(e)}")
    
    def get_activity_requirements(self, activity_id: str) -> Dict[str, Any]:
        """
        Get input requirements for executing a specific activity.
        
        Args:
            activity_id: Framework-specific activity identifier
            
        Returns:
            Dict[str, Any]: Input requirements for the activity
        """
        # Check if activity is supported
        if activity_id not in self.supported_activities:
            logger.warning(f"Activity {activity_id} not supported by agent {self.agent_id}")
            return {
                "supported": False,
                "message": f"Activity {activity_id} not supported",
                "activity_id": activity_id
            }
        
        # Return requirements
        return {
            "supported": True,
            "activity_id": activity_id,
            "framework": self.supported_activities[activity_id]["framework"],
            "required_inputs": self.supported_activities[activity_id].get("required_inputs", []),
            "optional_inputs": self.supported_activities[activity_id].get("optional_inputs", [])
        }
    
    def register_activity(self, activity_id: str, framework: str, name: str, 
                         description: str, implementation=None, 
                         required_inputs=None, optional_inputs=None):
        """
        Register an activity that this agent can perform.
        
        Args:
            activity_id: Framework-specific activity identifier
            framework: Process framework identifier (e.g., "apqc", "etom")
            name: Human-readable activity name
            description: Activity description
            implementation: Function to execute for this activity
            required_inputs: List of required input fields
            optional_inputs: List of optional input fields
        """
        self.supported_activities[activity_id] = {
            "framework": framework,
            "name": name,
            "description": description,
            "implementation": implementation,
            "required_inputs": required_inputs or [],
            "optional_inputs": optional_inputs or []
        }
        
        logger.debug(f"Registered activity {activity_id} ({framework}) for agent {self.agent_id}")
    
    def _perform_operation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform the operational function.
        
        For process-aware agents, this checks if the context specifies
        a particular activity to execute.
        
        Args:
            context: Dictionary containing execution context information
            
        Returns:
            Dict[str, Any]: Results of the operation
        """
        # Check if context specifies an activity
        activity_id = context.get("activity_id")
        if activity_id:
            return self.execute_activity(activity_id, context)
        
        # Default to normal operation (to be overridden)
        return {
            "success": False,
            "message": "No activity specified and no default operation implemented"
        }