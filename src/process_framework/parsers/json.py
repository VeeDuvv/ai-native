# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps our system read business process information stored in JSON format.
# It's like having a special tool that can read a specific type of file and understand
# all the instructions inside it.

# High School Explanation:
# This module implements a parser for JSON-formatted process frameworks, providing
# the ability to import process definitions from our standard JSON representation
# directly into the unified ProcessFramework model.

import json
from typing import Dict, Any, Optional, List, Union, IO
from pathlib import Path
import logging

from .base import FrameworkParser
from ..core import ProcessFramework, Process, Activity


class JsonFrameworkParser(FrameworkParser):
    """Parser for JSON-formatted process frameworks.
    
    This parser handles the standard JSON representation of process frameworks
    used by our system, allowing for easy import and export of framework definitions.
    """
    
    def __init__(self) -> None:
        """Initialize the JSON framework parser."""
        self.logger = logging.getLogger(__name__)
    
    def get_format_name(self) -> str:
        """Get the name of the format this parser handles.
        
        Returns:
            The name of the format
        """
        return "JSON Framework"
    
    def can_parse(self, source: Union[str, Path, IO]) -> bool:
        """Check if this parser can parse the given source.
        
        Args:
            source: The source to check
            
        Returns:
            True if this parser can parse the source, False otherwise
        """
        # Try to parse as JSON
        try:
            if isinstance(source, (str, Path)):
                # If it's a file path
                path = Path(source)
                if path.exists() and path.is_file():
                    with open(path, 'r') as f:
                        content = f.read()
                else:
                    # If it's a JSON string
                    content = source
                    
                # Try to parse as JSON
                data = json.loads(content)
                
                # Check for required fields
                return (isinstance(data, dict) and 
                        "framework_id" in data and
                        "name" in data and
                        "version" in data)
            elif hasattr(source, 'read'):
                # If it's a file-like object
                content = source.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                    
                # Try to parse as JSON
                data = json.loads(content)
                
                # Check for required fields
                return (isinstance(data, dict) and 
                        "framework_id" in data and
                        "name" in data and
                        "version" in data)
                        
            return False
        except Exception as e:
            self.logger.debug(f"Cannot parse as JSON: {str(e)}")
            return False
    
    def parse(self, source: Union[str, Path, IO]) -> ProcessFramework:
        """Parse a process framework from a JSON source.
        
        Args:
            source: The source to parse (file path, file-like object, or JSON string)
            
        Returns:
            A ProcessFramework instance
            
        Raises:
            ValueError: If the source is invalid or cannot be parsed
        """
        try:
            # Get JSON content
            if isinstance(source, (str, Path)):
                path = Path(source)
                if path.exists() and path.is_file():
                    with open(path, 'r') as f:
                        data = json.load(f)
                else:
                    # If it's a JSON string
                    data = json.loads(source)
            elif hasattr(source, 'read'):
                # If it's a file-like object
                content = source.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                data = json.loads(content)
            else:
                raise ValueError("Invalid source type")
                
            # Parse the framework directly
            return ProcessFramework.from_dict(data)
            
        except Exception as e:
            self.logger.error(f"Error parsing JSON framework: {str(e)}")
            raise ValueError(f"Error parsing JSON framework: {str(e)}")
    
    def serialize(self, framework: ProcessFramework) -> Dict[str, Any]:
        """Serialize a process framework to a JSON-compatible dictionary.
        
        Args:
            framework: The framework to serialize
            
        Returns:
            A dictionary representation of the framework
        """
        return framework.to_dict()
    
    def to_json(self, framework: ProcessFramework, indent: int = 2) -> str:
        """Convert a process framework to a JSON string.
        
        Args:
            framework: The framework to convert
            indent: Number of spaces for indentation
            
        Returns:
            A JSON string representation of the framework
        """
        return json.dumps(self.serialize(framework), indent=indent)