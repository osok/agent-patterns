"""
Example demonstrating the use of memory in agent patterns with Celery.

This example shows how to set up a ReAct agent with semantic, episodic, and procedural memory
using Celery as the task executor instead of asyncio.
"""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



import os
import sys
import time
from dotenv import load_dotenv
import logging
from pprint import pprint

# Add the parent directory to sys.path to import agent_patterns
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import utility for model configuration
from examples.utils.model_config import get_llm_configs

# Load environment variables
load_dotenv()

# Import memory task functions
from agent_patterns.core.memory.tasks import (
    initialize_persistence,
    save_memory,
    retrieve_memory
)
from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.celery_app import celery_app

# Define a simple tool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_wiki_tool():
    """Create a Wikipedia search tool."""
    wiki = WikipediaAPIWrapper()
    return WikipediaQueryRun(api_wrapper=wiki)

def setup_memory():
    """Set up memory using Celery tasks."""
    # Initialize persistence
    persistence_task = initialize_persistence.delay(persistence_type="in_memory")
    
    # Wait for persistence to be initialized
    persistence_result = persistence_task.get(timeout=30)
    
    if not persistence_result:
        raise RuntimeError("Failed to initialize persistence layer")
    
    logger.info("Persistence layer initialized successfully")
    
    # Prepopulate memory with some semantic memories
    save_memory.delay(
        persistence_type="in_memory",
        memory_type="semantic",
        namespace="user_semantic",
        content={"entity": "user", "attribute": "name", "value": "Alice"}
    ).get(timeout=30)
    
    save_memory.delay(
        persistence_type="in_memory",
        memory_type="semantic",
        namespace="user_semantic",
        content={"entity": "user", "attribute": "interests", "value": ["AI", "astronomy", "history"]}
    ).get(timeout=30)
    
    save_memory.delay(
        persistence_type="in_memory",
        memory_type="semantic",
        namespace="user_semantic",
        content={"entity": "user", "attribute": "preferred_language", "value": "simple explanations"}
    ).get(timeout=30)
    
    # Add a procedural memory for explaining concepts
    save_memory.delay(
        persistence_type="in_memory",
        memory_type="procedural",
        namespace="user_procedural",
        content={
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
        }
    ).get(timeout=30)
    
    logger.info("Memory populated with initial data")

def run_agent_example():
    """Run the memory example with Celery."""
    try:
        # Set up memory
        setup_memory()
        
        # Load LLM configs from environment variables
        llm_configs = get_llm_configs()
        logger.info("Using model configuration from environment variables")
        
        # Create tools
        wiki_tool = get_wiki_tool()
        
        # Create ReAct agent with memory
        # Note: The ReActAgent would need to be modified to use Celery tasks
        # This is just a placeholder showing how it would be structured
        agent = ReActAgent(
            llm_configs=llm_configs,
            tools=[wiki_tool],
            # Note: In a real implementation, we would pass a Celery-aware memory manager
            # For now, we're just showing the concept
            memory_config={
                "persistence_type": "in_memory",
                "semantic_namespace": "user_semantic",
                "episodic_namespace": "user_episodic",
                "procedural_namespace": "user_procedural",
                "use_celery": True  # Flag to indicate use of Celery tasks
            }
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
        
        # Use Celery task to retrieve memories
        episodes_task = retrieve_memory.delay(
            persistence_type="in_memory",
            memory_type="episodic",
            namespace="user_episodic",
            query="",
            limit=10
        )
        
        episodes = episodes_task.get(timeout=30)
        for i, episode in enumerate(episodes):
            print(f"{i+1}. {episode}")
        
        print("\nSemantic memories:")
        facts_task = retrieve_memory.delay(
            persistence_type="in_memory",
            memory_type="semantic",
            namespace="user_semantic",
            query="",
            limit=10
        )
        
        facts = facts_task.get(timeout=30)
        for i, fact in enumerate(facts):
            print(f"{i+1}. {fact}")
        
        print("\nProcedural memories:")
        procedures_task = retrieve_memory.delay(
            persistence_type="in_memory",
            memory_type="procedural",
            namespace="user_procedural",
            query="",
            limit=10
        )
        
        procedures = procedures_task.get(timeout=30)
        for i, proc in enumerate(procedures):
            print(f"{i+1}. {proc}")
        
    except Exception as e:
        logger.error(f"Error in agent example: {str(e)}")
        raise

def main():
    """Run the memory example."""
    # Ensure Celery worker is running
    logger.info("Checking Celery worker status...")
    
    try:
        # Simple check if worker is running
        # In production, you would use more robust methods
        i = celery_app.control.inspect()
        if not i.ping():
            logger.warning(
                "No Celery workers appear to be running. "
                "Please start a worker with: celery -A agent_patterns.core.celery_app worker --loglevel=info"
            )
            return
        
        logger.info("Celery worker is running")
        run_agent_example()
        
    except Exception as e:
        logger.error(f"Error checking Celery worker status: {str(e)}")
        logger.warning(
            "Could not connect to Celery broker. "
            "Please ensure Redis is running and Celery worker is started."
        )

if __name__ == "__main__":
    main() 