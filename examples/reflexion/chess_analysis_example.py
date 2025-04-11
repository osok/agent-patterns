"""Advanced example for the Reflexion Agent pattern.

This example demonstrates using the ReflexionAgent to analyze a chess position
through multiple trials, learning from past attempts to provide better analysis.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict
import logging
import json

import chess

# Add the parent directory to sys.path to import agent_patterns
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import agent patterns modules
from agent_patterns.patterns.reflexion_agent import ReflexionAgent
from agent_patterns.utils.structured_string import StructuredString
from agent_patterns.base import Task

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
    
    # For a chess analysis task, we might want more capable models
    llm_configs = {
        "planner": {
            "provider": os.getenv("PLANNER_MODEL_PROVIDER", default_provider),
            "model_name": os.getenv("PLANNER_MODEL_NAME", "gpt-4-turbo-preview"),
            "temperature": 0.7,
        },
        "executor": {
            "provider": os.getenv("EXECUTOR_MODEL_PROVIDER", default_provider),
            "model_name": os.getenv("EXECUTOR_MODEL_NAME", "gpt-4-turbo-preview"),
            "temperature": 0.5,
        },
        "evaluator": {
            "provider": os.getenv("EVALUATOR_MODEL_PROVIDER", default_provider),
            "model_name": os.getenv("EVALUATOR_MODEL_NAME", "gpt-4-turbo-preview"),
            "temperature": 0.3,
        },
        "reflector": {
            "provider": os.getenv("REFLECTOR_MODEL_PROVIDER", default_provider),
            "model_name": os.getenv("REFLECTOR_MODEL_NAME", "gpt-4-turbo-preview"),
            "temperature": 0.4,
        }
    }
    
    return llm_configs

def main():
    """Run an example of the Reflexion agent for chess analysis."""
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent

    # Set prompt directory path (using src directory)
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
    
    # Define a challenging chess analysis task
    # This is a famous position from the game Kasparov vs. Topalov, 1999
    # Known for the "Kasparov's Immortal" or "the moving rook sacrifice"
    task = """
    Analyze this chess position and find the best move for White. Explain your reasoning step by step.
    
    Position in FEN notation:
    r1b2rk1/pp2ppbp/1qn3p1/2pP4/2P1P3/2N2N2/PP2BPPP/R1BQ1RK1 w - - 0 1
    
    White to move. Evaluate the position, calculate the key variations, and suggest the best move.
    Ensure your analysis includes key tactical and strategic elements and considers potential defensive resources for Black.
    """
    
    logger.info("Running Reflexion agent on a chess analysis task")
    print(f"\nTASK: {task}\n")
    print("Running Reflexion agent with up to 3 trials...\n")
    
    # Run the agent
    result = agent.run(task)
    
    # Display the results
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    
    print(f"\nNumber of trials completed: {result['metadata']['trials_completed']}")
    
    print("\n" + "="*80)
    print("FINAL ANALYSIS")
    print("="*80 + "\n")
    
    print(result["output"])
    
    print("\n" + "="*80)
    print("REFLECTION JOURNEY")
    print("="*80 + "\n")
    
    for i, reflection in enumerate(result["metadata"]["reflections"]):
        print(f"Reflection {i+1}:")
        print("-" * 40)
        print(reflection)
        print("\n")

if __name__ == "__main__":
    main()