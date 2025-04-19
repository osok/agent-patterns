# **Agent Memory Systems Integration Design for Agent-Patterns**

**Version:** 1.0  
 **Date:** April 10, 2025  
 **Author:** Agent-Patterns Team

---

## **1\. Overview**

This design document outlines the integration of comprehensive memory systems into the agent-patterns library. Memory is crucial for agents to maintain context across interactions, learn from experience, and provide personalized responses. Our implementation will support multiple memory types based on recent research in the field, with the flexibility to enable or disable specific memory capabilities as needed.

IMPORTANT NOTE: UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC anything as long as we are using Python.

## **2\. Design Goals**

1. **Modularity**: Support various memory types that can be combined or used independently  
2. **Persistence**: Allow memories to be stored across sessions and conversations  
3. **Configurability**: Let developers toggle specific memory types on/off  
4. **Scalability**: Support efficient retrieval as memory stores grow  
5. **Extensibility**: Enable easy addition of new memory types in the future

## **3\. Memory Types**

Based on cognitive science and AI research, we'll implement three primary memory types:

### **3.1. Semantic Memory**

* **Purpose**: Store factual knowledge, concepts, and relationships  
* **Usage**: Personalization, domain knowledge, preferences  
* **Implementation**: Vector store \+ structured key-value pairs

### **3.2. Episodic Memory**

* **Purpose**: Store sequences of past events and interactions  
* **Usage**: Few-shot examples, learning from experience  
* **Implementation**: Vector store with temporal metadata

### **3.3. Procedural Memory**

* **Purpose**: Store learned behaviors and action patterns  
* **Usage**: Dynamic system prompts, evolving behaviors  
* **Implementation**: Updatable prompt templates \+ action sequences

## **4\. Architecture**

### **4.1 Core Components**

agent\_patterns/  
├── core/  
│   ├── memory/  
│   │   ├── \_\_init\_\_.py  
│   │   ├── base.py              \# Base memory interfaces  
│   │   ├── semantic.py          \# Semantic memory implementation  
│   │   ├── episodic.py          \# Episodic memory implementation  
│   │   ├── procedural.py        \# Procedural memory implementation  
│   │   ├── composite.py         \# Composite memory (combines multiple types)  
│   │   └── persistence/         \# Storage backends  
│   │       ├── \_\_init\_\_.py  
│   │       ├── in\_memory.py     \# Non-persistent (for testing)  
│   │       ├── file\_system.py   \# Local file storage  
│   │       ├── vector\_store.py  \# Vector DB integration  
│   │       └── redis.py         \# Redis integration  
│   └── ...  
└── ...

### **4.2 Key Interfaces**

#### **BaseMemory (Abstract Base Class)**

from abc import ABC, abstractmethod  
from typing import Dict, List, Any, Optional, TypeVar, Generic

T \= TypeVar('T')  \# Memory item type

class BaseMemory(Generic\[T\], ABC):  
    """Base interface for all memory types."""  
      
    @abstractmethod  
    def save(self, item: T, \*\*metadata) \-\> str:  
        """  
        Save an item to memory.  
          
        Args:  
            item: The item to save  
            \*\*metadata: Additional metadata for storage  
              
        Returns:  
            A unique identifier for the saved item  
        """  
        pass  
      
    @abstractmethod  
    def retrieve(self, query: Any, limit: int \= 5, \*\*filters) \-\> List\[T\]:  
        """  
        Retrieve items from memory based on a query.  
          
        Args:  
            query: The query to match against  
            limit: Maximum number of items to return  
            \*\*filters: Additional filters to apply  
              
        Returns:  
            A list of memory items matching the query  
        """  
        pass  
      
    @abstractmethod  
    def update(self, id: str, item: T, \*\*metadata) \-\> bool:  
        """  
        Update an existing memory item.  
          
        Args:  
            id: The identifier of the item to update  
            item: The new item data  
            \*\*metadata: Additional metadata to update  
              
        Returns:  
            Whether the update was successful  
        """  
        pass  
      
    @abstractmethod  
    def delete(self, id: str) \-\> bool:  
        """  
        Delete an item from memory.  
          
        Args:  
            id: The identifier of the item to delete  
              
        Returns:  
            Whether the deletion was successful  
        """  
        pass  
      
    @abstractmethod  
    def clear(self) \-\> None:  
        """Clear all items from memory."""  
        pass

#### **MemoryPersistence (Abstract Base Class)**

