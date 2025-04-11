"""Example demonstrating the LLM Compiler agent pattern with memory and tools.

This example shows how to set up and use the LLM Compiler agent pattern 
for parallel task execution with dependency management, enhanced with memory
capabilities and tool integration.
"""

import os
import sys
import logging
import asyncio
from dotenv import load_dotenv
from langchain_core.tools import BaseTool, tool
import time
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the LLMCompilerAgent and memory components
from agent_patterns.patterns import LLMCompilerAgent
from agent_patterns.core.memory import (
    SemanticMemory,
    EpisodicMemory,
    ProceduralMemory,
    CompositeMemory
)
from agent_patterns.core.memory.persistence import (
    InMemoryPersistence
)

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define tools for our agent to use
@tool
def search_web(query: str) -> str:
    """Search the web for information."""
    logger.info(f"Searching web for: {query}")
    # Simulate API call delay
    time.sleep(0.5)
    return f"Search results for '{query}': This is a simulated search result with relevant information."

@tool
def calculate(expression: str) -> str:
    """Calculate the result of a mathematical expression."""
    logger.info(f"Calculating: {expression}")
    try:
        # Safely evaluate the expression
        from math import sin, cos, tan, pi, sqrt, log
        result = eval(expression)
        return f"Result of '{expression}' = {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"

@tool
def fetch_weather(location: str) -> str:
    """Fetch the weather for a given location."""
    logger.info(f"Fetching weather for: {location}")
    # Simulate API call delay
    time.sleep(0.5)
    # In a real implementation, this would call a weather API
    weather_info = {
        "New York": {"temp": 72, "condition": "Sunny"},
        "London": {"temp": 60, "condition": "Cloudy"},
        "Tokyo": {"temp": 80, "condition": "Rainy"},
        "San Francisco": {"temp": 65, "condition": "Foggy"},
        "default": {"temp": 70, "condition": "Clear"}
    }
    
    info = weather_info.get(location, weather_info["default"])
    return f"Weather for {location}: {info['temp']}°F, {info['condition']}"

@tool
def convert_temperature(temp_str: str, to_unit: str) -> str:
    """Convert temperature between Fahrenheit and Celsius.
    
    Args:
        temp_str: Temperature value with unit (e.g., '32F', '100C')
        to_unit: Target unit ('F' or 'C')
    """
    logger.info(f"Converting temperature: {temp_str} to {to_unit}")
    try:
        # Extract value and unit
        value = float(temp_str[:-1])
        unit = temp_str[-1].upper()
        
        if unit == to_unit:
            return f"{value}{to_unit}"
        
        if unit == 'F' and to_unit == 'C':
            result = (value - 32) * 5/9
            return f"{result:.1f}°C"
        elif unit == 'C' and to_unit == 'F':
            result = value * 9/5 + 32
            return f"{result:.1f}°F"
        else:
            return f"Invalid units: {unit} to {to_unit}"
    except Exception as e:
        return f"Error converting temperature: {str(e)}"

async def setup_memory_async():
    """Set up a composite memory system asynchronously."""
    # Create persistence backend
    persistence = InMemoryPersistence()
    await persistence.initialize()
    
    # Create individual memory types
    semantic_memory = SemanticMemory(persistence, namespace="compiler_semantic")
    episodic_memory = EpisodicMemory(persistence, namespace="compiler_episodic")
    procedural_memory = ProceduralMemory(persistence, namespace="compiler_procedural")
    
    # Create composite memory
    memory = CompositeMemory({
        "semantic": semantic_memory,
        "episodic": episodic_memory,
        "procedural": procedural_memory
    })
    
    # Pre-populate with some semantic memories
    await memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "location", "value": "San Francisco"}
    )
    
    await memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "preferred_temperature_unit", "value": "C"}
    )
    
    # Add a procedural memory for query decomposition
    await memory.save_to(
        "procedural",
        {
            "name": "decompose_complex_query",
            "pattern": {
                "template": """When decomposing a complex query:
1. Identify independent sub-tasks that can run in parallel
2. Establish dependencies between related sub-tasks
3. Prioritize data gathering tasks before computation tasks
4. Consider user preferences when relevant: preferred_temperature_unit = {preferred_temperature_unit}
5. Be precise about what information is needed from each tool"""
            },
            "description": "Template for effectively decomposing complex queries",
            "tags": ["planning", "decomposition", "efficiency"]
        }
    )
    
    return memory

