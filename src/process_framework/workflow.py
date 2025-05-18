# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps our AI agents work together on business tasks in the right order.
# It's like a conductor that makes sure everyone in an orchestra plays their part
# at the right time.

# High School Explanation:
# This module implements the WorkflowEngine class, which coordinates the execution
# of process instances across multiple agents. It manages the state of processes,
# assigns activities to appropriate agents, and handles the flow of data between
# process steps.

import logging
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from datetime import datetime
import uuid
import asyncio
from enum import Enum
import threading
import time

from .core import (
    ProcessFramework, Process, Activity, 
    ProcessInstanceState, ActivityInstanceState,
    ProcessStatus, ProcessInput, ProcessOutput
)
from .repository import ProcessRepository
from .interpreter import ProcessInterpreter, ExecutionPlan


class AgentAssignment:
    """Represents an assignment of an activity to an agent."""
    
    def __init__(self,
                 agent_id: str,
                 activity_instance: ActivityInstanceState,
                 inputs: Dict[str, Any]) -> None:
        """Initialize an agent assignment.
        
        Args:
            agent_id: ID of the assigned agent
            activity_instance: The activity instance to execute
            inputs: Input values for the activity
        """
        self.agent_id = agent_id
        self.activity_instance = activity_instance
        self.inputs = inputs
        self.assigned_at = datetime.now().isoformat()
        

