"""
Trip Planning Agent using the Plan and Solve Pattern

This example demonstrates how to use the Plan and Solve agent pattern to
create a trip planning agent that can help users plan a trip to a specific destination.
"""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Add the parent directory to the path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agent_patterns.patterns.plan_and_solve_agent import PlanAndSolveAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    # Check if the required environment variables are set
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable not set. Please set it in your .env file.")
        return
    
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent
    
    # Check both potential prompt directory paths
    src_prompt_dir = project_root / "src" / "agent_patterns" / "prompts"
    non_src_prompt_dir = project_root / "agent_patterns" / "prompts"
    
    # Use the path that exists
    if src_prompt_dir.exists():
        prompt_dir = str(src_prompt_dir)
    else:
        prompt_dir = str(non_src_prompt_dir)
    
    # Get model names from environment variables with defaults
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1")
    anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-latest")
    google_model = os.getenv("GOOGLE_MODEL", "models/gemini-2.5-pro-preview-03-25")
    
    # Configure LLM for the planner and executor
    planner_config = {
        "provider": "openai",
        "model_name": openai_model,
        "temperature": 0.7
    }
    
    executor_config = {
        "provider": "openai",
        "model_name": openai_model,
        "temperature": 0.7
    }
    
    # Create LLM configurations for different roles
    llm_configs = {
        "planner": planner_config,
        "executor": executor_config
    }
    
    # Create a Plan and Solve agent for trip planning
    agent = PlanAndSolveAgent(
        llm_configs=llm_configs,
        prompt_dir=prompt_dir
    )
    
    # Define example trip planning queries
    example_queries = [
        "I want to plan a 3-day trip to Paris. What are the must-see attractions and how should I organize my days?",
        "I'm planning a trip to Japan for 10 days. I want to visit Tokyo, Kyoto, and Osaka. How should I plan my trip?",
        "I want to take my family of 4 to Yellowstone National Park for a week in July. What should we see and do?"
    ]
    
    # User selects a query or enters a custom one
    print("Trip Planning Agent")
    print("==================")
    print("\nExample queries:")
    for i, query in enumerate(example_queries):
        print(f"{i+1}. {query}")
    print("\nEnter the number of an example query or type your own query:")
    
    user_input = input("> ")
    
    try:
        # Try to parse as a number for example selection
        selection = int(user_input) - 1
        if 0 <= selection < len(example_queries):
            query = example_queries[selection]
        else:
            query = user_input
    except ValueError:
        # User entered a custom query
        query = user_input
    
    # Execute the trip planning query
    logger.info(f"Planning trip with query: {query}")
    result = agent.run(query)
    
    # Print the plan and solution
    print("\nTrip Planning Results")
    print("==================")
    
    if "error" in result:
        print("\nERROR:")
        print(result["error"])
    elif "output" in result:
        print("\nRESULT:")
        print(result["output"])
    else:
        print("\nNo output was generated. Available keys in result:")
        for key in result:
            print(f"- {key}")

if __name__ == "__main__":
    main()