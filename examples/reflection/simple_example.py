"""
Simple example demonstrating the Reflection Agent pattern.

This example shows how to initialize and run a Reflection Agent.
"""

import os
import logging
from dotenv import load_dotenv

from agent_patterns.patterns.reflection_agent import ReflectionAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Run a simple example of the Reflection Agent."""
    
    # Configure LLMs for different roles in the agent
    llm_configs = {
        "generator": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7
        },
        "critic": {
            "provider": "openai",
            "model": "gpt-4", # Using a potentially stronger model for critique
            "temperature": 0.2 # Lower temperature for more focused critique
        }
    }
    
    # Create the agent
    reflection_agent = ReflectionAgent(
        llm_configs=llm_configs,
        prompt_dir="src/agent_patterns/prompts",
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
    
if __name__ == "__main__":
    main()