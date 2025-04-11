# Memory API Reference

This document provides detailed API reference for the memory system in Agent Patterns.

## Memory Components

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
        - _calculate_embedding
        - _get_timestamp

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
        - retrieve_conversation
        - _get_timestamp

### ProceduralMemory

::: agent_patterns.core.memory.procedural.ProceduralMemory
    handler: python
    selection:
      members:
        - __init__
        - save
        - retrieve
        - update
        - delete
        - retrieve_procedures
        - _get_timestamp

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
        - get_component
        - list_components

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
        - _filter_by_query

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
        - _get_namespace_dir
        - _ensure_namespace_dir

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
        - _calculate_embedding

