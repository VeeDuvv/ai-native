# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file is like a security guard that checks if people are allowed to do things.
# It makes sure only the right people can see or change certain parts of the app.

# High School Explanation:
# This module implements a role-based access control system for securing application resources.
# It defines roles, permissions, and access control policies that can be used to authorize
# users for specific operations based on their assigned roles and the resources they
# are trying to access.

import json
import logging
import os
from enum import Enum
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Union, Callable
import uuid

# Configure logging
logger = logging.getLogger(__name__)


class Permission:
    """Represents a permission to perform an action on a resource."""
    
    def __init__(self, resource: str, action: str, description: Optional[str] = None):
        """
        Initialize a permission.
        
        Args:
            resource: The resource the permission applies to
            action: The action allowed on the resource
            description: Optional description of the permission
        """
        self.resource = resource
        self.action = action
        self.description = description
        
    @property
    def id(self) -> str:
        """Get the unique identifier for this permission."""
        return f"{self.resource}:{self.action}"
    
    def __str__(self) -> str:
        """Get a string representation of the permission."""
        return self.id
    
    def __eq__(self, other):
        """Check if two permissions are equal."""
        if not isinstance(other, Permission):
            return False
        return self.resource == other.resource and self.action == other.action
    
    def __hash__(self):
        """Get a hash of the permission."""
        return hash((self.resource, self.action))
    
    def to_dict(self) -> Dict[str, str]:
        """Convert the permission to a dictionary."""
        return {
            'resource': self.resource,
            'action': self.action,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'Permission':
        """Create a permission from a dictionary."""
        return cls(
            resource=data['resource'],
            action=data['action'],
            description=data.get('description')
        )


class Role:
    """Represents a role with a set of permissions."""
    
    def __init__(self, name: str, description: Optional[str] = None):
        """
        Initialize a role.
        
        Args:
            name: Name of the role
            description: Optional description of the role
        """
        self.name = name
        self.description = description
        self.permissions: Set[Permission] = set()
    
    def add_permission(self, permission: Permission):
        """
        Add a permission to the role.
        
        Args:
            permission: Permission to add
        """
        self.permissions.add(permission)
    
    def remove_permission(self, permission: Permission):
        """
        Remove a permission from the role.
        
        Args:
            permission: Permission to remove
        """
        self.permissions.discard(permission)
    
    def has_permission(self, permission: Permission) -> bool:
        """
        Check if the role has a specific permission.
        
        Args:
            permission: Permission to check
            
        Returns:
            True if the role has the permission, False otherwise
        """
        return permission in self.permissions
    
    def has_permissions(self, permissions: List[Permission]) -> bool:
        """
        Check if the role has all of the specified permissions.
        
        Args:
            permissions: Permissions to check
            
        Returns:
            True if the role has all the permissions, False otherwise
        """
        return all(self.has_permission(p) for p in permissions)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the role to a dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'permissions': [p.to_dict() for p in self.permissions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Role':
        """Create a role from a dictionary."""
        role = cls(
            name=data['name'],
            description=data.get('description')
        )
        
        for p_data in data.get('permissions', []):
            role.add_permission(Permission.from_dict(p_data))
        
        return role


class AccessControl:
    """
    Manages access control for the application.
    
    This class provides methods for checking permissions, managing roles and users,
    and enforcing access control policies.
    """
    
    def __init__(self, storage_path: Optional[Union[str, Path]] = None):
        """
        Initialize the access control manager.
        
        Args:
            storage_path: Path to store access control data.
                         If None, data will only be stored in memory.
        """
        self.storage_path = Path(storage_path) if storage_path else None
        
        # In-memory storage
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, List[str]] = {}
        self.user_permissions: Dict[str, Set[Permission]] = {}
        
        # Initialize storage directory if provided
        if self.storage_path:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self._load_data()
    
    def _load_data(self):
        """Load access control data from storage."""
        if not self.storage_path:
            return
        
        # Load roles
        roles_file = self.storage_path / 'roles.json'
        if roles_file.exists():
            try:
                with open(roles_file, 'r') as f:
                    roles_data = json.load(f)
                
                for role_data in roles_data:
                    role = Role.from_dict(role_data)
                    self.roles[role.name] = role
                
                logger.info(f"Loaded {len(self.roles)} roles")
            except Exception as e:
                logger.error(f"Failed to load roles: {e}")
        
        # Load user roles
        user_roles_file = self.storage_path / 'user_roles.json'
        if user_roles_file.exists():
            try:
                with open(user_roles_file, 'r') as f:
                    self.user_roles = json.load(f)
                
                logger.info(f"Loaded roles for {len(self.user_roles)} users")
            except Exception as e:
                logger.error(f"Failed to load user roles: {e}")
    
    def _save_roles(self):
        """Save roles to storage."""
        if not self.storage_path:
            return
        
        roles_file = self.storage_path / 'roles.json'
        
        try:
            roles_data = [role.to_dict() for role in self.roles.values()]
            
            with open(roles_file, 'w') as f:
                json.dump(roles_data, f, indent=2)
            
            logger.debug("Saved roles")
        except Exception as e:
            logger.error(f"Failed to save roles: {e}")
    
    def _save_user_roles(self):
        """Save user roles to storage."""
        if not self.storage_path:
            return
        
        user_roles_file = self.storage_path / 'user_roles.json'
        
        try:
            with open(user_roles_file, 'w') as f:
                json.dump(self.user_roles, f, indent=2)
            
            logger.debug("Saved user roles")
        except Exception as e:
            logger.error(f"Failed to save user roles: {e}")
    
    def create_role(self, name: str, description: Optional[str] = None) -> Role:
        """
        Create a new role.
        
        Args:
            name: Name of the role
            description: Optional description of the role
            
        Returns:
            The created role
        """
        role = Role(name, description)
        self.roles[name] = role
        
        self._save_roles()
        logger.info(f"Created role: {name}")
        
        return role
    
    def get_role(self, name: str) -> Optional[Role]:
        """
        Get a role by name.
        
        Args:
            name: Name of the role
            
        Returns:
            The role, or None if not found
        """
        return self.roles.get(name)
    
    def delete_role(self, name: str) -> bool:
        """
        Delete a role.
        
        Args:
            name: Name of the role
            
        Returns:
            True if the role was deleted, False if not found
        """
        if name not in self.roles:
            return False
        
        del self.roles[name]
        
        # Remove the role from all users
        for user_id, roles in self.user_roles.items():
            if name in roles:
                roles.remove(name)
        
        # Clear user permission caches
        self.user_permissions.clear()
        
        self._save_roles()
        self._save_user_roles()
        
        logger.info(f"Deleted role: {name}")
        
        return True
    
    def add_role_permission(self, role_name: str, permission: Permission) -> bool:
        """
        Add a permission to a role.
        
        Args:
            role_name: Name of the role
            permission: Permission to add
            
        Returns:
            True if the permission was added, False if the role was not found
        """
        role = self.get_role(role_name)
        if not role:
            return False
        
        role.add_permission(permission)
        
        # Clear user permission caches
        self.user_permissions.clear()
        
        self._save_roles()
        
        logger.info(f"Added permission {permission} to role {role_name}")
        
        return True
    
    def remove_role_permission(self, role_name: str, permission: Permission) -> bool:
        """
        Remove a permission from a role.
        
        Args:
            role_name: Name of the role
            permission: Permission to remove
            
        Returns:
            True if the permission was removed, False if the role was not found
        """
        role = self.get_role(role_name)
        if not role:
            return False
        
        role.remove_permission(permission)
        
        # Clear user permission caches
        self.user_permissions.clear()
        
        self._save_roles()
        
        logger.info(f"Removed permission {permission} from role {role_name}")
        
        return True
    
    def assign_role_to_user(self, user_id: str, role_name: str) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id: ID of the user
            role_name: Name of the role
            
        Returns:
            True if the role was assigned, False if the role was not found
        """
        if role_name not in self.roles:
            return False
        
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        
        if role_name not in self.user_roles[user_id]:
            self.user_roles[user_id].append(role_name)
        
        # Clear user permission cache
        if user_id in self.user_permissions:
            del self.user_permissions[user_id]
        
        self._save_user_roles()
        
        logger.info(f"Assigned role {role_name} to user {user_id}")
        
        return True
    
    def revoke_role_from_user(self, user_id: str, role_name: str) -> bool:
        """
        Revoke a role from a user.
        
        Args:
            user_id: ID of the user
            role_name: Name of the role
            
        Returns:
            True if the role was revoked, False if the user didn't have the role
        """
        if user_id not in self.user_roles or role_name not in self.user_roles[user_id]:
            return False
        
        self.user_roles[user_id].remove(role_name)
        
        # Clear user permission cache
        if user_id in self.user_permissions:
            del self.user_permissions[user_id]
        
        self._save_user_roles()
        
        logger.info(f"Revoked role {role_name} from user {user_id}")
        
        return True
    
    def get_user_roles(self, user_id: str) -> List[Role]:
        """
        Get all roles assigned to a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of roles assigned to the user
        """
        role_names = self.user_roles.get(user_id, [])
        return [self.roles[name] for name in role_names if name in self.roles]
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """
        Get all permissions a user has through their roles.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Set of permissions the user has
        """
        if user_id in self.user_permissions:
            return self.user_permissions[user_id]
        
        permissions = set()
        
        for role in self.get_user_roles(user_id):
            permissions.update(role.permissions)
        
        self.user_permissions[user_id] = permissions
        return permissions
    
    def has_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id: ID of the user
            permission: Permission to check
            
        Returns:
            True if the user has the permission, False otherwise
        """
        user_permissions = self.get_user_permissions(user_id)
        return permission in user_permissions
    
    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """
        Check if a user has permission to perform an action on a resource.
        
        Args:
            user_id: ID of the user
            resource: Resource to check
            action: Action to perform on the resource
            
        Returns:
            True if the user has permission, False otherwise
        """
        permission = Permission(resource, action)
        return self.has_permission(user_id, permission)
    
    def require_permission(self, user_id: str, resource: str, action: str):
        """
        Require that a user has permission to perform an action on a resource.
        
        Args:
            user_id: ID of the user
            resource: Resource to check
            action: Action to perform on the resource
            
        Raises:
            PermissionError: If the user doesn't have the required permission
        """
        if not self.check_permission(user_id, resource, action):
            raise PermissionError(f"User {user_id} doesn't have permission to {action} on {resource}")


class RBACService:
    """
    Provides role-based access control services for the application.
    
    This class offers a higher-level interface for access control operations,
    built on top of the AccessControl class.
    """
    
    def __init__(self, access_control: Optional[AccessControl] = None):
        """
        Initialize the RBAC service.
        
        Args:
            access_control: Access control instance to use.
                           If None, a new in-memory instance will be created.
        """
        self.access_control = access_control or AccessControl()
        
        # Map of resource types to their access patterns
        self.resource_patterns = {}
        
        # Permission checks for specific resources
        self.resource_checkers = {}
    
    def define_resource_pattern(self, resource_type: str, access_patterns: Dict[str, List[str]]):
        """
        Define access patterns for a resource type.
        
        Args:
            resource_type: Type of resource
            access_patterns: Dictionary mapping role names to lists of allowed actions
        """
        self.resource_patterns[resource_type] = access_patterns
        
        # Create any missing roles
        for role_name in access_patterns.keys():
            if not self.access_control.get_role(role_name):
                self.access_control.create_role(role_name)
        
        # Update role permissions
        for role_name, actions in access_patterns.items():
            for action in actions:
                permission = Permission(resource_type, action)
                self.access_control.add_role_permission(role_name, permission)
        
        logger.info(f"Defined access patterns for resource type: {resource_type}")
    
    def register_resource_checker(self, resource_type: str, 
                               checker: Callable[[str, str, str, Any], bool]):
        """
        Register a function to check permissions for specific resource instances.
        
        Args:
            resource_type: Type of resource
            checker: Function that takes (user_id, resource_id, action, resource) and returns a boolean
        """
        self.resource_checkers[resource_type] = checker
        logger.debug(f"Registered resource checker for {resource_type}")
    
    def create_standard_roles(self):
        """Create standard roles with common permission sets."""
        # Admin role
        admin_role = self.access_control.get_role('admin')
        if not admin_role:
            admin_role = self.access_control.create_role('admin', 'Administrator with full access')
        
        # User role
        user_role = self.access_control.get_role('user')
        if not user_role:
            user_role = self.access_control.create_role('user', 'Standard user with limited access')
        
        # Guest role
        guest_role = self.access_control.get_role('guest')
        if not guest_role:
            guest_role = self.access_control.create_role('guest', 'Guest with minimal access')
        
        logger.info("Created standard roles")
    
    def check_resource_access(self, user_id: str, resource_type: str, 
                           resource_id: str, action: str, 
                           resource: Optional[Any] = None) -> bool:
        """
        Check if a user has permission to perform an action on a specific resource.
        
        Args:
            user_id: ID of the user
            resource_type: Type of resource
            resource_id: ID of the resource
            action: Action to perform
            resource: Optional resource object for custom checks
            
        Returns:
            True if the user has permission, False otherwise
        """
        # First, check if the user has the permission through their roles
        if not self.access_control.check_permission(user_id, resource_type, action):
            return False
        
        # Then, check any resource-specific permissions
        checker = self.resource_checkers.get(resource_type)
        if checker and not checker(user_id, resource_id, action, resource):
            return False
        
        return True
    
    def authorize(self, user_id: str, resource_type: str, resource_id: str, 
                action: str, resource: Optional[Any] = None):
        """
        Authorize a user to perform an action on a specific resource.
        
        Args:
            user_id: ID of the user
            resource_type: Type of resource
            resource_id: ID of the resource
            action: Action to perform
            resource: Optional resource object for custom checks
            
        Raises:
            PermissionError: If the user doesn't have permission
        """
        if not self.check_resource_access(user_id, resource_type, resource_id, action, resource):
            raise PermissionError(
                f"User {user_id} is not authorized to {action} {resource_type} {resource_id}"
            )
    
    def get_allowed_actions(self, user_id: str, resource_type: str, 
                          resource_id: Optional[str] = None,
                          resource: Optional[Any] = None) -> List[str]:
        """
        Get all actions a user is allowed to perform on a resource type or specific resource.
        
        Args:
            user_id: ID of the user
            resource_type: Type of resource
            resource_id: Optional ID of a specific resource
            resource: Optional resource object for custom checks
            
        Returns:
            List of allowed actions
        """
        # Get all possible actions for this resource type
        all_actions = set()
        for actions in self.resource_patterns.get(resource_type, {}).values():
            all_actions.update(actions)
        
        # Filter by user's permissions
        allowed_actions = []
        for action in all_actions:
            if resource_id:
                if self.check_resource_access(user_id, resource_type, resource_id, action, resource):
                    allowed_actions.append(action)
            else:
                if self.access_control.check_permission(user_id, resource_type, action):
                    allowed_actions.append(action)
        
        return allowed_actions
    
    def get_accessible_resources(self, user_id: str, resource_type: str, 
                              action: str, resources: List[Any],
                              id_extractor: Callable[[Any], str]) -> List[Any]:
        """
        Filter a list of resources to only those the user can access.
        
        Args:
            user_id: ID of the user
            resource_type: Type of resource
            action: Action to check
            resources: List of resource objects
            id_extractor: Function to extract the ID from a resource
            
        Returns:
            List of resources the user can access
        """
        return [
            resource for resource in resources
            if self.check_resource_access(
                user_id, resource_type, id_extractor(resource), action, resource
            )
        ]