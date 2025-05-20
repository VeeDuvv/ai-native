// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

// Fifth Grade Explanation:
// This file helps our web page talk to our knowledge brain. It's like a messenger
// that asks for information and brings back answers.

// High School Explanation:
// This module provides API client functions for the TISIT dashboard components.
// It handles data fetching, formatting, and error handling for the React components
// to interact with the TISIT Knowledge Graph API.

import axios from 'axios';

// Configure API client
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_TISIT_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Transform API data into a format suitable for react-force-graph
 */
const transformToGraphData = (entities, relationships) => {
  // Create nodes array
  const nodes = entities.map(entity => ({
    id: entity.id,
    name: entity.name,
    type: entity.entity_type,
    description: entity.short_description,
    detailed_description: entity.detailed_description,
    tags: entity.tags,
    domain: entity.domain,
    created_at: entity.created_at,
    updated_at: entity.updated_at,
    metadata: entity.metadata,
    relationships: entity.relationships,
  }));
  
  // Create links array (for known relationships)
  const links = [];
  const nodeMap = new Map(nodes.map(node => [node.id, node]));
  
  // Add links from relationships array
  if (relationships && relationships.length > 0) {
    relationships.forEach(rel => {
      // Only add if both source and target exist in nodes
      if (nodeMap.has(rel.source_id) && nodeMap.has(rel.target_id)) {
        links.push({
          id: rel.id,
          source: rel.source_id,
          target: rel.target_id,
          type: rel.relation_type,
          description: rel.description,
          weight: rel.weight,
        });
      }
    });
  }
  
  // Fill in missing relationships from entity relationships
  nodes.forEach(node => {
    if (node.relationships) {
      Object.entries(node.relationships).forEach(([targetId, relationType]) => {
        // Only add if target exists in nodes and we don't already have this link
        if (nodeMap.has(targetId) && !links.some(link => 
          (link.source === node.id && link.target === targetId) || 
          (link.source === targetId && link.target === node.id)
        )) {
          links.push({
            id: `${node.id}-${targetId}`,
            source: node.id,
            target: targetId,
            type: relationType,
          });
        }
      });
    }
  });
  
  return { nodes, links };
};

/**
 * Fetch graph data for visualization
 * @param {Object} options - Options for filtering data
 * @param {string} options.entityType - Filter by entity type
 * @param {string} options.query - Search query
 * @returns {Promise<Object>} Graph data with nodes and links
 */
export const fetchGraphData = async ({ entityType = '', query = '' }) => {
  try {
    // Fetch entities
    let entities = [];
    
    if (query) {
      // Use search endpoint
      const searchResponse = await apiClient.post('/search', {
        query,
        entity_type: entityType || null,
        match_all_tags: true,
      });
      entities = searchResponse.data.entities || [];
    } else if (entityType) {
      // Fetch entities by type
      const response = await apiClient.get('/entities', {
        params: { entity_type: entityType, limit: 100 },
      });
      entities = response.data || [];
    } else {
      // Fetch all entities (with reasonable limit)
      const response = await apiClient.get('/entities', {
        params: { limit: 100 },
      });
      entities = response.data || [];
    }
    
    // If we have very few entities, expand with related entities
    if (entities.length > 0 && entities.length < 10) {
      // For each entity, fetch related entities to expand the graph
      const relatedPromises = entities.map(entity => 
        apiClient.get(`/entities/${entity.id}/related`, {
          params: { direction: 'all', depth: 1 },
        })
      );
      
      const relatedResponses = await Promise.all(relatedPromises);
      const relatedEntitiesArrays = relatedResponses.map(response => response.data || []);
      
      // Add all related entities to the entities array
      relatedEntitiesArrays.forEach(relatedArray => {
        relatedArray.forEach(related => {
          const entity = related.entity;
          // Add if not already in the list
          if (!entities.some(e => e.id === entity.id)) {
            entities.push(entity);
          }
        });
      });
    }
    
    // Fetch relationships between these entities
    // Currently not directly supported by the API, so use entity relationships
    
    // Transform to graph data format
    return transformToGraphData(entities, []);
  } catch (error) {
    console.error('Error fetching graph data:', error);
    throw error;
  }
};

/**
 * Fetch available entity types
 * @returns {Promise<string[]>} List of entity types
 */
export const fetchEntityTypes = async () => {
  try {
    const response = await apiClient.get('/graph/statistics');
    
    // Extract entity types from statistics
    if (response.data && response.data.entity_types) {
      return Object.keys(response.data.entity_types);
    }
    
    return [];
  } catch (error) {
    console.error('Error fetching entity types:', error);
    return [];
  }
};

/**
 * Search for entities
 * @param {Object} searchParams - Search parameters
 * @param {string} searchParams.query - Search query
 * @param {string} searchParams.entityType - Filter by entity type
 * @param {string[]} searchParams.tags - Filter by tags
 * @returns {Promise<Object>} Search results
 */
export const searchEntities = async ({ query, entityType, tags }) => {
  try {
    const response = await apiClient.post('/search', {
      query,
      entity_type: entityType || null,
      tags: tags || null,
      match_all_tags: true,
    });
    
    return response.data;
  } catch (error) {
    console.error('Error searching entities:', error);
    throw error;
  }
};

/**
 * Get entity by ID
 * @param {string} entityId - Entity ID
 * @returns {Promise<Object>} Entity data
 */
export const getEntity = async (entityId) => {
  try {
    const response = await apiClient.get(`/entities/${entityId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching entity ${entityId}:`, error);
    throw error;
  }
};

/**
 * Get related entities
 * @param {string} entityId - Entity ID
 * @param {Object} options - Options for filtering related entities
 * @param {string} options.relationType - Filter by relationship type
 * @param {string} options.direction - Direction of relationships ('outgoing', 'incoming', or 'all')
 * @param {number} options.depth - Depth of traversal
 * @returns {Promise<Object[]>} Related entities with relationship info
 */
export const getRelatedEntities = async (
  entityId, 
  { relationType = null, direction = 'all', depth = 1 } = {}
) => {
  try {
    const params = {
      direction,
      depth,
    };
    
    if (relationType) {
      params.relation_type = relationType;
    }
    
    const response = await apiClient.get(`/entities/${entityId}/related`, { params });
    return response.data;
  } catch (error) {
    console.error(`Error fetching related entities for ${entityId}:`, error);
    throw error;
  }
};

/**
 * Get campaign knowledge
 * @param {string} campaignName - Campaign name
 * @returns {Promise<Object>} Campaign knowledge data
 */
export const getCampaignKnowledge = async (campaignName) => {
  try {
    const response = await apiClient.get(`/domains/campaign/${encodeURIComponent(campaignName)}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching campaign knowledge for ${campaignName}:`, error);
    throw error;
  }
};