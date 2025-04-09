"""MCP Tool Provider implementation."""

import logging
import subprocess
import json
import sys
from typing import Dict, List, Any, Optional, Union, Tuple, IO
import tempfile
import os
import threading
import time
import atexit
import signal

from agent_patterns.core.tools.base import ToolProvider, ToolNotFoundError, ToolExecutionError


class MCPServer:
    """
    A representation of an MCP server connection.
    
    This class handles the low-level communication with an MCP server
    process, including process management, message passing, and error handling.
    """
    
    def __init__(
        self, 
        command: Union[str, List[str]], 
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        server_id: Optional[str] = None
    ):
        """
        Initialize the MCP server connection.
        
        Args:
            command: The command to run the MCP server, either as a string or list of args
            working_dir: Optional working directory for the server process
            env: Optional environment variables for the server process
            server_id: Optional unique identifier for this server
        """
        self.logger = logging.getLogger(f"MCPServer-{server_id or id(self)}")
        self.command = command
        self.working_dir = working_dir
        self.env = env or {}
        self.server_id = server_id or str(id(self))
        
        # Initialize process state
        self.process = None
        self.stdin = None
        self.stdout = None
        self.stderr = None
        
        # For caching tool list
        self._tools_cache = None
        
        # Thread for handling stderr in the background
        self.stderr_thread = None
        self.is_running = False
        
    def start(self) -> None:
        """
        Start the MCP server process.
        
        Raises:
            RuntimeError: If the process fails to start
        """
        if self.is_running:
            return
            
        try:
            # Convert command to list if it's a string
            cmd = self.command if isinstance(self.command, list) else self.command.split()
            
            # Prepare environment variables
            process_env = os.environ.copy()
            if self.env:
                process_env.update(self.env)
            
            # Start the process
            self.logger.info(f"Starting MCP server: {cmd}")
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.working_dir,
                env=process_env,
                bufsize=0,  # Unbuffered
                universal_newlines=True,  # Text mode
            )
            
            self.stdin = self.process.stdin
            self.stdout = self.process.stdout
            self.stderr = self.process.stderr
            
            # Start a thread to log stderr output
            def log_stderr():
                for line in self.stderr:
                    self.logger.debug(f"MCP server stderr: {line.strip()}")
            
            self.stderr_thread = threading.Thread(target=log_stderr, daemon=True)
            self.stderr_thread.start()
            
            # Register cleanup handler
            atexit.register(self.stop)
            
            # Mark as running
            self.is_running = True
            
            # Perform handshake to validate the server
            self._handshake()
            
        except Exception as e:
            self.logger.error(f"Failed to start MCP server: {e}")
            self.stop()  # Clean up any partial initialization
            raise RuntimeError(f"Failed to start MCP server: {e}")
    
    def stop(self) -> None:
        """Stop the MCP server process."""
        if not self.is_running:
            return
            
        try:
            # Try to gracefully terminate first
            if self.process and self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.logger.warning("MCP server did not terminate gracefully, forcing kill")
                    self.process.kill()
            
            # Clean up resources
            if self.stderr_thread and self.stderr_thread.is_alive():
                # Thread is daemon, so it will be terminated when the process exits
                pass
                
            # Unregister atexit handler to avoid double cleanup
            try:
                atexit.unregister(self.stop)
            except Exception:
                pass
                
            self.is_running = False
            self.process = None
            self.stdin = None
            self.stdout = None
            self.stderr = None
            
        except Exception as e:
            self.logger.error(f"Error stopping MCP server: {e}")
    
    def _send_message(self, message: Dict[str, Any]) -> None:
        """
        Send a message to the MCP server.
        
        Args:
            message: The message to send as a dictionary
            
        Raises:
            RuntimeError: If the message cannot be sent
        """
        if not self.is_running or not self.stdin:
            self.start()  # Try to start if not already running
            
        try:
            message_json = json.dumps(message)
            self.logger.debug(f"Sending message to MCP server: {message_json}")
            
            self.stdin.write(message_json + "\n")
            self.stdin.flush()
        except Exception as e:
            self.logger.error(f"Failed to send message to MCP server: {e}")
            self.stop()  # Server connection is likely broken
            raise RuntimeError(f"Failed to send message to MCP server: {e}")
    
    def _receive_message(self) -> Dict[str, Any]:
        """
        Receive a message from the MCP server.
        
        Returns:
            The parsed message as a dictionary
            
        Raises:
            RuntimeError: If the message cannot be received or parsed
        """
        if not self.is_running or not self.stdout:
            self.start()  # Try to start if not already running
            
        try:
            response_line = self.stdout.readline()
            if not response_line:
                # EOF reached, server likely terminated
                self.logger.error("MCP server terminated unexpectedly")
                self.stop()
                raise RuntimeError("MCP server terminated unexpectedly")
                
            self.logger.debug(f"Received message from MCP server: {response_line.strip()}")
            
            return json.loads(response_line)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse MCP server response: {e}")
            raise RuntimeError(f"Failed to parse MCP server response: {e}")
        except Exception as e:
            self.logger.error(f"Error receiving message from MCP server: {e}")
            self.stop()  # Server connection is likely broken
            raise RuntimeError(f"Error receiving message from MCP server: {e}")
    
    def _handshake(self) -> None:
        """
        Perform initial handshake with the MCP server.
        
        Raises:
            RuntimeError: If the handshake fails
        """
        try:
            # Send handshake message
            self._send_message({
                "type": "handshake",
                "version": "v1"
            })
            
            # Receive response
            response = self._receive_message()
            
            # Validate response
            if response.get("type") != "handshake_response":
                raise RuntimeError(f"Unexpected response type: {response.get('type')}")
                
            if response.get("status") != "success":
                raise RuntimeError(f"Handshake failed: {response.get('error')}")
                
            self.logger.info(f"Handshake successful with MCP server version {response.get('version')}")
            
        except Exception as e:
            self.logger.error(f"Handshake failed: {e}")
            self.stop()
            raise RuntimeError(f"Handshake failed: {e}")
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the MCP server.
        
        Returns:
            A list of tool specifications
            
        Raises:
            RuntimeError: If the tools cannot be listed
        """
        if self._tools_cache is not None:
            return self._tools_cache
            
        try:
            # Send list_tools message
            self._send_message({
                "type": "list_tools"
            })
            
            # Receive response
            response = self._receive_message()
            
            # Validate response
            if response.get("type") != "list_tools_response":
                raise RuntimeError(f"Unexpected response type: {response.get('type')}")
                
            if response.get("status") != "success":
                raise RuntimeError(f"Failed to list tools: {response.get('error')}")
                
            tools = response.get("tools", [])
            self.logger.info(f"Listed {len(tools)} tools from MCP server")
            
            # Cache the results
            self._tools_cache = tools
            return tools
            
        except Exception as e:
            self.logger.error(f"Failed to list tools: {e}")
            raise RuntimeError(f"Failed to list tools: {e}")
    
    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: The name of the tool to call
            params: The parameters to pass to the tool
            
        Returns:
            The result of the tool call
            
        Raises:
            ToolNotFoundError: If the tool doesn't exist
            ToolExecutionError: If the tool execution fails
        """
        try:
            # Send call_tool message
            self._send_message({
                "type": "call_tool",
                "tool": tool_name,
                "params": params
            })
            
            # Receive response
            response = self._receive_message()
            
            # Validate response
            if response.get("type") != "call_tool_response":
                raise RuntimeError(f"Unexpected response type: {response.get('type')}")
                
            if response.get("status") == "error":
                error_type = response.get("error_type", "")
                error_message = response.get("error", "Unknown error")
                
                if error_type == "tool_not_found":
                    raise ToolNotFoundError(f"Tool '{tool_name}' not found: {error_message}")
                else:
                    raise ToolExecutionError(f"Tool execution failed: {error_message}")
                    
            return response.get("result")
            
        except (ToolNotFoundError, ToolExecutionError):
            # Re-raise specific exceptions
            raise
        except Exception as e:
            self.logger.error(f"Error calling tool {tool_name}: {e}")
            raise ToolExecutionError(f"Error calling tool {tool_name}: {e}")


