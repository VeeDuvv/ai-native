# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This program starts all the pieces needed for our knowledge brain dashboard.
# It's like turning on multiple machines that work together to show information.

# High School Explanation:
# This script orchestrates the launching of all required components for the
# TISIT knowledge graph dashboard: the API server, the proxy server, and the
# dashboard server. It uses Python's subprocess module to run all components
# concurrently and handles graceful shutdown when interrupted.

import subprocess
import sys
import os
import time
import atexit
import signal
import webbrowser
from pathlib import Path

# Configuration
DASHBOARD_URL = "http://localhost:8080"
API_SERVER_COMMAND = ["python", "-m", "uvicorn", "src.tisit.api:app", "--host", "0.0.0.0", "--port", "8000"]
PROXY_SERVER_COMMAND = ["python", "serve_proxy.py"]
DASHBOARD_SERVER_COMMAND = ["python", "serve_dashboard.py"]

# Process tracking
processes = []

def ensure_file_exists(file_path):
    """Check if a file exists and exit if it doesn't."""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        sys.exit(1)

def stop_all_processes():
    """Stop all running processes."""
    print("\nStopping all services...")
    for proc in processes:
        if proc.poll() is None:  # If process is still running
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
    print("All services stopped.")

def signal_handler(sig, frame):
    """Handle interrupt signals to ensure clean shutdown."""
    stop_all_processes()
    sys.exit(0)

def start_service(command, name):
    """Start a service as a subprocess and return the process object."""
    print(f"Starting {name}...")
    try:
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        processes.append(proc)
        return proc
    except Exception as e:
        print(f"Error starting {name}: {str(e)}")
        stop_all_processes()
        sys.exit(1)

def main():
    """Main function to run all components of the dashboard."""
    # Check required files
    ensure_file_exists("simple-dashboard.html")
    ensure_file_exists("serve_dashboard.py")
    ensure_file_exists("serve_proxy.py")
    
    # Register cleanup function and signal handlers
    atexit.register(stop_all_processes)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start all services
    api_server = start_service(API_SERVER_COMMAND, "API Server")
    time.sleep(1)  # Wait for API server to start
    
    proxy_server = start_service(PROXY_SERVER_COMMAND, "Proxy Server")
    time.sleep(1)  # Wait for proxy server to start
    
    dashboard_server = start_service(DASHBOARD_SERVER_COMMAND, "Dashboard Server")
    time.sleep(1)  # Wait for dashboard server to start
    
    # Open dashboard in browser
    print(f"Opening dashboard at {DASHBOARD_URL}")
    try:
        webbrowser.open(DASHBOARD_URL)
    except Exception as e:
        print(f"Error opening browser: {str(e)}")
    
    print("\nAll services started. Press Ctrl+C to stop all services.")
    
    # Wait for processes to complete or get interrupted
    try:
        while all(proc.poll() is None for proc in processes):
            time.sleep(1)
        
        # Check if any process exited unexpectedly
        for proc, name in zip(processes, ["API Server", "Proxy Server", "Dashboard Server"]):
            if proc.poll() is not None:
                print(f"{name} exited unexpectedly with code {proc.poll()}")
                print(f"STDOUT: {proc.stdout.read()}")
                print(f"STDERR: {proc.stderr.read()}")
    except KeyboardInterrupt:
        pass
    finally:
        stop_all_processes()

if __name__ == "__main__":
    main()