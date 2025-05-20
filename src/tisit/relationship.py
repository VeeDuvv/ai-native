# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps us connect pieces of knowledge together, like explaining
# that a dog is a type of pet, or that rain comes from clouds.

# High School Explanation:
# This module defines the Relationship class, which represents connections between
# entities in the TISIT knowledge graph. It allows for typed, directed relationships
# with metadata and bidirectional traversal capabilities.

import uuid
import datetime
from typing import Dict, Optional, Any, List


class Relationship:
    """
    Represents a typed, directed relationship between two entities in the knowledge graph.
    
    Relationships are the connections that give the knowledge graph its structure and
    allow for traversal, inference, and context building.
    """
    
    # Standard relationship types with their inverse mappings
    RELATIONSHIP_TYPES = {
        # Hierarchical relationships
        'is_a': 'has_type',
        'part_of': 'contains',
        'instance_of': 'has_instance',
        
        # Dependency relationships
        'depends_on': 'enables',
        'requires': 'required_by',
        'uses': 'used_by',
        
        # Influence relationships
        'affects': 'affected_by',
        'influences': 'influenced_by',
        'created_by': 'created',
        
        # Similarity relationships
        'similar_to': 'similar_to',  # Symmetric
        'alternative_to': 'alternative_to',  # Symmetric
        
        # Marketing-specific relationships
        'targets': 'targeted_by',
        'performs_well_on': 'suitable_for',
        'measured_by': 'measures',
        'increases': 'increased_by',
        'decreases': 'decreased_by',
        'correlates_with': 'correlates_with',  # Symmetric
        'competing_with': 'competing_with',  # Symmetric
    }
    
    # Add inverse mappings automatically
    for rel, inv in list(RELATIONSHIP_TYPES.items()):
        if inv not in RELATIONSHIP_TYPES:
            RELATIONSHIP_TYPES[inv] = rel
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        description: str = "",
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        relationship_id: Optional[str] = None
    ):
        """
        Initialize a new Relationship instance.
        
        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            relation_type: Type of relationship (must be in RELATIONSHIP_TYPES)
            description: Optional description of the relationship
            weight: Strength or importance of the relationship (0.0 to 1.0)
            metadata: Additional custom metadata
            relationship_id: Unique identifier (generated if not provided)
        """
        if relation_type not in self.RELATIONSHIP_TYPES:
            raise ValueError(f"Relationship type '{relation_type}' is not valid. "
                           f"Valid types are: {', '.join(sorted(self.RELATIONSHIP_TYPES))}")
        
        self.id = relationship_id or str(uuid.uuid4())
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type
        self.description = description
        self.weight = max(0.0, min(1.0, weight))  # Clamp between 0 and 1
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = self.created_at
        self.metadata = metadata or {}
    
    def update_weight(self, weight: float) -> None:
        """Update the relationship's weight, clamping between 0 and 1."""
        self.weight = max(0.0, min(1.0, weight))
        self._update_timestamp()
    
    def update_description(self, description: str) -> None:
        """Update the relationship's description."""
        self.description = description
        self._update_timestamp()
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add or update metadata for the relationship."""
        self.metadata[key] = value
        self._update_timestamp()
    
    def remove_metadata(self, key: str) -> None:
        """Remove metadata if it exists."""
        if key in self.metadata:
            del self.metadata[key]
            self._update_timestamp()
    
    def get_inverse_type(self) -> str:
        """Get the inverse relationship type."""
        return self.RELATIONSHIP_TYPES.get(self.relation_type, "related_to")
    
    def _update_timestamp(self) -> None:
        """Update the relationship's last modified timestamp."""
        self.updated_at = datetime.datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the relationship to a dictionary for serialization."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "description": self.description,
            "weight": self.weight,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create a Relationship instance from a dictionary."""
        relationship = cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            relation_type=data["relation_type"],
            description=data.get("description", ""),
            weight=data.get("weight", 1.0),
            metadata=data.get("metadata", {}),
            relationship_id=data["id"]
        )
        
        # Set timestamps directly
        relationship.created_at = data.get("created_at", relationship.created_at)
        relationship.updated_at = data.get("updated_at", relationship.updated_at)
        
        return relationship
    
    def __str__(self) -> str:
        """String representation of the relationship."""
        return f"{self.source_id} --[{self.relation_type}]--> {self.target_id}"
    
    def __eq__(self, other) -> bool:
        """Compare relationships by their ID."""
        if not isinstance(other, Relationship):
            return False
        return self.id == other.id