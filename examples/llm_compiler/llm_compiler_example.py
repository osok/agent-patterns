"""Example demonstrating the LLM Compiler agent pattern.

This example shows how to set up and use the LLM Compiler agent pattern 
for parallel task execution with dependency management.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from langchain_core.tools import BaseTool, tool
import time

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the LLMCompilerAgent
from src.agent_patterns.patterns import LLMCompilerAgent

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

def basic_example():
    """Run a basic example of the LLM Compiler agent."""
    logger.info("Running basic LLM Compiler example")
    
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
    
    # Create a list of tools
    tools = [search_web, calculate, fetch_weather, convert_temperature]
    
    # Initialize the LLM Compiler agent
    agent = LLMCompilerAgent(
        llm_configs=llm_configs,
        tools=tools,
        prompt_dir="src/agent_patterns/prompts",
        log_level=logging.INFO
    )
    
    # User query that requires multiple tools and can benefit from parallel execution
    query = "What's the temperature in New York City, and how many days until Christmas? Also, what's 356 * 24?"
    
    # Run the agent
    logger.info(f"Running LLM Compiler agent with query: {query}")
    start_time = time.time()
    result = agent.run(query)
    end_time = time.time()
    
    # Display the result
    print("\n=== RESULT ===")
    print(result['output'])
    print("\n=== METADATA ===")
    print(f"Tasks planned: {result['metadata']['tasks_planned']}")
    print(f"Tasks completed: {result['metadata']['tasks_completed']}")
    print(f"Needed replanning: {result['metadata']['needed_replanning']}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")

def complex_query_example():
    """Run a more complex example with interdependent tasks."""
    logger.info("Running complex query example")
    
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
    
    # Create a list of tools
    tools = [search_web, calculate, fetch_weather, convert_temperature]
    
    # Initialize the LLM Compiler agent
    agent = LLMCompilerAgent(
        llm_configs=llm_configs,
        tools=tools,
        prompt_dir="src/agent_patterns/prompts",
        log_level=logging.INFO
    )
    
    # User query with dependencies between tasks
    query = """I'm planning a trip and need some information:
    1. What's the current weather in Tokyo and San Francisco?
    2. Convert Tokyo's temperature to Celsius
    3. What's the average of these two cities' temperatures?
    4. How many hours is the flight between these cities?"""
    
    # Run the agent
    logger.info(f"Running LLM Compiler agent with complex query: {query}")
    start_time = time.time()
    result = agent.run(query)
    end_time = time.time()
    
    # Display the result
    print("\n=== COMPLEX QUERY RESULT ===")
    print(result['output'])
    print("\n=== METADATA ===")
    print(f"Tasks planned: {result['metadata']['tasks_planned']}")
    print(f"Tasks completed: {result['metadata']['tasks_completed']}")
    print(f"Execution time: {end_time - start_time:.2f} seconds")

def streaming_example():
    """Run an example demonstrating streaming output."""
    logger.info("Running streaming example")
    
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
    
    # Create a list of tools
    tools = [search_web, calculate, fetch_weather]
    
    # Initialize the LLM Compiler agent
    agent = LLMCompilerAgent(
        llm_configs=llm_configs,
        tools=tools,
        prompt_dir="src/agent_patterns/prompts",
        log_level=logging.INFO
    )
    
    # User query
    query = "What's the weather in London and what's the square root of 144?"
    
    # Stream the agent execution
    logger.info(f"Streaming LLM Compiler agent with query: {query}")
    print("\n=== STREAMING EXECUTION ===")
    
    for i, state_update in enumerate(agent.stream(query)):
        print(f"\nUpdate {i+1}:")
        # Print a simplified version of the state update
        for key, value in state_update.items():
            if isinstance(value, (list, dict)) and len(str(value)) > 100:
                print(f"  {key}: [complex data]")
            else:
                print(f"  {key}: {value}")

def main():
    """Run all examples."""
    print("\n========== BASIC EXAMPLE ==========")
    basic_example()
    
    print("\n========== COMPLEX QUERY EXAMPLE ==========")
    complex_query_example()
    
    print("\n========== STREAMING EXAMPLE ==========")
    streaming_example()

if __name__ == "__main__":
    main() 