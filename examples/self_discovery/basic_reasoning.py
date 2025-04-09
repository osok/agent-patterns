"""
Basic reasoning example for the Self-Discovery Agent pattern.

This example demonstrates how to use the Self-Discovery Agent pattern to solve
complex reasoning problems by letting the LLM select and compose reasoning structures.
"""

import logging
import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import json

from agent_patterns.patterns.self_discovery_agent import SelfDiscoveryAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def main():
    """Run the Self-Discovery Agent example."""
    # Configure the LLMs for discovery and execution
    llm_configs = {
        "discovery": {
            "provider": "openai",
            "model": "gpt-4o",  # Using GPT-4o for discovery
            "temperature": 0.2,
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
        "execution": {
            "provider": "openai",
            "model": "gpt-4o",  # Using GPT-4o for execution
            "temperature": 0.3,
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
    }

    # Define a path to custom reasoning modules if desired
    # reasoning_modules_path = "path/to/custom_modules.json"

    # Create the Self-Discovery Agent
    agent = SelfDiscoveryAgent(
        llm_configs=llm_configs,
        prompt_dir="src/agent_patterns/prompts",
        # reasoning_modules_path=reasoning_modules_path,  # Uncomment to use custom modules
        log_level=logging.INFO,
    )

    # Define a complex reasoning task
    task = """
    You're designing a new educational game for children aged 8-12 to teach them 
    about environmental sustainability. The game needs to be engaging, educational, 
    and promote positive environmental behaviors. Design the core game mechanics, 
    educational content, and how you'll measure its effectiveness.
    """

    # Alternatively, try a logical reasoning problem
    # task = """
    # There are five houses in a row, each with a different color. The people living
    # in these houses are of different nationalities, have different pets, drink
    # different beverages, and play different sports. Given the following clues:
    # 1. The Norwegian lives in the first house.
    # 2. The person who plays tennis lives in the blue house.
    # 3. The Spaniard owns a dog.
    # 4. Coffee is drunk in the green house.
    # 5. The Ukrainian drinks tea.
    # 6. The green house is immediately to the right of the ivory house.
    # 7. The person who plays cricket owns snails.
    # 8. The person who plays hockey lives in the yellow house.
    # 9. Milk is drunk in the middle house.
    # 10. The American lives in the first house on the right.
    # 11. The person who plays basketball lives in the house next to the house with a fox.
    # 12. The person who plays hockey lives in the house next to the house where the horse is kept.
    # 13. The person who plays golf drinks orange juice.
    # 14. The Japanese plays baseball.
    # 15. The Norwegian lives next to the blue house.
    # Determine who plays basketball.
    # """

    logger.info("Running Self-Discovery Agent with task: %s", task[:100] + "...")

    # Run the agent
    result = agent.run(task)

    # Check for errors
    if "error" in result:
        logger.error("Agent execution failed: %s", result["error"])
        return

    # Print the final answer
    print("\n\n=== FINAL ANSWER ===\n")
    print(result["output"])

    # Print the discovered reasoning structure
    print("\n\n=== DISCOVERED REASONING STRUCTURE ===\n")
    print(json.dumps(result["reasoning_structure"], indent=2))


def example_with_fake_streaming():
    """Simulate a streaming example by running each step with visual separation."""
    # Configure the LLMs for discovery and execution
    llm_configs = {
        "discovery": {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.2,
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
        "execution": {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.3,
            "api_key": os.getenv("OPENAI_API_KEY"),
        },
    }

    # Create the Self-Discovery Agent
    agent = SelfDiscoveryAgent(
        llm_configs=llm_configs,
        prompt_dir="src/agent_patterns/prompts",
        log_level=logging.INFO,
    )

    # Define a complex reasoning task
    task = """
    Design a sustainable urban transportation system for a city of 500,000 people
    that reduces carbon emissions by at least 30% within 5 years while improving
    mobility for all residents, including those with disabilities and low incomes.
    """

    print("\n\n=== TASK ===\n")
    print(task.strip())
    
    print("\n\n=== STAGE: SELECT MODULES ===\n")
    # Manually call the first step
    initial_state = {
        "input": task,
        "chat_history": [],
        "reasoning_modules": agent.reasoning_modules,
        "selected_modules": None,
        "adapted_modules": None,
        "reasoning_structure": None,
        "execution_result": None,
        "final_answer": None
    }
    selection_state = agent._select_reasoning_modules(initial_state)
    print("\nSelected Reasoning Modules:")
    for module in selection_state["selected_modules"]:
        print(f"- {module}")
    
    # Small delay for readability
    time.sleep(1)
    
    print("\n\n=== STAGE: ADAPT MODULES ===\n")
    adaptation_state = agent._adapt_reasoning_modules({**initial_state, **selection_state})
    print("\nAdapted Reasoning Modules:")
    print(adaptation_state["adapted_modules"][0])
    
    # Small delay for readability
    time.sleep(1)
    
    print("\n\n=== STAGE: IMPLEMENT STRUCTURE ===\n")
    implementation_state = agent._implement_reasoning_structure({**initial_state, **selection_state, **adaptation_state})
    print("\nReasoning Structure:")
    print(json.dumps(implementation_state["reasoning_structure"], indent=2))
    
    # Small delay for readability
    time.sleep(1)
    
    print("\n\n=== STAGE: EXECUTE STRUCTURE ===\n")
    execution_state = agent._execute_reasoning_structure({**initial_state, **selection_state, **adaptation_state, **implementation_state})
    print("\nExecution Result (first 500 chars):")
    result = execution_state["execution_result"]
    print(result[:500] + "..." if len(result) > 500 else result)
    
    # Small delay for readability
    time.sleep(1)
    
    print("\n\n=== STAGE: FORMAT FINAL ANSWER ===\n")
    final_state = agent._format_final_answer({**initial_state, **selection_state, **adaptation_state, **implementation_state, **execution_state})
    print("\nFinal Answer (first 200 chars):")
    answer = final_state["final_answer"]
    print(answer[:200] + "..." if len(answer) > 200 else answer)
    
    print("\n\n=== COMPLETE FINAL ANSWER ===\n")
    print(answer)


if __name__ == "__main__":
    # Run the main example
    main()
    
    # Run the "streaming" example
    # example_with_fake_streaming() 