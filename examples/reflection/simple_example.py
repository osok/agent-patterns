"""
Simple example demonstrating the Reflection Agent pattern with memory and tools.

This example shows how to initialize and run a Reflection Agent with memory
and tool integration for enhanced capabilities.
"""

import os
import sys
import logging
import asyncio
from dotenv import load_dotenv
from pathlib import Path

# Add the parent directory to sys.path to import agent_patterns
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agent_patterns.patterns.reflection_agent import ReflectionAgent
from agent_patterns.core.memory import (
    SemanticMemory,
    EpisodicMemory,
    ProceduralMemory,
    CompositeMemory
)
from agent_patterns.core.memory.persistence import (
    InMemoryPersistence
)
from agent_patterns.core.tools.base import ToolProvider

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple search tool implementation
class SearchTool(ToolProvider):
    """A simple search tool provider that returns predefined results."""
    
    def list_tools(self):
        """List the available tools."""
        return [{
            "name": "search",
            "description": "Search for information about a topic",
            "parameters": {
                "query": {
                    "type": "string", 
                    "description": "The search query"
                }
            }
        }]
    
    def execute_tool(self, tool_name, params):
        """Execute the search tool with mock results for demonstration."""
        if tool_name != "search":
            return f"Unknown tool: {tool_name}"
            
        query = params.get("query", "").lower()
        
        # Predefined responses for relativity-related queries
        if "relativity" in query or "einstein" in query:
            return """
            Albert Einstein published the theory of relativity in 1915.
            Key concepts include:
            - The speed of light is constant for all observers
            - Space and time are interconnected as spacetime
            - Gravity is a curvature of spacetime caused by mass
            - The famous equation E=mc² relates energy and mass
            
            Practical applications include:
            - GPS systems must account for relativity effects
            - Nuclear energy (from E=mc²)
            - Gravitational lensing in astronomy
            """
        elif "technology" in query and ("modern" in query or "application" in query):
            return """
            Modern applications of relativity include:
            1. GPS satellites - must compensate for time dilation effects
            2. Particle accelerators - account for relativistic speeds
            3. Nuclear power - based on mass-energy equivalence
            4. Gravitational wave detectors (LIGO)
            5. Spacecraft navigation for deep space missions
            """
        else:
            return f"Search results for: {query} - Please refine your query for more specific information."

def setup_memory():
    """Set up a composite memory system."""
    # Create persistence backend
    persistence = InMemoryPersistence()
    asyncio.run(persistence.initialize())
    
    # Create individual memory types
    semantic_memory = SemanticMemory(persistence, namespace="theory_semantic")
    episodic_memory = EpisodicMemory(persistence, namespace="theory_episodic")
    procedural_memory = ProceduralMemory(persistence, namespace="theory_procedural")
    
    # Create composite memory
    memory = CompositeMemory({
        "semantic": semantic_memory,
        "episodic": episodic_memory,
        "procedural": procedural_memory
    })
    
    # Pre-populate with some semantic memories about the topic
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "relativity", "attribute": "core_concept", "value": "space and time are relative"}
    ))
    
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "knowledge_level", "value": "beginner"}
    ))
    
    # Add a procedural memory for explaining complex topics
    asyncio.run(memory.save_to(
        "procedural",
        {
            "name": "explain_complex_topic",
            "pattern": {
                "template": """When explaining complex scientific topics:
1. Begin with a simple analogy
2. Define key terms in accessible language
3. Provide real-world examples
4. Break complex concepts into smaller parts
5. Address common misconceptions
6. Tailor explanation to audience knowledge level: {knowledge_level}"""
            },
            "description": "Template for explaining complex scientific concepts",
            "tags": ["explanation", "science", "teaching"]
        }
    ))
    
    return memory

def main():
    """Run a simple example of the Reflection Agent with memory and tools."""
    
    # Configure LLMs for different roles in the agent
    llm_configs = {
        "generator": {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.7
        },
        "critic": {
            "provider": "openai",
            "model": "gpt-4o", # Using the same model for critique
            "temperature": 0.2 # Lower temperature for more focused critique
        }
    }
    
    # Set up memory
    memory = setup_memory()
    
    # Set up search tool
    search_tool = SearchTool()
    
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent
    
    # Try to find prompts directory - check both source and package paths
    src_prompt_dir = os.path.join(project_root, "src", "agent_patterns", "prompts")
    pkg_prompt_dir = os.path.join(project_root, "agent_patterns", "prompts")
    
    prompt_dir = src_prompt_dir if os.path.exists(src_prompt_dir) else pkg_prompt_dir
    
    # Create the agent with memory and tools
    reflection_agent = ReflectionAgent(
        llm_configs=llm_configs,
        prompt_dir=prompt_dir,
        memory=memory,
        memory_config={
            "semantic": True,
            "episodic": True,
            "procedural": True
        },
        tool_provider=search_tool,
        log_level=logging.INFO
    )
    
    # Define a test query that might benefit from reflection
    test_query = """
    Explain the theory of relativity and its practical applications in modern technology.
    """
    
    logger.info("Running Reflection Agent with query: %s", test_query)
    
    # Run the agent
    result = reflection_agent.run(test_query)
    
    # Display the result
    if "error" in result:
        logger.error("Agent execution failed: %s", result["error"])
    else:
        logger.info("Final Result:")
        print("\n" + "="*80)
        print(result["output"])
        print("="*80)
    
    # Show what was stored in memory
    print("\nMEMORY AFTER EXECUTION:")
    
    print("\nSemantic memories:")
    facts = asyncio.run(memory.retrieve_from("semantic", "", limit=5))
    for i, fact in enumerate(facts):
        print(f"{i+1}. {fact}")
    
    print("\nEpisodic memories:")
    episodes = asyncio.run(memory.retrieve_from("episodic", "relativity", limit=5))
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode.content}")
    
if __name__ == "__main__":
    main()