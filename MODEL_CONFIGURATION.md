# Model Configuration Guide

This document provides guidelines for maintaining consistent model configuration across all examples in the codebase. All examples must use environment variables from `.env` to determine which LLM source and model to use, rather than hardcoded values.

## Configuration Strategy

### 1. Environment Variables

The model provider and name for different roles should be defined in the `.env` file with the following naming convention:

```
ROLE_MODEL_PROVIDER=provider_name
ROLE_MODEL_NAME=model_name
```

For example:
```
THINKING_MODEL_PROVIDER=openai
THINKING_MODEL_NAME=gpt-4-turbo
PLANNING_MODEL_PROVIDER=anthropic
PLANNING_MODEL_NAME=claude-3-opus
```

### 2. Using the Model Configuration Utility

All examples should use the `get_llm_configs()` function from `examples/utils/model_config.py` to load model configurations. This utility provides a standardized way to access model configurations across all examples.

```python
from examples.utils.model_config import get_llm_configs

# Load LLM configs from environment variables
llm_configs = get_llm_configs()
```

The `get_llm_configs()` function returns a dictionary with configurations for different model roles (thinking, planning, reflection, etc.) based on the environment variables. If a specific role configuration is not found, it falls back to the default configuration.

### 3. Required Environment Variables

At minimum, your `.env` file should define one of these two sets of variables:

```
PLANNING_MODEL_PROVIDER=provider
PLANNING_MODEL_NAME=model_name
```

OR

```
REFLECTION_MODEL_PROVIDER=provider
REFLECTION_MODEL_NAME=model_name
```

These will be used as default configurations if specific role configurations are not available.

## Implementing in Your Examples

### Basic Implementation

```python
import os
from dotenv import load_dotenv
import sys

# Add parent directory to path to import from examples.utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from examples.utils.model_config import get_llm_configs

# Load environment variables
load_dotenv()

# Get model configurations
try:
    llm_configs = get_llm_configs()
except ValueError as e:
    print(f"Error loading model configuration: {e}")
    print("Please ensure your .env file contains the necessary model configuration variables.")
    exit(1)

# Initialize your agent with the loaded configurations
agent = YourAgent(llm_configs=llm_configs, ...)
```

### Advanced Implementation (With Role-Specific Models)

For examples that need different models for specific roles (like Reflexion agent), you can still use the utility function to get a consistent configuration:

```python
# The get_llm_configs() function will return a dictionary like:
llm_configs = {
    "default": {"provider": "openai", "model_name": "gpt-4-turbo"},
    "thinking": {"provider": "openai", "model_name": "gpt-4-turbo"},
    "reflection": {"provider": "anthropic", "model_name": "claude-3"},
    "worker": {"provider": "openai", "model_name": "gpt-4-turbo"},
    "solver": {"provider": "openai", "model_name": "gpt-3.5-turbo"},
    "critic": {"provider": "anthropic", "model_name": "claude-3"}
}

# Then you can use these configurations for different agent roles
agent = MultiRoleAgent(
    planner_config=llm_configs["thinking"],
    executor_config=llm_configs["worker"],
    evaluator_config=llm_configs["critic"],
    ...
)
```

## Testing Your Configuration

You can run the `check_model_config.py` script to identify examples that need to be updated:

```
python check_model_config.py
```

This script analyzes all example files to check if they properly use environment variables for model configuration and identifies those that still contain hardcoded model names.

## Additional Resources

- See `examples/reflexion/simple_example.py` for a good example of how to implement proper model configuration.
- The `.env.example` file shows the standard environment variables that should be defined. 