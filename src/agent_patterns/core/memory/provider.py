"""Memory provider for agent patterns.

This module provides a MemoryProvider class that interfaces between agents
and memory systems to support retrieving and storing memories.
"""

from typing import Dict, List, Any, Optional
from agent_patterns.core.memory.base import BaseMemory


class MemoryProvider:
    """Provider class for interfacing agents with memory systems.
    
    This class handles the integration between agents and memory systems,
    allowing agents to store and retrieve memories during execution.
    """
    
    def __init__(self, memory: BaseMemory):
        """Initialize the memory provider with a memory instance.
        
        Args:
            memory: The memory system to use for storage and retrieval.
        """
        self.memory = memory
    
    def add(self, key: str, data: Any) -> None:
        """Add data to memory.
        
        Args:
            key: The key to store the data under
            data: The data to store
        """
        self.memory.add(key, data)
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve data from memory.
        
        Args:
            key: The key to retrieve data for
            
        Returns:
            The retrieved data or None if not found
        """
        return self.memory.get(key)
    
    def update(self, key: str, data: Any) -> None:
        """Update existing data in memory.
        
        Args:
            key: The key of the data to update
            data: The new data to store
        """
        self.memory.update(key, data)
    
    def delete(self, key: str) -> None:
        """Delete data from memory.
        
        Args:
            key: The key of the data to delete
        """
        self.memory.delete(key)
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for data in memory.
        
        Args:
            query: The search query
            
        Returns:
            A list of matching results
        """
        return self.memory.search(query)
    
    def clear(self) -> None:
        """Clear all data from memory."""
        self.memory.clear()