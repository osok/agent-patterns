"""
Example usage of the LATS (Language Agent Tree Search) pattern.

This example demonstrates how to use the LATSAgent which explores multiple
reasoning paths using tree search techniques.
"""

import os
from dotenv import load_dotenv

from agent_patterns.patterns import LATSAgent


def main():
    """Run the LATS agent example."""
    # Load environment variables
    load_dotenv()

    # Configure LLMs
    llm_configs = {
        "thinking": {
            "provider": os.getenv("THINKING_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("THINKING_MODEL_NAME", "gpt-4o"),
            "temperature": float(os.getenv("THINKING_TEMPERATURE", "0.7")),
        },
        "documentation": {
            "provider": os.getenv("DOCUMENTATION_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("DOCUMENTATION_MODEL_NAME", "gpt-4o-mini"),
            "temperature": float(os.getenv("DOCUMENTATION_TEMPERATURE", "0.7")),
        },
    }

    print("Initializing LATS Agent...")
    agent = LATSAgent(
        llm_configs=llm_configs,
        max_iterations=10,
        num_expansions=3
    )

    # Example 1: Complex Reasoning Task
    print("\n" + "=" * 80)
    print("Example 1: Multi-Path Problem Solving")
    print("=" * 80)
    task1 = "Design a solution for a smart home system that optimizes energy usage while maintaining comfort"
    print(f"\nTask: {task1}")
    print("\nRunning agent (will explore multiple reasoning paths via tree search)...")

    try:
        result1 = agent.run(task1)
        print(f"\nFinal Result:\n{result1}")
    except Exception as e:
        print(f"\nError: {e}")

    print("\nNote: If you see an error about missing API keys, make sure to create a .env file with your LLM API keys.")

    # Example 2: Strategic Planning
    print("\n" + "=" * 80)
    print("Example 2: Strategic Decision Making")
    print("=" * 80)
    task2 = "Develop a strategy for launching a new product in a competitive market"
    print(f"\nTask: {task2}")
    print("\nRunning agent...")

    try:
        result2 = agent.run(task2)
        print(f"\nFinal Result:\n{result2}")
    except Exception as e:
        print(f"\nError: {e}")

    # Example 3: Complex Analysis
    print("\n" + "=" * 80)
    print("Example 3: Deep Analysis Task")
    print("=" * 80)
    task3 = "Analyze the potential impacts of remote work on urban development over the next decade"
    print(f"\nTask: {task3}")
    print("\nRunning agent...")

    try:
        result3 = agent.run(task3)
        print(f"\nFinal Result:\n{result3}")
    except Exception as e:
        print(f"\nError: {e}")

    print("\n" + "=" * 80)
    print("LATS Agent Examples Complete!")
    print("=" * 80)

    print("\nNote: The LATS agent uses tree search to explore multiple reasoning paths,")
    print("evaluating and selecting the best solution. This is particularly effective")
    print("for complex tasks where exploring alternatives leads to better outcomes.")


if __name__ == "__main__":
    main()
