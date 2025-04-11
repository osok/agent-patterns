"""Example usage of the Reflexion Agent pattern with memory and tools.

This example demonstrates using the ReflexionAgent to solve a problem
through multiple trials, learning from past attempts, with the enhanced
capabilities of memory and tool access.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict
import logging
import asyncio
import json
import time

# Add the parent directory to sys.path to import agent_patterns
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import agent patterns modules
from agent_patterns.patterns.reflexion_agent import ReflexionAgent
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

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Simple benchmarking tool implementation
class BenchmarkTool(ToolProvider):
    """A simple tool to benchmark Fibonacci implementations."""
    
    def list_tools(self):
        """List the available tools."""
        return [{
            "name": "benchmark_code",
            "description": "Benchmark a Python function for performance",
            "parameters": {
                "code": {
                    "type": "string", 
                    "description": "The Python code to benchmark"
                },
                "test_case": {
                    "type": "string",
                    "description": "The test case to run (e.g., 'fibonacci(35)')"
                }
            }
        }]
    
    def execute_tool(self, tool_name, params):
        """Execute the benchmarking tool."""
        if tool_name != "benchmark_code":
            return f"Unknown tool: {tool_name}"
            
        code = params.get("code", "")
        test_case = params.get("test_case", "fibonacci(35)")
        
        try:
            # Create a temporary namespace for execution
            namespace = {}
            
            # Execute the code in the namespace
            exec(code, namespace)
            
            # Check if the function exists
            function_name = test_case.split("(")[0]
            if function_name not in namespace:
                return f"Error: Function '{function_name}' not found in the code"
            
            # Import time for benchmarking
            import time
            
            # Run the function and measure time
            start_time = time.time()
            try:
                result = eval(test_case, namespace)
                end_time = time.time()
                execution_time = end_time - start_time
                
                return f"Result: {result}\nExecution time: {execution_time:.6f} seconds"
            except Exception as e:
                return f"Error during execution: {str(e)}"
                
        except Exception as e:
            return f"Error in code: {str(e)}"

async def setup_memory_async():
    """Set up a composite memory system for the Reflexion agent asynchronously."""
    # Create persistence backend
    persistence = InMemoryPersistence()
    await persistence.initialize()
    
    # Create individual memory types
    semantic_memory = SemanticMemory(persistence, namespace="fibonacci_semantic")
    episodic_memory = EpisodicMemory(persistence, namespace="fibonacci_episodic")
    procedural_memory = ProceduralMemory(persistence, namespace="fibonacci_procedural")
    
    # Create composite memory
    memory = CompositeMemory({
        "semantic": semantic_memory,
        "episodic": episodic_memory,
        "procedural": procedural_memory
    })
    
    # Pre-populate with some semantic memories about algorithms
    await memory.save_to(
        "semantic", 
        {"entity": "fibonacci", "attribute": "definition", "value": "A sequence where each number is the sum of the two preceding ones"}
    )
    
    await memory.save_to(
        "semantic", 
        {"entity": "recursive_algorithm", "attribute": "limitation", "value": "can lead to exponential time complexity without memoization"}
    )
    
    # Add a procedural memory for optimizing code
    await memory.save_to(
        "procedural",
        {
            "name": "optimize_recursive_function",
            "pattern": {
                "template": """When optimizing recursive functions:
