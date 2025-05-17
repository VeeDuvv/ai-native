"""
Tests for the agent communication protocol.
"""

import pytest
from typing import Dict, Any

from src.agent_framework.core.message import MessageType, MessagePriority
from src.agent_framework.communication.protocol import StandardCommunicationProtocol, CommunicatingAgentImpl


# Define test message types
class TestMessageType(MessageType):
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    NOTIFICATION = "NOTIFICATION"


class TestAgent(CommunicatingAgentImpl):
    """Agent implementation for testing."""
    
    def __init__(self, agent_id: str, protocol: StandardCommunicationProtocol):
        super().__init__(agent_id, f"Test Agent {agent_id}", protocol)
        self.received_request_count = 0
        self.received_response_count = 0
        self.received_notification_count = 0
        
        # Register message handlers
        self.register_message_handler(TestMessageType.REQUEST, self._handle_request)
        self.register_message_handler(TestMessageType.RESPONSE, self._handle_response)
        self.register_message_handler(TestMessageType.NOTIFICATION, self._handle_notification)
    
    def _handle_request(self, message: Dict[str, Any]) -> None:
        """Handle test request messages."""
        self.received_request_count += 1
        
        # Automatically respond to requests
        self.send_message(
            recipient_id=message.sender_id,
            message_type=TestMessageType.RESPONSE,
            content={"response_to": message.id, "status": "success"},
            conversation_id=message.conversation_id
        )
    
    def _handle_response(self, message: Dict[str, Any]) -> None:
        """Handle test response messages."""
        self.received_response_count += 1
    
    def _handle_notification(self, message: Dict[str, Any]) -> None:
        """Handle test notification messages."""
        self.received_notification_count += 1


@pytest.fixture
def communication_protocol():
    """Create a fresh communication protocol instance for testing."""
    return StandardCommunicationProtocol()


@pytest.fixture
def test_agents(communication_protocol):
    """Create test agents with the communication protocol."""
    agent_a = TestAgent("agent-a", communication_protocol)
    agent_b = TestAgent("agent-b", communication_protocol)
    agent_c = TestAgent("agent-c", communication_protocol)
    
    return {
        "agent_a": agent_a,
        "agent_b": agent_b,
        "agent_c": agent_c
    }


def test_agent_registration(communication_protocol):
    """Test registering and unregistering agents with the protocol."""
    agent = TestAgent("test-agent", communication_protocol)
    
    # Agent should be registered during initialization
    assert "test-agent" in communication_protocol.registered_agents
    
    # Test unregistering
    communication_protocol.unregister_agent("test-agent")
    assert "test-agent" not in communication_protocol.registered_agents


def test_send_message(test_agents, communication_protocol):
    """Test sending a message between agents."""
    agent_a = test_agents["agent_a"]
    agent_b = test_agents["agent_b"]
    
    # Send message from agent A to agent B
    message_id = agent_a.send_message(
        recipient_id=agent_b.id,
        message_type=TestMessageType.REQUEST,
        content={"test_key": "test_value"}
    )
    
    # Message should be queued but not delivered yet
    assert len(agent_a.sent_messages) == 1
    assert len(agent_b.received_messages) == 0
    
    # Process messages
    processed = communication_protocol.process_message_queue()
    assert processed == 1
    
    # Agent B should have received the message
    assert len(agent_b.received_messages) == 1
    assert agent_b.received_messages[0].id == message_id
    assert agent_b.received_request_count == 1
    
    # Process any automatic responses
    processed = communication_protocol.process_message_queue()
    assert processed == 1
    
    # Agent A should have received a response
    assert len(agent_a.received_messages) == 1
    assert agent_a.received_response_count == 1


def test_conversation_tracking(test_agents, communication_protocol):
    """Test tracking conversations between agents."""
    agent_a = test_agents["agent_a"]
    agent_b = test_agents["agent_b"]
    
    # Start a conversation
    message_id = agent_a.send_message(
        recipient_id=agent_b.id,
        message_type=TestMessageType.REQUEST,
        content={"subject": "Test conversation"}
    )
    
    # Process messages
    communication_protocol.process_message_queue()
    
    # Get the conversation ID from the sent message
    conversation_id = agent_a.sent_messages[0].conversation_id
    
    # Process responses
    communication_protocol.process_message_queue()
    
    # Check conversation tracking
    assert conversation_id in communication_protocol.conversations
    conversation = communication_protocol.conversations[conversation_id]
    
    # Conversation should have two participants
    assert len(conversation["participants"]) == 2
    assert agent_a.id in conversation["participants"]
    assert agent_b.id in conversation["participants"]
    
    # Conversation should have two messages (request and response)
    assert len(conversation["messages"]) == 2
    
    # Test getting conversation history
    history = communication_protocol.get_conversation_history(conversation_id)
    assert len(history) == 2
    assert history[0].sender_id == agent_a.id
    assert history[1].sender_id == agent_b.id


def test_message_priority(test_agents, communication_protocol):
    """Test message priority handling."""
    agent_a = test_agents["agent_a"]
    agent_b = test_agents["agent_b"]
    
    # Send messages with different priorities
    agent_a.send_message(
        recipient_id=agent_b.id,
        message_type=TestMessageType.NOTIFICATION,
        content={"priority": "low"},
        priority=MessagePriority.LOW
    )
    
    agent_a.send_message(
        recipient_id=agent_b.id,
        message_type=TestMessageType.NOTIFICATION,
        content={"priority": "high"},
        priority=MessagePriority.HIGH
    )
    
    # Process messages - high priority should be processed first
    communication_protocol.process_message_queue()
    
    # Both messages should be delivered
    assert agent_b.received_notification_count == 2


def test_message_filtering(test_agents, communication_protocol):
    """Test filtering messages by criteria."""
    agent_a = test_agents["agent_a"]
    agent_b = test_agents["agent_b"]
    agent_c = test_agents["agent_c"]
    
    # Send various messages
    agent_a.send_message(
        recipient_id=agent_b.id,
        message_type=TestMessageType.REQUEST,
        content={"request": "data"}
    )
    
    agent_c.send_message(
        recipient_id=agent_b.id,
        message_type=TestMessageType.NOTIFICATION,
        content={"notification": "update"}
    )
    
    # Process messages
    communication_protocol.process_message_queue()
    
    # Test filtering by sender
    sender_filtered = agent_b.get_received_messages(sender_id=agent_a.id)
    assert len(sender_filtered) == 1
    assert sender_filtered[0].sender_id == agent_a.id
    
    # Test filtering by message type
    type_filtered = agent_b.get_received_messages(message_type=TestMessageType.NOTIFICATION)
    assert len(type_filtered) == 1
    assert type_filtered[0].message_type == TestMessageType.NOTIFICATION