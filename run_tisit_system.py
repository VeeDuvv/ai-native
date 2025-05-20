# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This script starts up our whole knowledge system - the brain that stores
# information and the screen that shows it. It's like turning on a computer
# and a monitor at the same time.

# High School Explanation:
# This script orchestrates the startup of the TISIT Knowledge Graph system,
# including the API server and the dashboard web interface. It handles dependency
# checks, data preparation, and concurrent process management.

import os
import sys
import time
import shutil
import subprocess
import signal
import webbrowser
import platform
from pathlib import Path

# Configuration
API_PORT = 8000
DASHBOARD_PORT = 8080
API_SERVER_COMMAND = ["python", "-m", "uvicorn", "src.tisit.api:app", "--host", "0.0.0.0", "--port", str(API_PORT)]
DASHBOARD_SERVER_COMMAND = ["python", "dashboard_server.py"]
DEFAULT_DATA_DIR = os.path.expanduser("~/.tisit")

# Process tracking
processes = []

def ensure_clean_data_directory():
    """Reset the TISIT data directory to ensure a clean start."""
    data_dir = Path(DEFAULT_DATA_DIR)
    
    print(f"Ensuring clean TISIT data directory: {data_dir}")
    
    # Check if directory exists and remove it
    if data_dir.exists():
        shutil.rmtree(data_dir)
    
    # Create fresh directories
    entities_dir = data_dir / "entities"
    indexes_dir = data_dir / "indexes"
    relationships_dir = data_dir / "relationships"
    
    entities_dir.mkdir(parents=True, exist_ok=True)
    indexes_dir.mkdir(parents=True, exist_ok=True)
    relationships_dir.mkdir(parents=True, exist_ok=True)
    
    print("Data directory is ready.")

def ensure_dependencies():
    """Check for required Python packages."""
    required_packages = ["fastapi", "uvicorn", "networkx", "matplotlib"]
    
    print("Checking dependencies...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing_packages, 
                      check=True,
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE)
        
        print("Dependencies installed successfully.")
    else:
        print("All dependencies are satisfied.")

def stop_all_processes():
    """Stop all running processes."""
    print("\nStopping all services...")
    for proc in processes:
        if proc and proc.poll() is None:  # If process is still running
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                if platform.system() != "Windows":
                    proc.kill()
                else:
                    # Windows-specific process termination if needed
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)])
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

def check_service(url, name, max_attempts=10, delay=1):
    """Check if a service is running by attempting to connect to its URL."""
    import urllib.request
    import urllib.error
    
    print(f"Checking if {name} is running at {url}...")
    
    for attempt in range(max_attempts):
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    print(f"{name} is running!")
                    return True
        except (urllib.error.URLError, urllib.error.HTTPError, ConnectionRefusedError):
            print(f"Waiting for {name} to start (attempt {attempt+1}/{max_attempts})...")
            time.sleep(delay)
    
    print(f"Warning: Could not connect to {name} after {max_attempts} attempts.")
    return False

def create_sample_entity():
    """Create a sample entity to test the system."""
    import urllib.request
    import urllib.error
    import json
    
    print("Creating a sample entity...")
    
    sample_entity = {
        "name": "Sample Campaign",
        "entity_type": "campaign",
        "short_description": "An example campaign",
        "detailed_description": "This is a sample campaign created to test the TISIT knowledge graph.",
        "tags": ["sample", "test"],
        "domain": "testing"
    }
    
    try:
        req = urllib.request.Request(
            url=f"http://localhost:{API_PORT}/entities",
            data=json.dumps(sample_entity).encode(),
            method="POST",
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"Sample entity created with ID: {result['id']}")
            return True
    except Exception as e:
        print(f"Error creating sample entity: {str(e)}")
        return False

def main():
    """Main function to run the TISIT system."""
    # Check for needed dependencies
    ensure_dependencies()
    
    # Prepare data directory
    ensure_clean_data_directory()
    
    # Register cleanup function and signal handlers
    import atexit
    atexit.register(stop_all_processes)
    signal.signal(signal.SIGINT, signal_handler)
    if platform.system() != "Windows":
        signal.signal(signal.SIGTERM, signal_handler)
    
    # Start API server
    api_server = start_service(API_SERVER_COMMAND, "API Server")
    
    # Wait for API server to start
    api_running = check_service(f"http://localhost:{API_PORT}/graph/statistics", "API Server")
    
    if api_running:
        # Create a sample entity
        create_sample_entity()
        
        # Start dashboard server
        dashboard_server = start_service(DASHBOARD_SERVER_COMMAND, "Dashboard Server")
        
        # Wait for dashboard server to start
        dashboard_running = check_service(f"http://localhost:{DASHBOARD_PORT}", "Dashboard Server")
        
        if dashboard_running:
            # Open dashboard in browser
            dashboard_url = f"http://localhost:{DASHBOARD_PORT}"
            print(f"Opening dashboard at {dashboard_url}")
            try:
                webbrowser.open(dashboard_url)
            except Exception as e:
                print(f"Error opening browser: {str(e)}")
                print(f"Please manually navigate to {dashboard_url}")
    
    print("\nAll services started. Press Ctrl+C to stop all services.")
    
    # Wait for processes to complete or get interrupted
    try:
        while all(proc.poll() is None for proc in processes if proc):
            time.sleep(1)
        
        # Check if any process exited unexpectedly
        for i, (proc, name) in enumerate(zip(processes, ["API Server", "Dashboard Server"])):
            if proc and proc.poll() is not None:
                print(f"{name} exited unexpectedly with code {proc.poll()}")
                stderr = proc.stderr.read() if proc.stderr else "No error output"
                print(f"Error output: {stderr}")
    except KeyboardInterrupt:
        pass
    finally:
        stop_all_processes()

if __name__ == "__main__":
    main()