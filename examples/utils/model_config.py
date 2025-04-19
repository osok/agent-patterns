"""
Utility functions for model configuration.

This module provides standardized functions to load and configure models
from environment variables, ensuring consistent model usage across all examples.
"""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



import os
import logging
from typing import Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)

def get_model_config(role: str) -> Dict[str, str]:
    """
    Get model configuration for a specific role from environment variables.
    
    Args:
        role: The role of the model (e.g., 'reflection', 'planning', 'worker', etc.)
        
    Returns:
        Dictionary with model provider and name
        
    Raises:
        ValueError: If required environment variables are not set
    """
    # Convert role to uppercase for environment variable naming convention
    role_upper = role.upper()
    
    # Try to get provider and model name from environment variables
    provider_env = f"{role_upper}_MODEL_PROVIDER"
    model_name_env = f"{role_upper}_MODEL_NAME"
    
    provider = os.getenv(provider_env)
    model_name = os.getenv(model_name_env)
    
    if not provider or not model_name:
        raise ValueError(
            f"Required environment variables for {role} model are not set. "
            f"Please define {provider_env} and {model_name_env} in your .env file."
        )
    
    return {
        "provider": provider,
        "model_name": model_name
    }

def get_llm_configs() -> Dict[str, Dict[str, str]]:
    """
    Get standard LLM configurations for different roles.
    
    Returns:
        Dictionary mapping role names to model configurations
        
    Raises:
        ValueError: If required environment variables are not set
    """
    # Define the base configurations we need
    configs = {}
    
    # Try to load common model types
    try:
        configs["default"] = get_model_config("planning")
    except ValueError:
        # If planning isn't defined, try reflection
        try:
            configs["default"] = get_model_config("reflection")
        except ValueError:
            # If neither is available, require at least one to be defined
            raise ValueError(
                "No default model configuration found. "
                "Please define either PLANNING_MODEL_PROVIDER and PLANNING_MODEL_NAME "
                "or REFLECTION_MODEL_PROVIDER and REFLECTION_MODEL_NAME in your .env file."
            )
    
    # Try to add other standard roles if they exist
    for role in ["thinking", "documentation", "reflection", "worker", "solver", "critic"]:
        try:
            configs[role] = get_model_config(role)
        except ValueError:
            # Use the default config if role-specific one isn't available
            configs[role] = configs["default"]
            logger.info(f"No configuration found for {role} model, using default.")
    
    return configs 