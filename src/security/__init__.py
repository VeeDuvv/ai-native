# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps keep our app safe and secure. It makes sure only the right people 
# can see certain information and protects important data.

# High School Explanation:
# This module provides security and compliance features for the AI-native platform.
# It includes encryption, authentication, access control, audit logging, and data
# protection features to ensure the system meets regulatory requirements and 
# protects sensitive information.

from .encryption import EncryptionService, encrypt_data, decrypt_data
from .access_control import AccessControl, Role, Permission, RBACService
from .audit import AuditLogger, AuditEvent, EventSeverity
from .compliance import GDPRCompliance, CCPACompliance, DataRetentionPolicy

__version__ = '0.1.0'