"""
Example demonstrating the LATS (Language Agent Tree Search) agent for medical diagnosis reasoning.

This example shows how LATS can systematically explore multiple diagnostic hypotheses
and treatment options for a medical case by reasoning through different pathways.
"""

import os
from dotenv import load_dotenv
from agent_patterns.patterns.lats_agent import LATSAgent
from langgraph.errors import GraphRecursionError

# Load environment variables
load_dotenv()

def main():
    """Run the LATS agent for medical diagnosis reasoning."""
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
    
    # Create the LATS agent with parameters optimized for medical reasoning
    agent = LATSAgent(
        llm_configs=llm_configs,
        max_iterations=20,      # Reduced iterations to avoid recursion issues
        max_depth=5,            # Reasonable depth for clinical reasoning
        exploration_weight=0.8, # Lower exploration to focus on more likely diagnoses
        n_expansions=5,         # More branches to consider various diagnostic possibilities
        prompt_dir="src/agent_patterns/prompts"  # Path to prompt templates
    )
    
    # Medical case to diagnose
    problem = """
A 45-year-old female presents with progressive fatigue, weight gain of 15 pounds over 6 months,
dry skin, hair loss, and feeling cold even in warm environments. Lab results show:
- TSH: 8.5 mIU/L (normal 0.4-4.0)
- Free T4: 0.7 ng/dL (normal 0.8-1.8)
- Cholesterol: 245 mg/dL (normal <200)
- Anti-TPO antibodies: Positive

The patient has a family history of autoimmune disorders. She takes no medications
except occasional ibuprofen for joint pain. She reports having trouble concentrating at work
and feeling depressed. Physical exam shows bradycardia (58 bpm) and mild peripheral edema.

Provide a diagnosis, explanation of the underlying pathophysiology, recommended
additional tests if needed, and a comprehensive treatment plan including lifestyle modifications.
"""
    
    print("\n" + "="*80)
    print("MEDICAL CASE:")
    print("="*80)
    print(problem)
    
    # Configuration with higher recursion limit
    config = {"recursion_limit": 100}
    
    # Run the agent with error handling
    try:
        result = agent.run(problem, config=config)
        
        # Print the result
        print("\n" + "="*80)
        print("DIAGNOSIS AND TREATMENT PLAN:")
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