# Memory System API Documentation

This document provides detailed information about the memory system implementation in the agent-patterns library.

## Overview

The agent-patterns memory system provides agents with the ability to store and retrieve information across interactions. This capability is crucial for maintaining context, learning from past interactions, and providing personalized responses.

The memory system is designed to be:

- **Modular**: Different memory types can be used independently or together
- **Flexible**: Customizable retrieval and storage strategies
- **Extensible**: Easy to add new memory types or persistence backends
- **Optional**: Can be enabled or disabled as needed

## Memory Types

The memory system includes three primary types of memory, inspired by cognitive science:

### 1. Semantic Memory

Semantic memory stores factual knowledge, concepts, and relationships in a structured format. This type of memory is ideal for:

- Storing user preferences and attributes
- Recording facts and knowledge
- Maintaining entity relationships

```python
from agent_patterns.core.memory import SemanticMemory
from agent_patterns.core.memory.persistence import InMemoryPersistence

# Initialize the persistence layer
persistence = InMemoryPersistence()
asyncio.run(persistence.initialize())

# Create semantic memory
semantic_memory = SemanticMemory(
    persistence=persistence,
    namespace="user_semantic"  # Namespace for organization
)

# Store information
asyncio.run(semantic_memory.save({
    "entity": "user",
    "attribute": "name",
    "value": "Alice"
}))

# Retrieve information (returns list of matching items)
user_info = asyncio.run(semantic_memory.retrieve("user"))
```

### 2. Episodic Memory

Episodic memory stores sequences of events, interactions, and experiences. This memory type is useful for:

- Remembering conversation history
- Learning from past interactions
- Providing contextual continuity

```python
from agent_patterns.core.memory import EpisodicMemory
from agent_patterns.core.memory.persistence import InMemoryPersistence

# Initialize the persistence layer
persistence = InMemoryPersistence()
asyncio.run(persistence.initialize())

# Create episodic memory
episodic_memory = EpisodicMemory(
    persistence=persistence,
    namespace="conversation_history"
)

# Store an experience
asyncio.run(episodic_memory.save({
    "content": "User asked about climate change solutions",
    "importance": 0.8,  # Optional importance score
    "tags": ["climate", "question"]  # Optional tags for retrieval
}))

# Retrieve relevant memories
climate_memories = asyncio.run(episodic_memory.retrieve("climate change", limit=5))
```

### 3. Procedural Memory

Procedural memory stores patterns, workflows, and templates that guide the agent's behavior. This is useful for:

- Storing reasoning patterns
- Defining behavior templates
- Creating dynamic system prompts

```python
from agent_patterns.core.memory import ProceduralMemory
from agent_patterns.core.memory.persistence import InMemoryPersistence

# Initialize the persistence layer
persistence = InMemoryPersistence()
asyncio.run(persistence.initialize())

# Create procedural memory
procedural_memory = ProceduralMemory(
    persistence=persistence,
    namespace="reasoning_patterns"
)

# Store a reasoning pattern
asyncio.run(procedural_memory.save({
    "name": "explain_concept",
    "pattern": {
        "template": """When explaining {concept}, follow these steps:
1. Start with a simple analogy
2. Define key terms
3. Provide concrete examples
4. Address common misconceptions
5. Summarize the main points"""
    },
    "description": "Template for explaining complex concepts",
    "tags": ["explanation", "teaching"]
}))

# Retrieve relevant patterns
explanation_patterns = asyncio.run(procedural_memory.retrieve("explanation", limit=3))
```

### Composite Memory

The `CompositeMemory` class combines multiple memory types into a unified interface, making it easy to work with different memory types together:

```python
from agent_patterns.core.memory import CompositeMemory, SemanticMemory, EpisodicMemory
from agent_patterns.core.memory.persistence import InMemoryPersistence

# Initialize the persistence layer
persistence = InMemoryPersistence()
asyncio.run(persistence.initialize())

# Create individual memory types
semantic_memory = SemanticMemory(persistence, "semantic")
episodic_memory = EpisodicMemory(persistence, "episodic")

# Create composite memory
memory = CompositeMemory({
    "semantic": semantic_memory,
    "episodic": episodic_memory
})

# Save to a specific memory type
asyncio.run(memory.save_to("semantic", {"entity": "user", "attribute": "name", "value": "Alice"}))

# Retrieve from a specific memory type
user_info = asyncio.run(memory.retrieve_from("semantic", "user", limit=5))

# Retrieve from all memory types
all_memories = asyncio.run(memory.retrieve_all("query", limits={"semantic": 3, "episodic": 2}))
```

