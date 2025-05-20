# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps us create a map of all our knowledge, showing how different ideas
# are connected to each other. It's like a web that shows how everything is related.

# High School Explanation:
# This module implements the KnowledgeGraph class, which represents the complete
# network of entities and their relationships. It provides methods for adding,
# querying, and traversing knowledge in the form of a connected graph structure.

import os
import json
import logging
import uuid
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable
from pathlib import Path

from .entity import Entity
from .relationship import Relationship
from .storage import EntityStorage

logger = logging.getLogger(__name__)


class KnowledgeGraph:
    """
    Represents a knowledge graph composed of entities and relationships.
    
    The KnowledgeGraph provides a high-level interface for working with connected
    knowledge, including adding, querying, and traversing entities and their
    relationships.
    """
    
    def __init__(self, storage_path: str, auto_save: bool = True):
        """
        Initialize a knowledge graph.
        
        Args:
            storage_path: Path to the directory for storing knowledge graph data
            auto_save: Whether to automatically save changes to storage
        """
        self.storage = EntityStorage(storage_path)
        self.auto_save = auto_save
        self.graph = nx.DiGraph()
        self._load_graph()
    
    def _load_graph(self) -> None:
        """Load entities and relationships into the NetworkX graph."""
        # Clear existing graph
        self.graph.clear()
        
        # Add entities to graph
        try:
            entity_ids = self.storage.list_entities()
            for entity_id in entity_ids:
                try:
                    entity = self.storage.get_entity(entity_id)
                    if entity:
                        self.graph.add_node(entity.id, entity=entity)
                        
                        # Add relationships
                        for target_id, relation_type in entity.relationships.items():
                            self.graph.add_edge(
                                entity.id, 
                                target_id, 
                                type=relation_type
                            )
                except Exception as e:
                    logger.error(f"Error loading entity {entity_id}: {str(e)}")
                    # Continue loading other entities
        except Exception as e:
            logger.error(f"Error loading knowledge graph: {str(e)}")
            # Initialize an empty graph if we can't load the existing one
    
    def add_entity(self, entity: Entity) -> str:
        """
        Add an entity to the knowledge graph.
        
        Args:
            entity: The entity to add
            
        Returns:
            str: The entity ID
        """
        # Add to storage
        self.storage.save_entity(entity)
        
        # Add to graph
        self.graph.add_node(entity.id, entity=entity)
        
        return entity.id
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Retrieve an entity by its ID.
        
        Args:
            entity_id: The entity's unique identifier
            
        Returns:
            Optional[Entity]: The entity if found, None otherwise
        """
        return self.storage.get_entity(entity_id)
    
    def add_relationship(
        self, 
        source_id: str, 
        target_id: str, 
        relation_type: str, 
        description: str = "",
        weight: float = 1.0,
        bidirectional: bool = True
    ) -> str:
        """
        Add a relationship between two entities.
        
        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            relation_type: Type of relationship
            description: Optional description of the relationship
            weight: Strength or importance of the relationship (0.0 to 1.0)
            bidirectional: Whether to automatically add the inverse relationship
            
        Returns:
            str: The relationship ID
        """
        # Get entities to ensure they exist
        source_entity = self.get_entity(source_id)
        target_entity = self.get_entity(target_id)
        
        if not source_entity:
            raise ValueError(f"Source entity with ID {source_id} does not exist")
        if not target_entity:
            raise ValueError(f"Target entity with ID {target_id} does not exist")
        
        # Create and store relationship
        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            description=description,
            weight=weight
        )
        
        # Add to storage
        self.storage.save_relationship(relationship)
        
        # Update source entity's relationships
        source_entity.add_relationship(target_id, relation_type)
        self.storage.save_entity(source_entity)
        
        # Add to graph
        self.graph.add_edge(
            source_id, 
            target_id, 
            type=relation_type,
            weight=weight,
            relationship_id=relationship.id
        )
        
        # Add bidirectional relationship if requested
        if bidirectional:
            inverse_type = relationship.get_inverse_type()
            
            # Update target entity's relationships
            target_entity.add_relationship(source_id, inverse_type)
            self.storage.save_entity(target_entity)
            
            # Create the inverse relationship
            inverse_relationship = Relationship(
                source_id=target_id,
                target_id=source_id,
                relation_type=inverse_type,
                description=description,
                weight=weight
            )
            
            # Add to storage
            self.storage.save_relationship(inverse_relationship)
            
            # Add to graph
            self.graph.add_edge(
                target_id, 
                source_id, 
                type=inverse_type,
                weight=weight,
                relationship_id=inverse_relationship.id
            )
            
            return relationship.id
        
        return relationship.id
    
    def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity and all its relationships.
        
        Args:
            entity_id: The entity's unique identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        entity = self.get_entity(entity_id)
        if not entity:
            return False
        
        # Get all relationships involving this entity
        relationships = []
        for u, v, data in self.graph.edges(data=True):
            if u == entity_id or v == entity_id:
                relationships.append((u, v))
        
        # Remove from graph
        for u, v in relationships:
            self.graph.remove_edge(u, v)
        self.graph.remove_node(entity_id)
        
        # Remove from storage
        return self.storage.delete_entity(entity_id)
    
    def get_related_entities(
        self, 
        entity_id: str, 
        relation_type: Optional[str] = None,
        direction: str = "all",
        depth: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get entities related to the given entity.
        
        Args:
            entity_id: The entity's unique identifier
            relation_type: Type of relationship to filter by (optional)
            direction: Direction of relationships ('outgoing', 'incoming', or 'all')
            depth: How many steps to traverse (default is 1, direct connections only)
            
        Returns:
            List[Dict[str, Any]]: List of related entities with relationship info
        """
        if entity_id not in self.graph:
            return []
        
        related_entities = []
        
        # Get outgoing relationships
        if direction in ["outgoing", "all"]:
            for neighbor in self.graph.successors(entity_id):
                edge_data = self.graph.get_edge_data(entity_id, neighbor)
                if relation_type is None or edge_data.get("type") == relation_type:
                    target_entity = self.get_entity(neighbor)
                    if target_entity:
                        related_entities.append({
                            "entity": target_entity,
                            "relationship": edge_data.get("type"),
                            "direction": "outgoing"
                        })
        
        # Get incoming relationships
        if direction in ["incoming", "all"]:
            for neighbor in self.graph.predecessors(entity_id):
                edge_data = self.graph.get_edge_data(neighbor, entity_id)
                if relation_type is None or edge_data.get("type") == relation_type:
                    source_entity = self.get_entity(neighbor)
                    if source_entity:
                        related_entities.append({
                            "entity": source_entity,
                            "relationship": edge_data.get("type"),
                            "direction": "incoming"
                        })
        
        # If depth > 1, recursively get deeper relationships
        if depth > 1:
            deeper_entities = []
            for related in related_entities:
                deeper = self.get_related_entities(
                    related["entity"].id,
                    relation_type,
                    direction,
                    depth - 1
                )
                deeper_entities.extend(deeper)
            
            # Add deeper entities, avoiding duplicates
            existing_ids = {rel["entity"].id for rel in related_entities}
            for rel in deeper_entities:
                if rel["entity"].id not in existing_ids and rel["entity"].id != entity_id:
                    related_entities.append(rel)
                    existing_ids.add(rel["entity"].id)
        
        return related_entities
    
    def find_path(
        self, 
        source_id: str, 
        target_id: str, 
        max_depth: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find a path between two entities in the knowledge graph.
        
        Args:
            source_id: The starting entity ID
            target_id: The target entity ID
            max_depth: Maximum path length to consider
            
        Returns:
            List[Dict[str, Any]]: List of entities and relationships forming the path
        """
        if source_id not in self.graph or target_id not in self.graph:
            return []
        
        try:
            # Use NetworkX to find shortest path
            path_nodes = nx.shortest_path(
                self.graph, 
                source=source_id, 
                target=target_id, 
                weight=None,
                method="dijkstra"
            )
            
            if len(path_nodes) > max_depth + 1:
                return []  # Path is too long
            
            # Convert to entity and relationship list
            result = []
            for i in range(len(path_nodes) - 1):
                u, v = path_nodes[i], path_nodes[i+1]
                edge_data = self.graph.get_edge_data(u, v)
                
                source_entity = self.get_entity(u)
                target_entity = self.get_entity(v)
                
                if source_entity and target_entity:
                    result.append({
                        "source": source_entity,
                        "target": target_entity,
                        "relationship": edge_data.get("type")
                    })
            
            return result
        
        except nx.NetworkXNoPath:
            return []  # No path exists
    
    def find_entities(
        self,
        query: Optional[str] = None,
        entity_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        match_all_tags: bool = True
    ) -> List[Entity]:
        """
        Find entities matching the given criteria.
        
        Args:
            query: Text to search for in name, description (optional)
            entity_type: Entity type to filter by (optional)
            tags: Tags to filter by (optional)
            match_all_tags: Whether all tags must match (True) or any (False)
            
        Returns:
            List[Entity]: List of matching entities
        """
        # First, filter by entity type if provided
        if entity_type:
            entities = self.storage.find_by_type(entity_type)
        else:
            entity_ids = self.storage.list_entities()
            entities = [self.get_entity(eid) for eid in entity_ids]
            entities = [e for e in entities if e is not None]
        
        # Filter by tags if provided
        if tags and entities:
            if match_all_tags:
                entities = [
                    entity for entity in entities
                    if all(tag in entity.tags for tag in tags)
                ]
            else:
                entities = [
                    entity for entity in entities
                    if any(tag in entity.tags for tag in tags)
                ]
        
        # Filter by query if provided
        if query and entities:
            query = query.lower()
            entities = [
                entity for entity in entities
                if (query in entity.name.lower() or
                    query in entity.short_description.lower() or
                    query in entity.detailed_description.lower())
            ]
        
        return entities
    
    def find_by_relationship(
        self,
        source_entity: Optional[str] = None,
        relation_type: Optional[str] = None,
        target_entity: Optional[str] = None
    ) -> List[Tuple[Entity, str, Entity]]:
        """
        Find relationships matching the given criteria.
        
        Args:
            source_entity: Source entity ID or None to match any
            relation_type: Relationship type or None to match any
            target_entity: Target entity ID or None to match any
            
        Returns:
            List[Tuple[Entity, str, Entity]]: List of (source, relation, target) tuples
        """
        results = []
        
        # Filter edges based on criteria
        for u, v, data in self.graph.edges(data=True):
            if (source_entity is None or u == source_entity) and \
               (target_entity is None or v == target_entity) and \
               (relation_type is None or data.get("type") == relation_type):
                
                source = self.get_entity(u)
                target = self.get_entity(v)
                
                if source and target:
                    results.append((source, data.get("type"), target))
        
        return results
    
    def save(self) -> None:
        """Force save the knowledge graph to storage."""
        pass  # Storage is updated incrementally, no need for a full save
    
    def visualize(
        self,
        entity_ids: Optional[List[str]] = None,
        output_path: Optional[str] = None,
        max_nodes: int = 50
    ) -> None:
        """
        Create a visualization of the knowledge graph.
        
        Args:
            entity_ids: List of entity IDs to include (optional)
            output_path: Path to save the visualization (optional)
            max_nodes: Maximum number of nodes to include
        """
        if not entity_ids:
            # If no specific entities, use a subset of the graph
            entity_ids = list(self.graph.nodes())[:max_nodes]
        
        # Create a subgraph with only the specified entities
        subgraph = self.graph.subgraph(entity_ids)
        
        # Create labels with entity names
        labels = {}
        for node in subgraph.nodes():
            entity = self.get_entity(node)
            if entity:
                labels[node] = entity.name
        
        # Create edge labels with relationship types
        edge_labels = {}
        for u, v, data in subgraph.edges(data=True):
            edge_labels[(u, v)] = data.get("type", "")
        
        # Create colors based on entity types
        node_colors = []
        for node in subgraph.nodes():
            entity = self.get_entity(node)
            if entity:
                # Generate a hash-based color from entity type
                hashed = hash(entity.entity_type) % 20
                node_colors.append(f"C{hashed}")
            else:
                node_colors.append("gray")
        
        # Create the plot
        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(subgraph, seed=42)
        
        # Draw nodes and edges
        nx.draw_networkx_nodes(subgraph, pos, node_color=node_colors, node_size=800, alpha=0.8)
        nx.draw_networkx_edges(subgraph, pos, width=1.5, alpha=0.7, edge_color="gray")
        
        # Draw labels
        nx.draw_networkx_labels(subgraph, pos, labels, font_size=10, font_weight="bold")
        nx.draw_networkx_edge_labels(subgraph, pos, edge_labels=edge_labels, font_size=8)
        
        plt.title("Knowledge Graph Visualization")
        plt.axis("off")
        
        # Save or show
        if output_path:
            plt.savefig(output_path, bbox_inches="tight")
            print(f"Visualization saved to {output_path}")
        else:
            plt.show()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph.
        
        Returns:
            Dict[str, Any]: Statistics about the knowledge graph
        """
        entity_count = len(self.graph.nodes())
        relationship_count = len(self.graph.edges())
        
        entity_types = {}
        for node in self.graph.nodes():
            entity = self.get_entity(node)
            if entity:
                if entity.entity_type not in entity_types:
                    entity_types[entity.entity_type] = 0
                entity_types[entity.entity_type] += 1
        
        relationship_types = {}
        for _, _, data in self.graph.edges(data=True):
            rel_type = data.get("type")
            if rel_type:
                if rel_type not in relationship_types:
                    relationship_types[rel_type] = 0
                relationship_types[rel_type] += 1
        
        return {
            "entity_count": entity_count,
            "relationship_count": relationship_count,
            "entity_types": entity_types,
            "relationship_types": relationship_types,
        }