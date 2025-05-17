# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file describes how our AI helpers (agents) will work together. It's like 
# creating rules for a team sport, where each player knows exactly what they should 
# do and how to talk to their teammates.

# High School Explanation:
# This document defines the standardized interfaces that all agents in our system 
# must implement. It establishes the contract between agents and the core framework, 
# ensuring consistent behavior, reliable lifecycle management, and standardized 
# communication patterns.

# Agent Framework: Interface Definitions

## Overview

This document defines the core interfaces that all agents in our AI-native advertising platform must implement. By standardizing these interfaces, we ensure that agents can be developed independently while maintaining compatibility with the overall system. These interfaces address agent lifecycle management, configuration, communication, and observability.

## Core Interfaces

### 1. BaseAgent Interface

The foundation interface that all agents must implement:

```python
class BaseAgent:
    """
    Base interface that all agents must implement in our system.
    """
    
    def initialize(self, config: Dict) -> bool:
        """
        Initialize the agent with the provided configuration.
        
        Args:
            config: Dictionary containing agent configuration parameters
            
        Returns:
            bool: True if initialization succeeded, False otherwise
        """
        pass
        
    def execute(self, context: Dict) -> Dict:
        """
        Execute the agent's primary function with the given context.
        
        Args:
            context: Dictionary containing execution context information
            
        Returns:
            Dict: Results of the agent's execution
        """
        pass
        
    def shutdown(self) -> bool:
        """
        Perform cleanup and resource release operations.
        
        Returns:
            bool: True if shutdown succeeded, False otherwise
        """
        pass
        
    def get_capabilities(self) -> List[str]:
        """
        Return a list of this agent's advertised capabilities.
        
        Returns:
            List[str]: Capability identifiers this agent supports
        """
        pass
        
    def get_status(self) -> Dict:
        """
        Return the current status of the agent.
        
        Returns:
            Dict: Status information including health, state, and metrics
        """
        pass
```

### 2. Agent Lifecycle Interfaces

#### SetupAgent Interface

```python
class SetupAgent(BaseAgent):
    """
    Interface for agents that perform one-time initialization tasks.
    """
    
    def check_prerequisites(self) -> Dict:
        """
        Check if all prerequisites for setup are satisfied.
        
        Returns:
            Dict: Status of prerequisites with any missing dependencies
        """
        pass
    
    def validate_setup(self) -> Dict:
        """
        Validate that setup was completed successfully.
        
        Returns:
            Dict: Validation results including any issues found
        """
        pass
    
    def rollback(self) -> bool:
        """
        Roll back changes if setup fails midway.
        
        Returns:
            bool: True if rollback succeeded, False otherwise
        """
        pass
```

#### OperationalAgent Interface

```python
class OperationalAgent(BaseAgent):
    """
    Interface for agents that perform recurring operational tasks.
    """
    
    def pause(self) -> bool:
        """
        Temporarily pause the agent's operations.
        
        Returns:
            bool: True if successfully paused, False otherwise
        """
        pass
    
    def resume(self) -> bool:
        """
        Resume the agent's operations after being paused.
        
        Returns:
            bool: True if successfully resumed, False otherwise
        """
        pass
    
    def should_execute(self, context: Dict) -> bool:
        """
        Determine if the agent should execute based on the context.
        
        Args:
            context: Dictionary containing execution context information
            
        Returns:
            bool: True if the agent should execute, False otherwise
        """
        pass
```

### 3. Agent Communication Interface

```python
class CommunicatingAgent(BaseAgent):
    """
    Interface for agents that communicate with other agents.
    """
    
    def send_message(self, recipient_id: str, message_type: str, content: Dict) -> str:
        """
        Send a message to another agent.
        
        Args:
            recipient_id: Identifier of the recipient agent
            message_type: Type of message being sent
            content: Dictionary containing the message content
            
        Returns:
            str: Message ID for tracking/reference
        """
        pass
    
    def receive_message(self, message: Dict) -> Dict:
        """
        Process a received message.
        
        Args:
            message: Dictionary containing the message data
            
        Returns:
            Dict: Processing result or response
        """
        pass
    
    def list_subscribed_topics(self) -> List[str]:
        """
        List message topics this agent is subscribed to.
        
        Returns:
            List[str]: Topic identifiers
        """
        pass
```

### 4. Agent Observability Interface