def setup_memory():
    """Set up a composite memory system."""
    return asyncio.run(setup_memory_async())

def basic_example():
    """Run a basic example of the LLM Compiler agent with memory."""
    logger.info("Running basic LLM Compiler example with memory")
    
    # Configure LLMs for different roles
    llm_configs = {
        'planner': {
            'provider': 'openai',
            'model_name': 'gpt-4o',
            'temperature': 0.2
        },
        'executor': {
            'provider': 'openai',
            'model_name': 'gpt-4o',
            'temperature': 0.1
        },
        'joiner': {
            'provider': 'openai',
            'model_name': 'gpt-4o',
            'temperature': 0.2
        }
    }
    
    # Set up memory
    memory = setup_memory()
    
    # Create a list of tools
    tools = [search_web, calculate, fetch_weather, convert_temperature]
    
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent
    prompt_dir = str(project_root / "agent_patterns" / "prompts")
    
    # Initialize the LLM Compiler agent with memory
    agent = LLMCompilerAgent(
        llm_configs=llm_configs,
        tools=tools,
        prompt_dir=prompt_dir,
        memory=memory,
        memory_config={
            "semantic": True,
            "episodic": True,
            "procedural": True
        },
        log_level=logging.INFO
    )
    
    # User query that requires multiple tools and can benefit from parallel execution
    query = "What's the temperature in New York City and my location, and how many days until Christmas? Also, what's 356 * 24?"
    
    # Run the agent
    logger.info(f"Running LLM Compiler agent with query: {query}")
    start_time = time.time()
    result = agent.run(query)
    end_time = time.time()
    
    # Display the result
    print("\n=== RESULT ===")
    print(result.get('output', f"Error: {result.get('error', 'Unknown error')}"))
    print("\n=== METADATA ===")
    metadata = result.get('metadata', {})
    print(f"Tasks planned: {metadata.get('tasks_planned', 0)}")
    print(f"Tasks completed: {metadata.get('tasks_completed', 0)}")
    print(f"Needed replanning: {metadata.get('needed_replanning', False)}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    
    # Show what was stored in memory
    print("\n=== MEMORY AFTER EXECUTION ===")
    print("Semantic memories:")
    facts = asyncio.run(memory.retrieve_from("semantic", "", limit=5))
    for i, fact in enumerate(facts):
        print(f"{i+1}. {fact}")
    
    print("\nEpisodic memories:")
    episodes = asyncio.run(memory.retrieve_from("episodic", "temperature", limit=5))
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode.content}")

