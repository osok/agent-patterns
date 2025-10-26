"""
Example usage of the ReAct agent pattern.

This example demonstrates how to use the ReActAgent to answer questions
that require tool use and reasoning.
"""

import os
from dotenv import load_dotenv

from agent_patterns.patterns import ReActAgent


def search_tool(query: str) -> str:
    """
    Mock search tool that simulates web search.

    In a real implementation, this would call an actual search API.
    """
    # Simulate search results
    mock_results = {
        "weather in paris": "Current weather in Paris: 18°C, partly cloudy, light breeze",
        "population of tokyo": "Tokyo metropolitan area has approximately 37 million people",
        "capital of france": "The capital of France is Paris",
        "python programming": "Python is a high-level, interpreted programming language",
    }

    query_lower = query.lower()
    for key, value in mock_results.items():
        if key in query_lower:
            return value

    return f"Search results for '{query}': No specific results found in mock database"


def calculator_tool(expression: str) -> str:
    """
    Simple calculator tool that evaluates mathematical expressions.
    """
    try:
        # WARNING: Using eval() is dangerous in production!
        # This is just for demonstration purposes
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"


def main():
    """Run the ReAct agent example."""
    # Load environment variables
    load_dotenv()

    # Configure LLMs
    llm_configs = {
        "thinking": {
            "provider": os.getenv("THINKING_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("THINKING_MODEL_NAME", "gpt-4-turbo"),
            "temperature": float(os.getenv("THINKING_TEMPERATURE", "0.7")),
        }
    }

    # Define available tools
    tools = {
        "search_tool": search_tool,
        "calculator": calculator_tool,
    }

    # Create ReAct agent
    print("Initializing ReAct Agent...")
    agent = ReActAgent(
        llm_configs=llm_configs,
        tools=tools,
        max_iterations=5,
        prompt_dir="agent_patterns/prompts",
    )

    # Example 1: Simple search question
    print("\n" + "=" * 80)
    print("Example 1: Simple Question")
    print("=" * 80)
    question1 = "What is the current weather in Paris?"
    print(f"\nQuestion: {question1}")
    print("\nRunning agent...")

    try:
        answer1 = agent.run(question1)
        print(f"\nFinal Answer: {answer1}")
    except Exception as e:
        print(f"\nError: {str(e)}")
        print(
            "\nNote: If you see an error about missing API keys, "
            "make sure to create a .env file with your LLM API keys."
        )

    # Example 2: Question requiring calculation
    print("\n" + "=" * 80)
    print("Example 2: Question with Calculation")
    print("=" * 80)
    question2 = "What is the population of Tokyo divided by 10?"
    print(f"\nQuestion: {question2}")
    print("\nRunning agent...")

    try:
        answer2 = agent.run(question2)
        print(f"\nFinal Answer: {answer2}")
    except Exception as e:
        print(f"\nError: {str(e)}")

    # Example 3: Multi-step reasoning
    print("\n" + "=" * 80)
    print("Example 3: Multi-step Reasoning")
    print("=" * 80)
    question3 = "What is the capital of France and what is the weather there?"
    print(f"\nQuestion: {question3}")
    print("\nRunning agent...")

    try:
        answer3 = agent.run(question3)
        print(f"\nFinal Answer: {answer3}")
    except Exception as e:
        print(f"\nError: {str(e)}")

    print("\n" + "=" * 80)
    print("ReAct Agent Examples Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
