"""Module for managing prompts in the agent patterns library."""

import os
from pathlib import Path
from typing import Union

def load_prompt(prompt_path: Union[str, Path]) -> str:
    """Load a prompt from a file.
    
    Args:
        prompt_path: Path to the prompt file, either absolute or relative
        
    Returns:
        The loaded prompt as a string
        
    Raises:
        FileNotFoundError: If the prompt file cannot be found
    """
    # Handle both Path objects and strings
    path = Path(prompt_path) if isinstance(prompt_path, str) else prompt_path
    
    # If the path is absolute, use it directly
    if path.is_absolute():
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        return path.read_text()
        
    # Try to find the file in the repository
    repo_paths = [
        # Directly in src/agent_patterns/prompts
        Path(__file__).parent.parent / "prompts" / path.name,
        # Current directory
        Path.cwd() / path.name,
    ]
    
    for repo_path in repo_paths:
        if repo_path.exists():
            return repo_path.read_text()
            
    raise FileNotFoundError(f"Prompt file not found: {path}")