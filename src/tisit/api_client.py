# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps other programs talk to our knowledge brain easily. It's like
# a universal translator that handles all the complicated communication details.

# High School Explanation:
# This module provides a client library for interacting with the TISIT Knowledge
# Graph API. It abstracts away HTTP request details and provides a clean, object-oriented
# interface for operations on entities and relationships.

import json
import logging
from typing import Dict, List, Optional, Any, Union
import httpx
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class TisitApiClient:
    """
    Client for interacting with the TISIT Knowledge Graph API.
    
    This class provides methods for all API operations, including entity
    and relationship management, searching, and domain-specific operations.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 10):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the TISIT API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
    
    def _make_url(self, path: str) -> str:
        """Create a full URL from a path."""
        return urljoin(self.base_url, path)
    
    def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Process API response and handle errors."""
        if response.status_code >= 400:
            # Try to get error details from response
            error_detail = "Unknown error"
            try:
                error_data = response.json()
                if "detail" in error_data:
                    error_detail = error_data["detail"]
            except:
                error_detail = response.text
            
            logger.error(f"API error: {response.status_code} - {error_detail}")
            
            # Raise appropriate exception
            if response.status_code == 404:
                raise ValueError(f"Not found: {error_detail}")
            elif response.status_code == 400:
                raise ValueError(f"Bad request: {error_detail}")
            else:
                raise RuntimeError(f"API error ({response.status_code}): {error_detail}")
        
        # Return JSON response if possible
        try:
            return response.json()
        except:
            return {"success": True, "status_code": response.status_code}
    
    # Entity operations
    def create_entity(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new entity in the knowledge graph."""
        url = self._make_url("/entities")
        response = self.client.post(url, json=entity_data)
        return self._handle_response(response)
    
    def list_entities(self, entity_type: Optional[str] = None, 
                      tag: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """List entities with optional filtering."""
        url = self._make_url("/entities")
        params = {}
        if entity_type:
            params["entity_type"] = entity_type
        if tag:
            params["tag"] = tag
        params["limit"] = limit
        
        response = self.client.get(url, params=params)
        return self._handle_response(response)
    
    def get_entity(self, entity_id: str) -> Dict[str, Any]:
        """Get entity by ID."""
        url = self._make_url(f"/entities/{entity_id}")
        response = self.client.get(url)
        return self._handle_response(response)
    
    def update_entity(self, entity_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing entity."""
        url = self._make_url(f"/entities/{entity_id}")
        response = self.client.put(url, json=update_data)
        return self._handle_response(response)
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity and its relationships."""
        url = self._make_url(f"/entities/{entity_id}")
        response = self.client.delete(url)
        
        # Return True if successful (204 No Content)
        return response.status_code == 204
    
    def get_related_entities(self, entity_id: str, relation_type: Optional[str] = None,
                            direction: str = "all", depth: int = 1) -> List[Dict[str, Any]]:
        """Get entities related to the given entity."""
        url = self._make_url(f"/entities/{entity_id}/related")
        params = {
            "direction": direction,
            "depth": depth
        }
        if relation_type:
            params["relation_type"] = relation_type
        
        response = self.client.get(url, params=params)
        return self._handle_response(response)
    
    # Relationship operations
    def create_relationship(self, relationship_data: Dict[str, Any]) -> Dict[str, str]:
        """Create a new relationship between entities."""
        url = self._make_url("/relationships")
        response = self.client.post(url, json=relationship_data)
        return self._handle_response(response)
    
    def get_relationship(self, relationship_id: str) -> Dict[str, Any]:
        """Get relationship by ID."""
        url = self._make_url(f"/relationships/{relationship_id}")
        response = self.client.get(url)
        return self._handle_response(response)
    
    def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship."""
        url = self._make_url(f"/relationships/{relationship_id}")
        response = self.client.delete(url)
        
        # Return True if successful (204 No Content)
        return response.status_code == 204
    
    # Search operations
    def search_entities(self, query: Optional[str] = None, entity_type: Optional[str] = None,
                       tags: Optional[List[str]] = None, match_all_tags: bool = True) -> Dict[str, Any]:
        """Search for entities matching criteria."""
        url = self._make_url("/search")
        search_params = {
            "query": query,
            "entity_type": entity_type,
            "tags": tags,
            "match_all_tags": match_all_tags
        }
        
        response = self.client.post(url, json=search_params)
        return self._handle_response(response)
    
    # Graph operations
    def find_path(self, source_id: str, target_id: str, max_depth: int = 5) -> Dict[str, Any]:
        """Find a path between two entities in the graph."""
        url = self._make_url("/graph/path")
        params = {
            "source_id": source_id,
            "target_id": target_id,
            "max_depth": max_depth
        }
        
        response = self.client.get(url, params=params)
        return self._handle_response(response)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        url = self._make_url("/graph/statistics")
        response = self.client.get(url)
        return self._handle_response(response)
    
    # Domain-specific operations
    def store_campaign_knowledge(self, campaign_data: Dict[str, Any]) -> Dict[str, str]:
        """Store knowledge about a campaign in the knowledge graph."""
        url = self._make_url("/domains/campaign")
        response = self.client.post(url, json=campaign_data)
        return self._handle_response(response)
    
    def store_creative_knowledge(self, creative_data: Dict[str, Any]) -> Dict[str, str]:
        """Store knowledge about creative assets in the knowledge graph."""
        url = self._make_url("/domains/creative")
        response = self.client.post(url, json=creative_data)
        return self._handle_response(response)
    
    def store_media_knowledge(self, media_data: Dict[str, Any]) -> Dict[str, str]:
        """Store knowledge about media planning in the knowledge graph."""
        url = self._make_url("/domains/media")
        response = self.client.post(url, json=media_data)
        return self._handle_response(response)
    
    def store_analytics_knowledge(self, analytics_data: Dict[str, Any]) -> Dict[str, str]:
        """Store analytics insights in the knowledge graph."""
        url = self._make_url("/domains/analytics")
        response = self.client.post(url, json=analytics_data)
        return self._handle_response(response)
    
    def retrieve_campaign_knowledge(self, campaign_name: str) -> Dict[str, Any]:
        """Retrieve comprehensive knowledge about a campaign."""
        url = self._make_url(f"/domains/campaign/{campaign_name}")
        response = self.client.get(url)
        return self._handle_response(response)
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.close()


# Example usage
def example_usage():
    """Show example usage of the API client."""
    client = TisitApiClient()
    
    try:
        # Create entity
        entity = client.create_entity({
            "name": "Digital Storytelling",
            "entity_type": "creative_approach",
            "short_description": "Using digital media to tell compelling brand stories",
            "tags": ["creative", "digital", "storytelling"]
        })
        
        print(f"Created entity: {entity['name']} (ID: {entity['id']})")
        
        # Search for entities
        results = client.search_entities(query="storytelling")
        print(f"Found {results['count']} entities matching 'storytelling'")
        
        # Store campaign knowledge
        campaign_data = {
            "name": "Summer Product Launch",
            "objective": "Increase brand awareness and drive initial sales",
            "brand": "EcoTech",
            "audiences": [
                {"name": "Eco-conscious Millennials", "description": "25-40 year olds focused on sustainability"}
            ]
        }
        
        entity_ids = client.store_campaign_knowledge(campaign_data)
        print(f"Created campaign entity with ID: {entity_ids.get('campaign')}")
        
        # Close client
        client.close()
    
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    example_usage()