## Persistence Backends

The memory system supports multiple persistence backends through the `MemoryPersistence` interface:

### InMemoryPersistence

Stores memories in memory (non-persistent, useful for testing and development):

```python
from agent_patterns.core.memory.persistence import InMemoryPersistence

# Initialize in-memory storage
persistence = InMemoryPersistence()
asyncio.run(persistence.initialize())
```

### FileSystemPersistence

Stores memories on disk for persistence between runs:

```python
from agent_patterns.core.memory.persistence import FileSystemPersistence

# Initialize file system storage
persistence = FileSystemPersistence(directory="./memory_data")
asyncio.run(persistence.initialize())
```

### VectorStorePersistence

Stores memories in a vector database for semantic search capabilities:

```python
from agent_patterns.core.memory.persistence import VectorStorePersistence
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# Initialize the embedding function
embedding_function = OpenAIEmbeddings()

# Initialize vector store
vector_store = Chroma(
    collection_name="agent_memory",
    embedding_function=embedding_function,
    persist_directory="./chroma_db"
)

# Initialize vector store persistence
persistence = VectorStorePersistence(
    vector_store=vector_store,
    embedding_function=embedding_function
)
asyncio.run(persistence.initialize())
```

## Integration with Agents

All agent patterns in the library support memory integration through the `BaseAgent` class:

```python
from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.memory import CompositeMemory, SemanticMemory, EpisodicMemory
from agent_patterns.core.memory.persistence import InMemoryPersistence

# Set up memory
persistence = InMemoryPersistence()
asyncio.run(persistence.initialize())

semantic_memory = SemanticMemory(persistence, "semantic")
episodic_memory = EpisodicMemory(persistence, "episodic")

memory = CompositeMemory({
    "semantic": semantic_memory,
    "episodic": episodic_memory
})

# Create agent with memory
agent = ReActAgent(
    llm_configs={"default": {"provider": "openai", "model_name": "gpt-4o"}},
    memory=memory,
    memory_config={
        "semantic": True,  # Enable semantic memory
        "episodic": True,   # Enable episodic memory
        "procedural": False # Disable procedural memory
    }
)

# The agent will now automatically retrieve and save memories during its operation
result = agent.run("What's the weather in New York?")
```

## Advanced Usage

### Custom Memory Types

You can create custom memory types by extending the `BaseMemory` class:

```python
from agent_patterns.core.memory.base import BaseMemory
from agent_patterns.core.memory.persistence import MemoryPersistence
from typing import Dict, List, Any, Optional
import uuid

class CustomMemory(BaseMemory[Dict[str, Any]]):
    """Custom memory implementation."""
    
    def __init__(self, 
                 persistence: MemoryPersistence,
                 namespace: str = "custom",
                 config: Optional[Dict] = None):
        self.persistence = persistence
        self.namespace = namespace
        self.config = config or {}
    
    async def save(self, item: Dict[str, Any], **metadata) -> str:
        """Save an item to memory."""
        memory_id = f"custom_{uuid.uuid4().hex}"
        
        # Process the item if needed
        processed_item = self._process_item(item)
        
        # Store in persistence layer
        await self.persistence.store(
            self.namespace,
            memory_id,
            processed_item,
            metadata
        )
        
        return memory_id
    
    async def retrieve(self, query: Any, limit: int = 5, **filters) -> List[Dict[str, Any]]:
        """Retrieve items from memory."""
        # Process query if needed
        processed_query = self._process_query(query)
        
        # Search in persistence layer
        results = await self.persistence.search(
            self.namespace,
            processed_query,
            limit,
            **filters
        )
        
        return [item["value"] for item in results]
    
    async def update(self, id: str, item: Dict[str, Any], **metadata) -> bool:
        """Update an existing memory item."""
        existing = await self.persistence.retrieve(self.namespace, id)
        if not existing:
            return False
        
        # Process the update
        processed_item = self._process_update(existing, item)
        
        # Store updated value
        await self.persistence.store(
            self.namespace,
            id,
            processed_item,
            metadata
        )
        
        return True
    
    async def delete(self, id: str) -> bool:
        """Delete a memory item."""
        return await self.persistence.delete(self.namespace, id)
    
    async def clear(self) -> None:
        """Clear all memory items."""
        await self.persistence.clear_namespace(self.namespace)
    
    def _process_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Process an item before saving."""
        # Implement custom processing logic
        return item
    
    def _process_query(self, query: Any) -> Any:
        """Process a query before retrieval."""
        # Implement custom query processing
        return query
    
    def _process_update(self, existing: Dict, update: Dict) -> Dict:
        """Process an update."""
        # Implement custom update logic
        return {**existing, **update}
```

