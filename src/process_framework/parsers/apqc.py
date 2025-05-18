# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps our system understand APQC business process documents that are stored
# in Excel spreadsheets. It reads all the rows and columns and figures out how processes
# are organized and what they do.

# High School Explanation:
# This module implements a parser for APQC Process Classification Framework (PCF) Excel files.
# It extracts the hierarchical process structure, metadata, and relationships from APQC's
# standardized Excel format and converts it into our unified ProcessFramework model.

import os
import re
import logging
from typing import Dict, Any, Optional, List, Union, IO, Tuple
from pathlib import Path
import uuid

import pandas as pd

from .base import FrameworkParser
from ..core import ProcessFramework, Process, Activity, ProcessInput, ProcessOutput, ProcessRole, ProcessMetric


class APQCExcelParser(FrameworkParser):
    """Parser for APQC Process Classification Framework (PCF) Excel files.
    
    This parser handles the standard Excel format used by APQC to distribute
    their Process Classification Framework, transforming it into our unified model.
    """
    
    # APQC typically uses a hierarchical numbering system: 1.0, 1.1, 1.1.1, etc.
    ID_PATTERN = re.compile(r'^\d+(\.\d+)*$')
    
    # Column names in typical APQC Excel files (may vary by version)
    DEFAULT_ID_COLUMN = 'Process ID'
    DEFAULT_NAME_COLUMN = 'Process Name'
    DEFAULT_DEFINITION_COLUMN = 'Process Definition'
    
    def __init__(self) -> None:
        """Initialize the APQC Excel parser."""
        self.logger = logging.getLogger(__name__)
    
    def get_format_name(self) -> str:
        """Get the name of the format this parser handles.
        
        Returns:
            The name of the format
        """
        return "APQC Excel Framework"
    
    def can_parse(self, source: Union[str, Path, IO]) -> bool:
        """Check if this parser can parse the given source.
        
        Args:
            source: The source to check
            
        Returns:
            True if this parser can parse the source, False otherwise
        """
        try:
            # Only process file paths for Excel
            if not isinstance(source, (str, Path)):
                return False
                
            path = Path(source)
            if not path.exists() or not path.is_file():
                return False
                
            # Check file extension
            if path.suffix.lower() not in ['.xlsx', '.xls']:
                return False
                
            # Try to read the Excel file
            df = pd.read_excel(path, nrows=10)  # Just read a few rows to check
            
            # Look for expected columns or patterns
            columns = df.columns.tolist()
            
            # Check if we have ID and name columns (various possible names)
            id_column = self._find_id_column(df)
            name_column = self._find_name_column(df)
            
            if id_column and name_column:
                # Check if IDs follow APQC pattern
                ids = df[id_column].dropna().astype(str).tolist()
                valid_ids = [self.ID_PATTERN.match(id_str) is not None for id_str in ids[:5]]
                return any(valid_ids)
                
            return False
            
        except Exception as e:
            self.logger.debug(f"Cannot parse as APQC Excel: {str(e)}")
            return False
    
    def _find_id_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the ID column in the DataFrame.
        
        Args:
            df: DataFrame to search
            
        Returns:
            The name of the ID column if found, None otherwise
        """
        possible_names = [
            'Process ID', 'ID', 'PCF ID', 'Activity ID', 
            'Process Number', 'Number', 'Process Code'
        ]
        
        for name in possible_names:
            if name in df.columns:
                return name
                
        # If no exact match, try case-insensitive match
        columns = df.columns.tolist()
        for col in columns:
            for name in possible_names:
                if name.lower() in col.lower():
                    return col
                    
        return None
    
    def _find_name_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the name column in the DataFrame.
        
        Args:
            df: DataFrame to search
            
        Returns:
            The name of the name column if found, None otherwise
        """
        possible_names = [
            'Process Name', 'Name', 'Activity Name', 
            'Process Title', 'Title', 'Process Description'
        ]
        
        for name in possible_names:
            if name in df.columns:
                return name
                
        # If no exact match, try case-insensitive match
        columns = df.columns.tolist()
        for col in columns:
            for name in possible_names:
                if name.lower() in col.lower():
                    return col
                    
        return None
    
    def _find_definition_column(self, df: pd.DataFrame) -> Optional[str]:
        """Find the definition column in the DataFrame.
        
        Args:
            df: DataFrame to search
            
        Returns:
            The name of the definition column if found, None otherwise
        """
        possible_names = [
            'Process Definition', 'Definition', 'Description',
            'Process Description', 'Detail', 'Process Detail'
        ]
        
        for name in possible_names:
            if name in df.columns:
                return name
                
        # If no exact match, try case-insensitive match
        columns = df.columns.tolist()
        for col in columns:
            for name in possible_names:
                if name.lower() in col.lower():
                    return col
                    
        return None
    
    def parse(self, source: Union[str, Path, IO]) -> ProcessFramework:
        """Parse an APQC Process Classification Framework from an Excel file.
        
        Args:
            source: The source to parse (file path)
            
        Returns:
            A ProcessFramework instance
            
        Raises:
            ValueError: If the source is invalid or cannot be parsed
        """
        try:
            # Only process file paths for Excel
            if not isinstance(source, (str, Path)):
                raise ValueError("APQC parser requires a file path")
                
            path = Path(source)
            if not path.exists() or not path.is_file():
                raise ValueError(f"File does not exist: {path}")
                
            # Read the Excel file
            df = pd.read_excel(path)
            
            # Find key columns
            id_column = self._find_id_column(df)
            name_column = self._find_name_column(df)
            definition_column = self._find_definition_column(df)
            
            if not id_column or not name_column:
                raise ValueError("Could not identify required columns in the Excel file")
                
            # Clean the data
            df = df.dropna(subset=[id_column])
            df[id_column] = df[id_column].astype(str)
            
            # Get framework metadata from file name or header if available
            framework_name = "APQC Process Classification Framework"
            framework_version = "Unknown"
            
            # Try to extract version from filename
            filename = path.stem
            version_match = re.search(r'v(\d+\.\d+(\.\d+)?)', filename)
            if version_match:
                framework_version = version_match.group(1)
                
            # Create the framework
            framework = ProcessFramework(
                framework_id=f"apqc_{framework_version.replace('.', '_')}",
                name=framework_name,
                version=framework_version,
                description="APQC Process Classification Framework (PCF)",
                organization="APQC (American Productivity & Quality Center)",
                website="https://www.apqc.org",
                source=str(path)
            )
            
            # Parse the hierarchical process structure
            self._parse_processes(df, id_column, name_column, definition_column, framework)
            
            return framework
            
        except Exception as e:
            self.logger.error(f"Error parsing APQC Excel framework: {str(e)}")
            raise ValueError(f"Error parsing APQC Excel framework: {str(e)}")
    
    def _parse_processes(self, df: pd.DataFrame, id_column: str, name_column: str, 
                        definition_column: Optional[str], framework: ProcessFramework) -> None:
        """Parse processes from the DataFrame into the framework.
        
        Args:
            df: DataFrame containing the processes
            id_column: Name of the ID column
            name_column: Name of the name column
            definition_column: Name of the definition column (if available)
            framework: The framework to add processes to
        """
        # Sort by process ID to ensure proper hierarchy
        df = df.sort_values(by=[id_column])
        
        # Create a dictionary to keep track of processes by ID
        processes: Dict[str, Process] = {}
        
        # First pass: create all processes
        for _, row in df.iterrows():
            process_id = str(row[id_column]).strip()
            name = str(row[name_column]).strip()
            
            # Skip invalid rows
            if not process_id or not name:
                continue
                
            # Get description if available
            description = ""
            if definition_column and definition_column in row:
                description = str(row[definition_column]) if pd.notna(row[definition_column]) else ""
                
            # Create the process
            process = Process(
                process_id=process_id,
                name=name,
                description=description
            )
            
            processes[process_id] = process
            
        # Second pass: establish hierarchy
        for process_id, process in processes.items():
            # Calculate parent ID based on APQC's hierarchical ID structure
            # For example, for 1.2.3, the parent is 1.2
            parts = process_id.split('.')
            
            if len(parts) == 1:
                # Top-level process (e.g., 1, 2, 3)
                framework.add_process(process)
            elif len(parts) > 1:
                # Sub-process (e.g., 1.1, 1.2, 1.2.3)
                parent_id = '.'.join(parts[:-1])
                
                if parent_id in processes:
                    processes[parent_id].add_sub_process(process)
                else:
                    # Handle missing parent by creating a placeholder
                    self.logger.warning(f"Parent process {parent_id} not found for {process_id}")
                    
                    # Create placeholder parent
                    parent = Process(
                        process_id=parent_id,
                        name=f"Process {parent_id}",
                        description=f"Placeholder for missing process {parent_id}"
                    )
                    
                    processes[parent_id] = parent
                    parent.add_sub_process(process)
                    
                    # Add to framework or higher-level parent
                    if len(parent_id.split('.')) == 1:
                        framework.add_process(parent)
                    else:
                        grandparent_id = '.'.join(parent_id.split('.')[:-1])
                        if grandparent_id in processes:
                            processes[grandparent_id].add_sub_process(parent)
            
        # Third pass: convert leaf processes to activities
        self._convert_leaf_processes_to_activities(processes)