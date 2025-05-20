#!/usr/bin/env python3

import os
import re

def fix_comment_style(file_path):
    """Fix Python-style comments to JavaScript/CSS style in JS/JSX files."""
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Check if file starts with Python-style comments
    if content.startswith('#'):
        # For CSS files
        if file_path.endswith('.css'):
            # Replace Python-style comments with CSS comments
            content = re.sub(r'^# (.*?)$', r'/* \1 */', content, flags=re.MULTILINE)
        else:
            # Replace Python-style comments with JS comments
            content = re.sub(r'^# (.*?)$', r'// \1', content, flags=re.MULTILINE)
        
        with open(file_path, 'w') as file:
            file.write(content)
        print(f"Fixed: {file_path}")
        return True
    return False

def process_directory(directory):
    """Process all JS, JSX, and CSS files in a directory recursively."""
    fixed_files = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.js', '.jsx', '.css')):
                file_path = os.path.join(root, file)
                if fix_comment_style(file_path):
                    fixed_files += 1
    return fixed_files

if __name__ == "__main__":
    dashboard_dir = "/Users/vamsiduvvuri/My Documents/workspace/ai-native/dashboard"
    fixed_count = process_directory(dashboard_dir)
    print(f"Fixed {fixed_count} files in {dashboard_dir}")