"""
Example usage of the STORM agent pattern.

This example demonstrates how to use the STORMAgent to create comprehensive
multi-perspective reports on complex topics.
"""

import os
from dotenv import load_dotenv

from agent_patterns.patterns import STORMAgent


def main():
    """Run the STORM agent example."""
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

    # Define simple retrieval tools (in production, use real APIs)
    def search_tool(query: str) -> str:
        """Simulated search tool."""
        return f"[Simulated research findings for: {query}]"

    retrieval_tools = {
        "search": search_tool
    }

    print("Initializing STORM Agent...")
    agent = STORMAgent(
        llm_configs=llm_configs,
        retrieval_tools=retrieval_tools,
        num_perspectives=4
    )

    # Example 1: Technical Report
    print("\n" + "=" * 80)
    print("Example 1: Comprehensive Technical Report")
    print("=" * 80)
    task1 = "Create a comprehensive report on quantum computing applications in cryptography"
    print(f"\nTask: {task1}")
    print("\nRunning agent (will generate multi-perspective report with research)...")

    try:
        result1 = agent.run(task1)
        print(f"\nFinal Result:\n{result1}")
    except Exception as e:
        print(f"\nError: {e}")

    print("\nNote: If you see an error about missing API keys, make sure to create a .env file with your LLM API keys.")

    # Example 2: Industry Analysis
    print("\n" + "=" * 80)
    print("Example 2: Industry Analysis Report")
    print("=" * 80)
    task2 = "Analyze the impact of artificial intelligence on the healthcare industry"
    print(f"\nTask: {task2}")
    print("\nRunning agent...")

    try:
        result2 = agent.run(task2)
        print(f"\nFinal Result:\n{result2}")
    except Exception as e:
        print(f"\nError: {e}")

    # Example 3: Educational Content
    print("\n" + "=" * 80)
    print("Example 3: Educational Content Creation")
    print("=" * 80)
    task3 = "Write a comprehensive guide to sustainable agriculture practices"
    print(f"\nTask: {task3}")
    print("\nRunning agent...")

    try:
        result3 = agent.run(task3)
        print(f"\nFinal Result:\n{result3}")
    except Exception as e:
        print(f"\nError: {e}")

    print("\n" + "=" * 80)
    print("STORM Agent Examples Complete!")
    print("=" * 80)

    print("\nNote: The STORM agent creates comprehensive reports by:")
    print("  1. Generating an outline")
    print("  2. Creating questions from multiple perspectives (expert, critic, etc.)")
    print("  3. Retrieving information for each question")
    print("  4. Synthesizing all information into a structured report")


if __name__ == "__main__":
    main()
