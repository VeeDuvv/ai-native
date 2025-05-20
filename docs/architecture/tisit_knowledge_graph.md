# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# TISIT Knowledge Graph Implementation

## Overview

The TISIT (This Is What It Is) Knowledge Graph serves as the collective intelligence system for our AI-native advertising agency. It provides a structured way to represent, store, and access knowledge across all agent activities, ensuring that insights and learnings are preserved and leveraged throughout the platform.

## Core Components

The TISIT Knowledge Graph implementation consists of several key components:

### 1. Entity System

Entities are the primary building blocks of the knowledge graph, representing discrete units of knowledge:

- **Entity Types**: Supports various domain-specific types such as:
  - Marketing concepts: campaign, audience_segment, creative_approach, channel, strategy, metric, brand, message, asset
  - General knowledge: concept, framework, person, company, product, technology, methodology, process, standard, term, package

- **Entity Structure**:
  - Unique identifier
  - Name and type
  - Short and detailed descriptions
  - Tags for categorization
  - Domain classification
  - Creation and modification timestamps
  - Metadata as flexible key-value pairs
  - References to external sources

### 2. Relationship System

Relationships define connections between entities, enabling a rich graph structure:

- **Relationship Types**: Comprehensive set of typed relationships with bidirectional support:
  - Hierarchical: is_a, part_of, instance_of
  - Dependency: depends_on, requires, uses
  - Influence: affects, influences, created_by
  - Similarity: similar_to, alternative_to
  - Marketing-specific: targets, performs_well_on, measured_by, increases, decreases

- **Relationship Structure**:
  - Source and target entity IDs
  - Relationship type
  - Optional description
  - Weight (strength of relationship)
  - Creation and update timestamps
  - Additional metadata

### 3. Knowledge Graph

The central system that manages entities and relationships:

- **Core Capabilities**:
  - Entity and relationship management
  - Traversal and path finding
  - Pattern-based queries
  - Visualization generation
  - Graph statistics

- **Implementation Details**:
  - Uses NetworkX for graph operations
  - Supports directed, weighted graphs
  - Provides both programmatic and CLI interfaces

### 4. Storage Layer

Persistent storage for the knowledge graph:

- **File Organization**:
  ```
  /tisit/
    /entities/
      /frameworks/
        /a/
          angular.json
      /concepts/
        /a/
          agent-architecture.json
    /relationships/
      relationship1.json
      relationship2.json
    /indexes/
      term-index.json
      relationship-index.json
  ```

- **Storage Features**:
  - JSON-based entity and relationship storage
  - Efficient indexing for quick lookups
  - Directory structure for organized storage
  - Transaction support for atomic operations

### 5. Agent Integration

Specialized interfaces for agent interaction with the knowledge graph:

- **Agent Interface**:
  - Simplified knowledge access for agents
  - Specialized methods for domain-specific knowledge capture
  - Context-aware knowledge retrieval
  - Support for automatic knowledge enrichment

- **Domain-Specific Integration**:
  - Campaign knowledge capture and retrieval
  - Creative concept management
  - Media planning knowledge
  - Performance analytics insights

## Usage Patterns

### 1. Knowledge Capture

Agents can capture knowledge in several ways:

```python
# Basic entity creation
entity_id = agent.knowledge_interface.store_entity(
    name="Emotional Storytelling",
    entity_type="creative_approach",
    short_description="Technique that uses emotion to connect with audience",
    tags=["creative", "storytelling", "emotion"]
)

# Specialized campaign knowledge capture
campaign_entities = agent.knowledge_interface.store_campaign_knowledge({
    "name": "Summer Product Launch",
    "objective": "Increase brand awareness and drive initial sales",
    "brand": "EcoTech",
    "audiences": [
        {"name": "Eco-conscious Millennials", "description": "..."}
    ],
    "creative_approaches": [
        {"name": "Emotional Storytelling", "description": "..."}
    ]
})
```

### 2. Knowledge Retrieval

Agents can retrieve knowledge to inform decisions:

```python
# Simple context retrieval
knowledge = agent.knowledge_interface.get_knowledge_context(
    query="sustainability marketing",
    entity_types=["creative_approach", "audience_segment"],
    tags=["eco-friendly", "green"]
)

# Comprehensive campaign knowledge retrieval
campaign_knowledge = agent.knowledge_interface.retrieve_campaign_knowledge(
    "Summer Product Launch"
)
```

### 3. Relationship Management

Creating connections between knowledge entities:

```python
# Create relationships
agent.knowledge_interface.connect_entities(
    source_name="Emotional Storytelling",
    target_name="Brand Awareness",
    relation_type="increases",
    description="Emotional storytelling has been shown to increase brand awareness"
)

# Find connections
paths = knowledge_graph.find_path(
    source_id=entity1_id,
    target_id=entity2_id,
    max_depth=3
)
```

## Visualization and Exploration

The knowledge graph supports visualization capabilities:

- **Graph Visualization**:
  - NetworkX integration with matplotlib
  - Interactive visualizations (planned)
  - Custom node coloring by entity type
  - Edge labels showing relationship types

- **CLI Exploration**:
  - List entities by type: `tisit list --type campaign`
  - Search for specific entities: `tisit search "emotional storytelling"`
  - View entity details: `tisit view "Summer Product Launch" --related`
  - Create relationships: `tisit link "Technique A" "Metric B" increases`

## Integration Points

The TISIT Knowledge Graph integrates with the broader system in several ways:

1. **Agent Framework Integration**:
   - Specialized agent classes with knowledge capabilities
   - Standard interfaces for knowledge access
   - Background knowledge capture during agent activities

2. **Process Framework Integration**:
   - Process steps can capture and use knowledge
   - Knowledge-enhanced decision points
   - Process outcomes stored as knowledge entities

3. **API Layer Integration** (Planned):
   - RESTful API for knowledge access
   - GraphQL interface for complex graph queries
   - WebSocket notifications for knowledge updates

4. **Dashboard Integration** (Planned):
   - Interactive knowledge exploration
   - Visual relationship browsing
   - Knowledge analytics and metrics

## Future Development

Ongoing and planned enhancements to the TISIT Knowledge Graph:

1. **REST API Development**:
   - Complete RESTful API for programmatic access
   - Authentication and authorization controls
   - Rate limiting and caching for performance

2. **Dashboard Visualizations**:
   - Interactive graph visualization in the client dashboard
   - Knowledge entity browser and editor
   - Campaign-specific knowledge views

3. **Automated Knowledge Capture**:
   - Background processes for automatic knowledge extraction
   - Integration with agent communication channels
   - Natural language processing for knowledge identification

4. **Advanced Query Capabilities**:
   - Natural language queries for knowledge retrieval
   - Semantic search with embeddings
   - Complex pattern matching for insights discovery

## Conclusion

The TISIT Knowledge Graph serves as the collective intelligence engine for our AI-native advertising agency. By capturing, organizing, and providing access to knowledge across all aspects of the platform, it enables agents to make more informed decisions, learn from past experiences, and continuously improve the quality of their outputs.

This implementation follows our core architectural principles, particularly "Data-Driven Evolution" and "Agent-First Architecture," by providing a structured way for agents to build and leverage collective knowledge.