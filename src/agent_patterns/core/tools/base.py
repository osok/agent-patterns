"""Base interfaces for tool providers in agent-patterns library."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class ToolExecutionError(Exception):
    """Exception raised when a tool execution fails."""
    pass


class ToolNotFoundError(Exception):
    """Exception raised when a requested tool doesn't exist."""
    pass


class ToolProvider(ABC):
    """Abstract interface for tool providers.
    
    A ToolProvider is responsible for providing a list of available tools
    and executing those tools. This abstraction allows agents to interact
    with tools without knowing the specifics of how they are implemented.
    """
    
    @abstractmethod
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools with their metadata.
        
        Returns:
            A list of tool specifications, each containing at minimum:
            - name: The tool's name
            - description: What the tool does
            - parameters: The expected input parameters
        """
        pass
    
    @abstractmethod
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        Execute a tool with the given parameters.
        
        Args:
            tool_name: The name of the tool to execute
            params: The parameters to pass to the tool
            
        Returns:
            The result of the tool execution
            
        Raises:
            ToolNotFoundError: If the tool doesn't exist
            ToolExecutionError: If the tool execution fails
        """
        pass 