# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file creates an AI helper that talks to clients about their advertising campaigns.
# It sends updates, asks for approval on new ideas, and helps clients understand
# how their ads are performing.

# High School Explanation:
# This module implements a Client Communication Agent that manages interactions between
# the automated ad system and human clients. It handles status updates, approval workflows,
# feedback collection, and notification management to maintain effective client relationships.

import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
import threading
import time

from ..core.base import BaseProcessAwareAgent
from ..core.message import Message, MessageType
from ..core.process import ProcessActivity, ProcessContext
from ..communication.protocol import StandardCommunicationProtocol, DeliveryStatus, MessagePriority

logger = logging.getLogger(__name__)

class ClientMessage:
    """Represents a message to or from a client with tracking information."""
    
    def __init__(self, 
                 message_id: str,
                 client_id: str,
                 campaign_id: Optional[str],
                 message_type: str,
                 subject: str,
                 content: str,
                 attachments: Optional[List[Dict[str, Any]]] = None,
                 created_at: Optional[str] = None,
                 status: str = "pending",
                 direction: str = "outbound",
                 priority: str = "normal",
                 metadata: Optional[Dict[str, Any]] = None):
        self.message_id = message_id
        self.client_id = client_id
        self.campaign_id = campaign_id
        self.message_type = message_type
        self.subject = subject
        self.content = content
        self.attachments = attachments or []
        self.created_at = created_at or datetime.now().isoformat()
        self.status = status
        self.direction = direction  # outbound or inbound
        self.priority = priority
        self.metadata = metadata or {}
        self.response: Optional[Dict[str, Any]] = None
        self.sent_at: Optional[str] = None
        self.delivered_at: Optional[str] = None
        self.read_at: Optional[str] = None
        self.responded_at: Optional[str] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary representation."""
        return {
            "message_id": self.message_id,
            "client_id": self.client_id,
            "campaign_id": self.campaign_id,
            "message_type": self.message_type,
            "subject": self.subject,
            "content": self.content,
            "attachments": self.attachments,
            "created_at": self.created_at,
            "status": self.status,
            "direction": self.direction,
            "priority": self.priority,
            "metadata": self.metadata,
            "response": self.response,
            "sent_at": self.sent_at,
            "delivered_at": self.delivered_at,
            "read_at": self.read_at,
            "responded_at": self.responded_at
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClientMessage':
        """Create a ClientMessage instance from dictionary data."""
        message = cls(
            message_id=data["message_id"],
            client_id=data["client_id"],
            campaign_id=data.get("campaign_id"),
            message_type=data["message_type"],
            subject=data["subject"],
            content=data["content"],
            attachments=data.get("attachments", []),
            created_at=data.get("created_at"),
            status=data.get("status", "pending"),
            direction=data.get("direction", "outbound"),
            priority=data.get("priority", "normal"),
            metadata=data.get("metadata", {})
        )
        
        # Set additional fields if present
        if "response" in data:
            message.response = data["response"]
        if "sent_at" in data:
            message.sent_at = data["sent_at"]
        if "delivered_at" in data:
            message.delivered_at = data["delivered_at"]
        if "read_at" in data:
            message.read_at = data["read_at"]
        if "responded_at" in data:
            message.responded_at = data["responded_at"]
            
        return message


class ApprovalRequest:
    """Represents a request for client approval with tracking information."""
    
    def __init__(self, 
                 request_id: str,
                 client_id: str,
                 campaign_id: str,
                 request_type: str,
                 title: str,
                 description: str,
                 items_for_approval: List[Dict[str, Any]],
                 created_at: Optional[str] = None,
                 deadline: Optional[str] = None,
                 status: str = "pending",
                 priority: str = "normal",
                 metadata: Optional[Dict[str, Any]] = None):
        self.request_id = request_id
        self.client_id = client_id
        self.campaign_id = campaign_id
        self.request_type = request_type
        self.title = title
        self.description = description
        self.items_for_approval = items_for_approval
        self.created_at = created_at or datetime.now().isoformat()
        self.deadline = deadline
        self.status = status
        self.priority = priority
        self.metadata = metadata or {}
        self.sent_at: Optional[str] = None
        self.viewed_at: Optional[str] = None
        self.responded_at: Optional[str] = None
        self.decision: Optional[str] = None
        self.decision_details: Optional[Dict[str, Any]] = None
        self.feedback: Optional[str] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert approval request to dictionary representation."""
        return {
            "request_id": self.request_id,
            "client_id": self.client_id,
            "campaign_id": self.campaign_id,
            "request_type": self.request_type,
            "title": self.title,
            "description": self.description,
            "items_for_approval": self.items_for_approval,
            "created_at": self.created_at,
            "deadline": self.deadline,
            "status": self.status,
            "priority": self.priority,
            "metadata": self.metadata,
            "sent_at": self.sent_at,
            "viewed_at": self.viewed_at,
            "responded_at": self.responded_at,
            "decision": self.decision,
            "decision_details": self.decision_details,
            "feedback": self.feedback
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ApprovalRequest':
        """Create an ApprovalRequest instance from dictionary data."""
        request = cls(
            request_id=data["request_id"],
            client_id=data["client_id"],
            campaign_id=data["campaign_id"],
            request_type=data["request_type"],
            title=data["title"],
            description=data["description"],
            items_for_approval=data["items_for_approval"],
            created_at=data.get("created_at"),
            deadline=data.get("deadline"),
            status=data.get("status", "pending"),
            priority=data.get("priority", "normal"),
            metadata=data.get("metadata", {})
        )
        
        # Set additional fields if present
        if "sent_at" in data:
            request.sent_at = data["sent_at"]
        if "viewed_at" in data:
            request.viewed_at = data["viewed_at"]
        if "responded_at" in data:
            request.responded_at = data["responded_at"]
        if "decision" in data:
            request.decision = data["decision"]
        if "decision_details" in data:
            request.decision_details = data["decision_details"]
        if "feedback" in data:
            request.feedback = data["feedback"]
            
        return request


class ClientUpdate:
    """Represents a campaign update sent to a client."""
    
    def __init__(self, 
                 update_id: str,
                 client_id: str,
                 campaign_id: str,
                 update_type: str,
                 title: str,
                 content: str,
                 metrics: Optional[Dict[str, Any]] = None,
                 attachments: Optional[List[Dict[str, Any]]] = None,
                 created_at: Optional[str] = None,
                 importance: str = "medium",
                 status: str = "pending"):
        self.update_id = update_id
        self.client_id = client_id
        self.campaign_id = campaign_id
        self.update_type = update_type
        self.title = title
        self.content = content
        self.metrics = metrics or {}
        self.attachments = attachments or []
        self.created_at = created_at or datetime.now().isoformat()
        self.importance = importance
        self.status = status
        self.sent_at: Optional[str] = None
        self.viewed_at: Optional[str] = None
        self.acknowledged_at: Optional[str] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert update to dictionary representation."""
        return {
            "update_id": self.update_id,
            "client_id": self.client_id,
            "campaign_id": self.campaign_id,
            "update_type": self.update_type,
            "title": self.title,
            "content": self.content,
            "metrics": self.metrics,
            "attachments": self.attachments,
            "created_at": self.created_at,
            "importance": self.importance,
            "status": self.status,
            "sent_at": self.sent_at,
            "viewed_at": self.viewed_at,
            "acknowledged_at": self.acknowledged_at
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClientUpdate':
        """Create a ClientUpdate instance from dictionary data."""
        update = cls(
            update_id=data["update_id"],
            client_id=data["client_id"],
            campaign_id=data["campaign_id"],
            update_type=data["update_type"],
            title=data["title"],
            content=data["content"],
            metrics=data.get("metrics", {}),
            attachments=data.get("attachments", []),
            created_at=data.get("created_at"),
            importance=data.get("importance", "medium"),
            status=data.get("status", "pending")
        )
        
        # Set additional fields if present
        if "sent_at" in data:
            update.sent_at = data["sent_at"]
        if "viewed_at" in data:
            update.viewed_at = data["viewed_at"]
        if "acknowledged_at" in data:
            update.acknowledged_at = data["acknowledged_at"]
            
        return update


class ClientProfile:
    """Represents a client profile with communication preferences."""
    
    def __init__(self, 
                 client_id: str,
                 name: str,
                 email: str,
                 company: Optional[str] = None,
                 role: Optional[str] = None,
                 created_at: Optional[str] = None,
                 preferences: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.client_id = client_id
        self.name = name
        self.email = email
        self.company = company
        self.role = role
        self.created_at = created_at or datetime.now().isoformat()
        self.preferences = preferences or {
            "communication_frequency": "weekly",
            "notification_channels": ["email"],
            "update_types": ["performance", "approvals", "milestones"],
            "approval_reminders": True,
            "report_format": "summary"
        }
        self.metadata = metadata or {}
        self.campaigns: List[str] = []
        self.last_contact: Optional[str] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert client profile to dictionary representation."""
        return {
            "client_id": self.client_id,
            "name": self.name,
            "email": self.email,
            "company": self.company,
            "role": self.role,
            "created_at": self.created_at,
            "preferences": self.preferences,
            "metadata": self.metadata,
            "campaigns": self.campaigns,
            "last_contact": self.last_contact
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClientProfile':
        """Create a ClientProfile instance from dictionary data."""
        profile = cls(
            client_id=data["client_id"],
            name=data["name"],
            email=data["email"],
            company=data.get("company"),
            role=data.get("role"),
            created_at=data.get("created_at"),
            preferences=data.get("preferences", {}),
            metadata=data.get("metadata", {})
        )
        
        # Set additional fields if present
        if "campaigns" in data:
            profile.campaigns = data["campaigns"]
        if "last_contact" in data:
            profile.last_contact = data["last_contact"]
            
        return profile


class ClientCommunicationAgent(BaseProcessAwareAgent):
    """Agent responsible for managing client communications and approvals."""
    
    def __init__(self, agent_id: str = "client_agent", **kwargs):
        super().__init__(agent_id=agent_id, **kwargs)
        self.communication_protocol = StandardCommunicationProtocol()
        
        # Storage for client data
        self.client_profiles: Dict[str, ClientProfile] = {}
        self.messages: Dict[str, ClientMessage] = {}
        self.approval_requests: Dict[str, ApprovalRequest] = {}
        self.updates: Dict[str, ClientUpdate] = {}
        
        # Campaign data
        self.campaigns: Dict[str, Dict[str, Any]] = {}
        
        # Notification tracking
        self.notification_queue: List[Dict[str, Any]] = []
        self._notification_thread = None
        self._stop_notification = threading.Event()
        
        # Register message handlers
        self.register_message_handler("CLIENT_REQUEST", self._handle_client_request)
        self.register_message_handler("APPROVAL_REQUEST", self._handle_approval_request)
        self.register_message_handler("CAMPAIGN_UPDATE", self._handle_campaign_update)
        self.register_message_handler("CLIENT_RESPONSE", self._handle_client_response)
        
        # Subscribe to relevant topics
        self.communication_protocol.subscribe(
            self.agent_id,
            "campaign_updates"
        )
        self.communication_protocol.subscribe(
            self.agent_id, 
            "client_notifications"
        )
        
        # Register process activities
        self.register_activity("send_client_update", self._activity_send_update)
        self.register_activity("request_approval", self._activity_request_approval)
        self.register_activity("send_performance_report", self._activity_send_performance_report)
        self.register_activity("process_client_feedback", self._activity_process_feedback)
        self.register_activity("generate_client_summary", self._activity_generate_summary)
        
    def start_notification_processing(self, interval: int = 60) -> None:
        """Start background notification processing thread.
        
        Args:
            interval: Processing interval in seconds (default: 60 seconds)
        """
        if self._notification_thread and self._notification_thread.is_alive():
            logger.warning("Notification processing already running")
            return
            
        self._stop_notification.clear()
        self._notification_thread = threading.Thread(
            target=self._notification_worker,
            args=(interval,),
            daemon=True
        )
        self._notification_thread.start()
        logger.info(f"Started notification processing with interval {interval}s")
    
    def stop_notification_processing(self) -> None:
        """Stop background notification processing thread."""
        if not self._notification_thread or not self._notification_thread.is_alive():
            logger.warning("No notification processing running")
            return
            
        self._stop_notification.set()
        self._notification_thread.join(timeout=5.0)
        logger.info("Stopped notification processing")
    
    def _notification_worker(self, interval: int) -> None:
        """Background worker for notification processing.
        
        Args:
            interval: Processing interval in seconds
        """
        while not self._stop_notification.is_set():
            try:
                # Check for any notifications to send
                self._process_notification_queue()
                
                # Check for expiring approval requests
                self._check_approval_deadlines()
                
                # Generate scheduled client updates
                self._generate_scheduled_updates()
                
            except Exception as e:
                logger.error(f"Error in notification processing: {str(e)}")
                
            # Sleep until next processing interval
            self._stop_notification.wait(interval)
    
    def _process_notification_queue(self) -> None:
        """Process the notification queue."""
        if not self.notification_queue:
            return
            
        # Process in batches to avoid overwhelming the system
        batch_size = min(10, len(self.notification_queue))
        batch = self.notification_queue[:batch_size]
        self.notification_queue = self.notification_queue[batch_size:]
        
        for notification in batch:
            notification_type = notification.get("type")
            
            if notification_type == "message":
                message_id = notification.get("message_id")
                if message_id in self.messages:
                    self._send_client_message(message_id)
                    
            elif notification_type == "approval":
                request_id = notification.get("request_id")
                if request_id in self.approval_requests:
                    self._send_approval_request(request_id)
                    
            elif notification_type == "update":
                update_id = notification.get("update_id")
                if update_id in self.updates:
                    self._send_client_update(update_id)
                    
            elif notification_type == "reminder":
                request_id = notification.get("request_id")
                if request_id in self.approval_requests:
                    self._send_approval_reminder(request_id)
    
    def _check_approval_deadlines(self) -> None:
        """Check for approval requests approaching their deadline."""
        now = datetime.now()
        
        for request_id, request in self.approval_requests.items():
            if request.status != "pending" or not request.deadline:
                continue
                
            deadline = datetime.fromisoformat(request.deadline)
            time_left = deadline - now
            
            # If deadline is within 24 hours and no reminder has been sent recently
            if 0 < time_left.total_seconds() < 86400:  # 24 hours in seconds
                # Check if we've sent a reminder recently
                last_reminder = request.metadata.get("last_reminder")
                if not last_reminder or (now - datetime.fromisoformat(last_reminder)).total_seconds() > 14400:  # 4 hours
                    # Add reminder to notification queue
                    self.notification_queue.append({
                        "type": "reminder",
                        "request_id": request_id,
                        "time_left": time_left.total_seconds()
                    })
                    
                    # Update last reminder time
                    request.metadata["last_reminder"] = now.isoformat()
    
    def _generate_scheduled_updates(self) -> None:
        """Generate scheduled client updates based on preferences."""
        now = datetime.now()
        
        for client_id, profile in self.client_profiles.items():
            # Skip if client has no campaigns
            if not profile.campaigns:
                continue
                
            preferences = profile.preferences or {}
            frequency = preferences.get("communication_frequency", "weekly")
            
            # Check if it's time to send an update based on frequency
            last_update = profile.metadata.get("last_scheduled_update")
            
            if not last_update:
                # Never sent an update, schedule one
                self._schedule_client_update(client_id)
                continue
                
            last_update_time = datetime.fromisoformat(last_update)
            
            # Determine if it's time for an update based on frequency
            if frequency == "daily" and (now - last_update_time).days >= 1:
                self._schedule_client_update(client_id)
            elif frequency == "weekly" and (now - last_update_time).days >= 7:
                self._schedule_client_update(client_id)
            elif frequency == "monthly" and (now - last_update_time).days >= 30:
                self._schedule_client_update(client_id)
    
    def _schedule_client_update(self, client_id: str) -> None:
        """Schedule a client update based on their active campaigns.
        
        Args:
            client_id: Client ID
        """
        profile = self.client_profiles.get(client_id)
        if not profile or not profile.campaigns:
            return
            
        # Create a campaign status update
        for campaign_id in profile.campaigns:
            if campaign_id not in self.campaigns:
                continue
                
            # Check if we've sent an update for this campaign recently
            campaign = self.campaigns[campaign_id]
            last_campaign_update = campaign.get("last_update_time")
            
            if last_campaign_update:
                last_update_time = datetime.fromisoformat(last_campaign_update)
                if (datetime.now() - last_update_time).days < 3:
                    # Skip if we've sent an update in the last 3 days
                    continue
            
            # Create an update with campaign status information
            update_id = self._create_campaign_status_update(client_id, campaign_id)
            
            if update_id:
                # Schedule for sending
                self.notification_queue.append({
                    "type": "update",
                    "update_id": update_id
                })
                
                # Update tracking information
                self.client_profiles[client_id].metadata["last_scheduled_update"] = datetime.now().isoformat()
                self.campaigns[campaign_id]["last_update_time"] = datetime.now().isoformat()
                
                # Only send one update per execution to avoid overwhelming the client
                break
    
    def register_client(self, client_data: Dict[str, Any]) -> str:
        """Register a new client in the system.
        
        Args:
            client_data: Client information including name, email, etc.
            
        Returns:
            str: Client ID
        """
        client_id = client_data.get("client_id") or f"client-{str(uuid.uuid4())[:8]}"
        
        # Check if client already exists
        if client_id in self.client_profiles:
            logger.warning(f"Client {client_id} already exists, updating profile")
            
        # Create or update client profile
        client_profile = ClientProfile(
            client_id=client_id,
            name=client_data.get("name", ""),
            email=client_data.get("email", ""),
            company=client_data.get("company"),
            role=client_data.get("role"),
            preferences=client_data.get("preferences"),
            metadata=client_data.get("metadata", {})
        )
        
        # Set campaigns if provided
        if "campaigns" in client_data:
            client_profile.campaigns = client_data["campaigns"]
            
        # Store client profile
        self.client_profiles[client_id] = client_profile
        logger.info(f"Registered client {client_id} ({client_profile.name})")
        
        return client_id
    
    def associate_campaign(self, client_id: str, campaign_id: str, campaign_data: Optional[Dict[str, Any]] = None) -> bool:
        """Associate a campaign with a client.
        
        Args:
            client_id: Client ID
            campaign_id: Campaign ID
            campaign_data: Optional campaign information
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if client exists
        if client_id not in self.client_profiles:
            logger.warning(f"Cannot associate campaign: Client {client_id} not found")
            return False
            
        # Add campaign to client's list
        if campaign_id not in self.client_profiles[client_id].campaigns:
            self.client_profiles[client_id].campaigns.append(campaign_id)
            
        # Store campaign data if provided
        if campaign_data:
            if campaign_id not in self.campaigns:
                self.campaigns[campaign_id] = {
                    "campaign_id": campaign_id,
                    "client_id": client_id,
                    "created_at": datetime.now().isoformat(),
                    "last_update_time": None,
                    "status": campaign_data.get("status", "active")
                }
                
            # Update campaign data
            self.campaigns[campaign_id].update(campaign_data)
            
        logger.info(f"Associated campaign {campaign_id} with client {client_id}")
        return True
    
    def create_client_message(self, client_id: str, message_data: Dict[str, Any]) -> Optional[str]:
        """Create a message to send to a client.
        
        Args:
            client_id: Client ID
            message_data: Message content and metadata
            
        Returns:
            str: Message ID if successful, None otherwise
        """
        # Check if client exists
        if client_id not in self.client_profiles:
            logger.warning(f"Cannot create message: Client {client_id} not found")
            return None
            
        # Create message ID
        message_id = message_data.get("message_id") or f"msg-{str(uuid.uuid4())[:8]}"
        
        # Create client message
        message = ClientMessage(
            message_id=message_id,
            client_id=client_id,
            campaign_id=message_data.get("campaign_id"),
            message_type=message_data.get("message_type", "general"),
            subject=message_data.get("subject", ""),
            content=message_data.get("content", ""),
            attachments=message_data.get("attachments", []),
            priority=message_data.get("priority", "normal"),
            metadata=message_data.get("metadata", {})
        )
        
        # Store message
        self.messages[message_id] = message
        
        # Add to notification queue if immediate
        if message_data.get("send_immediately", False):
            self.notification_queue.append({
                "type": "message",
                "message_id": message_id
            })
            
        logger.info(f"Created client message {message_id} for client {client_id}")
        return message_id
    
    def create_approval_request(self, client_id: str, campaign_id: str, request_data: Dict[str, Any]) -> Optional[str]:
        """Create an approval request for a client.
        
        Args:
            client_id: Client ID
            campaign_id: Campaign ID
            request_data: Approval request data
            
        Returns:
            str: Request ID if successful, None otherwise
        """
        # Check if client and campaign exist
        if client_id not in self.client_profiles:
            logger.warning(f"Cannot create approval request: Client {client_id} not found")
            return None
            
        if campaign_id not in self.campaigns:
            logger.warning(f"Cannot create approval request: Campaign {campaign_id} not found")
            # Create campaign entry if it doesn't exist
            self.campaigns[campaign_id] = {
                "campaign_id": campaign_id,
                "client_id": client_id,
                "created_at": datetime.now().isoformat(),
                "last_update_time": None,
                "status": "active"
            }
            
        # Create request ID
        request_id = request_data.get("request_id") or f"req-{str(uuid.uuid4())[:8]}"
        
        # Set deadline if not provided
        deadline = request_data.get("deadline")
        if not deadline:
            # Default to 3 business days
            deadline_date = datetime.now() + timedelta(days=3)
            deadline = deadline_date.isoformat()
            
        # Create approval request
        request = ApprovalRequest(
            request_id=request_id,
            client_id=client_id,
            campaign_id=campaign_id,
            request_type=request_data.get("request_type", "creative"),
            title=request_data.get("title", ""),
            description=request_data.get("description", ""),
            items_for_approval=request_data.get("items_for_approval", []),
            deadline=deadline,
            priority=request_data.get("priority", "normal"),
            metadata=request_data.get("metadata", {})
        )
        
        # Store request
        self.approval_requests[request_id] = request
        
        # Update campaign data
        if campaign_id in self.campaigns:
            if "pending_approvals" not in self.campaigns[campaign_id]:
                self.campaigns[campaign_id]["pending_approvals"] = []
                
            self.campaigns[campaign_id]["pending_approvals"].append(request_id)
            self.campaigns[campaign_id]["last_approval_request"] = datetime.now().isoformat()
            
        # Add to notification queue if immediate
        if request_data.get("send_immediately", True):
            self.notification_queue.append({
                "type": "approval",
                "request_id": request_id
            })
            
        logger.info(f"Created approval request {request_id} for client {client_id}, campaign {campaign_id}")
        return request_id
    
    def create_client_update(self, client_id: str, campaign_id: str, update_data: Dict[str, Any]) -> Optional[str]:
        """Create a campaign update for a client.
        
        Args:
            client_id: Client ID
            campaign_id: Campaign ID
            update_data: Update content and metadata
            
        Returns:
            str: Update ID if successful, None otherwise
        """
        # Check if client exists
        if client_id not in self.client_profiles:
            logger.warning(f"Cannot create update: Client {client_id} not found")
            return None
            
        # Create update ID
        update_id = update_data.get("update_id") or f"upd-{str(uuid.uuid4())[:8]}"
        
        # Create client update
        update = ClientUpdate(
            update_id=update_id,
            client_id=client_id,
            campaign_id=campaign_id,
            update_type=update_data.get("update_type", "general"),
            title=update_data.get("title", ""),
            content=update_data.get("content", ""),
            metrics=update_data.get("metrics", {}),
            attachments=update_data.get("attachments", []),
            importance=update_data.get("importance", "medium")
        )
        
        # Store update
        self.updates[update_id] = update
        
        # Update campaign data
        if campaign_id in self.campaigns:
            self.campaigns[campaign_id]["last_update_time"] = datetime.now().isoformat()
            
        # Add to notification queue if immediate
        if update_data.get("send_immediately", True):
            self.notification_queue.append({
                "type": "update",
                "update_id": update_id
            })
            
        logger.info(f"Created client update {update_id} for client {client_id}, campaign {campaign_id}")
        return update_id
    
    def _create_campaign_status_update(self, client_id: str, campaign_id: str) -> Optional[str]:
        """Create a campaign status update.
        
        Args:
            client_id: Client ID
            campaign_id: Campaign ID
            
        Returns:
            str: Update ID if successful, None otherwise
        """
        # Check if campaign exists
        if campaign_id not in self.campaigns:
            logger.warning(f"Cannot create status update: Campaign {campaign_id} not found")
            return None
            
        campaign = self.campaigns[campaign_id]
        campaign_name = campaign.get("name", f"Campaign {campaign_id}")
        campaign_status = campaign.get("status", "active")
        
        # Prepare metrics if available
        metrics = {}
        if "metrics" in campaign:
            metrics = campaign["metrics"]
            
        # Prepare content based on campaign status
        content = f"Your campaign '{campaign_name}' is currently {campaign_status}."
        
        if campaign_status == "active":
            content += " We're working on delivering your campaign objectives and will keep you updated on performance."
        elif campaign_status == "paused":
            content += " The campaign is currently paused. Let us know when you'd like to resume activity."
        elif campaign_status == "completed":
            content += " The campaign has concluded. A full performance report is available in your dashboard."
            
        # Add metrics summary if available
        if metrics:
            content += "\n\nKey performance indicators:"
            for metric_name, value in metrics.items():
                if isinstance(value, (int, float)):
                    content += f"\n- {metric_name.replace('_', ' ').title()}: {value:,}"
                    
        # Create update
        update_data = {
            "update_type": "status",
            "title": f"{campaign_name} Status Update",
            "content": content,
            "metrics": metrics,
            "importance": "medium",
            "send_immediately": False
        }
        
        return self.create_client_update(client_id, campaign_id, update_data)
    
    def _send_client_message(self, message_id: str) -> bool:
        """Send a message to a client.
        
        Args:
            message_id: Message ID
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if message_id not in self.messages:
            logger.warning(f"Cannot send message: Message {message_id} not found")
            return False
            
        message = self.messages[message_id]
        
        # Check if client exists
        if message.client_id not in self.client_profiles:
            logger.warning(f"Cannot send message: Client {message.client_id} not found")
            return False
            
        client = self.client_profiles[message.client_id]
        
        # In a real implementation, this would send via email or other channels
        # For this demo, we'll simulate sending
        logger.info(f"Sending message {message_id} to {client.name} ({client.email})")
        logger.info(f"Subject: {message.subject}")
        
        # Update message status
        message.status = "sent"
        message.sent_at = datetime.now().isoformat()
        
        # Update client last contact
        client.last_contact = datetime.now().isoformat()
        
        # Publish message sent event
        self.communication_protocol.publish(
            sender=self.agent_id,
            topic="client_notifications",
            content={
                "event": "message_sent",
                "message_id": message_id,
                "client_id": message.client_id,
                "campaign_id": message.campaign_id,
                "message_type": message.message_type,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return True
    
    def _send_approval_request(self, request_id: str) -> bool:
        """Send an approval request to a client.
        
        Args:
            request_id: Request ID
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if request_id not in self.approval_requests:
            logger.warning(f"Cannot send approval request: Request {request_id} not found")
            return False
            
        request = self.approval_requests[request_id]
        
        # Check if client exists
        if request.client_id not in self.client_profiles:
            logger.warning(f"Cannot send approval request: Client {request.client_id} not found")
            return False
            
        client = self.client_profiles[request.client_id]
        
        # In a real implementation, this would send via email or other channels
        # For this demo, we'll simulate sending
        logger.info(f"Sending approval request {request_id} to {client.name} ({client.email})")
        logger.info(f"Title: {request.title}")
        logger.info(f"Items for approval: {len(request.items_for_approval)}")
        
        # Update request status
        request.status = "sent"
        request.sent_at = datetime.now().isoformat()
        
        # Update client last contact
        client.last_contact = datetime.now().isoformat()
        
        # Publish approval request sent event
        self.communication_protocol.publish(
            sender=self.agent_id,
            topic="client_notifications",
            content={
                "event": "approval_request_sent",
                "request_id": request_id,
                "client_id": request.client_id,
                "campaign_id": request.campaign_id,
                "request_type": request.request_type,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return True
    
    def _send_client_update(self, update_id: str) -> bool:
        """Send an update to a client.
        
        Args:
            update_id: Update ID
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if update_id not in self.updates:
            logger.warning(f"Cannot send update: Update {update_id} not found")
            return False
            
        update = self.updates[update_id]
        
        # Check if client exists
        if update.client_id not in self.client_profiles:
            logger.warning(f"Cannot send update: Client {update.client_id} not found")
            return False
            
        client = self.client_profiles[update.client_id]
        
        # In a real implementation, this would send via email or other channels
        # For this demo, we'll simulate sending
        logger.info(f"Sending update {update_id} to {client.name} ({client.email})")
        logger.info(f"Title: {update.title}")
        logger.info(f"Type: {update.update_type}")
        
        # Update status
        update.status = "sent"
        update.sent_at = datetime.now().isoformat()
        
        # Update client last contact
        client.last_contact = datetime.now().isoformat()
        
        # Publish update sent event
        self.communication_protocol.publish(
            sender=self.agent_id,
            topic="client_notifications",
            content={
                "event": "update_sent",
                "update_id": update_id,
                "client_id": update.client_id,
                "campaign_id": update.campaign_id,
                "update_type": update.update_type,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        return True
    
    def _send_approval_reminder(self, request_id: str) -> bool:
        """Send a reminder for an approval request.
        
        Args:
            request_id: Request ID
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if request_id not in self.approval_requests:
            logger.warning(f"Cannot send reminder: Request {request_id} not found")
            return False
            
        request = self.approval_requests[request_id]
        
        # Skip if request is no longer pending
        if request.status != "pending":
            return False
            
        # Check if client exists
        if request.client_id not in self.client_profiles:
            logger.warning(f"Cannot send reminder: Client {request.client_id} not found")
            return False
            
        client = self.client_profiles[request.client_id]
        
        # Calculate time until deadline
        deadline = datetime.fromisoformat(request.deadline) if request.deadline else None
        time_left = None
        if deadline:
            time_left = deadline - datetime.now()
            
        # Create reminder message
        reminder_subject = f"Reminder: {request.title} - Approval Needed"
        
        reminder_content = f"This is a friendly reminder that we're waiting for your approval on '{request.title}'."
        
        if time_left and time_left.total_seconds() > 0:
            days_left = int(time_left.total_seconds() / 86400)
            hours_left = int((time_left.total_seconds() % 86400) / 3600)
            
            if days_left > 0:
                reminder_content += f"\n\nTime remaining: {days_left} days and {hours_left} hours."
            else:
                reminder_content += f"\n\nTime remaining: {hours_left} hours."
        elif time_left:
            reminder_content += "\n\nThe approval deadline has passed. Please respond as soon as possible."
        
        # Create reminder message
        message_data = {
            "message_type": "reminder",
            "subject": reminder_subject,
            "content": reminder_content,
            "priority": "high",
            "metadata": {
                "request_id": request_id,
                "reminder": True
            },
            "send_immediately": True
        }
        
        # Send the reminder
        message_id = self.create_client_message(request.client_id, message_data)
        
        if message_id:
            # Update request metadata
            request.metadata["reminder_sent"] = datetime.now().isoformat()
            request.metadata["reminder_message_id"] = message_id
            
            logger.info(f"Sent approval reminder {message_id} for request {request_id} to {client.name}")
            return True
            
        return False
    
    def process_client_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a response from a client.
        
        Args:
            response_data: Response data including client ID, message ID, etc.
            
        Returns:
            Dict: Processing result
        """
        client_id = response_data.get("client_id")
        message_id = response_data.get("message_id")
        request_id = response_data.get("request_id")
        update_id = response_data.get("update_id")
        
        result = {
            "success": False,
            "error": None,
            "processed": False,
            "type": None,
            "details": {}
        }
        
        # Check if client exists
        if client_id and client_id not in self.client_profiles:
            result["error"] = f"Client {client_id} not found"
            return result
            
        # Process message response
        if message_id and message_id in self.messages:
            message = self.messages[message_id]
            
            # Check client ID match
            if message.client_id != client_id:
                result["error"] = "Client ID doesn't match message owner"
                return result
                
            # Mark message as read
            message.status = "read"
            message.read_at = datetime.now().isoformat()
            
            # Store response if provided
            if "response_content" in response_data:
                message.response = {
                    "content": response_data.get("response_content"),
                    "timestamp": datetime.now().isoformat()
                }
                message.responded_at = datetime.now().isoformat()
                
            result["success"] = True
            result["processed"] = True
            result["type"] = "message"
            result["details"] = {"message_id": message_id}
            
        # Process approval request response
        elif request_id and request_id in self.approval_requests:
            request = self.approval_requests[request_id]
            
            # Check client ID match
            if request.client_id != client_id:
                result["error"] = "Client ID doesn't match request owner"
                return result
                
            # Mark request as viewed if not already responded to
            if request.status == "sent" or request.status == "pending":
                request.status = "viewed"
                request.viewed_at = datetime.now().isoformat()
                
            # Process decision if provided
            if "decision" in response_data:
                decision = response_data.get("decision")
                
                if decision in ["approved", "rejected", "changes_requested"]:
                    request.status = decision
                    request.decision = decision
                    request.responded_at = datetime.now().isoformat()
                    
                    # Store decision details if provided
                    if "decision_details" in response_data:
                        request.decision_details = response_data.get("decision_details")
                        
                    # Store feedback if provided
                    if "feedback" in response_data:
                        request.feedback = response_data.get("feedback")
                        
                    # Update campaign data
                    if request.campaign_id in self.campaigns:
                        campaign = self.campaigns[request.campaign_id]
                        
                        # Remove from pending approvals
                        if "pending_approvals" in campaign and request_id in campaign["pending_approvals"]:
                            campaign["pending_approvals"].remove(request_id)
                            
                        # Add to approval history
                        if "approval_history" not in campaign:
                            campaign["approval_history"] = []
                            
                        campaign["approval_history"].append({
                            "request_id": request_id,
                            "decision": decision,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                    # Publish approval decision event
                    self.communication_protocol.publish(
                        sender=self.agent_id,
                        topic="campaign_updates",
                        content={
                            "event": "approval_decision",
                            "request_id": request_id,
                            "client_id": client_id,
                            "campaign_id": request.campaign_id,
                            "decision": decision,
                            "timestamp": datetime.now().isoformat()
                        }
                    )
                    
            result["success"] = True
            result["processed"] = True
            result["type"] = "approval"
            result["details"] = {"request_id": request_id}
            
        # Process update response
        elif update_id and update_id in self.updates:
            update = self.updates[update_id]
            
            # Check client ID match
            if update.client_id != client_id:
                result["error"] = "Client ID doesn't match update owner"
                return result
                
            # Mark update as viewed
            update.status = "viewed"
            update.viewed_at = datetime.now().isoformat()
            
            # Mark as acknowledged if indicated
            if response_data.get("acknowledged", False):
                update.status = "acknowledged"
                update.acknowledged_at = datetime.now().isoformat()
                
            result["success"] = True
            result["processed"] = True
            result["type"] = "update"
            result["details"] = {"update_id": update_id}
            
        else:
            result["error"] = "No valid message_id, request_id, or update_id provided"
            
        return result
    
    def generate_client_summary(self, client_id: str) -> Dict[str, Any]:
        """Generate a summary of client activity and campaigns.
        
        Args:
            client_id: Client ID
            
        Returns:
            Dict: Client summary
        """
        # Check if client exists
        if client_id not in self.client_profiles:
            return {
                "success": False,
                "error": f"Client {client_id} not found"
            }
            
        client = self.client_profiles[client_id]
        
        # Collect campaign data
        campaign_summaries = []
        for campaign_id in client.campaigns:
            if campaign_id in self.campaigns:
                campaign = self.campaigns[campaign_id]
                
                # Count pending approvals
                pending_approvals = len(campaign.get("pending_approvals", []))
                
                # Create campaign summary
                campaign_summary = {
                    "campaign_id": campaign_id,
                    "name": campaign.get("name", f"Campaign {campaign_id}"),
                    "status": campaign.get("status", "active"),
                    "pending_approvals": pending_approvals
                }
                
                # Add metrics if available
                if "metrics" in campaign:
                    campaign_summary["metrics"] = campaign["metrics"]
                    
                campaign_summaries.append(campaign_summary)
        
        # Count communication activities
        client_messages = [m for m in self.messages.values() if m.client_id == client_id]
        approval_requests = [r for r in self.approval_requests.values() if r.client_id == client_id]
        client_updates = [u for u in self.updates.values() if u.client_id == client_id]
        
        # Build summary
        summary = {
            "client_id": client_id,
            "name": client.name,
            "email": client.email,
            "company": client.company,
            "active_campaigns": len(client.campaigns),
            "campaign_summaries": campaign_summaries,
            "communication": {
                "messages": len(client_messages),
                "approval_requests": len(approval_requests),
                "updates": len(client_updates),
                "pending_approvals": len([r for r in approval_requests if r.status in ["pending", "sent", "viewed"]])
            },
            "last_contact": client.last_contact,
            "preferences": client.preferences
        }
        
        return {
            "success": True,
            "summary": summary
        }
    
    def _handle_client_request(self, message: Message) -> None:
        """Handle client request message.
        
        Args:
            message: Incoming message
        """
        logger.info(f"Received client request from {message.sender}")
        
        request_type = message.content.get("request_type")
        
        if not request_type:
            self._send_error_response(message, "Missing request_type in client request")
            return
            
        if request_type == "register_client":
            # Register a new client
            client_data = message.content.get("client_data", {})
            if not client_data:
                self._send_error_response(message, "Missing client_data in registration request")
                return
                
            client_id = self.register_client(client_data)
            
            # Send response
            response = Message(
                message_type=MessageType.RESPONSE,
                sender=self.agent_id,
                recipient=message.sender,
                content={
                    "request_type": request_type,
                    "success": True,
                    "client_id": client_id,
                    "message": f"Client registered successfully with ID {client_id}"
                }
            )
            
            self.communication_protocol.send_message(response)
            
        elif request_type == "associate_campaign":
            # Associate a campaign with a client
            client_id = message.content.get("client_id")
            campaign_id = message.content.get("campaign_id")
            campaign_data = message.content.get("campaign_data", {})
            
            if not client_id or not campaign_id:
                self._send_error_response(message, "Missing client_id or campaign_id in associate request")
                return
                
            success = self.associate_campaign(client_id, campaign_id, campaign_data)
            
            # Send response
            response = Message(
                message_type=MessageType.RESPONSE,
                sender=self.agent_id,
                recipient=message.sender,
                content={
                    "request_type": request_type,
                    "success": success,
                    "client_id": client_id,
                    "campaign_id": campaign_id,
                    "message": f"Campaign {campaign_id} associated with client {client_id}" if success else "Association failed"
                }
            )
            
            self.communication_protocol.send_message(response)
            
        elif request_type == "client_summary":
            # Generate client summary
            client_id = message.content.get("client_id")
            
            if not client_id:
                self._send_error_response(message, "Missing client_id in summary request")
                return
                
            summary_result = self.generate_client_summary(client_id)
            
            # Send response
            response = Message(
                message_type=MessageType.RESPONSE,
                sender=self.agent_id,
                recipient=message.sender,
                content={
                    "request_type": request_type,
                    "success": summary_result.get("success", False),
                    "client_id": client_id,
                    "summary": summary_result.get("summary", {}),
                    "error": summary_result.get("error")
                }
            )
            
            self.communication_protocol.send_message(response)
            
        else:
            self._send_error_response(message, f"Unknown request_type: {request_type}")
            
    def _handle_approval_request(self, message: Message) -> None:
        """Handle approval request message.
        
        Args:
            message: Incoming message
        """
        logger.info(f"Received approval request from {message.sender}")
        
        client_id = message.content.get("client_id")
        campaign_id = message.content.get("campaign_id")
        request_data = message.content
        
        if not client_id or not campaign_id:
            self._send_error_response(message, "Missing client_id or campaign_id in approval request")
            return
            
        # Create approval request
        request_id = self.create_approval_request(client_id, campaign_id, request_data)
        
        if not request_id:
            self._send_error_response(message, "Failed to create approval request")
            return
            
        # Send response
        response = Message(
            message_type=MessageType.RESPONSE,
            sender=self.agent_id,
            recipient=message.sender,
            content={
                "success": True,
                "request_id": request_id,
                "client_id": client_id,
                "campaign_id": campaign_id,
                "status": "created",
                "message": f"Approval request {request_id} created successfully"
            }
        )
        
        self.communication_protocol.send_message(response)
        
    def _handle_campaign_update(self, message: Message) -> None:
        """Handle campaign update message.
        
        Args:
            message: Incoming message
        """
        logger.info(f"Received campaign update from {message.sender}")
        
        client_id = message.content.get("client_id")
        campaign_id = message.content.get("campaign_id")
        update_data = message.content
        
        if not client_id or not campaign_id:
            self._send_error_response(message, "Missing client_id or campaign_id in update")
            return
            
        # Create client update
        update_id = self.create_client_update(client_id, campaign_id, update_data)
        
        if not update_id:
            self._send_error_response(message, "Failed to create client update")
            return
            
        # Send response
        response = Message(
            message_type=MessageType.RESPONSE,
            sender=self.agent_id,
            recipient=message.sender,
            content={
                "success": True,
                "update_id": update_id,
                "client_id": client_id,
                "campaign_id": campaign_id,
                "status": "created",
                "message": f"Client update {update_id} created successfully"
            }
        )
        
        self.communication_protocol.send_message(response)
        
    def _handle_client_response(self, message: Message) -> None:
        """Handle response from a client.
        
        Args:
            message: Incoming message
        """
        logger.info(f"Received client response from {message.sender}")
        
        response_data = message.content
        
        # Process the client response
        result = self.process_client_response(response_data)
        
        # Send response
        response = Message(
            message_type=MessageType.RESPONSE,
            sender=self.agent_id,
            recipient=message.sender,
            content={
                "success": result.get("success", False),
                "processed": result.get("processed", False),
                "type": result.get("type"),
                "details": result.get("details", {}),
                "error": result.get("error")
            }
        )
        
        self.communication_protocol.send_message(response)
        
    def _send_error_response(self, original_message: Message, error_text: str) -> None:
        """Send an error response for a message.
        
        Args:
            original_message: Original message
            error_text: Error message
        """
        response = Message(
            message_type=MessageType.ERROR,
            sender=self.agent_id,
            recipient=original_message.sender,
            content={
                "error": error_text,
                "original_message_id": original_message.message_id
            }
        )
        
        self.communication_protocol.send_message(response)
        logger.error(f"Sent error response to {original_message.sender}: {error_text}")
        
    def _activity_send_update(self, context: ProcessContext) -> Dict[str, Any]:
        """Process activity to send a client update.
        
        Args:
            context: Process activity context
            
        Returns:
            Dict: Activity results
        """
        try:
            # Get parameters
            client_id = context.get_parameter("client_id")
            campaign_id = context.get_parameter("campaign_id")
            update_type = context.get_parameter("update_type", "general")
            title = context.get_parameter("title")
            content = context.get_parameter("content")
            metrics = context.get_parameter("metrics", {})
            
            if not client_id or not campaign_id or not title or not content:
                return {
                    "success": False,
                    "error": "Missing required parameters: client_id, campaign_id, title, content"
                }
                
            # Create update data
            update_data = {
                "update_type": update_type,
                "title": title,
                "content": content,
                "metrics": metrics,
                "send_immediately": True
            }
            
            # Create client update
            update_id = self.create_client_update(client_id, campaign_id, update_data)
            
            if not update_id:
                return {
                    "success": False,
                    "error": f"Failed to create update for client {client_id}, campaign {campaign_id}"
                }
                
            return {
                "success": True,
                "update_id": update_id,
                "client_id": client_id,
                "campaign_id": campaign_id,
                "status": "sent"
            }
            
        except Exception as e:
            logger.error(f"Error in send_update activity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def _activity_request_approval(self, context: ProcessContext) -> Dict[str, Any]:
        """Process activity to request client approval.
        
        Args:
            context: Process activity context
            
        Returns:
            Dict: Activity results
        """
        try:
            # Get parameters
            client_id = context.get_parameter("client_id")
            campaign_id = context.get_parameter("campaign_id")
            request_type = context.get_parameter("request_type", "creative")
            title = context.get_parameter("title")
            description = context.get_parameter("description")
            items_for_approval = context.get_parameter("items_for_approval", [])
            deadline = context.get_parameter("deadline")
            
            if not client_id or not campaign_id or not title or not items_for_approval:
                return {
                    "success": False,
                    "error": "Missing required parameters: client_id, campaign_id, title, items_for_approval"
                }
                
            # Create request data
            request_data = {
                "request_type": request_type,
                "title": title,
                "description": description,
                "items_for_approval": items_for_approval,
                "deadline": deadline,
                "send_immediately": True
            }
            
            # Create approval request
            request_id = self.create_approval_request(client_id, campaign_id, request_data)
            
            if not request_id:
                return {
                    "success": False,
                    "error": f"Failed to create approval request for client {client_id}, campaign {campaign_id}"
                }
                
            return {
                "success": True,
                "request_id": request_id,
                "client_id": client_id,
                "campaign_id": campaign_id,
                "status": "sent"
            }
            
        except Exception as e:
            logger.error(f"Error in request_approval activity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def _activity_send_performance_report(self, context: ProcessContext) -> Dict[str, Any]:
        """Process activity to send a performance report to a client.
        
        Args:
            context: Process activity context
            
        Returns:
            Dict: Activity results
        """
        try:
            # Get parameters
            client_id = context.get_parameter("client_id")
            campaign_id = context.get_parameter("campaign_id")
            report_data = context.get_parameter("report_data", {})
            
            if not client_id or not campaign_id or not report_data:
                return {
                    "success": False,
                    "error": "Missing required parameters: client_id, campaign_id, report_data"
                }
                
            # Check if client exists
            if client_id not in self.client_profiles:
                return {
                    "success": False,
                    "error": f"Client {client_id} not found"
                }
                
            # Prepare update content
            title = report_data.get("title", "Campaign Performance Report")
            
            # Build report content
            content = f"Campaign Performance Report: {report_data.get('period_description', 'Current Period')}\n\n"
            
            # Add highlights
            if "highlights" in report_data:
                content += "Performance Highlights:\n"
                for highlight in report_data["highlights"]:
                    content += f"- {highlight}\n"
                content += "\n"
                
            # Add key metrics
            if "metrics" in report_data:
                content += "Key Metrics:\n"
                for metric_name, value in report_data["metrics"].items():
                    if isinstance(value, (int, float)):
                        content += f"- {metric_name.replace('_', ' ').title()}: {value:,}\n"
                content += "\n"
                
            # Add insights
            if "insights" in report_data:
                content += "Insights:\n"
                for insight in report_data["insights"]:
                    content += f"- {insight}\n"
                content += "\n"
                
            # Add recommendations
            if "recommendations" in report_data:
                content += "Recommendations:\n"
                for recommendation in report_data["recommendations"]:
                    content += f"- {recommendation}\n"
                content += "\n"
                
            # Create update data
            update_data = {
                "update_type": "performance_report",
                "title": title,
                "content": content,
                "metrics": report_data.get("metrics", {}),
                "importance": "high",
                "send_immediately": True
            }
            
            # Create client update
            update_id = self.create_client_update(client_id, campaign_id, update_data)
            
            if not update_id:
                return {
                    "success": False,
                    "error": f"Failed to create performance report for client {client_id}, campaign {campaign_id}"
                }
                
            return {
                "success": True,
                "update_id": update_id,
                "client_id": client_id,
                "campaign_id": campaign_id,
                "status": "sent"
            }
            
        except Exception as e:
            logger.error(f"Error in send_performance_report activity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def _activity_process_feedback(self, context: ProcessContext) -> Dict[str, Any]:
        """Process activity to handle client feedback.
        
        Args:
            context: Process activity context
            
        Returns:
            Dict: Activity results
        """
        try:
            # Get parameters
            client_id = context.get_parameter("client_id")
            feedback_data = context.get_parameter("feedback_data", {})
            
            if not client_id or not feedback_data:
                return {
                    "success": False,
                    "error": "Missing required parameters: client_id, feedback_data"
                }
                
            # Check if client exists
            if client_id not in self.client_profiles:
                return {
                    "success": False,
                    "error": f"Client {client_id} not found"
                }
                
            feedback_type = feedback_data.get("type", "general")
            source = feedback_data.get("source", "unknown")
            content = feedback_data.get("content", "")
            
            # Store feedback in client metadata
            client = self.client_profiles[client_id]
            
            if "feedback_history" not in client.metadata:
                client.metadata["feedback_history"] = []
                
            client.metadata["feedback_history"].append({
                "type": feedback_type,
                "source": source,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            
            # If campaign-specific feedback, store in campaign as well
            campaign_id = feedback_data.get("campaign_id")
            if campaign_id and campaign_id in self.campaigns:
                campaign = self.campaigns[campaign_id]
                
                if "feedback" not in campaign:
                    campaign["feedback"] = []
                    
                campaign["feedback"].append({
                    "client_id": client_id,
                    "type": feedback_type,
                    "source": source,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                })
                
            # Send acknowledgment if requested
            if feedback_data.get("send_acknowledgment", False):
                message_data = {
                    "message_type": "acknowledgment",
                    "subject": "Feedback Received - Thank You",
                    "content": "Thank you for your feedback. We appreciate your input and will use it to improve our services.",
                    "priority": "normal",
                    "send_immediately": True
                }
                
                message_id = self.create_client_message(client_id, message_data)
                
            # Publish feedback event
            self.communication_protocol.publish(
                sender=self.agent_id,
                topic="client_notifications",
                content={
                    "event": "feedback_received",
                    "client_id": client_id,
                    "campaign_id": campaign_id,
                    "feedback_type": feedback_type,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return {
                "success": True,
                "client_id": client_id,
                "feedback_type": feedback_type,
                "status": "processed"
            }
            
        except Exception as e:
            logger.error(f"Error in process_feedback activity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
            
    def _activity_generate_summary(self, context: ProcessContext) -> Dict[str, Any]:
        """Process activity to generate a client summary.
        
        Args:
            context: Process activity context
            
        Returns:
            Dict: Activity results
        """
        try:
            # Get parameters
            client_id = context.get_parameter("client_id")
            
            if not client_id:
                return {
                    "success": False,
                    "error": "Missing required parameter: client_id"
                }
                
            # Generate client summary
            summary_result = self.generate_client_summary(client_id)
            
            if not summary_result.get("success", False):
                return {
                    "success": False,
                    "error": summary_result.get("error", "Failed to generate client summary")
                }
                
            return {
                "success": True,
                "client_id": client_id,
                "summary": summary_result.get("summary", {})
            }
            
        except Exception as e:
            logger.error(f"Error in generate_summary activity: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }


# Create example function to demonstrate the agent
def run_client_communication_example():
    """Run an example of the client communication agent functionality."""
    # Create client communication agent
    client_agent = ClientCommunicationAgent("client-demo-agent")
    
    # Start notification processing
    client_agent.start_notification_processing(interval=2)
    
    # Register a test client
    client_id = client_agent.register_client({
        "name": "John Smith",
        "email": "john.smith@example.com",
        "company": "Acme Corp",
        "role": "Marketing Director",
        "preferences": {
            "communication_frequency": "weekly",
            "notification_channels": ["email"],
            "report_format": "detailed"
        }
    })
    
    # Create a test campaign
    campaign_id = f"camp-{str(uuid.uuid4())[:8]}"
    
    # Associate campaign with client
    client_agent.associate_campaign(client_id, campaign_id, {
        "name": "Summer Promotion 2025",
        "status": "active",
        "metrics": {
            "impressions": 125000,
            "clicks": 8750,
            "conversions": 750,
            "ctr": 0.07,
            "conversion_rate": 0.086,
            "cost": 12500
        }
    })
    
    # Create an approval request
    request_id = client_agent.create_approval_request(client_id, campaign_id, {
        "request_type": "creative",
        "title": "Summer Promotion Banner Ads",
        "description": "Please review and approve these banner ad designs for the Summer Promotion campaign",
        "items_for_approval": [
            {
                "item_id": "banner-1",
                "title": "Summer Sale - 50% Off",
                "description": "Main banner for homepage",
                "asset_url": "https://example.com/assets/banner1.jpg"
            },
            {
                "item_id": "banner-2",
                "title": "Summer Styles - New Collection",
                "description": "Secondary banner for category pages",
                "asset_url": "https://example.com/assets/banner2.jpg"
            }
        ],
        "priority": "high",
        "send_immediately": True
    })
    
    # Wait for processing
    time.sleep(2)
    
    # Simulate client response to approval request
    client_response = {
        "client_id": client_id,
        "request_id": request_id,
        "decision": "approved",
        "decision_details": {
            "approved_items": ["banner-1", "banner-2"],
            "rejected_items": []
        },
        "feedback": "These look great! Ready to go live."
    }
    
    result = client_agent.process_client_response(client_response)
    print(f"Processed client response: {result['success']}")
    
    # Create a campaign update
    update_id = client_agent.create_client_update(client_id, campaign_id, {
        "update_type": "performance",
        "title": "Summer Promotion - Week 1 Performance",
        "content": "Your campaign is performing well above industry benchmarks. Click-through rate is 40% higher than average.",
        "metrics": {
            "impressions": 125000,
            "clicks": 8750,
            "conversions": 750,
            "ctr": 0.07,
            "conversion_rate": 0.086,
            "cost": 12500
        },
        "importance": "medium",
        "send_immediately": True
    })
    
    # Wait for processing
    time.sleep(2)
    
    # Generate client summary
    summary = client_agent.generate_client_summary(client_id)
    
    # Stop notification processing
    client_agent.stop_notification_processing()
    
    print(f"Client summary: {summary['success']}")
    if summary['success']:
        print(f"Active campaigns: {summary['summary']['active_campaigns']}")
        print(f"Pending approvals: {summary['summary']['communication']['pending_approvals']}")
    
    return {
        "client_agent": client_agent,
        "client_id": client_id,
        "campaign_id": campaign_id,
        "request_id": request_id,
        "update_id": update_id
    }

if __name__ == "__main__":
    run_client_communication_example()