### Custom Persistence Backends

You can create custom persistence backends by implementing the `MemoryPersistence` interface:

```python
from agent_patterns.core.memory.persistence import MemoryPersistence
from typing import Dict, List, Any, Optional

class CustomPersistence(MemoryPersistence):
    """Custom persistence implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
    
    async def initialize(self) -> None:
        """Initialize the persistence layer."""
        # Set up connection to your storage backend
        self.client = YourStorageClient(self.config)
        await self.client.connect()
    
    async def store(self, namespace: str, key: str, value: Any, metadata: Dict = None) -> None:
        """Store a value with an associated key."""
        metadata = metadata or {}
        # Implement storage logic
        await self.client.store(namespace, key, value, metadata)
    
    async def retrieve(self, namespace: str, key: str) -> Optional[Any]:
        """Retrieve a value by key."""
        # Implement retrieval logic
        return await self.client.get(namespace, key)
    
    async def search(self, namespace: str, query: Any, limit: int = 10, **filters) -> List[Dict]:
        """Search for values matching a query."""
        # Implement search logic
        results = await self.client.search(namespace, query, limit, filters)
        return [
            {"id": item.id, "value": item.value, "metadata": item.metadata, "score": item.score}
            for item in results
        ]
    
    async def delete(self, namespace: str, key: str) -> bool:
        """Delete a value by key."""
        # Implement deletion logic
        return await self.client.delete(namespace, key)
    
    async def clear_namespace(self, namespace: str) -> None:
        """Clear all data in a namespace."""
        # Implement namespace clearing
        await self.client.clear(namespace)
```

## Synchronous Usage

While the memory API is primarily asynchronous, the agent patterns provide synchronous convenience methods for working with memory:

```python
# In an agent class
def sync_retrieve_memories(self, query: str) -> Dict[str, List[Any]]:
    """Synchronous wrapper for memory retrieval."""
    if not self.memory:
        return {}
        
    return asyncio.run(self._retrieve_memories(query))

def sync_save_memory(self, memory_type: str, item: Any, **metadata) -> Optional[str]:
    """Synchronous wrapper for memory saving."""
    if not self.memory or not self.memory_config.get(memory_type, False):
        return None
        
    return asyncio.run(self.memory.save_to(memory_type, item, **metadata))
```

## Best Practices

1. **Memory Organization**:
   - Use namespaces to organize different types of data
   - Use consistent schemas for similar types of information
   - Add metadata to improve retrieval accuracy

2. **Retrieval Optimization**:
   - Be specific with queries to get the most relevant results
   - Set appropriate limits to avoid overwhelming the model
   - Use filters to narrow down results when possible

3. **Memory Management**:
   - Implement regular pruning of less relevant memories
   - Consider the importance score when retrieving memories
   - Use tags consistently to improve retrieval

4. **Integration with Agents**:
   - Retrieve memories at the beginning of agent workflows
   - Save important information after completing tasks
   - Use memory-aware prompts to incorporate retrieved information

## Conclusion

The memory system provides powerful capabilities for building agents with persistent knowledge and contextual awareness. By integrating memory into your agents, you can create more personalized, consistent, and intelligent experiences.

For detailed examples, see the `examples/memory_example.py` and `examples/combined_memory_tools_example.py` files in the repository.