from abc import ABC, abstractmethod  
from typing import Dict, List, Any, Optional, TypeVar, Generic

T \= TypeVar('T')  \# The type of items being stored

class MemoryPersistence(Generic\[T\], ABC):  
    """Interface for memory persistence backends."""  
      
    @abstractmethod  
    def initialize(self) \-\> None:  
        """Initialize the persistence layer."""  
        pass  
      
    @abstractmethod  
    def store(self, namespace: str, key: str, value: T, metadata: Dict \= None) \-\> None:  
        """  
        Store a value with an associated key.  
          
        Args:  
            namespace: The namespace for organization  
            key: The unique key to store the value under  
            value: The value to store  
            metadata: Optional metadata for retrieval  
        """  
        pass  
      
    @abstractmethod  
    def retrieve(self, namespace: str, key: str) \-\> Optional\[T\]:  
        """  
        Retrieve a value by key.  
          
        Args:  
            namespace: The namespace to look in  
            key: The key to retrieve  
              
        Returns:  
            The stored value, or None if not found  
        """  
        pass  
      
    @abstractmethod  
    def search(self, namespace: str, query: Any, limit: int \= 10, \*\*filters) \-\> List\[Dict\]:  
        """  
        Search for values matching a query.  
          
        Args:  
            namespace: The namespace to search in  
            query: The query to match against  
            limit: Maximum number of results  
            \*\*filters: Additional filters  
              
        Returns:  
            A list of matching items with metadata  
        """  
        pass  
      
    @abstractmethod  
    def delete(self, namespace: str, key: str) \-\> bool:  
        """  
        Delete a value by key.  
          
        Args:  
            namespace: The namespace to delete from  
            key: The key to delete  
              
        Returns:  
            Whether the deletion was successful  
        """  
        pass  
      
    @abstractmethod  
    def clear\_namespace(self, namespace: str) \-\> None:  
        """  
        Clear all data in a namespace.  
          
        Args:  
            namespace: The namespace to clear  
        """  
        pass

### **4.3 Concrete Implementations**

#### **SemanticMemory**

from typing import Dict, List, Any, Optional  
from .base import BaseMemory  
from .persistence import MemoryPersistence

class SemanticMemory(BaseMemory\[Dict\[str, Any\]\]):  
    """  
    Stores factual knowledge as structured data.  
      
    Semantic memories represent:  
    \- Facts about entities (users, domains, etc.)  
    \- Preferences and settings  
    \- Conceptual relationships  
    """  
      
    def \_\_init\_\_(self,   
                 persistence: MemoryPersistence,  
                 namespace: str \= "semantic",  
                 llm\_config: Optional\[Dict\] \= None):  
        """  
        Initialize semantic memory.  
          
        Args:  
            persistence: The storage backend  
            namespace: Namespace for organization  
            llm\_config: Configuration for LLM-assisted memory operations  
        """  
        self.persistence \= persistence  
        self.namespace \= namespace  
        self.llm\_config \= llm\_config or {}  
          
    def save(self, item: Dict\[str, Any\], \*\*metadata) \-\> str:  
        """Save a semantic memory item."""  
        \# Generate a unique ID  
        memory\_id \= f"sem\_{uuid.uuid4().hex}"  
          
        \# Process with LLM if configured (for extraction/normalization)  
        if self.llm\_config and "save\_processor" in self.llm\_config:  
            item \= self.\_process\_with\_llm("save", item)  
          
        \# Store in persistence layer  
        self.persistence.store(  
            self.namespace,  
            memory\_id,  
            item,  
            metadata  
        )  
          
        return memory\_id  
      
    def retrieve(self, query: Any, limit: int \= 5, \*\*filters) \-\> List\[Dict\[str, Any\]\]:  
        """Retrieve semantic memories matching the query."""  
        \# Process query with LLM if configured  
        if self.llm\_config and "query\_processor" in self.llm\_config:  
            query \= self.\_process\_with\_llm("query", query)  
              
        \# Search in persistence layer  
        results \= self.persistence.search(  
            self.namespace,  
            query,  
            limit,  
            \*\*filters  
        )  
          
        return \[item\["value"\] for item in results\]  
      
    def update(self, id: str, item: Dict\[str, Any\], \*\*metadata) \-\> bool:  
        """Update an existing semantic memory."""  
        existing \= self.persistence.retrieve(self.namespace, id)  
        if not existing:  
            return False  
              
        \# Process with LLM if configured  
        if self.llm\_config and "update\_processor" in self.llm\_config:  
            item \= self.\_process\_with\_llm("update", {  
                "existing": existing,  
                "update": item  
            })  
              
        \# Store updated value  
        self.persistence.store(  
            self.namespace,  
            id,  
            item,  
            metadata  
        )  
          
        return True  
      
    def delete(self, id: str) \-\> bool:  
        """Delete a semantic memory."""  
        return self.persistence.delete(self.namespace, id)  
      
    def clear(self) \-\> None:  
        """Clear all semantic memories."""  
        self.persistence.clear\_namespace(self.namespace)  
      
    def \_process\_with\_llm(self, operation: str, data: Any) \-\> Any:  
        """Process memory operations with an LLM."""  
        \# Implementation depends on LLM integration  
        \# ...

