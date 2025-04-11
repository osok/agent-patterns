# Core API Reference

This document provides detailed API reference for the core components of Agent Patterns.

## BaseAgent

::: agent_patterns.core.base_agent.BaseAgent
    handler: python
    selection:
      members:
        - __init__
        - build_graph
        - run
        - process_response
        - save_to_memory
        - retrieve_from_memory
        - _call_llm
        - _get_prompt

## Memory System

### BaseMemory

::: agent_patterns.core.memory.base.BaseMemory
    handler: python
    selection:
      members:
        - __init__
        - save
        - retrieve
        - update
        - delete

### SemanticMemory

::: agent_patterns.core.memory.semantic.SemanticMemory
    handler: python
    selection:
      members:
        - __init__
        - save
        - retrieve
        - update
        - delete

### EpisodicMemory

::: agent_patterns.core.memory.episodic.EpisodicMemory
    handler: python
    selection:
      members:
        - __init__
        - save
        - retrieve
        - update
        - delete

### CompositeMemory

::: agent_patterns.core.memory.composite.CompositeMemory
    handler: python
    selection:
      members:
        - __init__
        - add_memory
        - save_to
        - retrieve_from
        - update_in
        - delete_from

## Persistence

### BasePersistence

::: agent_patterns.core.memory.persistence.base.BasePersistence
    handler: python
    selection:
      members:
        - __init__
        - initialize
        - save
        - retrieve
        - update
        - delete
        - close

### InMemoryPersistence

::: agent_patterns.core.memory.persistence.in_memory.InMemoryPersistence
    handler: python
    selection:
      members:
        - __init__
        - initialize
        - save
        - retrieve
        - update
        - delete
        - close

### FilePersistence

::: agent_patterns.core.memory.persistence.file.FilePersistence
    handler: python
    selection:
      members:
        - __init__
        - initialize
        - save
        - retrieve
        - update
        - delete
        - close

## Tool System

### BaseToolProvider

::: agent_patterns.core.tools.base.BaseToolProvider
    handler: python
    selection:
      members:
        - __init__
        - get_tools
        - execute_tool
        - get_tool

### Tool

::: agent_patterns.core.tools.base.Tool
    handler: python
    selection:
      members:
        - __init__
        - to_dict
        - get_schema

### CompositeToolProvider

::: agent_patterns.core.tools.providers.composite_provider.CompositeToolProvider
    handler: python
    selection:
      members:
        - __init__
        - get_tools
        - execute_tool
        - get_tool

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

## Utility Functions

### create_mcp_server_connection

::: agent_patterns.core.tools.providers.mcp_provider.create_mcp_server_connection
    handler: python

### format_prompt

::: agent_patterns.core.utils.prompts.format_prompt
    handler: python