# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file explains how our computer program talks to the internet and other programs.
# It's like creating special doorways that let information go in and out of our system
# in a safe and organized way.

# High School Explanation:
# This document details the design of our API gateway, which serves as the interface
# between our agent-based system and external clients/services. It defines the RESTful
# endpoints, authentication mechanisms, request/response formats, and integration points.

# API Layer Design

## Overview

The API Layer serves as the primary interface between our AI-native advertising platform and the outside world. It provides a consistent, secure, and well-documented way for clients to access our system's capabilities, while abstracting away the complexity of the underlying agent architecture.

This document outlines the design principles, architecture, and specifications for our API layer, in alignment with our API-first design principle.

## Design Principles

### 1. RESTful Resource Orientation

- APIs are organized around resources (nouns, not verbs)
- HTTP methods (GET, POST, PUT, DELETE) have consistent semantics
- Resource identifiers (URIs) follow a consistent, hierarchical structure
- Resources support standard CRUD operations where appropriate

### 2. Consistent Design Patterns

- Uniform request/response formats across all endpoints
- Consistent error handling and status codes
- Standardized pagination, filtering, and sorting
- Hypermedia links for resource relationships

### 3. Versioning Strategy

- All APIs are versioned in the URI path (e.g., `/v1/campaigns`)
- Backward compatibility maintained within major versions
- Clear deprecation notices and migration paths
- Version lifecycle documentation

### 4. Security by Design

- OAuth 2.0 authentication and authorization
- Fine-grained permission model
- Rate limiting and abuse prevention
- Comprehensive audit logging

### 5. Documentation as First-Class Citizen

- OpenAPI/Swagger specifications for all endpoints
- Interactive documentation
- Code examples for common operations
- SDK generation from API specifications

## API Architecture

### Components

1. **API Gateway**
   - Request routing and load balancing
   - Authentication and authorization enforcement
   - Rate limiting and throttling
   - Request/response transformation
   - Caching for appropriate resources

2. **API Controllers**
   - Resource-specific request handling
   - Input validation
   - Business logic coordination
   - Response formatting

3. **Agent Coordinator**
   - Translation between API requests and agent tasks
   - Agent selection and orchestration
   - Results aggregation and transformation
   - Error handling and recovery

4. **Authentication Service**
   - User/client identification
   - Token generation and validation
   - Permission enforcement
   - Integration with identity providers

5. **Documentation System**
   - API specification generation
   - Interactive API explorer
   - Code sample generation
   - Client SDK generation

### Technology Stack

1. **API Gateway**: FastAPI (Python framework)
2. **Authentication**: OAuth 2.0 with JWT
3. **Documentation**: OpenAPI 3.0 / Swagger UI
4. **Testing**: Pytest, Postman collections
5. **Monitoring**: Prometheus, Grafana

## API Resources

### Core Resources

#### 1. Campaigns

Represents advertising campaigns created and managed through our platform.

```
GET    /v1/campaigns
POST   /v1/campaigns
GET    /v1/campaigns/{campaign_id}
PUT    /v1/campaigns/{campaign_id}
DELETE /v1/campaigns/{campaign_id}
GET    /v1/campaigns/{campaign_id}/creatives
GET    /v1/campaigns/{campaign_id}/performance
POST   /v1/campaigns/{campaign_id}/actions/launch
POST   /v1/campaigns/{campaign_id}/actions/pause
```

#### 2. Creatives

Represents advertising content (text, images, videos) used in campaigns.

```
GET    /v1/creatives
POST   /v1/creatives
GET    /v1/creatives/{creative_id}
PUT    /v1/creatives/{creative_id}
DELETE /v1/creatives/{creative_id}
POST   /v1/creatives/{creative_id}/actions/generate-variations
GET    /v1/creatives/{creative_id}/variations
```

#### 3. Audiences

Represents target audience definitions for campaigns.

```
GET    /v1/audiences
POST   /v1/audiences
GET    /v1/audiences/{audience_id}
PUT    /v1/audiences/{audience_id}
DELETE /v1/audiences/{audience_id}
GET    /v1/audiences/{audience_id}/size-estimate
```

#### 4. Analytics

Provides performance metrics and insights for campaigns and creatives.

```
GET    /v1/analytics/campaigns
GET    /v1/analytics/campaigns/{campaign_id}
GET    /v1/analytics/creatives/{creative_id}
GET    /v1/analytics/audiences/{audience_id}
POST   /v1/analytics/reports
GET    /v1/analytics/reports/{report_id}
```

