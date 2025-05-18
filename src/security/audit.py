# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file keeps track of everything important that happens in the app.
# It's like a diary that remembers who did what and when they did it.

# High School Explanation:
# This module implements a comprehensive audit logging system to record security-relevant
# events within the application. It provides structured logging of user actions, system
# events, and security incidents with appropriate context information to support
# security monitoring, incident response, and compliance requirements.

import json
import logging
import os
import socket
import sys
import threading
import time
import traceback
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set, Callable
import uuid

from .encryption import encrypt_data, decrypt_data, get_encryption_service

# Configure logging
logger = logging.getLogger(__name__)


class EventCategory(str, Enum):
    """Categories of audit events."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    ADMIN = "admin"
    SYSTEM = "system"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    API = "api"


class EventSeverity(str, Enum):
    """Severity levels for audit events."""
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EventOutcome(str, Enum):
    """Possible outcomes of an event."""
    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"
    DENIED = "denied"
    UNKNOWN = "unknown"


class AuditEvent:
    """Represents an audit event with relevant context information."""
    
    def __init__(self, 
               category: Union[EventCategory, str], 
               action: str, 
               user_id: Optional[str] = None,
               resource_type: Optional[str] = None,
               resource_id: Optional[str] = None,
               outcome: Union[EventOutcome, str] = EventOutcome.SUCCESS,
               severity: Union[EventSeverity, str] = EventSeverity.INFO,
               details: Optional[Dict[str, Any]] = None,
               timestamp: Optional[datetime] = None,
               source_ip: Optional[str] = None,
               user_agent: Optional[str] = None,
               session_id: Optional[str] = None,
               request_id: Optional[str] = None):
        """
        Initialize an audit event.
        
        Args:
            category: Category of the event
            action: Action performed
            user_id: ID of the user who performed the action
            resource_type: Type of resource affected
            resource_id: ID of the resource affected
            outcome: Outcome of the action
            severity: Severity of the event
            details: Additional details about the event
            timestamp: When the event occurred
            source_ip: IP address of the client
            user_agent: User agent of the client
            session_id: ID of the user's session
            request_id: ID of the request
        """
        self.id = str(uuid.uuid4())
        self.category = category if isinstance(category, str) else category.value
        self.action = action
        self.user_id = user_id
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.outcome = outcome if isinstance(outcome, str) else outcome.value
        self.severity = severity if isinstance(severity, str) else severity.value
        self.details = details or {}
        self.timestamp = timestamp or datetime.now()
        self.source_ip = source_ip
        self.user_agent = user_agent
        self.session_id = session_id
        self.request_id = request_id
        
        # System context
        self.hostname = socket.gethostname()
        self.process_id = os.getpid()
        self.thread_id = threading.get_ident()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the event to a dictionary."""
        return {
            'id': self.id,
            'category': self.category,
            'action': self.action,
            'user_id': self.user_id,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'outcome': self.outcome,
            'severity': self.severity,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'source_ip': self.source_ip,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'request_id': self.request_id,
            'context': {
                'hostname': self.hostname,
                'process_id': self.process_id,
                'thread_id': self.thread_id
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEvent':
        """Create an event from a dictionary."""
        # Create a basic event
        event = cls(
            category=data['category'],
            action=data['action'],
            user_id=data.get('user_id'),
            resource_type=data.get('resource_type'),
            resource_id=data.get('resource_id'),
            outcome=data.get('outcome', EventOutcome.UNKNOWN.value),
            severity=data.get('severity', EventSeverity.INFO.value),
            details=data.get('details', {}),
            timestamp=datetime.fromisoformat(data['timestamp']) if 'timestamp' in data else None,
            source_ip=data.get('source_ip'),
            user_agent=data.get('user_agent'),
            session_id=data.get('session_id'),
            request_id=data.get('request_id')
        )
        
        # Set the ID if available
        if 'id' in data:
            event.id = data['id']
        
        # Set system context if available
        if 'context' in data:
            context = data['context']
            event.hostname = context.get('hostname', event.hostname)
            event.process_id = context.get('process_id', event.process_id)
            event.thread_id = context.get('thread_id', event.thread_id)
        
        return event
    
    def __str__(self) -> str:
        """Get a string representation of the event."""
        return (
            f"[{self.timestamp.isoformat()}] {self.severity.upper()} "
            f"{self.category}/{self.action} "
            f"user={self.user_id or 'none'} "
            f"resource={self.resource_type}:{self.resource_id if self.resource_id else 'none'} "
            f"outcome={self.outcome}"
        )


class AuditFilter:
    """Filter for audit events."""
    
    def __init__(self, 
               categories: Optional[Set[str]] = None,
               actions: Optional[Set[str]] = None,
               user_ids: Optional[Set[str]] = None,
               resource_types: Optional[Set[str]] = None,
               resource_ids: Optional[Set[str]] = None,
               outcomes: Optional[Set[str]] = None,
               severities: Optional[Set[str]] = None,
               start_time: Optional[datetime] = None,
               end_time: Optional[datetime] = None,
               source_ips: Optional[Set[str]] = None,
               session_ids: Optional[Set[str]] = None,
               request_ids: Optional[Set[str]] = None):
        """
        Initialize an audit filter.
        
        Args:
            categories: Set of categories to include
            actions: Set of actions to include
            user_ids: Set of user IDs to include
            resource_types: Set of resource types to include
            resource_ids: Set of resource IDs to include
            outcomes: Set of outcomes to include
            severities: Set of severities to include
            start_time: Start time for events
            end_time: End time for events
            source_ips: Set of source IPs to include
            session_ids: Set of session IDs to include
            request_ids: Set of request IDs to include
        """
        self.categories = categories
        self.actions = actions
        self.user_ids = user_ids
        self.resource_types = resource_types
        self.resource_ids = resource_ids
        self.outcomes = outcomes
        self.severities = severities
        self.start_time = start_time
        self.end_time = end_time
        self.source_ips = source_ips
        self.session_ids = session_ids
        self.request_ids = request_ids
    
    def matches(self, event: AuditEvent) -> bool:
        """
        Check if an event matches the filter.
        
        Args:
            event: Event to check
            
        Returns:
            True if the event matches the filter, False otherwise
        """
        if self.categories and event.category not in self.categories:
            return False
        
        if self.actions and event.action not in self.actions:
            return False
        
        if self.user_ids and (not event.user_id or event.user_id not in self.user_ids):
            return False
        
        if self.resource_types and (not event.resource_type or event.resource_type not in self.resource_types):
            return False
        
        if self.resource_ids and (not event.resource_id or event.resource_id not in self.resource_ids):
            return False
        
        if self.outcomes and event.outcome not in self.outcomes:
            return False
        
        if self.severities and event.severity not in self.severities:
            return False
        
        if self.start_time and event.timestamp < self.start_time:
            return False
        
        if self.end_time and event.timestamp > self.end_time:
            return False
        
        if self.source_ips and (not event.source_ip or event.source_ip not in self.source_ips):
            return False
        
        if self.session_ids and (not event.session_id or event.session_id not in self.session_ids):
            return False
        
        if self.request_ids and (not event.request_id or event.request_id not in self.request_ids):
            return False
        
        return True


class AuditLogger:
    """
    Logs and manages audit events.
    
    This class provides functionality for logging, storing, and querying
    audit events.
    """
    
    def __init__(self, 
               storage_dir: Optional[Union[str, Path]] = None,
               encrypt_logs: bool = False,
               encryption_key_name: str = "audit",
               max_memory_events: int = 1000,
               log_format: str = "json"):
        """
        Initialize the audit logger.
        
        Args:
            storage_dir: Directory to store audit logs.
                        If None, logs will only be stored in memory.
            encrypt_logs: Whether to encrypt stored logs
            encryption_key_name: Name of the encryption key to use
            max_memory_events: Maximum number of events to keep in memory
            log_format: Format for storing logs ('json' or 'jsonl')
        """
        self.storage_dir = Path(storage_dir) if storage_dir else None
        self.encrypt_logs = encrypt_logs
        self.encryption_key_name = encryption_key_name
        self.max_memory_events = max_memory_events
        self.log_format = log_format
        
        # In-memory event storage
        self.events = []
        
        # Event listeners
        self.listeners = []
        
        # Initialize storage directory if provided
        if self.storage_dir:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize the current log file
            self.current_log_file = self._get_log_file_path()
            
            # Create the archived logs directory
            archive_dir = self.storage_dir / 'archive'
            archive_dir.mkdir(exist_ok=True)
        else:
            self.current_log_file = None
    
    def _get_log_file_path(self) -> Optional[Path]:
        """Get the path to the current log file."""
        if not self.storage_dir:
            return None
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        if self.log_format == 'json':
            return self.storage_dir / f"audit_{date_str}.json"
        else:
            return self.storage_dir / f"audit_{date_str}.jsonl"
    
    def _rotate_log_file(self):
        """Rotate the log file if needed."""
        if not self.storage_dir:
            return
        
        new_log_file = self._get_log_file_path()
        
        if new_log_file != self.current_log_file:
            # Finalize the current log file if it exists
            if self.current_log_file and self.current_log_file.exists():
                # If the file is in JSON format and not encrypted, we need to finalize it
                if self.log_format == 'json' and not self.encrypt_logs:
                    try:
                        # Read the current content
                        with open(self.current_log_file, 'r') as f:
                            events = json.load(f)
                        
                        # Write it back with proper formatting
                        with open(self.current_log_file, 'w') as f:
                            json.dump(events, f, indent=2)
                    except Exception as e:
                        logger.error(f"Failed to finalize log file {self.current_log_file}: {e}")
            
            # Update the current log file
            self.current_log_file = new_log_file
    
    def _write_event_to_file(self, event: AuditEvent):
        """Write an event to the log file."""
        if not self.storage_dir:
            return
        
        # Rotate the log file if needed
        self._rotate_log_file()
        
        # Convert the event to a dictionary
        event_dict = event.to_dict()
        
        try:
            if self.log_format == 'json':
                # JSON format (one file per day with an array of events)
                if self.encrypt_logs:
                    # For encrypted logs, we need to write the entire file each time
                    events = []
                    
                    # Read existing events if the file exists
                    if self.current_log_file.exists():
                        try:
                            with open(self.current_log_file, 'rb') as f:
                                encrypted_data = f.read()
                            
                            # Decrypt the data
                            decrypted_data = decrypt_data(encrypted_data, self.encryption_key_name)
                            events = json.loads(decrypted_data.decode())
                        except Exception as e:
                            logger.error(f"Failed to read encrypted log file {self.current_log_file}: {e}")
                            # Start with an empty list if decryption fails
                            events = []
                    
                    # Add the new event
                    events.append(event_dict)
                    
                    # Encrypt and write the data
                    encrypted_data = encrypt_data(json.dumps(events), self.encryption_key_name)
                    with open(self.current_log_file, 'wb') as f:
                        f.write(encrypted_data)
                else:
                    # For unencrypted logs, we can append to the file
                    events = []
                    
                    # Read existing events if the file exists
                    if self.current_log_file.exists():
                        try:
                            with open(self.current_log_file, 'r') as f:
                                events = json.load(f)
                        except Exception as e:
                            logger.error(f"Failed to read log file {self.current_log_file}: {e}")
                            # Start with an empty list if reading fails
                            events = []
                    
                    # Add the new event
                    events.append(event_dict)
                    
                    # Write the data
                    with open(self.current_log_file, 'w') as f:
                        json.dump(events, f)
            else:
                # JSONL format (one event per line)
                if self.encrypt_logs:
                    # Encrypt the event
                    encrypted_data = encrypt_data(json.dumps(event_dict), self.encryption_key_name)
                    
                    # Write the encrypted data as base64
                    with open(self.current_log_file, 'ab') as f:
                        import base64
                        f.write(base64.b64encode(encrypted_data) + b'\n')
                else:
                    # Write the event as a JSON line
                    with open(self.current_log_file, 'a') as f:
                        f.write(json.dumps(event_dict) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit event to file: {e}")
    
    def add_listener(self, listener: Callable[[AuditEvent], None]):
        """
        Add a listener for audit events.
        
        Args:
            listener: Function that takes an audit event
        """
        self.listeners.append(listener)
    
    def remove_listener(self, listener: Callable[[AuditEvent], None]):
        """
        Remove a listener for audit events.
        
        Args:
            listener: Function to remove
        """
        if listener in self.listeners:
            self.listeners.remove(listener)
    
    def log_event(self, event: AuditEvent):
        """
        Log an audit event.
        
        Args:
            event: Event to log
        """
        # Add the event to the in-memory storage
        self.events.append(event)
        
        # Trim the in-memory storage if needed
        if len(self.events) > self.max_memory_events:
            self.events = self.events[-self.max_memory_events:]
        
        # Write the event to the log file
        self._write_event_to_file(event)
        
        # Notify listeners
        for listener in self.listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error in audit event listener: {e}")
        
        # Log to the application logger
        log_level = logging.INFO
        if event.severity == EventSeverity.WARNING.value:
            log_level = logging.WARNING
        elif event.severity == EventSeverity.ERROR.value:
            log_level = logging.ERROR
        elif event.severity == EventSeverity.CRITICAL.value:
            log_level = logging.CRITICAL
        
        logger.log(log_level, str(event))
    
    def log(self, 
          category: Union[EventCategory, str], 
          action: str, 
          user_id: Optional[str] = None,
          resource_type: Optional[str] = None,
          resource_id: Optional[str] = None,
          outcome: Union[EventOutcome, str] = EventOutcome.SUCCESS,
          severity: Union[EventSeverity, str] = EventSeverity.INFO,
          details: Optional[Dict[str, Any]] = None,
          source_ip: Optional[str] = None,
          user_agent: Optional[str] = None,
          session_id: Optional[str] = None,
          request_id: Optional[str] = None):
        """
        Create and log an audit event.
        
        Args:
            category: Category of the event
            action: Action performed
            user_id: ID of the user who performed the action
            resource_type: Type of resource affected
            resource_id: ID of the resource affected
            outcome: Outcome of the action
            severity: Severity of the event
            details: Additional details about the event
            source_ip: IP address of the client
            user_agent: User agent of the client
            session_id: ID of the user's session
            request_id: ID of the request
        """
        event = AuditEvent(
            category=category,
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
            severity=severity,
            details=details,
            source_ip=source_ip,
            user_agent=user_agent,
            session_id=session_id,
            request_id=request_id
        )
        
        self.log_event(event)
    
    def query_events(self, 
                   filter: Optional[AuditFilter] = None, 
                   limit: Optional[int] = None,
                   include_archived: bool = False) -> List[AuditEvent]:
        """
        Query audit events based on a filter.
        
        Args:
            filter: Filter to apply
            limit: Maximum number of events to return
            include_archived: Whether to include archived events
            
        Returns:
            List of matching events
        """
        # Start with in-memory events
        results = list(self.events)
        
        # Add events from the current log file
        if self.storage_dir and self.current_log_file and self.current_log_file.exists():
            try:
                if self.log_format == 'json':
                    if self.encrypt_logs:
                        # Read and decrypt the file
                        with open(self.current_log_file, 'rb') as f:
                            encrypted_data = f.read()
                        
                        decrypted_data = decrypt_data(encrypted_data, self.encryption_key_name)
                        file_events = json.loads(decrypted_data.decode())
                    else:
                        # Read the file directly
                        with open(self.current_log_file, 'r') as f:
                            file_events = json.load(f)
                    
                    # Convert to AuditEvent objects
                    for event_dict in file_events:
                        if event_dict['id'] not in {e.id for e in results}:
                            results.append(AuditEvent.from_dict(event_dict))
                else:
                    # Read JSONL file
                    with open(self.current_log_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            
                            if self.encrypt_logs:
                                # Decrypt the line
                                import base64
                                encrypted_data = base64.b64decode(line)
                                decrypted_data = decrypt_data(encrypted_data, self.encryption_key_name)
                                event_dict = json.loads(decrypted_data.decode())
                            else:
                                # Parse the JSON line
                                event_dict = json.loads(line)
                            
                            if event_dict['id'] not in {e.id for e in results}:
                                results.append(AuditEvent.from_dict(event_dict))
            except Exception as e:
                logger.error(f"Failed to read events from log file {self.current_log_file}: {e}")
        
        # Add events from archived log files
        if include_archived and self.storage_dir:
            archive_dir = self.storage_dir / 'archive'
            if archive_dir.exists():
                for log_file in archive_dir.glob(f"audit_*.{self.log_format}"):
                    try:
                        if self.log_format == 'json':
                            if self.encrypt_logs:
                                # Read and decrypt the file
                                with open(log_file, 'rb') as f:
                                    encrypted_data = f.read()
                                
                                decrypted_data = decrypt_data(encrypted_data, self.encryption_key_name)
                                file_events = json.loads(decrypted_data.decode())
                            else:
                                # Read the file directly
                                with open(log_file, 'r') as f:
                                    file_events = json.load(f)
                            
                            # Convert to AuditEvent objects
                            for event_dict in file_events:
                                if event_dict['id'] not in {e.id for e in results}:
                                    results.append(AuditEvent.from_dict(event_dict))
                        else:
                            # Read JSONL file
                            with open(log_file, 'r') as f:
                                for line in f:
                                    line = line.strip()
                                    if not line:
                                        continue
                                    
                                    if self.encrypt_logs:
                                        # Decrypt the line
                                        import base64
                                        encrypted_data = base64.b64decode(line)
                                        decrypted_data = decrypt_data(encrypted_data, self.encryption_key_name)
                                        event_dict = json.loads(decrypted_data.decode())
                                    else:
                                        # Parse the JSON line
                                        event_dict = json.loads(line)
                                    
                                    if event_dict['id'] not in {e.id for e in results}:
                                        results.append(AuditEvent.from_dict(event_dict))
                    except Exception as e:
                        logger.error(f"Failed to read events from archived log file {log_file}: {e}")
        
        # Apply the filter
        if filter:
            results = [event for event in results if filter.matches(event)]
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda e: e.timestamp, reverse=True)
        
        # Apply the limit
        if limit is not None and limit > 0:
            results = results[:limit]
        
        return results
    
    def archive_logs(self, before_date: datetime) -> int:
        """
        Archive logs older than a specified date.
        
        Args:
            before_date: Date to archive logs before
            
        Returns:
            Number of archived log files
        """
        if not self.storage_dir:
            return 0
        
        archive_dir = self.storage_dir / 'archive'
        archive_dir.mkdir(exist_ok=True)
        
        archived_count = 0
        
        # Find log files to archive
        for log_file in self.storage_dir.glob(f"audit_*.{self.log_format}"):
            # Parse the date from the filename
            try:
                date_str = log_file.stem.split('_')[1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Check if the file is old enough to archive
                if file_date < before_date:
                    # Move the file to the archive directory
                    target_path = archive_dir / log_file.name
                    log_file.rename(target_path)
                    archived_count += 1
            except Exception as e:
                logger.error(f"Failed to archive log file {log_file}: {e}")
        
        return archived_count
    
    def delete_archived_logs(self, before_date: datetime) -> int:
        """
        Delete archived logs older than a specified date.
        
        Args:
            before_date: Date to delete logs before
            
        Returns:
            Number of deleted log files
        """
        if not self.storage_dir:
            return 0
        
        archive_dir = self.storage_dir / 'archive'
        if not archive_dir.exists():
            return 0
        
        deleted_count = 0
        
        # Find archived log files to delete
        for log_file in archive_dir.glob(f"audit_*.{self.log_format}"):
            # Parse the date from the filename
            try:
                date_str = log_file.stem.split('_')[1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Check if the file is old enough to delete
                if file_date < before_date:
                    # Delete the file
                    log_file.unlink()
                    deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete archived log file {log_file}: {e}")
        
        return deleted_count
    
    def export_events(self, 
                    filter: Optional[AuditFilter] = None,
                    format: str = 'json',
                    output_file: Optional[Union[str, Path]] = None) -> Optional[str]:
        """
        Export audit events to a file or string.
        
        Args:
            filter: Filter to apply
            format: Export format ('json', 'jsonl', or 'csv')
            output_file: File to write the export to
            
        Returns:
            Exported data as a string if output_file is None
        """
        # Query the events
        events = self.query_events(filter, include_archived=True)
        
        # Convert to dictionaries
        event_dicts = [event.to_dict() for event in events]
        
        if format == 'json':
            # Export as JSON
            output = json.dumps(event_dicts, indent=2)
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(output)
                return None
            else:
                return output
        
        elif format == 'jsonl':
            # Export as JSONL
            output = '\n'.join(json.dumps(event_dict) for event_dict in event_dicts)
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(output)
                return None
            else:
                return output
        
        elif format == 'csv':
            # Export as CSV
            import csv
            import io
            
            output_buffer = io.StringIO()
            
            # Define the CSV header
            header = [
                'id', 'timestamp', 'category', 'action', 'user_id',
                'resource_type', 'resource_id', 'outcome', 'severity',
                'source_ip', 'user_agent', 'session_id', 'request_id',
                'hostname', 'process_id', 'thread_id', 'details'
            ]
            
            # Write the CSV
            writer = csv.DictWriter(output_buffer, fieldnames=header)
            writer.writeheader()
            
            for event_dict in event_dicts:
                # Flatten the context and details
                row = {
                    'id': event_dict['id'],
                    'timestamp': event_dict['timestamp'],
                    'category': event_dict['category'],
                    'action': event_dict['action'],
                    'user_id': event_dict.get('user_id', ''),
                    'resource_type': event_dict.get('resource_type', ''),
                    'resource_id': event_dict.get('resource_id', ''),
                    'outcome': event_dict['outcome'],
                    'severity': event_dict['severity'],
                    'source_ip': event_dict.get('source_ip', ''),
                    'user_agent': event_dict.get('user_agent', ''),
                    'session_id': event_dict.get('session_id', ''),
                    'request_id': event_dict.get('request_id', ''),
                    'hostname': event_dict['context'].get('hostname', ''),
                    'process_id': event_dict['context'].get('process_id', ''),
                    'thread_id': event_dict['context'].get('thread_id', ''),
                    'details': json.dumps(event_dict.get('details', {}))
                }
                
                writer.writerow(row)
            
            output = output_buffer.getvalue()
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(output)
                return None
            else:
                return output
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def generate_audit_report(self, 
                           start_time: datetime,
                           end_time: datetime,
                           categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate an audit report for a specific time period.
        
        Args:
            start_time: Start time for the report
            end_time: End time for the report
            categories: Optional list of categories to include
            
        Returns:
            Dictionary containing the audit report
        """
        # Create a filter for the time period
        filter = AuditFilter(
            categories=set(categories) if categories else None,
            start_time=start_time,
            end_time=end_time
        )
        
        # Query the events
        events = self.query_events(filter, include_archived=True)
        
        # Calculate statistics
        total_events = len(events)
        events_by_category = {}
        events_by_action = {}
        events_by_outcome = {}
        events_by_severity = {}
        events_by_user = {}
        
        for event in events:
            # Count by category
            if event.category not in events_by_category:
                events_by_category[event.category] = 0
            events_by_category[event.category] += 1
            
            # Count by action
            action_key = f"{event.category}/{event.action}"
            if action_key not in events_by_action:
                events_by_action[action_key] = 0
            events_by_action[action_key] += 1
            
            # Count by outcome
            if event.outcome not in events_by_outcome:
                events_by_outcome[event.outcome] = 0
            events_by_outcome[event.outcome] += 1
            
            # Count by severity
            if event.severity not in events_by_severity:
                events_by_severity[event.severity] = 0
            events_by_severity[event.severity] += 1
            
            # Count by user
            if event.user_id:
                if event.user_id not in events_by_user:
                    events_by_user[event.user_id] = 0
                events_by_user[event.user_id] += 1
        
        # Sort the statistics
        events_by_category = {k: v for k, v in sorted(events_by_category.items(), key=lambda item: item[1], reverse=True)}
        events_by_action = {k: v for k, v in sorted(events_by_action.items(), key=lambda item: item[1], reverse=True)}
        events_by_outcome = {k: v for k, v in sorted(events_by_outcome.items(), key=lambda item: item[1], reverse=True)}
        events_by_severity = {k: v for k, v in sorted(events_by_severity.items(), key=lambda item: item[1], reverse=True)}
        events_by_user = {k: v for k, v in sorted(events_by_user.items(), key=lambda item: item[1], reverse=True)}
        
        # Find significant events
        significant_events = []
        
        for event in events:
            # Include critical and error events
            if event.severity in (EventSeverity.CRITICAL.value, EventSeverity.ERROR.value):
                significant_events.append(event.to_dict())
            
            # Include failed authentication and authorization events
            elif event.category in (EventCategory.AUTHENTICATION.value, EventCategory.AUTHORIZATION.value) and event.outcome == EventOutcome.FAILURE.value:
                significant_events.append(event.to_dict())
        
        # Limit to top 100 significant events
        significant_events = significant_events[:100]
        
        # Create the report
        report = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'generated_at': datetime.now().isoformat(),
            'statistics': {
                'total_events': total_events,
                'by_category': events_by_category,
                'by_action': events_by_action,
                'by_outcome': events_by_outcome,
                'by_severity': events_by_severity,
                'by_user': events_by_user
            },
            'significant_events': significant_events
        }
        
        return report