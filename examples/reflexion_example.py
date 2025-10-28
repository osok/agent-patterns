"""
Example usage of the Reflexion agent pattern.

This example demonstrates how to use the ReflexionAgent which learns
from multiple trials by maintaining reflection memory.
"""

import os
from dotenv import load_dotenv

from agent_patterns.patterns import ReflexionAgent


def main():
    """Run the Reflexion agent example."""
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
        "reflection": {
            "provider": os.getenv("REFLECTION_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("REFLECTION_MODEL_NAME", "gpt-4o"),
            "temperature": float(os.getenv("REFLECTION_TEMPERATURE", "0.5")),
        },
        "documentation": {
            "provider": os.getenv("DOCUMENTATION_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("DOCUMENTATION_MODEL_NAME", "gpt-4o-mini"),
            "temperature": float(os.getenv("DOCUMENTATION_TEMPERATURE", "0.7")),
        },
    }

    print("Initializing Reflexion Agent...")
    agent = ReflexionAgent(llm_configs=llm_configs, max_trials=3)

    # Example 1: Problem Solving with Learning
    print("\n" + "=" * 80)
    print("Example 1: Complex Problem Solving")
    print("=" * 80)
    task1 = "Design a solution for reducing office energy consumption by 30%"
    print(f"\nTask: {task1}")
    print("\nRunning agent (will make multiple attempts, learning from each trial)...")

    try:
        result1 = agent.run(task1)
        print(f"\nFinal Result:\n{result1}")
    except Exception as e:
        print(f"\nError: {e}")

    print("\nNote: If you see an error about missing API keys, make sure to create a .env file with your LLM API keys.")

    # Example 2: Creative Task with Iteration
    print("\n" + "=" * 80)
    print("Example 2: Creative Writing with Improvement")
    print("=" * 80)
    task2 = "Write a compelling opening paragraph for a sci-fi novel about AI consciousness"
    print(f"\nTask: {task2}")
    print("\nRunning agent...")

    try:
        result2 = agent.run(task2)
        print(f"\nFinal Result:\n{result2}")
    except Exception as e:
        print(f"\nError: {e}")

    # Example 3: Strategy Development
    print("\n" + "=" * 80)
    print("Example 3: Marketing Strategy Development")
    print("=" * 80)
    task3 = "Create a marketing strategy for a new sustainable clothing brand targeting Gen Z"
    print(f"\nTask: {task3}")
    print("\nRunning agent...")

    try:
        result3 = agent.run(task3)
        print(f"\nFinal Result:\n{result3}")
    except Exception as e:
        print(f"\nError: {e}")

    print("\n" + "=" * 80)
    print("Reflexion Agent Examples Complete!")
    print("=" * 80)

    print("\nNote: The Reflexion agent makes multiple attempts at solving the task,")
    print("learning from each trial by storing insights in reflection memory.")
    print("Each new attempt benefits from lessons learned in previous trials.")


if __name__ == "__main__":
    main()
