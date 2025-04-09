"""Base interfaces for memory components."""

import abc
import asyncio
from typing import Dict, List, Any, Optional, TypeVar, Generic, Union

T = TypeVar('T')  # Memory item type

class BaseMemory(Generic[T], abc.ABC):
    """Base interface for all memory types."""
    
    @abc.abstractmethod
    async def save(self, item: T, **metadata) -> str:
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
    async def retrieve(self, query: Any, limit: int = 5, **filters) -> List[T]:
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
    async def update(self, id: str, item: T, **metadata) -> bool:
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
    async def delete(self, id: str) -> bool:
        """
        Delete an item from memory.
        
        Args:
            id: The identifier of the item to delete
            
        Returns:
            Whether the deletion was successful
        """
        pass
    
    @abc.abstractmethod
    async def clear(self) -> None:
        """Clear all items from memory."""
        pass

    def sync_save(self, item: T, **metadata) -> str:
        """Synchronous wrapper for save."""
        return asyncio.run(self.save(item, **metadata))
    
    def sync_retrieve(self, query: Any, limit: int = 5, **filters) -> List[T]:
        """Synchronous wrapper for retrieve."""
        return asyncio.run(self.retrieve(query, limit, **filters))
    
    def sync_update(self, id: str, item: T, **metadata) -> bool:
        """Synchronous wrapper for update."""
        return asyncio.run(self.update(id, item, **metadata))
    
    def sync_delete(self, id: str) -> bool:
        """Synchronous wrapper for delete."""
        return asyncio.run(self.delete(id))
    
    def sync_clear(self) -> None:
        """Synchronous wrapper for clear."""
        asyncio.run(self.clear())


class MemoryPersistence(Generic[T], abc.ABC):
    """Interface for memory persistence backends."""
    
    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize the persistence layer."""
        pass
    
    @abc.abstractmethod
    async def store(self, namespace: str, key: str, value: T, metadata: Dict = None) -> None:
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
    async def retrieve(self, namespace: str, key: str) -> Optional[T]:
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
    async def search(self, namespace: str, query: Any, limit: int = 10, **filters) -> List[Dict]:
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
    async def delete(self, namespace: str, key: str) -> bool:
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
    async def clear_namespace(self, namespace: str) -> None:
        """
        Clear all data in a namespace.
        
        Args:
            namespace: The namespace to clear
        """
        pass
    
    def sync_initialize(self) -> None:
        """Synchronous wrapper for initialize."""
        asyncio.run(self.initialize())
    
    def sync_store(self, namespace: str, key: str, value: T, metadata: Dict = None) -> None:
        """Synchronous wrapper for store."""
        asyncio.run(self.store(namespace, key, value, metadata))
    
    def sync_retrieve(self, namespace: str, key: str) -> Optional[T]:
        """Synchronous wrapper for retrieve."""
        return asyncio.run(self.retrieve(namespace, key))
    
    def sync_search(self, namespace: str, query: Any, limit: int = 10, **filters) -> List[Dict]:
        """Synchronous wrapper for search."""
        return asyncio.run(self.search(namespace, query, limit, **filters))
    
    def sync_delete(self, namespace: str, key: str) -> bool:
        """Synchronous wrapper for delete."""
        return asyncio.run(self.delete(namespace, key))
    
    def sync_clear_namespace(self, namespace: str) -> None:
        """Synchronous wrapper for clear_namespace."""
        asyncio.run(self.clear_namespace(namespace)) 