Similar implementations would be created for `EpisodicMemory` and `ProceduralMemory`.

#### **CompositeMemory**

from typing import Dict, List, Any, Optional  
from .base import BaseMemory

class CompositeMemory:  
    """  
    Combines multiple memory types into a unified interface.  
      
    This allows agents to use different memory types without  
    having to manage them individually.  
    """  
      
    def \_\_init\_\_(self, memories: Dict\[str, BaseMemory\]):  
        """  
        Initialize with a dictionary of memory instances.  
          
        Args:  
            memories: Dictionary mapping memory names to instances  
        """  
        self.memories \= memories  
          
    def save\_to(self, memory\_type: str, item: Any, \*\*metadata) \-\> str:  
        """  
        Save an item to a specific memory type.  
          
        Args:  
            memory\_type: Which memory to save to  
            item: The item to save  
            \*\*metadata: Additional metadata  
              
        Returns:  
            A unique identifier for the saved item  
        """  
        if memory\_type not in self.memories:  
            raise ValueError(f"Unknown memory type: {memory\_type}")  
              
        return self.memories\[memory\_type\].save(item, \*\*metadata)  
      
    def retrieve\_from(self, memory\_type: str, query: Any, limit: int \= 5, \*\*filters) \-\> List\[Any\]:  
        """  
        Retrieve items from a specific memory type.  
          
        Args:  
            memory\_type: Which memory to retrieve from  
            query: The query to match against  
            limit: Maximum number of items to return  
            \*\*filters: Additional filters to apply  
              
        Returns:  
            A list of memory items matching the query  
        """  
        if memory\_type not in self.memories:  
            raise ValueError(f"Unknown memory type: {memory\_type}")  
              
        return self.memories\[memory\_type\].retrieve(query, limit, \*\*filters)  
      
    def retrieve\_all(self, query: Any, limits: Dict\[str, int\] \= None) \-\> Dict\[str, List\[Any\]\]:  
        """  
        Retrieve items from all memory types.  
          
        Args:  
            query: The query to match against  
            limits: Dictionary mapping memory types to result limits  
              
        Returns:  
            Dictionary mapping memory types to retrieved items  
        """  
        limits \= limits or {k: 5 for k in self.memories}  
        results \= {}  
          
        for memory\_type, memory in self.memories.items():  
            limit \= limits.get(memory\_type, 5\)  
            results\[memory\_type\] \= memory.retrieve(query, limit)  
              
        return results

### **4.4 Vector Store Integration**

The `VectorStorePersistence` class provides an implementation of `MemoryPersistence` that uses vector databases:

from typing import Dict, List, Any, Optional  
from .base import MemoryPersistence