#### 5. Media

Manages media buying, placement, and optimization.

```
GET    /v1/media/channels
GET    /v1/media/placements
POST   /v1/media/placements
GET    /v1/media/placements/{placement_id}
PUT    /v1/media/placements/{placement_id}
DELETE /v1/media/placements/{placement_id}
GET    /v1/media/budgets
POST   /v1/media/budgets
GET    /v1/media/budgets/{budget_id}
PUT    /v1/media/budgets/{budget_id}
```

### System Resources

#### 1. Users and Authentication

Manages user accounts, authentication, and authorization.

```
POST   /v1/auth/token
POST   /v1/auth/refresh
POST   /v1/auth/revoke
GET    /v1/users/me
GET    /v1/users
POST   /v1/users
GET    /v1/users/{user_id}
PUT    /v1/users/{user_id}
DELETE /v1/users/{user_id}
GET    /v1/roles
GET    /v1/permissions
```

#### 2. Agents

Provides management and monitoring of the agent ecosystem.

```
GET    /v1/agents
GET    /v1/agents/{agent_id}
PUT    /v1/agents/{agent_id}/config
GET    /v1/agents/{agent_id}/status
GET    /v1/agents/{agent_id}/metrics
POST   /v1/agents/{agent_id}/actions/pause
POST   /v1/agents/{agent_id}/actions/resume
```

#### 3. Workflows

Manages business process workflows across the system.

```
GET    /v1/workflows
POST   /v1/workflows
GET    /v1/workflows/{workflow_id}
PUT    /v1/workflows/{workflow_id}
DELETE /v1/workflows/{workflow_id}
GET    /v1/workflows/{workflow_id}/status
POST   /v1/workflows/{workflow_id}/actions/start
POST   /v1/workflows/{workflow_id}/actions/pause
POST   /v1/workflows/{workflow_id}/actions/resume
```

## Request/Response Formats

### Standard Request Format

```json
{
  "data": {
    // Resource-specific request data
  },
  "meta": {
    "client_request_id": "optional-client-generated-id",
    "idempotency_key": "optional-idempotency-key"
  }
}
```

### Standard Response Format

```json
{
  "data": {
    // Resource-specific response data
  },
  "meta": {
    "request_id": "server-generated-request-id",
    "timestamp": "2025-05-17T12:34:56Z"
  },
  "links": {
    "self": "https://api.ai-native-ad.example/v1/resource/id",
    "related": {
      "relationship": "https://api.ai-native-ad.example/v1/related-resource"
    }
  },
  "included": [
    // Optional included related resources
  ]
}
```

### Collection Response Format

```json
{
  "data": [
    // Array of resource objects
  ],
  "meta": {
    "request_id": "server-generated-request-id",
    "timestamp": "2025-05-17T12:34:56Z",
    "pagination": {
      "total_items": 1423,
      "total_pages": 72,
      "current_page": 3,
      "items_per_page": 20
    }
  },
  "links": {
    "self": "https://api.ai-native-ad.example/v1/resources?page=3&per_page=20",
    "first": "https://api.ai-native-ad.example/v1/resources?page=1&per_page=20",
    "prev": "https://api.ai-native-ad.example/v1/resources?page=2&per_page=20",
    "next": "https://api.ai-native-ad.example/v1/resources?page=4&per_page=20",
    "last": "https://api.ai-native-ad.example/v1/resources?page=72&per_page=20"
  }
}
```

### Error Response Format

```json
{
  "errors": [
    {
      "code": "ERROR_CODE",
      "title": "Human-readable error title",
      "detail": "Detailed explanation of the error",
      "source": {
        "pointer": "/data/attributes/field_name"
      },
      "status": "HTTP_STATUS_CODE"
    }
  ],
  "meta": {
    "request_id": "server-generated-request-id",
    "timestamp": "2025-05-17T12:34:56Z"
  }
}
```

## Authentication and Authorization

### Authentication Flow

1. **Client Registration**
   - Clients register with the system to obtain client credentials
   - Admin approves client and assigns appropriate scopes

2. **Token Acquisition**
   - Client authenticates with client_id and client_secret
   - System issues JWT access token and refresh token
   - Access token includes scopes and expiration time

3. **API Access**
   - Client includes access token in Authorization header
   - API gateway validates token and extracts claims
   - Requests proceed with authenticated identity

4. **Token Refresh**
   - Client uses refresh token to obtain new access token
   - Refresh tokens have longer validity but can be revoked

### Permission Model

