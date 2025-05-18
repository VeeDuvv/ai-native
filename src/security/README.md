# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Security and Compliance Module

## Overview

The Security and Compliance module provides comprehensive tools for securing the AI-native platform and ensuring compliance with privacy regulations. It includes features for encryption, access control, audit logging, and regulatory compliance.

## Core Components

### Encryption (`encryption.py`)

The encryption module provides tools for protecting sensitive data:

- **Symmetric Encryption**: Fast encryption using a shared key
- **Asymmetric Encryption**: Public/private key encryption for secure data exchange
- **Key Management**: Generate, store, and rotate encryption keys
- **Secure Storage**: Options for memory-only or filesystem-based key storage

Example:
```python
from security.encryption import get_encryption_service

# Get the encryption service
encryption_service = get_encryption_service()

# Encrypt sensitive data
encrypted_data = encryption_service.encrypt_with_symmetric_key(
    "sensitive information", "my-key"
)

# Decrypt the data
decrypted_data = encryption_service.decrypt_with_symmetric_key(
    encrypted_data, "my-key"
)
```

### Access Control (`access_control.py`)

The access control module implements role-based access control (RBAC):

- **Permissions**: Granular control over actions on resources
- **Roles**: Collections of permissions assigned to users
- **Resource-Specific Access**: Control access to specific resource instances
- **RBAC Service**: Higher-level interface for managing access control policies

Example:
```python
from security.access_control import AccessControl, Permission

# Create an access control system
access_control = AccessControl()

# Define permissions
view_campaigns = Permission("campaign", "view")
edit_campaigns = Permission("campaign", "edit")

# Create roles
admin_role = access_control.create_role("admin")
user_role = access_control.create_role("user")

# Assign permissions to roles
access_control.add_role_permission("admin", view_campaigns)
access_control.add_role_permission("admin", edit_campaigns)
access_control.add_role_permission("user", view_campaigns)

# Assign roles to users
access_control.assign_role_to_user("admin123", "admin")
access_control.assign_role_to_user("user456", "user")

# Check permissions
can_edit = access_control.check_permission("user456", "campaign", "edit")
```

### Audit Logging (`audit.py`)

The audit module provides comprehensive logging of security-relevant events:

- **Structured Events**: Categorized events with standardized fields
- **Configurable Storage**: Options for memory-only or secure file-based storage
- **Event Querying**: Filter and search events based on various criteria
- **Report Generation**: Generate security and compliance reports
- **Event Listeners**: Register callbacks for real-time event monitoring

Example:
```python
from security.audit import AuditLogger, EventCategory, EventOutcome

# Create an audit logger
audit_logger = AuditLogger()

# Log a security event
audit_logger.log(
    category=EventCategory.AUTHENTICATION,
    action="login",
    user_id="user123",
    outcome=EventOutcome.SUCCESS,
    source_ip="192.168.1.100"
)

# Query for failed logins
failed_logins = audit_logger.query_events(
    filter=AuditFilter(
        categories={EventCategory.AUTHENTICATION.value},
        outcomes={EventOutcome.FAILURE.value}
    )
)
```

### Compliance (`compliance.py`)

The compliance module implements features required for regulatory compliance:

- **GDPR Compliance**: Manage consent, data subject rights, and processing records
- **CCPA Compliance**: Implement do-not-sell opt-outs and privacy disclosures
- **Data Retention**: Apply retention policies based on data categories and purposes
- **Secure Storage**: Encrypted storage of compliance-related data

Example:
```python
from security.compliance import GDPRCompliance, ConsentType

# Create a GDPR compliance manager
gdpr = GDPRCompliance()

# Record user consent
gdpr.record_consent(
    user_id="user123",
    consent_type=ConsentType.MARKETING,
    granted=True,
    details={"source": "website_form"}
)

# Check if user consented
has_consent = gdpr.check_consent("user123", ConsentType.MARKETING)
```

## Integration with the Platform

The security module is designed to integrate with all aspects of the AI-native platform:

1. **API Layer**: Apply access control and audit logging to API endpoints
2. **Agent Framework**: Secure agent communication and monitor agent activities
3. **Data Storage**: Encrypt sensitive data before storage
4. **User Management**: Enforce compliance with privacy regulations

## Usage Examples

See `examples.py` for comprehensive examples of how to use each component of the security module.

## Best Practices

1. **Defense in Depth**: Apply multiple security controls for critical operations
2. **Principle of Least Privilege**: Grant minimal permissions required for each role
3. **Secure by Default**: Always enable encryption, access control, and audit logging
4. **Comprehensive Logging**: Log all security-relevant events for monitoring and compliance
5. **Regular Key Rotation**: Rotate encryption keys on a regular schedule

## Configuration

The security module can be configured through environment variables:

- `ENCRYPTION_KEY_DIR`: Directory for storing encryption keys
- `ENCRYPTION_MASTER_PASSWORD`: Master password for protecting stored keys
- `ACCESS_CONTROL_STORAGE`: Path for storing access control data
- `AUDIT_LOG_DIR`: Directory for storing audit logs
- `AUDIT_LOG_ENCRYPTION`: Whether to encrypt audit logs (true/false)
- `COMPLIANCE_STORAGE_DIR`: Directory for storing compliance data