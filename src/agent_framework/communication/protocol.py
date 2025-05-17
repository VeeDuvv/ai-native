"""
Protocol implementation for agent-to-agent communication.

This module provides concrete implementations of the agent communication protocol
based on the abstractions defined in the core module.
"""

from typing import Dict, List, Optional, Any, Set
from uuid import uuid4
import logging
from datetime import datetime

from ..core.interfaces import CommunicatingAgent
from ..core.message import Message, MessageBroker, MessageType, MessagePriority
from ..core.base import AbstractCommunicatingAgent

logger = logging.getLogger(__name__)

class StandardCommunicationProtocol:
    """
    Standard implementation of the agent communication protocol.
    
    This class manages the communication flow between agents, providing
    message routing, delivery confirmation, and conversation tracking.
    """
    
    def __init__(self):
        self.message_broker = MessageBroker()
        self.conversations = {}  # track ongoing conversations
        self.registered_agents: Dict[str, CommunicatingAgent] = {}
    
    def register_agent(self, agent: CommunicatingAgent) -> None:
        """Register an agent with the communication protocol."""
        self.registered_agents[agent.id] = agent
        logger.info(f"Agent {agent.id} registered with communication protocol")
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the communication protocol."""
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
            logger.info(f"Agent {agent_id} unregistered from communication protocol")
    
    def send_message(self, message: Message) -> str:
        """
        Send a message from one agent to another.
        
        Returns:
            str: The message ID
        """
        if not message.conversation_id:
            message.conversation_id = str(uuid4())
            
        self.message_broker.queue_message(message)
        logger.debug(f"Message queued: {message.id} from {message.sender_id} to {message.recipient_id}")
        
        # Track conversation
        if message.conversation_id not in self.conversations:
            self.conversations[message.conversation_id] = {
                'started_at': datetime.now(),
                'participants': {message.sender_id, message.recipient_id},
                'messages': [message.id]
            }
        else:
            self.conversations[message.conversation_id]['messages'].append(message.id)
            self.conversations[message.conversation_id]['participants'].add(message.sender_id)
            self.conversations[message.conversation_id]['participants'].add(message.recipient_id)
        
        return message.id
    
    def process_message_queue(self) -> int:
        """
        Process all messages in the queue.
        
        Returns:
            int: Number of messages processed
        """
        processed_count = 0
        
        while True:
            message = self.message_broker.get_next_message()
            if not message:
                break
                
            if message.recipient_id not in self.registered_agents:
                logger.warning(f"Recipient agent {message.recipient_id} not found for message {message.id}")
                continue
                
            recipient = self.registered_agents[message.recipient_id]
            recipient.receive_message(message)
            processed_count += 1
            logger.debug(f"Message delivered: {message.id} to {message.recipient_id}")
        
        return processed_count
    
    def get_conversation_history(self, conversation_id: str) -> List[Message]:
        """Get the full history of messages in a conversation."""
        if conversation_id not in self.conversations:
            return []
            
        message_ids = self.conversations[conversation_id]['messages']
        return [self.message_broker.get_message_by_id(msg_id) for msg_id in message_ids 
                if self.message_broker.get_message_by_id(msg_id) is not None]


class CommunicatingAgentImpl(AbstractCommunicatingAgent):
    """
    Concrete implementation of a communicating agent.
    
    This class provides a standard implementation of the CommunicatingAgent
    interface, allowing agents to send and receive messages.
    """
    
    def __init__(self, agent_id: str, name: str, protocol: StandardCommunicationProtocol):
        super().__init__(agent_id, name)
        self.protocol = protocol
        self.received_messages: List[Message] = []
        self.sent_messages: List[Message] = []
        self.message_handlers: Dict[MessageType, callable] = {}
        
        # Register with the protocol
        self.protocol.register_agent(self)
    
    def send_message(self, recipient_id: str, message_type: MessageType, 
                    content: Dict[str, Any], conversation_id: Optional[str] = None,
                    priority: MessagePriority = MessagePriority.MEDIUM,
                    ttl: Optional[int] = None) -> str:
        """
        Send a message to another agent.
        
        Returns:
            str: The message ID
        """
        message = Message(
            sender_id=self.id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            conversation_id=conversation_id,
            priority=priority,
            ttl=ttl
        )
        
        self.sent_messages.append(message)
        return self.protocol.send_message(message)
    
    def receive_message(self, message: Message) -> bool:
        """Process a received message."""
        if message.recipient_id != self.id:
            logger.warning(f"Agent {self.id} received message intended for {message.recipient_id}")
            return False
        
        self.received_messages.append(message)
        logger.debug(f"Agent {self.id} received message {message.id} from {message.sender_id}")
        
        # Process message using registered handlers
        if message.message_type in self.message_handlers:
            try:
                self.message_handlers[message.message_type](message)
                logger.debug(f"Message {message.id} handled by registered handler for {message.message_type}")
                return True
            except Exception as e:
                logger.error(f"Error handling message {message.id}: {str(e)}")
                return False
        else:
            # Default handling
            logger.debug(f"No handler for message type {message.message_type}, using default handling")
            return self._default_message_handler(message)
    
    def register_message_handler(self, message_type: MessageType, handler_func: callable) -> None:
        """Register a handler function for a specific message type."""
        self.message_handlers[message_type] = handler_func
        logger.debug(f"Agent {self.id} registered handler for message type {message_type}")
    
    def _default_message_handler(self, message: Message) -> bool:
        """Default handler for messages without a specific registered handler."""
        # Basic implementation - override in subclasses for more specific behavior
        logger.info(f"Agent {self.id} default handling of message {message.id} of type {message.message_type}")
        return True
    
    def get_received_messages(self, sender_id: Optional[str] = None,
                             message_type: Optional[MessageType] = None,
                             conversation_id: Optional[str] = None) -> List[Message]:
        """Get received messages, optionally filtered by criteria."""
        filtered_messages = self.received_messages
        
        if sender_id:
            filtered_messages = [m for m in filtered_messages if m.sender_id == sender_id]
        
        if message_type:
            filtered_messages = [m for m in filtered_messages if m.message_type == message_type]
        
        if conversation_id:
            filtered_messages = [m for m in filtered_messages if m.conversation_id == conversation_id]
        
        return filtered_messages
    
    def clear_message_history(self) -> None:
        """Clear the agent's message history."""
        self.received_messages = []
        self.sent_messages = []