# Agent Communication Protocol

This module implements the communication protocol for the AI-native advertising agency platform, enabling agents to exchange messages and coordinate their activities.

## Overview

The agent communication protocol provides:

1. A standardized message format for agent-to-agent communication
2. Message routing and delivery between agents
3. Conversation tracking across multiple messages
4. Priority-based message processing
5. Message filtering and retrieval capabilities

## Key Components

### StandardCommunicationProtocol

The central class that manages communication between agents. It provides:

- Agent registration and message routing
- Message queue management
- Conversation tracking and history retrieval
- Priority-based message processing

```python
# Create a communication protocol
protocol = StandardCommunicationProtocol()

# Register agents with the protocol
protocol.register_agent(agent)

# Process messages in the queue
processed_count = protocol.process_message_queue()

# Get conversation history
messages = protocol.get_conversation_history(conversation_id)
```

### CommunicatingAgentImpl

A concrete implementation of the `CommunicatingAgent` interface that provides:

- Sending messages to other agents
- Receiving and processing incoming messages
- Message handler registration for specific message types
- Message filtering and retrieval capabilities

```python
# Create a communicating agent
agent = CommunicatingAgentImpl(agent_id, name, protocol)

# Send a message
agent.send_message(
    recipient_id=recipient_id,
    message_type=MessageType.REQUEST,
    content={"key": "value"}
)

# Register a message handler
agent.register_message_handler(
    MessageType.REQUEST,
    handler_function
)

# Filter received messages
messages = agent.get_received_messages(
    sender_id=sender_id,
    message_type=MessageType.RESPONSE
)
```

## Ad Agency Implementation

The module includes specialized implementations for the AI-native advertising agency domain:

### AgencyMessageType

Defines domain-specific message types for the advertising agency:

- Campaign management: `CAMPAIGN_REQUEST`, `CAMPAIGN_APPROVED`, etc.
- Creative production: `CREATIVE_REQUEST`, `CREATIVE_DELIVERY`, etc.
- Audience targeting: `AUDIENCE_REQUEST`, `AUDIENCE_DELIVERY`
- Media planning: `MEDIA_PLAN_REQUEST`, `MEDIA_PLAN_DELIVERY`, etc.
- Performance reporting: `PERFORMANCE_REQUEST`, `PERFORMANCE_REPORT`, etc.

### CampaignManagerAgent

Agent responsible for managing the overall campaign lifecycle, coordinating between various specialized agents:

- Initiates campaigns and tracks their progress
- Coordinates with creative, audience, media, and analytics agents
- Manages the campaign workflow from initiation to launch
- Tracks campaign components and their status

### CreativeAgent

Agent responsible for creative development:

- Generates creative assets based on campaign briefs
- Processes creative requests and delivers assets
- Handles feedback and revisions

## Usage Examples

The module includes several examples demonstrating how to use the protocol:

1. **Basic Example**: A simple example showing communication between two agents
2. **Ad Agency Example**: A more complex example demonstrating the full advertising campaign workflow
3. **Custom Example**: An example with multiple specialized creative agents

To run the examples, use the demo script:

```bash
python src/agent_framework/communication/demo.py
```

## Testing

The module includes comprehensive unit tests:

- `test_protocol.py`: Tests for the core protocol functionality
- `test_ad_agency.py`: Tests for the advertising agency implementation

Run the tests using pytest:

```bash
pytest tests/unit/agent_framework/communication/
```

## Integration with Other Components

This protocol integrates with:

1. **Agent Framework Core**: Uses interfaces and base classes from the core module
2. **API Layer**: Can be integrated with the API controllers for campaign, creative, and media management
3. **TISIT Knowledge Repository**: Will integrate with the knowledge sharing components (future development)

## Future Enhancements

Planned enhancements for the communication protocol:

1. **Agent Discovery**: Dynamic agent discovery and capability advertisement
2. **Security and Authentication**: Message signing and agent authentication
3. **Message Persistence**: Durable storage for messages and conversations
4. **Distributed Processing**: Support for distributed message processing
5. **Observability**: Integration with the agent observability framework