```python
class ObservableAgent(BaseAgent):
    """
    Interface for agents that expose detailed operational metrics and logs.
    """
    
    def get_metrics(self) -> Dict:
        """
        Get performance and operational metrics.
        
        Returns:
            Dict: Metrics keyed by metric name
        """
        pass
    
    def get_logs(self, start_time: datetime, end_time: datetime, 
                level: str = "INFO") -> List[Dict]:
        """
        Retrieve logs for a specific time period and level.
        
        Args:
            start_time: Start of the time period
            end_time: End of the time period
            level: Minimum log level to retrieve
            
        Returns:
            List[Dict]: Log entries matching criteria
        """
        pass
    
    def get_traces(self, trace_id: str = None) -> List[Dict]:
        """
        Get execution traces for debugging and performance analysis.
        
        Args:
            trace_id: Optional specific trace to retrieve
            
        Returns:
            List[Dict]: Trace data
        """
        pass
```

### 5. Agent Configuration Interface

```python
class ConfigurableAgent(BaseAgent):
    """
    Interface for agents with advanced configuration capabilities.
    """
    
    def update_config(self, config_updates: Dict) -> bool:
        """
        Update agent configuration dynamically.
        
        Args:
            config_updates: Dictionary containing configuration updates
            
        Returns:
            bool: True if update succeeded, False otherwise
        """
        pass
    
    def get_config_schema(self) -> Dict:
        """
        Get JSON schema defining valid configuration options.
        
        Returns:
            Dict: JSON schema for agent configuration
        """
        pass
    
    def validate_config(self, config: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a configuration against the agent's schema.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        pass
```

## Common Agent Composition Patterns

Agents in our system will typically implement multiple interfaces depending on their role and requirements:

### Campaign Strategy Agent

```python
class CampaignStrategyAgent(OperationalAgent, CommunicatingAgent, ObservableAgent, ConfigurableAgent):
    """
    Agent responsible for developing advertising campaign strategies.
    """
    pass
```

### Infrastructure Setup Agent

```python
class InfrastructureSetupAgent(SetupAgent, ObservableAgent, ConfigurableAgent):
    """
    Agent responsible for provisioning and configuring infrastructure.
    """
    pass
```

## Message Format

All agent communication will use a standardized message format:

```json
{
  "message_id": "uuid-string",
  "sender_id": "sender-agent-id",
  "recipient_id": "recipient-agent-id",
  "conversation_id": "uuid-string",
  "timestamp": "ISO-8601-timestamp",
  "message_type": "request|response|notification|error",
  "content_type": "application/json",
  "content": {
    "action": "string-action-identifier",
    "parameters": {},
    "data": {}
  },
  "metadata": {
    "priority": "high|medium|low",
    "ttl": "time-to-live-in-seconds",
    "trace_id": "uuid-string",
    "source_workflow": "workflow-identifier"
  }
}
```

## Context Format

Execution context passed to agents follows this structure:

```json
{
  "workflow_id": "uuid-string",
  "execution_id": "uuid-string",
  "timestamp": "ISO-8601-timestamp",
  "caller_id": "caller-identifier",
  "parameters": {},
  "data": {},
  "credentials": {},
  "constraints": {
    "timeout": "timeout-in-seconds",
    "max_resources": {},
    "allowed_actions": []
  },
  "state": {
    "previous_results": {},
    "workflow_state": {}
  }
}
```

## Agent Registration and Discovery

Agents register with the system through a manifest file:

```json
{
  "agent_id": "unique-agent-identifier",
  "name": "Human-readable agent name",
  "description": "Detailed description of agent purpose and functionality",
  "version": "semver-version-string",
  "agent_type": "setup|operational",
  "implemented_interfaces": ["BaseAgent", "ObservableAgent", "..."],
  "capabilities": ["capability-1", "capability-2", "..."],
  "requirements": {
    "cpu": "cpu-requirements",
    "memory": "memory-requirements",
    "storage": "storage-requirements",
    "dependencies": ["dependency-1", "dependency-2"]
  },
  "configuration_schema": {
    "type": "object",
    "properties": {}
  },
  "communication": {
    "subscribed_topics": ["topic-1", "topic-2", "..."],
    "published_topics": ["topic-3", "topic-4", "..."]
  },
  "metadata": {
    "author": "Agent author or team",
    "documentation_url": "URL to agent documentation",
    "tags": ["tag-1", "tag-2", "..."]
  }
}
```

## Error Handling

Agents should raise standardized exceptions derived from base exception types:

