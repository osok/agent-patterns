# Tools API Reference

This document provides detailed API reference for the tools system in Agent Patterns.

## Core Components

### ToolProvider

::: agent_patterns.core.tools.base.ToolProvider
    handler: python
    selection:
      members:
        - __init__
        - list_tools
        - execute_tool

### Tool Errors

::: agent_patterns.core.tools.base.ToolNotFoundError
    handler: python

::: agent_patterns.core.tools.base.ToolExecutionError
    handler: python

## Tool Providers



### MCPToolProvider

::: agent_patterns.core.tools.providers.mcp_provider.MCPToolProvider
    handler: python
    selection:
      members:
        - __init__
        - list_tools
        - execute_tool
        - start_servers
        - stop_servers



## MCP Integration

### MCPServer

::: agent_patterns.core.tools.providers.mcp_provider.MCPServer
    handler: python
    selection:
      members:
        - __init__
        - start
        - stop
        - list_tools
        - call_tool

### create_mcp_server_connection

::: agent_patterns.core.tools.providers.mcp_provider.create_mcp_server_connection
    handler: python

