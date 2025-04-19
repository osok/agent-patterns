"""Persistence backends for memory storage."""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



from .in_memory import InMemoryPersistence
from .file_system import FileSystemPersistence
from .vector_store import VectorStorePersistence

__all__ = [
    "InMemoryPersistence",
    "FileSystemPersistence",
    "VectorStorePersistence"
] 