def complex_query_example():
    """Run a more complex example with interdependent tasks and memory."""
    logger.info("Running complex query example with memory")
    
    # Configure LLMs for different roles
    llm_configs = {
        'planner': {
            'provider': 'openai',
            'model_name': 'gpt-4o',
            'temperature': 0.2
        },
        'executor': {
            'provider': 'openai',
            'model_name': 'gpt-4o',
            'temperature': 0.1
        },
        'joiner': {
            'provider': 'openai',
            'model_name': 'gpt-4o',
            'temperature': 0.2
        }
    }
    
    # Set up memory
    memory = setup_memory()
    
    # Create a list of tools
    tools = [search_web, calculate, fetch_weather, convert_temperature]
    
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent
    prompt_dir = str(project_root / "agent_patterns" / "prompts")
    
    # Initialize the LLM Compiler agent with memory
    agent = LLMCompilerAgent(
        llm_configs=llm_configs,
        tools=tools,
        prompt_dir=prompt_dir,
        memory=memory,
        memory_config={
            "semantic": True,
            "episodic": True,
            "procedural": True
        },
        log_level=logging.INFO
    )
    
    # User query with dependencies between tasks
    query = """I'm planning a trip and need some information:
    1. What's the current weather in Tokyo and my current location?
    2. Convert temperatures to my preferred temperature unit
    3. What's the average of these two cities' temperatures?
    4. How many hours is the flight between these cities?"""
    
    # Run the agent
    logger.info(f"Running LLM Compiler agent with complex query: {query}")
    start_time = time.time()
    result = agent.run(query)
    end_time = time.time()
    
    # Display the result
    print("\n=== COMPLEX QUERY RESULT ===")
    print(result.get('output', f"Error: {result.get('error', 'Unknown error')}"))
    print("\n=== METADATA ===")
    metadata = result.get('metadata', {})
    print(f"Tasks planned: {metadata.get('tasks_planned', 0)}")
    print(f"Tasks completed: {metadata.get('tasks_completed', 0)}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    
    # Show what was stored in memory
    print("\n=== MEMORY AFTER EXECUTION ===")
    print("Episodic memories from this interaction:")
    episodes = asyncio.run(memory.retrieve_from("episodic", "trip planning", limit=5))
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode.content}")

def streaming_example():
    """Run an example demonstrating streaming output with memory."""
    logger.info("Running streaming example with memory")
    
    # Configure LLMs for different roles
    llm_configs = {
        'planner': {
            'provider': 'openai',
            'model_name': 'gpt-4o',
            'temperature': 0.2
        },
        'executor': {
            'provider': 'openai',
            'model_name': 'gpt-4o',
            'temperature': 0.1
        },
        'joiner': {
            'provider': 'openai',
            'model_name': 'gpt-4o',
            'temperature': 0.2
        }
    }
    
    # Set up memory
    memory = setup_memory()
    
    # Create a list of tools
    tools = [search_web, calculate, fetch_weather]
    
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent
    prompt_dir = str(project_root / "agent_patterns" / "prompts")
    
    # Initialize the LLM Compiler agent with memory
    agent = LLMCompilerAgent(
        llm_configs=llm_configs,
        tools=tools,
        prompt_dir=prompt_dir,
        memory=memory,
        memory_config={
            "semantic": True,
            "episodic": True,
            "procedural": False  # Disable procedural memory for this example
        },
        log_level=logging.INFO
    )
    
    # User query
    query = "What's the weather in London and what's the square root of 144?"
    
    # Stream the agent execution
    logger.info(f"Streaming LLM Compiler agent with query: {query}")
    print("\n=== STREAMING EXECUTION ===")
    
    final_result = None
    
    for i, state_update in enumerate(agent.stream(query)):
        print(f"\nUpdate {i+1}:")
        
        # Check if this is an error update
        if "error" in state_update:
            print(f"  Error: {state_update['error']}")
            if "final_answer" in state_update:
                final_result = state_update["final_answer"]
            continue
            
        # Check if this contains the final answer
        if "final_answer" in state_update and state_update["final_answer"]:
            final_result = state_update["final_answer"]
            
        # Print a simplified version of the state update
        for key, value in state_update.items():
            if isinstance(value, (list, dict)) and len(str(value)) > 100:
                print(f"  {key}: [complex data]")
            else:
                print(f"  {key}: {value}")
    
    # Display the final result if available
    if final_result:
        print("\n=== FINAL RESULT ===")
        print(final_result)

def main():
    """Run all examples."""
    print("\n========== BASIC EXAMPLE WITH MEMORY ==========")
    basic_example()
    
    print("\n========== COMPLEX QUERY EXAMPLE WITH MEMORY ==========")
    complex_query_example()
    
    print("\n========== STREAMING EXAMPLE WITH MEMORY ==========")
    streaming_example()

if __name__ == "__main__":
    main() 