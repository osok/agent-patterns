"""Example usage of the Reflexion Agent pattern.

This example demonstrates using the ReflexionAgent to solve a problem
through multiple trials, learning from past attempts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def setup_llm_configs() -> Dict:
    """Set up LLM configurations for the Reflexion agent roles.
    
    Returns:
        Dictionary with LLM configurations for each role.
    """
    # Default to OpenAI if specific providers aren't specified
    default_provider = os.getenv("DEFAULT_MODEL_PROVIDER", "openai")
    default_model = os.getenv("DEFAULT_MODEL_NAME", "gpt-3.5-turbo")
    
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
    """Run an example of the Reflexion agent solving a problem."""
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent
    prompt_dir = str(project_root / "src" / "agent_patterns" / "prompts")
    
    # Set up the LLM configurations
    llm_configs = setup_llm_configs()
    
    # Create the Reflexion agent
    agent = ReflexionAgent(
        llm_configs=llm_configs,
        prompt_dir=prompt_dir,
        max_trials=3,  # Allow up to 3 attempts
        log_level=logging.INFO
    )
    
    # Define a task that might require multiple attempts
    # This recursive Fibonacci example can be challenging due to potential inefficiencies
    task = """
    Write a Python function to compute the nth Fibonacci number. 
    
    The Fibonacci sequence starts with 0 and 1, and each subsequent number is the sum of the two preceding ones.
    For example, the first 10 Fibonacci numbers are: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34.
    
    Your solution should be efficient enough to compute fibonacci(35) in under a second.
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

if __name__ == "__main__":
    main()