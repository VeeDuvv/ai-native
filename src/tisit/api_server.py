# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file starts a special computer program that lets other programs talk to our
# knowledge brain. It's like setting up a lemonade stand where information can be
# shared and found.

# High School Explanation:
# This module provides a command-line utility for starting the TISIT Knowledge Graph
# API server. It configures and launches the FastAPI application with options for
# controlling the host, port, and data directory.

import os
import sys
import argparse
import logging
import uvicorn
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Default settings
DEFAULT_HOST = "127.0.0.1"  # localhost
DEFAULT_PORT = 8000
DEFAULT_DATA_DIR = os.path.expanduser("~/.tisit")

def setup_parser() -> argparse.ArgumentParser:
    """Set up the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="TISIT Knowledge Graph API Server",
        epilog="Start a REST API server for the TISIT knowledge graph."
    )
    
    parser.add_argument('--host', type=str, default=DEFAULT_HOST,
                      help=f"Host to bind the server to (default: {DEFAULT_HOST})")
    
    parser.add_argument('--port', type=int, default=DEFAULT_PORT,
                      help=f"Port to bind the server to (default: {DEFAULT_PORT})")
    
    parser.add_argument('--data-dir', type=str, default=DEFAULT_DATA_DIR,
                      help=f"Directory for storing TISIT data (default: {DEFAULT_DATA_DIR})")
    
    parser.add_argument('--reload', action='store_true',
                      help="Enable auto-reload during development")
    
    parser.add_argument('--log-level', type=str, default="info",
                      choices=["debug", "info", "warning", "error", "critical"],
                      help="Set the logging level (default: info)")
    
    return parser

def main():
    """Main entry point for the API server."""
    parser = setup_parser()
    args = parser.parse_args()
    
    # Set log level
    log_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }
    logging.getLogger().setLevel(log_levels[args.log_level])
    
    # Ensure data directory exists
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Set the TISIT_DATA_DIR environment variable
    os.environ["TISIT_DATA_DIR"] = str(data_dir)
    
    logger.info(f"Starting TISIT Knowledge Graph API server")
    logger.info(f"Host: {args.host}")
    logger.info(f"Port: {args.port}")
    logger.info(f"Data directory: {args.data_dir}")
    
    # Start the server
    uvicorn.run(
        "src.tisit.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()