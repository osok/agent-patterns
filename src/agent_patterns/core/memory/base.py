"""Base interfaces for memory components."""

import abc
from typing import Dict, List, Any, Optional, TypeVar, Generic, Union

T = TypeVar('T')  # Memory item type

class BaseMemory(Generic[T], abc.ABC):
    """Base interface for all memory types."""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only


    
    @abc.abstractmethod
    def save(self, item: T, **metadata) -> str:
        """
        Save an item to memory.
        
        Args:
            item: The item to save
            **metadata: Additional metadata for storage
            
        Returns:
            A unique identifier for the saved item
        """
        pass
    
    @abc.abstractmethod
    def retrieve(self, query: Any, limit: int = 5, **filters) -> List[T]:
        """
        Retrieve items from memory based on a query.
        
        Args:
            query: The query to match against
            limit: Maximum number of items to return
            **filters: Additional filters to apply
            
        Returns:
            A list of memory items matching the query
        """
        pass
    
    @abc.abstractmethod
    def update(self, id: str, item: T, **metadata) -> bool:
        """
        Update an existing memory item.
        
        Args:
            id: The identifier of the item to update
            item: The new item data
            **metadata: Additional metadata to update
            
        Returns:
            Whether the update was successful
        """
        pass
    
    @abc.abstractmethod
    def delete(self, id: str) -> bool:
        """
        Delete an item from memory.
        
        Args:
            id: The identifier of the item to delete
            
        Returns:
            Whether the deletion was successful
        """
        pass
    
    @abc.abstractmethod
    def clear(self) -> None:
        """Clear all items from memory."""
        pass


class MemoryPersistence(Generic[T], abc.ABC):
    """Interface for memory persistence backends."""
    
    @abc.abstractmethod
    def initialize(self) -> None:
        """Initialize the persistence layer."""
        pass
    
    @abc.abstractmethod
    def store(self, namespace: str, key: str, value: T, metadata: Dict = None) -> None:
        """
        Store a value with an associated key.
        
        Args:
            namespace: The namespace for organization
            key: The unique key to store the value under
            value: The value to store
            metadata: Optional metadata for retrieval
        """
        pass
    
    @abc.abstractmethod
    def retrieve(self, namespace: str, key: str) -> Optional[T]:
        """
        Retrieve a value by key.
        
        Args:
            namespace: The namespace to look in
            key: The key to retrieve
            
        Returns:
            The stored value, or None if not found
        """
        pass
    
    @abc.abstractmethod
    def search(self, namespace: str, query: Any, limit: int = 10, **filters) -> List[Dict]:
        """
        Search for values matching a query.
        
        Args:
            namespace: The namespace to search in
            query: The query to match against
            limit: Maximum number of results
            **filters: Additional filters
            
        Returns:
            A list of matching items with metadata
        """
        pass
    
    @abc.abstractmethod
    def delete(self, namespace: str, key: str) -> bool:
        """
        Delete a value by key.
        
        Args:
            namespace: The namespace to delete from
            key: The key to delete
            
        Returns:
            Whether the deletion was successful
        """
        pass
    
    @abc.abstractmethod
    def clear_namespace(self, namespace: str) -> None:
        """
        Clear all data in a namespace.
        
        Args:
            namespace: The namespace to clear
        """
        pass 