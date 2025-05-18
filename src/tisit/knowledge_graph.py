# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file is like a big web of connections between all the things we know. It helps us
# organize ideas, see how they're related, and find information quickly when we need it.

# High School Explanation:
# This module implements the KnowledgeGraph class, which serves as the central component
# of the TISIT second brain. It provides a graph-based representation of knowledge entities
# and their relationships, with methods for querying, traversing, and analyzing the
# knowledge structure.

import os
from typing import Dict, List, Optional, Set, Tuple, Any, Iterator
from pathlib import Path
import json
import uuid
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict, deque

from .entity import Entity
from .relationship import Relationship
from .storage import EntityStorage

class KnowledgeGraph:
    """Central knowledge graph implementation for TISIT.
    
    The knowledge graph connects entities through typed relationships, enabling
    knowledge navigation, discovery, and contextual retrieval. It provides methods
    for adding, removing, and querying entities and relationships.
    """
    
    def __init__(self, storage_root: str) -> None:
        """Initialize the knowledge graph.
        
        Args:
            storage_root: Root directory for storing the knowledge graph data
        """
        self.storage_root = Path(storage_root)
        self.entity_storage = EntityStorage(str(self.storage_root / "entities"))
        self.relationships_dir = self.storage_root / "relationships"
        self.relationships_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory graph representation (using networkx for efficiency)
        self.graph = nx.DiGraph()
        
        # Load existing data
        self._load_graph()
    
    def _load_graph(self) -> None:
        """Load the knowledge graph from storage."""
        # Load entities
        for entity_id in self.entity_storage.list_entities():
            entity = self.entity_storage.get_entity(entity_id)
            if entity:
                self.graph.add_node(entity.id, entity=entity)
        
        # Load relationships
        relationship_files = list(self.relationships_dir.glob("*.json"))
        for rel_file in relationship_files:
            with open(rel_file, 'r') as f:
                rel_json = f.read()
                rel = Relationship.from_json(rel_json)
                
                # Add an edge for the relationship if both nodes exist
                if self.graph.has_node(rel.source_id) and self.graph.has_node(rel.target_id):
                    self.graph.add_edge(
                        rel.source_id,
                        rel.target_id,
                        id=rel.id,
                        type=rel.type,
                        properties=rel.properties,
                        description=rel.description,
                        bidirectional=rel.bidirectional
                    )
                    
                    # Add reverse edge if bidirectional
                    if rel.bidirectional:
                        inverse_type = rel.get_inverse_type() or rel.type
                        self.graph.add_edge(
                            rel.target_id,
                            rel.source_id,
                            id=f"{rel.id}_inverse",
                            type=inverse_type,
                            properties=rel.properties,
                            description=rel.description,
                            bidirectional=True
                        )
    
    def _get_relationship_path(self, relationship_id: str) -> Path:
        """Get the file path for a relationship.
        
        Args:
            relationship_id: The unique identifier of the relationship
            
        Returns:
            Path object for the relationship file
        """
        return self.relationships_dir / f"{relationship_id}.json"
    
    def add_entity(self, entity: Entity) -> str:
        """Add an entity to the knowledge graph.
        
        Args:
            entity: The entity to add
            
        Returns:
            The ID of the added entity
        """
        # Save the entity to storage
        self.entity_storage.save_entity(entity)
        
        # Add to in-memory graph
        self.graph.add_node(entity.id, entity=entity)
        
        return entity.id
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by its ID.
        
        Args:
            entity_id: The ID of the entity to retrieve
            
        Returns:
            The entity if found, None otherwise
        """
        return self.entity_storage.get_entity(entity_id)
    
    def update_entity(self, entity: Entity) -> bool:
        """Update an existing entity.
        
        Args:
            entity: The updated entity
            
        Returns:
            True if the entity was updated, False if it doesn't exist
        """
        if not self.graph.has_node(entity.id):
            return False
        
        # Save to storage
        self.entity_storage.save_entity(entity)
        
        # Update in-memory graph
        self.graph.nodes[entity.id]['entity'] = entity
        
        return True
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity and all its relationships.
        
        Args:
            entity_id: The ID of the entity to delete
            
        Returns:
            True if the entity was deleted, False if it doesn't exist
        """
        if not self.graph.has_node(entity_id):
            return False
        
        # Get all relationships involving this entity
        relationships_to_delete = []
        
        # Outgoing relationships
        for _, target_id, data in self.graph.out_edges(entity_id, data=True):
            if 'id' in data:
                relationships_to_delete.append(data['id'])
        
        # Incoming relationships
        for source_id, _, data in self.graph.in_edges(entity_id, data=True):
            if 'id' in data:
                relationships_to_delete.append(data['id'])
        
        # Delete all relationships
        for rel_id in relationships_to_delete:
            # Skip inverse relationships as they'll be handled with their primary relationship
            if not rel_id.endswith('_inverse'):
                self.delete_relationship(rel_id)
        
        # Delete from storage
        self.entity_storage.delete_entity(entity_id)
        
        # Remove from in-memory graph
        self.graph.remove_node(entity_id)
        
        return True
    
    def add_relationship(self, 
                        source_id: str, 
                        target_id: str, 
                        relation_type: str,
                        description: Optional[str] = None,
                        properties: Optional[Dict[str, Any]] = None,
                        bidirectional: bool = False) -> Optional[str]:
        """Add a relationship between two entities.
        
        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            relation_type: Type of relationship
            description: Optional description of the relationship
            properties: Additional properties for the relationship
            bidirectional: Whether the relationship applies in both directions
            
        Returns:
            The ID of the created relationship, or None if the entities don't exist
        """
        # Verify both entities exist
        if not (self.graph.has_node(source_id) and self.graph.has_node(target_id)):
            return None
        
        # Create the relationship
        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            description=description,
            properties=properties,
            bidirectional=bidirectional
        )
        
        # Save to file
        relationship_path = self._get_relationship_path(relationship.id)
        with open(relationship_path, 'w') as f:
            f.write(relationship.to_json())
        
        # Add to in-memory graph
        self.graph.add_edge(
            source_id,
            target_id,
            id=relationship.id,
            type=relation_type,
            properties=properties or {},
            description=description or "",
            bidirectional=bidirectional
        )
        
        # Add reverse edge if bidirectional
        if bidirectional:
            inverse_type = relationship.get_inverse_type() or relation_type
            self.graph.add_edge(
                target_id,
                source_id,
                id=f"{relationship.id}_inverse",
                type=inverse_type,
                properties=properties or {},
                description=description or "",
                bidirectional=True
            )
        
        return relationship.id
    
    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """Get a relationship by its ID.
        
        Args:
            relationship_id: The ID of the relationship to retrieve
            
        Returns:
            The relationship if found, None otherwise
        """
        # Skip inverse relationships as they don't have actual files
        if relationship_id.endswith('_inverse'):
            primary_id = relationship_id[:-8]  # Remove "_inverse"
            relationship_path = self._get_relationship_path(primary_id)
            
            if not relationship_path.exists():
                return None
                
            with open(relationship_path, 'r') as f:
                rel_json = f.read()
                rel = Relationship.from_json(rel_json)
                
                # Create a reversed version
                inverse_type = rel.get_inverse_type() or rel.type
                return Relationship(
                    source_id=rel.target_id,
                    target_id=rel.source_id,
                    relation_type=inverse_type,
                    description=rel.description,
                    relationship_id=relationship_id,
                    properties=rel.properties,
                    bidirectional=rel.bidirectional,
                    created_at=rel.created_at,
                    last_updated=rel.last_updated
                )
        
        # Normal relationships
        relationship_path = self._get_relationship_path(relationship_id)
        
        if not relationship_path.exists():
            return None
            
        with open(relationship_path, 'r') as f:
            rel_json = f.read()
            return Relationship.from_json(rel_json)
    
    def update_relationship(self, relationship: Relationship) -> bool:
        """Update an existing relationship.
        
        Args:
            relationship: The updated relationship
            
        Returns:
            True if the relationship was updated, False if it doesn't exist
        """
        # We don't update inverse relationships directly
        if relationship.id.endswith('_inverse'):
            return False
            
        relationship_path = self._get_relationship_path(relationship.id)
        
        if not relationship_path.exists():
            return False
            
        # Get existing relationship to check for bidirectionality changes
        with open(relationship_path, 'r') as f:
            old_rel_json = f.read()
            old_rel = Relationship.from_json(old_rel_json)
        
        # Update file
        with open(relationship_path, 'w') as f:
            f.write(relationship.to_json())
        
        # Update in-memory graph
        if self.graph.has_edge(relationship.source_id, relationship.target_id):
            # Update the edge attributes
            self.graph[relationship.source_id][relationship.target_id].update({
                'type': relationship.type,
                'properties': relationship.properties,
                'description': relationship.description,
                'bidirectional': relationship.bidirectional
            })
            
            # Handle bidirectionality changes
            if old_rel.bidirectional and not relationship.bidirectional:
                # Remove inverse edge
                if self.graph.has_edge(relationship.target_id, relationship.source_id):
                    inverse_id = self.graph[relationship.target_id][relationship.source_id].get('id')
                    if inverse_id and inverse_id.endswith('_inverse'):
                        self.graph.remove_edge(relationship.target_id, relationship.source_id)
            
            elif not old_rel.bidirectional and relationship.bidirectional:
                # Add inverse edge
                inverse_type = relationship.get_inverse_type() or relationship.type
                self.graph.add_edge(
                    relationship.target_id,
                    relationship.source_id,
                    id=f"{relationship.id}_inverse",
                    type=inverse_type,
                    properties=relationship.properties,
                    description=relationship.description,
                    bidirectional=True
                )
            
            elif relationship.bidirectional:
                # Update existing inverse edge
                if self.graph.has_edge(relationship.target_id, relationship.source_id):
                    inverse_type = relationship.get_inverse_type() or relationship.type
                    self.graph[relationship.target_id][relationship.source_id].update({
                        'type': inverse_type,
                        'properties': relationship.properties,
                        'description': relationship.description,
                        'bidirectional': True
                    })
        
        return True
    
    def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship.
        
        Args:
            relationship_id: The ID of the relationship to delete
            
        Returns:
            True if the relationship was deleted, False if it doesn't exist
        """
        # We don't delete inverse relationships directly
        if relationship_id.endswith('_inverse'):
            return False
            
        relationship_path = self._get_relationship_path(relationship_id)
        
        if not relationship_path.exists():
            return False
            
        # Get the relationship for source/target info
        with open(relationship_path, 'r') as f:
            rel_json = f.read()
            rel = Relationship.from_json(rel_json)
        
        # Remove from in-memory graph
        if self.graph.has_edge(rel.source_id, rel.target_id):
            self.graph.remove_edge(rel.source_id, rel.target_id)
            
        # Remove inverse edge if it exists
        if rel.bidirectional and self.graph.has_edge(rel.target_id, rel.source_id):
            self.graph.remove_edge(rel.target_id, rel.source_id)
        
        # Delete the file
        relationship_path.unlink()
        
        return True
    
    def get_entity_relationships(self, entity_id: str, direction: str = 'both') -> List[Relationship]:
        """Get all relationships involving an entity.
        
        Args:
            entity_id: The ID of the entity
            direction: 'outgoing', 'incoming', or 'both'
            
        Returns:
            List of relationships
        """
        if not self.graph.has_node(entity_id):
            return []
            
        relationships = []
        
        # Outgoing relationships
        if direction in ['outgoing', 'both']:
            for _, target_id, data in self.graph.out_edges(entity_id, data=True):
                rel_id = data.get('id')
                if rel_id and not rel_id.endswith('_inverse'):
                    rel = self.get_relationship(rel_id)
                    if rel:
                        relationships.append(rel)
        
        # Incoming relationships
        if direction in ['incoming', 'both']:
            for source_id, _, data in self.graph.in_edges(entity_id, data=True):
                rel_id = data.get('id')
                if rel_id and not rel_id.endswith('_inverse'):
                    rel = self.get_relationship(rel_id)
                    if rel:
                        relationships.append(rel)
        
        return relationships
    
    def find_connections(self, source_id: str, target_id: str, max_depth: int = 3) -> List[List[Tuple[str, str, str]]]:
        """Find connection paths between two entities.
        
        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            max_depth: Maximum path length to search
            
        Returns:
            List of paths, where each path is a list of (source_id, relation_type, target_id) tuples
        """
        if not (self.graph.has_node(source_id) and self.graph.has_node(target_id)):
            return []
            
        if source_id == target_id:
            return [[]]
            
        # Use networkx to find all simple paths
        paths = []
        for path in nx.all_simple_paths(self.graph, source_id, target_id, cutoff=max_depth):
            edge_path = []
            for i in range(len(path) - 1):
                from_id, to_id = path[i], path[i+1]
                rel_type = self.graph[from_id][to_id]['type']
                edge_path.append((from_id, rel_type, to_id))
            paths.append(edge_path)
            
        return paths
    
    def get_related_entities(self, entity_id: str, relation_types: Optional[List[str]] = None, 
                            max_depth: int = 1) -> Dict[str, List[Entity]]:
        """Get entities related to the given entity.
        
        Args:
            entity_id: The ID of the entity
            relation_types: Optional list of relationship types to filter by
            max_depth: Maximum depth to search for related entities
            
        Returns:
            Dictionary mapping relationship types to lists of related entities
        """
        if not self.graph.has_node(entity_id):
            return {}
            
        related = defaultdict(list)
        
        # BFS to find all related entities up to max_depth
        visited = {entity_id}
        queue = deque([(entity_id, 0)])  # (node_id, depth)
        
        while queue:
            node_id, depth = queue.popleft()
            
            if depth >= max_depth:
                continue
                
            # Process outgoing edges
            for _, target_id, data in self.graph.out_edges(node_id, data=True):
                rel_type = data.get('type', '')
                
                # Skip if not a requested relation type
                if relation_types and rel_type not in relation_types:
                    continue
                    
                # Add the target entity to results
                target_entity = self.get_entity(target_id)
                if target_entity and target_id not in visited:
                    related[rel_type].append(target_entity)
                    visited.add(target_id)
                    queue.append((target_id, depth + 1))
                    
            # Process incoming edges
            for source_id, _, data in self.graph.in_edges(node_id, data=True):
                rel_type = data.get('type', '')
                
                # Skip if not a requested relation type
                if relation_types and rel_type not in relation_types:
                    continue
                    
                # Add the source entity to results
                source_entity = self.get_entity(source_id)
                if source_entity and source_id not in visited:
                    related[rel_type].append(source_entity)
                    visited.add(source_id)
                    queue.append((source_id, depth + 1))
                    
        return related
    
    def find_entities(self, query: str) -> List[Entity]:
        """Find entities matching a text query.
        
        Args:
            query: The search text
            
        Returns:
            List of matching entities
        """
        return self.entity_storage.find(query)
    
    def find_entities_by_type(self, entity_type: str) -> List[Entity]:
        """Find entities of a specific type.
        
        Args:
            entity_type: The entity type to find
            
        Returns:
            List of matching entities
        """
        return self.entity_storage.find_by_type(entity_type)
    
    def find_entities_by_tags(self, tags: List[str], match_all: bool = True) -> List[Entity]:
        """Find entities with specific tags.
        
        Args:
            tags: The tags to search for
            match_all: If True, entities must have all tags; if False, at least one
            
        Returns:
            List of matching entities
        """
        return self.entity_storage.find_by_tags(tags, match_all)
    
    def export_to_visualization(self, output_file: str, entity_ids: Optional[List[str]] = None,
                               include_labels: bool = True, layout: str = 'spring') -> None:
        """Export the knowledge graph to a visualization file.
        
        Args:
            output_file: Path to save the visualization (PNG, PDF, SVG, etc.)
            entity_ids: Optional list of entity IDs to include (if None, include all)
            include_labels: Whether to include node and edge labels
            layout: The layout algorithm to use ('spring', 'circular', 'random', etc.)
        """
        if entity_ids:
            # Create a subgraph with the specified entities
            subgraph = self.graph.subgraph(entity_ids)
        else:
            subgraph = self.graph
        
        plt.figure(figsize=(12, 10))
        
        # Choose the layout algorithm
        if layout == 'spring':
            pos = nx.spring_layout(subgraph)
        elif layout == 'circular':
            pos = nx.circular_layout(subgraph)
        elif layout == 'random':
            pos = nx.random_layout(subgraph)
        else:
            pos = nx.spring_layout(subgraph)  # Default to spring layout
        
        # Draw nodes
        nx.draw_networkx_nodes(subgraph, pos, node_size=700, node_color='skyblue')
        
        # Draw edges
        nx.draw_networkx_edges(subgraph, pos, width=2, arrowsize=20)
        
        if include_labels:
            # Draw node labels
            node_labels = {}
            for node_id in subgraph.nodes():
                entity = self.get_entity(node_id)
                if entity:
                    node_labels[node_id] = entity.name
                else:
                    node_labels[node_id] = node_id
            nx.draw_networkx_labels(subgraph, pos, labels=node_labels, font_size=12)
            
            # Draw edge labels
            edge_labels = {}
            for source, target, data in subgraph.edges(data=True):
                edge_labels[(source, target)] = data.get('type', '')
            nx.draw_networkx_edge_labels(subgraph, pos, edge_labels=edge_labels, font_size=10)
        
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_file)
        plt.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph.
        
        Returns:
            Dictionary of graph statistics
        """
        # Basic graph statistics
        num_entities = self.graph.number_of_nodes()
        num_relationships = sum(1 for edge in self.graph.edges() if not str(self.graph.edges[edge].get('id', '')).endswith('_inverse'))
        
        # Entity type distribution
        type_counts = defaultdict(int)
        for node_id in self.graph.nodes():
            entity = self.get_entity(node_id)
            if entity:
                type_counts[entity.type] += 1
        
        # Relationship type distribution
        rel_type_counts = defaultdict(int)
        for _, _, data in self.graph.edges(data=True):
            rel_id = data.get('id', '')
            if not rel_id.endswith('_inverse'):
                rel_type = data.get('type', 'unknown')
                rel_type_counts[rel_type] += 1
        
        # Most connected entities
        degree_centrality = nx.degree_centrality(self.graph)
        top_entities = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        top_entities_info = []
        for entity_id, centrality in top_entities:
            entity = self.get_entity(entity_id)
            if entity:
                top_entities_info.append({
                    'id': entity_id,
                    'name': entity.name,
                    'type': entity.type,
                    'centrality': centrality,
                    'connections': self.graph.degree(entity_id)
                })
        
        return {
            'num_entities': num_entities,
            'num_relationships': num_relationships,
            'entity_types': dict(type_counts),
            'relationship_types': dict(rel_type_counts),
            'top_connected_entities': top_entities_info,
            'density': nx.density(self.graph),
            'is_connected': nx.is_strongly_connected(self.graph) if num_entities > 0 else True,
            'avg_clustering': nx.average_clustering(self.graph.to_undirected()) if num_entities > 0 else 0,
            'diameter': nx.diameter(self.graph) if nx.is_strongly_connected(self.graph) and num_entities > 0 else float('inf')
        }
    
    def clear(self) -> None:
        """Clear the entire knowledge graph.
        
        This is a destructive operation and should be used with caution.
        """
        # Clear entity storage
        self.entity_storage.clear_all()
        
        # Clear relationships
        for rel_file in self.relationships_dir.glob("*.json"):
            rel_file.unlink()
        
        # Reset in-memory graph
        self.graph = nx.DiGraph()