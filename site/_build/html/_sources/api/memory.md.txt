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
        - _filter_by_query

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
        - _get_namespace_dir
        - _ensure_namespace_dir

### VectorDBPersistence

::: agent_patterns.core.memory.persistence.vector_db.VectorDBPersistence
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

## Memory Utilities

### MemoryFormatter

::: agent_patterns.core.memory.utils.formatter.MemoryFormatter
    handler: python
    selection:
      members:
        - format_memory
        - format_semantic_memory
        - format_episodic_memory
        - format_procedural_memory
        - format_composite_memory

### MemoryEncoder

::: agent_patterns.core.memory.utils.encoder.MemoryEncoder
    handler: python
    selection:
      members:
        - encode_memory
        - decode_memory
        - calculate_embedding

### MemoryRetriever

::: agent_patterns.core.memory.utils.retriever.MemoryRetriever
    handler: python
    selection:
      members:
        - retrieve_relevant
        - retrieve_recent
        - retrieve_by_tag
        - combine_retrievals