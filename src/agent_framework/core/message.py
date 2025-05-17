# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file defines how our AI helpers send messages to each other. It's like 
# creating special envelopes that contain information in a way that all the 
# helpers can understand.

# High School Explanation:
# This module defines the structure and validation rules for messages exchanged
# between agents. It ensures consistent formatting, proper addressing, and
# reliable delivery of information across the agent ecosystem.

"""
Message definitions for the Agent Framework.

This module provides the structure and utilities for messages exchanged between
agents, including message formatting, validation, and routing.
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional


class MessageType(Enum):
    """
    Enumeration of standard message types used in agent communication.
    """
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class MessagePriority(Enum):
    """
    Enumeration of message priority levels.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Message:
    """
    Represents a message exchanged between agents.
    
    This class provides a structured format for inter-agent communication,
    ensuring consistent message formatting and validation.
    """
    
    def __init__(self, sender_id: str, recipient_id: str, 
                message_type: MessageType, content: Dict[str, Any],
                conversation_id: Optional[str] = None,
                priority: MessagePriority = MessagePriority.MEDIUM,
                ttl: Optional[int] = None):
        """
        Initialize a new message.
        
        Args:
            sender_id: Identifier of the sending agent
            recipient_id: Identifier of the recipient agent
            message_type: Type of message being sent
            content: Dictionary containing the message content
            conversation_id: Optional ID for grouping related messages
            priority: Message priority level
            ttl: Time-to-live in seconds (for message expiration)
        """
        self.message_id = str(uuid.uuid4())
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
        self.message_type = message_type
        self.content_type = "application/json"
        self.content = content
        self.priority = priority
        self.ttl = ttl
        self.trace_id = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the message to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the message
        """
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "conversation_id": self.conversation_id,
            "timestamp": self.timestamp,
            "message_type": self.message_type.value if isinstance(self.message_type, MessageType) else self.message_type,
            "content_type": self.content_type,
            "content": self.content,
            "metadata": {
                "priority": self.priority.value if isinstance(self.priority, MessagePriority) else self.priority,
                "ttl": self.ttl,
                "trace_id": self.trace_id
            }
        }
    
    def to_json(self) -> str:
        """
        Convert the message to a JSON string.
        
        Returns:
            str: JSON representation of the message
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        Create a message from a dictionary.
        
        Args:
            data: Dictionary containing message data
            
        Returns:
            Message: New message instance
        """
        # Create basic message
        message = cls(
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            message_type=MessageType(data["message_type"]) if data["message_type"] in [e.value for e in MessageType] else data["message_type"],
            content=data["content"]
        )
        
        # Set additional fields
        message.message_id = data["message_id"]
        message.conversation_id = data["conversation_id"]
        message.timestamp = data["timestamp"]
        message.content_type = data["content_type"]
        
        # Set metadata
        metadata = data.get("metadata", {})
        if "priority" in metadata:
            message.priority = MessagePriority(metadata["priority"]) if metadata["priority"] in [e.value for e in MessagePriority] else metadata["priority"]
        if "ttl" in metadata:
            message.ttl = metadata["ttl"]
        if "trace_id" in metadata:
            message.trace_id = metadata["trace_id"]
        
        return message
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """
        Create a message from a JSON string.
        
        Args:
            json_str: JSON string containing message data
            
        Returns:
            Message: New message instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def create_response(self, content: Dict[str, Any], 
                        error: bool = False) -> 'Message':
        """
        Create a response to this message.
        
        Args:
            content: Content for the response
            error: Whether this is an error response
            
        Returns:
            Message: Response message
        """
        message_type = MessageType.ERROR if error else MessageType.RESPONSE
        
        return Message(
            sender_id=self.recipient_id,
            recipient_id=self.sender_id,
            message_type=message_type,
            content=content,
            conversation_id=self.conversation_id,
            priority=self.priority
        )
    
    def is_expired(self) -> bool:
        """
        Check if the message has expired based on TTL.
        
        Returns:
            bool: True if the message has expired, False otherwise
        """
        if not self.ttl:
            return False
        
        # Parse timestamp
        message_time = datetime.fromisoformat(self.timestamp)
        
        # Check if current time exceeds message time + TTL
        current_time = datetime.now()
        expiration_time = message_time.timestamp() + self.ttl
        
        return current_time.timestamp() > expiration_time


class MessageValidationError(Exception):
    """Exception raised for message validation errors."""
    pass


class MessageValidator:
    """
    Validates messages to ensure they meet system requirements.
    """
    
    @staticmethod
    def validate(message: Message) -> bool:
        """
        Validate a message.
        
        Args:
            message: Message to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            MessageValidationError: If validation fails
        """
        # Check required fields
        if not message.sender_id:
            raise MessageValidationError("Missing sender_id")
        
        if not message.recipient_id:
            raise MessageValidationError("Missing recipient_id")
        
        # Check message type
        if isinstance(message.message_type, MessageType):
            # Enum instance - valid
            pass
        elif isinstance(message.message_type, str):
            # String - check if valid enum value
            if message.message_type not in [e.value for e in MessageType]:
                raise MessageValidationError(f"Invalid message_type: {message.message_type}")
        else:
            raise MessageValidationError(f"Invalid message_type format: {type(message.message_type)}")
        
        # Check content
        if not isinstance(message.content, dict):
            raise MessageValidationError("Content must be a dictionary")
        
        # Check action for request type
        if message.message_type == MessageType.REQUEST or message.message_type == "request":
            if "action" not in message.content:
                raise MessageValidationError("Request messages must have an 'action' in content")
        
        return True


