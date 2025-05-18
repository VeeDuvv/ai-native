# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps our AI understand business process instructions. It's like a
# translator that reads a business recipe and figures out the exact steps to follow
# and who should do what.

# High School Explanation:
# This module implements the ProcessInterpreter class, which analyzes process
# definitions from standard frameworks, resolves dependencies between activities,
# and translates them into executable workflows for the agent system.

import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
import uuid
from collections import defaultdict

from .core import (
    ProcessFramework, Process, Activity, 
    ProcessInstanceState, ActivityInstanceState,
    ProcessStatus, ProcessInput, ProcessOutput
)
from .repository import ProcessRepository


class ActivityDependency:
    """Represents a dependency between activities in a process."""
    
    def __init__(self, 
                 source_activity_id: str, 
                 target_activity_id: str,
                 dependency_type: str = "follows",
                 optional: bool = False,
                 condition: Optional[str] = None) -> None:
        """Initialize an activity dependency.
        
        Args:
            source_activity_id: ID of the source activity
            target_activity_id: ID of the target activity (depends on source)
            dependency_type: Type of dependency (follows, requires, etc.)
            optional: Whether this dependency is optional
            condition: Optional condition for the dependency
        """
        self.source_activity_id = source_activity_id
        self.target_activity_id = target_activity_id
        self.dependency_type = dependency_type
        self.optional = optional
        self.condition = condition
        

class ExecutionPlan:
    """Represents an execution plan for a process instance."""
    
    def __init__(self, 
                 process_id: str,
                 instance_id: str,
                 activities: List[ActivityInstanceState],
                 dependencies: List[ActivityDependency],
                 context: Dict[str, Any]) -> None:
        """Initialize an execution plan.
        
        Args:
            process_id: ID of the process definition
            instance_id: ID of the process instance
            activities: Activity instances in the plan
            dependencies: Dependencies between activities
            context: Execution context
        """
        self.process_id = process_id
        self.instance_id = instance_id
        self.activities = activities
        self.dependencies = dependencies
        self.context = context
        
    def get_ready_activities(self) -> List[ActivityInstanceState]:
        """Get activities that are ready to execute.
        
        Returns:
            List of activity instances ready for execution
        """
        ready_activities = []
        
        # Find activities that are not started and have all dependencies satisfied
        for activity in self.activities:
            if activity.status != ProcessStatus.NOT_STARTED:
                continue
                
            # Check if all dependencies are satisfied
            dependencies_satisfied = True
            for dep in self.dependencies:
                if dep.target_activity_id == activity.activity_id:
                    # Find the source activity
                    source_activity = next(
                        (a for a in self.activities if a.activity_id == dep.source_activity_id),
                        None
                    )
                    
                    if source_activity:
                        if not dep.optional and source_activity.status != ProcessStatus.COMPLETED:
                            dependencies_satisfied = False
                            break
                        
                        # Check condition if present
                        if dep.condition and not self._evaluate_condition(dep.condition, source_activity):
                            dependencies_satisfied = False
                            break
                            
            if dependencies_satisfied:
                ready_activities.append(activity)
                
        return ready_activities
    
    def _evaluate_condition(self, condition: str, source_activity: ActivityInstanceState) -> bool:
        """Evaluate a dependency condition.
        
        Args:
            condition: The condition expression
            source_activity: The source activity
            
        Returns:
            True if the condition is satisfied, False otherwise
        """
        # For now, implement a simple condition evaluator
        # In a real implementation, this might use a rule engine or expression evaluator
        
        try:
            # Create a context for evaluation
            eval_context = {
                "activity": source_activity,
                "status": source_activity.status.value,
                "context": source_activity.context,
                "process_context": self.context
            }
            
            # Evaluate the condition
            return eval(condition, {"__builtins__": {}}, eval_context)
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Error evaluating condition '{condition}': {str(e)}")
            return False
            
    def is_complete(self) -> bool:
        """Check if the execution plan is complete.
        
        Returns:
            True if all activities are completed or canceled, False otherwise
        """
        for activity in self.activities:
            if activity.status not in [ProcessStatus.COMPLETED, ProcessStatus.CANCELED]:
                return False
                
        return True
    
    def is_failed(self) -> bool:
        """Check if the execution plan has failed.
        
        Returns:
            True if any required activity has failed, False otherwise
        """
        for activity in self.activities:
            if activity.status == ProcessStatus.FAILED:
                # Check if this activity is optional
                is_optional = all(
                    dep.optional 
                    for dep in self.dependencies 
                    if dep.source_activity_id == activity.activity_id
                )
                
                if not is_optional:
                    return True
                    
        return False


