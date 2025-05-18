# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps make sure our app follows important rules about protecting people's information.
# It's like having a guardian that makes sure we're treating people's personal data with respect.

# High School Explanation:
# This module implements compliance features for various data protection regulations
# like GDPR and CCPA. It provides tools for managing user consent, data subject rights,
# data minimization, retention periods, and documenting data processing activities to
# ensure the platform meets its legal obligations.

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable, Set
from enum import Enum
import uuid

from .encryption import encrypt_data, decrypt_data, get_encryption_service

# Configure logging
logger = logging.getLogger(__name__)


class ConsentType(str, Enum):
    """Types of user consent."""
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    PROFILING = "profiling"
    ESSENTIAL = "essential"
    THIRD_PARTY = "third_party"


class RightType(str, Enum):
    """Types of data subject rights."""
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    RESTRICTION = "restriction"
    PORTABILITY = "portability"
    OBJECT = "object"
    AUTOMATED_DECISION = "automated_decision"


class RetentionPolicy(str, Enum):
    """Types of data retention policies."""
    INDEFINITE = "indefinite"
    FIXED_PERIOD = "fixed_period"
    UNTIL_PURPOSE_COMPLETE = "until_purpose_complete"
    LEGAL_REQUIREMENT = "legal_requirement"
    USER_REQUEST = "user_request"


class DataCategory(str, Enum):
    """Categories of personal data."""
    BASIC_INFO = "basic_info"  # Name, email, etc.
    CONTACT_INFO = "contact_info"  # Address, phone number, etc.
    IDENTIFICATION = "identification"  # ID numbers, passport, etc.
    FINANCIAL = "financial"  # Credit card, bank account, etc.
    PROFESSIONAL = "professional"  # Job title, company, etc.
    TECHNICAL = "technical"  # IP address, cookies, etc.
    USAGE = "usage"  # User behavior, preferences, etc.
    LOCATION = "location"  # GPS data, IP-based location, etc.
    SENSITIVE = "sensitive"  # Health, religion, politics, etc.


class ProcessingPurpose(str, Enum):
    """Purposes for processing personal data."""
    SERVICE_PROVISION = "service_provision"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    LEGAL_OBLIGATION = "legal_obligation"
    CONTRACT_FULFILLMENT = "contract_fulfillment"
    LEGITIMATE_INTEREST = "legitimate_interest"
    PUBLIC_INTEREST = "public_interest"
    VITAL_INTEREST = "vital_interest"


class ComplianceError(Exception):
    """Base exception for compliance errors."""
    pass


class ConsentNotFoundError(ComplianceError):
    """Raised when consent is required but not found."""
    pass


