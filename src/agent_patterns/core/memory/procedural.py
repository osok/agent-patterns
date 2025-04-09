"""Procedural memory implementation for storing learned behaviors and action patterns."""

import uuid
import json
import asyncio
from typing import Dict, List, Any, Optional, TypeVar, Union, cast
import logging

from .base import BaseMemory, MemoryPersistence

class Procedure:
    """Represents a learned behavior or action pattern in procedural memory."""
    
    def __init__(
        self,
        name: str,
        pattern: Dict[str, Any],
        description: str = "",
        success_rate: float = 0.0,
        usage_count: int = 0,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a procedure.
        
        Args:
            name: Unique name for the procedure
            pattern: The pattern/template for the procedure (could be a prompt template, action sequence, etc.)
            description: Human-readable description of what the procedure does
            success_rate: Historical success rate of this procedure (0.0 to 1.0)
            usage_count: Number of times this procedure has been used
            tags: List of tags for categorization
            metadata: Additional metadata for the procedure
        """
        self.name = name
        self.pattern = pattern
        self.description = description
        self.success_rate = max(0.0, min(1.0, success_rate))  # Clamp to [0, 1]
        self.usage_count = max(0, usage_count)
        self.tags = tags or []
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for storage."""
        return {
            "name": self.name,
            "pattern": self.pattern,
            "description": self.description,
            "success_rate": self.success_rate,
            "usage_count": self.usage_count,
            "tags": self.tags,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Procedure':
        """Create a procedure from a dictionary."""
        return cls(
            name=data.get("name", ""),
            pattern=data.get("pattern", {}),
            description=data.get("description", ""),
            success_rate=data.get("success_rate", 0.0),
            usage_count=data.get("usage_count", 0),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )
    
    def record_usage(self, success: bool) -> None:
        """
        Record a usage of this procedure.
        
        Args:
            success: Whether the procedure was successful
        """
        # Update success rate as a weighted average
        if self.usage_count > 0:
            # Use a weighted average that gives more weight to recent results
            # as the usage count increases
            weight = min(0.1, 1.0 / self.usage_count)  # Lower weight as usage increases
            self.success_rate = (1 - weight) * self.success_rate + weight * (1.0 if success else 0.0)
        else:
            # First usage
            self.success_rate = 1.0 if success else 0.0
        
        # Increment usage count
        self.usage_count += 1


class ProceduralMemory(BaseMemory[Procedure]):
    """
    Stores learned behaviors and action patterns.
    
    Procedural memories represent:
    - Reusable action sequences
    - Learned techniques and behaviors
    - Templates for solving common problems
    
    Uses a combination of semantic retrieval and success metrics for selection.
    """
    
    def __init__(
        self,
        persistence: MemoryPersistence,
        namespace: str = "procedural",
        llm_config: Optional[Dict] = None
    ):
        """
        Initialize procedural memory.
        
        Args:
            persistence: The storage backend
            namespace: Namespace for organization
            llm_config: Configuration for LLM-assisted memory operations
        """
        self.persistence = persistence
        self.namespace = namespace
        self.llm_config = llm_config or {}
        self.logger = logging.getLogger("ProceduralMemory")
        
        # Ensure the storage system is initialized
        asyncio.create_task(self.persistence.initialize())
    
    async def save(self, item: Union[Procedure, Dict, Any], **metadata) -> str:
        """
        Save a procedural memory.
        
        Args:
            item: The procedure to save (Procedure object, dict, or pattern)
            **metadata: Additional metadata for storage
            
        Returns:
            A unique identifier for the saved procedure
        """
        # Convert to Procedure object if not already
        procedure = self._ensure_procedure(item)
        
        # Process with LLM if configured (for analysis, description generation, etc.)
        if self.llm_config and "save_processor" in self.llm_config:
            try:
                procedure = await self._process_with_llm("save", procedure)
            except Exception as e:
                self.logger.warning(f"LLM processing failed during save: {str(e)}")
        
        # Generate a unique ID if not provided
        memory_id = metadata.pop('id', procedure.name or f"proc_{uuid.uuid4().hex}")
        
        # Merge metadata
        combined_metadata = {
            "name": procedure.name,
            "description": procedure.description,
            "success_rate": procedure.success_rate,
            "usage_count": procedure.usage_count,
            "tags": procedure.tags,
            **procedure.metadata,
            **metadata
        }
        
        # Store in persistence layer
        await self.persistence.store(
            self.namespace,
            memory_id,
            procedure.to_dict(),
            combined_metadata
        )
        
        self.logger.debug(f"Saved procedural memory with ID {memory_id}")
        return memory_id
    
    async def retrieve(self, query: Any, limit: int = 5, **filters) -> List[Procedure]:
        """
        Retrieve procedural memories matching the query.
        
        Args:
            query: The query to match against
            limit: Maximum number of items to return
            **filters: Additional filters (min_success_rate, min_usage, tags, etc.)
            
        Returns:
            A list of procedures matching the query
        """
        # Process query with LLM if configured
        if self.llm_config and "query_processor" in self.llm_config:
            try:
                query = await self._process_with_llm("query", query)
            except Exception as e:
                self.logger.warning(f"LLM processing failed during query: {str(e)}")
        
        # Handle procedure-specific filters
        proc_filters = {}
        
        # Handle min_success_rate filter
        if "min_success_rate" in filters:
            threshold = float(filters.pop("min_success_rate"))
            proc_filters["success_rate_gte"] = threshold
        
        # Handle min_usage filter
        if "min_usage" in filters:
            threshold = int(filters.pop("min_usage"))
            proc_filters["usage_count_gte"] = threshold
        
        # Handle tag filtering
        if "tags" in filters and filters["tags"]:
            tags = filters.pop("tags")
            if isinstance(tags, str):
                tags = [tags]
            if isinstance(tags, list):
                proc_filters["tags"] = tags
        
        # Combine all filters
        combined_filters = {**proc_filters, **filters}
        
        # Search in persistence layer
        results = await self.persistence.search(
            self.namespace,
            query,
            limit,
            **combined_filters
        )
        
        # Convert results to Procedure objects
        procedures = []
        for item in results:
            try:
                if isinstance(item["value"], Procedure):
                    procedures.append(item["value"])
                elif isinstance(item["value"], dict):
                    procedures.append(Procedure.from_dict(item["value"]))
                else:
                    self.logger.warning(f"Unexpected item format: {type(item['value'])}")
            except Exception as e:
                self.logger.error(f"Error converting result to Procedure: {str(e)}")
        
        return procedures
    
    async def record_usage(self, id: str, success: bool) -> bool:
        """
        Record a usage of a procedure.
        
        Args:
            id: The identifier of the procedure
            success: Whether the procedure was successful
            
        Returns:
            Whether the update was successful
        """
        # Retrieve the existing procedure
        existing = await self.persistence.retrieve(self.namespace, id)
        if not existing:
            self.logger.warning(f"Cannot record usage for procedure with ID {id}: not found")
            return False
        
        try:
            # Convert to Procedure if needed
            if isinstance(existing, Procedure):
                procedure = existing
            elif isinstance(existing, dict):
                procedure = Procedure.from_dict(existing)
            else:
                self.logger.warning(f"Unexpected format for procedure with ID {id}")
                return False
            
            # Record the usage
            procedure.record_usage(success)
            
            # Update in persistence layer
            await self.persistence.store(
                self.namespace,
                id,
                procedure.to_dict(),
                {
                    "name": procedure.name,
                    "description": procedure.description,
                    "success_rate": procedure.success_rate,
                    "usage_count": procedure.usage_count,
                    "tags": procedure.tags,
                    **procedure.metadata
                }
            )
            
            self.logger.debug(f"Recorded usage for procedure {id}, success={success}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording usage for procedure {id}: {str(e)}")
            return False
    
    async def update(self, id: str, item: Union[Procedure, Dict, Any], **metadata) -> bool:
        """
        Update an existing procedural memory.
        
        Args:
            id: The identifier of the procedure to update
            item: The new procedure data
            **metadata: Additional metadata to update
            
        Returns:
            Whether the update was successful
        """
        # Check if the procedure exists
        existing_data = await self.persistence.retrieve(self.namespace, id)
        if not existing_data:
            self.logger.warning(f"Cannot update procedural memory with ID {id}: not found")
            return False
        
        # Convert to Procedure if it isn't already
        procedure = self._ensure_procedure(item)
        
        # Process with LLM if configured
        if self.llm_config and "update_processor" in self.llm_config:
            try:
                existing_procedure = (
                    existing_data if isinstance(existing_data, Procedure) 
                    else Procedure.from_dict(existing_data)
                )
                procedure = await self._process_with_llm("update", {
                    "existing": existing_procedure,
                    "update": procedure
                })
            except Exception as e:
                self.logger.warning(f"LLM processing failed during update: {str(e)}")
        
        # Merge metadata
        combined_metadata = {
            "name": procedure.name,
            "description": procedure.description,
            "success_rate": procedure.success_rate,
            "usage_count": procedure.usage_count,
            "tags": procedure.tags,
            **procedure.metadata,
            **metadata
        }
        
        # Store updated value
        await self.persistence.store(
            self.namespace,
            id,
            procedure.to_dict(),
            combined_metadata
        )
        
        self.logger.debug(f"Updated procedural memory with ID {id}")
        return True
    
    async def delete(self, id: str) -> bool:
        """
        Delete a procedural memory.
        
        Args:
            id: The identifier of the procedure to delete
            
        Returns:
            Whether the deletion was successful
        """
        result = await self.persistence.delete(self.namespace, id)
        if result:
            self.logger.debug(f"Deleted procedural memory with ID {id}")
        else:
            self.logger.warning(f"Failed to delete procedural memory with ID {id}")
        return result
    
    async def clear(self) -> None:
        """Clear all procedural memories."""
        await self.persistence.clear_namespace(self.namespace)
        self.logger.debug(f"Cleared all procedural memories in namespace {self.namespace}")
    
    def _ensure_procedure(self, item: Union[Procedure, Dict, Any]) -> Procedure:
        """
        Ensure the item is a Procedure object.
        
        Args:
            item: The item to convert to a Procedure
            
        Returns:
            The item as a Procedure object
        """
        if isinstance(item, Procedure):
            return item
        
        if isinstance(item, dict):
            if "name" in item and "pattern" in item:
                try:
                    return Procedure.from_dict(item)
                except Exception as e:
                    self.logger.warning(f"Error converting dict to Procedure: {str(e)}")
            else:
                # Assume it's just the pattern
                return Procedure(
                    name=f"procedure_{uuid.uuid4().hex[:8]}",
                    pattern=item
                )
        
        # For other types, create a new Procedure with the item as pattern
        return Procedure(
            name=f"procedure_{uuid.uuid4().hex[:8]}",
            pattern={"content": item}
        )
    
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