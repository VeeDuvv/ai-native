# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file defines a blueprint for all the translators that convert business process
# documents into our system. It makes sure all the translators work the same way even 
# though they read different types of documents.

# High School Explanation:
# This module defines the base abstract class for process framework parsers.
# It establishes a common interface that all specific parser implementations
# must follow to convert external framework formats into our unified model.

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union, IO
from pathlib import Path

from ..core import ProcessFramework


class FrameworkParser(ABC):
    """Base abstract class for process framework parsers.
    
    This class defines the interface that all process framework parsers
    must implement to convert external framework formats into our unified
    ProcessFramework model.
    """
    
    @abstractmethod
    def parse(self, source: Union[str, Path, IO]) -> ProcessFramework:
        """Parse a process framework from a source.
        
        Args:
            source: The source to parse (file path, file-like object, or content string)
            
        Returns:
            A ProcessFramework instance
            
        Raises:
            ValueError: If the source is invalid or cannot be parsed
        """
        pass
    
    @abstractmethod
    def get_format_name(self) -> str:
        """Get the name of the format this parser handles.
        
        Returns:
            The name of the format (e.g., "APQC Excel", "eTOM XML")
        """
        pass
    
    @abstractmethod
    def can_parse(self, source: Union[str, Path, IO]) -> bool:
        """Check if this parser can parse the given source.
        
        Args:
            source: The source to check
            
        Returns:
            True if this parser can parse the source, False otherwise
        """
        pass