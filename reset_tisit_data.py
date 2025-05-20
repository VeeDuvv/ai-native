# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This script cleans up our knowledge brain storage by deleting all the files
# and folders where data is kept, so we can start fresh without any errors.

# High School Explanation:
# This script removes all TISIT knowledge graph data from the default storage
# location, allowing a clean start without corrupted entity files.
# It resets the storage directory and its contents.

import os
import shutil
from pathlib import Path

# Default TISIT data directory
DEFAULT_DATA_DIR = os.path.expanduser("~/.tisit")

def reset_tisit_data():
    """Reset the TISIT data directory by removing and recreating it."""
    data_dir = Path(DEFAULT_DATA_DIR)
    
    print(f"Resetting TISIT data directory: {data_dir}")
    
    # Check if directory exists
    if data_dir.exists():
        # Remove the directory and all its contents
        print("Removing existing data...")
        shutil.rmtree(data_dir)
        print("Data removed successfully.")
    
    # Create fresh directories
    print("Creating new directories...")
    entities_dir = data_dir / "entities"
    indexes_dir = data_dir / "indexes"
    relationships_dir = data_dir / "relationships"
    
    entities_dir.mkdir(parents=True, exist_ok=True)
    indexes_dir.mkdir(parents=True, exist_ok=True)
    relationships_dir.mkdir(parents=True, exist_ok=True)
    
    print("Reset complete. TISIT data directory has been recreated.")

if __name__ == "__main__":
    reset_tisit_data()