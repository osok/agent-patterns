"""
Example demonstrating the use of memory in agent patterns.

This example shows how to set up a ReAct agent with semantic, episodic, and procedural memory.
"""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging
from pprint import pprint

# Add the parent directory to sys.path to import agent_patterns
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all memory types
from agent_patterns.core.memory import (
    CompositeMemory,
    SemanticMemory,
    EpisodicMemory,
    ProceduralMemory
)

# Import memory persistence for storage
from agent_patterns.core.memory.persistence import InMemoryPersistence

# Import utility for model configuration
from examples.utils.model_config import get_llm_configs

# Create a ReAct agent
from agent_patterns.patterns.re_act_agent import ReActAgent

# Define a simple tool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_memory():
    """Set up memory with semantic, episodic, and procedural components."""
    # Create a shared in-memory persistence layer
    persistence = InMemoryPersistence()
    persistence.initialize()
    
    # Create separate memory instances
    semantic_memory = SemanticMemory(persistence, namespace="user_semantic")
    episodic_memory = EpisodicMemory(persistence, namespace="user_episodic")
    procedural_memory = ProceduralMemory(persistence, namespace="user_procedural")
    
    # Combine them into a composite memory
    memory = CompositeMemory({
        "semantic": semantic_memory,
        "episodic": episodic_memory,
        "procedural": procedural_memory
    })
    
    # Prepopulate with some semantic memories
    memory.save_to("semantic", {
        "entity": "user",
        "attribute": "name",
        "value": "Alice"
    })
    
    memory.save_to("semantic", {
        "entity": "user",
        "attribute": "interests",
        "value": ["AI", "astronomy", "history"]
    })
    
    memory.save_to("semantic", {
        "entity": "user", 
        "attribute": "preferred_language",
        "value": "simple explanations"
    })
    
    # Add a procedural memory for explaining concepts
    memory.save_to("procedural", {
        "name": "explain_concept",
        "pattern": {
            "template": """When explaining {concept}, remember to:
1. Start with a simple analogy
2. Define key terms clearly
3. Provide concrete examples
4. Relate to common knowledge
5. Use simple language"""
        },
        "description": "Template for explaining complex concepts in simple terms",
        "tags": ["explanation", "teaching"]
    })
    
    return memory, persistence

def get_wiki_tool():
    """Create a Wikipedia search tool."""
    wiki = WikipediaAPIWrapper()
    return WikipediaQueryRun(api_wrapper=wiki)

def main_sync():
    """Run the memory example."""
    memory, persistence = setup_memory()
    
    # Load LLM configs from environment variables
    llm_configs = get_llm_configs()
    logger.info("Using model configuration from environment variables")
    
    # Create tools
    wiki_tool = get_wiki_tool()
    
    # Create ReAct agent with memory
    agent = ReActAgent(
        llm_configs=llm_configs,
        tools=[wiki_tool],
        memory=memory
    )
    
    # Run a series of interactions
    print("\n======= FIRST INTERACTION =======")
    print("User: Tell me about black holes")
    
    result = agent.run("Tell me about black holes")
    print("\nAgent response:")
    print(result["output"])
    
    # Run a second query that can use the memory of the first interaction
    print("\n======= SECOND INTERACTION =======")
    print("User: What were we just talking about?")
    
    result = agent.run("What were we just talking about?")
    print("\nAgent response:")
    print(result["output"])
    
    # Run a third query that uses semantic memory
    print("\n======= THIRD INTERACTION =======")
    print("User: Tell me about something related to my interests")
    
    result = agent.run("Tell me about something related to my interests")
    print("\nAgent response:")
    print(result["output"])
    
    # Check what's in episodic memory
    print("\n======= MEMORY CONTENTS =======")
    print("Episodic memories:")
    episodes = memory.retrieve_from("episodic", "", limit=10)
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode}")
    
    print("\nSemantic memories:")
    facts = memory.retrieve_from("semantic", "", limit=10)
    for i, fact in enumerate(facts):
        print(f"{i+1}. {fact}")
    
    print("\nProcedural memories:")
    procedures = memory.retrieve_from("procedural", "", limit=10)
    for i, proc in enumerate(procedures):
        print(f"{i+1}. {proc}")

def main():
    """Entry point."""
    main_sync()

if __name__ == "__main__":
    main() 