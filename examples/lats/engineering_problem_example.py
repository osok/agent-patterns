"""
Example demonstrating the LATS (Language Agent Tree Search) agent for engineering problem solving.

This example shows how LATS can be used to explore multiple approaches to solve
a complex engineering problem by systematically exploring solution paths.
"""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



import os
from dotenv import load_dotenv
from agent_patterns.patterns.lats_agent import LATSAgent
from langgraph.errors import GraphRecursionError

# Load environment variables
load_dotenv()

def main():
    """Run the LATS agent for engineering problem solving."""
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
    
    # Create the LATS agent with custom parameters for thorough exploration
    agent = LATSAgent(
        llm_configs=llm_configs,
        max_iterations=15,     # Reduced iterations to avoid recursion issues
        max_depth=4,           # Reasonable depth for exploration
        exploration_weight=1.2, # Slightly higher exploration to consider diverse solutions
        n_expansions=4,        # More branches to consider multiple engineering approaches
        prompt_dir="src/agent_patterns/prompts"  # Path to prompt templates
    )
    
    # Engineering challenge: Design a sustainable urban transportation system
    problem = """Design a sustainable urban transportation system for a city of 1 million people
that reduces carbon emissions by at least 40% compared to traditional systems,
while maintaining affordability and accessibility for all residents.
Consider infrastructure requirements, costs, technology integration, and implementation timeline."""
    
    print("\n" + "="*80)
    print("ENGINEERING CHALLENGE:")
    print("="*80)
    print(problem)
    
    # Configuration with higher recursion limit
    config = {"recursion_limit": 100}
    
    # Run the agent with error handling
    try:
        result = agent.run(problem, config=config)
        
        # Print the result
        print("\n" + "="*80)
        print("PROPOSED SOLUTION:")
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