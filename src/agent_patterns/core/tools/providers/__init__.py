"""Tool providers for agent-patterns library."""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



# Re-export key providers for easier imports
from agent_patterns.core.tools.providers.mcp_provider import MCPToolProvider 