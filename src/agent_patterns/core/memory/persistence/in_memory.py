"""In-memory persistence backend for memory storage."""

import uuid
from typing import Dict, List, Any, Optional, TypeVar, Set, Union
from difflib import SequenceMatcher

from ..base import MemoryPersistence

T = TypeVar('T')  # Memory item type

class InMemoryPersistence(MemoryPersistence[T]):
    """
    In-memory implementation of memory persistence.
    
    This implementation stores all data in memory and is intended primarily for testing.
    Data will be lost when the process terminates.
    """
    
    def __init__(self):
        """Initialize the in-memory persistence layer."""
        self._storage: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the persistence layer."""
        self._storage = {}
        self._initialized = True
    
    async def store(self, namespace: str, key: str, value: T, metadata: Dict = None) -> None:
        """
        Store a value with an associated key.
        
        Args:
            namespace: The namespace for organization
            key: The unique key to store the value under
            value: The value to store
            metadata: Optional metadata for retrieval
        """
        self._ensure_initialized()
        
        if namespace not in self._storage:
            self._storage[namespace] = {}
        
        self._storage[namespace][key] = {
            "value": value,
            "metadata": metadata or {}
        }
    
    async def retrieve(self, namespace: str, key: str) -> Optional[T]:
        """
        Retrieve a value by key.
        
        Args:
            namespace: The namespace to look in
            key: The key to retrieve
            
        Returns:
            The stored value, or None if not found
        """
        self._ensure_initialized()
        
        if namespace not in self._storage or key not in self._storage[namespace]:
            return None
        
        return self._storage[namespace][key]["value"]
    
    async def search(self, namespace: str, query: Any, limit: int = 10, **filters) -> List[Dict]:
        """
        Search for values matching a query.
        
        For in-memory persistence, we use a simple text similarity algorithm.
        For more sophisticated searches, use a vector store backend.
        
        Args:
            namespace: The namespace to search in
            query: The query string to match against
            limit: Maximum number of results
            **filters: Additional metadata filters to apply
            
        Returns:
            A list of matching items with metadata and id
        """
        self._ensure_initialized()
        
        if namespace not in self._storage:
            return []
        
        query_str = str(query)
        results = []
        
        for key, item in self._storage[namespace].items():
            # Check if item matches filters
            if not self._matches_filters(item["metadata"], filters):
                continue
            
            # Simple similarity using all fields
            similarity = 0
            
            # Calculate similarity based on string representation of the value
            value_str = str(item["value"])
            similarity = SequenceMatcher(None, query_str, value_str).ratio()
            
            results.append({
                "id": key,
                "value": item["value"],
                "metadata": item["metadata"],
                "score": similarity
            })
        
        # Sort by score and limit results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    async def delete(self, namespace: str, key: str) -> bool:
        """
        Delete a value by key.
        
        Args:
            namespace: The namespace to delete from
            key: The key to delete
            
        Returns:
            Whether the deletion was successful
        """
        self._ensure_initialized()
        
        if namespace not in self._storage or key not in self._storage[namespace]:
            return False
        
        del self._storage[namespace][key]
        return True
    
    async def clear_namespace(self, namespace: str) -> None:
        """
        Clear all data in a namespace.
        
        Args:
            namespace: The namespace to clear
        """
        self._ensure_initialized()
        
        if namespace in self._storage:
            self._storage[namespace] = {}
    
    def _ensure_initialized(self) -> None:
        """Ensure the persistence layer is initialized."""
        if not self._initialized:
            raise RuntimeError("Persistence layer not initialized. Call initialize() first.")
    
    def _matches_filters(self, metadata: Dict, filters: Dict) -> bool:
        """Check if metadata matches all given filters."""
        if not filters:
            return True
        
        for key, value in filters.items():
            if key not in metadata or metadata[key] != value:
                return False
        
        return True 