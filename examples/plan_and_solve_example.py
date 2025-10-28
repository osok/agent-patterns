"""
Example usage of the Plan & Solve agent pattern.

This example demonstrates how to use the PlanAndSolveAgent for tasks
that benefit from separating planning from execution.
"""

import os
from dotenv import load_dotenv

from agent_patterns.patterns import PlanAndSolveAgent


def main():
    """Run the Plan & Solve agent example."""
    # Load environment variables
    load_dotenv()

    # Configure LLMs
    llm_configs = {
        "planning": {
            "provider": os.getenv("PLANNING_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("PLANNING_MODEL_NAME", "gpt-4o"),
            "temperature": float(os.getenv("PLANNING_TEMPERATURE", "0.5")),
        },
        "execution": {
            "provider": os.getenv("EXECUTION_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("EXECUTION_MODEL_NAME", "gpt-4o-mini"),
            "temperature": float(os.getenv("EXECUTION_TEMPERATURE", "0.3")),
        },
        "documentation": {
            "provider": os.getenv("DOCUMENTATION_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("DOCUMENTATION_MODEL_NAME", "gpt-4o-mini"),
            "temperature": float(os.getenv("DOCUMENTATION_TEMPERATURE", "0.7")),
        },
    }

    print("Initializing Plan & Solve Agent...")
    agent = PlanAndSolveAgent(llm_configs=llm_configs)

    # Example 1: Research Task
    print("\n" + "=" * 80)
    print("Example 1: Research and Analysis")
    print("=" * 80)
    task1 = "Research the benefits and drawbacks of solar energy, then write a balanced summary"
    print(f"\nTask: {task1}")
    print("\nRunning agent (this will plan steps, then execute each one)...")

    try:
        result1 = agent.run(task1)
        print(f"\nFinal Result:\n{result1}")
    except Exception as e:
        print(f"\nError: {e}")

    print("\nNote: If you see an error about missing API keys, make sure to create a .env file with your LLM API keys.")

    # Example 2: Multi-step Problem
    print("\n" + "=" * 80)
    print("Example 2: Complex Problem Solving")
    print("=" * 80)
    task2 = "Calculate the compound interest on $1000 invested for 5 years at 5% annual rate, then explain what the result means"
    print(f"\nTask: {task2}")
    print("\nRunning agent...")

    try:
        result2 = agent.run(task2)
        print(f"\nFinal Result:\n{result2}")
    except Exception as e:
        print(f"\nError: {e}")

    # Example 3: Content Creation
    print("\n" + "=" * 80)
    print("Example 3: Content Creation Task")
    print("=" * 80)
    task3 = "Create a step-by-step tutorial on how to make sourdough bread"
    print(f"\nTask: {task3}")
    print("\nRunning agent...")

    try:
        result3 = agent.run(task3)
        print(f"\nFinal Result:\n{result3}")
    except Exception as e:
        print(f"\nError: {e}")

    print("\n" + "=" * 80)
    print("Plan & Solve Agent Examples Complete!")
    print("=" * 80)

    print("\nNote: The Plan & Solve agent creates a multi-step plan first,")
    print("then executes each step sequentially. This is ideal for tasks")
    print("that require structured thinking and can be broken into clear steps.")


if __name__ == "__main__":
    main()
