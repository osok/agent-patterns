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

### Persistence Providers

The memory system includes several persistence providers for storing memory data.

### InMemoryPersistence

::: agent_patterns.core.memory.persistence.InMemoryPersistence
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

### FileSystemPersistence

::: agent_patterns.core.memory.persistence.FileSystemPersistence
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

### VectorStorePersistence

::: agent_patterns.core.memory.persistence.VectorStorePersistence
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

## Utility Functions

### create_mcp_server_connection

::: agent_patterns.core.tools.providers.mcp_provider.create_mcp_server_connection
    handler: python