```python
class AgentException(Exception):
    """Base exception for all agent-related errors."""
    pass

class AgentInitializationError(AgentException):
    """Raised when an agent fails to initialize."""
    pass

class AgentExecutionError(AgentException):
    """Raised when an agent encounters an error during execution."""
    pass

class AgentCommunicationError(AgentException):
    """Raised when there is an error in agent communication."""
    pass

class AgentConfigurationError(AgentException):
    """Raised when there is an error in agent configuration."""
    pass

class AgentResourceError(AgentException):
    """Raised when an agent cannot access required resources."""
    pass
```

## Implementation Guidelines

When implementing agents according to these interfaces:

1. **Single Responsibility Principle**: Each agent should have a focused, well-defined responsibility
2. **Fail Fast**: Validate inputs and prerequisites early to detect problems quickly
3. **Comprehensive Logging**: Log all significant actions and state changes
4. **Proper Resource Management**: Release resources in shutdown method
5. **Defensive Programming**: Handle edge cases and unexpected inputs gracefully
6. **Configuration Validation**: Validate all configuration before using it
7. **Status Transparency**: Provide accurate, up-to-date status information
8. **Efficient Communication**: Be concise in communication, only sending necessary data
9. **Timeout Handling**: Implement timeouts for all external operations
10. **Version Compatibility**: Document version compatibility requirements

## Mock Implementation Example

Below is a simplified mock implementation of a creative generation agent:

```python
class CreativeGenerationAgent(OperationalAgent, CommunicatingAgent, ObservableAgent, ConfigurableAgent):
    """
    Agent responsible for generating creative content for advertising campaigns.
    """
    
    def __init__(self):
        self.config = {}
        self.status = {"health": "initializing", "state": "idle"}
        self.metrics = {
            "creatives_generated": 0,
            "average_generation_time": 0,
            "success_rate": 1.0,
        }
        self.logs = []
        
    def initialize(self, config):
        try:
            # Validate configuration
            valid, errors = self.validate_config(config)
            if not valid:
                raise AgentConfigurationError(f"Invalid configuration: {errors}")
                
            # Store configuration
            self.config = config
            
            # Initialize resources
            self._setup_creative_engine()
            self._setup_monitoring()
            
            self.status["health"] = "healthy"
            return True
        except Exception as e:
            self.status["health"] = "error"
            self.logs.append({
                "level": "ERROR",
                "timestamp": datetime.now().isoformat(),
                "message": f"Initialization failed: {str(e)}"
            })
            return False
    
    def execute(self, context):
        try:
            self.status["state"] = "executing"
            
            # Extract parameters
            creative_type = context["parameters"].get("type", "text_ad")
            target_audience = context["parameters"].get("target_audience", {})
            brand_guidelines = context["parameters"].get("brand_guidelines", {})
            
            # Generate creative content
            start_time = time.time()
            creative_content = self._generate_creative(creative_type, target_audience, brand_guidelines)
            generation_time = time.time() - start_time
            
            # Update metrics
            self.metrics["creatives_generated"] += 1
            self.metrics["average_generation_time"] = (
                (self.metrics["average_generation_time"] * (self.metrics["creatives_generated"] - 1) + generation_time) 
                / self.metrics["creatives_generated"]
            )
            
            # Log success
            self.logs.append({
                "level": "INFO",
                "timestamp": datetime.now().isoformat(),
                "message": f"Generated {creative_type} creative in {generation_time:.2f}s"
            })
            
            self.status["state"] = "idle"
            return {
                "success": True,
                "creative": creative_content,
                "generation_time": generation_time,
                "metadata": {
                    "creative_type": creative_type,
                    "target_audience": target_audience,
                    "timestamp": datetime.now().isoformat()
                }
            }
        except Exception as e:
            self.status["state"] = "error"
            self.metrics["success_rate"] = (
                (self.metrics["success_rate"] * (self.metrics["creatives_generated"] - 1) + 0) 
                / self.metrics["creatives_generated"] if self.metrics["creatives_generated"] > 0 else 0
            )
            
            self.logs.append({
                "level": "ERROR",
                "timestamp": datetime.now().isoformat(),
                "message": f"Execution failed: {str(e)}"
            })
            
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    def shutdown(self):
        try:
            # Release resources
            self._cleanup_creative_engine()
            self._cleanup_monitoring()
            
            self.status["health"] = "shutdown"
            self.status["state"] = "terminated"
            return True
        except Exception as e:
            self.status["health"] = "error"
            self.logs.append({
                "level": "ERROR",
                "timestamp": datetime.now().isoformat(),
                "message": f"Shutdown failed: {str(e)}"
            })
            return False
    
    # OperationalAgent methods
    def pause(self):
        self.status["state"] = "paused"
        return True
        
    def resume(self):
        self.status["state"] = "idle"
        return True
        
    def should_execute(self, context):
        # Check if the requested creative type is supported
        requested_type = context["parameters"].get("type", "text_ad")
        return requested_type in self.config.get("supported_creative_types", ["text_ad"])
    
    # CommunicatingAgent methods
    def send_message(self, recipient_id, message_type, content):
        message_id = str(uuid.uuid4())
        # Logic to send message to the message bus or directly to recipient
        return message_id
        
    def receive_message(self, message):
        # Process incoming message
        if message["message_type"] == "request" and message["content"]["action"] == "generate_creative":
            # Handle creative generation request
            result = self.execute({"parameters": message["content"]["parameters"]})
            return {
                "success": True,
                "response": result
            }
        return {
            "success": False,
            "error": "Unsupported message type or action"
        }
        
    def list_subscribed_topics(self):
        return ["creative.generation.request", "system.config.update"]
    
    # ObservableAgent methods
    def get_metrics(self):
        return self.metrics
        
    def get_logs(self, start_time, end_time, level="INFO"):
        return [log for log in self.logs 
                if start_time <= datetime.fromisoformat(log["timestamp"]) <= end_time
                and log["level"] >= level]
                
    def get_traces(self, trace_id=None):
        # Simplified trace retrieval
        return []
    
    # ConfigurableAgent methods
    def update_config(self, config_updates):
        # Validate updates
        valid, errors = self.validate_config({**self.config, **config_updates})
        if not valid:
            return False
            
        # Apply updates
        self.config.update(config_updates)
        
        # Reinitialize if necessary
        if any(key in config_updates for key in ["creative_engine", "model_parameters"]):
            self._setup_creative_engine()
            
        return True
        
    def get_config_schema(self):
        return {
            "type": "object",
            "properties": {
                "supported_creative_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Types of creative content this agent can generate"
                },
                "creative_engine": {
                    "type": "string",
                    "enum": ["openai", "anthropic", "stable_diffusion", "internal"],
                    "description": "Engine to use for creative generation"
                },
                "model_parameters": {
                    "type": "object",
                    "description": "Parameters for the creative generation model"
                },
                "rate_limits": {
                    "type": "object",
                    "properties": {
                        "requests_per_minute": {"type": "number"},
                        "concurrent_requests": {"type": "number"}
                    },
                    "description": "Rate limiting configuration"
                }
            },
            "required": ["supported_creative_types", "creative_engine"]
        }
        
    def validate_config(self, config):
        # Check for required fields
        if "supported_creative_types" not in config:
            return False, ["Missing required field: supported_creative_types"]
            
        if "creative_engine" not in config:
            return False, ["Missing required field: creative_engine"]
            
        # Validate creative engine
        valid_engines = ["openai", "anthropic", "stable_diffusion", "internal"]
        if config["creative_engine"] not in valid_engines:
            return False, [f"Invalid creative_engine. Must be one of: {', '.join(valid_engines)}"]
            
        return True, []
    
    # Helper methods
    def _setup_creative_engine(self):
        # Initialize the creative generation engine based on configuration
        pass
        
    def _setup_monitoring(self):
        # Set up monitoring and telemetry
        pass
        
    def _cleanup_creative_engine(self):
        # Release resources associated with the creative engine
        pass
        
    def _cleanup_monitoring(self):
        # Cleanup monitoring resources
        pass
        
    def _generate_creative(self, creative_type, target_audience, brand_guidelines):
        # Logic to generate creative content
        # This would integrate with AI models like OpenAI or Anthropic
        return {
            "type": creative_type,
            "content": "Sample creative content would go here",
            "variations": ["Variation 1", "Variation 2"]
        }
    
    # BaseAgent methods
    def get_capabilities(self):
        return ["creative.generation.text", "creative.generation.image", "creative.variation"]
        
    def get_status(self):
        return {
            **self.status,
            "uptime": "calculate uptime here",
            "version": "1.0.0",
            "last_execution": "ISO timestamp of last execution",
            "configured_creative_types": self.config.get("supported_creative_types", [])
        }
```

## Next Steps

After defining these interfaces, we will:

1. Implement the core framework that supports these interfaces
2. Create base classes that provide common functionality
3. Develop test harnesses for validating agent implementations
4. Implement the agent registry for discovery and management
5. Create initial agent implementations for key system functions

## Conclusion

These interface definitions provide the foundation for our agent ecosystem. By adhering to these standards, we ensure that agents can be developed independently while still working together seamlessly within the larger system. The combination of clear interfaces, standardized messaging, and defined lifecycle management enables both flexibility and reliability in our agent-first architecture.