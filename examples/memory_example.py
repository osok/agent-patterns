"""
Example demonstrating the use of memory in agent patterns.

This example shows how to set up a ReAct agent with semantic, episodic, and procedural memory.
"""

import os
import sys
from dotenv import load_dotenv
from pprint import pprint
import asyncio

# Add the parent directory to sys.path to import agent_patterns
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.memory import (
    SemanticMemory,
    EpisodicMemory,
    ProceduralMemory,
    CompositeMemory
)
from agent_patterns.core.memory.persistence import (
    InMemoryPersistence
)

# Define a simple tool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

def get_wiki_tool():
    """Create a Wikipedia search tool."""
    wiki = WikipediaAPIWrapper()
    return WikipediaQueryRun(api_wrapper=wiki)

def main():
    """Run the memory example."""
    # Create persistence backend (in-memory for this example)
    persistence = InMemoryPersistence()
    asyncio.run(persistence.initialize())
    
    # Create individual memory types
    semantic_memory = SemanticMemory(persistence, namespace="user_semantic")
    episodic_memory = EpisodicMemory(persistence, namespace="user_episodic")
    procedural_memory = ProceduralMemory(persistence, namespace="user_procedural")
    
    # Create composite memory
    memory = CompositeMemory({
        "semantic": semantic_memory,
        "episodic": episodic_memory,
        "procedural": procedural_memory
    })
    
    # Pre-populate with some semantic memories for the user
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "name", "value": "Alice"}
    ))
    
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "interests", "value": ["AI", "astronomy", "history"]}
    ))
    
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "preferred_language", "value": "simple explanations"}
    ))
    
    # Create a procedural memory for explaining concepts
    asyncio.run(memory.save_to(
        "procedural",
        {
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
    ))
    
    # Configure LLM (from environment variable)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in .env file.")
    
    llm_configs = {
        "default": {
            "provider": "openai",
            "model_name": "gpt-4o",
            "temperature": 0.7
        }
    }
    
    # Create tools
    wiki_tool = get_wiki_tool()
    
    # Create ReAct agent with memory
    agent = ReActAgent(
        llm_configs=llm_configs,
        tools=[wiki_tool],
        memory=memory,
        memory_config={
            "semantic": True,  # Enable semantic memory
            "episodic": True,  # Enable episodic memory
            "procedural": True  # Enable procedural memory
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
    episodes = asyncio.run(memory.retrieve_from("episodic", "", limit=10))
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode.content}")
    
    print("\nSemantic memories:")
    facts = asyncio.run(memory.retrieve_from("semantic", "", limit=10))
    for i, fact in enumerate(facts):
        print(f"{i+1}. {fact}")
    
    print("\nProcedural memories:")
    procedures = asyncio.run(memory.retrieve_from("procedural", "", limit=10))
    for i, proc in enumerate(procedures):
        print(f"{i+1}. {proc.name}: {proc.description}")

if __name__ == "__main__":
    main() 