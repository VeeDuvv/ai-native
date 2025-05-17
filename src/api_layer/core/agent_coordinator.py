# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps our web service talk to our AI helpers. It's like a translator that
# takes requests from the internet and turns them into instructions that our AI helpers
# can understand.

# High School Explanation:
# This module provides the interface between the API layer and the agent framework.
# It translates API requests into agent tasks, selects appropriate agents based on
# capabilities, and transforms agent results back into API responses.

"""
Agent coordinator for the API layer.

This module bridges the gap between the API layer and the agent framework,
providing a clean interface for API controllers to interact with agents
without needing to understand the details of agent execution.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Type, Union
import asyncio
from datetime import datetime

# Import agent framework types
from src.agent_framework.core.interfaces import BaseAgent
from src.agent_framework.core.process import ProcessActivity, ProcessFrameworkType

# Set up logging
logger = logging.getLogger("api.agent_coordinator")


class AgentCoordinator:
    """
    Coordinator for agent execution from the API layer.
    
    This class provides a high-level interface for API controllers to
    interact with the agent framework, handling agent selection,
    execution, and result transformation.
    """
    
    def __init__(self):
        """Initialize the agent coordinator."""
        self.available_agents: Dict[str, BaseAgent] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
        self.registered_activities: Dict[str, Dict[str, Any]] = {}
        self.task_status: Dict[str, Dict[str, Any]] = {}
    
    def register_agent(self, agent_id: str, agent: BaseAgent) -> None:
        """
        Register an agent with the coordinator.
        
        Args:
            agent_id: Unique identifier for the agent
            agent: Agent instance
        """
        self.available_agents[agent_id] = agent
        self.agent_capabilities[agent_id] = agent.get_capabilities()
        logger.info(f"Registered agent: {agent_id} with capabilities: {', '.join(self.agent_capabilities[agent_id])}")
    
    def register_process_activity(
        self,
        framework_id: str,
        activity_id: str,
        required_capabilities: List[str],
        input_schema: Dict[str, Any],
        output_schema: Dict[str, Any]
    ) -> None:
        """
        Register a process framework activity.
        
        Args:
            framework_id: Process framework identifier
            activity_id: Activity identifier
            required_capabilities: Capabilities required to execute this activity
            input_schema: Schema for activity inputs
            output_schema: Schema for activity outputs
        """
        activity_key = f"{framework_id}:{activity_id}"
        self.registered_activities[activity_key] = {
            "framework_id": framework_id,
            "activity_id": activity_id,
            "required_capabilities": required_capabilities,
            "input_schema": input_schema,
            "output_schema": output_schema
        }
        logger.info(f"Registered activity: {activity_key}")
    
    def find_agents_for_capabilities(self, required_capabilities: List[str]) -> List[str]:
        """
        Find agents that have all the required capabilities.
        
        Args:
            required_capabilities: List of required capabilities
            
        Returns:
            List[str]: List of agent IDs that meet the requirements
        """
        matching_agents = []
        
        for agent_id, capabilities in self.agent_capabilities.items():
            if all(cap in capabilities for cap in required_capabilities):
                matching_agents.append(agent_id)
        
        return matching_agents
    
    def find_agents_for_activity(self, framework_id: str, activity_id: str) -> List[str]:
        """
        Find agents that can execute a specific process activity.
        
        Args:
            framework_id: Process framework identifier
            activity_id: Activity identifier
            
        Returns:
            List[str]: List of agent IDs that can execute the activity
        """
        activity_key = f"{framework_id}:{activity_id}"
        
        if activity_key not in self.registered_activities:
            logger.warning(f"Activity not registered: {activity_key}")
            return []
        
        required_capabilities = self.registered_activities[activity_key]["required_capabilities"]
        return self.find_agents_for_capabilities(required_capabilities)
    
    async def execute_task(
        self,
        agent_id: str,
        task_type: str,
        task_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a task with a specific agent.
        
        Args:
            agent_id: Agent identifier
            task_type: Type of task to execute
            task_data: Task input data
            context: Additional execution context
            
        Returns:
            Dict[str, Any]: Task execution results
            
        Raises:
            ValueError: If the agent does not exist
        """
        # Check if agent exists
        if agent_id not in self.available_agents:
            raise ValueError(f"Agent not found: {agent_id}")
        
        # Get agent
        agent = self.available_agents[agent_id]
        
        # Create task ID
        task_id = str(uuid.uuid4())
        
        # Create execution context
        task_context = {
            "task_id": task_id,
            "task_type": task_type,
            "data": task_data,
            **(context or {})
        }
        
        # Initialize task status
        self.task_status[task_id] = {
            "agent_id": agent_id,
            "task_type": task_type,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result": None
        }
        
        try:
            # Update task status
            self.task_status[task_id]["status"] = "executing"
            self.task_status[task_id]["updated_at"] = datetime.now().isoformat()
            
            # Execute task
            logger.info(f"Executing task {task_id} with agent {agent_id}: {task_type}")
            result = agent.execute(task_context)
            
            # Update task status
            self.task_status[task_id]["status"] = "completed"
            self.task_status[task_id]["updated_at"] = datetime.now().isoformat()
            self.task_status[task_id]["result"] = result
            
            return result
        except Exception as e:
            # Update task status
            self.task_status[task_id]["status"] = "failed"
            self.task_status[task_id]["updated_at"] = datetime.now().isoformat()
            self.task_status[task_id]["error"] = str(e)
            
            logger.exception(f"Error executing task {task_id} with agent {agent_id}: {e}")
            raise
    
    async def execute_process_activity(
        self,
        framework_id: str,
        activity_id: str,
        input_data: Dict[str, Any],
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a process activity.
        
        Args:
            framework_id: Process framework identifier
            activity_id: Activity identifier
            input_data: Activity input data
            agent_id: Optional specific agent to use
            
        Returns:
            Dict[str, Any]: Activity execution results
            
        Raises:
            ValueError: If the activity is not registered or no suitable agent is found
        """
        activity_key = f"{framework_id}:{activity_id}"
        
        # Check if activity is registered
        if activity_key not in self.registered_activities:
            raise ValueError(f"Activity not registered: {activity_key}")
        
        # Find a suitable agent if not specified
        if agent_id is None:
            suitable_agents = self.find_agents_for_activity(framework_id, activity_id)
            
            if not suitable_agents:
                raise ValueError(f"No suitable agent found for activity: {activity_key}")
            
            agent_id = suitable_agents[0]
        elif agent_id not in self.available_agents:
            raise ValueError(f"Agent not found: {agent_id}")
        
        # Create task context
        context = {
            "framework_id": framework_id,
            "activity_id": activity_id,
            "activity_key": activity_key
        }
        
        # Execute task
        return await self.execute_task(
            agent_id=agent_id,
            task_type="process_activity",
            task_data=input_data,
            context=context
        )
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Optional[Dict[str, Any]]: Task status or None if not found
        """
        return self.task_status.get(task_id)


# Create a global coordinator instance
coordinator = AgentCoordinator()