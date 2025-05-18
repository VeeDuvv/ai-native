# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps our AI agents understand how to work with business processes.
# It's like giving them a special guide on how to read and follow the business
# recipes we've created.

# High School Explanation:
# This module defines the ProcessAwareAgent interface, which extends the base
# agent interfaces to provide process framework integration. It enables agents
# to discover, execute, and report on activities from standard process frameworks.

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union

from ..agent_framework.core.interfaces import OperationalAgent
from .core import Activity, ProcessStatus


class ProcessAwareAgent(OperationalAgent, ABC):
    """Agent interface for process-aware operational agents.
    
    This interface extends the base OperationalAgent interface with
    process-specific capabilities, allowing agents to participate in
    standardized business processes.
    """
    
    @abstractmethod
    def get_supported_activities(self) -> List[Dict[str, Any]]:
        """Returns activities this agent can perform from the process framework.
        
        This method allows the agent to declare which activities from the
        process framework it can execute, along with their framework identifiers.
        
        Returns:
            List[Dict]: List of supported activities with framework identifiers
        """
        pass
    
    @abstractmethod
    def execute_activity(self, activity_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific activity from the process framework.
        
        This method executes an activity identified by its framework ID,
        using the provided context for inputs and parameters.
        
        Args:
            activity_id: Framework-specific activity identifier
            context: Activity execution context with inputs
            
        Returns:
            Dict: Activity execution results/outputs
            
        Raises:
            ValueError: If the activity is not supported or invalid
            RuntimeError: If the activity execution fails
        """
        pass
    
    @abstractmethod
    def get_activity_requirements(self, activity_id: str) -> Dict[str, Any]:
        """Get input requirements for executing a specific activity.
        
        This method returns the input requirements for an activity,
        which can be used to validate and prepare the execution context.
        
        Args:
            activity_id: Framework-specific activity identifier
            
        Returns:
            Dict: Input requirements for the activity
            
        Raises:
            ValueError: If the activity is not supported or invalid
        """
        pass
    
    @abstractmethod
    def verify_activity_result(self, activity_id: str, result: Dict[str, Any]) -> bool:
        """Verify that an activity result meets the expected output requirements.
        
        This method validates the outputs of an activity against the expected
        output schema defined in the process framework.
        
        Args:
            activity_id: Framework-specific activity identifier
            result: Activity execution result
            
        Returns:
            bool: True if the result is valid, False otherwise
        """
        pass


class BaseProcessAwareAgent(ProcessAwareAgent):
    """Base implementation of the ProcessAwareAgent interface.
    
    This class provides a partial implementation of the ProcessAwareAgent
    interface, handling common functionality while leaving specific
    implementations to derived classes.
    """
    
    def __init__(self, agent_id: str, name: str) -> None:
        """Initialize the base process-aware agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
        """
        super().__init__(agent_id, name)
        self._activity_handlers: Dict[str, callable] = {}
        self._activity_requirements: Dict[str, Dict[str, Any]] = {}
        
    def register_activity_handler(self, 
                                 activity_id: str, 
                                 handler: callable,
                                 requirements: Dict[str, Any]) -> None:
        """Register a handler for a specific activity.
        
        Args:
            activity_id: Framework-specific activity identifier
            handler: Function to execute the activity
            requirements: Input requirements for the activity
        """
        self._activity_handlers[activity_id] = handler
        self._activity_requirements[activity_id] = requirements
        
    def get_supported_activities(self) -> List[Dict[str, Any]]:
        """Returns activities this agent can perform from the process framework.
        
        Returns:
            List of supported activities with their requirements
        """
        return [
            {
                "activity_id": activity_id,
                "requirements": requirements
            }
            for activity_id, requirements in self._activity_requirements.items()
        ]
    
    def execute_activity(self, activity_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific activity from the process framework.
        
        Args:
            activity_id: Framework-specific activity identifier
            context: Activity execution context with inputs
            
        Returns:
            Activity execution results/outputs
            
        Raises:
            ValueError: If the activity is not supported
            RuntimeError: If the activity execution fails
        """
        # Check if the activity is supported
        if activity_id not in self._activity_handlers:
            raise ValueError(f"Activity {activity_id} is not supported by this agent")
            
        # Get the handler
        handler = self._activity_handlers[activity_id]
        
        # Execute the activity
        try:
            return handler(context)
        except Exception as e:
            raise RuntimeError(f"Error executing activity {activity_id}: {str(e)}")
    
    def get_activity_requirements(self, activity_id: str) -> Dict[str, Any]:
        """Get input requirements for executing a specific activity.
        
        Args:
            activity_id: Framework-specific activity identifier
            
        Returns:
            Input requirements for the activity
            
        Raises:
            ValueError: If the activity is not supported
        """
        # Check if the activity is supported
        if activity_id not in self._activity_requirements:
            raise ValueError(f"Activity {activity_id} is not supported by this agent")
            
        return self._activity_requirements[activity_id]
    
    def verify_activity_result(self, activity_id: str, result: Dict[str, Any]) -> bool:
        """Verify that an activity result meets the expected output requirements.
        
        Args:
            activity_id: Framework-specific activity identifier
            result: Activity execution result
            
        Returns:
            True if the result is valid, False otherwise
        """
        # For now, simply return True
        # A more sophisticated implementation would validate the result against an output schema
        return True


class AgentWorkflowManager:
    """Manages the interaction between agents and the workflow engine.
    
    This class provides a simplified interface for agents to interact with the
    workflow engine, hiding the complexity of the underlying workflow system.
    """
    
    def __init__(self, workflow_engine):
        """Initialize the agent workflow manager.
        
        Args:
            workflow_engine: The workflow engine to use
        """
        self.workflow_engine = workflow_engine
        
    def register_agent(self, agent: ProcessAwareAgent) -> None:
        """Register an agent with the workflow engine.
        
        Args:
            agent: The agent to register
        """
        # Extract supported activities and their capabilities
        activities = agent.get_supported_activities()
        capabilities = [activity["activity_id"] for activity in activities]
        
        # Register with workflow engine
        self.workflow_engine.register_agent(agent.id, capabilities)
        
    def unregister_agent(self, agent: ProcessAwareAgent) -> None:
        """Unregister an agent from the workflow engine.
        
        Args:
            agent: The agent to unregister
        """
        self.workflow_engine.unregister_agent(agent.id)
        
    def get_agent_assignments(self, agent: ProcessAwareAgent) -> List[Dict[str, Any]]:
        """Get current activity assignments for an agent.
        
        Args:
            agent: The agent to get assignments for
            
        Returns:
            List of assignment details
        """
        assignments = self.workflow_engine.get_agent_assignments(agent.id)
        
        return [
            {
                "activity_id": assignment.activity_instance.activity_id,
                "activity_instance_id": assignment.activity_instance.instance_id,
                "process_instance_id": assignment.activity_instance.process_instance_id,
                "inputs": assignment.inputs,
                "assigned_at": assignment.assigned_at
            }
            for assignment in assignments
        ]
        
    def start_activity(self, 
                      agent: ProcessAwareAgent,
                      activity_instance_id: str) -> bool:
        """Start execution of an assigned activity.
        
        Args:
            agent: The agent executing the activity
            activity_instance_id: ID of the activity instance
            
        Returns:
            True if the activity was started, False otherwise
        """
        # Check if the agent has this assignment
        assignments = self.workflow_engine.get_agent_assignments(agent.id)
        assignment = next(
            (a for a in assignments if a.activity_instance.instance_id == activity_instance_id),
            None
        )
        
        if not assignment:
            return False
            
        # Start the activity
        return self.workflow_engine.start_activity(activity_instance_id)
        
    def complete_activity(self,
                         agent: ProcessAwareAgent,
                         activity_instance_id: str,
                         outputs: Dict[str, Any]) -> bool:
        """Complete an activity with its outputs.
        
        Args:
            agent: The agent that executed the activity
            activity_instance_id: ID of the activity instance
            outputs: Output values from the activity
            
        Returns:
            True if the activity was completed, False otherwise
        """
        # Get the assignment
        assignment = self.workflow_engine.get_activity_assignment(activity_instance_id)
        
        if not assignment or assignment.agent_id != agent.id:
            return False
            
        # Complete the activity
        return self.workflow_engine.complete_activity(activity_instance_id, outputs)
        
    def fail_activity(self,
                     agent: ProcessAwareAgent,
                     activity_instance_id: str,
                     error: str) -> bool:
        """Mark an activity as failed.
        
        Args:
            agent: The agent that attempted the activity
            activity_instance_id: ID of the activity instance
            error: Error message
            
        Returns:
            True if the activity was marked as failed, False otherwise
        """
        # Get the assignment
        assignment = self.workflow_engine.get_activity_assignment(activity_instance_id)
        
        if not assignment or assignment.agent_id != agent.id:
            return False
            
        # Fail the activity
        return self.workflow_engine.fail_activity(activity_instance_id, error)
        
    def execute_activity(self,
                        agent: ProcessAwareAgent,
                        activity_instance_id: str) -> Dict[str, Any]:
        """Execute an activity from start to finish.
        
        This is a convenience method that starts the activity, executes it,
        and completes it in one operation.
        
        Args:
            agent: The agent to execute the activity
            activity_instance_id: ID of the activity instance
            
        Returns:
            Activity outputs
            
        Raises:
            ValueError: If the activity is not assigned to this agent
            RuntimeError: If the activity execution fails
        """
        # Get the assignment
        assignment = self.workflow_engine.get_activity_assignment(activity_instance_id)
        
        if not assignment or assignment.agent_id != agent.id:
            raise ValueError(f"Activity {activity_instance_id} is not assigned to agent {agent.id}")
            
        # Start the activity
        if not self.workflow_engine.start_activity(activity_instance_id):
            raise RuntimeError(f"Failed to start activity {activity_instance_id}")
            
        try:
            # Execute the activity
            activity_id = assignment.activity_instance.activity_id
            outputs = agent.execute_activity(activity_id, assignment.inputs)
            
            # Verify the result
            if not agent.verify_activity_result(activity_id, outputs):
                raise ValueError(f"Activity result verification failed for {activity_id}")
                
            # Complete the activity
            if not self.workflow_engine.complete_activity(activity_instance_id, outputs):
                raise RuntimeError(f"Failed to complete activity {activity_instance_id}")
                
            return outputs
            
        except Exception as e:
            # Mark the activity as failed
            self.workflow_engine.fail_activity(activity_instance_id, str(e))
            raise