class MCPToolProvider(ToolProvider):
    """MCP-based implementation of the ToolProvider interface."""
    
    def __init__(self, mcp_servers: List[MCPServer], cache_tools: bool = True):
        """
        Initialize with a list of MCP server connections.
        
        Args:
            mcp_servers: List of MCP server connections
            cache_tools: Whether to cache tool definitions (recommended for performance)
        """
        self.mcp_servers = mcp_servers
        self.cache_tools = cache_tools
        self._tools_cache = None if not cache_tools else {}
        self.logger = logging.getLogger("MCPToolProvider")
    
    def list_tools(self) -> List[Dict]:
        """Get tools from all connected MCP servers."""
        if self.cache_tools and self._tools_cache is not None:
            return self._tools_cache
        
        tools = []
        for server in self.mcp_servers:
            try:
                server_tools = server.list_tools()
                tools.extend(server_tools)
            except Exception as e:
                self.logger.warning(f"Failed to list tools from server {server.server_id}: {e}")
        
        if self.cache_tools:
            self._tools_cache = tools
        
        return tools
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Find the right MCP server and execute the tool."""
        for server in self.mcp_servers:
            try:
                # Check if this server has the requested tool
                tools = server.list_tools()
                if any(tool["name"] == tool_name for tool in tools):
                    return server.call_tool(tool_name, params)
            except ToolNotFoundError:
                # This server doesn't have the tool, try the next one
                continue
            except Exception as e:
                # Log other errors but keep trying other servers
                self.logger.warning(f"Error executing tool {tool_name} on server {server.server_id}: {e}")
        
        # If we get here, no server had the tool or all attempts failed
        raise ToolNotFoundError(f"Tool '{tool_name}' not found in any MCP server")
    
    def invalidate_cache(self):
        """Invalidate the tools cache to force a refresh on next list_tools call."""
        self._tools_cache = None


def create_mcp_server_connection(server_type: str, config: Dict[str, Any]) -> MCPServer:
    """
    Create a connection to an MCP server.
    
    Args:
        server_type: The type of connection (stdio, sse, socket, etc.)
        config: Configuration for the connection
        
    Returns:
        An MCP server connection object
        
    Raises:
        ValueError: If the server type is unknown
    """
    if server_type == "stdio":
        return _create_stdio_connection(config)
    else:
        raise ValueError(f"Unknown MCP server type: {server_type}")


def _create_stdio_connection(config: Dict[str, Any]) -> MCPServer:
    """
    Create a stdio-based MCP server connection.
    
    Args:
        config: Configuration for the connection, including:
               - command: The command to run the server
               - working_dir: Optional working directory
               - env: Optional environment variables
               
    Returns:
        An MCPServer instance
    """
    command = config.get("command")
    working_dir = config.get("working_dir")
    env = config.get("env")
    server_id = config.get("id")
    
    if not command:
        raise ValueError("Missing required 'command' configuration")
    
    return MCPServer(
        command=command,
        working_dir=working_dir,
        env=env,
        server_id=server_id
    ) 