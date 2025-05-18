# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps Python recognize the specialized agent folder as a package,
# making it easier to import and use different specialized AI agents.

# High School Explanation:
# This module marks the specialized directory as a Python package, enabling
# structured imports of specialized agent implementations designed for specific
# advertising roles within the agent ecosystem.

"""
Specialized agent implementations for the AI-native ad agency.

This package contains concrete agent implementations for specialized roles
in the advertising agency, leveraging the agent framework foundation.
"""

from . import strategy
from . import creative
from . import media
from . import analytics
from . import client