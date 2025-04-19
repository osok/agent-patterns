"""Episodic memory implementation for storing past experiences."""

import uuid
import json
from typing import Dict, List, Any, Optional, TypeVar, Union, cast
import logging
from datetime import datetime

from .base import BaseMemory, MemoryPersistence

T = TypeVar('T')  # Memory item type

class Episode:
    """Represents a single episode or experience."""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only


    
    def __init__(
        self,
        content: Any,
        timestamp: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an episode.
        
        Args:
            content: The main content of the episode
            timestamp: When the episode occurred
            tags: Optional tags for categorization
            metadata: Additional metadata about the episode
        """
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.tags = tags or []
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for storage."""
        return {
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Episode':
        """Create an episode from a dictionary."""
        timestamp = datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else None
        return cls(
            content=data["content"],
            timestamp=timestamp,
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )
    
    def __str__(self) -> str:
        """String representation of the episode."""
        return f"Episode({self.content}, {self.timestamp.isoformat()})"

class EpisodicMemory(BaseMemory[Episode]):
    """
    Stores past experiences as a sequence of episodes.
    
    Episodic memories represent:
    - Conversation history
    - Past interactions
    - Personal experiences
    - Historical events
    
    Each memory is timestamped and can be retrieved chronologically
    or by content similarity.
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
        self.persistence.initialize()
    
    def save(self, item: Any, **metadata) -> str:
        """
        Save an episode to memory.
        
        Args:
            item: The content to save (can be any serializable type)
            **metadata: Additional metadata for the episode
            
        Returns:
            A unique identifier for the saved episode
        """
        # If already an Episode object, use it directly
        if isinstance(item, Episode):
            episode = item
        else:
            # Get any special fields from metadata
            tags = metadata.pop("tags", [])
            timestamp = metadata.pop("timestamp", None)
            
            # Create a new episode
            episode = Episode(
                content=item,
                timestamp=timestamp,
                tags=tags,
                metadata=metadata
            )
        
        # Process with LLM if configured
        if self.llm_config and "save_processor" in self.llm_config:
            try:
                processed_data = self._process_with_llm("save", episode.to_dict())
                episode = Episode.from_dict(processed_data)
            except Exception as e:
                self.logger.warning(f"LLM processing failed during save: {str(e)}")
        
        # Generate a unique ID if not provided
        memory_id = metadata.pop('id', f"ep_{uuid.uuid4().hex}")
        
        # Store in persistence layer
        self.persistence.store(
            self.namespace,
            memory_id,
            episode.to_dict(),
            metadata
        )
        
        self.logger.debug(f"Saved episode with ID {memory_id}")
        return memory_id
    
    def retrieve(self, query: Any, limit: int = 5, **filters) -> List[Episode]:
        """
        Retrieve episodes matching the query.
        
        Args:
            query: The query to match against
            limit: Maximum number of episodes to return
            **filters: Additional filters to apply
            
        Returns:
            A list of episodes matching the query
        """
        # Process query with LLM if configured
        if self.llm_config and "query_processor" in self.llm_config:
            try:
                query = self._process_with_llm("query", query)
            except Exception as e:
                self.logger.warning(f"LLM processing failed during query: {str(e)}")
        
        # Search in persistence layer
        results = self.persistence.search(
            self.namespace,
            query,
            limit,
            **filters
        )
        
        # Convert results back to Episode objects
        episodes = []
        for item in results:
            try:
                episode = Episode.from_dict(item["value"])
                episodes.append(episode)
            except Exception as e:
                self.logger.warning(f"Error parsing episode: {str(e)}")
        
        return episodes
    
    def update(self, id: str, item: Any, **metadata) -> bool:
        """
        Update an existing episode.
        
        Args:
            id: The identifier of the episode to update
            item: The new episode content
            **metadata: Additional metadata to update
            
        Returns:
            Whether the update was successful
        """
        # Get existing episode
        existing = self.persistence.retrieve(self.namespace, id)
        if not existing:
            self.logger.warning(f"Cannot update episode with ID {id}: not found")
            return False
        
        # Convert to Episode if not already
        if isinstance(item, Episode):
            episode = item
        else:
            # Get any special fields from metadata
            tags = metadata.pop("tags", existing.get("tags", []))
            timestamp_str = metadata.pop("timestamp", existing.get("timestamp"))
            
            # Parse timestamp if string
            if isinstance(timestamp_str, str):
                timestamp = datetime.fromisoformat(timestamp_str)
            else:
                timestamp = timestamp_str or datetime.now()
            
            # Create an updated episode
            episode = Episode(
                content=item,
                timestamp=timestamp,
                tags=tags,
                metadata=metadata or existing.get("metadata", {})
            )
        
        # Process with LLM if configured
        if self.llm_config and "update_processor" in self.llm_config:
            try:
                processed_data = self._process_with_llm("update", {
                    "existing": existing,
                    "update": episode.to_dict()
                })
                episode = Episode.from_dict(processed_data)
            except Exception as e:
                self.logger.warning(f"LLM processing failed during update: {str(e)}")
        
        # Store updated value
        self.persistence.store(
            self.namespace,
            id,
            episode.to_dict(),
            metadata
        )
        
        self.logger.debug(f"Updated episode with ID {id}")
        return True
    
    def delete(self, id: str) -> bool:
        """
        Delete an episode.
        
        Args:
            id: The identifier of the episode to delete
            
        Returns:
            Whether the deletion was successful
        """
        result = self.persistence.delete(self.namespace, id)
        if result:
            self.logger.debug(f"Deleted episode with ID {id}")
        else:
            self.logger.warning(f"Failed to delete episode with ID {id}")
        return result
    
    def clear(self) -> None:
        """Clear all episodes."""
        self.persistence.clear_namespace(self.namespace)
        self.logger.debug(f"Cleared all episodes in namespace {self.namespace}")
    
    def _process_with_llm(self, operation: str, data: Any) -> Any:
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
        return processor(data) 