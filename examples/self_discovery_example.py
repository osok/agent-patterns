"""
Example usage of the Self-Discovery agent pattern.

This example demonstrates how to use the SelfDiscoveryAgent which dynamically
selects and adapts reasoning modules for each specific task.
"""

import os
from dotenv import load_dotenv

from agent_patterns.patterns import SelfDiscoveryAgent


def main():
    """Run the Self-Discovery agent example."""
    # Load environment variables
    load_dotenv()

    # Configure LLMs
    llm_configs = {
        "thinking": {
            "provider": os.getenv("THINKING_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("THINKING_MODEL_NAME", "gpt-4o"),
            "temperature": float(os.getenv("THINKING_TEMPERATURE", "0.7")),
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

    print("Initializing Self-Discovery Agent...")
    agent = SelfDiscoveryAgent(llm_configs=llm_configs)

    # Example 1: Complex Analysis Task
    print("\n" + "=" * 80)
    print("Example 1: Complex Business Analysis")
    print("=" * 80)
    task1 = "Analyze the potential risks and opportunities of expanding a retail business into e-commerce"
    print(f"\nTask: {task1}")
    print("\nRunning agent (will discover and adapt relevant reasoning modules)...")

    try:
        result1 = agent.run(task1)
        print(f"\nFinal Result:\n{result1}")
    except Exception as e:
        print(f"\nError: {e}")

    print("\nNote: If you see an error about missing API keys, make sure to create a .env file with your LLM API keys.")

    # Example 2: Technical Problem
    print("\n" + "=" * 80)
    print("Example 2: Technical System Design")
    print("=" * 80)
    task2 = "Design a scalable microservices architecture for a real-time chat application"
    print(f"\nTask: {task2}")
    print("\nRunning agent...")

    try:
        result2 = agent.run(task2)
        print(f"\nFinal Result:\n{result2}")
    except Exception as e:
        print(f"\nError: {e}")

    # Example 3: Strategic Planning
    print("\n" + "=" * 80)
    print("Example 3: Educational Program Design")
    print("=" * 80)
    task3 = "Design a comprehensive online learning program for teaching data science to beginners"
    print(f"\nTask: {task3}")
    print("\nRunning agent...")

    try:
        result3 = agent.run(task3)
        print(f"\nFinal Result:\n{result3}")
    except Exception as e:
        print(f"\nError: {e}")

    print("\n" + "=" * 80)
    print("Self-Discovery Agent Examples Complete!")
    print("=" * 80)

    print("\nNote: The Self-Discovery agent dynamically selects reasoning modules")
    print("from a library of problem-solving approaches (break down, first principles,")
    print("pros & cons, etc.) and adapts them to the specific task at hand.")


if __name__ == "__main__":
    main()
