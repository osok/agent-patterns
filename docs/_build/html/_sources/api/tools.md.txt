# Tools API Reference

This document provides detailed API reference for the tools system in Agent Patterns.

## Core Components

### BaseToolProvider

::: agent_patterns.core.tools.base.BaseToolProvider
    handler: python
    selection:
      members:
        - __init__
        - get_tools
        - execute_tool
        - get_tool
        - list_tools

### Tool

::: agent_patterns.core.tools.base.Tool
    handler: python
    selection:
      members:
        - __init__
        - to_dict
        - get_schema
        - validate_params

## Tool Providers

### CompositeToolProvider

::: agent_patterns.core.tools.providers.composite_provider.CompositeToolProvider
    handler: python
    selection:
      members:
        - __init__
        - get_tools
        - execute_tool
        - get_tool
        - add_provider
        - remove_provider

### MCPToolProvider

::: agent_patterns.core.tools.providers.mcp_provider.MCPToolProvider
    handler: python
    selection:
      members:
        - __init__
        - get_tools
        - execute_tool
        - get_tool
        - start_servers
        - stop_servers
        - add_server
        - remove_server

### SearchToolProvider

::: agent_patterns.core.tools.providers.search_provider.SearchToolProvider
    handler: python
    selection:
      members:
        - __init__
        - get_tools
        - search
        - search_news

### FileToolProvider

::: agent_patterns.core.tools.providers.file_provider.FileToolProvider
    handler: python
    selection:
      members:
        - __init__
        - get_tools
        - read_file
        - write_file
        - list_directory
        - create_directory
        - delete_file

### WikipediaToolProvider

::: agent_patterns.core.tools.providers.wikipedia_provider.WikipediaToolProvider
    handler: python
    selection:
      members:
        - __init__
        - get_tools
        - search_wikipedia
        - get_wikipedia_page

### WebToolProvider

::: agent_patterns.core.tools.providers.web_provider.WebToolProvider
    handler: python
    selection:
      members:
        - __init__
        - get_tools
        - browse_url
        - extract_links
        - extract_text

## MCP Integration

### MCPServer

::: agent_patterns.core.tools.providers.mcp_provider.MCPServer
    handler: python
    selection:
      members:
        - __init__
        - start
        - stop
        - send_request
        - get_tools
        - is_running

### create_mcp_server_connection

::: agent_patterns.core.tools.providers.mcp_provider.create_mcp_server_connection
    handler: python

### MCPWebServer

::: agent_patterns.core.tools.providers.mcp_provider.MCPWebServer
    handler: python
    selection:
      members:
        - __init__
        - start
        - stop
        - send_request
        - get_tools

### MCPStdioServer

::: agent_patterns.core.tools.providers.mcp_provider.MCPStdioServer
    handler: python
    selection:
      members:
        - __init__
        - start
        - stop
        - send_request
        - get_tools

## Tool Utilities

### ToolValidator

::: agent_patterns.core.tools.utils.validator.ToolValidator
    handler: python
    selection:
      members:
        - validate_schema
        - validate_parameters
        - validate_result

### ToolFormatter

::: agent_patterns.core.tools.utils.formatter.ToolFormatter
    handler: python
    selection:
      members:
        - format_tool
        - format_tools
        - format_result

### ToolParser

::: agent_patterns.core.tools.utils.parser.ToolParser
    handler: python
    selection:
      members:
        - parse_tool_call
        - parse_tool_calls
        - extract_tool_name
        - extract_parameters