"""Composite memory implementation that combines multiple memory types."""

import uuid
from typing import Dict, List, Any, Optional, TypeVar, Union, Generic, Type, cast
import logging

from .base import BaseMemory

T = TypeVar('T')  # Memory item type

class CompositeMemory:
    """

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only


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
        
        # Initialize persistence layers
        self._initialize_persistence()
    
    def _initialize_persistence(self):
        """Initialize all persistence layers."""
        for memory_type, memory in self.memories.items():
            if hasattr(memory.persistence, 'initialize'):
                memory.persistence.initialize()
    
    def save_to(self, memory_type: str, item: Any, **metadata) -> Optional[str]:
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
            memory = self.memories[memory_type]
            memory_id = memory.save(item, **metadata)
            self.logger.debug(f"Saved item to {memory_type} memory with ID {memory_id}")
            return memory_id
        except Exception as e:
            self.logger.error(f"Error saving to {memory_type} memory: {str(e)}")
            return None
    
    def retrieve_from(self, memory_type: str, query: Any, limit: int = 5, **filters) -> List[Any]:
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
            memory = self.memories[memory_type]
            items = memory.retrieve(query, limit, **filters)
            self.logger.debug(f"Retrieved {len(items)} items from {memory_type} memory")
            return items
        except Exception as e:
            self.logger.error(f"Error retrieving from {memory_type} memory: {str(e)}")
            return []
    
    def retrieve_all(self, query: Any, limits: Optional[Dict[str, int]] = None, 
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
        
        # Retrieve from each memory type
        for memory_type, memory in self.memories.items():
            limit = limits.get(memory_type, 5)
            memory_filters = filters.get(memory_type, {})
            
            try:
                items = memory.retrieve(query, limit, **memory_filters)
                results[memory_type] = items
            except Exception as e:
                self.logger.error(f"Error retrieving from {memory_type} memory: {str(e)}")
                results[memory_type] = []
        
        return results
    
    def update_in(self, memory_type: str, id: str, item: Any, **metadata) -> bool:
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
            memory = self.memories[memory_type]
            success = memory.update(id, item, **metadata)
            
            if success:
                self.logger.debug(f"Updated item in {memory_type} memory with ID {id}")
            else:
                self.logger.warning(f"Failed to update item in {memory_type} memory with ID {id}")
                
            return success
        except Exception as e:
            self.logger.error(f"Error updating in {memory_type} memory: {str(e)}")
            return False
    
    def delete_from(self, memory_type: str, id: str) -> bool:
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
            memory = self.memories[memory_type]
            success = memory.delete(id)
            
            if success:
                self.logger.debug(f"Deleted item from {memory_type} memory with ID {id}")
            else:
                self.logger.warning(f"Failed to delete item from {memory_type} memory with ID {id}")
                
            return success
        except Exception as e:
            self.logger.error(f"Error deleting from {memory_type} memory: {str(e)}")
            return False
    
    def clear_all(self) -> None:
        """Clear all memories of all types."""
        for memory_type, memory in self.memories.items():
            self.clear_type(memory_type)
    
    def clear_type(self, memory_type: str) -> bool:
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
            memory = self.memories[memory_type]
            memory.clear()
            self.logger.debug(f"Cleared all {memory_type} memories")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing {memory_type} memory: {str(e)}")
            return False 