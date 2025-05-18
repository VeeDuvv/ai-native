# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps our system understand different types of business process documents. It's like
# having special translators that can read different languages and convert them to one
# language that our AI helpers can understand.

# High School Explanation:
# This module provides parser implementations for various process framework formats,
# allowing the system to import and standardize process definitions from different
# sources like APQC, eTOM, and custom formats into our unified representation.

"""Parsers for process framework formats.

This package contains parsers for various process framework formats, enabling
the import of process definitions from different sources into our unified model.
"""

from .base import FrameworkParser
from .apqc import APQCExcelParser
from .etom import ETOMXmlParser
from .json import JsonFrameworkParser