class DataRetentionPolicy:
    """
    Defines and applies data retention policies.
    
    This class manages the lifecycle of data, determining when data should be
    archived or deleted based on configurable policies.
    """
    
    def __init__(self, 
                storage_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the data retention policy manager.
        
        Args:
            storage_dir: Directory to store retention policy configurations and logs.
                        If None, settings will only be stored in memory.
        """
        self.storage_dir = Path(storage_dir) if storage_dir else None
        self.policies = {}
        self.retention_periods = {}
        self.deletion_hooks = {}
        
        # Initialize storage directory if provided
        if self.storage_dir:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            self._load_policies()
    
    def _load_policies(self):
        """Load retention policies from storage."""
        if not self.storage_dir:
            return
        
        policy_file = self.storage_dir / 'retention_policies.json'
        if policy_file.exists():
            try:
                with open(policy_file, 'r') as f:
                    data = json.load(f)
                
                self.policies = data.get('policies', {})
                self.retention_periods = data.get('retention_periods', {})
                
                logger.info(f"Loaded {len(self.policies)} retention policies")
            except Exception as e:
                logger.error(f"Failed to load retention policies: {e}")
    
    def _save_policies(self):
        """Save retention policies to storage."""
        if not self.storage_dir:
            return
        
        policy_file = self.storage_dir / 'retention_policies.json'
        
        try:
            with open(policy_file, 'w') as f:
                json.dump({
                    'policies': self.policies,
                    'retention_periods': self.retention_periods
                }, f, indent=2)
            
            logger.debug("Saved retention policies")
        except Exception as e:
            logger.error(f"Failed to save retention policies: {e}")
    
    def set_retention_period(self, 
                           data_category: Union[DataCategory, str], 
                           period_days: int):
        """
        Set the retention period for a data category.
        
        Args:
            data_category: Category of data
            period_days: Retention period in days
        """
        if isinstance(data_category, DataCategory):
            data_category = data_category.value
        
        self.retention_periods[data_category] = period_days
        logger.info(f"Set retention period for {data_category} to {period_days} days")
        
        self._save_policies()
    
    def get_retention_period(self, 
                          data_category: Union[DataCategory, str]) -> Optional[int]:
        """
        Get the retention period for a data category.
        
        Args:
            data_category: Category of data
            
        Returns:
            Retention period in days, or None if not set
        """
        if isinstance(data_category, DataCategory):
            data_category = data_category.value
        
        return self.retention_periods.get(data_category)
    
    def set_policy(self, 
                 data_type: str, 
                 policy_type: Union[RetentionPolicy, str], 
                 parameters: Optional[Dict[str, Any]] = None):
        """
        Set a retention policy for a specific data type.
        
        Args:
            data_type: Type of data the policy applies to
            policy_type: Type of retention policy
            parameters: Additional parameters for the policy
        """
        if isinstance(policy_type, RetentionPolicy):
            policy_type = policy_type.value
        
        self.policies[data_type] = {
            'type': policy_type,
            'parameters': parameters or {}
        }
        
        logger.info(f"Set {policy_type} retention policy for {data_type}")
        self._save_policies()
    
    def get_policy(self, data_type: str) -> Optional[Dict[str, Any]]:
        """
        Get the retention policy for a data type.
        
        Args:
            data_type: Type of data
            
        Returns:
            Policy configuration, or None if not set
        """
        return self.policies.get(data_type)
    
    def register_deletion_hook(self, 
                              data_type: str, 
                              hook: Callable[[str, Any], None]):
        """
        Register a function to be called when data of a specific type is deleted.
        
        Args:
            data_type: Type of data
            hook: Function to call with (data_id, data) when data is deleted
        """
        if data_type not in self.deletion_hooks:
            self.deletion_hooks[data_type] = []
        
        self.deletion_hooks[data_type].append(hook)
        logger.debug(f"Registered deletion hook for {data_type}")
    
    def should_retain(self, 
                    data_type: str, 
                    creation_date: datetime, 
                    last_access_date: Optional[datetime] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Determine if data should be retained based on the applicable policy.
        
        Args:
            data_type: Type of data
            creation_date: When the data was created
            last_access_date: When the data was last accessed
            metadata: Additional metadata about the data
            
        Returns:
            True if the data should be retained, False if it should be deleted
        """
        # Get the policy for this data type
        policy = self.get_policy(data_type)
        if not policy:
            # No policy means retain by default
            return True
        
        policy_type = policy['type']
        parameters = policy['parameters']
        
        now = datetime.now()
        
        # Check if data should be retained based on policy type
        if policy_type == RetentionPolicy.INDEFINITE.value:
            return True
            
        elif policy_type == RetentionPolicy.FIXED_PERIOD.value:
            period_days = parameters.get('period_days')
            if period_days is None:
                # Try to get the period from the data category
                data_category = parameters.get('data_category')
                if data_category:
                    period_days = self.get_retention_period(data_category)
            
            if not period_days:
                logger.warning(f"No retention period specified for {data_type}")
                return True
            
            cutoff_date = now - timedelta(days=period_days)
            return creation_date > cutoff_date
            
        elif policy_type == RetentionPolicy.UNTIL_PURPOSE_COMPLETE.value:
            purpose_complete = parameters.get('purpose_complete', False)
            if isinstance(purpose_complete, str) and metadata:
                # The purpose_complete is a key in the metadata
                purpose_complete = metadata.get(purpose_complete, False)
            
            return not purpose_complete
            
        elif policy_type == RetentionPolicy.LEGAL_REQUIREMENT.value:
            # Legal requirements always mean retain
            return True
            
        elif policy_type == RetentionPolicy.USER_REQUEST.value:
            deletion_requested = parameters.get('deletion_requested', False)
            if isinstance(deletion_requested, str) and metadata:
                # The deletion_requested is a key in the metadata
                deletion_requested = metadata.get(deletion_requested, False)
            
            return not deletion_requested
            
        # Unknown policy type, retain by default
        logger.warning(f"Unknown retention policy type: {policy_type}")
        return True
    
    def execute_deletion(self, 
                       data_type: str, 
                       data_id: str, 
                       data: Any) -> bool:
        """
        Execute the deletion of data, calling any registered hooks.
        
        Args:
            data_type: Type of data
            data_id: Identifier for the data
            data: The data to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Call any registered hooks
            hooks = self.deletion_hooks.get(data_type, [])
            for hook in hooks:
                try:
                    hook(data_id, data)
                except Exception as e:
                    logger.error(f"Error in deletion hook for {data_type}: {e}")
            
            logger.info(f"Deleted {data_type} data with ID {data_id}")
            
            # Log the deletion for audit purposes
            if self.storage_dir:
                log_file = self.storage_dir / 'deletion_log.jsonl'
                with open(log_file, 'a') as f:
                    log_entry = {
                        'timestamp': datetime.now().isoformat(),
                        'data_type': data_type,
                        'data_id': data_id,
                        'reason': 'retention_policy'
                    }
                    f.write(json.dumps(log_entry) + '\n')
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete {data_type} data with ID {data_id}: {e}")
            return False
    
    def apply_retention_policies(self, 
                              data_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply retention policies to a list of data items.
        
        Args:
            data_items: List of data items with keys:
                        - data_type: Type of data
                        - data_id: Identifier for the data
                        - creation_date: When the data was created
                        - last_access_date: When the data was last accessed (optional)
                        - metadata: Additional metadata (optional)
                        - data: The actual data
            
        Returns:
            List of data items that should be retained
        """
        retained_items = []
        
        for item in data_items:
            data_type = item['data_type']
            data_id = item['data_id']
            creation_date = item['creation_date']
            last_access_date = item.get('last_access_date')
            metadata = item.get('metadata', {})
            data = item['data']
            
            if self.should_retain(data_type, creation_date, last_access_date, metadata):
                retained_items.append(item)
            else:
                self.execute_deletion(data_type, data_id, data)
        
        return retained_items


class GDPRCompliance:
    """
    Implements GDPR compliance features.
    
    This class provides functionality to manage user consent, data subject rights,
    and other GDPR requirements.
    """
    
    def __init__(self, 
                storage_dir: Optional[Union[str, Path]] = None,
                encryption_key_name: str = "gdpr"):
        """
        Initialize the GDPR compliance manager.
        
        Args:
            storage_dir: Directory to store GDPR-related data.
                        If None, data will only be stored in memory.
            encryption_key_name: Name of the encryption key to use for GDPR data.
        """
        self.storage_dir = Path(storage_dir) if storage_dir else None
        self.encryption_key_name = encryption_key_name
        
        # In-memory storage
        self.consents = {}
        self.data_processing_records = {}
        self.data_subject_requests = {}
        
        # Initialize storage directory if provided
        if self.storage_dir:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (self.storage_dir / 'consents').mkdir(exist_ok=True)
            (self.storage_dir / 'processing_records').mkdir(exist_ok=True)
            (self.storage_dir / 'data_subject_requests').mkdir(exist_ok=True)
    
    def _save_consent(self, user_id: str, consent_data: Dict[str, Any]):
        """Save consent data to storage."""
        if not self.storage_dir:
            return
        
        consent_file = self.storage_dir / 'consents' / f"{user_id}.json"
        
        try:
            # Encrypt the consent data
            encrypted_data = encrypt_data(consent_data, self.encryption_key_name)
            
            with open(consent_file, 'wb') as f:
                f.write(encrypted_data)
            
            logger.debug(f"Saved consent data for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to save consent data for user {user_id}: {e}")
    
    def _load_consent(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load consent data from storage."""
        if not self.storage_dir:
            return None
        
        consent_file = self.storage_dir / 'consents' / f"{user_id}.json"
        
        if not consent_file.exists():
            return None
        
        try:
            with open(consent_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt the consent data
            consent_data = decrypt_data(encrypted_data, self.encryption_key_name)
            return json.loads(consent_data.decode())
        except Exception as e:
            logger.error(f"Failed to load consent data for user {user_id}: {e}")
            return None
    
    def record_consent(self, 
                     user_id: str, 
                     consent_type: Union[ConsentType, str], 
                     granted: bool, 
                     timestamp: Optional[datetime] = None,
                     details: Optional[Dict[str, Any]] = None):
        """
        Record user consent for a specific purpose.
        
        Args:
            user_id: Identifier for the user
            consent_type: Type of consent
            granted: Whether consent was granted
            timestamp: When the consent was recorded
            details: Additional details about the consent
        """
        if isinstance(consent_type, ConsentType):
            consent_type = consent_type.value
        
        timestamp = timestamp or datetime.now()
        
        # Load existing consent data
        if user_id in self.consents:
            consent_data = self.consents[user_id]
        else:
            stored_consent = self._load_consent(user_id)
            if stored_consent:
                consent_data = stored_consent
            else:
                consent_data = {
                    'user_id': user_id,
                    'consents': {},
                    'history': []
                }
        
        # Update consent status
        consent_data['consents'][consent_type] = {
            'granted': granted,
            'timestamp': timestamp.isoformat(),
            'details': details or {}
        }
        
        # Add to history
        consent_data['history'].append({
            'consent_type': consent_type,
            'granted': granted,
            'timestamp': timestamp.isoformat(),
            'details': details or {}
        })
        
        # Save the updated consent data
        self.consents[user_id] = consent_data
        self._save_consent(user_id, consent_data)
        
        logger.info(f"Recorded {consent_type} consent for user {user_id}: {'granted' if granted else 'denied'}")
    
    def check_consent(self, 
                    user_id: str, 
                    consent_type: Union[ConsentType, str]) -> bool:
        """
        Check if a user has granted consent for a specific purpose.
        
        Args:
            user_id: Identifier for the user
            consent_type: Type of consent to check
            
        Returns:
            True if consent was granted, False otherwise
            
        Raises:
            ConsentNotFoundError: If no consent record exists for the user and type
        """
        if isinstance(consent_type, ConsentType):
            consent_type = consent_type.value
        
        # Load consent data if not already loaded
        if user_id not in self.consents:
            stored_consent = self._load_consent(user_id)
            if stored_consent:
                self.consents[user_id] = stored_consent
        
        # Check if consent exists
        if user_id not in self.consents or consent_type not in self.consents[user_id]['consents']:
            raise ConsentNotFoundError(f"No consent record found for user {user_id} and type {consent_type}")
        
        return self.consents[user_id]['consents'][consent_type]['granted']
    
    def get_consent_history(self, 
                          user_id: str, 
                          consent_type: Optional[Union[ConsentType, str]] = None) -> List[Dict[str, Any]]:
        """
        Get the consent history for a user.
        
        Args:
            user_id: Identifier for the user
            consent_type: Optional type of consent to filter by
            
        Returns:
            List of consent history entries
        """
        if isinstance(consent_type, ConsentType):
            consent_type = consent_type.value
        
        # Load consent data if not already loaded
        if user_id not in self.consents:
            stored_consent = self._load_consent(user_id)
            if stored_consent:
                self.consents[user_id] = stored_consent
            else:
                return []
        
        history = self.consents[user_id].get('history', [])
        
        # Filter by consent type if specified
        if consent_type:
            history = [entry for entry in history if entry['consent_type'] == consent_type]
        
        return history
    
    def record_data_processing_activity(self, 
                                      activity_id: str, 
                                      data_category: Union[DataCategory, str],
                                      processing_purpose: Union[ProcessingPurpose, str],
                                      user_ids: List[str],
                                      legal_basis: str,
                                      timestamp: Optional[datetime] = None,
                                      details: Optional[Dict[str, Any]] = None):
        """
        Record a data processing activity for GDPR compliance documentation.
        
        Args:
            activity_id: Identifier for the activity
            data_category: Category of data being processed
            processing_purpose: Purpose of the processing
            user_ids: List of user IDs affected by the processing
            legal_basis: Legal basis for the processing
            timestamp: When the processing occurred
            details: Additional details about the processing
        """
        if isinstance(data_category, DataCategory):
            data_category = data_category.value
            
        if isinstance(processing_purpose, ProcessingPurpose):
            processing_purpose = processing_purpose.value
            
        timestamp = timestamp or datetime.now()
        
        activity_record = {
            'activity_id': activity_id,
            'data_category': data_category,
            'processing_purpose': processing_purpose,
            'user_ids': user_ids,
            'legal_basis': legal_basis,
            'timestamp': timestamp.isoformat(),
            'details': details or {}
        }
        
        # Save the activity record
        self.data_processing_records[activity_id] = activity_record
        
        # Save to storage if configured
        if self.storage_dir:
            record_file = self.storage_dir / 'processing_records' / f"{activity_id}.json"
            
            try:
                # Encrypt the record
                encrypted_data = encrypt_data(activity_record, self.encryption_key_name)
                
                with open(record_file, 'wb') as f:
                    f.write(encrypted_data)
                
                logger.debug(f"Saved processing activity record: {activity_id}")
            except Exception as e:
                logger.error(f"Failed to save processing activity record: {e}")
        
        logger.info(f"Recorded data processing activity: {activity_id}")
    
    def get_processing_activities_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all processing activities that affected a specific user.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            List of processing activity records
        """
        # Load processing records from storage if needed
        if not self.data_processing_records and self.storage_dir:
            record_dir = self.storage_dir / 'processing_records'
            for record_file in record_dir.glob('*.json'):
                try:
                    with open(record_file, 'rb') as f:
                        encrypted_data = f.read()
                    
                    # Decrypt the record
                    record_data = decrypt_data(encrypted_data, self.encryption_key_name)
                    record = json.loads(record_data.decode())
                    
                    self.data_processing_records[record['activity_id']] = record
                except Exception as e:
                    logger.error(f"Failed to load processing record {record_file}: {e}")
        
        # Filter activities for the specified user
        return [
            record for record in self.data_processing_records.values()
            if user_id in record['user_ids']
        ]
    
    def create_data_subject_request(self, 
                                  user_id: str, 
                                  right_type: Union[RightType, str], 
                                  details: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new data subject request.
        
        Args:
            user_id: Identifier for the user
            right_type: Type of right being exercised
            details: Additional details about the request
            
        Returns:
            Request ID
        """
        if isinstance(right_type, RightType):
            right_type = right_type.value
            
        request_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        request = {
            'request_id': request_id,
            'user_id': user_id,
            'right_type': right_type,
            'status': 'pending',
            'created_at': timestamp.isoformat(),
            'updated_at': timestamp.isoformat(),
            'completed_at': None,
            'details': details or {},
            'history': [
                {
                    'status': 'pending',
                    'timestamp': timestamp.isoformat(),
                    'comment': 'Request created'
                }
            ]
        }
        
        # Save the request
        self.data_subject_requests[request_id] = request
        
        # Save to storage if configured
        if self.storage_dir:
            request_file = self.storage_dir / 'data_subject_requests' / f"{request_id}.json"
            
            try:
                # Encrypt the request
                encrypted_data = encrypt_data(request, self.encryption_key_name)
                
                with open(request_file, 'wb') as f:
                    f.write(encrypted_data)
                
                logger.debug(f"Saved data subject request: {request_id}")
            except Exception as e:
                logger.error(f"Failed to save data subject request: {e}")
        
        logger.info(f"Created data subject request: {request_id} for user {user_id}")
        
        return request_id
    
    def update_data_subject_request(self, 
                                  request_id: str, 
                                  status: str, 
                                  comment: Optional[str] = None,
                                  details: Optional[Dict[str, Any]] = None):
        """
        Update the status of a data subject request.
        
        Args:
            request_id: Identifier for the request
            status: New status for the request
            comment: Optional comment about the update
            details: Additional details to update
        """
        if request_id not in self.data_subject_requests:
            # Try to load from storage
            if self.storage_dir:
                request_file = self.storage_dir / 'data_subject_requests' / f"{request_id}.json"
                
                if request_file.exists():
                    try:
                        with open(request_file, 'rb') as f:
                            encrypted_data = f.read()
                        
                        # Decrypt the request
                        request_data = decrypt_data(encrypted_data, self.encryption_key_name)
                        request = json.loads(request_data.decode())
                        
                        self.data_subject_requests[request_id] = request
                    except Exception as e:
                        logger.error(f"Failed to load data subject request {request_id}: {e}")
        
        if request_id not in self.data_subject_requests:
            raise ValueError(f"Data subject request {request_id} not found")
        
        timestamp = datetime.now()
        request = self.data_subject_requests[request_id]
        
        # Update the request
        request['status'] = status
        request['updated_at'] = timestamp.isoformat()
        
        if status in ('completed', 'rejected'):
            request['completed_at'] = timestamp.isoformat()
        
        # Update details if provided
        if details:
            request['details'].update(details)
        
        # Add to history
        request['history'].append({
            'status': status,
            'timestamp': timestamp.isoformat(),
            'comment': comment or f"Status updated to {status}"
        })
        
        # Save to storage if configured
        if self.storage_dir:
            request_file = self.storage_dir / 'data_subject_requests' / f"{request_id}.json"
            
            try:
                # Encrypt the request
                encrypted_data = encrypt_data(request, self.encryption_key_name)
                
                with open(request_file, 'wb') as f:
                    f.write(encrypted_data)
                
                logger.debug(f"Updated data subject request: {request_id}")
            except Exception as e:
                logger.error(f"Failed to update data subject request: {e}")
        
        logger.info(f"Updated data subject request: {request_id} to status {status}")
    
    def get_data_subject_requests_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all data subject requests for a specific user.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            List of data subject request records
        """
        # Load requests from storage if needed
        if not self.data_subject_requests and self.storage_dir:
            request_dir = self.storage_dir / 'data_subject_requests'
            for request_file in request_dir.glob('*.json'):
                try:
                    with open(request_file, 'rb') as f:
                        encrypted_data = f.read()
                    
                    # Decrypt the request
                    request_data = decrypt_data(encrypted_data, self.encryption_key_name)
                    request = json.loads(request_data.decode())
                    
                    self.data_subject_requests[request['request_id']] = request
                except Exception as e:
                    logger.error(f"Failed to load data subject request {request_file}: {e}")
        
        # Filter requests for the specified user
        return [
            request for request in self.data_subject_requests.values()
            if request['user_id'] == user_id
        ]
    
    def generate_data_export(self, user_id: str) -> Dict[str, Any]:
        """
        Generate a data export for a user, containing all their personal data.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            Dictionary containing the user's personal data
        """
        export = {
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'consents': self.get_consent_history(user_id),
            'processing_activities': self.get_processing_activities_for_user(user_id),
            'data_subject_requests': self.get_data_subject_requests_for_user(user_id)
        }
        
        logger.info(f"Generated data export for user {user_id}")
        
        return export


class CCPACompliance:
    """
    Implements CCPA compliance features.
    
    This class provides functionality to manage user privacy rights under the
    California Consumer Privacy Act.
    """
    
    def __init__(self, 
                storage_dir: Optional[Union[str, Path]] = None,
                encryption_key_name: str = "ccpa"):
        """
        Initialize the CCPA compliance manager.
        
        Args:
            storage_dir: Directory to store CCPA-related data.
                        If None, data will only be stored in memory.
            encryption_key_name: Name of the encryption key to use for CCPA data.
        """
        self.storage_dir = Path(storage_dir) if storage_dir else None
        self.encryption_key_name = encryption_key_name
        
        # In-memory storage
        self.opt_out_records = {}
        self.data_sale_records = {}
        self.privacy_requests = {}
        
        # Initialize storage directory if provided
        if self.storage_dir:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (self.storage_dir / 'opt_out_records').mkdir(exist_ok=True)
            (self.storage_dir / 'data_sale_records').mkdir(exist_ok=True)
            (self.storage_dir / 'privacy_requests').mkdir(exist_ok=True)
    
    def _save_opt_out_record(self, user_id: str, record: Dict[str, Any]):
        """Save opt-out record to storage."""
        if not self.storage_dir:
            return
        
        record_file = self.storage_dir / 'opt_out_records' / f"{user_id}.json"
        
        try:
            # Encrypt the record
            encrypted_data = encrypt_data(record, self.encryption_key_name)
            
            with open(record_file, 'wb') as f:
                f.write(encrypted_data)
            
            logger.debug(f"Saved opt-out record for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to save opt-out record for user {user_id}: {e}")
    
    def _load_opt_out_record(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load opt-out record from storage."""
        if not self.storage_dir:
            return None
        
        record_file = self.storage_dir / 'opt_out_records' / f"{user_id}.json"
        
        if not record_file.exists():
            return None
        
        try:
            with open(record_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt the record
            record_data = decrypt_data(encrypted_data, self.encryption_key_name)
            return json.loads(record_data.decode())
        except Exception as e:
            logger.error(f"Failed to load opt-out record for user {user_id}: {e}")
            return None
    
    def record_do_not_sell_opt_out(self, 
                                 user_id: str, 
                                 opted_out: bool, 
                                 timestamp: Optional[datetime] = None,
                                 details: Optional[Dict[str, Any]] = None):
        """
        Record a user's opt-out preference for selling their personal information.
        
        Args:
            user_id: Identifier for the user
            opted_out: Whether the user has opted out of data sales
            timestamp: When the opt-out was recorded
            details: Additional details about the opt-out
        """
        timestamp = timestamp or datetime.now()
        
        # Load existing opt-out record
        if user_id in self.opt_out_records:
            record = self.opt_out_records[user_id]
        else:
            stored_record = self._load_opt_out_record(user_id)
            if stored_record:
                record = stored_record
            else:
                record = {
                    'user_id': user_id,
                    'status': None,
                    'history': []
                }
        
        # Update opt-out status
        record['status'] = {
            'opted_out': opted_out,
            'timestamp': timestamp.isoformat(),
            'details': details or {}
        }
        
        # Add to history
        record['history'].append({
            'opted_out': opted_out,
            'timestamp': timestamp.isoformat(),
            'details': details or {}
        })
        
        # Save the updated record
        self.opt_out_records[user_id] = record
        self._save_opt_out_record(user_id, record)
        
        logger.info(f"Recorded Do Not Sell opt-out for user {user_id}: {'opted out' if opted_out else 'opted in'}")
    
    def check_do_not_sell_opt_out(self, user_id: str) -> bool:
        """
        Check if a user has opted out of selling their personal information.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            True if the user has opted out, False otherwise
        """
        # Load opt-out record if not already loaded
        if user_id not in self.opt_out_records:
            stored_record = self._load_opt_out_record(user_id)
            if stored_record:
                self.opt_out_records[user_id] = stored_record
        
        # Check if opt-out record exists
        if user_id not in self.opt_out_records or not self.opt_out_records[user_id]['status']:
            return False
        
        return self.opt_out_records[user_id]['status']['opted_out']
    
    def create_data_deletion_request(self, 
                                   user_id: str, 
                                   request_details: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new data deletion request under CCPA.
        
        Args:
            user_id: Identifier for the user
            request_details: Additional details about the request
            
        Returns:
            Request ID
        """
        request_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        request = {
            'request_id': request_id,
            'user_id': user_id,
            'type': 'deletion',
            'status': 'pending',
            'created_at': timestamp.isoformat(),
            'updated_at': timestamp.isoformat(),
            'completed_at': None,
            'details': request_details or {},
            'history': [
                {
                    'status': 'pending',
                    'timestamp': timestamp.isoformat(),
                    'comment': 'Request created'
                }
            ]
        }
        
        # Save the request
        self.privacy_requests[request_id] = request
        
        # Save to storage if configured
        if self.storage_dir:
            request_file = self.storage_dir / 'privacy_requests' / f"{request_id}.json"
            
            try:
                # Encrypt the request
                encrypted_data = encrypt_data(request, self.encryption_key_name)
                
                with open(request_file, 'wb') as f:
                    f.write(encrypted_data)
                
                logger.debug(f"Saved privacy request: {request_id}")
            except Exception as e:
                logger.error(f"Failed to save privacy request: {e}")
        
        logger.info(f"Created data deletion request: {request_id} for user {user_id}")
        
        return request_id
    
    def update_privacy_request(self, 
                            request_id: str, 
                            status: str, 
                            comment: Optional[str] = None,
                            details: Optional[Dict[str, Any]] = None):
        """
        Update the status of a privacy request.
        
        Args:
            request_id: Identifier for the request
            status: New status for the request
            comment: Optional comment about the update
            details: Additional details to update
        """
        if request_id not in self.privacy_requests:
            # Try to load from storage
            if self.storage_dir:
                request_file = self.storage_dir / 'privacy_requests' / f"{request_id}.json"
                
                if request_file.exists():
                    try:
                        with open(request_file, 'rb') as f:
                            encrypted_data = f.read()
                        
                        # Decrypt the request
                        request_data = decrypt_data(encrypted_data, self.encryption_key_name)
                        request = json.loads(request_data.decode())
                        
                        self.privacy_requests[request_id] = request
                    except Exception as e:
                        logger.error(f"Failed to load privacy request {request_id}: {e}")
        
        if request_id not in self.privacy_requests:
            raise ValueError(f"Privacy request {request_id} not found")
        
        timestamp = datetime.now()
        request = self.privacy_requests[request_id]
        
        # Update the request
        request['status'] = status
        request['updated_at'] = timestamp.isoformat()
        
        if status in ('completed', 'rejected'):
            request['completed_at'] = timestamp.isoformat()
        
        # Update details if provided
        if details:
            request['details'].update(details)
        
        # Add to history
        request['history'].append({
            'status': status,
            'timestamp': timestamp.isoformat(),
            'comment': comment or f"Status updated to {status}"
        })
        
        # Save to storage if configured
        if self.storage_dir:
            request_file = self.storage_dir / 'privacy_requests' / f"{request_id}.json"
            
            try:
                # Encrypt the request
                encrypted_data = encrypt_data(request, self.encryption_key_name)
                
                with open(request_file, 'wb') as f:
                    f.write(encrypted_data)
                
                logger.debug(f"Updated privacy request: {request_id}")
            except Exception as e:
                logger.error(f"Failed to update privacy request: {e}")
        
        logger.info(f"Updated privacy request: {request_id} to status {status}")
    
    def record_data_categories(self, 
                            user_id: str, 
                            categories: Dict[str, List[str]],
                            sources: Dict[str, List[str]],
                            third_parties: Dict[str, List[str]]):
        """
        Record categories of personal information collected, their sources, and third parties
        they are shared with, as required by CCPA.
        
        Args:
            user_id: Identifier for the user
            categories: Dictionary mapping category names to lists of data types
            sources: Dictionary mapping category names to lists of data sources
            third_parties: Dictionary mapping category names to lists of third parties
        """
        timestamp = datetime.now()
        
        record = {
            'user_id': user_id,
            'timestamp': timestamp.isoformat(),
            'categories': categories,
            'sources': sources,
            'third_parties': third_parties
        }
        
        record_id = f"{user_id}_{int(timestamp.timestamp())}"
        self.data_sale_records[record_id] = record
        
        # Save to storage if configured
        if self.storage_dir:
            record_file = self.storage_dir / 'data_sale_records' / f"{record_id}.json"
            
            try:
                # Encrypt the record
                encrypted_data = encrypt_data(record, self.encryption_key_name)
                
                with open(record_file, 'wb') as f:
                    f.write(encrypted_data)
                
                logger.debug(f"Saved data category record: {record_id}")
            except Exception as e:
                logger.error(f"Failed to save data category record: {e}")
        
        logger.info(f"Recorded data categories for user {user_id}")
    
    def generate_privacy_disclosure(self, user_id: str) -> Dict[str, Any]:
        """
        Generate a privacy disclosure for a user, containing all required CCPA information.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            Dictionary containing the privacy disclosure
        """
        # Load privacy records from storage if needed
        if self.storage_dir:
            record_dir = self.storage_dir / 'data_sale_records'
            for record_file in record_dir.glob(f"{user_id}_*.json"):
                try:
                    with open(record_file, 'rb') as f:
                        encrypted_data = f.read()
                    
                    # Decrypt the record
                    record_data = decrypt_data(encrypted_data, self.encryption_key_name)
                    record = json.loads(record_data.decode())
                    
                    record_id = record_file.stem
                    self.data_sale_records[record_id] = record
                except Exception as e:
                    logger.error(f"Failed to load data category record {record_file}: {e}")
        
        # Get opt-out status
        opt_out_status = self.check_do_not_sell_opt_out(user_id)
        
        # Filter records for the specified user
        user_records = [
            record for record_id, record in self.data_sale_records.items()
            if record['user_id'] == user_id
        ]
        
        # Sort by timestamp (newest first)
        user_records.sort(key=lambda r: r['timestamp'], reverse=True)
        
        # Use the most recent record
        latest_record = user_records[0] if user_records else {
            'categories': {},
            'sources': {},
            'third_parties': {}
        }
        
        disclosure = {
            'user_id': user_id,
            'generated_at': datetime.now().isoformat(),
            'do_not_sell_opt_out': opt_out_status,
            'categories_collected': latest_record['categories'],
            'sources': latest_record['sources'],
            'third_parties': latest_record['third_parties'],
            'privacy_policy_url': "https://example.com/privacy-policy",  # This should be configured
            'last_updated': latest_record.get('timestamp', datetime.now().isoformat())
        }
        
        logger.info(f"Generated privacy disclosure for user {user_id}")
        
        return disclosure