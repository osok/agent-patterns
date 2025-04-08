"""
Example demonstrating the LATS (Language Agent Tree Search) agent pattern.

This example shows how to initialize and use the LATS agent for
solving problems that benefit from exploring multiple reasoning paths.
"""

import os
from dotenv import load_dotenv
from agent_patterns.patterns.lats_agent import LATSAgent
from langgraph.errors import GraphRecursionError

# Load environment variables
load_dotenv()

def main():
    """Run the LATS agent example."""
    # Configure the LLMs for different roles
    llm_configs = {
        "thinking": {
            "provider": os.getenv("THINKING_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("THINKING_MODEL_NAME", "gpt-4-turbo"),
        },
        "evaluation": {
            "provider": os.getenv("EVALUATION_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("EVALUATION_MODEL_NAME", "gpt-4-turbo"),
        }
    }
    
    # Create the LATS agent with custom parameters
    agent = LATSAgent(
        llm_configs=llm_configs,
        max_iterations=15,  # Maximum number of search iterations
        max_depth=4,        # Maximum depth of tree exploration
        exploration_weight=1.0,  # UCB exploration parameter (higher = more exploration)
        n_expansions=3,     # Number of branches to create at each node
        prompt_dir="src/agent_patterns/prompts"  # Path to prompt templates
    )
    
    # Example problem
    problem = "Develop a strategy to increase user engagement on a social media platform"
    
    print("\n" + "="*80)
    print(f"PROBLEM: {problem}")
    print("="*80)
    
    # Configuration with higher recursion limit
    config = {"recursion_limit": 100}
    
    # Run the agent with error handling
    try:
        result = agent.run(problem, config=config)
        
        # Print the result
        print("\n" + "="*80)
        print("SOLUTION:")
        print("="*80)
        print(result)
    except GraphRecursionError as e:
        print("\n" + "="*80)
        print("ERROR: Graph recursion limit reached.")
        print("The example requires a higher recursion limit to complete.")
        print("Please increase the recursion_limit parameter or reduce the max_iterations/max_depth.")
        print("="*80)

if __name__ == "__main__":
    main() 