class WorkflowEvent:
    """Represents an event in the workflow execution."""
    
    class Type(Enum):
        """Types of workflow events."""
        PROCESS_STARTED = "process_started"
        PROCESS_COMPLETED = "process_completed"
        PROCESS_FAILED = "process_failed"
        ACTIVITY_STARTED = "activity_started"
        ACTIVITY_COMPLETED = "activity_completed"
        ACTIVITY_FAILED = "activity_failed"
        ACTIVITY_ASSIGNED = "activity_assigned"
        ERROR = "error"
    
    def __init__(self, 
                 event_type: Type,
                 process_id: str,
                 process_instance_id: str,
                 activity_id: Optional[str] = None,
                 activity_instance_id: Optional[str] = None,
                 agent_id: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a workflow event.
        
        Args:
            event_type: Type of the event
            process_id: ID of the process
            process_instance_id: ID of the process instance
            activity_id: Optional ID of the activity
            activity_instance_id: Optional ID of the activity instance
            agent_id: Optional ID of the agent
            details: Optional additional details
        """
        self.event_type = event_type
        self.process_id = process_id
        self.process_instance_id = process_instance_id
        self.activity_id = activity_id
        self.activity_instance_id = activity_instance_id
        self.agent_id = agent_id
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            "event_type": self.event_type.value,
            "process_id": self.process_id,
            "process_instance_id": self.process_instance_id,
            "activity_id": self.activity_id,
            "activity_instance_id": self.activity_instance_id,
            "agent_id": self.agent_id,
            "details": self.details,
            "timestamp": self.timestamp
        }


class WorkflowEngine:
    """Coordinates the execution of process instances across multiple agents.
    
    This class manages the state of processes, assigns activities to appropriate agents,
    and handles the flow of data between process steps.
    """
    
    def __init__(self, 
                 repository: ProcessRepository,
                 storage_dir: Optional[str] = None) -> None:
        """Initialize the workflow engine.
        
        Args:
            repository: Repository containing process frameworks
            storage_dir: Optional directory for storing workflow state
        """
        self.repository = repository
        self.interpreter = ProcessInterpreter(repository)
        self.logger = logging.getLogger(__name__)
        
        # Storage for process instances
        self.storage_dir = Path(storage_dir) if storage_dir else Path("workflows")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Active process instances
        self.process_instances: Dict[str, ProcessInstanceState] = {}
        
        # Agent assignments
        self.assignments: Dict[str, AgentAssignment] = {}
        
        # Event listeners
        self.event_listeners: List[Callable[[WorkflowEvent], None]] = []
        
        # Agent capability registry
        self.agent_capabilities: Dict[str, List[str]] = {}
    
    def register_agent(self, agent_id: str, capabilities: List[str]) -> None:
        """Register an agent with its capabilities.
        
        Args:
            agent_id: ID of the agent
            capabilities: List of agent capabilities
        """
        self.agent_capabilities[agent_id] = capabilities
        self.logger.info(f"Registered agent {agent_id} with capabilities: {capabilities}")
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent.
        
        Args:
            agent_id: ID of the agent to unregister
        """
        if agent_id in self.agent_capabilities:
            del self.agent_capabilities[agent_id]
            self.logger.info(f"Unregistered agent {agent_id}")
    
    def add_event_listener(self, listener: Callable[[WorkflowEvent], None]) -> None:
        """Add a listener for workflow events.
        
        Args:
            listener: Function to call when an event occurs
        """
        self.event_listeners.append(listener)
    
    def _emit_event(self, event: WorkflowEvent) -> None:
        """Emit a workflow event to all listeners.
        
        Args:
            event: The event to emit
        """
        for listener in self.event_listeners:
            try:
                listener(event)
            except Exception as e:
                self.logger.error(f"Error in event listener: {str(e)}")
    
    def start_process(self, 
                     process_id: str, 
                     framework_id: Optional[str] = None,
                     initial_context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Start a new process instance.
        
        Args:
            process_id: ID of the process to start
            framework_id: Optional ID of the framework
            initial_context: Initial context for the process
            
        Returns:
            ID of the process instance, or None if the process could not be started
        """
        # Create a process instance
        instance = self.interpreter.create_process_instance(
            process_id=process_id,
            framework_id=framework_id,
            initial_context=initial_context
        )
        
        if not instance:
            self.logger.error(f"Could not create process instance for {process_id}")
            return None
            
        # Store the instance
        self.process_instances[instance.instance_id] = instance
        self._save_process_instance(instance)
        
        # Emit event
        self._emit_event(WorkflowEvent(
            event_type=WorkflowEvent.Type.PROCESS_STARTED,
            process_id=process_id,
            process_instance_id=instance.instance_id,
            details={"framework_id": framework_id} if framework_id else {}
        ))
        
        # Update status
        instance.update_status(ProcessStatus.IN_PROGRESS)
        self._save_process_instance(instance)
        
        # Schedule the process
        self._schedule_process(instance)
        
        return instance.instance_id
    
    def _save_process_instance(self, instance: ProcessInstanceState) -> None:
        """Save a process instance to storage.
        
        Args:
            instance: The process instance to save
        """
        # Ensure the directory exists
        instance_dir = self.storage_dir / instance.instance_id
        instance_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the instance state
        state_path = instance_dir / "state.json"
        with open(state_path, 'w') as f:
            json.dump(instance.to_dict(), f, indent=2)
            
    def _load_process_instance(self, instance_id: str) -> Optional[ProcessInstanceState]:
        """Load a process instance from storage.
        
        Args:
            instance_id: ID of the process instance
            
        Returns:
            The process instance, or None if not found
        """
        instance_dir = self.storage_dir / instance_id
        state_path = instance_dir / "state.json"
        
        if not state_path.exists():
            return None
            
        try:
            with open(state_path, 'r') as f:
                state_data = json.load(f)
                return ProcessInstanceState.from_dict(state_data)
        except Exception as e:
            self.logger.error(f"Error loading process instance {instance_id}: {str(e)}")
            return None
    
    def _schedule_process(self, instance: ProcessInstanceState) -> None:
        """Schedule a process for execution.
        
        Args:
            instance: The process instance to schedule
        """
        # Create an execution plan
        plan = self.interpreter.create_execution_plan(instance)
        
        # Find activities that are ready to execute
        ready_activities = plan.get_ready_activities()
        
        # Assign activities to agents
        for activity in ready_activities:
            self._assign_activity(activity, plan)
    
    def _assign_activity(self, activity: ActivityInstanceState, plan: ExecutionPlan) -> None:
        """Assign an activity to an agent.
        
        Args:
            activity: The activity instance to assign
            plan: The execution plan
        """
        # Find an agent with the required capabilities
        activity_def = self.repository.get_activity_by_id(activity.activity_id)
        if not activity_def:
            self.logger.error(f"Activity definition not found: {activity.activity_id}")
            return
            
        # Find a suitable agent
        agent_id = self._find_agent_for_activity(activity_def)
        if not agent_id:
            self.logger.warning(f"No suitable agent found for activity {activity.activity_id}")
            return
            
        # Resolve activity inputs
        inputs = self.interpreter.resolve_activity_requirements(
            activity_id=activity.activity_id,
            context=plan.context
        )
        
        # Create the assignment
        assignment = AgentAssignment(
            agent_id=agent_id,
            activity_instance=activity,
            inputs=inputs
        )
        
        # Store the assignment
        self.assignments[activity.instance_id] = assignment
        
        # Update activity state
        activity.assign_agent(agent_id)
        activity.update_status(ProcessStatus.WAITING)
        
        # Save the updated instance
        instance = self.process_instances.get(activity.process_instance_id)
        if instance:
            self._save_process_instance(instance)
            
        # Emit event
        self._emit_event(WorkflowEvent(
            event_type=WorkflowEvent.Type.ACTIVITY_ASSIGNED,
            process_id=activity_def.activity_id,
            process_instance_id=activity.process_instance_id,
            activity_id=activity.activity_id,
            activity_instance_id=activity.instance_id,
            agent_id=agent_id
        ))
    
    def _find_agent_for_activity(self, activity: Activity) -> Optional[str]:
        """Find an agent that can execute an activity.
        
        Args:
            activity: The activity to execute
            
        Returns:
            ID of a suitable agent, or None if no agent is found
        """
        # If no specific capabilities are required, any agent can do it
        if not activity.agent_capabilities:
            if self.agent_capabilities:
                return next(iter(self.agent_capabilities.keys()))
            return None
            
        # Find agents with all required capabilities
        for agent_id, capabilities in self.agent_capabilities.items():
            if all(required in capabilities for required in activity.agent_capabilities):
                return agent_id
                
        return None
    
    def start_activity(self, activity_instance_id: str) -> bool:
        """Start execution of an activity.
        
        Args:
            activity_instance_id: ID of the activity instance
            
        Returns:
            True if the activity was started, False otherwise
        """
        # Find the assignment
        assignment = self.assignments.get(activity_instance_id)
        if not assignment:
            self.logger.error(f"Assignment not found for activity instance {activity_instance_id}")
            return False
            
        # Update activity state
        activity = assignment.activity_instance
        activity.update_status(ProcessStatus.IN_PROGRESS)
        
        # Save the updated instance
        instance = self.process_instances.get(activity.process_instance_id)
        if instance:
            self._save_process_instance(instance)
            
        # Emit event
        self._emit_event(WorkflowEvent(
            event_type=WorkflowEvent.Type.ACTIVITY_STARTED,
            process_id=activity.activity_id,
            process_instance_id=activity.process_instance_id,
            activity_id=activity.activity_id,
            activity_instance_id=activity.instance_id,
            agent_id=assignment.agent_id
        ))
        
        return True
    
    def complete_activity(self, 
                         activity_instance_id: str, 
                         outputs: Dict[str, Any]) -> bool:
        """Complete an activity with its outputs.
        
        Args:
            activity_instance_id: ID of the activity instance
            outputs: Output values from the activity
            
        Returns:
            True if the activity was completed, False otherwise
        """
        # Find the assignment
        assignment = self.assignments.get(activity_instance_id)
        if not assignment:
            self.logger.error(f"Assignment not found for activity instance {activity_instance_id}")
            return False
            
        # Update activity state
        activity = assignment.activity_instance
        activity.update_status(ProcessStatus.COMPLETED)
        activity.context.update(outputs)
        
        # Get the process instance
        instance = self.process_instances.get(activity.process_instance_id)
        if not instance:
            self.logger.error(f"Process instance not found: {activity.process_instance_id}")
            return False
            
        # Update process context with activity outputs
        instance.context = self.interpreter.update_context_with_outputs(
            activity_id=activity.activity_id,
            outputs=outputs,
            context=instance.context
        )
        
        # Save the updated instance
        self._save_process_instance(instance)
        
        # Emit event
        self._emit_event(WorkflowEvent(
            event_type=WorkflowEvent.Type.ACTIVITY_COMPLETED,
            process_id=activity.activity_id,
            process_instance_id=activity.process_instance_id,
            activity_id=activity.activity_id,
            activity_instance_id=activity.instance_id,
            agent_id=assignment.agent_id,
            details={"outputs": outputs}
        ))
        
        # Remove the assignment
        del self.assignments[activity_instance_id]
        
        # Check if the process is complete
        self._check_process_completion(instance)
        
        # Schedule the next activities
        self._schedule_process(instance)
        
        return True
    
    def fail_activity(self, 
                     activity_instance_id: str, 
                     error: str) -> bool:
        """Mark an activity as failed.
        
        Args:
            activity_instance_id: ID of the activity instance
            error: Error message
            
        Returns:
            True if the activity was marked as failed, False otherwise
        """
        # Find the assignment
        assignment = self.assignments.get(activity_instance_id)
        if not assignment:
            self.logger.error(f"Assignment not found for activity instance {activity_instance_id}")
            return False
            
        # Update activity state
        activity = assignment.activity_instance
        activity.update_status(ProcessStatus.FAILED)
        activity.context["error"] = error
        
        # Get the process instance
        instance = self.process_instances.get(activity.process_instance_id)
        if not instance:
            self.logger.error(f"Process instance not found: {activity.process_instance_id}")
            return False
            
        # Save the updated instance
        self._save_process_instance(instance)
        
        # Emit event
        self._emit_event(WorkflowEvent(
            event_type=WorkflowEvent.Type.ACTIVITY_FAILED,
            process_id=activity.activity_id,
            process_instance_id=activity.process_instance_id,
            activity_id=activity.activity_id,
            activity_instance_id=activity.instance_id,
            agent_id=assignment.agent_id,
            details={"error": error}
        ))
        
        # Remove the assignment
        del self.assignments[activity_instance_id]
        
        # Check if the process has failed
        plan = self.interpreter.create_execution_plan(instance)
        if plan.is_failed():
            self._fail_process(instance, "Process failed due to activity failure")
        else:
            # Schedule the next activities
            self._schedule_process(instance)
            
        return True
    
    def _check_process_completion(self, instance: ProcessInstanceState) -> None:
        """Check if a process instance is complete.
        
        Args:
            instance: The process instance to check
        """
        # Create an execution plan
        plan = self.interpreter.create_execution_plan(instance)
        
        # Check if the plan is complete
        if plan.is_complete():
            self._complete_process(instance)
    
    def _complete_process(self, instance: ProcessInstanceState) -> None:
        """Mark a process instance as completed.
        
        Args:
            instance: The process instance to complete
        """
        # Update process state
        instance.update_status(ProcessStatus.COMPLETED)
        
        # Save the updated instance
        self._save_process_instance(instance)
        
        # Emit event
        self._emit_event(WorkflowEvent(
            event_type=WorkflowEvent.Type.PROCESS_COMPLETED,
            process_id=instance.process_id,
            process_instance_id=instance.instance_id,
            details={"context": instance.context}
        ))
    
    def _fail_process(self, instance: ProcessInstanceState, error: str) -> None:
        """Mark a process instance as failed.
        
        Args:
            instance: The process instance to fail
            error: Error message
        """
        # Update process state
        instance.update_status(ProcessStatus.FAILED)
        instance.context["error"] = error
        
        # Save the updated instance
        self._save_process_instance(instance)
        
        # Emit event
        self._emit_event(WorkflowEvent(
            event_type=WorkflowEvent.Type.PROCESS_FAILED,
            process_id=instance.process_id,
            process_instance_id=instance.instance_id,
            details={"error": error}
        ))
    
    def get_process_instance(self, instance_id: str) -> Optional[ProcessInstanceState]:
        """Get a process instance.
        
        Args:
            instance_id: ID of the process instance
            
        Returns:
            The process instance, or None if not found
        """
        # Check in-memory cache first
        if instance_id in self.process_instances:
            return self.process_instances[instance_id]
            
        # Try to load from storage
        instance = self._load_process_instance(instance_id)
        if instance:
            # Add to in-memory cache
            self.process_instances[instance_id] = instance
            
        return instance
    
    def get_agent_assignments(self, agent_id: str) -> List[AgentAssignment]:
        """Get assignments for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            List of assignments for the agent
        """
        return [
            assignment for assignment in self.assignments.values()
            if assignment.agent_id == agent_id
        ]
    
    def get_activity_assignment(self, activity_instance_id: str) -> Optional[AgentAssignment]:
        """Get the assignment for an activity.
        
        Args:
            activity_instance_id: ID of the activity instance
            
        Returns:
            The assignment for the activity, or None if not found
        """
        return self.assignments.get(activity_instance_id)