#!/usr/bin/env python

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only

"""
Fix imports and prompt paths in agent-patterns examples.

This script updates:
1. Import statements from src.agent_patterns to agent_patterns 
2. Prompt directory paths to handle both development and installed paths
"""

import os
import re
import sys
from pathlib import Path

def fix_file(file_path):
    """Fix imports and prompt paths in a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix imports
    fixed_imports = re.sub(
        r'from src\.agent_patterns', 
        'from agent_patterns', 
        content
    )
    
    # Fix prompt directories
    prompt_dir_pattern = r'prompt_dir = str\(project_root / "src" / "agent_patterns" / "prompts"\)'
    prompt_dir_replacement = '''
# Try to find prompts directory - check both installed package and development paths
src_prompt_dir = project_root / "src" / "agent_patterns" / "prompts"
pkg_prompt_dir = project_root / "agent_patterns" / "prompts"

if src_prompt_dir.exists():
    prompt_dir = str(src_prompt_dir)
else:
    prompt_dir = str(pkg_prompt_dir)'''
    
    fixed_prompt_dirs = re.sub(
        prompt_dir_pattern,
        prompt_dir_replacement,
        fixed_imports
    )
    
    # Only write if changes were made
    if fixed_prompt_dirs != content:
        with open(file_path, 'w') as f:
            f.write(fixed_prompt_dirs)
        return True
    
    return False

def fix_directory(directory):
    """Fix all Python files in a directory and its subdirectories."""
    fixed_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_file(file_path):
                    fixed_files.append(file_path)
    
    return fixed_files

def main():
    """Main entry point."""
    # Get the repository root
    repo_root = Path(__file__).parent.parent
    
    # Directories to fix
    directories = [
        repo_root / "examples",
        repo_root / "tests"
    ]
    
    fixed_files = []
    for directory in directories:
        fixed_files.extend(fix_directory(directory))
    
    # Print summary
    print(f"Fixed {len(fixed_files)} files:")
    for file in fixed_files:
        print(f"  - {file}")

if __name__ == "__main__":
    main() 