class VectorStorePersistence(MemoryPersistence):  
    """Vector store implementation of memory persistence."""  
      
    def \_\_init\_\_(self, vector\_store, embedding\_function):  
        """  
        Initialize with a vector store and embedding function.  
          
        Args:  
            vector\_store: The vector database client  
            embedding\_function: Function to convert items to vectors  
        """  
        self.vector\_store \= vector\_store  
        self.embedding\_function \= embedding\_function  
          
    def initialize(self) \-\> None:  
        """Initialize the vector store."""  
        \# Implementation depends on the specific vector store  
        pass  
      
    def store(self, namespace: str, key: str, value: Any, metadata: Dict \= None) \-\> None:  
        """Store a value with an associated key."""  
        metadata \= metadata or {}  
        metadata\["\_id"\] \= key  
          
        \# Generate embedding  
        embedding \= self.embedding\_function(value)  
          
        \# Store in vector database  
        self.vector\_store.add(  
            collection=namespace,  
            embedding=embedding,  
            document=value,  
            metadata=metadata  
        )  
      
    def retrieve(self, namespace: str, key: str) \-\> Optional\[Any\]:  
        """Retrieve a value by key."""  
        result \= self.vector\_store.get(  
            collection=namespace,  
            filter={"\_id": key}  
        )  
          
        if not result:  
            return None  
              
        return result\[0\]\["document"\]  
      
    def search(self, namespace: str, query: Any, limit: int \= 10, \*\*filters) \-\> List\[Dict\]:  
        """Search for values matching a query."""  
        \# Generate query embedding  
        embedding \= self.embedding\_function(query)  
          
        \# Search vector database  
        results \= self.vector\_store.search(  
            collection=namespace,  
            query\_embedding=embedding,  
            limit=limit,  
            filter=filters  
        )  
          
        return \[  
            {  
                "id": item\["metadata"\]\["\_id"\],  
                "value": item\["document"\],  
                "metadata": item\["metadata"\],  
                "score": item\["score"\]  
            }  
            for item in results  
        \]  
      
    def delete(self, namespace: str, key: str) \-\> bool:  
        """Delete a value by key."""  
        return self.vector\_store.delete(  
            collection=namespace,  
            filter={"\_id": key}  
        )  
      
    def clear\_namespace(self, namespace: str) \-\> None:  
        """Clear all data in a namespace."""  
        self.vector\_store.delete\_collection(namespace)

## **5\. Integration with Agent Patterns**

### **5.1 BaseAgent Enhancement**

Update the `BaseAgent` class to support memory:

class BaseAgent(abc.ABC):  
    def \_\_init\_\_(self,   
                 llm\_configs: dict,   
                 prompt\_dir: str \= "prompts",  
                 tool\_provider: Optional\[ToolProvider\] \= None,  
                 memory: Optional\[CompositeMemory\] \= None,  
                 memory\_config: Optional\[Dict\[str, bool\]\] \= None):  
        """  
        Initialize the agent.  
          
        Args:  
            llm\_configs: Dictionary specifying provider, model, and roles  
            prompt\_dir: Directory for prompt templates  
            tool\_provider: Optional provider for tools the agent can use  
            memory: Optional composite memory instance  
            memory\_config: Configuration for which memory types to use  
        """  
        self.llm\_configs \= llm\_configs  
        self.prompt\_dir \= prompt\_dir  
        self.tool\_provider \= tool\_provider  
        self.memory \= memory  
        self.memory\_config \= memory\_config or {  
            "semantic": True,  
            "episodic": True,  
            "procedural": False  \# Off by default as it's more experimental  
        }  
          
        self.graph \= None  \# set by self.build\_graph()  
          
        \# Subclass is expected to build/compile its graph  
        self.build\_graph()  
      
    def \_retrieve\_memories(self, query: str) \-\> Dict\[str, List\[Any\]\]:  
        """  
        Retrieve relevant memories for a query.  
          
        Args:  
            query: The input query or context  
              
        Returns:  
            Dictionary mapping memory types to retrieved items  
        """  
        if not self.memory:  
            return {}  
              
        \# Filter enabled memory types  
        enabled\_memories \= {  
            k: v for k, v in self.memory.memories.items()  
            if self.memory\_config.get(k, False)  
        }  
          
        if not enabled\_memories:  
            return {}  
              
        \# Create a filtered composite memory  
        filtered\_memory \= CompositeMemory(enabled\_memories)  
          
        \# Retrieve from all enabled memories  
        return filtered\_memory.retrieve\_all(query)  
      
    def \_save\_memory(self, memory\_type: str, item: Any, \*\*metadata) \-\> Optional\[str\]:  
        """  
        Save an item to a specific memory type if enabled.  
          
        Args:  
            memory\_type: Which memory to save to  
            item: The item to save  
            \*\*metadata: Additional metadata  
              
        Returns:  
            A unique identifier for the saved item, or None if memory type is disabled  
        """  
        if not self.memory or not self.memory\_config.get(memory\_type, False):  
            return None  
              
        return self.memory.save\_to(memory\_type, item, \*\*metadata)

### **5.2 Pattern-Specific Enhancements**

#### **ReActAgent with Memory**

def \_generate\_thought\_and\_action(self, state: Dict) \-\> Dict:  
    """Generate the next thought and action based on the current state."""  
    \# Retrieve relevant memories  
    memories \= self.\_retrieve\_memories(state\["input"\])  
      
    \# Prepare the prompt with memories  
    prompt\_data \= self.\_loa
