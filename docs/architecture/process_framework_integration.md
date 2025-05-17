# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file explains how our AI helpers will follow standard business rules that experts 
# have created, instead of making up their own rules. It's like following a recipe book 
# written by professional chefs instead of making up your own recipes.

# High School Explanation:
# This document outlines how our agent framework will integrate with standard process 
# frameworks like APQC and eTOM to define workflows and processes. Instead of hardcoding 
# process logic, agents will dynamically interpret and execute standardized process 
# definitions from these established frameworks.

# Process Framework Integration for Agent System

## Overview

Rather than hardcoding business processes and workflows within our agent system, we will integrate industry-standard process frameworks like APQC (American Productivity & Quality Center) and eTOM (enhanced Telecom Operations Map) to guide agent behavior and workflows. This approach provides several advantages:

1. **Standardization**: Leveraging established, industry-recognized process frameworks
2. **Flexibility**: Processes can be modified without code changes
3. **Completeness**: Ensures comprehensive coverage of business functions
4. **Interoperability**: Facilitates integration with other systems using the same frameworks
5. **Best Practices**: Incorporates industry best practices and benchmarks

This document outlines our strategy for integrating these process frameworks into our agent architecture.

## Process Framework Selection

Our system will support multiple process frameworks, with initial focus on:

1. **APQC Process Classification Framework (PCF)**
   - Comprehensive, cross-industry taxonomy of business processes
   - Hierarchical structure with process categories, groups, processes, and activities
   - Widely adopted across industries

2. **eTOM (Business Process Framework)**
   - Telecommunications industry-specific process framework
   - Three main process areas: Strategy/Infrastructure/Product, Operations, and Enterprise Management
   - Detailed process decomposition with specific activities

3. **Custom Framework Extensions**
   - Industry-specific extensions to standard frameworks
   - Domain-specific processes for advertising industry
   - Client-specific process adaptations

## Architecture Components

### 1. Process Repository

A central database storing process definitions from various frameworks:

```json
{
  "framework_id": "apqc",
  "version": "7.2.1",
  "processes": [
    {
      "id": "10.0",
      "name": "Develop and Manage Products and Services",
      "description": "Process of identifying, developing, and refining products and services",
      "sub_processes": [
        {
          "id": "10.1",
          "name": "Manage product and service portfolio",
          "activities": [
            {
              "id": "10.1.1",
              "name": "Evaluate performance of existing products/services against market opportunities",
              "inputs": [...],
              "outputs": [...],
              "metrics": [...],
              "roles": [...]
            },
            ...
          ]
        },
        ...
      ]
    },
    ...
  ]
}
```

### 2. Process Interpreter

An engine that parses and interprets process definitions:

- Resolves process hierarchies and relationships
- Extracts activity sequences and dependencies
- Maps process activities to agent capabilities
- Handles process variations and exceptions

### 3. Workflow Engine

Coordinates the execution of processes across multiple agents:

- Creates execution plans from process definitions
- Manages process state and transitions
- Tracks process instances and their progress
- Handles parallel, sequential, and conditional flows
- Implements compensating transactions for failures

### 4. Process-Aware Agent Interface

Extension of the base agent interfaces with process-specific capabilities:

```python
class ProcessAwareAgent(OperationalAgent):
    """
    Agent interface for process-aware operational agents.
    """
    
    def get_supported_activities(self) -> List[Dict]:
        """
        Returns activities this agent can perform from the process framework.
        
        Returns:
            List[Dict]: List of supported activities with framework identifiers
        """
        pass
    
    def execute_activity(self, activity_id: str, context: Dict) -> Dict:
        """
        Execute a specific activity from the process framework.
        
        Args:
            activity_id: Framework-specific activity identifier
            context: Activity execution context
            
        Returns:
            Dict: Activity execution results
        """
        pass
    
    def get_activity_requirements(self, activity_id: str) -> Dict:
        """
        Get input requirements for executing a specific activity.
        
        Args:
            activity_id: Framework-specific activity identifier
            
        Returns:
            Dict: Input requirements for the activity
        """
        pass
```

### 5. Process Definition Tools

Tools for importing, mapping, and customizing process framework definitions:

- Framework importers for standard formats (APQC Excel, eTOM XML)
- Visual process editor for customization
- Version control for process definitions
- Compatibility validators for framework updates

## Implementation Approach

### 1. Process Framework Representation

Process frameworks will be represented in a standardized, machine-readable format:

```python
class ProcessFramework:
    """Represents a process framework like APQC or eTOM."""
    
    def __init__(self, framework_id, name, version):
        self.framework_id = framework_id
        self.name = name
        self.version = version
        self.root_processes = []  # Top-level processes
        
class Process:
    """Represents a process within a framework."""
    
    def __init__(self, process_id, name, description):
        self.process_id = process_id
        self.name = name
        self.description = description
        self.sub_processes = []  # Child processes
        self.activities = []     # Executable activities
        self.inputs = []         # Required inputs
        self.outputs = []        # Expected outputs
        self.metrics = []        # Performance metrics
        self.roles = []          # Responsible roles
        
class Activity:
    """Represents an executable activity within a process."""
    
    def __init__(self, activity_id, name, description):
        self.activity_id = activity_id
        self.name = name
        self.description = description
        self.preconditions = []  # Required conditions before execution
        self.postconditions = [] # Expected conditions after execution
        self.inputs = []         # Required inputs
        self.outputs = []        # Expected outputs
        self.agent_capabilities = [] # Required agent capabilities
        self.execution_steps = [] # Detailed execution steps
```

