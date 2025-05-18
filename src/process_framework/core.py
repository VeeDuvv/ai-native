# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file has the building blocks for our business process system. It's like having
# different pieces of a puzzle that fit together to create a complete picture of how
# businesses work.

# High School Explanation:
# This module defines the core data structures for representing business process frameworks.
# It includes classes for frameworks, processes, activities, and related components that
# model the hierarchical structure of standard process frameworks like APQC and eTOM.

from typing import Dict, List, Optional, Any, Set, Union
from datetime import datetime
import uuid
from enum import Enum
from dataclasses import dataclass, field


class ProcessStatus(Enum):
    """Status of a process or activity instance."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"
    CANCELED = "canceled"


@dataclass
class ProcessMetric:
    """Represents a performance metric for a process or activity."""
    id: str
    name: str
    description: str
    unit: str
    target_value: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    aggregation_method: str = "average"  # average, sum, min, max
    tags: List[str] = field(default_factory=list)


@dataclass
class ProcessInput:
    """Represents an input required by a process or activity."""
    id: str
    name: str
    description: str
    data_type: str  # string, number, object, array, etc.
    required: bool = True
    default_value: Optional[Any] = None
    validation_rules: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class ProcessOutput:
    """Represents an output produced by a process or activity."""
    id: str
    name: str 
    description: str
    data_type: str  # string, number, object, array, etc.
    tags: List[str] = field(default_factory=list)


@dataclass
class ProcessRole:
    """Represents a role involved in a process or activity."""
    id: str
    name: str
    description: str
    responsibilities: List[str] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class Activity:
    """Represents an executable activity within a process."""
    
    def __init__(self, 
                 activity_id: str, 
                 name: str, 
                 description: str,
                 inputs: Optional[List[ProcessInput]] = None,
                 outputs: Optional[List[ProcessOutput]] = None,
                 metrics: Optional[List[ProcessMetric]] = None,
                 roles: Optional[List[ProcessRole]] = None,
                 execution_steps: Optional[List[str]] = None,
                 agent_capabilities: Optional[List[str]] = None,
                 preconditions: Optional[List[str]] = None,
                 postconditions: Optional[List[str]] = None) -> None:
        """Initialize an activity.
        
        Args:
            activity_id: Unique identifier for the activity
            name: Name of the activity
            description: Description of what the activity does
            inputs: Required inputs for the activity
            outputs: Outputs produced by the activity
            metrics: Performance metrics for the activity
            roles: Roles responsible for the activity
            execution_steps: Detailed steps for executing the activity
            agent_capabilities: Required agent capabilities to perform this activity
            preconditions: Conditions that must be true before execution
            postconditions: Conditions that should be true after execution
        """
        self.activity_id = activity_id
        self.name = name
        self.description = description
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.metrics = metrics or []
        self.roles = roles or []
        self.execution_steps = execution_steps or []
        self.agent_capabilities = agent_capabilities or []
        self.preconditions = preconditions or []
        self.postconditions = postconditions or []
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the activity to a dictionary.
        
        Returns:
            Dictionary representation of the activity
        """
        return {
            "activity_id": self.activity_id,
            "name": self.name,
            "description": self.description,
            "inputs": [i.__dict__ for i in self.inputs],
            "outputs": [o.__dict__ for o in self.outputs],
            "metrics": [m.__dict__ for m in self.metrics],
            "roles": [r.__dict__ for r in self.roles],
            "execution_steps": self.execution_steps,
            "agent_capabilities": self.agent_capabilities,
            "preconditions": self.preconditions,
            "postconditions": self.postconditions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Activity':
        """Create an Activity from a dictionary.
        
        Args:
            data: Dictionary containing activity data
            
        Returns:
            A new Activity instance
        """
        inputs = [ProcessInput(**i) for i in data.get("inputs", [])]
        outputs = [ProcessOutput(**o) for o in data.get("outputs", [])]
        metrics = [ProcessMetric(**m) for m in data.get("metrics", [])]
        roles = [ProcessRole(**r) for r in data.get("roles", [])]
        
        return cls(
            activity_id=data["activity_id"],
            name=data["name"],
            description=data["description"],
            inputs=inputs,
            outputs=outputs,
            metrics=metrics,
            roles=roles,
            execution_steps=data.get("execution_steps", []),
            agent_capabilities=data.get("agent_capabilities", []),
            preconditions=data.get("preconditions", []),
            postconditions=data.get("postconditions", [])
        )


class Process:
    """Represents a process within a framework."""
    
    def __init__(self,
                 process_id: str,
                 name: str,
                 description: str,
                 version: str = "1.0",
                 categories: Optional[List[str]] = None,
                 owner: Optional[str] = None,
                 inputs: Optional[List[ProcessInput]] = None,
                 outputs: Optional[List[ProcessOutput]] = None,
                 metrics: Optional[List[ProcessMetric]] = None,
                 roles: Optional[List[ProcessRole]] = None,
                 parent_id: Optional[str] = None) -> None:
        """Initialize a process.
        
        Args:
            process_id: Unique identifier for the process
            name: Name of the process
            description: Description of what the process does
            version: Version of the process definition
            categories: Categories this process belongs to
            owner: Owner or responsible entity for the process
            inputs: Required inputs for the process
            outputs: Outputs produced by the process
            metrics: Performance metrics for the process
            roles: Roles responsible for the process
            parent_id: ID of the parent process if this is a sub-process
        """
        self.process_id = process_id
        self.name = name
        self.description = description
        self.version = version
        self.categories = categories or []
        self.owner = owner
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.metrics = metrics or []
        self.roles = roles or []
        self.parent_id = parent_id
        self.sub_processes: List[Process] = []
        self.activities: List[Activity] = []
        
    def add_sub_process(self, process: 'Process') -> None:
        """Add a sub-process to this process.
        
        Args:
            process: The sub-process to add
        """
        process.parent_id = self.process_id
        self.sub_processes.append(process)
        
    def add_activity(self, activity: Activity) -> None:
        """Add an activity to this process.
        
        Args:
            activity: The activity to add
        """
        self.activities.append(activity)
        
    def get_all_activities(self) -> List[Activity]:
        """Get all activities in this process and its sub-processes.
        
        Returns:
            List of all activities
        """
        all_activities = self.activities.copy()
        
        for sub_process in self.sub_processes:
            all_activities.extend(sub_process.get_all_activities())
            
        return all_activities
    
    def get_activity_by_id(self, activity_id: str) -> Optional[Activity]:
        """Get an activity by its ID.
        
        Args:
            activity_id: ID of the activity to find
            
        Returns:
            The activity if found, None otherwise
        """
        # Check activities in this process
        for activity in self.activities:
            if activity.activity_id == activity_id:
                return activity
                
        # Check activities in sub-processes
        for sub_process in self.sub_processes:
            activity = sub_process.get_activity_by_id(activity_id)
            if activity:
                return activity
                
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the process to a dictionary.
        
        Returns:
            Dictionary representation of the process
        """
        return {
            "process_id": self.process_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "categories": self.categories,
            "owner": self.owner,
            "inputs": [i.__dict__ for i in self.inputs],
            "outputs": [o.__dict__ for o in self.outputs],
            "metrics": [m.__dict__ for m in self.metrics],
            "roles": [r.__dict__ for r in self.roles],
            "parent_id": self.parent_id,
            "sub_processes": [p.to_dict() for p in self.sub_processes],
            "activities": [a.to_dict() for a in self.activities]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Process':
        """Create a Process from a dictionary.
        
        Args:
            data: Dictionary containing process data
            
        Returns:
            A new Process instance
        """
        inputs = [ProcessInput(**i) for i in data.get("inputs", [])]
        outputs = [ProcessOutput(**o) for o in data.get("outputs", [])]
        metrics = [ProcessMetric(**m) for m in data.get("metrics", [])]
        roles = [ProcessRole(**r) for r in data.get("roles", [])]
        
        process = cls(
            process_id=data["process_id"],
            name=data["name"],
            description=data["description"],
            version=data.get("version", "1.0"),
            categories=data.get("categories", []),
            owner=data.get("owner"),
            inputs=inputs,
            outputs=outputs,
            metrics=metrics,
            roles=roles,
            parent_id=data.get("parent_id")
        )
        
        # Add sub-processes recursively
        for sub_process_data in data.get("sub_processes", []):
            sub_process = Process.from_dict(sub_process_data)
            process.add_sub_process(sub_process)
            
        # Add activities
        for activity_data in data.get("activities", []):
            activity = Activity.from_dict(activity_data)
            process.add_activity(activity)
            
        return process


class ProcessFramework:
    """Represents a process framework like APQC or eTOM."""
    
    def __init__(self,
                 framework_id: str,
                 name: str,
                 version: str,
                 description: Optional[str] = None,
                 organization: Optional[str] = None,
                 website: Optional[str] = None,
                 source: Optional[str] = None) -> None:
        """Initialize a process framework.
        
        Args:
            framework_id: Unique identifier for the framework
            name: Name of the framework
            version: Version of the framework
            description: Description of the framework
            organization: Organization that maintains the framework
            website: Website with more information about the framework
            source: Source of the framework definition
        """
        self.framework_id = framework_id
        self.name = name
        self.version = version
        self.description = description or ""
        self.organization = organization
        self.website = website
        self.source = source
        self.root_processes: List[Process] = []
        
    def add_process(self, process: Process) -> None:
        """Add a top-level process to the framework.
        
        Args:
            process: The process to add
        """
        self.root_processes.append(process)
        
    def get_process_by_id(self, process_id: str) -> Optional[Process]:
        """Get a process by its ID.
        
        Args:
            process_id: ID of the process to find
            
        Returns:
            The process if found, None otherwise
        """
        def search_process(processes: List[Process]) -> Optional[Process]:
            for process in processes:
                if process.process_id == process_id:
                    return process
                    
                # Search in sub-processes
                result = search_process(process.sub_processes)
                if result:
                    return result
                    
            return None
            
        return search_process(self.root_processes)
    
    def get_activity_by_id(self, activity_id: str) -> Optional[Activity]:
        """Get an activity by its ID.
        
        Args:
            activity_id: ID of the activity to find
            
        Returns:
            The activity if found, None otherwise
        """
        for process in self.root_processes:
            activity = process.get_activity_by_id(activity_id)
            if activity:
                return activity
                
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the framework to a dictionary.
        
        Returns:
            Dictionary representation of the framework
        """
        return {
            "framework_id": self.framework_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "organization": self.organization,
            "website": self.website,
            "source": self.source,
            "root_processes": [p.to_dict() for p in self.root_processes]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessFramework':
        """Create a ProcessFramework from a dictionary.
        
        Args:
            data: Dictionary containing framework data
            
        Returns:
            A new ProcessFramework instance
        """
        framework = cls(
            framework_id=data["framework_id"],
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            organization=data.get("organization"),
            website=data.get("website"),
            source=data.get("source")
        )
        
        # Add processes recursively
        for process_data in data.get("root_processes", []):
            process = Process.from_dict(process_data)
            framework.add_process(process)
            
        return framework


class ProcessInstanceState:
    """Represents the state of a process instance."""
    
    def __init__(self, 
                 process_id: str, 
                 instance_id: Optional[str] = None,
                 status: ProcessStatus = ProcessStatus.NOT_STARTED,
                 context: Optional[Dict[str, Any]] = None,
                 parent_instance_id: Optional[str] = None,
                 created_at: Optional[str] = None,
                 updated_at: Optional[str] = None) -> None:
        """Initialize a process instance state.
        
        Args:
            process_id: ID of the process definition
            instance_id: Unique identifier for this instance
            status: Current status of the instance
            context: Execution context with inputs and outputs
            parent_instance_id: ID of the parent process instance
            created_at: Creation timestamp
            updated_at: Last update timestamp
        """
        self.process_id = process_id
        self.instance_id = instance_id or str(uuid.uuid4())
        self.status = status
        self.context = context or {}
        self.parent_instance_id = parent_instance_id
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or self.created_at
        self.activity_states: Dict[str, 'ActivityInstanceState'] = {}
        self.sub_process_states: Dict[str, 'ProcessInstanceState'] = {}
        
    def update_status(self, status: ProcessStatus) -> None:
        """Update the status of this process instance.
        
        Args:
            status: New status value
        """
        self.status = status
        self.updated_at = datetime.now().isoformat()
        
    def add_activity_state(self, activity_state: 'ActivityInstanceState') -> None:
        """Add an activity instance state.
        
        Args:
            activity_state: The activity state to add
        """
        self.activity_states[activity_state.activity_id] = activity_state
        
    def add_sub_process_state(self, process_state: 'ProcessInstanceState') -> None:
        """Add a sub-process instance state.
        
        Args:
            process_state: The process state to add
        """
        process_state.parent_instance_id = self.instance_id
        self.sub_process_states[process_state.instance_id] = process_state
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the process instance state to a dictionary.
        
        Returns:
            Dictionary representation of the state
        """
        return {
            "process_id": self.process_id,
            "instance_id": self.instance_id,
            "status": self.status.value,
            "context": self.context,
            "parent_instance_id": self.parent_instance_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "activity_states": {
                k: v.to_dict() for k, v in self.activity_states.items()
            },
            "sub_process_states": {
                k: v.to_dict() for k, v in self.sub_process_states.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessInstanceState':
        """Create a ProcessInstanceState from a dictionary.
        
        Args:
            data: Dictionary containing state data
            
        Returns:
            A new ProcessInstanceState instance
        """
        state = cls(
            process_id=data["process_id"],
            instance_id=data["instance_id"],
            status=ProcessStatus(data["status"]),
            context=data.get("context", {}),
            parent_instance_id=data.get("parent_instance_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
        
        # Add activity states
        for activity_id, activity_state_data in data.get("activity_states", {}).items():
            activity_state = ActivityInstanceState.from_dict(activity_state_data)
            state.add_activity_state(activity_state)
            
        # Add sub-process states
        for instance_id, process_state_data in data.get("sub_process_states", {}).items():
            process_state = ProcessInstanceState.from_dict(process_state_data)
            state.add_sub_process_state(process_state)
            
        return state


class ActivityInstanceState:
    """Represents the state of an activity instance."""
    
    def __init__(self,
                 activity_id: str,
                 process_instance_id: str,
                 instance_id: Optional[str] = None,
                 status: ProcessStatus = ProcessStatus.NOT_STARTED,
                 context: Optional[Dict[str, Any]] = None,
                 assigned_agent: Optional[str] = None,
                 created_at: Optional[str] = None,
                 updated_at: Optional[str] = None,
                 started_at: Optional[str] = None,
                 completed_at: Optional[str] = None) -> None:
        """Initialize an activity instance state.
        
        Args:
            activity_id: ID of the activity definition
            process_instance_id: ID of the parent process instance
            instance_id: Unique identifier for this instance
            status: Current status of the instance
            context: Execution context with inputs and outputs
            assigned_agent: ID of the agent assigned to this activity
            created_at: Creation timestamp
            updated_at: Last update timestamp
            started_at: Start execution timestamp
            completed_at: Completion timestamp
        """
        self.activity_id = activity_id
        self.process_instance_id = process_instance_id
        self.instance_id = instance_id or str(uuid.uuid4())
        self.status = status
        self.context = context or {}
        self.assigned_agent = assigned_agent
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or self.created_at
        self.started_at = started_at
        self.completed_at = completed_at
        
    def update_status(self, status: ProcessStatus) -> None:
        """Update the status of this activity instance.
        
        Args:
            status: New status value
        """
        self.status = status
        self.updated_at = datetime.now().isoformat()
        
        if status == ProcessStatus.IN_PROGRESS and not self.started_at:
            self.started_at = datetime.now().isoformat()
            
        if status in (ProcessStatus.COMPLETED, ProcessStatus.FAILED) and not self.completed_at:
            self.completed_at = datetime.now().isoformat()
            
    def assign_agent(self, agent_id: str) -> None:
        """Assign an agent to this activity.
        
        Args:
            agent_id: ID of the agent to assign
        """
        self.assigned_agent = agent_id
        self.updated_at = datetime.now().isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the activity instance state to a dictionary.
        
        Returns:
            Dictionary representation of the state
        """
        return {
            "activity_id": self.activity_id,
            "process_instance_id": self.process_instance_id,
            "instance_id": self.instance_id,
            "status": self.status.value,
            "context": self.context,
            "assigned_agent": self.assigned_agent,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActivityInstanceState':
        """Create an ActivityInstanceState from a dictionary.
        
        Args:
            data: Dictionary containing state data
            
        Returns:
            A new ActivityInstanceState instance
        """
        return cls(
            activity_id=data["activity_id"],
            process_instance_id=data["process_instance_id"],
            instance_id=data["instance_id"],
            status=ProcessStatus(data["status"]),
            context=data.get("context", {}),
            assigned_agent=data.get("assigned_agent"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at")
        )