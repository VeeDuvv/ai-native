# Project Context

This file contains important information about the AI-native project.

## Project Objectives

Project Objective: I want to use Generative AI and Agentic AI to create an AI-native company

## CTO Role and Perspective

- As the CTO, my primary responsibility is to provide expert solutions with a critical thinking mindset
- I am committed to building the startup by:
  - Developing innovative technological strategies
  - Ensuring our solutions align with our core project tenets
  - Maintaining a forward-thinking approach to our technical architecture
  - Being a strategic partner in transforming our vision into reality

## Development Guidelines

### License and Copyright

Include the following lines at the top of every file we create:

```
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri
```

### Documentation Requirements

For every file we create, include two explanations of the file's purpose:

1. **Fifth Grade Explanation**: A simple explanation that a 10-11 year old could understand
2. **High School Explanation**: A more detailed explanation suitable for a high school student

Example:
```
# Fifth Grade Explanation:
# This file is like a translator that helps your computer talk to Claude. It sends your
# questions to Claude and brings back the answers.

# High School Explanation:
# This module implements a client for the Claude API that handles authentication,
# request formatting, and response parsing. It abstracts the HTTP communication
# and provides a clean interface for the application to interact with Claude's
# capabilities.
```

## Our Tenets: AI-Native Ad Agency Architecture Principles

<!-- SPDX-License-Identifier: MIT -->
<!-- Copyright (c) 2025 Vamsi Duvvuri -->

### Introduction

The AI-Native Ad Agency is built on foundational principles that guide our technology decisions. These tenets represent our values and vision for creating a truly AI-native platform that can scale, adapt, and evolve over time.

### Core Tenets

#### 1. Agent-First Architecture

**Principle**: Our platform is built around autonomous AI agents as first-class citizens.

**Implementation**:
- Each agent has a clear, focused responsibility
- Agents communicate via standardized protocols
- New agents can be dynamically created and integrated
- All agent activity is observable and measurable

#### 2. API-First Design

**Principle**: All functionality is built as APIs first, interfaces second.

**Implementation**:
- Every capability is exposed via a well-documented API
- APIs are versioned, stable, and backward-compatible
- UIs consume the same APIs that are available externally
- Authentication and access control are handled at the API layer

#### 3. Extensibility Over Optimization

**Principle**: We prioritize the ability to extend our system over premature optimization.

**Implementation**:
- Modular components with clear interfaces
- Plugin architecture for specialized functionality
- Configuration over code wherever possible
- Libraries and frameworks chosen for flexibility

#### 4. Separation of Concerns

**Principle**: System components should have minimal knowledge of each other.

**Implementation**:
- Backend, frontend, and agent systems are cleanly separated
- Each component has a single responsibility
- Communication happens through well-defined interfaces
- Components can be developed, tested, and deployed independently

#### 5. Data-Driven Evolution

**Principle**: The system should learn and improve based on its own operation.

**Implementation**:
- Comprehensive logging of all operations
- Analytics built into the core architecture
- Feedback loops for agent performance
- Knowledge repository that grows with system use

#### 6. Minimizing Technical Debt

**Principle**: We make decisions that consider long-term implications over short-term gains.

**Implementation**:
- Thorough documentation of all components
- Regular refactoring to maintain clean code
- Comprehensive test coverage at all levels
- Clear deprecation processes for legacy components

#### 7. Human-AI Collaboration

**Principle**: We design for effective collaboration between human users and AI agents.

**Implementation**:
- Intuitive interfaces for agent configuration
- Transparent AI operations with explainable decisions
- Appropriate human oversight and intervention points
- Incremental automation with human feedback

### Architecture Guidelines

To support these tenets, we follow these specific architecture guidelines:

#### Backend Guidelines

1. **Stateless Services**: Backend services should be stateless where possible to enable scaling
2. **Resource-Based API Design**: Follow RESTful principles with clear resource naming
3. **Proper Error Handling**: Informative error messages with appropriate status codes
4. **Comprehensive Logging**: All operations should be logged with appropriate detail
5. **Configuration Management**: External configuration for environment-specific settings

#### Agent System Guidelines

1. **Independent Agent Context**: Each agent maintains its own execution context
2. **Standardized Messages**: All inter-agent communication uses standard message formats
3. **Monitored Execution**: Agent activities are tracked for performance and debugging
4. **Transactional Operations**: Long-running agent operations should be transactional
5. **Fallback Mechanisms**: Graceful degradation when agents fail or timeout

#### Frontend Guidelines

1. **Component-Based Design**: UIs built from reusable, composable components
2. **Consistent Data Flow**: Unidirectional data flow for predictable state management
3. **Responsive Design**: All UIs work across various screen sizes and devices
4. **Accessibility**: UIs meet accessibility standards (WCAG 2.1 AA)
5. **Performance Budgets**: Clear metrics for load time and interaction responsiveness

### Anti-Patterns We Avoid

1. **Hardcoded Business Logic**: Business rules should be configurable, not hardcoded
2. **Monolithic Applications**: We avoid large, all-in-one applications
3. **Tight Coupling**: Components should not have detailed knowledge of each other
4. **Direct Database Access**: Applications access data via APIs, not direct DB queries
5. **Premature Optimization**: We don't optimize before measuring performance
6. **Inconsistent Interfaces**: APIs follow consistent patterns across the platform

### Conclusion

These tenets guide our day-to-day decisions and help us build a platform that can evolve with our business needs. They ensure we're building a truly AI-native ad agency that leverages the power of autonomous agents while maintaining the flexibility to adapt to changing requirements and technologies.

## Project Structure

- claude_client.py