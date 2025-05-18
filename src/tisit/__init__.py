# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file tells Python that the 'tisit' folder is a package that can be used by other parts
# of our program. It's like putting a flag on a building to say "this is part of our project".

# High School Explanation:
# This __init__.py file marks the tisit directory as a Python package, allowing its modules
# to be imported elsewhere in the codebase. It also provides package-level imports and
# version information for the TISIT knowledge graph implementation.

__version__ = '0.1.0'

from .entity import Entity
from .knowledge_graph import KnowledgeGraph
from .storage import EntityStorage
from .relationship import Relationship
from .cli import CLI
