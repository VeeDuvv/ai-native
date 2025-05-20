# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps our program use a special brain that remembers everything
# about advertising. It's like having a really smart friend who never forgets anything.

# High School Explanation:
# This module initializes the TISIT knowledge graph system and provides
# import shortcuts to the main components needed for accessing and manipulating
# the knowledge graph throughout the application.

from .entity import Entity
from .relationship import Relationship
from .knowledge_graph import KnowledgeGraph
from .storage import EntityStorage

__all__ = ['Entity', 'Relationship', 'KnowledgeGraph', 'EntityStorage']