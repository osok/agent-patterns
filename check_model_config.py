#!/usr/bin/env python3

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only

"""
Script to check if all examples properly use environment variables for model configuration.

This script analyzes all example files to identify which ones need to be updated
to use the .env file for determining LLM source and model.
"""

import os
import re
import sys
from pathlib import Path

def analyze_file(file_path):
    """
    Analyze a Python file to check if it properly uses environment variables for model configuration.
    
    Returns:
        dict: Analysis results with status and suggestions
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Initialize result
    result = {
        'path': str(file_path),
        'filename': file_path.name,
        'uses_env_vars': False,
        'uses_model_config_util': False,
        'has_hardcoded_models': False,
        'hardcoded_models': [],
        'needs_update': False,
        'suggestion': ''
    }
    
    # Check if file imports model_config utility
    model_config_import = re.search(r'from\s+examples\.utils\.model_config\s+import', content)
    if model_config_import:
        result['uses_model_config_util'] = True
    
    # Check if file uses environment variables for models
    env_var_patterns = [
        r'os\.getenv\(["\'].*MODEL_PROVIDER["\']',
        r'os\.getenv\(["\'].*MODEL_NAME["\']',
        r'os\.environ\.get\(["\'].*MODEL_PROVIDER["\']',
        r'os\.environ\.get\(["\'].*MODEL_NAME["\']'
    ]
    
    for pattern in env_var_patterns:
        if re.search(pattern, content):
            result['uses_env_vars'] = True
            break
    
    # Check for hardcoded model names
    hardcoded_model_patterns = [
        r'["\'](gpt-4[^"\']*)["\']',
        r'["\'](gpt-3.5[^"\']*)["\']',
        r'["\'](claude[^"\']*)["\']',
        r'["\'](llama[^"\']*)["\']',
        r'["\'](text-davinci[^"\']*)["\']'
    ]
    
    for pattern in hardcoded_model_patterns:
        matches = re.findall(pattern, content)
        if matches:
            result['has_hardcoded_models'] = True
            result['hardcoded_models'].extend(matches)
    
    # Determine if file needs update
    if (result['has_hardcoded_models'] and not result['uses_env_vars'] and 
            not result['uses_model_config_util']):
        result['needs_update'] = True
        result['suggestion'] = "Update to use environment variables or the model_config utility"
    
    return result

def main():
    """Find all example files and analyze their model configuration usage."""
    # Find the repository root directory
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir
    
    # Find all example Python files
    examples_dir = repo_root / 'examples'
    if not examples_dir.exists():
        print(f"Error: Examples directory not found at {examples_dir}")
        sys.exit(1)
    
    example_files = []
    for root, _, files in os.walk(examples_dir):
        for file in files:
            if file.endswith('.py'):
                example_files.append(Path(root) / file)
    
    print(f"Found {len(example_files)} example files to analyze")
    
    # Analyze each file
    needs_update = []
    for file_path in example_files:
        result = analyze_file(file_path)
        if result['needs_update']:
            needs_update.append(result)
            print(f"❌ {result['path']} - NEEDS UPDATE")
            print(f"   Hardcoded models: {', '.join(result['hardcoded_models'])}")
            print(f"   Suggestion: {result['suggestion']}")
        else:
            print(f"✅ {result['path']} - OK")
    
    # Summary
    print("\n=== SUMMARY ===")
    print(f"Total example files: {len(example_files)}")
    print(f"Files needing update: {len(needs_update)}")
    
    if needs_update:
        print("\nSuggested update strategy:")
        print("1. Use the model_config utility from examples/utils/model_config.py")
        print("2. Replace hardcoded model values with environment variable references")
        print("3. Add proper fallbacks for missing environment variables")
    else:
        print("\nAll example files are properly using environment variables for model configuration!")

if __name__ == "__main__":
    main() 