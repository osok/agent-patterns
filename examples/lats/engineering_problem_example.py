"""
Example demonstrating the LATS (Language Agent Tree Search) agent for engineering problem solving.

This example shows how LATS can be used to explore multiple approaches to solve
a complex engineering problem by systematically exploring solution paths.
"""

import os
from dotenv import load_dotenv
from agent_patterns.patterns.lats_agent import LATSAgent

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
        max_iterations=20,     # More iterations for deeper search
        max_depth=5,           # Deeper reasoning chains
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
    
    # Run the agent
    result = agent.run(problem)
    
    # Print the result
    print("\n" + "="*80)
    print("PROPOSED SOLUTION:")
    print("="*80)
    print(result)

if __name__ == "__main__":
    main() 