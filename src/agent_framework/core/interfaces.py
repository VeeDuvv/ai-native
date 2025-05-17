# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file defines the rules that all our AI helpers must follow. It's like 
# a rulebook for a game that explains what moves each player can make and 
# how they should play together.

# High School Explanation:
# This module defines the core interfaces that all agents must implement. These 
# interfaces establish the contract between agents and the framework, ensuring 
# consistent behavior and interoperability across different agent implementations.

"""
Core interfaces for the Agent Framework.

This module defines the fundamental interfaces that all agents must implement
to participate in the agent ecosystem. These interfaces ensure consistent
behavior, predictable lifecycle management, and standardized communication.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

class BaseAgent(ABC):
    """
    Base interface that all agents must implement in our system.
    
    This interface defines the fundamental methods that every agent
    must support, regardless of its specific role or capabilities.
    """
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the agent with the provided configuration.
        
        Args:
            config: Dictionary containing agent configuration parameters
            
        Returns:
            bool: True if initialization succeeded, False otherwise
        """
        pass
        
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's primary function with the given context.
        
        Args:
            context: Dictionary containing execution context information
            
        Returns:
            Dict[str, Any]: Results of the agent's execution
        """
        pass
        
    @abstractmethod
    def shutdown(self) -> bool:
        """
        Perform cleanup and resource release operations.
        
        Returns:
            bool: True if shutdown succeeded, False otherwise
        """
        pass
        
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return a list of this agent's advertised capabilities.
        
        Returns:
            List[str]: Capability identifiers this agent supports
        """
        pass
        
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Return the current status of the agent.
        
        Returns:
            Dict[str, Any]: Status information including health, state, and metrics
        """
        pass


class SetupAgent(BaseAgent):
    """
    Interface for agents that perform one-time initialization tasks.
    
    Setup agents handle tasks that are typically executed once during
    system initialization or configuration. They include methods for
    checking prerequisites, validating setup, and rolling back changes
    if necessary.
    """
    
    @abstractmethod
    def check_prerequisites(self) -> Dict[str, Any]:
        """
        Check if all prerequisites for setup are satisfied.
        
        Returns:
            Dict[str, Any]: Status of prerequisites with any missing dependencies
        """
        pass
    
    @abstractmethod
    def validate_setup(self) -> Dict[str, Any]:
        """
        Validate that setup was completed successfully.
        
        Returns:
            Dict[str, Any]: Validation results including any issues found
        """
        pass
    
    @abstractmethod
    def rollback(self) -> bool:
        """
        Roll back changes if setup fails midway.
        
        Returns:
            bool: True if rollback succeeded, False otherwise
        """
        pass


class OperationalAgent(BaseAgent):
    """
    Interface for agents that perform recurring operational tasks.
    
    Operational agents handle ongoing business processes and are invoked
    regularly as part of normal system operation. They include methods
    for pausing, resuming, and determining execution conditions.
    """
    
    @abstractmethod
    def pause(self) -> bool:
        """
        Temporarily pause the agent's operations.
        
        Returns:
            bool: True if successfully paused, False otherwise
        """
        pass
    
    @abstractmethod
    def resume(self) -> bool:
        """
        Resume the agent's operations after being paused.
        
        Returns:
            bool: True if successfully resumed, False otherwise
        """
        pass
    
    @abstractmethod
    def should_execute(self, context: Dict[str, Any]) -> bool:
        """
        Determine if the agent should execute based on the context.
        
        Args:
            context: Dictionary containing execution context information
            
        Returns:
            bool: True if the agent should execute, False otherwise
        """
        pass


class CommunicatingAgent(BaseAgent):
    """
    Interface for agents that communicate with other agents.
    
    Communicating agents can send and receive messages to/from other
    agents in the system. They implement methods for message handling
    and topic subscription.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def receive_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a received message.
        
        Args:
            message: Dictionary containing the message data
            
        Returns:
            Dict[str, Any]: Processing result or response
        """
        pass
    
    @abstractmethod
    def list_subscribed_topics(self) -> List[str]:
        """
        List message topics this agent is subscribed to.
        
        Returns:
            List[str]: Topic identifiers
        """
        pass


class ObservableAgent(BaseAgent):
    """
    Interface for agents that expose detailed operational metrics and logs.
    
    Observable agents provide rich information about their internal state,
    performance, and behavior for monitoring and debugging purposes.
    """
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance and operational metrics.
        
        Returns:
            Dict[str, Any]: Metrics keyed by metric name
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_traces(self, trace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get execution traces for debugging and performance analysis.
        
        Args:
            trace_id: Optional specific trace to retrieve
            
        Returns:
            List[Dict[str, Any]]: Trace data
        """
        pass


class ConfigurableAgent(BaseAgent):
    """
    Interface for agents with advanced configuration capabilities.
    
    Configurable agents can have their behavior modified dynamically through
    configuration updates. They provide methods for validating and applying
    configuration changes.
    """
    
    @abstractmethod
    def update_config(self, config_updates: Dict[str, Any]) -> bool:
        """
        Update agent configuration dynamically.
        
        Args:
            config_updates: Dictionary containing configuration updates
            
        Returns:
            bool: True if update succeeded, False otherwise
        """
        pass
    
    @abstractmethod
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema defining valid configuration options.
        
        Returns:
            Dict[str, Any]: JSON schema for agent configuration
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a configuration against the agent's schema.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        pass


class ProcessAwareAgent(OperationalAgent):
    """
    Interface for agents that execute activities defined in process frameworks.
    
    Process-aware agents can interpret and execute activities from standard
    process frameworks like APQC or eTOM. They provide methods for identifying
    supported activities and executing specific process steps.
    """
    
    @abstractmethod
    def get_supported_activities(self) -> List[Dict[str, Any]]:
        """
        Returns activities this agent can perform from the process framework.
        
        Returns:
            List[Dict[str, Any]]: List of supported activities with framework identifiers
        """
        pass
    
    @abstractmethod
    def execute_activity(self, activity_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific activity from the process framework.
        
        Args:
            activity_id: Framework-specific activity identifier
            context: Activity execution context
            
        Returns:
            Dict[str, Any]: Activity execution results
        """
        pass
    
    @abstractmethod
    def get_activity_requirements(self, activity_id: str) -> Dict[str, Any]:
        """
        Get input requirements for executing a specific activity.
        
        Args:
            activity_id: Framework-specific activity identifier
            
        Returns:
            Dict[str, Any]: Input requirements for the activity
        """
        pass


# Define exception hierarchy for agent-related errors

class AgentException(Exception):
    """Base exception for all agent-related errors."""
    pass

class AgentInitializationError(AgentException):
    """Raised when an agent fails to initialize."""
    pass

class AgentExecutionError(AgentException):
    """Raised when an agent encounters an error during execution."""
    pass

class AgentCommunicationError(AgentException):
    """Raised when there is an error in agent communication."""
    pass

class AgentConfigurationError(AgentException):
    """Raised when there is an error in agent configuration."""
    pass

class AgentResourceError(AgentException):
    """Raised when an agent cannot access required resources."""
    pass