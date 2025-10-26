"""
Example usage of the Reflection agent pattern.

This example demonstrates how to use the ReflectionAgent to generate
and refine high-quality outputs through self-critique.
"""

import os
from dotenv import load_dotenv

from agent_patterns.patterns import ReflectionAgent


def main():
    """Run the Reflection agent example."""
    # Load environment variables
    load_dotenv()

    # Configure LLMs
    llm_configs = {
        "documentation": {
            "provider": os.getenv("DOCUMENTATION_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("DOCUMENTATION_MODEL_NAME", "gpt-3.5-turbo"),
            "temperature": float(os.getenv("DOCUMENTATION_TEMPERATURE", "0.7")),
        },
        "reflection": {
            "provider": os.getenv("REFLECTION_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("REFLECTION_MODEL_NAME", "gpt-4-turbo"),
            "temperature": float(os.getenv("REFLECTION_TEMPERATURE", "0.5")),
        },
    }

    # Create Reflection agent
    print("Initializing Reflection Agent...")
    agent = ReflectionAgent(
        llm_configs=llm_configs,
        max_reflection_cycles=1,
        prompt_dir="agent_patterns/prompts",
    )

    # Example 1: Story writing
    print("\n" + "=" * 80)
    print("Example 1: Creative Writing")
    print("=" * 80)
    task1 = "Write a short story (3-4 paragraphs) about a robot dog discovering friendship"
    print(f"\nTask: {task1}")
    print("\nRunning agent (this will generate, reflect, and refine)...")

    try:
        result1 = agent.run(task1)
        print(f"\nFinal Output:\n{result1}")
    except Exception as e:
        print(f"\nError: {str(e)}")
        print(
            "\nNote: If you see an error about missing API keys, "
            "make sure to create a .env file with your LLM API keys."
        )

    # Example 2: Technical explanation
    print("\n" + "=" * 80)
    print("Example 2: Technical Explanation")
    print("=" * 80)
    task2 = "Explain how blockchain technology works to someone with no technical background"
    print(f"\nTask: {task2}")
    print("\nRunning agent...")

    try:
        result2 = agent.run(task2)
        print(f"\nFinal Output:\n{result2}")
    except Exception as e:
        print(f"\nError: {str(e)}")

    # Example 3: Code documentation
    print("\n" + "=" * 80)
    print("Example 3: Code Documentation")
    print("=" * 80)
    task3 = """
    Write documentation for this Python function:

    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)

    Include: purpose, parameters, return value, and usage example.
    """
    print(f"\nTask: {task3}")
    print("\nRunning agent...")

    try:
        result3 = agent.run(task3)
        print(f"\nFinal Output:\n{result3}")
    except Exception as e:
        print(f"\nError: {str(e)}")

    print("\n" + "=" * 80)
    print("Reflection Agent Examples Complete!")
    print("=" * 80)
    print(
        "\nNote: The Reflection agent generates an initial response, "
        "critiques it, and then refines it based on the critique."
    )


if __name__ == "__main__":
    main()
