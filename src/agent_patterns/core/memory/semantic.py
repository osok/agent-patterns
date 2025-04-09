"""Semantic memory implementation for storing factual knowledge."""

import uuid
import json
import asyncio
from typing import Dict, List, Any, Optional, TypeVar, Union, cast
import logging

from .base import BaseMemory, MemoryPersistence

T = TypeVar('T')  # Item type, typically Dict[str, Any] for semantic memory

class SemanticMemory(BaseMemory[Dict[str, Any]]):
    """
    Stores factual knowledge as structured data.
    
    Semantic memories represent:
    - Facts about entities (users, domains, etc.)
    - Preferences and settings
    - Conceptual relationships
    
    Uses a structured key-value format for storing facts and knowledge.
    """
    
    def __init__(
        self,
        persistence: MemoryPersistence,
        namespace: str = "semantic",
        llm_config: Optional[Dict] = None
    ):
        """
        Initialize semantic memory.
        
        Args:
            persistence: The storage backend
            namespace: Namespace for organization
            llm_config: Configuration for LLM-assisted memory operations
        """
        self.persistence = persistence
        self.namespace = namespace
        self.llm_config = llm_config or {}
        self.logger = logging.getLogger("SemanticMemory")
        
        # Ensure the storage system is initialized
        asyncio.create_task(self.persistence.initialize())
    
    async def save(self, item: Dict[str, Any], **metadata) -> str:
        """
        Save a semantic memory item.
        
        Args:
            item: The item to save (dictionary of attributes)
            **metadata: Additional metadata for storage
            
        Returns:
            A unique identifier for the saved item
        """
        if not isinstance(item, dict):
            raise TypeError("Semantic memory items must be dictionaries")
        
        # Generate a unique ID if not provided
        memory_id = metadata.pop('id', f"sem_{uuid.uuid4().hex}")
        
        # Process with LLM if configured (for extraction/normalization)
        if self.llm_config and "save_processor" in self.llm_config:
            try:
                item = await self._process_with_llm("save", item)
            except Exception as e:
                self.logger.warning(f"LLM processing failed during save: {str(e)}")
        
        # Store in persistence layer
        await self.persistence.store(
            self.namespace,
            memory_id,
            item,
            metadata
        )
        
        self.logger.debug(f"Saved semantic memory with ID {memory_id}")
        return memory_id
    
    async def retrieve(self, query: Any, limit: int = 5, **filters) -> List[Dict[str, Any]]:
        """
        Retrieve semantic memories matching the query.
        
        Args:
            query: The query to match against
            limit: Maximum number of items to return
            **filters: Additional filters to apply
            
        Returns:
            A list of memory items matching the query
        """
        # Process query with LLM if configured
        if self.llm_config and "query_processor" in self.llm_config:
            try:
                query = await self._process_with_llm("query", query)
            except Exception as e:
                self.logger.warning(f"LLM processing failed during query: {str(e)}")
        
        # Search in persistence layer
        results = await self.persistence.search(
            self.namespace,
            query,
            limit,
            **filters
        )
        
        return [item["value"] for item in results]
    
    async def update(self, id: str, item: Dict[str, Any], **metadata) -> bool:
        """
        Update an existing semantic memory.
        
        Args:
            id: The identifier of the item to update
            item: The new item data
            **metadata: Additional metadata to update
            
        Returns:
            Whether the update was successful
        """
        if not isinstance(item, dict):
            raise TypeError("Semantic memory items must be dictionaries")
            
        # Check if the item exists
        existing = await self.persistence.retrieve(self.namespace, id)
        if not existing:
            self.logger.warning(f"Cannot update semantic memory with ID {id}: not found")
            return False
        
        # Process with LLM if configured
        if self.llm_config and "update_processor" in self.llm_config:
            try:
                item = await self._process_with_llm("update", {
                    "existing": existing,
                    "update": item
                })
            except Exception as e:
                self.logger.warning(f"LLM processing failed during update: {str(e)}")
        
        # Store updated value
        await self.persistence.store(
            self.namespace,
            id,
            item,
            metadata
        )
        
        self.logger.debug(f"Updated semantic memory with ID {id}")
        return True
    
    async def delete(self, id: str) -> bool:
        """
        Delete a semantic memory.
        
        Args:
            id: The identifier of the item to delete
            
        Returns:
            Whether the deletion was successful
        """
        result = await self.persistence.delete(self.namespace, id)
        if result:
            self.logger.debug(f"Deleted semantic memory with ID {id}")
        else:
            self.logger.warning(f"Failed to delete semantic memory with ID {id}")
        return result
    
    async def clear(self) -> None:
        """Clear all semantic memories."""
        await self.persistence.clear_namespace(self.namespace)
        self.logger.debug(f"Cleared all semantic memories in namespace {self.namespace}")
    
    async def _process_with_llm(self, operation: str, data: Any) -> Any:
        """
        Process memory operations with an LLM.
        
        Args:
            operation: The type of operation (save, query, update)
            data: The data to process
            
        Returns:
            The processed data
        """
        if not self.llm_config or f"{operation}_processor" not in self.llm_config:
            return data
        
        processor = self.llm_config[f"{operation}_processor"]
        
        if asyncio.iscoroutinefunction(processor):
            return await processor(data)
        else:
            return processor(data) 