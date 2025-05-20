# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file defines what a "piece of knowledge" looks like in our system.
# It's like creating a form that helps us store information in an organized way.

# High School Explanation:
# This module defines the Entity class, which represents a discrete unit of knowledge
# within the TISIT system. Entities encapsulate metadata, descriptions, tags, and references
# to form the building blocks of the knowledge graph.

import uuid
import datetime
from typing import Dict, List, Optional, Any, Set


class Entity:
    """
    Represents a discrete unit of knowledge within the TISIT system.
    
    Entities are the primary building blocks of the knowledge graph, representing
    concepts, frameworks, strategies, campaigns, or any other discrete knowledge element.
    """
    
    VALID_TYPES = {
        # Marketing concepts
        'campaign', 'audience_segment', 'creative_approach', 'channel', 
        'strategy', 'metric', 'brand', 'message', 'asset',
        
        # General knowledge types
        'concept', 'framework', 'person', 'company', 'product', 'technology',
        'methodology', 'process', 'standard', 'term', 'package'
    }
    
    def __init__(
        self,
        name: str,
        entity_type: str,
        short_description: str = "",
        detailed_description: str = "",
        tags: Optional[List[str]] = None,
        domain: Optional[str] = None,
        created_by: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        entity_id: Optional[str] = None
    ):
        """
        Initialize a new Entity instance.
        
        Args:
            name: The name of the entity
            entity_type: The type of entity (must be in VALID_TYPES)
            short_description: A brief description of the entity
            detailed_description: An in-depth description
            tags: List of tags for categorization
            domain: The primary domain this entity belongs to
            created_by: Identifier of the creator (user, agent, etc.)
            metadata: Additional custom metadata as key-value pairs
            entity_id: Unique identifier (generated if not provided)
        """
        if entity_type not in self.VALID_TYPES:
            raise ValueError(f"Entity type '{entity_type}' is not valid. "
                           f"Valid types are: {', '.join(sorted(self.VALID_TYPES))}")
        
        self.id = entity_id or str(uuid.uuid4())
        self.name = name
        self.entity_type = entity_type
        self.short_description = short_description
        self.detailed_description = detailed_description
        self.tags = tags or []
        self.domain = domain
        self.created_by = created_by
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
        self.metadata = metadata or {}
        self.relationships = {}  # Dict[entity_id, relationship_type]
        self.references = []  # List of external references/sources
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the entity if it doesn't already exist."""
        if tag not in self.tags:
            self.tags.append(tag)
            self._update_timestamp()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the entity if it exists."""
        if tag in self.tags:
            self.tags.remove(tag)
            self._update_timestamp()
    
    def update_description(self, short: Optional[str] = None, detailed: Optional[str] = None) -> None:
        """Update the entity's descriptions."""
        if short is not None:
            self.short_description = short
        if detailed is not None:
            self.detailed_description = detailed
        self._update_timestamp()
    
    def add_reference(self, reference: Dict[str, str]) -> None:
        """
        Add an external reference to the entity.
        
        Args:
            reference: Dict containing reference data (url, title, etc.)
        """
        self.references.append(reference)
        self._update_timestamp()
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add or update metadata for the entity."""
        self.metadata[key] = value
        self._update_timestamp()
    
    def remove_metadata(self, key: str) -> None:
        """Remove metadata if it exists."""
        if key in self.metadata:
            del self.metadata[key]
            self._update_timestamp()
    
    def add_relationship(self, target_id: str, relation_type: str) -> None:
        """Record a relationship to another entity."""
        self.relationships[target_id] = relation_type
        self._update_timestamp()
    
    def remove_relationship(self, target_id: str) -> None:
        """Remove a relationship if it exists."""
        if target_id in self.relationships:
            del self.relationships[target_id]
            self._update_timestamp()
    
    def _update_timestamp(self) -> None:
        """Update the entity's last modified timestamp."""
        self.updated_at = datetime.datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entity to a dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type,
            "short_description": self.short_description,
            "detailed_description": self.detailed_description,
            "tags": self.tags,
            "domain": self.domain,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "relationships": self.relationships,
            "references": self.references
        }
        
    def to_json(self) -> str:
        """Convert the entity to a JSON string."""
        import json
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create an Entity instance from a dictionary."""
        entity = cls(
            name=data["name"],
            entity_type=data["entity_type"],
            short_description=data.get("short_description", ""),
            detailed_description=data.get("detailed_description", ""),
            tags=data.get("tags", []),
            domain=data.get("domain"),
            created_by=data.get("created_by"),
            metadata=data.get("metadata", {}),
            entity_id=data["id"]
        )
        
        # Set timestamps directly
        entity.created_at = data.get("created_at", entity.created_at)
        entity.updated_at = data.get("updated_at", entity.updated_at)
        
        # Set relationships and references
        entity.relationships = data.get("relationships", {})
        entity.references = data.get("references", [])
        
        return entity
        
    @classmethod
    def from_json(cls, json_str: str) -> 'Entity':
        """Create an Entity instance from a JSON string."""
        import json
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        """String representation of the entity."""
        return f"{self.name} ({self.entity_type}): {self.short_description}"
    
    def __eq__(self, other) -> bool:
        """Compare entities by their ID."""
        if not isinstance(other, Entity):
            return False
        return self.id == other.id