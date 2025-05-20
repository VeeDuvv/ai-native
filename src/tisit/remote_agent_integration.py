# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps our AI helpers talk to our knowledge brain even when it's
# running on a different computer. It's like using a telephone to talk to a friend
# who lives far away.

# High School Explanation:
# This module provides a remote integration interface for agents to interact with
# the TISIT knowledge graph via its REST API. It implements the same interface as
# the direct integration, but communicates over HTTP instead of directly.

import json
import logging
from typing import Dict, List, Optional, Any, Union

from .api_client import TisitApiClient

logger = logging.getLogger(__name__)


class RemoteTisitAgentInterface:
    """
    Provides a remote interface for agents to interact with the TISIT knowledge graph.
    
    This class implements the same interface as TisitAgentInterface, but communicates
    with the knowledge graph via its REST API instead of directly. This allows agents
    to access the knowledge graph even when it's running in a different process or
    on a different machine.
    """
    
    def __init__(self, api_url: str, agent_name: str):
        """
        Initialize the remote TISIT agent interface.
        
        Args:
            api_url: URL of the TISIT API
            agent_name: Name of the agent using this interface (for tracking contributions)
        """
        self.api_client = TisitApiClient(base_url=api_url)
        self.agent_name = agent_name
    
    def store_entity(
        self, 
        name: str,
        entity_type: str,
        short_description: str,
        detailed_description: str = "",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a new entity in the knowledge graph.
        
        Args:
            name: Name of the entity
            entity_type: Type of entity (must be one of Entity.VALID_TYPES)
            short_description: Brief description of the entity
            detailed_description: Detailed explanation of the entity
            tags: List of tags for categorization
            metadata: Additional metadata as key-value pairs
            
        Returns:
            str: ID of the created entity
        """
        # Prepare entity data
        entity_data = {
            "name": name,
            "entity_type": entity_type,
            "short_description": short_description,
            "detailed_description": detailed_description,
            "tags": tags or [],
            "created_by": self.agent_name,
            "metadata": metadata or {}
        }
        
        # Add creation metadata
        if "created_by_agent" not in entity_data["metadata"]:
            entity_data["metadata"]["created_by_agent"] = self.agent_name
        
        # Create entity via API
        response = self.api_client.create_entity(entity_data)
        
        return response["id"]
    
    def connect_entities(
        self,
        source_name: str,
        target_name: str,
        relation_type: str,
        description: str = "",
    ) -> Optional[str]:
        """
        Create a relationship between two entities by their names.
        
        This is a convenience method for agents to connect entities without
        needing to know their IDs.
        
        Args:
            source_name: Name of the source entity
            target_name: Name of the target entity
            relation_type: Type of relationship
            description: Description of the relationship
            
        Returns:
            Optional[str]: ID of the created relationship, or None if entities not found
        """
        # Search for source entity
        source_results = self.api_client.search_entities(query=source_name)
        source_entities = source_results.get("entities", [])
        
        # Search for target entity
        target_results = self.api_client.search_entities(query=target_name)
        target_entities = target_results.get("entities", [])
        
        # Find exact name matches
        source_entity = next((e for e in source_entities if e["name"].lower() == source_name.lower()), None)
        target_entity = next((e for e in target_entities if e["name"].lower() == target_name.lower()), None)
        
        if not source_entity or not target_entity:
            logger.warning(f"Could not connect entities: {source_name} or {target_name} not found")
            return None
        
        # Create relationship
        relationship_data = {
            "source_id": source_entity["id"],
            "target_id": target_entity["id"],
            "relation_type": relation_type,
            "description": description,
            "bidirectional": True
        }
        
        response = self.api_client.create_relationship(relationship_data)
        
        return response.get("id")
    
    def get_knowledge_context(
        self,
        query: str,
        entity_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Get relevant knowledge context for a given query.
        
        This method helps agents find relevant knowledge when making decisions
        or generating content.
        
        Args:
            query: The query text to match against knowledge
            entity_types: Optional list of entity types to filter results
            tags: Optional list of tags to filter results
            max_results: Maximum number of results to return
            
        Returns:
            Dict[str, Any]: Structured knowledge context with entities and relationships
        """
        # First, search for entities matching the query
        search_results = self.api_client.search_entities(
            query=query,
            entity_type=entity_types[0] if entity_types else None,
            tags=tags
        )
        
        entities = search_results.get("entities", [])[:max_results]
        
        if not entities:
            # If no direct matches, try broader search with individual terms
            query_parts = query.split()
            for part in query_parts:
                if len(part) > 3:  # Only search for meaningful words
                    part_results = self.api_client.search_entities(query=part)
                    entities.extend(part_results.get("entities", []))
                    if len(entities) >= max_results:
                        entities = entities[:max_results]
                        break
        
        # If still no results, return empty context
        if not entities:
            return {
                "query": query,
                "entities": [],
                "relationships": []
            }
        
        # Get related entities and relationships
        result = {
            "query": query,
            "entities": [],
            "relationships": []
        }
        
        # Track IDs to avoid duplicates
        entity_ids = set()
        
        for entity in entities:
            # Add entity if not already included
            if entity["id"] not in entity_ids:
                result["entities"].append({
                    "id": entity["id"],
                    "name": entity["name"],
                    "type": entity["entity_type"],
                    "description": entity["short_description"],
                    "tags": entity["tags"]
                })
                entity_ids.add(entity["id"])
            
                # Get related entities
                related = self.api_client.get_related_entities(entity["id"])
                
                # Add relationships and related entities
                for rel in related:
                    related_entity = rel["entity"]
                    
                    # Add relationship
                    result["relationships"].append({
                        "source": entity["name"],
                        "source_id": entity["id"],
                        "target": related_entity["name"],
                        "target_id": related_entity["id"],
                        "type": rel["relationship"],
                        "direction": rel["direction"]
                    })
                    
                    # Add related entity if not already included
                    if related_entity["id"] not in entity_ids:
                        result["entities"].append({
                            "id": related_entity["id"],
                            "name": related_entity["name"],
                            "type": related_entity["entity_type"],
                            "description": related_entity["short_description"],
                            "tags": related_entity["tags"]
                        })
                        entity_ids.add(related_entity["id"])
        
        return result
    
    def store_campaign_knowledge(self, campaign_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Store knowledge about a campaign in the knowledge graph.
        
        Args:
            campaign_data: Dictionary containing campaign information
            
        Returns:
            Dict[str, str]: Dictionary mapping entity names to their IDs
        """
        return self.api_client.store_campaign_knowledge(campaign_data)
    
    def capture_creative_knowledge(self, creative_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Store knowledge about creative assets in the knowledge graph.
        
        Args:
            creative_data: Dictionary containing creative information
            
        Returns:
            Dict[str, str]: Dictionary mapping entity names to their IDs
        """
        return self.api_client.store_creative_knowledge(creative_data)
    
    def capture_media_knowledge(self, media_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Store knowledge about media planning in the knowledge graph.
        
        Args:
            media_data: Dictionary containing media planning information
            
        Returns:
            Dict[str, str]: Dictionary mapping entity names to their IDs
        """
        return self.api_client.store_media_knowledge(media_data)
    
    def capture_analytics_knowledge(self, analytics_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Store analytics insights in the knowledge graph.
        
        Args:
            analytics_data: Dictionary containing analytics information
            
        Returns:
            Dict[str, str]: Dictionary mapping entity names to their IDs
        """
        return self.api_client.store_analytics_knowledge(analytics_data)
    
    def retrieve_campaign_knowledge(self, campaign_name: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive knowledge about a campaign.
        
        Args:
            campaign_name: Name of the campaign
            
        Returns:
            Dict[str, Any]: Comprehensive campaign knowledge
        """
        return self.api_client.retrieve_campaign_knowledge(campaign_name)
    
    def close(self):
        """Close the API client connection."""
        self.api_client.close()


class RemoteKnowledgeEnhancedAgent:
    """
    Base class for agents that interact with a remote TISIT knowledge graph.
    
    This class provides common methods for agents to store and retrieve knowledge
    from a TISIT knowledge graph over a network connection.
    """
    
    def __init__(self, name: str, api_url: str, description: str = ""):
        """
        Initialize a remote knowledge-enhanced agent.
        
        Args:
            name: Name of the agent
            api_url: URL of the TISIT API
            description: Optional description of the agent
        """
        self.name = name
        self.description = description
        self.knowledge_interface = RemoteTisitAgentInterface(api_url, name)
    
    def remember(self, entity_name: str, entity_type: str, description: str, 
                 details: str = "", tags: List[str] = None) -> str:
        """
        Store information in the knowledge graph.
        
        Args:
            entity_name: Name of the entity to store
            entity_type: Type of entity (concept, strategy, etc.)
            description: Short description of the entity
            details: Detailed description
            tags: List of tags for categorization
            
        Returns:
            str: ID of the created entity
        """
        return self.knowledge_interface.store_entity(
            name=entity_name,
            entity_type=entity_type,
            short_description=description,
            detailed_description=details,
            tags=tags or []
        )
    
    def connect(self, source_name: str, target_name: str, relationship: str, 
                description: str = "") -> Optional[str]:
        """
        Create a relationship between two knowledge entities.
        
        Args:
            source_name: Name of the source entity
            target_name: Name of the target entity
            relationship: Type of relationship
            description: Description of the relationship
            
        Returns:
            Optional[str]: ID of the created relationship, or None if entities not found
        """
        return self.knowledge_interface.connect_entities(
            source_name=source_name,
            target_name=target_name,
            relation_type=relationship,
            description=description
        )
    
    def recall(self, query: str, entity_types: List[str] = None, 
               tags: List[str] = None) -> Dict[str, Any]:
        """
        Retrieve relevant knowledge based on a query.
        
        Args:
            query: The query text to search for
            entity_types: Optional types of entities to search for
            tags: Optional tags to filter by
            
        Returns:
            Dict[str, Any]: Knowledge context with entities and relationships
        """
        return self.knowledge_interface.get_knowledge_context(
            query=query,
            entity_types=entity_types,
            tags=tags
        )
    
    def enhance_message_with_knowledge(self, message: str, context_query: str) -> str:
        """
        Enhance a message with relevant knowledge from TISIT.
        
        Args:
            message: The original message
            context_query: Query to find relevant knowledge
            
        Returns:
            str: Enhanced message with knowledge context
        """
        # Get relevant knowledge
        knowledge = self.recall(context_query)
        
        if not knowledge.get("entities"):
            return message  # No relevant knowledge found
        
        # Build knowledge context section
        knowledge_section = "\n\nRelevant Knowledge Context:\n"
        
        for entity in knowledge.get("entities", [])[:3]:  # Limit to 3 entities
            knowledge_section += f"- {entity['name']} ({entity['type']}): {entity['description']}\n"
        
        # Add relationships
        if knowledge.get("relationships"):
            knowledge_section += "\nRelationships:\n"
            for rel in knowledge.get("relationships", [])[:5]:  # Limit to 5 relationships
                knowledge_section += f"- {rel['source']} {rel['type']} {rel['target']}\n"
        
        # Combine original message with knowledge context
        enhanced_message = message + knowledge_section
        return enhanced_message