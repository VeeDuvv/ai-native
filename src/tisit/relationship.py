# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps us connect different pieces of knowledge together, like showing that
# one idea is related to another idea. It's like drawing lines between important things
# to show how they are connected.

# High School Explanation:
# This module implements the Relationship class, which represents the connections
# between knowledge entities in the TISIT graph. It defines the structure, types,
# and properties of relationships, as well as methods for creating and managing them.

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import uuid

class Relationship:
    """Represents a relationship between two entities in the TISIT knowledge graph.
    
    Relationships are directed connections between entities with specific types
    and optional properties.
    """
    
    VALID_TYPES = [
        "depends_on", "created_by", "similar_to", "part_of", "uses", 
        "implements", "extends", "supersedes", "related_to", "contains",
        "alternative_to", "inspires", "derived_from", "successor_of",
        "predecessor_of", "competes_with", "complements", "integrates_with"
    ]
    
    def __init__(self, 
                 source_id: str,
                 target_id: str,
                 relation_type: str,
                 description: Optional[str] = None,
                 relationship_id: Optional[str] = None,
                 properties: Optional[Dict[str, Any]] = None,
                 bidirectional: bool = False,
                 created_at: Optional[str] = None,
                 last_updated: Optional[str] = None) -> None:
        """Initialize a new relationship between entities.
        
        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            relation_type: Type of relationship (must be one of VALID_TYPES)
            description: Optional description of the relationship
            relationship_id: Unique identifier (generated if not provided)
            properties: Additional properties for the relationship
            bidirectional: Whether the relationship applies equally in both directions
            created_at: When the relationship was created (ISO-8601)
            last_updated: When the relationship was last modified (ISO-8601)
        """
        # Validate relationship type
        if relation_type not in self.VALID_TYPES:
            raise ValueError(
                f"Invalid relationship type: {relation_type}. Must be one of: {', '.join(self.VALID_TYPES)}"
            )
            
        # Required fields
        self.source_id = source_id
        self.target_id = target_id
        self.type = relation_type
        
        # Optional fields with defaults
        self.id = relationship_id or str(uuid.uuid4())
        self.description = description or ""
        self.properties = properties or {}
        self.bidirectional = bidirectional
        self.created_at = created_at or datetime.now().isoformat()
        self.last_updated = last_updated or datetime.now().isoformat()
    
    def update_property(self, key: str, value: Any) -> None:
        """Set or update a property of the relationship.
        
        Args:
            key: The property name
            value: The property value
        """
        self.properties[key] = value
        self._update_timestamp()
    
    def remove_property(self, key: str) -> bool:
        """Remove a property from the relationship.
        
        Args:
            key: The property name to remove
            
        Returns:
            True if the property existed and was removed, False otherwise
        """
        if key in self.properties:
            del self.properties[key]
            self._update_timestamp()
            return True
        return False
    
    def update_description(self, description: str) -> None:
        """Update the relationship description.
        
        Args:
            description: The new description
        """
        self.description = description
        self._update_timestamp()
    
    def set_bidirectional(self, bidirectional: bool) -> None:
        """Set whether the relationship is bidirectional.
        
        Args:
            bidirectional: True if the relationship applies equally in both directions
        """
        self.bidirectional = bidirectional
        self._update_timestamp()
    
    def _update_timestamp(self) -> None:
        """Update the last_updated timestamp to the current time."""
        self.last_updated = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the relationship to a dictionary representation.
        
        Returns:
            A dictionary containing all relationship properties
        """
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
            "description": self.description,
            "properties": self.properties,
            "bidirectional": self.bidirectional,
            "created_at": self.created_at,
            "last_updated": self.last_updated
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert the relationship to a JSON string.
        
        Args:
            indent: Number of spaces for indentation
            
        Returns:
            A JSON string representation of the relationship
        """
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create a Relationship instance from a dictionary.
        
        Args:
            data: Dictionary containing relationship properties
            
        Returns:
            A new Relationship instance
        """
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            relation_type=data["type"],
            description=data.get("description"),
            relationship_id=data.get("id"),
            properties=data.get("properties"),
            bidirectional=data.get("bidirectional", False),
            created_at=data.get("created_at"),
            last_updated=data.get("last_updated")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Relationship':
        """Create a Relationship instance from a JSON string.
        
        Args:
            json_str: JSON string representing a relationship
            
        Returns:
            A new Relationship instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def get_inverse_type(self) -> Optional[str]:
        """Get the inverse relationship type, if one exists.
        
        Returns:
            The inverse relationship type, or None if no clear inverse exists
        """
        inverse_map = {
            "depends_on": "required_by",
            "part_of": "contains",
            "contains": "part_of",
            "created_by": "created",
            "uses": "used_by",
            "implements": "implemented_by",
            "extends": "extended_by",
            "supersedes": "superseded_by",
            "successor_of": "predecessor_of",
            "predecessor_of": "successor_of"
        }
        
        return inverse_map.get(self.type)