# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file contains functions that help us create standard responses for our web service.
# It's like making sure all our letters follow the same template so people know what to expect.

# High School Explanation:
# This module provides standardized functions for creating consistent API responses
# and error messages. It ensures that all API endpoints return data in a uniform format,
# making it easier for clients to consume and process the responses.

"""
API response formatting utilities.

This module provides functions for creating standardized API responses
and error responses to ensure consistency across all API endpoints.
"""

from typing import Dict, List, Optional, Any, Union


def create_response(data=None, meta=None, links=None, included=None):
    """
    Create a standardized API response.
    
    Args:
        data: The primary response data
        meta: Additional metadata
        links: HATEOAS links
        included: Related resources
        
    Returns:
        Dict: Standardized response object
    """
    response = {}
    
    if data is not None:
        response["data"] = data
        
    if meta is not None:
        response["meta"] = meta
    else:
        response["meta"] = {}
        
    if links is not None:
        response["links"] = links
        
    if included is not None:
        response["included"] = included
        
    return response


def create_error_response(status_code, error_code, title, detail=None, source=None):
    """
    Create a standardized error response.
    
    Args:
        status_code: HTTP status code
        error_code: Application-specific error code
        title: A short, human-readable summary of the problem
        detail: A human-readable explanation of the error
        source: An object containing references to the source of the error
        
    Returns:
        Dict: Standardized error response object
    """
    error = {
        "status": str(status_code),
        "code": error_code,
        "title": title
    }
    
    if detail:
        error["detail"] = detail
        
    if source:
        error["source"] = source
        
    return {
        "errors": [error],
        "meta": {}
    }