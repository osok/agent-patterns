"""
Utilities for agent-patterns examples.

This package provides common utilities for examples in the agent-patterns library.
"""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



from examples.utils.model_config import get_model_config, get_llm_configs

__all__ = ["get_model_config", "get_llm_configs"] 