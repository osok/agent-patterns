"""File system persistence backend for memory storage."""

import os
import json
import asyncio
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, TypeVar, Union, cast
import logging
from difflib import SequenceMatcher

from ..base import MemoryPersistence

T = TypeVar('T')  # Memory item type

class FileSystemPersistence(MemoryPersistence[T]):
    """
    File system implementation of memory persistence.
    
    This implementation stores data in JSON files on the local file system.
    Each namespace is a separate directory with key-based files within.
    """
    
    def __init__(self, base_dir: Union[str, Path], encoding: str = "utf-8"):
        """
        Initialize the file system persistence layer.
        
        Args:
            base_dir: Base directory for storing files
            encoding: Text encoding for files (default: utf-8)
        """
        self.base_dir = Path(base_dir) if isinstance(base_dir, str) else base_dir
        self.encoding = encoding
        self._initialized = False
        self.logger = logging.getLogger("FileSystemPersistence")
    
    async def initialize(self) -> None:
        """Initialize the persistence layer by creating the base directory."""
        os.makedirs(self.base_dir, exist_ok=True)
        self._initialized = True
        self.logger.debug(f"Initialized file system persistence at {self.base_dir}")
    
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
        
        # Create namespace directory if it doesn't exist
        namespace_dir = self.base_dir / namespace
        os.makedirs(namespace_dir, exist_ok=True)
        
        # Create the file path
        file_path = namespace_dir / f"{key}.json"
        
        # Create the content to store
        data = {
            "value": value,
            "metadata": metadata or {}
        }
        
        # Write to file
        try:
            async with asyncio.Lock():
                with open(file_path, 'w', encoding=self.encoding) as f:
                    json.dump(data, f, indent=2, default=self._json_serialize)
            self.logger.debug(f"Stored item at {file_path}")
        except Exception as e:
            self.logger.error(f"Error storing item at {file_path}: {str(e)}")
            raise
    
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
        
        # Create the file path
        file_path = self.base_dir / namespace / f"{key}.json"
        
        # Check if file exists
        if not file_path.exists():
            return None
        
        # Read from file
        try:
            async with asyncio.Lock():
                with open(file_path, 'r', encoding=self.encoding) as f:
                    data = json.load(f)
            
            return cast(T, data["value"])
        except Exception as e:
            self.logger.error(f"Error retrieving item from {file_path}: {str(e)}")
            return None
    
    async def search(self, namespace: str, query: Any, limit: int = 10, **filters) -> List[Dict]:
        """
        Search for values matching a query.
        
        This is a simple implementation that loads all files in a namespace
        and performs an in-memory search. For large datasets, consider using
        a more efficient storage mechanism like a vector database.
        
        Args:
            namespace: The namespace to search in
            query: The query string to match against
            limit: Maximum number of results
            **filters: Additional metadata filters to apply
            
        Returns:
            A list of matching items with metadata and id
        """
        self._ensure_initialized()
        
        namespace_dir = self.base_dir / namespace
        
        # Check if namespace directory exists
        if not namespace_dir.exists() or not namespace_dir.is_dir():
            return []
        
        query_str = str(query)
        results = []
        
        # Iterate through all files in the namespace
        for file_path in namespace_dir.glob("*.json"):
            try:
                # Get key from filename
                key = file_path.stem
                
                # Read the file
                async with asyncio.Lock():
                    with open(file_path, 'r', encoding=self.encoding) as f:
                        data = json.load(f)
                
                # Check if matches filters
                if not self._matches_filters(data["metadata"], filters):
                    continue
                
                # Calculate similarity
                value_str = str(data["value"])
                similarity = SequenceMatcher(None, query_str, value_str).ratio()
                
                results.append({
                    "id": key,
                    "value": data["value"],
                    "metadata": data["metadata"],
                    "score": similarity
                })
            except Exception as e:
                self.logger.error(f"Error reading item from {file_path}: {str(e)}")
                continue
        
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
        
        # Create the file path
        file_path = self.base_dir / namespace / f"{key}.json"
        
        # Check if file exists
        if not file_path.exists():
            return False
        
        # Delete the file
        try:
            async with asyncio.Lock():
                os.remove(file_path)
            self.logger.debug(f"Deleted item at {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting item at {file_path}: {str(e)}")
            return False
    
    async def clear_namespace(self, namespace: str) -> None:
        """
        Clear all data in a namespace.
        
        Args:
            namespace: The namespace to clear
        """
        self._ensure_initialized()
        
        namespace_dir = self.base_dir / namespace
        
        # Check if namespace directory exists
        if not namespace_dir.exists() or not namespace_dir.is_dir():
            return
        
        # Delete all files in the namespace
        try:
            async with asyncio.Lock():
                for file_path in namespace_dir.glob("*.json"):
                    os.remove(file_path)
            self.logger.debug(f"Cleared namespace {namespace}")
        except Exception as e:
            self.logger.error(f"Error clearing namespace {namespace}: {str(e)}")
            raise
    
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
    
    def _json_serialize(self, obj: Any) -> Any:
        """Custom JSON serializer for objects not serializable by default."""
        try:
            return obj.__dict__
        except AttributeError:
            return str(obj) 