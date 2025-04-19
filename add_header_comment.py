#!/usr/bin/env python3
"""
Script to add the standardized header comment to all Python files in the codebase.
This ensures the critical requirement of not using async is clearly visible in every file.
"""

import os
import sys
from pathlib import Path

# The standardized header comment to be added
HEADER_COMMENT = """# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only
"""

def add_header_to_file(file_path):
    """Add the header comment to a single file if it doesn't already have it."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if header comment is already present
    if HEADER_COMMENT in content:
        print(f"Header already exists in {file_path}")
        return
    
    # If file starts with shebang, preserve it
    if content.startswith('#!'):
        shebang_end = content.find('\n') + 1
        new_content = content[:shebang_end] + '\n' + HEADER_COMMENT + '\n' + content[shebang_end:]
    # If file starts with encoding or docstring, insert after those
    elif content.startswith('# -*- coding') or content.startswith('"""') or content.startswith("'''"):
        lines = content.splitlines()
        insert_pos = 0
        
        # Skip encoding line if present
        if lines[0].startswith('# -*- coding'):
            insert_pos = 1
        
        # Skip docstring if present
        if insert_pos < len(lines) and (lines[insert_pos].startswith('"""') or lines[insert_pos].startswith("'''")):
            insert_pos += 1
            # Find end of docstring
            for i in range(insert_pos, len(lines)):
                if lines[i].endswith('"""') or lines[i].endswith("'''"):
                    insert_pos = i + 1
                    break
        
        # Insert the header after these elements
        if insert_pos >= len(lines):
            new_content = content + '\n\n' + HEADER_COMMENT
        else:
            new_content = '\n'.join(lines[:insert_pos]) + '\n\n' + HEADER_COMMENT + '\n\n' + '\n'.join(lines[insert_pos:])
    else:
        # Otherwise, just add to the beginning
        new_content = HEADER_COMMENT + '\n\n' + content
    
    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Added header to {file_path}")

def process_directory(directory_path, extensions=('.py',)):
    """Process all files in directory and subdirectories with the given extensions."""
    count = 0
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(extensions):
                file_path = os.path.join(root, file)
                add_header_to_file(file_path)
                count += 1
    return count

if __name__ == "__main__":
    # Get the base directory (default to current directory if not provided)
    base_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    base_path = Path(base_dir).resolve()
    
    if not base_path.exists() or not base_path.is_dir():
        print(f"Error: {base_path} is not a valid directory")
        sys.exit(1)
    
    print(f"Adding header comment to all Python files in {base_path}")
    count = process_directory(base_path)
    print(f"Processed {count} Python files") 