### 2. Agent-Process Mapping

A mapping system will connect process activities to agent capabilities:

```json
{
  "activity_id": "10.1.2.3",
  "framework": "apqc",
  "agent_types": ["CampaignStrategyAgent", "CreativeGenerationAgent"],
  "required_capabilities": ["strategy.market_analysis", "creative.concept_development"],
  "input_mapping": {
    "market_data": "context.data.market_analysis",
    "client_brief": "context.data.client_requirements"
  },
  "output_mapping": {
    "campaign_strategy": "result.strategy_document",
    "creative_concepts": "result.concept_list"
  }
}
```

### 3. Process Execution Flow

The workflow engine will manage process execution:

1. **Process Initialization**:
   - Client request triggers a process instance creation
   - System identifies the applicable process from frameworks
   - Initial context is established

2. **Activity Planning**:
   - Activities are identified and sequenced based on process definition
   - Dependencies and conditions are evaluated
   - Suitable agents are identified for each activity

3. **Activity Execution**:
   - Selected agent(s) execute each activity
   - Inputs are transformed to agent-specific format
   - Outputs are captured and mapped back to process format

4. **Process Monitoring and Control**:
   - Progress is tracked against process definition
   - Metrics are collected for process evaluation
   - Exceptions are handled according to process rules

5. **Process Completion**:
   - Final outputs are compiled
   - Process metrics are recorded
   - Resources are released

## Example: APQC-Driven Campaign Creation Process

Here's how our system would handle a campaign creation process using APQC's framework:

1. **Process Identification**:
   - System identifies APQC process 3.4 "Develop and manage marketing campaigns"
   - Loads the process definition with its sub-processes and activities

2. **Process Orchestration**:
   - Creates execution plan based on APQC 3.4.1 - 3.4.5 activities
   - Maps activities to agent capabilities

3. **Agent Assignment**:
   - APQC 3.4.1 "Develop campaign concepts" → assigned to CampaignStrategyAgent
   - APQC 3.4.2 "Test marketing campaigns" → assigned to AnalyticsAgent
   - APQC 3.4.3 "Launch marketing campaigns" → assigned to MediaBuyingAgent
   - APQC 3.4.4 "Execute marketing campaigns" → coordinated across agents
   - APQC 3.4.5 "Measure marketing campaign effectiveness" → assigned to AnalyticsAgent

4. **Activity Execution**:
   - Each agent executes its assigned activities
   - Workflow engine manages transitions between activities
   - Process data is maintained according to APQC's input/output specifications

## Implementation Strategy

We will implement the process framework integration in phases:

### Phase 1: Framework Representation
- Develop data models for process frameworks
- Create importers for APQC and eTOM
- Build basic process repository

### Phase 2: Process Interpreter
- Implement process parsing and interpretation
- Create activity resolution and mapping system
- Develop agent capability matching

### Phase 3: Workflow Engine
- Build process instance management
- Implement activity sequencing and execution
- Create state tracking and persistence

### Phase 4: Agent Integration
- Extend agent interfaces for process awareness
- Implement activity execution handlers
- Develop input/output transformations

### Phase 5: Advanced Features
- Add process monitoring and metrics
- Implement exception handling and recovery
- Create process optimization mechanisms

## Benefits of Framework-Driven Approach

1. **Reduced Development Time**: Leverage existing process definitions rather than creating from scratch
2. **Business-IT Alignment**: Use terminology and structures familiar to business stakeholders
3. **Scalability**: New processes can be added without code changes
4. **Maintainability**: Process changes don't require code modifications
5. **Consistency**: Standard approach to process execution across the system
6. **Analytics**: Standard metrics for benchmarking and improvement

## Challenges and Mitigations

| Challenge | Mitigation |
|-----------|------------|
| Framework complexity | Create simplified views for common scenarios |
| Process variations | Support framework extensions and customizations |
| Performance overhead | Cache process definitions and execution paths |
| Framework updates | Version control and compatibility testing |
| Integration with legacy systems | Develop adapters for specific systems |

## Conclusion

By integrating standard process frameworks like APQC and eTOM into our agent architecture, we create a flexible system that can adapt to different business processes without code changes. Our agents become interpreters of standardized process definitions rather than hardcoded workflow implementations.

This approach enables our AI-native advertising agency to follow industry best practices while maintaining the flexibility to customize processes for specific client needs. It creates a clear separation between business process definitions (what should be done) and agent implementations (how it should be done), making our system more maintainable and adaptable.