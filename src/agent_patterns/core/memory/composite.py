"""Composite memory implementation that combines multiple memory types."""

import uuid
import asyncio
from typing import Dict, List, Any, Optional, TypeVar, Union, Generic, Type, cast
import logging

from .base import BaseMemory

T = TypeVar('T')  # Memory item type

class CompositeMemory:
    """
    Combines multiple memory types into a unified interface.
    
    This allows agents to use different memory types without
    having to manage them individually.
    """
    
    def __init__(self, memories: Dict[str, BaseMemory]):
        """
        Initialize with a dictionary of memory instances.
        
        Args:
            memories: Dictionary mapping memory names to instances
        """
        self.memories = memories
        self.logger = logging.getLogger("CompositeMemory")
    
    async def save_to(self, memory_type: str, item: Any, **metadata) -> Optional[str]:
        """
        Save an item to a specific memory type.
        
        Args:
            memory_type: Which memory to save to
            item: The item to save
            **metadata: Additional metadata
            
        Returns:
            A unique identifier for the saved item or None if memory type not found
        """
        if memory_type not in self.memories:
            self.logger.warning(f"Unknown memory type: {memory_type}")
            return None
        
        try:
            memory_id = await self.memories[memory_type].save(item, **metadata)
            self.logger.debug(f"Saved item to {memory_type} memory with ID {memory_id}")
            return memory_id
        except Exception as e:
            self.logger.error(f"Error saving to {memory_type} memory: {str(e)}")
            return None
    
    async def retrieve_from(self, memory_type: str, query: Any, limit: int = 5, **filters) -> List[Any]:
        """
        Retrieve items from a specific memory type.
        
        Args:
            memory_type: Which memory to retrieve from
            query: The query to match against
            limit: Maximum number of items to return
            **filters: Additional filters to apply
            
        Returns:
            A list of memory items matching the query or empty list if memory type not found
        """
        if memory_type not in self.memories:
            self.logger.warning(f"Unknown memory type: {memory_type}")
            return []
        
        try:
            items = await self.memories[memory_type].retrieve(query, limit, **filters)
            self.logger.debug(f"Retrieved {len(items)} items from {memory_type} memory")
            return items
        except Exception as e:
            self.logger.error(f"Error retrieving from {memory_type} memory: {str(e)}")
            return []
    
    async def retrieve_all(self, query: Any, limits: Optional[Dict[str, int]] = None, 
                          filters: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, List[Any]]:
        """
        Retrieve items from all memory types.
        
        Args:
            query: The query to match against
            limits: Dictionary mapping memory types to result limits
            filters: Dictionary mapping memory types to filter dictionaries
            
        Returns:
            Dictionary mapping memory types to retrieved items
        """
        limits = limits or {k: 5 for k in self.memories}
        filters = filters or {}
        results = {}
        
        # Create async tasks for all memory retrievals
        tasks = []
        for memory_type, memory in self.memories.items():
            limit = limits.get(memory_type, 5)
            memory_filters = filters.get(memory_type, {})
            
            task = asyncio.create_task(
                self._safe_retrieve(memory_type, memory, query, limit, **memory_filters)
            )
            tasks.append((memory_type, task))
        
        # Gather all results
        for memory_type, task in tasks:
            try:
                items = await task
                results[memory_type] = items
            except Exception as e:
                self.logger.error(f"Error retrieving from {memory_type} memory: {str(e)}")
                results[memory_type] = []
        
        return results
    
    async def update_in(self, memory_type: str, id: str, item: Any, **metadata) -> bool:
        """
        Update an item in a specific memory type.
        
        Args:
            memory_type: Which memory to update in
            id: The identifier of the item to update
            item: The new item data
            **metadata: Additional metadata to update
            
        Returns:
            Whether the update was successful
        """
        if memory_type not in self.memories:
            self.logger.warning(f"Unknown memory type: {memory_type}")
            return False
        
        try:
            result = await self.memories[memory_type].update(id, item, **metadata)
            if result:
                self.logger.debug(f"Updated item in {memory_type} memory with ID {id}")
            else:
                self.logger.warning(f"Failed to update item in {memory_type} memory with ID {id}")
            return result
        except Exception as e:
            self.logger.error(f"Error updating in {memory_type} memory: {str(e)}")
            return False
    
    async def delete_from(self, memory_type: str, id: str) -> bool:
        """
        Delete an item from a specific memory type.
        
        Args:
            memory_type: Which memory to delete from
            id: The identifier of the item to delete
            
        Returns:
            Whether the deletion was successful
        """
        if memory_type not in self.memories:
            self.logger.warning(f"Unknown memory type: {memory_type}")
            return False
        
        try:
            result = await self.memories[memory_type].delete(id)
            if result:
                self.logger.debug(f"Deleted item from {memory_type} memory with ID {id}")
            else:
                self.logger.warning(f"Failed to delete item from {memory_type} memory with ID {id}")
            return result
        except Exception as e:
            self.logger.error(f"Error deleting from {memory_type} memory: {str(e)}")
            return False
    
    async def clear_all(self) -> None:
        """Clear all memories of all types."""
        tasks = []
        for memory_type, memory in self.memories.items():
            task = asyncio.create_task(self._safe_clear(memory_type, memory))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        self.logger.debug("Cleared all memories")
    
    async def clear_type(self, memory_type: str) -> bool:
        """
        Clear all memories of a specific type.
        
        Args:
            memory_type: Which memory type to clear
            
        Returns:
            Whether the operation was successful
        """
        if memory_type not in self.memories:
            self.logger.warning(f"Unknown memory type: {memory_type}")
            return False
        
        try:
            await self.memories[memory_type].clear()
            self.logger.debug(f"Cleared all {memory_type} memories")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing {memory_type} memory: {str(e)}")
            return False
    
    # Helper methods
    
    async def _safe_retrieve(self, memory_type: str, memory: BaseMemory, 
                            query: Any, limit: int, **filters) -> List[Any]:
        """Safely retrieve from a memory with error handling."""
        try:
            return await memory.retrieve(query, limit, **filters)
        except Exception as e:
            self.logger.error(f"Error retrieving from {memory_type} memory: {str(e)}")
            return []
    
    async def _safe_clear(self, memory_type: str, memory: BaseMemory) -> None:
        """Safely clear a memory with error handling."""
        try:
            await memory.clear()
            self.logger.debug(f"Cleared {memory_type} memory")
        except Exception as e:
            self.logger.error(f"Error clearing {memory_type} memory: {str(e)}")
    
    # Synchronous versions of methods for convenience
    
    def sync_save_to(self, memory_type: str, item: Any, **metadata) -> Optional[str]:
        """Synchronous wrapper for save_to."""
        return asyncio.run(self.save_to(memory_type, item, **metadata))
    
    def sync_retrieve_from(self, memory_type: str, query: Any, limit: int = 5, **filters) -> List[Any]:
        """Synchronous wrapper for retrieve_from."""
        return asyncio.run(self.retrieve_from(memory_type, query, limit, **filters))
    
    def sync_retrieve_all(self, query: Any, limits: Optional[Dict[str, int]] = None, 
                         filters: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, List[Any]]:
        """Synchronous wrapper for retrieve_all."""
        return asyncio.run(self.retrieve_all(query, limits, filters))
    
    def sync_update_in(self, memory_type: str, id: str, item: Any, **metadata) -> bool:
        """Synchronous wrapper for update_in."""
        return asyncio.run(self.update_in(memory_type, id, item, **metadata))
    
    def sync_delete_from(self, memory_type: str, id: str) -> bool:
        """Synchronous wrapper for delete_from."""
        return asyncio.run(self.delete_from(memory_type, id))
    
    def sync_clear_all(self) -> None:
        """Synchronous wrapper for clear_all."""
        asyncio.run(self.clear_all())
    
    def sync_clear_type(self, memory_type: str) -> bool:
        """Synchronous wrapper for clear_type."""
        return asyncio.run(self.clear_type(memory_type)) 