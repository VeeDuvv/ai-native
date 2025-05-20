# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file is the main control center for our web service. It sets up how
# people can talk to our AI helpers through the internet and makes sure
# everything works together smoothly.

# High School Explanation:
# This module initializes the FastAPI application, configures middleware,
# registers API routes, and provides core functionality for standardized
# response formatting. It serves as the entry point for the API layer.

"""
API application core module.

This module initializes the FastAPI application, configures middleware, sets up
error handling, and registers all API routes from the various controllers.
"""

from datetime import datetime
import json
import logging
from typing import Dict, List, Optional, Any, Union

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.api_layer.core.config import config
from src.api_layer.core.responses import create_response, create_error_response

# Set up logging
logger = logging.getLogger("api")

# Create FastAPI app
app = FastAPI(
    title="AI-Native Ad Agency API",
    description="API for the AI-Native Ad Agency platform",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.allow_origins,
    allow_credentials=config.cors.allow_credentials,
    allow_methods=config.cors.allow_methods,
    allow_headers=config.cors.allow_headers,
)

# Create response timestamp middleware
@app.middleware("http")
async def add_timestamp_to_response(request: Request, call_next):
    """Add timestamp to all JSON responses."""
    # Process request
    response = await call_next(request)
    
    # Only modify JSON responses
    if response.headers.get("content-type") == "application/json":
        # Get response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
            
        # Parse body
        try:
            data = json.loads(body)
            
            # Add timestamp to meta
            if "meta" in data:
                data["meta"]["timestamp"] = datetime.utcnow().isoformat()
            
            # Create new response
            return JSONResponse(
                content=data,
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        except json.JSONDecodeError:
            # If we can't parse the body, return the original response
            pass
            
    return response


# Create API router
api_router = APIRouter(prefix="/api/v1")

# We need to import controllers after defining 'app' to avoid circular imports
from src.api_layer.controllers import (
    auth,
    campaigns,
    creatives,
    audiences,
    media,
)

# Register controller routers
api_router.include_router(auth.router)
api_router.include_router(campaigns.router)
api_router.include_router(creatives.router)
api_router.include_router(audiences.router)
api_router.include_router(media.router)

# Register API router with app
app.include_router(api_router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint for the API."""
    return create_response(
        data={
            "name": "AI-Native Ad Agency API",
            "version": app.version,
            "status": "operational"
        },
        links={
            "documentation": "/api/docs",
            "openapi": "/api/openapi.json"
        }
    )