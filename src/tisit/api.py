# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps computers talk to our knowledge brain over the internet.
# It's like creating a special telephone that lets other programs ask questions
# and add new ideas to our knowledge collection.

# High School Explanation:
# This module implements a RESTful API for the TISIT knowledge graph using FastAPI.
# It provides endpoints for creating, retrieving, updating, and deleting entities
# and relationships, as well as performing graph operations and searches.

import os
import json
import logging
from typing import Dict, List, Optional, Any, Set, Union
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Depends, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .entity import Entity
from .relationship import Relationship
from .knowledge_graph import KnowledgeGraph

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Default data directory
DEFAULT_DATA_DIR = os.path.expanduser("~/.tisit")

# Initialize the knowledge graph
knowledge_graph = KnowledgeGraph(DEFAULT_DATA_DIR)

# Create FastAPI app
app = FastAPI(
    title="TISIT Knowledge Graph API",
    description="API for accessing and manipulating the TISIT knowledge graph",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class EntityCreate(BaseModel):
    name: str
    entity_type: str
    short_description: str = ""
    detailed_description: str = ""
    tags: List[str] = []
    domain: Optional[str] = None
    created_by: Optional[str] = None
    metadata: Dict[str, Any] = {}

class EntityUpdate(BaseModel):
    short_description: Optional[str] = None
    detailed_description: Optional[str] = None
    tags: Optional[List[str]] = None
    domain: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class EntityResponse(BaseModel):
    id: str
    name: str
    entity_type: str
    short_description: str
    detailed_description: str
    tags: List[str]
    domain: Optional[str]
    created_by: Optional[str]
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]
    relationships: Dict[str, str]

class RelationshipCreate(BaseModel):
    source_id: str
    target_id: str
    relation_type: str
    description: str = ""
    weight: float = 1.0
    bidirectional: bool = True

class RelationshipResponse(BaseModel):
    id: str
    source_id: str
    target_id: str
    relation_type: str
    description: str
    weight: float
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]

class GraphPathResponse(BaseModel):
    path: List[Dict[str, Any]]
    length: int

class SearchParams(BaseModel):
    query: Optional[str] = None
    entity_type: Optional[str] = None
    tags: Optional[List[str]] = None
    match_all_tags: bool = True

class SearchResponse(BaseModel):
    entities: List[EntityResponse]
    count: int

class GraphStatistics(BaseModel):
    entity_count: int
    relationship_count: int
    entity_types: Dict[str, int]
    relationship_types: Dict[str, int]

# Helper function to convert Entity to EntityResponse
def entity_to_response(entity: Entity) -> EntityResponse:
    return EntityResponse(
        id=entity.id,
        name=entity.name,
        entity_type=entity.entity_type,
        short_description=entity.short_description,
        detailed_description=entity.detailed_description,
        tags=entity.tags,
        domain=entity.domain,
        created_by=entity.created_by,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        metadata=entity.metadata,
        relationships=entity.relationships
    )

# Helper function to convert Relationship to RelationshipResponse
def relationship_to_response(relationship: Relationship) -> RelationshipResponse:
    return RelationshipResponse(
        id=relationship.id,
        source_id=relationship.source_id,
        target_id=relationship.target_id,
        relation_type=relationship.relation_type,
        description=relationship.description,
        weight=relationship.weight,
        created_at=relationship.created_at,
        updated_at=relationship.updated_at,
        metadata=relationship.metadata
    )

# Entity endpoints
@app.post("/entities", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(entity_data: EntityCreate):
    """Create a new entity in the knowledge graph."""
    try:
        # Create entity
        entity = Entity(
            name=entity_data.name,
            entity_type=entity_data.entity_type,
            short_description=entity_data.short_description,
            detailed_description=entity_data.detailed_description,
            tags=entity_data.tags,
            domain=entity_data.domain,
            created_by=entity_data.created_by,
            metadata=entity_data.metadata
        )
        
        # Add to knowledge graph
        entity_id = knowledge_graph.add_entity(entity)
        
        # Get entity from storage to ensure latest data
        entity = knowledge_graph.get_entity(entity_id)
        
        if not entity:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Entity was created but could not be retrieved"
            )
        
        return entity_to_response(entity)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating entity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating entity: {str(e)}"
        )

@app.get("/entities", response_model=List[EntityResponse])
def list_entities(
    entity_type: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100)
):
    """List entities with optional filtering."""
    try:
        if entity_type:
            entities = knowledge_graph.storage.get_entities_by_type(entity_type)
        elif tag:
            entities = knowledge_graph.storage.get_entities_by_tag(tag)
        else:
            # Get all entities
            entities = [knowledge_graph.get_entity(eid) for eid in knowledge_graph.storage.list_entities()]
            entities = [e for e in entities if e is not None]
        
        # Limit results
        entities = entities[:limit]
        
        return [entity_to_response(entity) for entity in entities]
    
    except Exception as e:
        logger.error(f"Error listing entities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing entities: {str(e)}"
        )

