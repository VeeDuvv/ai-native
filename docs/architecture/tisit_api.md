# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# TISIT Knowledge Graph API

## Overview

The TISIT Knowledge Graph API provides a RESTful interface for accessing and manipulating the TISIT knowledge graph. This enables distributed architectures where agents and other systems can interact with a centralized knowledge repository over the network.

## Architecture

The API is built using FastAPI, a modern, high-performance web framework for building APIs with Python. It provides the following key components:

1. **API Server**: Provides the HTTP endpoints and request handling.
2. **API Client**: Client library for easily integrating with the API from Python code.
3. **Remote Agent Integration**: Adapters that allow agents to interact with the TISIT knowledge graph over the network.

![API Architecture Diagram]

## Endpoints

The API provides the following endpoint categories:

### Entity Endpoints

| Endpoint                 | Method | Description                                 |
|--------------------------|--------|---------------------------------------------|
| `/entities`              | POST   | Create a new entity                         |
| `/entities`              | GET    | List entities with optional filtering       |
| `/entities/{entity_id}`  | GET    | Get entity by ID                            |
| `/entities/{entity_id}`  | PUT    | Update an existing entity                   |
| `/entities/{entity_id}`  | DELETE | Delete an entity and its relationships      |
| `/entities/{entity_id}/related` | GET | Get entities related to the given entity |

### Relationship Endpoints

| Endpoint                        | Method | Description                       |
|---------------------------------|--------|-----------------------------------|
| `/relationships`                | POST   | Create a new relationship         |
| `/relationships/{relationship_id}` | GET | Get relationship by ID           |
| `/relationships/{relationship_id}` | DELETE | Delete a relationship          |

### Search Endpoints

| Endpoint    | Method | Description                          |
|-------------|--------|--------------------------------------|
| `/search`   | POST   | Search for entities matching criteria |

### Graph Operations

| Endpoint           | Method | Description                           |
|--------------------|--------|---------------------------------------|
| `/graph/path`      | GET    | Find a path between two entities      |
| `/graph/statistics`| GET    | Get statistics about the knowledge graph |

### Domain-Specific Endpoints

| Endpoint                       | Method | Description                                 |
|--------------------------------|--------|---------------------------------------------|
| `/domains/campaign`            | POST   | Store knowledge about a campaign            |
| `/domains/creative`            | POST   | Store knowledge about creative assets       |
| `/domains/media`               | POST   | Store knowledge about media planning        |
| `/domains/analytics`           | POST   | Store analytics insights                    |
| `/domains/campaign/{campaign_name}` | GET | Retrieve comprehensive campaign knowledge |

## Client Library

The API client library provides a simple, object-oriented interface for interacting with the API:

```python
from src.tisit.api_client import TisitApiClient

# Create client
client = TisitApiClient(base_url="http://localhost:8000")

# Create entity
entity = client.create_entity({
    "name": "Digital Storytelling",
    "entity_type": "creative_approach",
    "short_description": "Using digital media to tell compelling brand stories",
    "tags": ["creative", "digital", "storytelling"]
})

# Search for entities
results = client.search_entities(query="storytelling")
print(f"Found {results['count']} entities matching 'storytelling'")

# Store campaign knowledge
entity_ids = client.store_campaign_knowledge({
    "name": "Summer Product Launch",
    "objective": "Increase brand awareness",
    "brand": "EcoTech",
    "audiences": [
        {"name": "Eco-conscious Millennials", "description": "..."}
    ]
})
```

## Remote Agent Integration

The remote agent integration allows agents to interact with the TISIT knowledge graph over the network using the same interface as the direct integration:

```python
from src.tisit.remote_agent_integration import RemoteKnowledgeEnhancedAgent

# Create agent with remote knowledge graph integration
agent = RemoteKnowledgeEnhancedAgent(
    name="StrategyAgent",
    api_url="http://localhost:8000",
    description="Develops campaign strategies with knowledge-enhanced insights"
)

# Store information in the knowledge graph
entity_id = agent.remember(
    entity_name="Emotional Storytelling",
    entity_type="creative_approach",
    description="Technique that uses emotion to connect with audience",
    tags=["creative", "storytelling", "emotion"]
)

# Retrieve relevant knowledge
knowledge = agent.recall(
    query="sustainability marketing",
    entity_types=["creative_approach", "audience_segment"],
    tags=["eco-friendly", "green"]
)
```

## Deployment Options

The API server can be deployed in various ways:

1. **Standalone Server**: Run as a standalone service on a dedicated server.
2. **Docker Container**: Package as a Docker container for easy deployment.
3. **Serverless**: Deploy as a serverless function (e.g., AWS Lambda with API Gateway).
4. **Kubernetes**: Deploy as a service in a Kubernetes cluster for scaling.

The API server can be started with the following command:

```bash
python -m src.tisit.api_server --host 0.0.0.0 --port 8000 --data-dir /path/to/data
```

## Security Considerations

The current implementation is focused on functionality rather than security. For production use, the following security enhancements should be considered:

1. **Authentication**: Add JWT-based authentication.
2. **Authorization**: Implement role-based access control.
3. **Transport Security**: Enable HTTPS with proper certificates.
4. **Rate Limiting**: Add rate limiting to prevent abuse.
5. **Input Validation**: Strengthen input validation beyond Pydantic.

## Future Enhancements

Planned enhancements for the API include:

1. **GraphQL Interface**: Add GraphQL support for more flexible querying.
2. **WebSocket Support**: Enable real-time notifications for knowledge updates.
3. **Batch Operations**: Support for batch entity and relationship operations.
4. **Semantic Search**: Add vector-based semantic search capabilities.
5. **Advanced Filtering**: More sophisticated filtering options for entity queries.
6. **Pagination**: Implement cursor-based pagination for large result sets.

## Integration with Agent Framework

The API integrates with our agent framework through the remote agent integration layer, which provides a drop-in replacement for the direct integration. This allows agents to interact with the knowledge graph regardless of whether it's local or remote.

The remote integration maintains the same interface as the direct integration, enabling code to work without modification when switching between local and remote knowledge graphs.