1. **Role-Based Access Control**
   - Users/clients are assigned to roles
   - Roles contain collections of permissions
   - Permissions grant access to specific resources/actions

2. **Scope-Based Authorization**
   - OAuth scopes limit token capabilities
   - Scopes mapped to specific API endpoints
   - Granular control over client permissions

3. **Resource Ownership**
   - Resources have owners (users/organizations)
   - Access policies respect ownership boundaries
   - Delegation mechanisms for shared resources

## Rate Limiting and Quotas

### Rate Limiting Strategy

1. **Per-Client Limits**
   - Limits based on client identity
   - Different tiers for different client types
   - Configurable per endpoint or resource type

2. **Graduated Response**
   - Warning headers when approaching limits
   - Throttling before hard rejection
   - Clear error messages with reset time

3. **Burst Handling**
   - Token bucket algorithm for handling bursts
   - Short-term flexibility with long-term constraints
   - Configurable burst parameters

### Quota Management

1. **Usage Tracking**
   - Track resource consumption per client
   - Reset periods (daily, monthly)
   - Usage notifications and reporting

2. **Resource-Specific Quotas**
   - Different limits for different resources
   - Higher costs for computationally expensive operations
   - Special allocations for premium clients

## Integration with Agent Framework

The API Layer interacts with our agent framework through a dedicated coordinator component:

### 1. Request Translation

API requests are translated into tasks that agents can understand:

```
API Request → Task Definition → Agent Assignment
```

For example, a `POST /v1/campaigns` request is translated into a task for the Campaign Strategy Agent.

### 2. Agent Selection

The coordinator selects appropriate agents based on:
- Task requirements
- Agent capabilities
- Current availability
- Load balancing

### 3. Task Execution

Tasks are executed by agents through the agent framework:
- Long-running operations use asynchronous processing
- Status endpoints for checking progress
- Webhooks for completion notifications

### 4. Response Composition

Agent outputs are transformed back into API responses:
- Data formatting and structure
- Inclusion of related resources
- Error normalization
- HATEOAS links

## Versioning and Evolution

### Version Control

1. **URI Path Versioning**
   - Major version in path: `/v1/resources`
   - Ensures clear separation between versions

2. **Compatibility Policy**
   - No breaking changes within a major version
   - Additive changes only (new fields, endpoints)
   - Deprecation notices before removal

### Migration Support

1. **Version Sunset Process**
   - Clear timelines for version deprecation
   - Transition period with both versions available
   - Migration guides and support tools

2. **Compatibility Headers**
   - Optional headers for fine-grained compatibility
   - Feature flags for incremental adoption
   - Backward compatibility mode

## Documentation

### OpenAPI Specification

Each API endpoint will be documented with OpenAPI 3.0 specifications, including:
- Complete endpoint definitions
- Request/response schemas
- Authentication requirements
- Example requests and responses
- Error scenarios

### Developer Portal

A comprehensive developer portal will provide:
- Interactive API explorer
- Getting started guides
- Authentication tutorials
- SDK documentation
- Best practices
- Change logs

## Implementation Plan

### Phase 1: Foundation

1. **Core Infrastructure**
   - API gateway setup
   - Authentication system
   - Basic routing

2. **Documentation Framework**
   - OpenAPI specification structure
   - Documentation generation pipeline
   - Developer portal skeleton

3. **Initial Endpoints**
   - Health/status endpoints
   - Authentication endpoints
   - User management

### Phase 2: Core Resources

1. **Campaign Management**
   - Campaign CRUD operations
   - Campaign status management
   - Creative association

2. **Creative Development**
   - Creative generation
   - Creative management
   - Variation handling

3. **Media Placement**
   - Channel management
   - Placement creation
   - Budget allocation

### Phase 3: Advanced Features

1. **Analytics and Reporting**
   - Performance metrics
   - Custom report generation
   - Data visualization endpoints

2. **Workflow Management**
   - Process execution
   - Workflow monitoring
   - Custom workflow creation

3. **System Administration**
   - Agent management
   - Configuration endpoints
   - System monitoring

## Conclusion

The API Layer is designed to provide a robust, secure, and developer-friendly interface to our AI-native advertising platform. By following RESTful principles, implementing consistent patterns, and providing comprehensive documentation, we aim to make our platform accessible and intuitive for clients while maintaining security and scalability.

The design aligns with our core architectural principles, particularly API-first design and separation of concerns. It provides a clear boundary between external interactions and internal agent processes, enabling each to evolve independently while maintaining compatibility.