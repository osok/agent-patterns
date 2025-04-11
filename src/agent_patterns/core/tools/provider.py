"""Tool provider for agent patterns.

This module provides a ToolProvider implementation for agent patterns.
"""

from typing import Dict, List, Any, Optional
from agent_patterns.core.tools.base import ToolProvider, ToolNotFoundError


class DefaultToolProvider(ToolProvider):
    """Default implementation of a tool provider.
    
    This class implements the ToolProvider interface to provide tool management
    and execution capabilities.
    """
    
    def __init__(self, tools: List[Dict[str, Any]] = None):
        """Initialize the tool provider with an optional list of tools.
        
        Args:
            tools: Optional list of tool specifications to register
        """
        self.tools = tools or []
        self.tool_map = {tool["name"]: tool for tool in self.tools}
    
    def add_tool(self, tool: Dict[str, Any]) -> None:
        """Add a tool to the provider.
        
        Args:
            tool: The tool specification to add
        """
        self.tools.append(tool)
        self.tool_map[tool["name"]] = tool
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools with their metadata.
        
        Returns:
            A list of tool specifications
        """
        return self.tools
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a tool with the given parameters.
        
        Args:
            tool_name: The name of the tool to execute
            params: The parameters to pass to the tool
            
        Returns:
            The result of the tool execution
            
        Raises:
            ToolNotFoundError: If the tool doesn't exist
        """
        if tool_name not in self.tool_map:
            raise ToolNotFoundError(f"Tool '{tool_name}' not found")
        
        tool = self.tool_map[tool_name]
        if "function" in tool:
            return tool["function"](**params)
        else:
            raise NotImplementedError(f"Execution for tool '{tool_name}' is not implemented")