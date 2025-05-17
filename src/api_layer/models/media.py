"""Stub for Media models."""

from enum import Enum


class MediaChannelType(str, Enum):
    SOCIAL = "social"
    DISPLAY = "display"


class MediaPlacementStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"


class BudgetType(str, Enum):
    DAILY = "daily"
    LIFETIME = "lifetime"


class MediaPacingStrategy(str, Enum):
    EVEN = "even"
    ACCELERATED = "accelerated"


class BiddingStrategy(str, Enum):
    CPM = "cpm"
    CPC = "cpc"


class MediaChannel:
    """Stub class for MediaChannel model."""
    pass


class MediaBudget:
    """Stub class for MediaBudget model."""
    pass


class MediaPlacement:
    """Stub class for MediaPlacement model."""
    pass
