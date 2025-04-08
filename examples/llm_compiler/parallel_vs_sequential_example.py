"""Comparative example showing LLM Compiler vs sequential execution.

This example demonstrates the performance advantage of the LLM Compiler pattern
by comparing it to sequential execution of the same tasks.
"""

import os
import sys
import logging
import time
from dotenv import load_dotenv
from langchain_core.tools import BaseTool, tool
from typing import List, Dict, Any

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the LLMCompilerAgent and ReActAgent for comparison
from src.agent_patterns.patterns import LLMCompilerAgent, ReActAgent

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define tools with simulated latency for better comparison
@tool
def search_web(query: str) -> str:
    """Search the web for information with 1 second latency."""
    logger.info(f"Searching web for: {query}")
    # Simulate API call delay
    time.sleep(1.0)
    return f"Search results for '{query}': Found relevant information about {query}."

@tool
def fetch_weather(location: str) -> str:
    """Fetch the weather for a location with 1 second latency."""
    logger.info(f"Fetching weather for: {location}")
    # Simulate API call delay
    time.sleep(1.0)
    return f"Weather for {location}: 70°F, Clear skies"

@tool
def fetch_population(location: str) -> str:
    """Fetch the population of a location with 1 second latency."""
    logger.info(f"Fetching population for: {location}")
    # Simulate API call delay
    time.sleep(1.0)
    return f"Population of {location}: 1.5 million people"

@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression with 1 second latency."""
    logger.info(f"Calculating: {expression}")
    # Simulate computation delay
    time.sleep(1.0)
    try:
        # Safely evaluate the expression
        from math import sin, cos, tan, pi, sqrt, log
        result = eval(expression)
        return f"Result of '{expression}' = {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"

def run_llm_compiler(query: str, tools: List[BaseTool]) -> Dict[str, Any]:
    """Run the query using the LLM Compiler agent pattern.
    
    This pattern can execute multiple independent tasks in parallel.
    """
    # Configure LLMs for different roles
    llm_configs = {
        'planner': {
            'provider': 'openai',
            'model': 'gpt-3.5-turbo',
            'temperature': 0.2
        },
        'executor': {
            'provider': 'openai',
            'model': 'gpt-3.5-turbo',
            'temperature': 0.1
        },
        'joiner': {
            'provider': 'openai',
            'model': 'gpt-3.5-turbo',
            'temperature': 0.2
        }
    }
    
    # Initialize the LLM Compiler agent
    compiler_agent = LLMCompilerAgent(
        llm_configs=llm_configs,
        tools=tools,
        prompt_dir="src/agent_patterns/prompts",
        log_level=logging.INFO
    )
    
    # Run the agent and measure time
    start_time = time.time()
    result = compiler_agent.run(query)
    end_time = time.time()
    
    return {
        "output": result['output'],
        "execution_time": end_time - start_time,
        "pattern": "LLM Compiler",
        "metadata": result['metadata']
    }

def run_sequential(query: str, tools: List[BaseTool]) -> Dict[str, Any]:
    """Run the query using a standard sequential approach (ReAct pattern).
    
    This pattern executes tasks one at a time, so tasks will run sequentially
    even when they don't depend on each other.
    """
    # Configure LLMs for different roles
    llm_configs = {
        'default': {
            'provider': 'openai',
            'model': 'gpt-3.5-turbo',
            'temperature': 0.2
        }
    }
    
    # Initialize the ReAct agent (sequential execution)
    react_agent = ReActAgent(
        llm_configs=llm_configs,
        tools=tools,
        prompt_dir="src/agent_patterns/prompts",
        log_level=logging.INFO
    )
    
    # Run the agent and measure time
    start_time = time.time()
    result = react_agent.run(query)
    end_time = time.time()
    
    return {
        "output": result['output'],
        "execution_time": end_time - start_time,
        "pattern": "Sequential (ReAct)",
        "metadata": result.get('metadata', {})
    }

def main():
    """Compare LLM Compiler (parallel) vs sequential execution."""
    # Create a list of tools
    tools = [search_web, fetch_weather, fetch_population, calculate]
    
    # Query that requires multiple independent tasks
    query = """
    I need information on three cities:
    1. What's the weather in New York?
    2. What's the population of Tokyo?
    3. What's the weather in London?
    Also, calculate 128 * 256.
    """
    
    # Make sure the query is well formatted for the agent
    query = query.strip()
    
    print("\n========== EXECUTION COMPARISON ==========")
    print(f"\nQuery: {query}\n")
    
    # Run the comparison
    compiler_result = run_llm_compiler(query, tools)
    sequential_result = run_sequential(query, tools)
    
    # Display comparison
    print("\n========== RESULTS COMPARISON ==========")
    
    print(f"\n--- LLM COMPILER PATTERN (PARALLEL) ---")
    print(f"Execution time: {compiler_result['execution_time']:.2f} seconds")
    print(f"Tasks planned: {compiler_result['metadata'].get('tasks_planned', 'N/A')}")
    print(f"Tasks completed: {compiler_result['metadata'].get('tasks_completed', 'N/A')}")
    print("\nOutput:")
    print(compiler_result['output'])
    
    print(f"\n--- SEQUENTIAL PATTERN (REACT) ---")
    print(f"Execution time: {sequential_result['execution_time']:.2f} seconds")
    print("\nOutput:")
    print(sequential_result['output'])
    
    # Calculate speedup
    speedup = sequential_result['execution_time'] / compiler_result['execution_time']
    print(f"\n========== PERFORMANCE ANALYSIS ==========")
    print(f"LLM Compiler was {speedup:.2f}x faster than sequential execution.")
    print(f"Time saved: {sequential_result['execution_time'] - compiler_result['execution_time']:.2f} seconds")
    
    if speedup > 1:
        print("\nThe LLM Compiler pattern's parallel execution provided a significant speedup,")
        print("particularly for queries with multiple independent tasks that can run in parallel.")
    else:
        print("\nIn this case, parallel execution didn't provide a speedup.")
        print("This can happen when tasks have dependencies or overhead outweighs benefits.")

if __name__ == "__main__":
    main() 