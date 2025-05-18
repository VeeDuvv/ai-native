# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file defines what information we collect about important ideas and things in our project.
# It's like a special form that we fill out for each piece of knowledge we want to remember.

# High School Explanation:
# This module implements the Entity class, which represents a single knowledge entity in
# the TISIT knowledge graph. It provides the data structure, validation, and methods for
# managing individual pieces of knowledge within our second brain implementation.

from datetime import datetime
from typing import Dict, List, Optional, Union, Any
import json
import uuid

class Entity:
    """Represents a knowledge entity in the TISIT system.
    
    An entity can be a framework, package, concept, person, company, or term.
    Each entity has properties like name, type, descriptions, and relationships
    to other entities.
    """
    
    VALID_TYPES = [
        "framework", "package", "concept", "person", "company", "term",
        "methodology", "technology", "process", "metric", "standard"
    ]
    
    def __init__(self, 
                 name: str, 
                 entity_type: str,
                 short_description: str,
                 detailed_description: Optional[str] = None,
                 entity_id: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 first_encountered: Optional[str] = None,
                 last_updated: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 references: Optional[List[Dict[str, str]]] = None,
                 links: Optional[List[Dict[str, str]]] = None) -> None:
        """Initialize a new knowledge entity.
        
        Args:
            name: The name of the entity
            entity_type: The type of entity (must be one of VALID_TYPES)
            short_description: A one-sentence summary of the entity
            detailed_description: A comprehensive explanation (optional)
            entity_id: A unique identifier (generated if not provided)
            tags: A list of tags associated with this entity
            first_encountered: When this entity was first added (ISO-8601)
            last_updated: When this entity was last modified (ISO-8601)
            metadata: Additional metadata for the entity
            references: List of references to this entity
            links: Relationships to other entities
        """
        # Validate entity type
        if entity_type not in self.VALID_TYPES:
            raise ValueError(
                f"Invalid entity type: {entity_type}. Must be one of: {', '.join(self.VALID_TYPES)}"
            )
            
        # Required fields
        self.name = name
        self.type = entity_type
        self.short_description = short_description
        
        # Optional fields with defaults
        self.id = entity_id or str(uuid.uuid4())
        self.detailed_description = detailed_description or ""
        self.tags = tags or []
        self.first_encountered = first_encountered or datetime.now().isoformat()
        self.last_updated = last_updated or datetime.now().isoformat()
        self.metadata = metadata or {}
        self.references = references or []
        self.links = links or []
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the entity if it doesn't already exist.
        
        Args:
            tag: The tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
            self._update_timestamp()
            
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the entity if it exists.
        
        Args:
            tag: The tag to remove
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self._update_timestamp()
    
    def add_link(self, target_id: str, relation_type: str, description: Optional[str] = None) -> None:
        """Add a relationship link to another entity.
        
        Args:
            target_id: The ID of the target entity
            relation_type: The type of relationship (depends_on, created_by, etc.)
            description: Optional description of the relationship
        """
        link = {
            "relation_type": relation_type,
            "target_id": target_id,
            "description": description or ""
        }
        
        # Check if the exact same link already exists
        for existing_link in self.links:
            if (existing_link["target_id"] == target_id and 
                existing_link["relation_type"] == relation_type):
                return  # Link already exists, don't add it again
                
        self.links.append(link)
        self._update_timestamp()
    
    def remove_link(self, target_id: str, relation_type: Optional[str] = None) -> None:
        """Remove a relationship link to another entity.
        
        Args:
            target_id: The ID of the target entity
            relation_type: Optional relation type to be more specific
        """
        original_length = len(self.links)
        
        if relation_type:
            self.links = [link for link in self.links if not 
                         (link["target_id"] == target_id and link["relation_type"] == relation_type)]
        else:
            self.links = [link for link in self.links if link["target_id"] != target_id]
            
        if len(self.links) != original_length:
            self._update_timestamp()
    
    def add_reference(self, location: str, ref_type: str = "external", context: Optional[str] = None) -> None:
        """Add a reference to this entity.
        
        Args:
            location: The file path or URL of the reference
            ref_type: The type of reference (internal or external)
            context: Optional context about how/where this was referenced
        """
        reference = {
            "type": ref_type,
            "location": location,
            "context": context or ""
        }
        
        self.references.append(reference)
        self._update_timestamp()
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update or add a metadata field.
        
        Args:
            key: The metadata key
            value: The metadata value
        """
        self.metadata[key] = value
        self._update_timestamp()
    
    def _update_timestamp(self) -> None:
        """Update the last_updated timestamp to the current time."""
        self.last_updated = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entity to a dictionary representation.
        
        Returns:
            A dictionary containing all entity properties
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "short_description": self.short_description,
            "detailed_description": self.detailed_description,
            "first_encountered": self.first_encountered,
            "last_updated": self.last_updated,
            "tags": self.tags,
            "links": self.links,
            "metadata": self.metadata,
            "references": self.references
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert the entity to a JSON string.
        
        Args:
            indent: Number of spaces for indentation
            
        Returns:
            A JSON string representation of the entity
        """
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create an Entity instance from a dictionary.
        
        Args:
            data: Dictionary containing entity properties
            
        Returns:
            A new Entity instance
        """
        return cls(
            name=data["name"],
            entity_type=data["type"],
            short_description=data["short_description"],
            detailed_description=data.get("detailed_description"),
            entity_id=data.get("id"),
            tags=data.get("tags"),
            first_encountered=data.get("first_encountered"),
            last_updated=data.get("last_updated"),
            metadata=data.get("metadata"),
            references=data.get("references"),
            links=data.get("links")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Entity':
        """Create an Entity instance from a JSON string.
        
        Args:
            json_str: JSON string representing an entity
            
        Returns:
            A new Entity instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
