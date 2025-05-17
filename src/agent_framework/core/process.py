# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps our AI helpers understand and follow standard business steps,
# like following a recipe or instructions for building a model. It lets them use
# expert-created instructions instead of making up their own steps.

# High School Explanation:
# This module provides the foundation for integrating standard process frameworks
# like APQC and eTOM into our agent architecture. It enables agents to interpret,
# execute, and coordinate activities based on standardized process definitions.

"""
Process framework integration for the Agent Framework.

This module provides classes and utilities for integrating standard process
frameworks like APQC and eTOM into the agent ecosystem, enabling agents to
execute standardized business processes.
"""

import json
import logging
import os
from enum import Enum
from typing import Dict, List, Any, Optional, Callable

# Set up logging
logger = logging.getLogger(__name__)


class ProcessFrameworkType(Enum):
    """
    Enumeration of supported process framework types.
    """
    APQC = "apqc"       # American Productivity & Quality Center PCF
    ETOM = "etom"       # Enhanced Telecom Operations Map
    ITIL = "itil"       # IT Infrastructure Library
    CUSTOM = "custom"   # Custom process framework


class ProcessActivity:
    """
    Represents an activity within a process framework.
    
    Activities are the executable units of work within a process framework.
    They define the specific actions that agents can perform as part of a
    business process.
    """
    
    def __init__(self, activity_id: str, name: str, description: str, 
                framework_type: ProcessFrameworkType):
        """
        Initialize a process activity.
        
        Args:
            activity_id: Unique identifier for the activity
            name: Human-readable name
            description: Detailed description
            framework_type: Type of process framework
        """
        self.activity_id = activity_id
        self.name = name
        self.description = description
        self.framework_type = framework_type
        self.inputs = []
        self.outputs = []
        self.preconditions = []
        self.postconditions = []
        self.roles = []
        self.parent_process = None
        self.execution_steps = []
        self.metrics = []
    
    def add_input(self, name: str, description: str, required: bool = True, 
                 data_type: str = "string"):
        """
        Add an input parameter to this activity.
        
        Args:
            name: Input name
            description: Input description
            required: Whether this input is required
            data_type: Type of data expected
        """
        self.inputs.append({
            "name": name,
            "description": description,
            "required": required,
            "data_type": data_type
        })
    
    def add_output(self, name: str, description: str, data_type: str = "string"):
        """
        Add an output parameter to this activity.
        
        Args:
            name: Output name
            description: Output description
            data_type: Type of data produced
        """
        self.outputs.append({
            "name": name,
            "description": description,
            "data_type": data_type
        })
    
    def add_precondition(self, description: str):
        """
        Add a precondition for this activity.
        
        Args:
            description: Precondition description
        """
        self.preconditions.append(description)
    
    def add_postcondition(self, description: str):
        """
        Add a postcondition for this activity.
        
        Args:
            description: Postcondition description
        """
        self.postconditions.append(description)
    
    def add_role(self, name: str, responsibility: str):
        """
        Add a role associated with this activity.
        
        Args:
            name: Role name
            responsibility: Role responsibility
        """
        self.roles.append({
            "name": name,
            "responsibility": responsibility
        })
    
    def add_execution_step(self, description: str, order: int):
        """
        Add an execution step for this activity.
        
        Args:
            description: Step description
            order: Step order
        """
        self.execution_steps.append({
            "description": description,
            "order": order
        })
        
        # Sort steps by order
        self.execution_steps.sort(key=lambda x: x["order"])
    
    def add_metric(self, name: str, description: str, unit: str = ""):
        """
        Add a performance metric for this activity.
        
        Args:
            name: Metric name
            description: Metric description
            unit: Unit of measurement
        """
        self.metrics.append({
            "name": name,
            "description": description,
            "unit": unit
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the activity to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the activity
        """
        return {
            "activity_id": self.activity_id,
            "name": self.name,
            "description": self.description,
            "framework_type": self.framework_type.value,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "preconditions": self.preconditions,
            "postconditions": self.postconditions,
            "roles": self.roles,
            "parent_process": self.parent_process,
            "execution_steps": self.execution_steps,
            "metrics": self.metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessActivity':
        """
        Create an activity from a dictionary.
        
        Args:
            data: Dictionary containing activity data
            
        Returns:
            ProcessActivity: New process activity instance
        """
        framework_type = ProcessFrameworkType(data["framework_type"])
        
        activity = cls(
            activity_id=data["activity_id"],
            name=data["name"],
            description=data["description"],
            framework_type=framework_type
        )
        
        # Set additional fields
        activity.inputs = data.get("inputs", [])
        activity.outputs = data.get("outputs", [])
        activity.preconditions = data.get("preconditions", [])
        activity.postconditions = data.get("postconditions", [])
        activity.roles = data.get("roles", [])
        activity.parent_process = data.get("parent_process")
        activity.execution_steps = data.get("execution_steps", [])
        activity.metrics = data.get("metrics", [])
        
        return activity


class Process:
    """
    Represents a process within a process framework.
    
    Processes are collections of related activities that work together to
    achieve a specific business outcome. They provide structure and context
    for individual activities.
    """
    
    def __init__(self, process_id: str, name: str, description: str, 
                framework_type: ProcessFrameworkType):
        """
        Initialize a process.
        
        Args:
            process_id: Unique identifier for the process
            name: Human-readable name
            description: Detailed description
            framework_type: Type of process framework
        """
        self.process_id = process_id
        self.name = name
        self.description = description
        self.framework_type = framework_type
        self.activities = []
        self.subprocesses = []
        self.parent_process = None
        self.inputs = []
        self.outputs = []
        self.metrics = []
    
    def add_activity(self, activity: ProcessActivity):
        """
        Add an activity to this process.
        
        Args:
            activity: Activity to add
        """
        activity.parent_process = self.process_id
        self.activities.append(activity)
    
    def add_subprocess(self, subprocess: 'Process'):
        """
        Add a subprocess to this process.
        
        Args:
            subprocess: Subprocess to add
        """
        subprocess.parent_process = self.process_id
        self.subprocesses.append(subprocess)
    
    def add_input(self, name: str, description: str):
        """
        Add an input to this process.
        
        Args:
            name: Input name
            description: Input description
        """
        self.inputs.append({
            "name": name,
            "description": description
        })
    
    def add_output(self, name: str, description: str):
        """
        Add an output to this process.
        
        Args:
            name: Output name
            description: Output description
        """
        self.outputs.append({
            "name": name,
            "description": description
        })
    
    def add_metric(self, name: str, description: str, unit: str = ""):
        """
        Add a performance metric for this process.
        
        Args:
            name: Metric name
            description: Metric description
            unit: Unit of measurement
        """
        self.metrics.append({
            "name": name,
            "description": description,
            "unit": unit
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the process to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the process
        """
        return {
            "process_id": self.process_id,
            "name": self.name,
            "description": self.description,
            "framework_type": self.framework_type.value,
            "activities": [a.to_dict() for a in self.activities],
            "subprocesses": [p.to_dict() for p in self.subprocesses],
            "parent_process": self.parent_process,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "metrics": self.metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Process':
        """
        Create a process from a dictionary.
        
        Args:
            data: Dictionary containing process data
            
        Returns:
            Process: New process instance
        """
        framework_type = ProcessFrameworkType(data["framework_type"])
        
        process = cls(
            process_id=data["process_id"],
            name=data["name"],
            description=data["description"],
            framework_type=framework_type
        )
        
        # Set additional fields
        process.parent_process = data.get("parent_process")
        process.inputs = data.get("inputs", [])
        process.outputs = data.get("outputs", [])
        process.metrics = data.get("metrics", [])
        
        # Add activities
        for activity_data in data.get("activities", []):
            activity = ProcessActivity.from_dict(activity_data)
            process.activities.append(activity)
        
        # Add subprocesses (recursive)
        for subprocess_data in data.get("subprocesses", []):
            subprocess = Process.from_dict(subprocess_data)
            process.subprocesses.append(subprocess)
        
        return process


class ProcessFramework:
    """
    Represents a complete process framework.
    
    Process frameworks provide a structured taxonomy of business processes and
    activities that define how an organization operates. They serve as a common
    language and reference model for business processes.
    """
    
    def __init__(self, framework_id: str, name: str, version: str, 
                framework_type: ProcessFrameworkType):
        """
        Initialize a process framework.
        
        Args:
            framework_id: Unique identifier for the framework
            name: Human-readable name
            version: Version string
            framework_type: Type of process framework
        """
        self.framework_id = framework_id
        self.name = name
        self.version = version
        self.framework_type = framework_type
        self.processes = []
        self.description = ""
        self.source_url = ""
        self.source_organization = ""
    
    def add_process(self, process: Process):
        """
        Add a top-level process to the framework.
        
        Args:
            process: Process to add
        """
        self.processes.append(process)
    
    def get_process_by_id(self, process_id: str) -> Optional[Process]:
        """
        Find a process by its ID.
        
        Args:
            process_id: Process identifier
            
        Returns:
            Optional[Process]: Process if found, None otherwise
        """
        # Check top-level processes
        for process in self.processes:
            if process.process_id == process_id:
                return process
        
        # Check subprocesses (recursive)
        for process in self.processes:
            result = self._find_subprocess(process, process_id)
            if result:
                return result
        
        return None
    
    def _find_subprocess(self, parent: Process, process_id: str) -> Optional[Process]:
        """
        Recursively search for a subprocess by ID.
        
        Args:
            parent: Parent process to search within
            process_id: Process identifier to find
            
        Returns:
            Optional[Process]: Process if found, None otherwise
        """
        for subprocess in parent.subprocesses:
            if subprocess.process_id == process_id:
                return subprocess
            
            # Recursive search
            result = self._find_subprocess(subprocess, process_id)
            if result:
                return result
        
        return None
    
    def get_activity_by_id(self, activity_id: str) -> Optional[ProcessActivity]:
        """
        Find an activity by its ID.
        
        Args:
            activity_id: Activity identifier
            
        Returns:
            Optional[ProcessActivity]: Activity if found, None otherwise
        """
        # Search all processes and subprocesses
        for process in self.processes:
            result = self._find_activity(process, activity_id)
            if result:
                return result
        
        return None
    
    def _find_activity(self, process: Process, activity_id: str) -> Optional[ProcessActivity]:
        """
        Recursively search for an activity by ID.
        
        Args:
            process: Process to search within
            activity_id: Activity identifier to find
            
        Returns:
            Optional[ProcessActivity]: Activity if found, None otherwise
        """
        # Check activities in this process
        for activity in process.activities:
            if activity.activity_id == activity_id:
                return activity
        
        # Check subprocesses (recursive)
        for subprocess in process.subprocesses:
            result = self._find_activity(subprocess, activity_id)
            if result:
                return result
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the framework to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the framework
        """
        return {
            "framework_id": self.framework_id,
            "name": self.name,
            "version": self.version,
            "framework_type": self.framework_type.value,
            "description": self.description,
            "source_url": self.source_url,
            "source_organization": self.source_organization,
            "processes": [p.to_dict() for p in self.processes]
        }
    
    def save_to_file(self, filepath: str):
        """
        Save the framework to a JSON file.
        
        Args:
            filepath: Path to save the file
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessFramework':
        """
        Create a framework from a dictionary.
        
        Args:
            data: Dictionary containing framework data
            
        Returns:
            ProcessFramework: New process framework instance
        """
        framework_type = ProcessFrameworkType(data["framework_type"])
        
        framework = cls(
            framework_id=data["framework_id"],
            name=data["name"],
            version=data["version"],
            framework_type=framework_type
        )
        
        # Set additional fields
        framework.description = data.get("description", "")
        framework.source_url = data.get("source_url", "")
        framework.source_organization = data.get("source_organization", "")
        
        # Add processes
        for process_data in data.get("processes", []):
            process = Process.from_dict(process_data)
            framework.processes.append(process)
        
        return framework
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'ProcessFramework':
        """
        Load a framework from a JSON file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            ProcessFramework: Loaded process framework
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return cls.from_dict(data)


class ProcessRepository:
    """
    Manages a collection of process frameworks.
    
    The repository provides storage, retrieval, and querying capabilities for
    process frameworks, making them available to agents for execution.
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize the process repository.
        
        Args:
            storage_dir: Directory for storing framework files
        """
        self.frameworks = {}
        self.storage_dir = storage_dir
        
        # Create storage directory if provided and doesn't exist
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
    
    def add_framework(self, framework: ProcessFramework):
        """
        Add a framework to the repository.
        
        Args:
            framework: Process framework to add
        """
        self.frameworks[framework.framework_id] = framework
        
        # Save to file if storage directory is set
        if self.storage_dir:
            filepath = os.path.join(self.storage_dir, f"{framework.framework_id}.json")
            framework.save_to_file(filepath)
    
    def get_framework(self, framework_id: str) -> Optional[ProcessFramework]:
        """
        Get a framework by ID.
        
        Args:
            framework_id: Framework identifier
            
        Returns:
            Optional[ProcessFramework]: Framework if found, None otherwise
        """
        return self.frameworks.get(framework_id)
    
    def list_frameworks(self) -> List[Dict[str, Any]]:
        """
        List all frameworks in the repository.
        
        Returns:
            List[Dict[str, Any]]: List of framework summaries
        """
        return [
            {
                "framework_id": fw.framework_id,
                "name": fw.name,
                "version": fw.version,
                "framework_type": fw.framework_type.value,
                "process_count": len(fw.processes)
            }
            for fw in self.frameworks.values()
        ]
    
    def get_process(self, framework_id: str, process_id: str) -> Optional[Process]:
        """
        Get a process from a specific framework.
        
        Args:
            framework_id: Framework identifier
            process_id: Process identifier
            
        Returns:
            Optional[Process]: Process if found, None otherwise
        """
        framework = self.get_framework(framework_id)
        if not framework:
            return None
        
        return framework.get_process_by_id(process_id)
    
    def get_activity(self, framework_id: str, activity_id: str) -> Optional[ProcessActivity]:
        """
        Get an activity from a specific framework.
        
        Args:
            framework_id: Framework identifier
            activity_id: Activity identifier
            
        Returns:
            Optional[ProcessActivity]: Activity if found, None otherwise
        """
        framework = self.get_framework(framework_id)
        if not framework:
            return None
        
        return framework.get_activity_by_id(activity_id)
    
    def search_processes(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for processes matching a query.
        
        Args:
            query: Search query string
            
        Returns:
            List[Dict[str, Any]]: List of matching process summaries
        """
        results = []
        
        # Search all frameworks
        for framework in self.frameworks.values():
            for process in framework.processes:
                self._search_process_recursive(process, query, framework.framework_id, results)
        
        return results
    
    def _search_process_recursive(self, process: Process, query: str, 
                                framework_id: str, results: List[Dict[str, Any]]):
        """
        Recursively search a process and its subprocesses.
        
        Args:
            process: Process to search
            query: Search query string
            framework_id: ID of the framework containing this process
            results: List to collect results in
        """
        # Check if this process matches
        if (query.lower() in process.name.lower() or 
            query.lower() in process.description.lower() or
            query.lower() in process.process_id.lower()):
            
            results.append({
                "framework_id": framework_id,
                "process_id": process.process_id,
                "name": process.name,
                "description": process.description,
                "parent_process": process.parent_process
            })
        
        # Search subprocesses
        for subprocess in process.subprocesses:
            self._search_process_recursive(subprocess, query, framework_id, results)
    
    def search_activities(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for activities matching a query.
        
        Args:
            query: Search query string
            
        Returns:
            List[Dict[str, Any]]: List of matching activity summaries
        """
        results = []
        
        # Search all frameworks
        for framework in self.frameworks.values():
            for process in framework.processes:
                self._search_activities_recursive(process, query, framework.framework_id, results)
        
        return results
    
    def _search_activities_recursive(self, process: Process, query: str, 
                                   framework_id: str, results: List[Dict[str, Any]]):
        """
        Recursively search activities in a process and its subprocesses.
        
        Args:
            process: Process to search within
            query: Search query string
            framework_id: ID of the framework containing this process
            results: List to collect results in
        """
        # Check activities in this process
        for activity in process.activities:
            if (query.lower() in activity.name.lower() or 
                query.lower() in activity.description.lower() or
                query.lower() in activity.activity_id.lower()):
                
                results.append({
                    "framework_id": framework_id,
                    "activity_id": activity.activity_id,
                    "name": activity.name,
                    "description": activity.description,
                    "parent_process": process.process_id
                })
        
        # Search subprocesses
        for subprocess in process.subprocesses:
            self._search_activities_recursive(subprocess, query, framework_id, results)
    
    def load_frameworks_from_directory(self, directory: str):
        """
        Load all framework files from a directory.
        
        Args:
            directory: Directory containing framework JSON files
        """
        if not os.path.exists(directory):
            logger.warning(f"Directory not found: {directory}")
            return
        
        # Load each JSON file in the directory
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                filepath = os.path.join(directory, filename)
                try:
                    framework = ProcessFramework.load_from_file(filepath)
                    self.frameworks[framework.framework_id] = framework
                    logger.info(f"Loaded framework: {framework.name} ({framework.framework_id})")
                except Exception as e:
                    logger.error(f"Error loading framework from {filepath}: {str(e)}")


class ProcessInterpreter:
    """
    Interprets process definitions for execution by agents.
    
    The interpreter translates process framework definitions into executable
    actions that agents can perform, mapping between the standardized process
    language and agent capabilities.
    """
    
    def __init__(self, repository: ProcessRepository):
        """
        Initialize the process interpreter.
        
        Args:
            repository: Repository of process frameworks
        """
        self.repository = repository
        self.capability_mappings = {}  # Maps activity IDs to agent capabilities
        self.execution_handlers = {}   # Custom execution handlers for activities
    
    def register_capability_mapping(self, framework_id: str, activity_id: str, 
                                  capabilities: List[str]):
        """
        Register a mapping between an activity and agent capabilities.
        
        Args:
            framework_id: Framework identifier
            activity_id: Activity identifier
            capabilities: List of agent capabilities required
        """
        key = f"{framework_id}:{activity_id}"
        self.capability_mappings[key] = capabilities
    
    def register_execution_handler(self, framework_id: str, activity_id: str, 
                                 handler: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """
        Register a custom execution handler for an activity.
        
        Args:
            framework_id: Framework identifier
            activity_id: Activity identifier
            handler: Function to handle activity execution
        """
        key = f"{framework_id}:{activity_id}"
        self.execution_handlers[key] = handler
    
    def get_required_capabilities(self, framework_id: str, 
                                activity_id: str) -> List[str]:
        """
        Get capabilities required to execute an activity.
        
        Args:
            framework_id: Framework identifier
            activity_id: Activity identifier
            
        Returns:
            List[str]: List of required capabilities
        """
        key = f"{framework_id}:{activity_id}"
        return self.capability_mappings.get(key, [])
    
    def prepare_execution_context(self, framework_id: str, activity_id: str, 
                               input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare context for activity execution.
        
        Args:
            framework_id: Framework identifier
            activity_id: Activity identifier
            input_data: Input data for the activity
            
        Returns:
            Dict[str, Any]: Execution context
        """
        # Get activity definition
        activity = self.repository.get_activity(framework_id, activity_id)
        if not activity:
            raise ValueError(f"Activity not found: {framework_id}:{activity_id}")
        
        # Build execution context
        context = {
            "framework_id": framework_id,
            "activity_id": activity_id,
            "activity_name": activity.name,
            "activity_description": activity.description,
            "framework_type": activity.framework_type.value,
            "input_data": input_data,
            "parent_process": activity.parent_process,
            "execution_steps": activity.execution_steps
        }
        
        # Check required inputs
        missing_inputs = []
        for input_def in activity.inputs:
            if input_def["required"] and input_def["name"] not in input_data:
                missing_inputs.append(input_def["name"])
        
        if missing_inputs:
            context["missing_inputs"] = missing_inputs
            context["status"] = "incomplete_inputs"
        else:
            context["status"] = "ready"
        
        return context
    
    def execute_activity(self, framework_id: str, activity_id: str, 
                      input_data: Dict[str, Any], agent=None) -> Dict[str, Any]:
        """
        Execute an activity using an agent or custom handler.
        
        Args:
            framework_id: Framework identifier
            activity_id: Activity identifier
            input_data: Input data for the activity
            agent: Optional agent to execute the activity
            
        Returns:
            Dict[str, Any]: Execution results
        """
        # Prepare execution context
        context = self.prepare_execution_context(framework_id, activity_id, input_data)
        
        # Check if context is ready
        if context["status"] != "ready":
            return {
                "success": False,
                "message": "Execution context not ready",
                "details": context
            }
        
        # Check for custom handler
        key = f"{framework_id}:{activity_id}"
        if key in self.execution_handlers:
            try:
                return self.execution_handlers[key](context)
            except Exception as e:
                logger.error(f"Error in custom handler: {str(e)}")
                return {
                    "success": False,
                    "message": f"Handler error: {str(e)}",
                    "activity_id": activity_id
                }
        
        # Use agent if provided
        if agent:
            try:
                # Check agent capabilities
                required_capabilities = self.get_required_capabilities(framework_id, activity_id)
                agent_capabilities = agent.get_capabilities()
                
                missing_capabilities = [cap for cap in required_capabilities 
                                       if cap not in agent_capabilities]
                
                if missing_capabilities:
                    return {
                        "success": False,
                        "message": "Agent lacks required capabilities",
                        "missing_capabilities": missing_capabilities,
                        "activity_id": activity_id
                    }
                
                # Execute via agent
                if hasattr(agent, 'execute_activity'):
                    return agent.execute_activity(activity_id, context)
                else:
                    return agent.execute(context)
                
            except Exception as e:
                logger.error(f"Agent execution error: {str(e)}")
                return {
                    "success": False,
                    "message": f"Agent execution error: {str(e)}",
                    "activity_id": activity_id
                }
        
        # No handler or agent available
        return {
            "success": False,
            "message": "No execution handler or agent provided",
            "activity_id": activity_id
        }


class WorkflowEngine:
    """
    Coordinates the execution of processes across multiple agents.
    
    The workflow engine manages the sequencing, state tracking, and coordination
    of process activities, ensuring that they are executed in the correct order
    with the proper inputs and outputs.
    """
    
    def __init__(self, interpreter: ProcessInterpreter):
        """
        Initialize the workflow engine.
        
        Args:
            interpreter: Process interpreter for activity execution
        """
        self.interpreter = interpreter
        self.workflows = {}  # Workflow instances by ID
        self.registered_agents = {}  # Agent registry by capability
    
    def register_agent(self, agent, capabilities: List[str] = None):
        """
        Register an agent with the workflow engine.
        
        Args:
            agent: Agent object
            capabilities: Optional specific capabilities to register
        """
        # If no specific capabilities provided, use all from the agent
        if capabilities is None:
            capabilities = agent.get_capabilities()
        
        # Register for each capability
        for capability in capabilities:
            if capability not in self.registered_agents:
                self.registered_agents[capability] = []
            
            if agent not in self.registered_agents[capability]:
                self.registered_agents[capability].append(agent)
    
    def find_agents_for_activity(self, framework_id: str, 
                              activity_id: str) -> List[Any]:
        """
        Find agents capable of executing an activity.
        
        Args:
            framework_id: Framework identifier
            activity_id: Activity identifier
            
        Returns:
            List[Any]: List of suitable agents
        """
        # Get required capabilities
        required_capabilities = self.interpreter.get_required_capabilities(
            framework_id, activity_id)
        
        # If no required capabilities defined, can't match
        if not required_capabilities:
            return []
        
        # Find agents that have ALL required capabilities
        candidate_agents = set(self.registered_agents.get(required_capabilities[0], []))
        
        for capability in required_capabilities[1:]:
            candidate_agents &= set(self.registered_agents.get(capability, []))
        
        return list(candidate_agents)
    
    def create_workflow(self, framework_id: str, process_id: str) -> str:
        """
        Create a new workflow instance for a process.
        
        Args:
            framework_id: Framework identifier
            process_id: Process identifier
            
        Returns:
            str: Workflow identifier
        """
        from uuid import uuid4
        
        # Get process definition
        repository = self.interpreter.repository
        process = repository.get_process(framework_id, process_id)
        
        if not process:
            raise ValueError(f"Process not found: {framework_id}:{process_id}")
        
        # Create workflow instance
        workflow_id = str(uuid4())
        
        # Build activity list (flattened)
        activities = []
        self._collect_activities_recursive(process, activities)
        
        # Create workflow structure
        workflow = {
            "workflow_id": workflow_id,
            "framework_id": framework_id,
            "process_id": process_id,
            "process_name": process.name,
            "status": "created",
            "activities": activities,
            "current_activity_index": 0,
            "activity_results": {},
            "workflow_data": {},
            "created_at": None,  # Will be set when started
            "completed_at": None
        }
        
        self.workflows[workflow_id] = workflow
        return workflow_id
    
    def _collect_activities_recursive(self, process: Process, activities: List[Dict[str, Any]]):
        """
        Recursively collect activities from a process and its subprocesses.
        
        Args:
            process: Process to collect activities from
            activities: List to collect activities in
        """
        # Add activities from this process
        for activity in process.activities:
            activities.append({
                "activity_id": activity.activity_id,
                "name": activity.name,
                "description": activity.description,
                "status": "pending",
                "parent_process": process.process_id
            })
        
        # Collect from subprocesses
        for subprocess in process.subprocesses:
            self._collect_activities_recursive(subprocess, activities)
    
    def start_workflow(self, workflow_id: str, initial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Start a workflow's execution.
        
        Args:
            workflow_id: Workflow identifier
            initial_data: Initial data for the workflow
            
        Returns:
            Dict[str, Any]: Status information
        """
        from datetime import datetime
        
        # Check if workflow exists
        if workflow_id not in self.workflows:
            return {
                "success": False,
                "message": f"Workflow not found: {workflow_id}"
            }
        
        workflow = self.workflows[workflow_id]
        
        # Check if already started
        if workflow["status"] != "created":
            return {
                "success": False,
                "message": f"Workflow already started with status: {workflow['status']}"
            }
        
        # Set initial data
        workflow["workflow_data"] = initial_data or {}
        workflow["status"] = "running"
        workflow["created_at"] = datetime.now().isoformat()
        
        # Execute first activity if available
        if workflow["activities"]:
            return self.execute_next_activity(workflow_id)
        else:
            # No activities to execute
            workflow["status"] = "completed"
            workflow["completed_at"] = datetime.now().isoformat()
            return {
                "success": True,
                "message": "Workflow completed (no activities)",
                "workflow_id": workflow_id,
                "status": "completed"
            }
    
    def execute_next_activity(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute the next activity in a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Dict[str, Any]: Execution results
        """
        # Check if workflow exists
        if workflow_id not in self.workflows:
            return {
                "success": False,
                "message": f"Workflow not found: {workflow_id}"
            }
        
        workflow = self.workflows[workflow_id]
        
        # Check if workflow is running
        if workflow["status"] != "running":
            return {
                "success": False,
                "message": f"Workflow not in running state: {workflow['status']}"
            }
        
        # Check if there are more activities to execute
        if workflow["current_activity_index"] >= len(workflow["activities"]):
            # All activities completed
            workflow["status"] = "completed"
            workflow["completed_at"] = datetime.now().isoformat()
            return {
                "success": True,
                "message": "All activities completed",
                "workflow_id": workflow_id,
                "status": "completed"
            }
        
        # Get next activity
        activity_index = workflow["current_activity_index"]
        activity = workflow["activities"][activity_index]
        
        # Update activity status
        activity["status"] = "executing"
        
        # Find agents capable of executing this activity
        framework_id = workflow["framework_id"]
        activity_id = activity["activity_id"]
        agents = self.find_agents_for_activity(framework_id, activity_id)
        
        if not agents:
            # No suitable agents found
            activity["status"] = "failed"
            activity["result"] = {
                "success": False,
                "message": "No suitable agents found"
            }
            
            # Move to next activity
            workflow["current_activity_index"] += 1
            return {
                "success": False,
                "message": "No suitable agents for activity",
                "activity_id": activity_id,
                "workflow_id": workflow_id
            }
        
        # Select first available agent
        agent = agents[0]
        
        try:
            # Execute activity
            result = self.interpreter.execute_activity(
                framework_id, activity_id, workflow["workflow_data"], agent)
            
            # Store result
            activity["status"] = "completed" if result.get("success", False) else "failed"
            activity["result"] = result
            workflow["activity_results"][activity_id] = result
            
            # Update workflow data with outputs if successful
            if result.get("success", False) and "outputs" in result:
                workflow["workflow_data"].update(result["outputs"])
            
            # Move to next activity
            workflow["current_activity_index"] += 1
            
            # If this was the last activity, mark workflow as completed
            if workflow["current_activity_index"] >= len(workflow["activities"]):
                workflow["status"] = "completed"
                workflow["completed_at"] = datetime.now().isoformat()
                result["workflow_completed"] = True
            
            return result
            
        except Exception as e:
            # Handle execution error
            activity["status"] = "failed"
            activity["result"] = {
                "success": False,
                "message": f"Execution error: {str(e)}"
            }
            
            # Move to next activity
            workflow["current_activity_index"] += 1
            return {
                "success": False,
                "message": f"Activity execution error: {str(e)}",
                "activity_id": activity_id,
                "workflow_id": workflow_id
            }
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get the current status of a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Dict[str, Any]: Workflow status information
        """
        # Check if workflow exists
        if workflow_id not in self.workflows:
            return {
                "success": False,
                "message": f"Workflow not found: {workflow_id}"
            }
        
        workflow = self.workflows[workflow_id]
        
        # Calculate progress
        total_activities = len(workflow["activities"])
        completed_activities = sum(1 for activity in workflow["activities"] 
                                 if activity["status"] in ["completed", "failed"])
        
        progress = 0 if total_activities == 0 else (completed_activities / total_activities) * 100
        
        # Build status response
        return {
            "success": True,
            "workflow_id": workflow_id,
            "process_name": workflow["process_name"],
            "status": workflow["status"],
            "progress": progress,
            "total_activities": total_activities,
            "completed_activities": completed_activities,
            "created_at": workflow["created_at"],
            "completed_at": workflow["completed_at"]
        }
    
    def get_activity_results(self, workflow_id: str, 
                          activity_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get results for activities in a workflow.
        
        Args:
            workflow_id: Workflow identifier
            activity_id: Optional specific activity to get results for
            
        Returns:
            Dict[str, Any]: Activity results
        """
        # Check if workflow exists
        if workflow_id not in self.workflows:
            return {
                "success": False,
                "message": f"Workflow not found: {workflow_id}"
            }
        
        workflow = self.workflows[workflow_id]
        
        if activity_id:
            # Get specific activity result
            if activity_id in workflow["activity_results"]:
                return {
                    "success": True,
                    "activity_id": activity_id,
                    "result": workflow["activity_results"][activity_id]
                }
            else:
                return {
                    "success": False,
                    "message": f"No results for activity: {activity_id}"
                }
        else:
            # Get all activity results
            return {
                "success": True,
                "workflow_id": workflow_id,
                "results": workflow["activity_results"]
            }