@app.get("/entities/{entity_id}", response_model=EntityResponse)
def get_entity(entity_id: str):
    """Get entity by ID."""
    entity = knowledge_graph.get_entity(entity_id)
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {entity_id} not found"
        )
    
    return entity_to_response(entity)

@app.put("/entities/{entity_id}", response_model=EntityResponse)
def update_entity(entity_id: str, update_data: EntityUpdate):
    """Update an existing entity."""
    entity = knowledge_graph.get_entity(entity_id)
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {entity_id} not found"
        )
    
    try:
        # Update descriptions if provided
        if update_data.short_description is not None or update_data.detailed_description is not None:
            entity.update_description(
                short=update_data.short_description, 
                detailed=update_data.detailed_description
            )
        
        # Update domain if provided
        if update_data.domain is not None:
            entity.domain = update_data.domain
        
        # Update tags if provided
        if update_data.tags is not None:
            # Remove tags that aren't in the new list
            for tag in list(entity.tags):
                if tag not in update_data.tags:
                    entity.remove_tag(tag)
            
            # Add new tags
            for tag in update_data.tags:
                if tag not in entity.tags:
                    entity.add_tag(tag)
        
        # Update metadata if provided
        if update_data.metadata is not None:
            # Merge metadata
            for key, value in update_data.metadata.items():
                entity.add_metadata(key, value)
        
        # Save entity
        knowledge_graph.storage.save_entity(entity)
        
        # Get updated entity
        updated_entity = knowledge_graph.get_entity(entity_id)
        
        if not updated_entity:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Entity was updated but could not be retrieved"
            )
        
        return entity_to_response(updated_entity)
    
    except Exception as e:
        logger.error(f"Error updating entity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating entity: {str(e)}"
        )

@app.delete("/entities/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entity(entity_id: str):
    """Delete an entity and its relationships."""
    entity = knowledge_graph.get_entity(entity_id)
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {entity_id} not found"
        )
    
    try:
        success = knowledge_graph.delete_entity(entity_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete entity with ID {entity_id}"
            )
        
        return None
    
    except Exception as e:
        logger.error(f"Error deleting entity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting entity: {str(e)}"
        )

@app.get("/entities/{entity_id}/related", response_model=List[Dict[str, Any]])
def get_related_entities(
    entity_id: str,
    relation_type: Optional[str] = None,
    direction: str = Query("all", regex="^(outgoing|incoming|all)$"),
    depth: int = Query(1, ge=1, le=5)
):
    """Get entities related to the given entity."""
    entity = knowledge_graph.get_entity(entity_id)
    
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with ID {entity_id} not found"
        )
    
    try:
        related = knowledge_graph.get_related_entities(
            entity_id=entity_id,
            relation_type=relation_type,
            direction=direction,
            depth=depth
        )
        
        # Convert entity objects to response format
        response = []
        for rel in related:
            entity_data = entity_to_response(rel["entity"]).dict()
            response.append({
                "entity": entity_data,
                "relationship": rel["relationship"],
                "direction": rel["direction"]
            })
        
        return response
    
    except Exception as e:
        logger.error(f"Error getting related entities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting related entities: {str(e)}"
        )

# Relationship endpoints
@app.post("/relationships", response_model=Dict[str, str], status_code=status.HTTP_201_CREATED)
def create_relationship(relationship_data: RelationshipCreate):
    """Create a new relationship between entities."""
    try:
        # Get entities to check they exist
        source_entity = knowledge_graph.get_entity(relationship_data.source_id)
        target_entity = knowledge_graph.get_entity(relationship_data.target_id)
        
        if not source_entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source entity with ID {relationship_data.source_id} not found"
            )
        
        if not target_entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target entity with ID {relationship_data.target_id} not found"
            )
        
        # Create relationship
        rel_id = knowledge_graph.add_relationship(
            source_id=relationship_data.source_id,
            target_id=relationship_data.target_id,
            relation_type=relationship_data.relation_type,
            description=relationship_data.description,
            weight=relationship_data.weight,
            bidirectional=relationship_data.bidirectional
        )
        
        response = {
            "id": rel_id,
            "message": "Relationship created successfully"
        }
        
        if relationship_data.bidirectional:
            response["message"] = "Bidirectional relationship created successfully"
        
        return response
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating relationship: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating relationship: {str(e)}"
        )

@app.get("/relationships/{relationship_id}", response_model=RelationshipResponse)
def get_relationship(relationship_id: str):
    """Get relationship by ID."""
    relationship = knowledge_graph.storage.get_relationship(relationship_id)
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship with ID {relationship_id} not found"
        )
    
    return relationship_to_response(relationship)

@app.delete("/relationships/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relationship(relationship_id: str):
    """Delete a relationship."""
    relationship = knowledge_graph.storage.get_relationship(relationship_id)
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship with ID {relationship_id} not found"
        )
    
    try:
        success = knowledge_graph.storage.delete_relationship(relationship_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete relationship with ID {relationship_id}"
            )
        
        return None
    
    except Exception as e:
        logger.error(f"Error deleting relationship: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting relationship: {str(e)}"
        )

