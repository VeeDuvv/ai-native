# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps our system understand eTOM business process documents that use XML format.
# It's like a special translator that can read a specific type of business recipe and
# convert it into something our AI helpers can understand.

# High School Explanation:
# This module implements a parser for the eTOM (enhanced Telecom Operations Map) framework
# in XML format. It extracts the process hierarchy, relationships, and metadata from the
# TM Forum's standardized XML representation and transforms it into our unified model.

import os
import re
import logging
from typing import Dict, Any, Optional, List, Union, IO, Tuple
from pathlib import Path
import uuid
import xml.etree.ElementTree as ET

from .base import FrameworkParser
from ..core import ProcessFramework, Process, Activity, ProcessInput, ProcessOutput, ProcessRole, ProcessMetric


class ETOMXmlParser(FrameworkParser):
    """Parser for eTOM (enhanced Telecom Operations Map) XML files.
    
    This parser handles the XML format used by TM Forum for distributing
    the eTOM framework, converting it into our unified model.
    """
    
    # Namespace map for eTOM XML
    NAMESPACES = {
        'etom': 'http://www.tmforum.org/xml/etom',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    
    def __init__(self) -> None:
        """Initialize the eTOM XML parser."""
        self.logger = logging.getLogger(__name__)
    
    def get_format_name(self) -> str:
        """Get the name of the format this parser handles.
        
        Returns:
            The name of the format
        """
        return "eTOM XML Framework"
    
    def can_parse(self, source: Union[str, Path, IO]) -> bool:
        """Check if this parser can parse the given source.
        
        Args:
            source: The source to check
            
        Returns:
            True if this parser can parse the source, False otherwise
        """
        try:
            # Get XML content
            if isinstance(source, (str, Path)):
                path = Path(source)
                if path.exists() and path.is_file():
                    if path.suffix.lower() != '.xml':
                        return False
                        
                    with open(path, 'r') as f:
                        content = f.read()
                else:
                    # If it's an XML string
                    content = source
            elif hasattr(source, 'read'):
                # If it's a file-like object
                content = source.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
            else:
                return False
                
            # Check for eTOM XML markers
            if ('<etom:' in content or 
                'xmlns:etom=' in content or 
                'tmforum.org/xml/etom' in content):
                return True
                
            # Try parsing as XML and check root element
            root = ET.fromstring(content)
            if root.tag == '{http://www.tmforum.org/xml/etom}ProcessFramework' or root.tag == 'ProcessFramework':
                return True
                
            return False
            
        except Exception as e:
            self.logger.debug(f"Cannot parse as eTOM XML: {str(e)}")
            return False
    
    def parse(self, source: Union[str, Path, IO]) -> ProcessFramework:
        """Parse an eTOM framework from an XML source.
        
        Args:
            source: The source to parse (file path, file-like object, or XML string)
            
        Returns:
            A ProcessFramework instance
            
        Raises:
            ValueError: If the source is invalid or cannot be parsed
        """
        try:
            # Get XML content
            if isinstance(source, (str, Path)):
                path = Path(source)
                if path.exists() and path.is_file():
                    tree = ET.parse(path)
                    root = tree.getroot()
                    source_path = str(path)
                else:
                    # If it's an XML string
                    root = ET.fromstring(source)
                    source_path = "string"
            elif hasattr(source, 'read'):
                # If it's a file-like object
                content = source.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                root = ET.fromstring(content)
                source_path = "stream"
            else:
                raise ValueError("Invalid source type")
                
            # Extract namespace if present
            ns = '{http://www.tmforum.org/xml/etom}' if root.tag.startswith('{') else ''
            
            # Extract framework metadata
            framework_name = "eTOM Framework"
            framework_version = "Unknown"
            framework_description = "Enhanced Telecom Operations Map"
            
            # Look for metadata in the root element
            if root.tag == f'{ns}ProcessFramework' or root.tag == 'ProcessFramework':
                if 'name' in root.attrib:
                    framework_name = root.attrib['name']
                if 'version' in root.attrib:
                    framework_version = root.attrib['version']
                if 'description' in root.attrib:
                    framework_description = root.attrib['description']
                    
                # Look for description element
                desc_elem = root.find(f'{ns}Description') or root.find('Description')
                if desc_elem is not None and desc_elem.text:
                    framework_description = desc_elem.text.strip()
            
            # Create the framework
            framework = ProcessFramework(
                framework_id=f"etom_{framework_version.replace('.', '_')}",
                name=framework_name,
                version=framework_version,
                description=framework_description,
                organization="TM Forum",
                website="https://www.tmforum.org",
                source=source_path
            )
            
            # Parse process areas (top-level processes)
            process_areas = root.findall(f'{ns}ProcessArea') or root.findall('ProcessArea')
            for area in process_areas:
                self._parse_process_area(area, framework, ns)
                
            return framework
            
        except Exception as e:
            self.logger.error(f"Error parsing eTOM XML framework: {str(e)}")
            raise ValueError(f"Error parsing eTOM XML framework: {str(e)}")
    
    def _parse_process_area(self, area_elem: ET.Element, framework: ProcessFramework, ns: str) -> None:
        """Parse a process area (top-level process) from an XML element.
        
        Args:
            area_elem: XML element representing the process area
            framework: The framework to add the process to
            ns: XML namespace
        """
        area_id = area_elem.attrib.get('id', f"area_{len(framework.root_processes) + 1}")
        area_name = area_elem.attrib.get('name', f"Process Area {area_id}")
        
        # Get description if available
        area_desc = ""
        desc_elem = area_elem.find(f'{ns}Description') or area_elem.find('Description')
        if desc_elem is not None and desc_elem.text:
            area_desc = desc_elem.text.strip()
            
        # Create the process area
        area_process = Process(
            process_id=area_id,
            name=area_name,
            description=area_desc
        )
        
        # Parse process groups within the area
        process_groups = area_elem.findall(f'{ns}ProcessGroup') or area_elem.findall('ProcessGroup')
        for group in process_groups:
            self._parse_process_group(group, area_process, ns)
            
        # Add to framework
        framework.add_process(area_process)
    
    def _parse_process_group(self, group_elem: ET.Element, parent_process: Process, ns: str) -> None:
        """Parse a process group (mid-level process) from an XML element.
        
        Args:
            group_elem: XML element representing the process group
            parent_process: The parent process to add this group to
            ns: XML namespace
        """
        group_id = group_elem.attrib.get('id', f"{parent_process.process_id}.{len(parent_process.sub_processes) + 1}")
        group_name = group_elem.attrib.get('name', f"Process Group {group_id}")
        
        # Get description if available
        group_desc = ""
        desc_elem = group_elem.find(f'{ns}Description') or group_elem.find('Description')
        if desc_elem is not None and desc_elem.text:
            group_desc = desc_elem.text.strip()
            
        # Create the process group
        group_process = Process(
            process_id=group_id,
            name=group_name,
            description=group_desc
        )
        
        # Parse processes within the group
        processes = group_elem.findall(f'{ns}Process') or group_elem.findall('Process')
        for process in processes:
            self._parse_process(process, group_process, ns)
            
        # Add to parent
        parent_process.add_sub_process(group_process)
    
    def _parse_process(self, process_elem: ET.Element, parent_process: Process, ns: str) -> None:
        """Parse a process from an XML element.
        
        Args:
            process_elem: XML element representing the process
            parent_process: The parent process to add this process to
            ns: XML namespace
        """
        process_id = process_elem.attrib.get('id', f"{parent_process.process_id}.{len(parent_process.sub_processes) + 1}")
        process_name = process_elem.attrib.get('name', f"Process {process_id}")
        
        # Get description if available
        process_desc = ""
        desc_elem = process_elem.find(f'{ns}Description') or process_elem.find('Description')
        if desc_elem is not None and desc_elem.text:
            process_desc = desc_elem.text.strip()
            
        # Create the process
        sub_process = Process(
            process_id=process_id,
            name=process_name,
            description=process_desc
        )
        
        # Parse activities within the process
        activities = process_elem.findall(f'{ns}Activity') or process_elem.findall('Activity')
        for activity in activities:
            self._parse_activity(activity, sub_process, ns)
            
        # Parse sub-processes if any
        sub_processes = process_elem.findall(f'{ns}Process') or process_elem.findall('Process')
        for sub_proc in sub_processes:
            self._parse_process(sub_proc, sub_process, ns)
            
        # Add to parent
        parent_process.add_sub_process(sub_process)
    
    def _parse_activity(self, activity_elem: ET.Element, parent_process: Process, ns: str) -> None:
        """Parse an activity from an XML element.
        
        Args:
            activity_elem: XML element representing the activity
            parent_process: The parent process to add this activity to
            ns: XML namespace
        """
        activity_id = activity_elem.attrib.get('id', f"{parent_process.process_id}.{len(parent_process.activities) + 1}")
        activity_name = activity_elem.attrib.get('name', f"Activity {activity_id}")
        
        # Get description if available
        activity_desc = ""
        desc_elem = activity_elem.find(f'{ns}Description') or activity_elem.find('Description')
        if desc_elem is not None and desc_elem.text:
            activity_desc = desc_elem.text.strip()
            
        # Parse inputs
        inputs = []
        inputs_elem = activity_elem.find(f'{ns}Inputs') or activity_elem.find('Inputs')
        if inputs_elem is not None:
            for input_elem in inputs_elem:
                input_id = input_elem.attrib.get('id', f"input_{uuid.uuid4().hex[:8]}")
                input_name = input_elem.attrib.get('name', f"Input {input_id}")
                input_desc = input_elem.text.strip() if input_elem.text else ""
                
                inputs.append(ProcessInput(
                    id=input_id,
                    name=input_name,
                    description=input_desc,
                    data_type="string"  # Default type
                ))
                
        # Parse outputs
        outputs = []
        outputs_elem = activity_elem.find(f'{ns}Outputs') or activity_elem.find('Outputs')
        if outputs_elem is not None:
            for output_elem in outputs_elem:
                output_id = output_elem.attrib.get('id', f"output_{uuid.uuid4().hex[:8]}")
                output_name = output_elem.attrib.get('name', f"Output {output_id}")
                output_desc = output_elem.text.strip() if output_elem.text else ""
                
                outputs.append(ProcessOutput(
                    id=output_id,
                    name=output_name,
                    description=output_desc,
                    data_type="string"  # Default type
                ))
                
        # Create the activity
        activity = Activity(
            activity_id=activity_id,
            name=activity_name,
            description=activity_desc,
            inputs=inputs,
            outputs=outputs
        )
        
        # Add to parent process
        parent_process.add_activity(activity)