class MessageBroker:
    """
    Facilitates the routing and delivery of messages between agents.
    
    This class provides mechanisms for sending messages, subscribing to topics,
    and handling message delivery within the agent ecosystem.
    """
    
    def __init__(self):
        """
        Initialize the message broker.
        """
        self.subscriptions = {}  # topic -> list of agent_ids
        self.agents = {}  # agent_id -> agent object
        self.topics = {}  # topic -> description
        self.message_history = []
    
    def register_agent(self, agent_id: str, agent_obj):
        """
        Register an agent with the broker.
        
        Args:
            agent_id: Agent identifier
            agent_obj: Agent object with receive_message method
        """
        self.agents[agent_id] = agent_obj
    
    def register_topic(self, topic: str, description: str = ""):
        """
        Register a message topic.
        
        Args:
            topic: Topic identifier
            description: Topic description
        """
        self.topics[topic] = description
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
    
    def subscribe(self, agent_id: str, topic: str):
        """
        Subscribe an agent to a topic.
        
        Args:
            agent_id: Agent identifier
            topic: Topic to subscribe to
        """
        # Create topic if it doesn't exist
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
            self.topics[topic] = ""
        
        # Add agent to subscription list if not already present
        if agent_id not in self.subscriptions[topic]:
            self.subscriptions[topic].append(agent_id)
    
    def unsubscribe(self, agent_id: str, topic: str):
        """
        Unsubscribe an agent from a topic.
        
        Args:
            agent_id: Agent identifier
            topic: Topic to unsubscribe from
        """
        if topic in self.subscriptions and agent_id in self.subscriptions[topic]:
            self.subscriptions[topic].remove(agent_id)
    
    def list_topics(self) -> List[Dict[str, Any]]:
        """
        List all available topics.
        
        Returns:
            List[Dict[str, Any]]: List of topics with descriptions and subscriber counts
        """
        return [
            {
                "topic": topic,
                "description": description,
                "subscribers": len(self.subscriptions.get(topic, []))
            }
            for topic, description in self.topics.items()
        ]
    
    def send_message(self, message: Message) -> bool:
        """
        Send a message to a specific agent.
        
        Args:
            message: Message to send
            
        Returns:
            bool: True if message was delivered, False otherwise
        """
        # Validate message
        try:
            MessageValidator.validate(message)
        except MessageValidationError as e:
            print(f"Message validation failed: {str(e)}")
            return False
        
        # Add to history
        self.message_history.append({
            "timestamp": datetime.now().isoformat(),
            "message": message.to_dict()
        })
        
        # Check if recipient is registered
        recipient_id = message.recipient_id
        if recipient_id not in self.agents:
            print(f"Unknown recipient: {recipient_id}")
            return False
        
        # Deliver message
        try:
            self.agents[recipient_id].receive_message(message.to_dict())
            return True
        except Exception as e:
            print(f"Error delivering message: {str(e)}")
            return False
    
    def publish(self, topic: str, sender_id: str, content: Dict[str, Any],
               message_type: MessageType = MessageType.NOTIFICATION) -> int:
        """
        Publish a message to a topic.
        
        Args:
            topic: Topic to publish to
            sender_id: Identifier of the sending agent
            content: Message content
            message_type: Type of message
            
        Returns:
            int: Number of subscribers the message was delivered to
        """
        # Check if topic exists
        if topic not in self.subscriptions:
            print(f"Unknown topic: {topic}")
            return 0
        
        # Create conversation ID for this publication
        conversation_id = str(uuid.uuid4())
        
        # Get subscribers
        subscribers = self.subscriptions[topic]
        delivered_count = 0
        
        # Create and send message to each subscriber
        for agent_id in subscribers:
            message = Message(
                sender_id=sender_id,
                recipient_id=agent_id,
                message_type=message_type,
                content={"topic": topic, **content},
                conversation_id=conversation_id
            )
            
            if self.send_message(message):
                delivered_count += 1
        
        return delivered_count


def create_request(sender_id: str, recipient_id: str, action: str, 
                  parameters: Dict[str, Any] = None, 
                  data: Dict[str, Any] = None,
                  conversation_id: Optional[str] = None,
                  priority: MessagePriority = MessagePriority.MEDIUM) -> Message:
    """
    Create a request message.
    
    Args:
        sender_id: Identifier of the sending agent
        recipient_id: Identifier of the recipient agent
        action: Requested action
        parameters: Parameters for the action
        data: Data payload for the action
        conversation_id: Optional ID for grouping related messages
        priority: Message priority level
        
    Returns:
        Message: Newly created request message
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
        priority=priority
    )


def create_response(request_message: Message, success: bool, 
                   result: Dict[str, Any] = None,
                   error_message: str = None) -> Message:
    """
    Create a response message for a request.
    
    Args:
        request_message: Original request message
        success: Whether the request was successful
        result: Result data (for successful requests)
        error_message: Error message (for failed requests)
        
    Returns:
        Message: Newly created response message
    """
    content = {
        "success": success,
        "action": request_message.content.get("action")
    }
    
    if success:
        content["result"] = result or {}
    else:
        content["error"] = error_message or "Unknown error"
        return request_message.create_response(content, error=True)
    
    return request_message.create_response(content)