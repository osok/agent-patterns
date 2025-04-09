"""Registry for tool providers in agent-patterns library."""

from typing import Dict, List, Any, Optional
from agent_patterns.core.tools.base import ToolProvider, ToolNotFoundError, ToolExecutionError


class ToolRegistry:
    """
    A registry for managing and executing tools from multiple providers.
    
    This class maintains a collection of ToolProviders and provides a unified
    interface for accessing and executing tools from any registered provider.
    """
    
    def __init__(self, providers: Optional[List[ToolProvider]] = None):
        """
        Initialize the tool registry.
        
        Args:
            providers: An optional list of ToolProviders to register initially.
        """
        self._providers = providers or []
        self._tools_cache = None
    
    def register_provider(self, provider: ToolProvider) -> None:
        """
        Register a new tool provider.
        
        Args:
            provider: The ToolProvider to register.
        """
        self._providers.append(provider)
        # Invalidate cache when providers change
        self._tools_cache = None
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools from all registered providers.
        
        Returns:
            A list of tool specifications from all providers.
        """
        if self._tools_cache is not None:
            return self._tools_cache
        
        all_tools = []
        for provider in self._providers:
            all_tools.extend(provider.list_tools())
        
        # Cache the results for future calls
        self._tools_cache = all_tools
        return all_tools
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        Execute a tool with the given parameters.
        
        Attempts to find the tool in any registered provider and execute it.
        
        Args:
            tool_name: The name of the tool to execute.
            params: The parameters to pass to the tool.
            
        Returns:
            The result of the tool execution.
            
        Raises:
            ToolNotFoundError: If the tool isn't found in any provider.
            ToolExecutionError: If the tool execution fails.
        """
        # Check each provider for the tool
        for provider in self._providers:
            try:
                return provider.execute_tool(tool_name, params)
            except ToolNotFoundError:
                # This provider doesn't have the tool, try the next one
                continue
            except ToolExecutionError as e:
                # If a provider has the tool but execution fails, don't try others
                raise e
        
        # If we get here, no provider has the tool
        raise ToolNotFoundError(f"Tool '{tool_name}' not found in any registered provider")
    
    def invalidate_cache(self) -> None:
        """
        Invalidate the tools cache to force a refresh on next call to list_tools.
        """
        self._tools_cache = None 