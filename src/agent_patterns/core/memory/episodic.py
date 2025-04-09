"""Episodic memory implementation for storing sequences of past events."""

import uuid
import json
import asyncio
import datetime
from typing import Dict, List, Any, Optional, TypeVar, Union, cast
import logging

from .base import BaseMemory, MemoryPersistence

class Episode:
    """Represents a single episode or event in episodic memory."""
    
    def __init__(
        self,
        content: Any,
        timestamp: Optional[datetime.datetime] = None,
        importance: float = 0.5,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize an episode.
        
        Args:
            content: The content of the episode
            timestamp: When the episode occurred (defaults to now)
            importance: Subjective importance of the episode (0.0 to 1.0)
            tags: List of tags for categorization
            metadata: Additional metadata for the episode
        """
        self.content = content
        self.timestamp = timestamp or datetime.datetime.now()
        self.importance = max(0.0, min(1.0, importance))  # Clamp to [0, 1]
        self.tags = tags or []
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for storage."""
        return {
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance,
            "tags": self.tags,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Episode':
        """Create an episode from a dictionary."""
        # Convert timestamp string back to datetime
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.datetime.fromisoformat(timestamp)
            except ValueError:
                timestamp = datetime.datetime.now()
        
        return cls(
            content=data.get("content"),
            timestamp=timestamp,
            importance=data.get("importance", 0.5),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )


class EpisodicMemory(BaseMemory[Episode]):
    """
    Stores sequences of past events and interactions.
    
    Episodic memories represent:
    - Conversations and interactions
    - Time-ordered experiences
    - Events with temporal context
    
    Uses a vector store with temporal metadata for efficient retrieval.
    """
    
    def __init__(
        self,
        persistence: MemoryPersistence,
        namespace: str = "episodic",
        llm_config: Optional[Dict] = None
    ):
        """
        Initialize episodic memory.
        
        Args:
            persistence: The storage backend
            namespace: Namespace for organization
            llm_config: Configuration for LLM-assisted memory operations
        """
        self.persistence = persistence
        self.namespace = namespace
        self.llm_config = llm_config or {}
        self.logger = logging.getLogger("EpisodicMemory")
        
        # Ensure the storage system is initialized
        asyncio.create_task(self.persistence.initialize())
    
    async def save(self, item: Union[Episode, Dict, Any], **metadata) -> str:
        """
        Save an episodic memory.
        
        Args:
            item: The episode to save (Episode object, dict, or raw content)
            **metadata: Additional metadata for storage
            
        Returns:
            A unique identifier for the saved episode
        """
        # Convert to Episode object if not already
        episode = self._ensure_episode(item)
        
        # Process with LLM if configured (for importance scoring, tagging, etc.)
        if self.llm_config and "save_processor" in self.llm_config:
            try:
                episode = await self._process_with_llm("save", episode)
            except Exception as e:
                self.logger.warning(f"LLM processing failed during save: {str(e)}")
        
        # Generate a unique ID if not provided
        memory_id = metadata.pop('id', f"ep_{uuid.uuid4().hex}")
        
        # Merge metadata
        combined_metadata = {
            "timestamp": episode.timestamp.isoformat(),
            "importance": episode.importance,
            "tags": episode.tags,
            **episode.metadata,
            **metadata
        }
        
        # Store in persistence layer
        await self.persistence.store(
            self.namespace,
            memory_id,
            episode.to_dict(),
            combined_metadata
        )
        
        self.logger.debug(f"Saved episodic memory with ID {memory_id}")
        return memory_id
    
    async def retrieve(self, query: Any, limit: int = 5, **filters) -> List[Episode]:
        """
        Retrieve episodic memories matching the query.
        
        Args:
            query: The query to match against
            limit: Maximum number of items to return
            **filters: Additional filters (time_range, tags, importance, etc.)
            
        Returns:
            A list of episodes matching the query
        """
        # Process query with LLM if configured
        if self.llm_config and "query_processor" in self.llm_config:
            try:
                query = await self._process_with_llm("query", query)
            except Exception as e:
                self.logger.warning(f"LLM processing failed during query: {str(e)}")
        
        # Handle time-based filters
        time_filters = {}
        
        # Handle time_range filter
        if "time_range" in filters:
            time_range = filters.pop("time_range")
            if isinstance(time_range, tuple) and len(time_range) == 2:
                start, end = time_range
                if start:
                    time_filters["timestamp_gte"] = start.isoformat() if hasattr(start, "isoformat") else start
                if end:
                    time_filters["timestamp_lte"] = end.isoformat() if hasattr(end, "isoformat") else end
        
        # Handle importance_threshold
        if "importance_threshold" in filters:
            threshold = float(filters.pop("importance_threshold"))
            time_filters["importance_gte"] = threshold
        
        # Handle tag filtering
        if "tags" in filters and filters["tags"]:
            tags = filters.pop("tags")
            if isinstance(tags, str):
                tags = [tags]
            if isinstance(tags, list):
                time_filters["tags"] = tags
        
        # Combine all filters
        combined_filters = {**time_filters, **filters}
        
        # Search in persistence layer
        results = await self.persistence.search(
            self.namespace,
            query,
            limit,
            **combined_filters
        )
        
        # Convert results to Episode objects
        episodes = []
        for item in results:
            try:
                if isinstance(item["value"], Episode):
                    episodes.append(item["value"])
                elif isinstance(item["value"], dict):
                    episodes.append(Episode.from_dict(item["value"]))
                else:
                    self.logger.warning(f"Unexpected item format: {type(item['value'])}")
            except Exception as e:
                self.logger.error(f"Error converting result to Episode: {str(e)}")
        
        return episodes
    
    async def retrieve_by_timerange(
        self, 
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        limit: int = 100
    ) -> List[Episode]:
        """
        Retrieve episodes within a specific time range.
        
        Args:
            start_time: The start time (inclusive)
            end_time: The end time (inclusive)
            limit: Maximum number of episodes to retrieve
            
        Returns:
            List of episodes within the time range, ordered by timestamp
        """
        filters = {}
        if start_time:
            filters["timestamp_gte"] = start_time.isoformat()
        if end_time:
            filters["timestamp_lte"] = end_time.isoformat()
        
        # Use a generic query that will match most episodes,
        # relying primarily on the time filters
        results = await self.persistence.search(
            self.namespace,
            "",
            limit,
            **filters
        )
        
        # Convert results to Episode objects
        episodes = []
        for item in results:
            try:
                if isinstance(item["value"], dict):
                    episodes.append(Episode.from_dict(item["value"]))
                else:
                    self.logger.warning(f"Unexpected item format: {type(item['value'])}")
            except Exception as e:
                self.logger.error(f"Error converting result to Episode: {str(e)}")
        
        # Sort by timestamp
        episodes.sort(key=lambda ep: ep.timestamp)
        return episodes
    
    async def update(self, id: str, item: Union[Episode, Dict, Any], **metadata) -> bool:
        """
        Update an existing episodic memory.
        
        Args:
            id: The identifier of the episode to update
            item: The new episode data
            **metadata: Additional metadata to update
            
        Returns:
            Whether the update was successful
        """
        # Check if the episode exists
        existing_data = await self.persistence.retrieve(self.namespace, id)
        if not existing_data:
            self.logger.warning(f"Cannot update episodic memory with ID {id}: not found")
            return False
        
        # Convert to Episode if it isn't already
        episode = self._ensure_episode(item)
        
        # Process with LLM if configured
        if self.llm_config and "update_processor" in self.llm_config:
            try:
                existing_episode = Episode.from_dict(existing_data)
                episode = await self._process_with_llm("update", {
                    "existing": existing_episode,
                    "update": episode
                })
            except Exception as e:
                self.logger.warning(f"LLM processing failed during update: {str(e)}")
        
        # Merge metadata
        combined_metadata = {
            "timestamp": episode.timestamp.isoformat(),
            "importance": episode.importance,
            "tags": episode.tags,
            **episode.metadata,
            **metadata
        }
        
        # Store updated value
        await self.persistence.store(
            self.namespace,
            id,
            episode.to_dict(),
            combined_metadata
        )
        
        self.logger.debug(f"Updated episodic memory with ID {id}")
        return True
    
    async def delete(self, id: str) -> bool:
        """
        Delete an episodic memory.
        
        Args:
            id: The identifier of the episode to delete
            
        Returns:
            Whether the deletion was successful
        """
        result = await self.persistence.delete(self.namespace, id)
        if result:
            self.logger.debug(f"Deleted episodic memory with ID {id}")
        else:
            self.logger.warning(f"Failed to delete episodic memory with ID {id}")
        return result
    
    async def clear(self) -> None:
        """Clear all episodic memories."""
        await self.persistence.clear_namespace(self.namespace)
        self.logger.debug(f"Cleared all episodic memories in namespace {self.namespace}")
    
    def _ensure_episode(self, item: Union[Episode, Dict, Any]) -> Episode:
        """
        Ensure the item is an Episode object.
        
        Args:
            item: The item to convert to an Episode
            
        Returns:
            The item as an Episode object
        """
        if isinstance(item, Episode):
            return item
        
        if isinstance(item, dict):
            try:
                return Episode.from_dict(item)
            except Exception as e:
                self.logger.warning(f"Error converting dict to Episode: {str(e)}")
        
        # For other types, create a new Episode with the item as content
        return Episode(content=item)
    
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