class ProcessInterpreter:
    """Interprets process definitions and creates execution plans.
    
    This class analyzes process frameworks, resolves dependencies, and prepares
    processes for execution by the workflow engine.
    """
    
    def __init__(self, repository: ProcessRepository) -> None:
        """Initialize the process interpreter.
        
        Args:
            repository: Repository containing process frameworks
        """
        self.repository = repository
        self.logger = logging.getLogger(__name__)
        
    def create_process_instance(self, 
                               process_id: str, 
                               framework_id: Optional[str] = None,
                               initial_context: Optional[Dict[str, Any]] = None) -> Optional[ProcessInstanceState]:
        """Create a new process instance.
        
        Args:
            process_id: ID of the process to instantiate
            framework_id: Optional ID of the framework
            initial_context: Initial context for the process
            
        Returns:
            A new process instance state, or None if the process is not found
        """
        # Find the process definition
        process = self.repository.get_process_by_id(process_id, framework_id)
        if not process:
            self.logger.error(f"Process not found: {process_id}")
            return None
            
        # Create the process instance state
        instance = ProcessInstanceState(
            process_id=process_id,
            status=ProcessStatus.NOT_STARTED,
            context=initial_context or {}
        )
        
        # Create activity instance states
        self._create_activity_instances(process, instance)
        
        return instance
    
    def _create_activity_instances(self, process: Process, instance: ProcessInstanceState) -> None:
        """Create activity instances for a process recursively.
        
        Args:
            process: Process definition
            instance: Process instance state
        """
        # Create activity instances for direct activities
        for activity in process.activities:
            activity_instance = ActivityInstanceState(
                activity_id=activity.activity_id,
                process_instance_id=instance.instance_id,
                status=ProcessStatus.NOT_STARTED
            )
            instance.add_activity_state(activity_instance)
            
        # Create sub-process instances recursively
        for sub_process in process.sub_processes:
            sub_instance = ProcessInstanceState(
                process_id=sub_process.process_id,
                status=ProcessStatus.NOT_STARTED,
                parent_instance_id=instance.instance_id
            )
            
            # Recursively create activity instances
            self._create_activity_instances(sub_process, sub_instance)
            
            # Add the sub-process instance
            instance.add_sub_process_state(sub_instance)
    
    def create_execution_plan(self, 
                             instance: ProcessInstanceState,
                             context: Optional[Dict[str, Any]] = None) -> ExecutionPlan:
        """Create an execution plan for a process instance.
        
        Args:
            instance: Process instance state
            context: Optional context to use (overrides instance context)
            
        Returns:
            An execution plan for the process
        """
        # Find the process definition
        process = self.repository.get_process_by_id(instance.process_id)
        if not process:
            self.logger.error(f"Process definition not found: {instance.process_id}")
            # Create an empty plan
            return ExecutionPlan(
                process_id=instance.process_id,
                instance_id=instance.instance_id,
                activities=[],
                dependencies=[],
                context=context or instance.context
            )
            
        # Flatten activities from the process hierarchy
        activities = self._flatten_activities(instance)
        
        # Identify dependencies between activities
        dependencies = self._identify_dependencies(process, instance)
        
        # Create the execution plan
        return ExecutionPlan(
            process_id=instance.process_id,
            instance_id=instance.instance_id,
            activities=activities,
            dependencies=dependencies,
            context=context or instance.context
        )
    
    def _flatten_activities(self, instance: ProcessInstanceState) -> List[ActivityInstanceState]:
        """Flatten the activity hierarchy into a list.
        
        Args:
            instance: Process instance state
            
        Returns:
            List of all activity instances
        """
        activities = list(instance.activity_states.values())
        
        # Add activities from sub-processes recursively
        for sub_instance in instance.sub_process_states.values():
            activities.extend(self._flatten_activities(sub_instance))
            
        return activities
    
    def _identify_dependencies(self, 
                              process: Process, 
                              instance: ProcessInstanceState) -> List[ActivityDependency]:
        """Identify dependencies between activities.
        
        Args:
            process: Process definition
            instance: Process instance state
            
        Returns:
            List of activity dependencies
        """
        dependencies = []
        
        # Create structural dependencies based on process hierarchy
        # Activities within a process are typically sequential unless otherwise specified
        self._create_sequential_dependencies(process, dependencies)
        
        # Create data dependencies based on inputs and outputs
        self._create_data_dependencies(process, dependencies)
        
        # Create dependencies for sub-processes
        for sub_process in process.sub_processes:
            sub_instance = next(
                (i for i in instance.sub_process_states.values() if i.process_id == sub_process.process_id),
                None
            )
            
            if sub_instance:
                sub_dependencies = self._identify_dependencies(sub_process, sub_instance)
                dependencies.extend(sub_dependencies)
                
        return dependencies
    
    def _create_sequential_dependencies(self, process: Process, dependencies: List[ActivityDependency]) -> None:
        """Create sequential dependencies between activities in a process.
        
        Args:
            process: Process definition
            dependencies: List to add dependencies to
        """
        activities = process.activities
        
        # Create dependencies for sequential activities
        for i in range(1, len(activities)):
            prev_activity = activities[i-1]
            curr_activity = activities[i]
            
            dependencies.append(ActivityDependency(
                source_activity_id=prev_activity.activity_id,
                target_activity_id=curr_activity.activity_id,
                dependency_type="follows"
            ))
            
        # Create dependencies for sub-processes
        for sub_process in process.sub_processes:
            self._create_sequential_dependencies(sub_process, dependencies)
    
    def _create_data_dependencies(self, process: Process, dependencies: List[ActivityDependency]) -> None:
        """Create data dependencies between activities based on inputs and outputs.
        
        Args:
            process: Process definition
            dependencies: List to add dependencies to
        """
        # Create an index of outputs by name
        output_producers = defaultdict(list)
        
        # Map all activities producing outputs
        for activity in process.get_all_activities():
            for output in activity.outputs:
                output_producers[output.name].append(activity)
                
        # Create dependencies for inputs
        for activity in process.get_all_activities():
            for input_req in activity.inputs:
                # Find activities that produce this input
                producers = output_producers.get(input_req.name, [])
                
                for producer in producers:
                    # Create dependency
                    dependencies.append(ActivityDependency(
                        source_activity_id=producer.activity_id,
                        target_activity_id=activity.activity_id,
                        dependency_type="data_dependency",
                        optional=not input_req.required
                    ))
    
    def resolve_activity_requirements(self, 
                                    activity_id: str, 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve input requirements for an activity.
        
        Args:
            activity_id: ID of the activity
            context: Execution context
            
        Returns:
            Dictionary of resolved input values
        """
        # Find the activity definition
        activity = self.repository.get_activity_by_id(activity_id)
        if not activity:
            self.logger.error(f"Activity not found: {activity_id}")
            return {}
            
        # Resolve input values from context
        resolved_inputs = {}
        
        for input_req in activity.inputs:
            # Try to find the input in the context
            if input_req.name in context:
                resolved_inputs[input_req.name] = context[input_req.name]
            elif input_req.default_value is not None:
                resolved_inputs[input_req.name] = input_req.default_value
            elif input_req.required:
                self.logger.warning(f"Required input '{input_req.name}' not found in context for activity {activity_id}")
                
        return resolved_inputs
    
    def update_context_with_outputs(self, 
                                  activity_id: str, 
                                  outputs: Dict[str, Any],
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Update the execution context with activity outputs.
        
        Args:
            activity_id: ID of the activity
            outputs: Activity output values
            context: Current execution context
            
        Returns:
            Updated execution context
        """
        # Find the activity definition
        activity = self.repository.get_activity_by_id(activity_id)
        if not activity:
            self.logger.error(f"Activity not found: {activity_id}")
            return context
            
        # Create a copy of the context
        updated_context = context.copy()
        
        # Add outputs to the context
        for output_def in activity.outputs:
            if output_def.name in outputs:
                updated_context[output_def.name] = outputs[output_def.name]
                
        return updated_context