# Search endpoint
@app.post("/search", response_model=SearchResponse)
def search_entities(search_params: SearchParams):
    """Search for entities matching criteria."""
    try:
        entities = knowledge_graph.find_entities(
            query=search_params.query,
            entity_type=search_params.entity_type,
            tags=search_params.tags,
            match_all_tags=search_params.match_all_tags
        )
        
        response = {
            "entities": [entity_to_response(entity) for entity in entities],
            "count": len(entities)
        }
        
        return response
    
    except Exception as e:
        logger.error(f"Error searching entities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching entities: {str(e)}"
        )

# Graph operations
@app.get("/graph/path", response_model=GraphPathResponse)
def find_path(
    source_id: str,
    target_id: str,
    max_depth: int = Query(5, ge=1, le=10)
):
    """Find a path between two entities in the graph."""
    source_entity = knowledge_graph.get_entity(source_id)
    target_entity = knowledge_graph.get_entity(target_id)
    
    if not source_entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source entity with ID {source_id} not found"
        )
    
    if not target_entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target entity with ID {target_id} not found"
        )
    
    try:
        path = knowledge_graph.find_path(
            source_id=source_id,
            target_id=target_id,
            max_depth=max_depth
        )
        
        if not path:
            return {"path": [], "length": 0}
        
        # Format path for response
        response_path = []
        for step in path:
            response_path.append({
                "source": {
                    "id": step["source"].id,
                    "name": step["source"].name,
                    "type": step["source"].entity_type
                },
                "relationship": step["relationship"],
                "target": {
                    "id": step["target"].id,
                    "name": step["target"].name,
                    "type": step["target"].entity_type
                }
            })
        
        return {
            "path": response_path,
            "length": len(response_path)
        }
    
    except Exception as e:
        logger.error(f"Error finding path: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error finding path: {str(e)}"
        )

@app.get("/graph/statistics", response_model=GraphStatistics)
def get_statistics():
    """Get statistics about the knowledge graph."""
    try:
        stats = knowledge_graph.get_statistics()
        return stats
    
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting statistics: {str(e)}"
        )

# Domain-specific endpoints
@app.post("/domains/campaign", response_model=Dict[str, str])
def store_campaign_knowledge(campaign_data: Dict[str, Any]):
    """Store knowledge about a campaign in the knowledge graph."""
    try:
        from .agent_integration import TisitAgentInterface
        
        # Create a temporary interface for API operations
        interface = TisitAgentInterface(knowledge_graph, "API")
        
        # Store campaign knowledge
        entity_ids = interface.store_campaign_knowledge(campaign_data)
        
        return entity_ids
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error storing campaign knowledge: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error storing campaign knowledge: {str(e)}"
        )

@app.post("/domains/creative", response_model=Dict[str, str])
def store_creative_knowledge(creative_data: Dict[str, Any]):
    """Store knowledge about creative assets in the knowledge graph."""
    try:
        from .agent_integration import TisitAgentInterface
        
        # Create a temporary interface for API operations
        interface = TisitAgentInterface(knowledge_graph, "API")
        
        # Store creative knowledge
        entity_ids = interface.capture_creative_knowledge(creative_data)
        
        return entity_ids
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error storing creative knowledge: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error storing creative knowledge: {str(e)}"
        )

@app.post("/domains/media", response_model=Dict[str, str])
def store_media_knowledge(media_data: Dict[str, Any]):
    """Store knowledge about media planning in the knowledge graph."""
    try:
        from .agent_integration import TisitAgentInterface
        
        # Create a temporary interface for API operations
        interface = TisitAgentInterface(knowledge_graph, "API")
        
        # Store media knowledge
        entity_ids = interface.capture_media_knowledge(media_data)
        
        return entity_ids
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error storing media knowledge: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error storing media knowledge: {str(e)}"
        )

@app.post("/domains/analytics", response_model=Dict[str, str])
def store_analytics_knowledge(analytics_data: Dict[str, Any]):
    """Store analytics insights in the knowledge graph."""
    try:
        from .agent_integration import TisitAgentInterface
        
        # Create a temporary interface for API operations
        interface = TisitAgentInterface(knowledge_graph, "API")
        
        # Store analytics knowledge
        entity_ids = interface.capture_analytics_knowledge(analytics_data)
        
        return entity_ids
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error storing analytics knowledge: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error storing analytics knowledge: {str(e)}"
        )

@app.get("/domains/campaign/{campaign_name}", response_model=Dict[str, Any])
def retrieve_campaign_knowledge(campaign_name: str):
    """Retrieve comprehensive knowledge about a campaign."""
    try:
        from .agent_integration import TisitAgentInterface
        
        # Create a temporary interface for API operations
        interface = TisitAgentInterface(knowledge_graph, "API")
        
        # Retrieve campaign knowledge
        campaign_knowledge = interface.retrieve_campaign_knowledge(campaign_name)
        
        if "error" in campaign_knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=campaign_knowledge["error"]
            )
        
        return campaign_knowledge
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving campaign knowledge: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving campaign knowledge: {str(e)}"
        )

# Run standalone server if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("tisit.api:app", host="0.0.0.0", port=8000, reload=True)