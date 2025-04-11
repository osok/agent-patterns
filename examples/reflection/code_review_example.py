"""
Advanced example demonstrating the Reflection Agent for code review.

This example shows how to use the Reflection Agent to perform a code review,
generating initial feedback and then refining it through reflection.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from agent_patterns.patterns.reflection_agent import ReflectionAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample code to review
SAMPLE_CODE = """
def calculate_statistics(numbers):
    '''Calculate basic statistics for a list of numbers.'''
    total = 0
    for num in numbers:
        total += num
    
    mean = total / len(numbers)
    
    # Calculate variance
    variance = 0
    for num in numbers:
        variance += (num - mean) ** 2
    variance = variance / len(numbers)
    
    # Calculate standard deviation
    std_dev = variance ** 0.5
    
    return {
        'mean': mean,
        'variance': variance,
        'standard_deviation': std_dev,
        'sum': total,
        'count': len(numbers)
    }

# Example usage
data = [1, 2, 3, 4, 5]
stats = calculate_statistics(data)
print(f"Statistics for {data}: {stats}")

# This will cause an error
empty_data = []
empty_stats = calculate_statistics(empty_data)
"""

def main():
    """Run the Reflection Agent for the code review task."""
    # Get the project root directory
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    project_root = current_dir.parent.parent
    
    # Try to find prompts directory - check both source and package paths
    src_prompt_dir = project_root / "src" / "agent_patterns" / "prompts"
    pkg_prompt_dir = project_root / "agent_patterns" / "prompts"
    
    prompt_dir = str(src_prompt_dir if src_prompt_dir.exists() else pkg_prompt_dir)
    
    # Configure LLMs for different roles in the agent
    llm_configs = {
        "generator": {
            "provider": "openai",
            "model_name": "gpt-4-turbo-preview",
            "temperature": 0.7
        },
        "critic": {
            "provider": "openai",
            "model_name": "gpt-4-turbo-preview", 
            "temperature": 0.3  # Lower temperature for more focused critique
        }
    }
    
    # Create the agent
    reflection_agent = ReflectionAgent(
        llm_configs=llm_configs,
        prompt_dir=prompt_dir,
        log_level=logging.INFO
    )
    
    # Define the code review task
    review_task = f"""
    Perform a comprehensive code review of the following Python function.
    Identify any bugs, inefficiencies, or improvements that could be made.
    Consider edge cases, exception handling, and performance.
    
    Code to review:
    ```python
    {SAMPLE_CODE}
    ```
    
    Provide specific recommendations and code examples for improvements.
    """
    
    logger.info("Running Reflection Agent for code review task")
    
    # Run the agent
    result = reflection_agent.run(review_task)
    
    # Display the result
    if "error" in result:
        logger.error("Agent execution failed: %s", result["error"])
    else:
        print("\n" + "="*80)
        print("CODE REVIEW TASK:")
        print("="*80)
        print(review_task)
        
        print("\n" + "="*80)
        print("FINAL CODE REVIEW RESULT:")
        print("="*80)
        print(result["output"])
    
if __name__ == "__main__":
    main()