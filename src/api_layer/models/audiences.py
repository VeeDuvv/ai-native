"""Stub for Audience models."""

from enum import Enum


class AudienceType(str, Enum):
    DEMOGRAPHIC = "demographic"
    INTEREST = "interest"


class AudienceStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"


class AudienceCriteria:
    """Stub class for AudienceCriteria model."""
    pass


class Audience:
    """Stub class for Audience model."""
    pass
