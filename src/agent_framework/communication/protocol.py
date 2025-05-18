# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps our AI agents talk to each other in a clear way. It's like creating
# rules for how they should send messages, where to send them, and how to deal with
# problems when messages don't get through.

# High School Explanation:
# This module implements a standardized communication protocol for agent-to-agent
# messaging. It provides message routing, delivery confirmation, error handling, and
# a publish-subscribe mechanism for efficient information sharing across the agent
# ecosystem.

"""
Protocol implementation for agent-to-agent communication.

This module provides concrete implementations of the agent communication protocol
based on the abstractions defined in the core module.
"""

from typing import Dict, List, Optional, Any, Set, Callable, Tuple, Union
from uuid import uuid4
import logging
from datetime import datetime
import threading
import queue
import time
import json
from enum import Enum
import traceback

from ..core.interfaces import CommunicatingAgent
from ..core.message import Message, MessageBroker, MessageType, MessagePriority
from ..core.base import AbstractCommunicatingAgent

logger = logging.getLogger(__name__)


class DeliveryStatus(Enum):
    """Status of message delivery."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"


class DeliveryConfirmation:
    """Confirmation of message delivery."""
    
    def __init__(self, message_id: str, recipient_id: str, 
                 status: DeliveryStatus = DeliveryStatus.PENDING):
        """Initialize a delivery confirmation.
        
        Args:
            message_id: ID of the message
            recipient_id: ID of the recipient
            status: Delivery status
        """
        self.message_id = message_id
        self.recipient_id = recipient_id
        self.status = status
        self.timestamp = datetime.now().isoformat()
        self.error_message = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "message_id": self.message_id,
            "recipient_id": self.recipient_id,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "error_message": self.error_message
        }
        
    def mark_delivered(self) -> None:
        """Mark the message as delivered."""
        self.status = DeliveryStatus.DELIVERED
        self.timestamp = datetime.now().isoformat()
        
    def mark_failed(self, error_message: str) -> None:
        """Mark the message as failed.
        
        Args:
            error_message: Error message explaining the failure
        """
        self.status = DeliveryStatus.FAILED
        self.timestamp = datetime.now().isoformat()
        self.error_message = error_message
        
    def mark_expired(self) -> None:
        """Mark the message as expired."""
        self.status = DeliveryStatus.EXPIRED
        self.timestamp = datetime.now().isoformat()
        self.error_message = "Message TTL expired"


class TopicSubscription:
    """Subscription to a topic in the publish-subscribe system."""
    
    def __init__(self, topic: str, subscriber_id: str, filter_condition: Optional[Dict[str, Any]] = None):
        """Initialize a topic subscription.
        
        Args:
            topic: Topic name
            subscriber_id: ID of the subscribing agent
            filter_condition: Optional condition for message filtering
        """
        self.topic = topic
        self.subscriber_id = subscriber_id
        self.filter_condition = filter_condition
        self.subscription_id = str(uuid4())
        self.created_at = datetime.now().isoformat()
        
    def matches(self, message_content: Dict[str, Any]) -> bool:
        """Check if a message matches the subscription filter.
        
        Args:
            message_content: Content of the message
            
        Returns:
            True if the message matches the filter, False otherwise
        """
        # If no filter, all messages match
        if not self.filter_condition:
            return True
            
        # Check each filter condition
        for key, value in self.filter_condition.items():
            if key not in message_content:
                return False
                
            # Simple equality check
            if message_content[key] != value:
                return False
                
        return True


class MessageQueue:
    """Thread-safe message queue for asynchronous message processing."""
    
    def __init__(self, max_size: int = 1000):
        """Initialize the message queue.
        
        Args:
            max_size: Maximum queue size
        """
        self.queue = queue.PriorityQueue(maxsize=max_size)
        self.lock = threading.Lock()
        
    def enqueue(self, message: Message) -> None:
        """Add a message to the queue.
        
        Args:
            message: Message to add
            
        Raises:
            queue.Full: If the queue is full
        """
        # Priority is based on message priority (lower value = higher priority)
        if message.priority == MessagePriority.HIGH:
            priority = 0
        elif message.priority == MessagePriority.MEDIUM:
            priority = 1
        else:
            priority = 2
            
        with self.lock:
            self.queue.put((priority, message))
            
    def dequeue(self) -> Optional[Message]:
        """Get the next message from the queue.
        
        Returns:
            The next message, or None if the queue is empty
        """
        try:
            with self.lock:
                if self.queue.empty():
                    return None
                priority, message = self.queue.get_nowait()
                return message
        except queue.Empty:
            return None
            
    def size(self) -> int:
        """Get the current size of the queue.
        
        Returns:
            Queue size
        """
        with self.lock:
            return self.queue.qsize()
            
    def is_empty(self) -> bool:
        """Check if the queue is empty.
        
        Returns:
            True if empty, False otherwise
        """
        with self.lock:
            return self.queue.empty()


class StandardCommunicationProtocol:
    """
    Standard implementation of the agent communication protocol.
    
    This class manages the communication flow between agents, providing
    message routing, delivery confirmation, and conversation tracking.
    """
    
    def __init__(self):
        """Initialize the communication protocol."""
        self.message_broker = MessageBroker()
        self.conversations = {}  # track ongoing conversations
        self.registered_agents: Dict[str, CommunicatingAgent] = {}
        self.subscriptions: Dict[str, List[TopicSubscription]] = {}  # topic -> subscriptions
        self.message_queue = MessageQueue()
        self.delivery_confirmations: Dict[str, DeliveryConfirmation] = {}  # message_id -> confirmation
        self.message_history: List[Message] = []
        self.topics: Dict[str, Dict[str, Any]] = {}  # topic -> metadata
        self.delivery_callbacks: Dict[str, Callable] = {}  # message_id -> callback
        self.background_thread = None
        self.running = False
        self.logger = logger
        
    def register_agent(self, agent: CommunicatingAgent) -> None:
        """Register an agent with the communication protocol.
        
        Args:
            agent: Agent to register
        """
        self.registered_agents[agent.id] = agent
        self.logger.info(f"Agent {agent.id} registered with communication protocol")
        
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the communication protocol.
        
        Args:
            agent_id: ID of the agent to unregister
        """
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]
            
            # Clean up subscriptions
            for topic, subscriptions in list(self.subscriptions.items()):
                self.subscriptions[topic] = [s for s in subscriptions if s.subscriber_id != agent_id]
                if not self.subscriptions[topic]:
                    del self.subscriptions[topic]
                    
            self.logger.info(f"Agent {agent_id} unregistered from communication protocol")
    
    def send_message(self, message: Message, callback: Optional[Callable] = None) -> str:
        """
        Send a message from one agent to another.
        
        Args:
            message: Message to send
            callback: Optional callback function to call when delivery is confirmed
            
        Returns:
            The message ID
        """
        if not message.conversation_id:
            message.conversation_id = str(uuid4())
            
        # Create a delivery confirmation
        confirmation = DeliveryConfirmation(message.message_id, message.recipient_id)
        self.delivery_confirmations[message.message_id] = confirmation
        
        # Store callback if provided
        if callback:
            self.delivery_callbacks[message.message_id] = callback
            
        # Add to message queue
        self.message_queue.enqueue(message)
        self.logger.debug(f"Message queued: {message.message_id} from {message.sender_id} to {message.recipient_id}")
        
        # Track conversation
        if message.conversation_id not in self.conversations:
            self.conversations[message.conversation_id] = {
                'started_at': datetime.now(),
                'participants': {message.sender_id, message.recipient_id},
                'messages': [message.message_id]
            }
        else:
            self.conversations[message.conversation_id]['messages'].append(message.message_id)
            self.conversations[message.conversation_id]['participants'].add(message.sender_id)
            self.conversations[message.conversation_id]['participants'].add(message.recipient_id)
            
        # Add to history
        self.message_history.append(message)
        
        return message.message_id
    
    def process_message_queue(self) -> int:
        """
        Process messages in the queue.
        
        Returns:
            Number of messages processed
        """
        processed_count = 0
        
        while True:
            message = self.message_queue.dequeue()
            if not message:
                break
                
            # Check if message has expired
            if message.is_expired():
                confirmation = self.delivery_confirmations.get(message.message_id)
                if confirmation:
                    confirmation.mark_expired()
                    self._handle_delivery_callback(message.message_id, confirmation)
                continue
                
            # Check if recipient agent is registered
            if message.recipient_id not in self.registered_agents:
                self.logger.warning(f"Recipient agent {message.recipient_id} not found for message {message.message_id}")
                
                # Mark delivery as failed
                confirmation = self.delivery_confirmations.get(message.message_id)
                if confirmation:
                    confirmation.mark_failed(f"Recipient agent {message.recipient_id} not found")
                    self._handle_delivery_callback(message.message_id, confirmation)
                continue
                
            # Deliver message to recipient
            try:
                recipient = self.registered_agents[message.recipient_id]
                recipient.receive_message(message)
                processed_count += 1
                self.logger.debug(f"Message delivered: {message.message_id} to {message.recipient_id}")
                
                # Mark delivery as successful
                confirmation = self.delivery_confirmations.get(message.message_id)
                if confirmation:
                    confirmation.mark_delivered()
                    self._handle_delivery_callback(message.message_id, confirmation)
                    
            except Exception as e:
                self.logger.error(f"Error delivering message {message.message_id}: {str(e)}")
                traceback.print_exc()
                
                # Mark delivery as failed
                confirmation = self.delivery_confirmations.get(message.message_id)
                if confirmation:
                    confirmation.mark_failed(str(e))
                    self._handle_delivery_callback(message.message_id, confirmation)
        
        return processed_count
    
    def _handle_delivery_callback(self, message_id: str, confirmation: DeliveryConfirmation) -> None:
        """Handle delivery callback for a message.
        
        Args:
            message_id: Message ID
            confirmation: Delivery confirmation
        """
        callback = self.delivery_callbacks.get(message_id)
        if callback:
            try:
                callback(confirmation)
            except Exception as e:
                self.logger.error(f"Error in delivery callback for message {message_id}: {str(e)}")
            
            # Remove callback after execution
            del self.delivery_callbacks[message_id]
    
    def get_conversation_history(self, conversation_id: str) -> List[Message]:
        """Get the full history of messages in a conversation.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            List of messages in the conversation
        """
        if conversation_id not in self.conversations:
            return []
            
        message_ids = self.conversations[conversation_id]['messages']
        return [msg for msg in self.message_history 
                if msg.message_id in message_ids]
    
    def register_topic(self, 
                      topic: str, 
                      description: str = "", 
                      metadata: Optional[Dict[str, Any]] = None) -> None:
        """Register a new topic in the pub/sub system.
        
        Args:
            topic: Topic name
            description: Topic description
            metadata: Additional topic metadata
        """
        if topic not in self.topics:
            self.topics[topic] = {
                'description': description,
                'created_at': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            # Initialize subscription list
            if topic not in self.subscriptions:
                self.subscriptions[topic] = []
                
            self.logger.info(f"Topic registered: {topic}")
    
    def subscribe(self, 
                 agent_id: str, 
                 topic: str, 
                 filter_condition: Optional[Dict[str, Any]] = None) -> str:
        """Subscribe an agent to a topic.
        
        Args:
            agent_id: ID of the subscribing agent
            topic: Topic to subscribe to
            filter_condition: Optional condition for message filtering
            
        Returns:
            Subscription ID
        """
        # Ensure topic exists
        if topic not in self.topics:
            self.register_topic(topic)
            
        # Create subscription
        subscription = TopicSubscription(topic, agent_id, filter_condition)
        
        # Add to subscription list
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append(subscription)
        
        self.logger.info(f"Agent {agent_id} subscribed to topic {topic}")
        return subscription.subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a topic.
        
        Args:
            subscription_id: ID of the subscription to cancel
            
        Returns:
            True if successful, False otherwise
        """
        # Find the subscription
        for topic, subscriptions in self.subscriptions.items():
            for i, subscription in enumerate(subscriptions):
                if subscription.subscription_id == subscription_id:
                    # Remove subscription
                    self.subscriptions[topic].pop(i)
                    
                    # Clean up empty subscription lists
                    if not self.subscriptions[topic]:
                        del self.subscriptions[topic]
                        
                    self.logger.info(f"Unsubscribed from topic {topic} with subscription {subscription_id}")
                    return True
                    
        return False
    
    def publish(self, 
               sender_id: str,
               topic: str, 
               content: Dict[str, Any],
               conversation_id: Optional[str] = None,
               priority: MessagePriority = MessagePriority.MEDIUM) -> Tuple[int, List[str]]:
        """Publish a message to a topic.
        
        Args:
            sender_id: ID of the publishing agent
            topic: Topic to publish to
            content: Message content
            conversation_id: Optional conversation ID
            priority: Message priority
            
        Returns:
            Tuple of (number of subscribers, list of message IDs)
        """
        # Ensure topic exists
        if topic not in self.topics:
            self.register_topic(topic)
            
        # Get subscriptions for this topic
        subscriptions = self.subscriptions.get(topic, [])
        message_ids = []
        
        # Create conversation ID if needed
        if not conversation_id:
            conversation_id = str(uuid4())
            
        # Prepare message content
        message_content = {
            "topic": topic,
            **content
        }
        
        # Send message to each subscriber
        for subscription in subscriptions:
            # Check if message matches subscription filter
            if not subscription.matches(content):
                continue
                
            # Create message
            message = Message(
                sender_id=sender_id,
                recipient_id=subscription.subscriber_id,
                message_type=MessageType.NOTIFICATION,
                content=message_content,
                conversation_id=conversation_id,
                priority=priority
            )
            
            # Send message
            message_id = self.send_message(message)
            message_ids.append(message_id)
            
        return len(message_ids), message_ids
    
    def get_delivery_status(self, message_id: str) -> Optional[DeliveryConfirmation]:
        """Get the delivery status for a message.
        
        Args:
            message_id: ID of the message
            
        Returns:
            Delivery confirmation, or None if not found
        """
        return self.delivery_confirmations.get(message_id)
    
    def list_topics(self) -> List[Dict[str, Any]]:
        """List all registered topics.
        
        Returns:
            List of topic information
        """
        return [
            {
                "name": topic,
                "description": info.get('description', ''),
                "created_at": info.get('created_at', ''),
                "subscribers": len(self.subscriptions.get(topic, [])),
                "metadata": info.get('metadata', {})
            }
            for topic, info in self.topics.items()
        ]
    
    def get_topic_subscribers(self, topic: str) -> List[Dict[str, Any]]:
        """Get all subscribers for a topic.
        
        Args:
            topic: Topic name
            
        Returns:
            List of subscriber information
        """
        if topic not in self.subscriptions:
            return []
            
        return [
            {
                "subscription_id": subscription.subscription_id,
                "subscriber_id": subscription.subscriber_id,
                "filter_condition": subscription.filter_condition,
                "created_at": subscription.created_at
            }
            for subscription in self.subscriptions[topic]
        ]
    
    def start_background_processing(self, interval: float = 0.1) -> None:
        """Start background thread for message processing.
        
        Args:
            interval: Processing interval in seconds
        """
        if self.background_thread and self.background_thread.is_alive():
            return
            
        self.running = True
        
        def processing_loop():
            while self.running:
                self.process_message_queue()
                time.sleep(interval)
                
        self.background_thread = threading.Thread(target=processing_loop, daemon=True)
        self.background_thread.start()
        self.logger.info("Background message processing started")
    
    def stop_background_processing(self) -> None:
        """Stop background message processing."""
        self.running = False
        if self.background_thread:
            self.background_thread.join(timeout=1.0)
            self.background_thread = None
            self.logger.info("Background message processing stopped")
    
    def clear_history(self, conversation_id: Optional[str] = None) -> None:
        """Clear message history.
        
        Args:
            conversation_id: Optional conversation ID to clear specific history
        """
        if conversation_id:
            if conversation_id in self.conversations:
                message_ids = self.conversations[conversation_id]['messages']
                self.message_history = [msg for msg in self.message_history 
                                      if msg.message_id not in message_ids]
                del self.conversations[conversation_id]
        else:
            self.message_history = []
            self.conversations = {}
            self.delivery_confirmations = {}
            self.delivery_callbacks = {}


class CommunicatingAgentImpl(AbstractCommunicatingAgent):
    """
    Concrete implementation of a communicating agent.
    
    This class provides a standard implementation of the CommunicatingAgent
    interface, allowing agents to send and receive messages.
    """
    
    def __init__(self, agent_id: str, name: str, protocol: StandardCommunicationProtocol):
        """Initialize a communicating agent.
        
        Args:
            agent_id: Agent ID
            name: Agent name
            protocol: Communication protocol to use
        """
        super().__init__(agent_id, name)
        self.protocol = protocol
        self.received_messages: List[Message] = []
        self.sent_messages: List[Message] = []
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.subscriptions: Dict[str, str] = {}  # topic -> subscription_id
        
        # Register with the protocol
        self.protocol.register_agent(self)
    
    def send_message(self, 
                    recipient_id: str, 
                    message_type: MessageType, 
                    content: Dict[str, Any], 
                    conversation_id: Optional[str] = None,
                    priority: MessagePriority = MessagePriority.MEDIUM,
                    ttl: Optional[int] = None) -> str:
        """
        Send a message to another agent.
        
        Args:
            recipient_id: ID of the recipient agent
            message_type: Type of message
            content: Message content
            conversation_id: Optional conversation ID
            priority: Message priority
            ttl: Time-to-live in seconds
            
        Returns:
            The message ID
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
        """Process a received message.
        
        Args:
            message: The received message
            
        Returns:
            True if handled successfully, False otherwise
        """
        if message.recipient_id != self.id:
            self.logger.warning(f"Agent {self.id} received message intended for {message.recipient_id}")
            return False
        
        self.received_messages.append(message)
        self.logger.debug(f"Agent {self.id} received message {message.message_id} from {message.sender_id}")
        
        # Process message using registered handlers
        if message.message_type in self.message_handlers:
            try:
                self.message_handlers[message.message_type](message)
                self.logger.debug(f"Message {message.message_id} handled by registered handler for {message.message_type}")
                return True
            except Exception as e:
                self.logger.error(f"Error handling message {message.message_id}: {str(e)}")
                return False
        else:
            # Default handling
            self.logger.debug(f"No handler for message type {message.message_type}, using default handling")
            return self._default_message_handler(message)
    
    def register_message_handler(self, message_type: MessageType, handler_func: Callable) -> None:
        """Register a handler function for a specific message type.
        
        Args:
            message_type: Message type to handle
            handler_func: Handler function
        """
        self.message_handlers[message_type] = handler_func
        self.logger.debug(f"Agent {self.id} registered handler for message type {message_type}")
    
    def _default_message_handler(self, message: Message) -> bool:
        """Default handler for messages without a specific registered handler.
        
        Args:
            message: The message to handle
            
        Returns:
            True if handled successfully, False otherwise
        """
        # Basic implementation - override in subclasses for more specific behavior
        self.logger.info(f"Agent {self.id} default handling of message {message.message_id} of type {message.message_type}")
        return True
    
    def get_received_messages(self, 
                            sender_id: Optional[str] = None,
                            message_type: Optional[MessageType] = None,
                            conversation_id: Optional[str] = None) -> List[Message]:
        """Get received messages, optionally filtered by criteria.
        
        Args:
            sender_id: Optional sender ID filter
            message_type: Optional message type filter
            conversation_id: Optional conversation ID filter
            
        Returns:
            List of matching messages
        """
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
    
    def subscribe_to_topic(self, 
                        topic: str, 
                        filter_condition: Optional[Dict[str, Any]] = None) -> str:
        """Subscribe to a topic.
        
        Args:
            topic: Topic to subscribe to
            filter_condition: Optional filter condition
            
        Returns:
            Subscription ID
        """
        subscription_id = self.protocol.subscribe(self.id, topic, filter_condition)
        self.subscriptions[topic] = subscription_id
        return subscription_id
    
    def unsubscribe_from_topic(self, topic: str) -> bool:
        """Unsubscribe from a topic.
        
        Args:
            topic: Topic to unsubscribe from
            
        Returns:
            True if successful, False otherwise
        """
        if topic not in self.subscriptions:
            return False
            
        subscription_id = self.subscriptions[topic]
        result = self.protocol.unsubscribe(subscription_id)
        
        if result:
            del self.subscriptions[topic]
            
        return result
    
    def publish_to_topic(self, 
                       topic: str, 
                       content: Dict[str, Any],
                       conversation_id: Optional[str] = None,
                       priority: MessagePriority = MessagePriority.MEDIUM) -> Tuple[int, List[str]]:
        """Publish a message to a topic.
        
        Args:
            topic: Topic to publish to
            content: Message content
            conversation_id: Optional conversation ID
            priority: Message priority
            
        Returns:
            Tuple of (number of subscribers, list of message IDs)
        """
        return self.protocol.publish(
            sender_id=self.id,
            topic=topic,
            content=content,
            conversation_id=conversation_id,
            priority=priority
        )
    
    def get_subscribed_topics(self) -> List[str]:
        """Get the list of topics this agent is subscribed to.
        
        Returns:
            List of topic names
        """
        return list(self.subscriptions.keys())


def create_request(sender_id: str, 
                  recipient_id: str, 
                  action: str,
                  parameters: Dict[str, Any] = None,
                  data: Dict[str, Any] = None,
                  conversation_id: Optional[str] = None,
                  priority: MessagePriority = MessagePriority.MEDIUM,
                  ttl: Optional[int] = None) -> Message:
    """
    Create a request message.
    
    Args:
        sender_id: ID of the sending agent
        recipient_id: ID of the recipient agent
        action: Requested action
        parameters: Action parameters
        data: Data payload
        conversation_id: Optional conversation ID
        priority: Message priority
        ttl: Time-to-live in seconds
        
    Returns:
        The created message
    """
    content = {
        "action": action,
        "parameters": parameters or {},
        "data": data or {}
    }
    
    return Message(
        sender_id=sender_id,
        recipient_id=recipient_id,
        message_type=MessageType.REQUEST,
        content=content,
        conversation_id=conversation_id,
        priority=priority,
        ttl=ttl
    )


def create_response(request_message: Message,
                   success: bool,
                   result: Dict[str, Any] = None,
                   error_message: Optional[str] = None) -> Message:
    """
    Create a response message to a request.
    
    Args:
        request_message: The original request message
        success: Whether the request was successful
        result: Result data for successful requests
        error_message: Error message for failed requests
        
    Returns:
        The created response message
    """
    content = {
        "success": success,
        "action": request_message.content.get("action", "unknown")
    }
    
    if success:
        content["result"] = result or {}
    else:
        content["error"] = error_message or "Unknown error"
        return request_message.create_response(content, error=True)
    
    return request_message.create_response(content)


def create_notification(sender_id: str,
                       recipient_id: str,
                       notification_type: str,
                       data: Dict[str, Any],
                       conversation_id: Optional[str] = None,
                       priority: MessagePriority = MessagePriority.MEDIUM) -> Message:
    """
    Create a notification message.
    
    Args:
        sender_id: ID of the sending agent
        recipient_id: ID of the recipient agent
        notification_type: Type of notification
        data: Notification data
        conversation_id: Optional conversation ID
        priority: Message priority
        
    Returns:
        The created message
    """
    content = {
        "notification_type": notification_type,
        "data": data
    }
    
    return Message(
        sender_id=sender_id,
        recipient_id=recipient_id,
        message_type=MessageType.NOTIFICATION,
        content=content,
        conversation_id=conversation_id,
        priority=priority
    )