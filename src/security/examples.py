# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file shows examples of how to use the security tools we've built.
# It's like a guide that helps people learn how to keep information safe.

# High School Explanation:
# This module provides examples of how to use the security and compliance features
# of the platform. It demonstrates encryption, access control, audit logging, and
# compliance features with practical code examples that can be used as a reference
# for developers implementing security in their applications.

import os
import json
import logging
import time
from pathlib import Path
from datetime import datetime, timedelta

from .encryption import (
    EncryptionService, encrypt_data, decrypt_data, get_encryption_service
)
from .access_control import (
    Permission, Role, AccessControl, RBACService
)
from .audit import (
    AuditLogger, AuditEvent, AuditFilter, EventCategory, EventSeverity, EventOutcome
)
from .compliance import (
    GDPRCompliance, CCPACompliance, DataRetentionPolicy,
    ConsentType, RightType, DataCategory, ProcessingPurpose, RetentionPolicy
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Example 1: Basic encryption and decryption
def example_encryption():
    print("\n=== Example 1: Basic Encryption and Decryption ===")
    
    # Create an in-memory encryption service
    encryption_service = EncryptionService()
    
    # Create a symmetric key
    key = encryption_service.create_symmetric_key("example-key")
    print(f"Created symmetric key: {key}")
    
    # Encrypt some data
    sensitive_data = "This is sensitive information!"
    encrypted_data = encryption_service.encrypt_with_symmetric_key(sensitive_data, "example-key")
    print(f"Encrypted data: {encrypted_data}")
    
    # Decrypt the data
    decrypted_data = encryption_service.decrypt_with_symmetric_key(encrypted_data, "example-key")
    print(f"Decrypted data: {decrypted_data.decode()}")
    
    # Encrypt a JSON object
    user_data = {
        "user_id": "user123",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "credit_card": "1234-5678-9012-3456"
    }
    
    encrypted_json = encryption_service.encrypt_json(user_data, "example-key")
    print(f"Encrypted JSON: {encrypted_json}")
    
    # Decrypt the JSON
    decrypted_json = encryption_service.decrypt_json(encrypted_json, "example-key")
    print(f"Decrypted JSON: {decrypted_json}")
    
    # Create an asymmetric key pair
    private_key, public_key = encryption_service.create_asymmetric_key_pair("example-asymmetric")
    print(f"Created asymmetric key pair")
    
    # Encrypt data with the public key
    message = "This is a secret message for asymmetric encryption"
    encrypted_message = encryption_service.encrypt_with_asymmetric_key(message, "example-asymmetric")
    print(f"Encrypted message with public key: {encrypted_message}")
    
    # Decrypt data with the private key
    decrypted_message = encryption_service.decrypt_with_asymmetric_key(encrypted_message, "example-asymmetric")
    print(f"Decrypted message with private key: {decrypted_message.decode()}")
    
    return encryption_service


# Example 2: Role-based access control
def example_rbac():
    print("\n=== Example 2: Role-Based Access Control ===")
    
    # Create an in-memory access control system
    access_control = AccessControl()
    
    # Create some permissions
    view_campaigns = Permission("campaign", "view", "View campaign details")
    edit_campaigns = Permission("campaign", "edit", "Edit campaign details")
    delete_campaigns = Permission("campaign", "delete", "Delete campaigns")
    
    view_creatives = Permission("creative", "view", "View creative assets")
    edit_creatives = Permission("creative", "edit", "Edit creative assets")
    
    view_analytics = Permission("analytics", "view", "View analytics reports")
    
    # Create roles
    admin_role = access_control.create_role("admin", "Administrator with full access")
    manager_role = access_control.create_role("manager", "Campaign manager")
    creator_role = access_control.create_role("creator", "Creative designer")
    viewer_role = access_control.create_role("viewer", "Read-only user")
    
    # Assign permissions to roles
    access_control.add_role_permission("admin", view_campaigns)
    access_control.add_role_permission("admin", edit_campaigns)
    access_control.add_role_permission("admin", delete_campaigns)
    access_control.add_role_permission("admin", view_creatives)
    access_control.add_role_permission("admin", edit_creatives)
    access_control.add_role_permission("admin", view_analytics)
    
    access_control.add_role_permission("manager", view_campaigns)
    access_control.add_role_permission("manager", edit_campaigns)
    access_control.add_role_permission("manager", view_creatives)
    access_control.add_role_permission("manager", view_analytics)
    
    access_control.add_role_permission("creator", view_campaigns)
    access_control.add_role_permission("creator", view_creatives)
    access_control.add_role_permission("creator", edit_creatives)
    
    access_control.add_role_permission("viewer", view_campaigns)
    access_control.add_role_permission("viewer", view_creatives)
    access_control.add_role_permission("viewer", view_analytics)
    
    # Assign roles to users
    access_control.assign_role_to_user("user1", "admin")
    access_control.assign_role_to_user("user2", "manager")
    access_control.assign_role_to_user("user3", "creator")
    access_control.assign_role_to_user("user4", "viewer")
    
    # Check permissions
    print("Permission checks:")
    print(f"user1 can view campaigns: {access_control.check_permission('user1', 'campaign', 'view')}")
    print(f"user1 can delete campaigns: {access_control.check_permission('user1', 'campaign', 'delete')}")
    print(f"user2 can edit campaigns: {access_control.check_permission('user2', 'campaign', 'edit')}")
    print(f"user2 can delete campaigns: {access_control.check_permission('user2', 'campaign', 'delete')}")
    print(f"user3 can edit creatives: {access_control.check_permission('user3', 'creative', 'edit')}")
    print(f"user3 can edit campaigns: {access_control.check_permission('user3', 'campaign', 'edit')}")
    print(f"user4 can view analytics: {access_control.check_permission('user4', 'analytics', 'view')}")
    print(f"user4 can edit anything: {access_control.check_permission('user4', 'campaign', 'edit') or access_control.check_permission('user4', 'creative', 'edit')}")
    
    # Create an RBAC service for higher-level operations
    rbac_service = RBACService(access_control)
    
    # Define resource patterns
    rbac_service.define_resource_pattern(
        "campaign",
        {
            "admin": ["view", "edit", "delete", "create", "approve"],
            "manager": ["view", "edit", "create", "approve"],
            "creator": ["view"],
            "viewer": ["view"]
        }
    )
    
    # Register a resource checker for campaign-specific permissions
    def campaign_checker(user_id, resource_id, action, resource):
        # Example: Only the owner of a campaign can delete it
        if action == "delete" and resource and resource.get("owner_id") != user_id:
            return False
        return True
    
    rbac_service.register_resource_checker("campaign", campaign_checker)
    
    # Check resource access
    campaign1 = {"id": "campaign1", "name": "Summer Sale", "owner_id": "user2"}
    
    print("\nResource-specific checks:")
    print(f"user1 can delete campaign1: {rbac_service.check_resource_access('user1', 'campaign', 'campaign1', 'delete', campaign1)}")
    print(f"user2 can delete campaign1: {rbac_service.check_resource_access('user2', 'campaign', 'campaign1', 'delete', campaign1)}")
    
    # Get allowed actions for a user on a resource
    print("\nAllowed actions:")
    print(f"user1 allowed actions on campaigns: {rbac_service.get_allowed_actions('user1', 'campaign')}")
    print(f"user2 allowed actions on campaigns: {rbac_service.get_allowed_actions('user2', 'campaign')}")
    print(f"user3 allowed actions on campaigns: {rbac_service.get_allowed_actions('user3', 'campaign')}")
    print(f"user4 allowed actions on campaigns: {rbac_service.get_allowed_actions('user4', 'campaign')}")
    
    return rbac_service


# Example 3: Audit logging
def example_audit_logging():
    print("\n=== Example 3: Audit Logging ===")
    
    # Create an in-memory audit logger
    audit_logger = AuditLogger()
    
    # Add a simple listener that prints events
    def print_event(event):
        print(f"Audit event: {event}")
    
    audit_logger.add_listener(print_event)
    
    # Log some events
    print("Logging events:")
    
    # Authentication events
    audit_logger.log(
        category=EventCategory.AUTHENTICATION,
        action="login",
        user_id="user1",
        outcome=EventOutcome.SUCCESS,
        source_ip="192.168.1.100",
        details={"method": "password"}
    )
    
    audit_logger.log(
        category=EventCategory.AUTHENTICATION,
        action="login",
        user_id="user2",
        outcome=EventOutcome.FAILURE,
        severity=EventSeverity.WARNING,
        source_ip="192.168.1.101",
        details={"method": "password", "reason": "Invalid password"}
    )
    
    # Authorization events
    audit_logger.log(
        category=EventCategory.AUTHORIZATION,
        action="access",
        user_id="user1",
        resource_type="campaign",
        resource_id="campaign1",
        outcome=EventOutcome.SUCCESS
    )
    
    audit_logger.log(
        category=EventCategory.AUTHORIZATION,
        action="access",
        user_id="user3",
        resource_type="campaign",
        resource_id="campaign1",
        outcome=EventOutcome.DENIED,
        severity=EventSeverity.WARNING
    )
    
    # Data modification events
    audit_logger.log(
        category=EventCategory.DATA_MODIFICATION,
        action="update",
        user_id="user1",
        resource_type="campaign",
        resource_id="campaign1",
        details={"fields": ["name", "budget"], "changes": {"budget": "1000->2000"}}
    )
    
    # System events
    audit_logger.log(
        category=EventCategory.SYSTEM,
        action="backup",
        outcome=EventOutcome.SUCCESS
    )
    
    audit_logger.log(
        category=EventCategory.SYSTEM,
        action="maintenance",
        severity=EventSeverity.NOTICE,
        details={"type": "index_optimization"}
    )
    
    # Security events
    audit_logger.log(
        category=EventCategory.SECURITY,
        action="brute_force_attempt",
        user_id="user5",
        source_ip="203.0.113.1",
        outcome=EventOutcome.FAILURE,
        severity=EventSeverity.ERROR,
        details={"attempts": 5, "action_taken": "ip_blocked"}
    )
    
    # Query events
    print("\nQuerying authentication events:")
    auth_filter = AuditFilter(categories={EventCategory.AUTHENTICATION.value})
    auth_events = audit_logger.query_events(auth_filter)
    
    for event in auth_events:
        print(f"  {event}")
    
    print("\nQuerying high severity events:")
    severity_filter = AuditFilter(
        severities={EventSeverity.ERROR.value, EventSeverity.CRITICAL.value}
    )
    severity_events = audit_logger.query_events(severity_filter)
    
    for event in severity_events:
        print(f"  {event}")
    
    # Generate an audit report
    print("\nGenerating audit report:")
    yesterday = datetime.now() - timedelta(days=1)
    report = audit_logger.generate_audit_report(
        start_time=yesterday,
        end_time=datetime.now()
    )
    
    print(f"  Total events: {report['statistics']['total_events']}")
    print(f"  Events by category: {report['statistics']['by_category']}")
    print(f"  Events by severity: {report['statistics']['by_severity']}")
    print(f"  Events by outcome: {report['statistics']['by_outcome']}")
    print(f"  Significant events: {len(report['significant_events'])}")
    
    return audit_logger


# Example 4: GDPR compliance
def example_gdpr_compliance():
    print("\n=== Example 4: GDPR Compliance ===")
    
    # Create an in-memory GDPR compliance manager
    gdpr = GDPRCompliance()
    
    # Record user consent
    print("Recording user consent:")
    gdpr.record_consent(
        user_id="user1",
        consent_type=ConsentType.MARKETING,
        granted=True,
        details={"source": "website_form", "ip_address": "192.168.1.100"}
    )
    
    gdpr.record_consent(
        user_id="user1",
        consent_type=ConsentType.ANALYTICS,
        granted=True,
        details={"source": "website_form", "ip_address": "192.168.1.100"}
    )
    
    gdpr.record_consent(
        user_id="user1",
        consent_type=ConsentType.PROFILING,
        granted=False,
        details={"source": "website_form", "ip_address": "192.168.1.100"}
    )
    
    # Check consent
    print("\nChecking consent:")
    try:
        print(f"user1 granted marketing consent: {gdpr.check_consent('user1', ConsentType.MARKETING)}")
        print(f"user1 granted analytics consent: {gdpr.check_consent('user1', ConsentType.ANALYTICS)}")
        print(f"user1 granted profiling consent: {gdpr.check_consent('user1', ConsentType.PROFILING)}")
    except Exception as e:
        print(f"Error checking consent: {e}")
    
    # Record data processing activities
    print("\nRecording data processing activities:")
    gdpr.record_data_processing_activity(
        activity_id="email_campaign_1",
        data_category=DataCategory.CONTACT_INFO,
        processing_purpose=ProcessingPurpose.MARKETING,
        user_ids=["user1", "user2", "user3"],
        legal_basis="consent",
        details={"campaign_name": "Summer Newsletter", "data_types": ["email"]}
    )
    
    gdpr.record_data_processing_activity(
        activity_id="website_analytics_1",
        data_category=DataCategory.USAGE,
        processing_purpose=ProcessingPurpose.ANALYTICS,
        user_ids=["user1", "user2", "user4"],
        legal_basis="legitimate_interest",
        details={"tools": ["Google Analytics"], "data_types": ["page_views", "time_on_page"]}
    )
    
    # Get processing activities for a user
    print("\nGetting processing activities for user1:")
    activities = gdpr.get_processing_activities_for_user("user1")
    
    for activity in activities:
        print(f"  {activity['activity_id']}: {activity['processing_purpose']} - {activity['data_category']}")
    
    # Create data subject requests
    print("\nCreating data subject requests:")
    request_id = gdpr.create_data_subject_request(
        user_id="user1",
        right_type=RightType.ACCESS,
        details={"request_method": "email", "contact_email": "user1@example.com"}
    )
    
    print(f"  Created request {request_id} for user1")
    
    # Update request status
    gdpr.update_data_subject_request(
        request_id=request_id,
        status="in_progress",
        comment="Request is being processed"
    )
    
    gdpr.update_data_subject_request(
        request_id=request_id,
        status="completed",
        comment="Data export provided to user",
        details={"export_date": datetime.now().isoformat(), "export_format": "json"}
    )
    
    # Generate a data export for a user
    print("\nGenerating data export for user1:")
    export = gdpr.generate_data_export("user1")
    
    print(f"  Export contains {len(export['consents'])} consent records")
    print(f"  Export contains {len(export['processing_activities'])} processing activities")
    print(f"  Export contains {len(export['data_subject_requests'])} data subject requests")
    
    return gdpr


# Example 5: CCPA compliance
def example_ccpa_compliance():
    print("\n=== Example 5: CCPA Compliance ===")
    
    # Create an in-memory CCPA compliance manager
    ccpa = CCPACompliance()
    
    # Record do-not-sell preferences
    print("Recording do-not-sell preferences:")
    ccpa.record_do_not_sell_opt_out(
        user_id="user1",
        opted_out=True,
        details={"source": "privacy_settings", "ip_address": "192.168.1.100"}
    )
    
    ccpa.record_do_not_sell_opt_out(
        user_id="user2",
        opted_out=False,
        details={"source": "privacy_settings", "ip_address": "192.168.1.101"}
    )
    
    # Check opt-out status
    print("\nChecking opt-out status:")
    print(f"user1 opted out of data sales: {ccpa.check_do_not_sell_opt_out('user1')}")
    print(f"user2 opted out of data sales: {ccpa.check_do_not_sell_opt_out('user2')}")
    
    # Record data categories collected
    print("\nRecording data categories collected:")
    ccpa.record_data_categories(
        user_id="user1",
        categories={
            "identifiers": ["name", "email", "device_id"],
            "commercial_information": ["purchase_history", "products_viewed"],
            "internet_activity": ["browsing_history", "search_history"]
        },
        sources={
            "identifiers": ["user_provided", "cookies"],
            "commercial_information": ["website", "mobile_app"],
            "internet_activity": ["website", "mobile_app"]
        },
        third_parties={
            "identifiers": ["marketing_partners", "analytics_providers"],
            "commercial_information": ["marketing_partners"],
            "internet_activity": ["analytics_providers"]
        }
    )
    
    # Create a data deletion request
    print("\nCreating data deletion request:")
    request_id = ccpa.create_data_deletion_request(
        user_id="user1",
        request_details={"request_method": "webform", "contact_email": "user1@example.com"}
    )
    
    print(f"  Created request {request_id} for user1")
    
    # Update request status
    ccpa.update_privacy_request(
        request_id=request_id,
        status="in_progress",
        comment="Request is being processed"
    )
    
    ccpa.update_privacy_request(
        request_id=request_id,
        status="completed",
        comment="Data deletion completed",
        details={"deletion_date": datetime.now().isoformat(), "deleted_categories": ["browsing_history", "search_history"]}
    )
    
    # Generate a privacy disclosure
    print("\nGenerating privacy disclosure for user1:")
    disclosure = ccpa.generate_privacy_disclosure("user1")
    
    print(f"  Disclosure shows opt-out status: {disclosure['do_not_sell_opt_out']}")
    print(f"  Disclosure lists {len(disclosure['categories_collected'])} categories of personal information")
    print(f"  Disclosure lists {len(disclosure['sources'])} sources of personal information")
    print(f"  Disclosure lists {len(disclosure['third_parties'])} third parties")
    
    return ccpa


# Example 6: Data retention
def example_data_retention():
    print("\n=== Example 6: Data Retention ===")
    
    # Create an in-memory data retention policy manager
    retention = DataRetentionPolicy()
    
    # Set retention periods for data categories
    print("Setting retention periods:")
    retention.set_retention_period(DataCategory.BASIC_INFO, 730)  # 2 years
    retention.set_retention_period(DataCategory.CONTACT_INFO, 730)  # 2 years
    retention.set_retention_period(DataCategory.USAGE, 365)  # 1 year
    retention.set_retention_period(DataCategory.TECHNICAL, 90)  # 90 days
    
    print(f"  Basic info retention period: {retention.get_retention_period(DataCategory.BASIC_INFO)} days")
    print(f"  Contact info retention period: {retention.get_retention_period(DataCategory.CONTACT_INFO)} days")
    print(f"  Usage data retention period: {retention.get_retention_period(DataCategory.USAGE)} days")
    print(f"  Technical data retention period: {retention.get_retention_period(DataCategory.TECHNICAL)} days")
    
    # Set retention policies for data types
    print("\nSetting retention policies:")
    
    # Fixed period retention
    retention.set_policy(
        data_type="user_profile",
        policy_type=RetentionPolicy.FIXED_PERIOD,
        parameters={"period_days": 730}  # 2 years
    )
    
    # Retention until purpose is complete
    retention.set_policy(
        data_type="campaign_data",
        policy_type=RetentionPolicy.UNTIL_PURPOSE_COMPLETE,
        parameters={"purpose_complete_field": "is_complete"}
    )
    
    # User-requested deletion
    retention.set_policy(
        data_type="browsing_history",
        policy_type=RetentionPolicy.USER_REQUEST,
        parameters={"deletion_requested_field": "deletion_requested"}
    )
    
    # Category-based retention
    retention.set_policy(
        data_type="log_data",
        policy_type=RetentionPolicy.FIXED_PERIOD,
        parameters={"data_category": DataCategory.TECHNICAL.value}
    )
    
    # Test retention decisions
    print("\nTesting retention decisions:")
    
    # Create some test data
    now = datetime.now()
    
    test_items = [
        {
            "data_type": "user_profile",
            "data_id": "profile1",
            "creation_date": now - timedelta(days=700),
            "data": {"user_id": "user1", "name": "John"}
        },
        {
            "data_type": "user_profile",
            "data_id": "profile2",
            "creation_date": now - timedelta(days=800),
            "data": {"user_id": "user2", "name": "Jane"}
        },
        {
            "data_type": "campaign_data",
            "data_id": "campaign1",
            "creation_date": now - timedelta(days=100),
            "metadata": {"is_complete": False},
            "data": {"campaign_id": "123", "status": "active"}
        },
        {
            "data_type": "campaign_data",
            "data_id": "campaign2",
            "creation_date": now - timedelta(days=100),
            "metadata": {"is_complete": True},
            "data": {"campaign_id": "456", "status": "complete"}
        },
        {
            "data_type": "browsing_history",
            "data_id": "history1",
            "creation_date": now - timedelta(days=10),
            "metadata": {"deletion_requested": False},
            "data": {"user_id": "user1", "pages": ["/home", "/products"]}
        },
        {
            "data_type": "browsing_history",
            "data_id": "history2",
            "creation_date": now - timedelta(days=10),
            "metadata": {"deletion_requested": True},
            "data": {"user_id": "user2", "pages": ["/home", "/about"]}
        },
        {
            "data_type": "log_data",
            "data_id": "log1",
            "creation_date": now - timedelta(days=80),
            "data": {"ip": "192.168.1.100", "action": "login"}
        },
        {
            "data_type": "log_data",
            "data_id": "log2",
            "creation_date": now - timedelta(days=100),
            "data": {"ip": "192.168.1.101", "action": "logout"}
        }
    ]
    
    for item in test_items:
        should_retain = retention.should_retain(
            data_type=item["data_type"],
            creation_date=item["creation_date"],
            metadata=item.get("metadata")
        )
        
        print(f"  {item['data_type']} {item['data_id']}: {should_retain}")
    
    # Apply retention policies to the test data
    print("\nApplying retention policies:")
    retained_items = retention.apply_retention_policies(test_items)
    
    print(f"  {len(retained_items)} of {len(test_items)} items retained")
    
    # Show retained items
    print("\nRetained items:")
    for item in retained_items:
        print(f"  {item['data_type']} {item['data_id']}")
    
    return retention


# Example 7: Combined security features
def example_complete_security_system():
    print("\n=== Example 7: Complete Security System ===")
    
    # 1. Set up encryption
    print("1. Setting up encryption service")
    temp_dir = Path("./temp_security")
    temp_dir.mkdir(exist_ok=True)
    
    encryption_service = EncryptionService(
        key_dir=temp_dir / "keys",
        master_password="master-password-example"
    )
    
    encryption_service.create_symmetric_key("system-key")
    encryption_service.create_asymmetric_key_pair("user-keys")
    
    # 2. Set up access control
    print("\n2. Setting up access control")
    access_control = AccessControl(storage_path=temp_dir / "access_control")
    
    # Create standard roles and permissions
    rbac_service = RBACService(access_control)
    rbac_service.create_standard_roles()
    
    # Define resource patterns
    rbac_service.define_resource_pattern(
        "user",
        {
            "admin": ["view", "create", "edit", "delete"],
            "manager": ["view", "create", "edit"],
            "user": ["view", "edit_own"],
            "guest": ["view"]
        }
    )
    
    rbac_service.define_resource_pattern(
        "campaign",
        {
            "admin": ["view", "create", "edit", "delete", "approve"],
            "manager": ["view", "create", "edit", "approve"],
            "user": ["view", "create", "edit_own"],
            "guest": ["view"]
        }
    )
    
    rbac_service.define_resource_pattern(
        "analytics",
        {
            "admin": ["view", "export"],
            "manager": ["view", "export"],
            "user": ["view_own"],
            "guest": []
        }
    )
    
    # Assign roles to users
    access_control.assign_role_to_user("admin1", "admin")
    access_control.assign_role_to_user("manager1", "manager")
    access_control.assign_role_to_user("user1", "user")
    access_control.assign_role_to_user("guest1", "guest")
    
    # 3. Set up audit logging
    print("\n3. Setting up audit logging")
    audit_logger = AuditLogger(
        storage_dir=temp_dir / "audit_logs",
        encrypt_logs=True,
        encryption_key_name="system-key"
    )
    
    # 4. Set up compliance features
    print("\n4. Setting up compliance features")
    gdpr = GDPRCompliance(
        storage_dir=temp_dir / "gdpr",
        encryption_key_name="system-key"
    )
    
    ccpa = CCPACompliance(
        storage_dir=temp_dir / "ccpa",
        encryption_key_name="system-key"
    )
    
    retention = DataRetentionPolicy(
        storage_dir=temp_dir / "retention"
    )
    
    # Set standard retention periods
    retention.set_retention_period(DataCategory.BASIC_INFO, 730)  # 2 years
    retention.set_retention_period(DataCategory.CONTACT_INFO, 730)  # 2 years
    retention.set_retention_period(DataCategory.USAGE, 365)  # 1 year
    retention.set_retention_period(DataCategory.TECHNICAL, 90)  # 90 days
    
    # 5. Simulate a complete user journey with security enforced
    print("\n5. Simulating a user journey with security enforced")
    
    # User registration
    print("\n   a. User registration")
    
    # Create user data and encrypt sensitive parts
    user_data = {
        "user_id": "new_user",
        "email": "new.user@example.com",
        "password_hash": encryption_service.encrypt_with_symmetric_key(
            "bcrypt_hash_would_go_here", "system-key"
        ).decode('latin1'),  # Store as a string
        "created_at": datetime.now().isoformat()
    }
    
    # Record the registration in the audit log
    audit_logger.log(
        category=EventCategory.SYSTEM,
        action="user_registration",
        user_id="new_user",
        resource_type="user",
        resource_id="new_user",
        source_ip="203.0.113.100"
    )
    
    # Assign a role to the user
    access_control.assign_role_to_user("new_user", "user")
    
    # User login
    print("\n   b. User login")
    
    # Log the login attempt
    audit_logger.log(
        category=EventCategory.AUTHENTICATION,
        action="login",
        user_id="new_user",
        outcome=EventOutcome.SUCCESS,
        source_ip="203.0.113.100",
        session_id="session-123456"
    )
    
    # User provides consent
    print("\n   c. User provides consent")
    
    gdpr.record_consent(
        user_id="new_user",
        consent_type=ConsentType.MARKETING,
        granted=True,
        details={"source": "registration_form", "ip_address": "203.0.113.100"}
    )
    
    gdpr.record_consent(
        user_id="new_user",
        consent_type=ConsentType.ANALYTICS,
        granted=True,
        details={"source": "registration_form", "ip_address": "203.0.113.100"}
    )
    
    ccpa.record_do_not_sell_opt_out(
        user_id="new_user",
        opted_out=False,
        details={"source": "registration_form", "ip_address": "203.0.113.100"}
    )
    
    # User creates a resource
    print("\n   d. User creates a campaign")
    
    # First, check if the user has permission
    if access_control.check_permission("new_user", "campaign", "create"):
        # Create the campaign
        campaign_data = {
            "campaign_id": "campaign123",
            "name": "My First Campaign",
            "budget": 1000,
            "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=37)).isoformat(),
            "owner_id": "new_user",
            "status": "draft"
        }
        
        # Record the creation in the audit log
        audit_logger.log(
            category=EventCategory.DATA_MODIFICATION,
            action="create",
            user_id="new_user",
            resource_type="campaign",
            resource_id="campaign123",
            session_id="session-123456"
        )
        
        # Record this as a data processing activity
        gdpr.record_data_processing_activity(
            activity_id="campaign_creation_123",
            data_category=DataCategory.BASIC_INFO,
            processing_purpose=ProcessingPurpose.SERVICE_PROVISION,
            user_ids=["new_user"],
            legal_basis="contract_fulfillment",
            details={"campaign_id": "campaign123", "action": "create"}
        )
        
        print(f"      Campaign created: {campaign_data['name']}")
    else:
        print("      Permission denied: User cannot create campaigns")
    
    # Admin user accesses the campaign
    print("\n   e. Admin accesses the campaign")
    
    # Check if admin has permission
    if access_control.check_permission("admin1", "campaign", "view"):
        # Record the access in the audit log
        audit_logger.log(
            category=EventCategory.DATA_ACCESS,
            action="view",
            user_id="admin1",
            resource_type="campaign",
            resource_id="campaign123",
            session_id="session-admin-789012"
        )
        
        print("      Admin successfully accessed the campaign")
    else:
        print("      Permission denied: Admin cannot view campaigns")
    
    # Guest user tries to modify the campaign
    print("\n   f. Guest tries to modify the campaign")
    
    # Check if guest has permission
    if access_control.check_permission("guest1", "campaign", "edit"):
        print("      Guest can edit campaigns (this shouldn't happen)")
    else:
        # Record the denied access in the audit log
        audit_logger.log(
            category=EventCategory.AUTHORIZATION,
            action="edit",
            user_id="guest1",
            resource_type="campaign",
            resource_id="campaign123",
            outcome=EventOutcome.DENIED,
            severity=EventSeverity.WARNING,
            session_id="session-guest-345678"
        )
        
        print("      Permission denied: Guest cannot edit campaigns")
    
    # User requests account deletion (data subject right)
    print("\n   g. User requests account deletion")
    
    # Create a data deletion request
    deletion_request_id = gdpr.create_data_subject_request(
        user_id="new_user",
        right_type=RightType.ERASURE,
        details={"request_method": "email", "contact_email": "new.user@example.com"}
    )
    
    # Record the request in the audit log
    audit_logger.log(
        category=EventCategory.COMPLIANCE,
        action="data_subject_request",
        user_id="new_user",
        details={"request_id": deletion_request_id, "right_type": "erasure"}
    )
    
    # Process the deletion request
    gdpr.update_data_subject_request(
        request_id=deletion_request_id,
        status="in_progress",
        comment="Verifying identity and gathering data"
    )
    
    # Apply retention policies
    print("\n   h. Apply retention policies")
    
    # Define some retention policies
    retention.set_policy(
        data_type="user_account",
        policy_type=RetentionPolicy.USER_REQUEST,
        parameters={"deletion_requested_field": "deletion_requested"}
    )
    
    retention.set_policy(
        data_type="campaign",
        policy_type=RetentionPolicy.FIXED_PERIOD,
        parameters={"period_days": 365}  # 1 year after end date
    )
    
    # Create some test data for retention checks
    test_items = [
        {
            "data_type": "user_account",
            "data_id": "old_user1",
            "creation_date": datetime.now() - timedelta(days=1000),
            "metadata": {"deletion_requested": True},
            "data": {"user_id": "old_user1", "name": "Old User 1"}
        },
        {
            "data_type": "user_account",
            "data_id": "old_user2",
            "creation_date": datetime.now() - timedelta(days=1000),
            "metadata": {"deletion_requested": False},
            "data": {"user_id": "old_user2", "name": "Old User 2"}
        },
        {
            "data_type": "campaign",
            "data_id": "old_campaign1",
            "creation_date": datetime.now() - timedelta(days=500),
            "data": {"campaign_id": "old_campaign1", "name": "Old Campaign 1"}
        }
    ]
    
    # Register a deletion hook
    def log_deletion(data_id, data):
        audit_logger.log(
            category=EventCategory.DATA_MODIFICATION,
            action="delete",
            resource_id=data_id,
            resource_type=data["data_type"] if isinstance(data, dict) else "unknown",
            details={"reason": "retention_policy"}
        )
        print(f"      Deleted {data_id} due to retention policy")
    
    retention.register_deletion_hook("user_account", log_deletion)
    retention.register_deletion_hook("campaign", log_deletion)
    
    # Apply the retention policies
    retained_items = retention.apply_retention_policies(test_items)
    print(f"      {len(retained_items)} of {len(test_items)} items retained")
    
    # Complete the user deletion
    gdpr.update_data_subject_request(
        request_id=deletion_request_id,
        status="completed",
        comment="User data has been deleted",
        details={"deletion_date": datetime.now().isoformat()}
    )
    
    # 6. Clean up temporary files
    print("\n6. Cleaning up temporary files")
    # Comment out the next line if you want to examine the files
    # import shutil
    # shutil.rmtree(temp_dir)
    
    return {
        "encryption": encryption_service,
        "access_control": access_control,
        "rbac": rbac_service,
        "audit": audit_logger,
        "gdpr": gdpr,
        "ccpa": ccpa,
        "retention": retention
    }


# Run all examples
def run_examples():
    examples = [
        example_encryption,
        example_rbac,
        example_audit_logging,
        example_gdpr_compliance,
        example_ccpa_compliance,
        example_data_retention,
        # Uncomment to run the complete example
        # example_complete_security_system
    ]
    
    results = {}
    
    for example in examples:
        try:
            results[example.__name__] = example()
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
            import traceback
            print(traceback.format_exc())
    
    return results


if __name__ == "__main__":
    run_examples()