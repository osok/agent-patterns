"""Example demonstrating the ReActAgent."""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



import os
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.tools import Tool
from agent_patterns.patterns.re_act_agent import ReActAgent

# Add the parent directory to sys.path to import from examples.utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from examples.utils.model_config import get_llm_configs

def main():
    # Load environment variables
    load_dotenv()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # Setup LLM configs using the utility function
    try:
        # This will use PLANNING_MODEL_PROVIDER and PLANNING_MODEL_NAME from .env
        llm_configs = get_llm_configs()
    except ValueError as e:
        logger.error(f"Error loading model configuration: {e}")
        logger.error("Please ensure your .env file contains the necessary model configuration variables.")
        return
    
    # Define sample tools for the ReAct agent
    tools = [
        Tool(
            name="search",
            func=lambda query: f"Search results for: {query}",
            description="Search the web for information on a given topic."
        ),
        Tool(
            name="calculator",
            func=lambda expression: str(eval(expression)),
            description="Evaluate a mathematical expression."
        ),
        Tool(
            name="weather",
            func=lambda location: f"The weather in {location} is currently sunny and 75°F.",
            description="Get the current weather for a specified location."
        )
    ]
    
    # Get the correct prompt directory
    # The prompts are in src/agent_patterns/prompts
    prompt_dir = "src/agent_patterns/prompts"
    
    # Initialize the agent
    agent = ReActAgent(
        llm_configs=llm_configs,
        tools=tools,
        prompt_dir=prompt_dir,
        max_steps=5,
        log_level=logging.INFO
    )
    
    # Example task
    task = "What's the weather like in San Francisco? Also, what is 25 * 4?"
    
    logger.info(f"Running ReAct agent with task: {task}")
    
    # Run the agent
    result = agent.run(task)
    
    # Display the result
    if "error" in result:
        logger.error(f"Agent execution failed: {result['error']}")
    else:
        logger.info("Agent execution completed successfully")
        print("\n" + "="*80 + "\n")
        print("TASK:")
        print(task)
        print("\n" + "="*80 + "\n")
        print("RESULT:")
        print(result["output"])
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()