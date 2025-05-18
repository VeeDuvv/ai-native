# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file is like a big library that stores all the business processes. It helps us
# find and keep track of different business recipes that our AI agents can follow.

# High School Explanation:
# This module implements the ProcessRepository class, which serves as a central storage
# system for process framework definitions. It handles loading, saving, and querying
# process frameworks, processes, and activities from persistent storage.

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import logging
from datetime import datetime

from .core import ProcessFramework, Process, Activity


class ProcessRepository:
    """Central repository for storing and retrieving process frameworks.
    
    This class provides methods for saving and loading process frameworks,
    searching for processes by various criteria, and managing different
    versions of frameworks.
    """
    
    def __init__(self, storage_dir: str) -> None:
        """Initialize the process repository.
        
        Args:
            storage_dir: Directory for storing process framework files
        """
        self.storage_dir = Path(storage_dir)
        self.frameworks_dir = self.storage_dir / "frameworks"
        self.frameworks_dir.mkdir(parents=True, exist_ok=True)
        
        self.frameworks: Dict[str, ProcessFramework] = {}
        self.logger = logging.getLogger(__name__)
        
        # Load existing frameworks
        self._load_frameworks()
        
    def _load_frameworks(self) -> None:
        """Load all framework definitions from disk."""
        framework_files = list(self.frameworks_dir.glob("*.json"))
        
        for file_path in framework_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                framework = ProcessFramework.from_dict(data)
                self.frameworks[framework.framework_id] = framework
                self.logger.info(f"Loaded framework: {framework.name} (v{framework.version})")
                
            except Exception as e:
                self.logger.error(f"Error loading framework from {file_path}: {str(e)}")
                
    def _get_framework_path(self, framework_id: str) -> Path:
        """Get the file path for a framework.
        
        Args:
            framework_id: ID of the framework
            
        Returns:
            Path object for the framework file
        """
        return self.frameworks_dir / f"{framework_id}.json"
    
    def save_framework(self, framework: ProcessFramework) -> None:
        """Save a framework to the repository.
        
        Args:
            framework: The framework to save
        """
        # Convert to dictionary
        data = framework.to_dict()
        
        # Save to file
        file_path = self._get_framework_path(framework.framework_id)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        # Update in-memory cache
        self.frameworks[framework.framework_id] = framework
        self.logger.info(f"Saved framework: {framework.name} (v{framework.version})")
        
    def get_framework(self, framework_id: str) -> Optional[ProcessFramework]:
        """Get a framework by its ID.
        
        Args:
            framework_id: ID of the framework to retrieve
            
        Returns:
            The framework if found, None otherwise
        """
        return self.frameworks.get(framework_id)
    
    def delete_framework(self, framework_id: str) -> bool:
        """Delete a framework from the repository.
        
        Args:
            framework_id: ID of the framework to delete
            
        Returns:
            True if the framework was deleted, False otherwise
        """
        if framework_id not in self.frameworks:
            return False
            
        # Delete from disk
        file_path = self._get_framework_path(framework_id)
        if file_path.exists():
            file_path.unlink()
            
        # Remove from in-memory cache
        del self.frameworks[framework_id]
        self.logger.info(f"Deleted framework: {framework_id}")
        
        return True
    
    def list_frameworks(self) -> List[Dict[str, str]]:
        """List all frameworks in the repository.
        
        Returns:
            List of frameworks with basic information
        """
        return [
            {
                "id": fw.framework_id,
                "name": fw.name,
                "version": fw.version,
                "organization": fw.organization or "Unknown"
            }
            for fw in self.frameworks.values()
        ]
    
    def find_process(self, search_term: str, framework_id: Optional[str] = None) -> List[Process]:
        """Find processes matching a search term.
        
        Args:
            search_term: Term to search for in process names and descriptions
            framework_id: Optional framework ID to limit the search
            
        Returns:
            List of matching processes
        """
        results = []
        search_term = search_term.lower()
        
        frameworks_to_search = []
        if framework_id:
            if framework_id in self.frameworks:
                frameworks_to_search = [self.frameworks[framework_id]]
            else:
                return []
        else:
            frameworks_to_search = list(self.frameworks.values())
            
        for framework in frameworks_to_search:
            for process in self._search_processes_recursive(framework.root_processes, search_term):
                results.append(process)
                
        return results
    
    def _search_processes_recursive(self, processes: List[Process], search_term: str) -> List[Process]:
        """Recursively search for processes matching a term.
        
        Args:
            processes: List of processes to search
            search_term: Term to search for
            
        Returns:
            List of matching processes
        """
        results = []
        
        for process in processes:
            # Check if this process matches
            if (search_term in process.name.lower() or 
                search_term in process.description.lower() or
                search_term in process.process_id.lower()):
                results.append(process)
                
            # Check sub-processes
            sub_results = self._search_processes_recursive(process.sub_processes, search_term)
            results.extend(sub_results)
            
        return results
    
    def find_activity(self, search_term: str, framework_id: Optional[str] = None) -> List[Activity]:
        """Find activities matching a search term.
        
        Args:
            search_term: Term to search for in activity names and descriptions
            framework_id: Optional framework ID to limit the search
            
        Returns:
            List of matching activities
        """
        results = []
        search_term = search_term.lower()
        
        frameworks_to_search = []
        if framework_id:
            if framework_id in self.frameworks:
                frameworks_to_search = [self.frameworks[framework_id]]
            else:
                return []
        else:
            frameworks_to_search = list(self.frameworks.values())
            
        for framework in frameworks_to_search:
            for process in framework.root_processes:
                for activity in self._search_activities_recursive(process, search_term):
                    results.append(activity)
                    
        return results
    
    def _search_activities_recursive(self, process: Process, search_term: str) -> List[Activity]:
        """Recursively search for activities matching a term.
        
        Args:
            process: Process to search within
            search_term: Term to search for
            
        Returns:
            List of matching activities
        """
        results = []
        
        # Check activities in this process
        for activity in process.activities:
            if (search_term in activity.name.lower() or
                search_term in activity.description.lower() or
                search_term in activity.activity_id.lower() or
                any(search_term in cap.lower() for cap in activity.agent_capabilities)):
                results.append(activity)
                
        # Check activities in sub-processes
        for sub_process in process.sub_processes:
            sub_results = self._search_activities_recursive(sub_process, search_term)
            results.extend(sub_results)
            
        return results
    
    def get_process_by_id(self, process_id: str, framework_id: Optional[str] = None) -> Optional[Process]:
        """Get a process by its ID.
        
        Args:
            process_id: ID of the process to find
            framework_id: Optional framework ID to limit the search
            
        Returns:
            The process if found, None otherwise
        """
        if framework_id:
            if framework_id in self.frameworks:
                return self.frameworks[framework_id].get_process_by_id(process_id)
            return None
            
        # Search in all frameworks
        for framework in self.frameworks.values():
            process = framework.get_process_by_id(process_id)
            if process:
                return process
                
        return None
    
    def get_activity_by_id(self, activity_id: str, framework_id: Optional[str] = None) -> Optional[Activity]:
        """Get an activity by its ID.
        
        Args:
            activity_id: ID of the activity to find
            framework_id: Optional framework ID to limit the search
            
        Returns:
            The activity if found, None otherwise
        """
        if framework_id:
            if framework_id in self.frameworks:
                return self.frameworks[framework_id].get_activity_by_id(activity_id)
            return None
            
        # Search in all frameworks
        for framework in self.frameworks.values():
            activity = framework.get_activity_by_id(activity_id)
            if activity:
                return activity
                
        return None
    
    def find_by_capability(self, capability: str) -> List[Activity]:
        """Find activities that require a specific agent capability.
        
        Args:
            capability: The capability to search for
            
        Returns:
            List of activities requiring the capability
        """
        results = []
        capability = capability.lower()
        
        for framework in self.frameworks.values():
            for process in framework.root_processes:
                for activity in self._find_activities_by_capability(process, capability):
                    results.append(activity)
                    
        return results
    
    def _find_activities_by_capability(self, process: Process, capability: str) -> List[Activity]:
        """Recursively find activities requiring a capability.
        
        Args:
            process: Process to search within
            capability: Capability to search for
            
        Returns:
            List of matching activities
        """
        results = []
        
        # Check activities in this process
        for activity in process.activities:
            if any(capability in cap.lower() for cap in activity.agent_capabilities):
                results.append(activity)
                
        # Check activities in sub-processes
        for sub_process in process.sub_processes:
            sub_results = self._find_activities_by_capability(sub_process, capability)
            results.extend(sub_results)
            
        return results