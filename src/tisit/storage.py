# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps us save and find our knowledge entities. It's like a filing cabinet
# where we store all our important information cards so we can find them later.

# High School Explanation:
# This module implements the EntityStorage class, which manages the persistence of
# knowledge entities to disk. It handles reading and writing entity JSON files, maintaining
# indexes, and providing efficient query capabilities for the knowledge graph.

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import shutil

from .entity import Entity

class EntityStorage:
    """Manages the storage and retrieval of knowledge entities.
    
    This class handles the persistence of entities to the file system, maintains
    indexes for efficient querying, and provides operations to find, update, and
    delete entities.
    """
    
    def __init__(self, storage_root: str) -> None:
        """Initialize the entity storage system.
        
        Args:
            storage_root: The root directory for storing entities and indexes
        """
        self.storage_root = Path(storage_root)
        self.entities_dir = self.storage_root / "entities"
        self.indexes_dir = self.storage_root / "indexes"
        
        # Create directory structure if it doesn't exist
        self.entities_dir.mkdir(parents=True, exist_ok=True)
        self.indexes_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize indexes
        self.term_index: Dict[str, str] = {}
        self.tag_index: Dict[str, List[str]] = {}
        self.type_index: Dict[str, List[str]] = {}
        
        # Load existing indexes if they exist
        self._load_indexes()
    
    def _load_indexes(self) -> None:
        """Load existing indexes from disk."""
        term_index_path = self.indexes_dir / "term-index.json"
        tag_index_path = self.indexes_dir / "tag-index.json"
        type_index_path = self.indexes_dir / "type-index.json"
        
        if term_index_path.exists():
            with open(term_index_path, 'r') as f:
                self.term_index = json.load(f)
                
        if tag_index_path.exists():
            with open(tag_index_path, 'r') as f:
                self.tag_index = json.load(f)
                
        if type_index_path.exists():
            with open(type_index_path, 'r') as f:
                self.type_index = json.load(f)
    
    def _save_indexes(self) -> None:
        """Save indexes to disk."""
        term_index_path = self.indexes_dir / "term-index.json"
        tag_index_path = self.indexes_dir / "tag-index.json"
        type_index_path = self.indexes_dir / "type-index.json"
        
        with open(term_index_path, 'w') as f:
            json.dump(self.term_index, f, indent=2)
            
        with open(tag_index_path, 'w') as f:
            json.dump(self.tag_index, f, indent=2)
            
        with open(type_index_path, 'w') as f:
            json.dump(self.type_index, f, indent=2)
    
    def _get_entity_path(self, entity_id: str) -> Path:
        """Get the file path for an entity.
        
        Args:
            entity_id: The unique identifier of the entity
            
        Returns:
            Path object for the entity file
        """
        return self.entities_dir / f"{entity_id}.json"
    
    def _update_indexes(self, entity: Entity) -> None:
        """Update indexes with entity information.
        
        Args:
            entity: The entity to index
        """
        # Update term index (name to id mapping)
        self.term_index[entity.name.lower()] = entity.id
        
        # Update tag index
        for tag in entity.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            if entity.id not in self.tag_index[tag]:
                self.tag_index[tag].append(entity.id)
        
        # Update type index
        if entity.entity_type not in self.type_index:
            self.type_index[entity.entity_type] = []
        if entity.id not in self.type_index[entity.entity_type]:
            self.type_index[entity.entity_type].append(entity.id)
    
    def _remove_from_indexes(self, entity: Entity) -> None:
        """Remove entity from indexes.
        
        Args:
            entity: The entity to remove from indexes
        """
        # Remove from term index
        if entity.name.lower() in self.term_index:
            del self.term_index[entity.name.lower()]
        
        # Remove from tag index
        for tag in entity.tags:
            if tag in self.tag_index and entity.id in self.tag_index[tag]:
                self.tag_index[tag].remove(entity.id)
                if not self.tag_index[tag]:  # If the tag has no more entities
                    del self.tag_index[tag]
        
        # Remove from type index
        if entity.entity_type in self.type_index and entity.id in self.type_index[entity.entity_type]:
            self.type_index[entity.entity_type].remove(entity.id)
            if not self.type_index[entity.entity_type]:  # If the type has no more entities
                del self.type_index[entity.entity_type]
    
    def save_entity(self, entity: Entity) -> None:
        """Save an entity to storage.
        
        Args:
            entity: The entity to save
        """
        # Update the entity timestamp if needed
        entity._update_timestamp()
        
        # Get the file path
        entity_path = self._get_entity_path(entity.id)
        
        # Save entity to file
        with open(entity_path, 'w') as f:
            f.write(entity.to_json())
        
        # Update indexes
        self._update_indexes(entity)
        self._save_indexes()
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Retrieve an entity by its ID.
        
        Args:
            entity_id: The unique identifier of the entity
            
        Returns:
            The entity if found, None otherwise
        """
        entity_path = self._get_entity_path(entity_id)
        
        if not entity_path.exists():
            return None
        
        with open(entity_path, 'r') as f:
            entity_json = f.read()
            
        return Entity.from_json(entity_json)
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity from storage.
        
        Args:
            entity_id: The unique identifier of the entity
            
        Returns:
            True if the entity was deleted, False if it didn't exist
        """
        entity_path = self._get_entity_path(entity_id)
        
        if not entity_path.exists():
            return False
        
        # Get the entity first to update indexes
        entity = self.get_entity(entity_id)
        if entity:
            self._remove_from_indexes(entity)
        
        # Delete the file
        entity_path.unlink()
        
        # Save updated indexes
        self._save_indexes()
        
        return True
    
    def list_entities(self) -> List[str]:
        """List all entity IDs in storage.
        
        Returns:
            List of entity IDs
        """
        entity_files = list(self.entities_dir.glob("*.json"))
        return [file.stem for file in entity_files]
    
    def find_by_name(self, name: str) -> Optional[Entity]:
        """Find an entity by its name (case-insensitive).
        
        Args:
            name: The name to search for
            
        Returns:
            The entity if found, None otherwise
        """
        name_lower = name.lower()
        
        if name_lower in self.term_index:
            return self.get_entity(self.term_index[name_lower])
        
        return None
    
    def find_by_tags(self, tags: List[str], match_all: bool = True) -> List[Entity]:
        """Find entities that match the given tags.
        
        Args:
            tags: The tags to search for
            match_all: If True, entities must have all tags; if False, at least one
            
        Returns:
            List of matching entities
        """
        result_ids: Set[str] = set()
        
        if not tags:
            return []
        
        if match_all:
            # Initialize with the first tag's entities
            if tags[0] in self.tag_index:
                result_ids = set(self.tag_index[tags[0]])
            else:
                return []  # No entities with the first tag
                
            # Intersect with each subsequent tag
            for tag in tags[1:]:
                if tag not in self.tag_index:
                    return []  # No entities with this tag
                result_ids &= set(self.tag_index[tag])
        else:
            # Union of all tag's entities
            for tag in tags:
                if tag in self.tag_index:
                    result_ids |= set(self.tag_index[tag])
        
        # Retrieve all matching entities
        return [self.get_entity(entity_id) for entity_id in result_ids if entity_id]
    
    def find_by_type(self, entity_type: str) -> List[Entity]:
        """Find entities of a specific type.
        
        Args:
            entity_type: The entity type to search for
            
        Returns:
            List of matching entities
        """
        if entity_type not in self.type_index:
            return []
        
        return [self.get_entity(entity_id) for entity_id in self.type_index[entity_type] if entity_id]
    
    def find(self, query: str) -> List[Entity]:
        """Find entities matching a simple text query.
        
        Searches entity names, tags, and descriptions.
        
        Args:
            query: The text to search for
            
        Returns:
            List of matching entities
        """
        query_lower = query.lower()
        matching_entities: List[Entity] = []
        
        # Check all entities for matches
        for entity_id in self.list_entities():
            entity = self.get_entity(entity_id)
            if entity and (
                query_lower in entity.name.lower() or
                query_lower in entity.short_description.lower() or
                query_lower in entity.detailed_description.lower() or
                any(query_lower in tag.lower() for tag in entity.tags)
            ):
                matching_entities.append(entity)
        
        return matching_entities
    
    def clear_all(self) -> None:
        """Clear all entities and indexes from storage.
        
        This is a destructive operation and should be used with caution.
        """
        # Delete all entity files
        if self.entities_dir.exists():
            shutil.rmtree(self.entities_dir)
            self.entities_dir.mkdir(parents=True)
        
        # Clear indexes
        self.term_index = {}
        self.tag_index = {}
        self.type_index = {}
        
        # Save empty indexes
        self._save_indexes()