1. Consider using memoization to avoid redundant calculations
2. Try converting to an iterative approach
3. Use dynamic programming for overlapping subproblems
4. Consider space-time tradeoffs
5. Analyze the time complexity of your solution"""
            },
            "description": "Template for optimizing recursive functions",
            "tags": ["optimization", "recursion", "algorithm"]
        }
    )
    
    return memory

def setup_memory():
    """Set up a composite memory system for the Reflexion agent."""
    return asyncio.run(setup_memory_async())

async def retrieve_memories(memory, memory_type, query, limit=5):
    """Retrieve memories asynchronously."""
    return await memory.retrieve_from(memory_type, query, limit=limit)

def setup_llm_configs() -> Dict:
    """Set up LLM configurations for the Reflexion agent roles.
    
    Returns:
        Dictionary with LLM configurations for each role.
    """
    # Default to OpenAI if specific providers aren't specified
    default_provider = os.getenv("DEFAULT_MODEL_PROVIDER", "openai")
    default_model = os.getenv("DEFAULT_MODEL_NAME", "gpt-4o")
    
    # Define configurations for each role
    # In a production setting, you might want different models for different roles
    llm_configs = {
        "planner": {
            "provider": os.getenv("PLANNER_MODEL_PROVIDER", default_provider),
            "model_name": os.getenv("PLANNER_MODEL_NAME", default_model),
        },
        "executor": {
            "provider": os.getenv("EXECUTOR_MODEL_PROVIDER", default_provider),
            "model_name": os.getenv("EXECUTOR_MODEL_NAME", default_model),
        },
        "evaluator": {
            "provider": os.getenv("EVALUATOR_MODEL_PROVIDER", default_provider),
            "model_name": os.getenv("EVALUATOR_MODEL_NAME", default_model),
        },
        "reflector": {
            "provider": os.getenv("REFLECTOR_MODEL_PROVIDER", default_provider),
            "model_name": os.getenv("REFLECTOR_MODEL_NAME", default_model),
        }
    }
    
    return llm_configs

def main():
    """Run a simple example of the Reflexion agent."""
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent

    # Set prompt directory path (using src directory)
    prompt_dir = str(project_root / "src" / "agent_patterns" / "prompts")
    
    # Set up the LLM configurations
    llm_configs = setup_llm_configs()
    
    # Set up memory
    memory = setup_memory()
    
    # Set up benchmark tool
    benchmark_tool = BenchmarkTool()
    
    # Create the Reflexion agent with memory and tools
    agent = ReflexionAgent(
        llm_configs=llm_configs,
        prompt_dir=prompt_dir,
        max_trials=3,  # Allow up to 3 attempts
        memory=memory,
        memory_config={
            "semantic": True,
            "episodic": True,
            "procedural": True
        },
        tool_provider=benchmark_tool,
        log_level=logging.INFO
    )
    
    # Define a task that might require multiple attempts
    # This recursive Fibonacci example can be challenging due to potential inefficiencies
    task = """
    Write a Python function to compute the nth Fibonacci number. 
    
    The Fibonacci sequence starts with 0 and 1, and each subsequent number is the sum of the two preceding ones.
    For example, the first 10 Fibonacci numbers are: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34.
    
    Your solution should be efficient enough to compute fibonacci(35) in under a second.
    You can use the benchmark_code tool to test your solution's performance.
    """
    
    logger.info("Running Reflexion agent for Fibonacci implementation")
    print(f"Task: {task}\n")
    print("Running Reflexion agent with up to 3 trials...\n")
    
    # Run the agent
    result = agent.run(task)
    
    # Display the results
    print("\n=== RESULTS ===\n")
    print(f"Number of trials: {result['metadata']['trials_completed']}")
    print("\n=== FINAL SOLUTION ===\n")
    print(result["output"])
    
    print("\n=== REFLECTIONS ===\n")
    for i, reflection in enumerate(result["metadata"]["reflections"]):
        print(f"Reflection {i+1}:")
        print(reflection)
        print()
    
    # Show what was stored in memory
    print("\n=== MEMORY AFTER EXECUTION ===\n")
    print("Semantic memories:")
    facts = asyncio.run(retrieve_memories(memory, "semantic", "", 5))
    for i, fact in enumerate(facts):
        print(f"{i+1}. {fact}")
    
    print("\nEpisodic memories:")
    episodes = asyncio.run(retrieve_memories(memory, "episodic", "fibonacci", 5))
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode.content}")

if __name__ == "__main__":
    main()