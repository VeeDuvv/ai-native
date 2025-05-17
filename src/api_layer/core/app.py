"""
API application core module.
"""

from fastapi import FastAPI

# Create a minimal app for testing
app = FastAPI()

def create_response(data=None, meta=None, links=None, included=None):
    """Create a standard response."""
    response = {}
    
    if data is not None:
        response["data"] = data
        
    if meta is not None:
        response["meta"] = meta
    else:
        response["meta"] = {
            "timestamp": "This will be filled in by middleware"
        }
        
    if links is not None:
        response["links"] = links
        
    if included is not None:
        response["included"] = included
        
    return response

def create_error_response(status_code, error_code, title, detail=None, source=None):
    """Create a standard error response."""
    error = {
        "code": error_code,
        "title": title,
        "status": str(status_code)
    }
    
    if detail:
        error["detail"] = detail
        
    if source:
        error["source"] = source
        
    return {
        "errors": [error],
        "meta": {
            "timestamp": "This will be filled in by middleware"
        }
    }
