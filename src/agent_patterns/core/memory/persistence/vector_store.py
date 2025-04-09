"""Vector store persistence backend for memory storage."""

import uuid
import json
import asyncio
from typing import Dict, List, Any, Optional, TypeVar, Callable, Union, cast
import logging

from ..base import MemoryPersistence

T = TypeVar('T')  # Memory item type

class VectorStorePersistence(MemoryPersistence[T]):
    """
    Vector store implementation of memory persistence.
    
    This implementation uses a vector database for semantic search.
    It requires a compatible vector store and an embedding function.
    """
    
    def __init__(
        self, 
        vector_store: Any, 
        embedding_function: Callable[[Any], List[float]],
        text_key: str = None
    ):
        """
        Initialize with a vector store and embedding function.
        
        Args:
            vector_store: The vector database client (langchain compatible)
            embedding_function: Function to convert items to vectors
            text_key: For dict items, specifies which key to use for text content (optional)
        """
        self.vector_store = vector_store
        self.embedding_function = embedding_function
        self.text_key = text_key
        self._initialized = False
        self.logger = logging.getLogger("VectorStorePersistence")
    
    async def initialize(self) -> None:
        """Initialize the vector store."""
        # Most vector stores don't need explicit initialization
        self._initialized = True
        self.logger.debug("Initialized vector store persistence")
    
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
        
        metadata = metadata or {}
        metadata["_id"] = key
        
        # Determine text for embedding
        text_for_embedding = self._extract_text(value)
        
        # Generate embedding
        try:
            embedding = await self._get_embedding(text_for_embedding)
        except Exception as e:
            self.logger.error(f"Error generating embedding: {str(e)}")
            raise
        
        # Store in vector database
        try:
            # Use async when available, otherwise use synchronous
            if hasattr(self.vector_store, "aadd_documents"):
                await self.vector_store.aadd_documents(
                    texts=[text_for_embedding],
                    metadatas=[{"namespace": namespace, **metadata}],
                    embeddings=[embedding],
                    ids=[f"{namespace}:{key}"]
                )
            else:
                # Fall back to synchronous API
                self.vector_store.add_documents(
                    texts=[text_for_embedding],
                    metadatas=[{"namespace": namespace, **metadata}],
                    embeddings=[embedding],
                    ids=[f"{namespace}:{key}"]
                )
            
            self.logger.debug(f"Stored item with key {key} in namespace {namespace}")
        except Exception as e:
            self.logger.error(f"Error storing in vector store: {str(e)}")
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
        
        # Construct a filter for exact ID matching
        filter_dict = {"namespace": namespace, "_id": key}
        
        try:
            # Use async when available, otherwise use synchronous
            if hasattr(self.vector_store, "asimilarity_search"):
                docs = await self.vector_store.asimilarity_search(
                    query="",  # Empty query for exact match via filter
                    k=1,
                    filter=filter_dict
                )
            else:
                # Fall back to synchronous API
                docs = self.vector_store.similarity_search(
                    query="",  # Empty query for exact match via filter
                    k=1,
                    filter=filter_dict
                )
            
            if not docs:
                return None
            
            # Parse the stored value
            doc = docs[0]
            
            if hasattr(doc, "metadata") and "_value" in doc.metadata:
                # If value was stored in metadata, retrieve it
                try:
                    value_json = doc.metadata["_value"]
                    if isinstance(value_json, str):
                        return cast(T, json.loads(value_json))
                    return cast(T, value_json)
                except:
                    # If parsing fails, return the document text as a fallback
                    return cast(T, doc.page_content)
            
            # Default: return document text
            return cast(T, doc.page_content)
            
        except Exception as e:
            self.logger.error(f"Error retrieving from vector store: {str(e)}")
            return None
    
    async def search(self, namespace: str, query: Any, limit: int = 10, **filters) -> List[Dict]:
        """
        Search for values matching a query.
        
        Args:
            namespace: The namespace to search in
            query: The query to match against
            limit: Maximum number of results
            **filters: Additional filters to apply
            
        Returns:
            A list of matching items with metadata and id
        """
        self._ensure_initialized()
        
        # Convert query to string if it's not already
        query_text = self._extract_text(query)
        
        # Generate query embedding
        try:
            embedding = await self._get_embedding(query_text)
        except Exception as e:
            self.logger.error(f"Error generating query embedding: {str(e)}")
            return []
        
        # Construct search filter
        search_filter = {"namespace": namespace}
        for key, value in filters.items():
            search_filter[key] = value
        
        try:
            # Use async when available, otherwise use synchronous
            if hasattr(self.vector_store, "asimilarity_search_by_vector_with_relevance_scores"):
                results = await self.vector_store.asimilarity_search_by_vector_with_relevance_scores(
                    embedding=embedding,
                    k=limit,
                    filter=search_filter
                )
            else:
                # Fall back to synchronous API
                results = self.vector_store.similarity_search_by_vector_with_relevance_scores(
                    embedding=embedding,
                    k=limit,
                    filter=search_filter
                )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                if not hasattr(doc, "metadata"):
                    continue
                
                metadata = doc.metadata.copy()
                
                # Extract namespace and ID
                namespace = metadata.pop("namespace", None)
                key = metadata.pop("_id", None)
                
                if key is None:
                    # If no key is found, skip this result
                    continue
                
                # Extract value
                value = None
                if "_value" in metadata:
                    try:
                        value_json = metadata.pop("_value")
                        if isinstance(value_json, str):
                            value = json.loads(value_json)
                        else:
                            value = value_json
                    except:
                        value = doc.page_content
                else:
                    value = doc.page_content
                
                formatted_results.append({
                    "id": key,
                    "value": value,
                    "metadata": metadata,
                    "score": score
                })
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error searching vector store: {str(e)}")
            return []
    
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
        
        try:
            # Use async when available, otherwise use synchronous
            if hasattr(self.vector_store, "adelete"):
                await self.vector_store.adelete(
                    ids=[f"{namespace}:{key}"]
                )
            else:
                # Fall back to synchronous API
                self.vector_store.delete(
                    ids=[f"{namespace}:{key}"]
                )
            
            self.logger.debug(f"Deleted item with key {key} from namespace {namespace}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting from vector store: {str(e)}")
            return False
    
    async def clear_namespace(self, namespace: str) -> None:
        """
        Clear all data in a namespace.
        
        Args:
            namespace: The namespace to clear
        """
        self._ensure_initialized()
        
        try:
            # Use async when available, otherwise use synchronous
            if hasattr(self.vector_store, "adelete"):
                await self.vector_store.adelete(
                    filter={"namespace": namespace}
                )
            else:
                # Fall back to synchronous API
                self.vector_store.delete(
                    filter={"namespace": namespace}
                )
            
            self.logger.debug(f"Cleared namespace {namespace}")
        except Exception as e:
            self.logger.error(f"Error clearing namespace {namespace}: {str(e)}")
    
    def _ensure_initialized(self) -> None:
        """Ensure the persistence layer is initialized."""
        if not self._initialized:
            raise RuntimeError("Persistence layer not initialized. Call initialize() first.")
    
    def _extract_text(self, value: Any) -> str:
        """Extract text for embedding from a value."""
        if isinstance(value, str):
            return value
        elif isinstance(value, dict) and self.text_key and self.text_key in value:
            return str(value[self.text_key])
        else:
            # Try JSON serialization for structured data
            try:
                return json.dumps(value)
            except:
                return str(value)
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text, handling both sync and async embedding functions."""
        if asyncio.iscoroutinefunction(self.embedding_function):
            return await self.embedding_function(text)
        else:
            # Run in thread pool if it's a synchronous function
            return await asyncio.to_thread(self.embedding_function, text) 