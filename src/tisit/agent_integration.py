# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps our AI agents use the knowledge brain. It's like giving them
# a library card so they can look up information and add new things they learn.

# High School Explanation:
# This module provides integration between the agent framework and the TISIT
# knowledge graph system. It offers specialized interfaces for agents to query,
# contribute to, and leverage the collective knowledge stored in TISIT.

import json
import logging
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from pathlib import Path
import datetime

from .entity import Entity
from .relationship import Relationship
from .knowledge_graph import KnowledgeGraph

logger = logging.getLogger(__name__)


class TisitAgentInterface:
    """
    Provides a standardized interface for agents to interact with the TISIT knowledge graph.
    
    This class acts as an adapter between the agent framework and the knowledge graph,
    offering simplified methods for common knowledge operations that agents need to perform.
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph, agent_name: str):
        """
        Initialize the TISIT agent interface.
        
        Args:
            knowledge_graph: The knowledge graph to interact with
            agent_name: Name of the agent using this interface (for tracking contributions)
        """
        self.knowledge_graph = knowledge_graph
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
        entity = Entity(
            name=name,
            entity_type=entity_type,
            short_description=short_description,
            detailed_description=detailed_description,
            tags=tags or [],
            created_by=self.agent_name,
            metadata=metadata or {}
        )
        
        # Add creation timestamp and agent info
        entity.add_metadata("created_timestamp", datetime.datetime.now().isoformat())
        entity.add_metadata("created_by_agent", self.agent_name)
        
        return self.knowledge_graph.add_entity(entity)
    
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
        # Find entities by name
        source_entities = self.knowledge_graph.find_entities(query=source_name)
        target_entities = self.knowledge_graph.find_entities(query=target_name)
        
        # Filter for exact name matches
        source_entity = next((e for e in source_entities if e.name.lower() == source_name.lower()), None)
        target_entity = next((e for e in target_entities if e.name.lower() == target_name.lower()), None)
        
        if not source_entity or not target_entity:
            logger.warning(f"Could not connect entities: {source_name} or {target_name} not found")
            return None
        
        # Create relationship
        return self.knowledge_graph.add_relationship(
            source_id=source_entity.id,
            target_id=target_entity.id,
            relation_type=relation_type,
            description=description
        )
    
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
        relevant_entities = []
        
        # Search for direct matches first
        direct_matches = self.knowledge_graph.find_entities(query=query)
        
        # If entity types provided, filter by type
        if entity_types:
            for entity_type in entity_types:
                type_matches = self.knowledge_graph.find_entities(entity_type=entity_type)
                # Keep only those that match the query
                filtered_matches = [
                    e for e in type_matches 
                    if query.lower() in e.name.lower() or 
                    query.lower() in e.short_description.lower() or
                    query.lower() in e.detailed_description.lower()
                ]
                direct_matches.extend(filtered_matches)
        
        # If tags provided, find entities with those tags
        if tags:
            tag_matches = []
            for entity in self.knowledge_graph.find_entities():
                if any(tag.lower() in [t.lower() for t in entity.tags] for tag in tags):
                    if (query.lower() in entity.name.lower() or 
                        query.lower() in entity.short_description.lower() or
                        query.lower() in entity.detailed_description.lower()):
                        tag_matches.append(entity)
            direct_matches.extend(tag_matches)
        
        # Remove duplicates and limit results
        seen_ids = set()
        for entity in direct_matches:
            if entity.id not in seen_ids:
                relevant_entities.append(entity)
                seen_ids.add(entity.id)
                if len(relevant_entities) >= max_results:
                    break
        
        # If we don't have enough results, try broader search
        if len(relevant_entities) < max_results:
            query_parts = query.split()
            for part in query_parts:
                if len(part) > 3:  # Only search for meaningful words
                    part_matches = self.knowledge_graph.find_entities(query=part)
                    for entity in part_matches:
                        if entity.id not in seen_ids:
                            relevant_entities.append(entity)
                            seen_ids.add(entity.id)
                            if len(relevant_entities) >= max_results:
                                break
                if len(relevant_entities) >= max_results:
                    break
        
        # For each entity, get related entities and relationships
        result = {
            "query": query,
            "entities": [],
            "relationships": []
        }
        
        # Add the entities and their direct relationships
        for entity in relevant_entities:
            # Add entity
            result["entities"].append({
                "id": entity.id,
                "name": entity.name,
                "type": entity.entity_type,
                "description": entity.short_description,
                "tags": entity.tags
            })
            
            # Get related entities
            related = self.knowledge_graph.get_related_entities(entity.id)
            
            # Add relationships
            for rel in related:
                related_entity = rel["entity"]
                result["relationships"].append({
                    "source": entity.name,
                    "source_id": entity.id,
                    "target": related_entity.name,
                    "target_id": related_entity.id,
                    "type": rel["relationship"],
                    "direction": rel["direction"]
                })
                
                # Add related entity if not already included
                if related_entity.id not in seen_ids:
                    result["entities"].append({
                        "id": related_entity.id,
                        "name": related_entity.name,
                        "type": related_entity.entity_type,
                        "description": related_entity.short_description,
                        "tags": related_entity.tags
                    })
                    seen_ids.add(related_entity.id)
        
        return result
    
    def store_campaign_knowledge(self, campaign_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Store knowledge about a campaign in the knowledge graph.
        
        This specialized method helps Strategy and Campaign agents automatically
        capture campaign information in the knowledge graph.
        
        Args:
            campaign_data: Dictionary containing campaign information
            
        Returns:
            Dict[str, str]: Dictionary mapping entity names to their IDs
        """
        entity_ids = {}
        
        # Create campaign entity
        campaign_id = self.store_entity(
            name=campaign_data["name"],
            entity_type="campaign",
            short_description=campaign_data.get("objective", ""),
            detailed_description=campaign_data.get("brief", ""),
            tags=["campaign", campaign_data.get("type", "advertising")],
            metadata={
                "budget": campaign_data.get("budget"),
                "start_date": campaign_data.get("start_date"),
                "end_date": campaign_data.get("end_date"),
                "status": campaign_data.get("status", "draft"),
                "client": campaign_data.get("client")
            }
        )
        entity_ids["campaign"] = campaign_id
        
        # Create brand entity if it doesn't exist
        if "brand" in campaign_data:
            brand_entities = self.knowledge_graph.find_entities(
                query=campaign_data["brand"],
                entity_type="brand"
            )
            
            brand_entity = next((e for e in brand_entities if e.name.lower() == campaign_data["brand"].lower()), None)
            
            if not brand_entity:
                brand_id = self.store_entity(
                    name=campaign_data["brand"],
                    entity_type="brand",
                    short_description=f"Brand: {campaign_data['brand']}",
                    tags=["brand"],
                    metadata={
                        "industry": campaign_data.get("industry"),
                        "client": campaign_data.get("client")
                    }
                )
                entity_ids["brand"] = brand_id
            else:
                entity_ids["brand"] = brand_entity.id
            
            # Connect campaign to brand
            self.knowledge_graph.add_relationship(
                source_id=campaign_id,
                target_id=entity_ids["brand"],
                relation_type="promotes",
                description=f"Campaign for {campaign_data['brand']}"
            )
        
        # Create audience entities
        if "audiences" in campaign_data and isinstance(campaign_data["audiences"], list):
            audience_ids = []
            for idx, audience in enumerate(campaign_data["audiences"]):
                if isinstance(audience, dict):
                    audience_name = audience.get("name", f"Audience {idx+1}")
                    audience_desc = audience.get("description", "")
                else:
                    audience_name = str(audience)
                    audience_desc = ""
                
                audience_id = self.store_entity(
                    name=audience_name,
                    entity_type="audience_segment",
                    short_description=audience_desc,
                    tags=["audience"],
                    metadata=audience if isinstance(audience, dict) else {}
                )
                audience_ids.append(audience_id)
                entity_ids[f"audience_{idx}"] = audience_id
                
                # Connect campaign to audience
                self.knowledge_graph.add_relationship(
                    source_id=campaign_id,
                    target_id=audience_id,
                    relation_type="targets",
                    description=f"Campaign targets {audience_name}"
                )
        
        # Create creative approach entities
        if "creative_approaches" in campaign_data and isinstance(campaign_data["creative_approaches"], list):
            for idx, approach in enumerate(campaign_data["creative_approaches"]):
                if isinstance(approach, dict):
                    approach_name = approach.get("name", f"Creative Approach {idx+1}")
                    approach_desc = approach.get("description", "")
                else:
                    approach_name = str(approach)
                    approach_desc = ""
                
                approach_id = self.store_entity(
                    name=approach_name,
                    entity_type="creative_approach",
                    short_description=approach_desc,
                    tags=["creative"],
                    metadata=approach if isinstance(approach, dict) else {}
                )
                entity_ids[f"creative_{idx}"] = approach_id
                
                # Connect campaign to creative approach
                self.knowledge_graph.add_relationship(
                    source_id=campaign_id,
                    target_id=approach_id,
                    relation_type="uses",
                    description=f"Campaign uses {approach_name} creative approach"
                )
        
        # Create channel entities
        if "channels" in campaign_data and isinstance(campaign_data["channels"], list):
            for idx, channel in enumerate(campaign_data["channels"]):
                if isinstance(channel, dict):
                    channel_name = channel.get("name", f"Channel {idx+1}")
                    channel_desc = channel.get("description", "")
                else:
                    channel_name = str(channel)
                    channel_desc = ""
                
                # Check if channel already exists
                channel_entities = self.knowledge_graph.find_entities(
                    query=channel_name,
                    entity_type="channel"
                )
                
                channel_entity = next((e for e in channel_entities if e.name.lower() == channel_name.lower()), None)
                
                if not channel_entity:
                    channel_id = self.store_entity(
                        name=channel_name,
                        entity_type="channel",
                        short_description=channel_desc,
                        tags=["channel"],
                        metadata=channel if isinstance(channel, dict) else {}
                    )
                    entity_ids[f"channel_{idx}"] = channel_id
                else:
                    entity_ids[f"channel_{idx}"] = channel_entity.id
                
                # Connect campaign to channel
                self.knowledge_graph.add_relationship(
                    source_id=campaign_id,
                    target_id=entity_ids[f"channel_{idx}"],
                    relation_type="uses",
                    description=f"Campaign uses {channel_name} channel"
                )
        
        return entity_ids
    
    def capture_creative_knowledge(self, creative_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Store knowledge about creative assets in the knowledge graph.
        
        This specialized method helps Creative agents capture design patterns,
        messaging frameworks, and creative assets.
        
        Args:
            creative_data: Dictionary containing creative information
            
        Returns:
            Dict[str, str]: Dictionary mapping entity names to their IDs
        """
        entity_ids = {}
        
        # Create creative asset entity
        asset_id = self.store_entity(
            name=creative_data["name"],
            entity_type="asset",
            short_description=creative_data.get("headline", creative_data.get("description", "")),
            detailed_description=creative_data.get("content", ""),
            tags=["creative", creative_data.get("type", "asset")],
            metadata={
                "format": creative_data.get("format"),
                "dimensions": creative_data.get("dimensions"),
                "created_date": creative_data.get("created_date"),
                "version": creative_data.get("version", "1.0"),
                "status": creative_data.get("status", "draft")
            }
        )
        entity_ids["asset"] = asset_id
        
        # Link to campaign if provided
        if "campaign" in creative_data:
            campaign_entities = self.knowledge_graph.find_entities(
                query=creative_data["campaign"],
                entity_type="campaign"
            )
            
            campaign_entity = next((e for e in campaign_entities if e.name.lower() == creative_data["campaign"].lower()), None)
            
            if campaign_entity:
                self.knowledge_graph.add_relationship(
                    source_id=asset_id,
                    target_id=campaign_entity.id,
                    relation_type="part_of",
                    description=f"Creative asset for {creative_data['campaign']} campaign"
                )
                entity_ids["campaign"] = campaign_entity.id
        
        # Capture creative approach or pattern
        if "approach" in creative_data:
            approach_name = creative_data["approach"]
            approach_entities = self.knowledge_graph.find_entities(
                query=approach_name,
                entity_type="creative_approach"
            )
            
            approach_entity = next((e for e in approach_entities if e.name.lower() == approach_name.lower()), None)
            
            if not approach_entity:
                approach_id = self.store_entity(
                    name=approach_name,
                    entity_type="creative_approach",
                    short_description=f"Creative approach: {approach_name}",
                    tags=["creative", "approach"],
                    metadata={}
                )
                entity_ids["approach"] = approach_id
            else:
                entity_ids["approach"] = approach_entity.id
            
            # Connect asset to approach
            self.knowledge_graph.add_relationship(
                source_id=asset_id,
                target_id=entity_ids["approach"],
                relation_type="uses",
                description=f"Creative asset uses {approach_name} approach"
            )
        
        # Capture messaging elements
        if "messages" in creative_data and isinstance(creative_data["messages"], list):
            for idx, message in enumerate(creative_data["messages"]):
                if isinstance(message, dict):
                    message_name = message.get("name", f"Message {idx+1}")
                    message_text = message.get("text", "")
                else:
                    message_name = f"Message {idx+1}"
                    message_text = str(message)
                
                message_id = self.store_entity(
                    name=message_name,
                    entity_type="message",
                    short_description=message_text[:100] + ("..." if len(message_text) > 100 else ""),
                    detailed_description=message_text,
                    tags=["message"],
                    metadata=message if isinstance(message, dict) else {}
                )
                entity_ids[f"message_{idx}"] = message_id
                
                # Connect asset to message
                self.knowledge_graph.add_relationship(
                    source_id=asset_id,
                    target_id=message_id,
                    relation_type="contains",
                    description=f"Creative asset contains this message"
                )
        
        return entity_ids
    
    def capture_media_knowledge(self, media_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Store knowledge about media planning in the knowledge graph.
        
        This specialized method helps Media Planning agents capture channel information,
        budget allocation patterns, and performance data.
        
        Args:
            media_data: Dictionary containing media planning information
            
        Returns:
            Dict[str, str]: Dictionary mapping entity names to their IDs
        """
        entity_ids = {}
        
        # Create media plan entity
        plan_id = self.store_entity(
            name=media_data["name"],
            entity_type="media_plan",
            short_description=media_data.get("objective", ""),
            detailed_description=media_data.get("description", ""),
            tags=["media", "plan"],
            metadata={
                "budget": media_data.get("budget"),
                "start_date": media_data.get("start_date"),
                "end_date": media_data.get("end_date"),
                "status": media_data.get("status", "draft")
            }
        )
        entity_ids["plan"] = plan_id
        
        # Link to campaign if provided
        if "campaign" in media_data:
            campaign_entities = self.knowledge_graph.find_entities(
                query=media_data["campaign"],
                entity_type="campaign"
            )
            
            campaign_entity = next((e for e in campaign_entities if e.name.lower() == media_data["campaign"].lower()), None)
            
            if campaign_entity:
                self.knowledge_graph.add_relationship(
                    source_id=plan_id,
                    target_id=campaign_entity.id,
                    relation_type="part_of",
                    description=f"Media plan for {media_data['campaign']} campaign"
                )
                entity_ids["campaign"] = campaign_entity.id
        
        # Store channel allocations
        if "allocations" in media_data and isinstance(media_data["allocations"], list):
            for idx, allocation in enumerate(media_data["allocations"]):
                channel_name = allocation.get("channel")
                budget = allocation.get("budget")
                
                if not channel_name:
                    continue
                
                # Check if channel already exists
                channel_entities = self.knowledge_graph.find_entities(
                    query=channel_name,
                    entity_type="channel"
                )
                
                channel_entity = next((e for e in channel_entities if e.name.lower() == channel_name.lower()), None)
                
                if not channel_entity:
                    channel_id = self.store_entity(
                        name=channel_name,
                        entity_type="channel",
                        short_description=f"Media channel: {channel_name}",
                        tags=["channel"],
                        metadata={}
                    )
                    entity_ids[f"channel_{idx}"] = channel_id
                else:
                    entity_ids[f"channel_{idx}"] = channel_entity.id
                
                # Create allocation entity
                allocation_id = self.store_entity(
                    name=f"{channel_name} Allocation",
                    entity_type="media_allocation",
                    short_description=f"Budget allocation for {channel_name}",
                    tags=["allocation"],
                    metadata={
                        "channel": channel_name,
                        "budget": budget,
                        "percentage": allocation.get("percentage"),
                        "start_date": allocation.get("start_date"),
                        "end_date": allocation.get("end_date"),
                        "targeting": allocation.get("targeting")
                    }
                )
                entity_ids[f"allocation_{idx}"] = allocation_id
                
                # Connect plan to allocation
                self.knowledge_graph.add_relationship(
                    source_id=plan_id,
                    target_id=allocation_id,
                    relation_type="contains",
                    description=f"Media plan includes this allocation"
                )
                
                # Connect allocation to channel
                self.knowledge_graph.add_relationship(
                    source_id=allocation_id,
                    target_id=entity_ids[f"channel_{idx}"],
                    relation_type="allocates_to",
                    description=f"Budget allocated to {channel_name}"
                )
        
        # Store performance metrics if available
        if "metrics" in media_data and isinstance(media_data["metrics"], list):
            for idx, metric in enumerate(media_data["metrics"]):
                metric_name = metric.get("name")
                
                if not metric_name:
                    continue
                
                metric_id = self.store_entity(
                    name=metric_name,
                    entity_type="metric",
                    short_description=metric.get("description", f"Performance metric: {metric_name}"),
                    tags=["metric"],
                    metadata={
                        "value": metric.get("value"),
                        "unit": metric.get("unit"),
                        "target": metric.get("target"),
                        "date": metric.get("date")
                    }
                )
                entity_ids[f"metric_{idx}"] = metric_id
                
                # Connect plan to metric
                self.knowledge_graph.add_relationship(
                    source_id=plan_id,
                    target_id=metric_id,
                    relation_type="measured_by",
                    description=f"Media plan performance measured by {metric_name}"
                )
        
        return entity_ids
    
    def capture_analytics_knowledge(self, analytics_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Store analytics insights in the knowledge graph.
        
        This specialized method helps Analytics agents capture performance data,
        insights, and recommendations.
        
        Args:
            analytics_data: Dictionary containing analytics information
            
        Returns:
            Dict[str, str]: Dictionary mapping entity names to their IDs
        """
        entity_ids = {}
        
        # Create insight entity
        insight_id = self.store_entity(
            name=analytics_data["name"],
            entity_type="insight",
            short_description=analytics_data.get("summary", ""),
            detailed_description=analytics_data.get("description", ""),
            tags=["analytics", "insight", analytics_data.get("type", "performance")],
            metadata={
                "confidence": analytics_data.get("confidence"),
                "impact": analytics_data.get("impact"),
                "date": analytics_data.get("date"),
                "source": analytics_data.get("source")
            }
        )
        entity_ids["insight"] = insight_id
        
        # Link to campaign if provided
        if "campaign" in analytics_data:
            campaign_entities = self.knowledge_graph.find_entities(
                query=analytics_data["campaign"],
                entity_type="campaign"
            )
            
            campaign_entity = next((e for e in campaign_entities if e.name.lower() == analytics_data["campaign"].lower()), None)
            
            if campaign_entity:
                self.knowledge_graph.add_relationship(
                    source_id=insight_id,
                    target_id=campaign_entity.id,
                    relation_type="derived_from",
                    description=f"Insight derived from {analytics_data['campaign']} campaign"
                )
                entity_ids["campaign"] = campaign_entity.id
        
        # Store metrics
        if "metrics" in analytics_data and isinstance(analytics_data["metrics"], list):
            for idx, metric in enumerate(analytics_data["metrics"]):
                metric_name = metric.get("name")
                
                if not metric_name:
                    continue
                
                metric_id = self.store_entity(
                    name=metric_name,
                    entity_type="metric",
                    short_description=metric.get("description", f"Performance metric: {metric_name}"),
                    tags=["metric"],
                    metadata={
                        "value": metric.get("value"),
                        "unit": metric.get("unit"),
                        "benchmark": metric.get("benchmark"),
                        "date": metric.get("date"),
                        "trend": metric.get("trend")
                    }
                )
                entity_ids[f"metric_{idx}"] = metric_id
                
                # Connect insight to metric
                self.knowledge_graph.add_relationship(
                    source_id=insight_id,
                    target_id=metric_id,
                    relation_type="based_on",
                    description=f"Insight based on {metric_name} metric"
                )
        
        # Store recommendations
        if "recommendations" in analytics_data and isinstance(analytics_data["recommendations"], list):
            for idx, recommendation in enumerate(analytics_data["recommendations"]):
                if isinstance(recommendation, dict):
                    rec_name = recommendation.get("name", f"Recommendation {idx+1}")
                    rec_desc = recommendation.get("description", "")
                else:
                    rec_name = f"Recommendation {idx+1}"
                    rec_desc = str(recommendation)
                
                rec_id = self.store_entity(
                    name=rec_name,
                    entity_type="recommendation",
                    short_description=rec_desc[:100] + ("..." if len(rec_desc) > 100 else ""),
                    detailed_description=rec_desc,
                    tags=["recommendation"],
                    metadata=recommendation if isinstance(recommendation, dict) else {}
                )
                entity_ids[f"recommendation_{idx}"] = rec_id
                
                # Connect insight to recommendation
                self.knowledge_graph.add_relationship(
                    source_id=insight_id,
                    target_id=rec_id,
                    relation_type="leads_to",
                    description=f"Insight leads to this recommendation"
                )
        
        return entity_ids
    
    def retrieve_campaign_knowledge(self, campaign_name: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive knowledge about a campaign.
        
        This method gathers all related entities and relationships for a given campaign,
        providing a complete view of its structure, assets, performance, and insights.
        
        Args:
            campaign_name: Name of the campaign
            
        Returns:
            Dict[str, Any]: Comprehensive campaign knowledge
        """
        # Find campaign entity
        campaign_entities = self.knowledge_graph.find_entities(
            query=campaign_name,
            entity_type="campaign"
        )
        
        campaign_entity = next((e for e in campaign_entities if e.name.lower() == campaign_name.lower()), None)
        
        if not campaign_entity:
            return {"error": f"Campaign '{campaign_name}' not found"}
        
        # Get all entities related to this campaign with depth=2
        related = self.knowledge_graph.get_related_entities(
            entity_id=campaign_entity.id,
            depth=2
        )
        
        # Organize related entities by type and relationship
        result = {
            "campaign": {
                "id": campaign_entity.id,
                "name": campaign_entity.name,
                "description": campaign_entity.short_description,
                "detailed_description": campaign_entity.detailed_description,
                "metadata": campaign_entity.metadata
            },
            "brand": [],
            "audiences": [],
            "creative_approaches": [],
            "assets": [],
            "channels": [],
            "metrics": [],
            "insights": [],
            "recommendations": []
        }
        
        # Process related entities
        for relation in related:
            entity = relation["entity"]
            relationship = relation["relationship"]
            direction = relation["direction"]
            
            entity_data = {
                "id": entity.id,
                "name": entity.name,
                "description": entity.short_description,
                "metadata": entity.metadata,
                "relationship": relationship,
                "direction": direction
            }
            
            # Add to appropriate category based on entity type
            if entity.entity_type == "brand":
                result["brand"].append(entity_data)
            elif entity.entity_type == "audience_segment":
                result["audiences"].append(entity_data)
            elif entity.entity_type == "creative_approach":
                result["creative_approaches"].append(entity_data)
            elif entity.entity_type == "asset":
                result["assets"].append(entity_data)
            elif entity.entity_type == "channel":
                result["channels"].append(entity_data)
            elif entity.entity_type == "metric":
                result["metrics"].append(entity_data)
            elif entity.entity_type == "insight":
                result["insights"].append(entity_data)
            elif entity.entity_type == "recommendation":
                result["recommendations"].append(entity_data)
        
        return result