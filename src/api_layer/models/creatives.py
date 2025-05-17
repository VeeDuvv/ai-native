"""Stub for Creative models."""

from enum import Enum


class CreativeType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"


class CreativeStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"


class CreativeFormat(str, Enum):
    SQUARE = "square"
    PORTRAIT = "portrait"


class Creative:
    """Stub class for Creative model."""
    pass
