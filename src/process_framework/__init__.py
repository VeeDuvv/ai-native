# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file tells Python that our process_framework folder is a package that other parts
# of our code can use. It's like putting a special sign on a door that says "You can come in!"

# High School Explanation:
# This module initializes the process_framework package, making its modules and classes
# available for import from other parts of the application. It provides version information
# and exposes the key components of the process framework integration system.

"""Process Framework Integration for AI-Native Ad Agency.

This package provides integration with standard business process frameworks like APQC and eTOM,
allowing agents to execute standardized business processes through a workflow engine.
"""

__version__ = '0.1.0'

from .core import ProcessFramework, Process, Activity
from .repository import ProcessRepository
from .interpreter import ProcessInterpreter
from .workflow import WorkflowEngine
from .interface import ProcessAwareAgent