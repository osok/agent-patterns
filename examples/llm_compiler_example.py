"""Example usage of the LLMCompilerAgent pattern.

This script demonstrates how to use the LLMCompiler pattern to execute
complex multi-tool workflows using DAG-based execution.
"""

import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

from agent_patterns.patterns.llm_compiler_agent import LLMCompilerAgent


def setup_environment():
    """Load environment variables from .env file."""
    # Try to load from project root
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"

    if env_path.exists():
        load_dotenv(env_path)
    else:
        print(f"Warning: .env file not found at {env_path}")
        print("Make sure to set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables")


# Example tool functions
def search_tool(query: str) -> str:
    """Simulated search tool that returns information about a query.

    Args:
        query: The search query

    Returns:
        Search results as a string
    """
    # In production, this would call a real search API
    responses = {
        "population of Tokyo": "The population of Tokyo is approximately 14 million people (as of 2023).",
        "capital of France": "Paris is the capital and largest city of France.",
        "speed of light": "The speed of light in a vacuum is approximately 299,792,458 meters per second.",
        "Python programming language": "Python is a high-level, interpreted programming language created by Guido van Rossum in 1991.",
    }

    # Simple keyword matching
    for key, value in responses.items():
        if key.lower() in query.lower():
            return value

    return f"Search results for '{query}': [Simulated search result - no specific data available]"


def calculator_tool(expression: str) -> float:
    """Simulated calculator tool that evaluates mathematical expressions.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Result of the calculation

    Note:
        This is a simplified version. In production, use a safe expression parser.
    """
    try:
        # Replace common patterns
        expression = expression.replace("million", "* 1000000")
        expression = expression.replace("approximately", "")

        # Safe evaluation (in production, use ast.literal_eval or similar)
        result = eval(expression)
        return float(result)
    except Exception as e:
        return f"Error: {str(e)}"


def weather_tool(location: str) -> str:
    """Simulated weather tool that returns weather information.

    Args:
        location: Location to get weather for

    Returns:
        Weather information as a string
    """
    # Simulated weather data
    weather_data = {
        "Tokyo": "Sunny, 22°C (72°F), Humidity: 65%",
        "Paris": "Partly cloudy, 18°C (64°F), Humidity: 70%",
        "New York": "Rainy, 15°C (59°F), Humidity: 85%",
    }

    for city, weather in weather_data.items():
        if city.lower() in location.lower():
            return f"Weather in {city}: {weather}"

    return f"Weather in {location}: [Simulated data - Clear, 20°C (68°F)]"


def translation_tool(text: str, target_language: str = "English") -> str:
    """Simulated translation tool.

    Args:
        text: Text to translate
        target_language: Target language for translation

    Returns:
        Translated text
    """
    # Simulated translations
    if "French" in target_language:
        if "hello" in text.lower():
            return "Bonjour"
        return f"[Translation to French]: {text}"

    if "Spanish" in target_language:
        if "hello" in text.lower():
            return "Hola"
        return f"[Translation to Spanish]: {text}"

    return f"[Translation to {target_language}]: {text}"


def example_1_simple_calculation():
    """Example 1: Simple multi-step calculation task.

    Demonstrates basic DAG execution with sequential dependencies.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Simple Multi-Step Calculation")
    print("=" * 80)

    # Configure LLMs - use provider and models from .env
    llm_configs = {
        "thinking": {
            "provider": os.getenv("THINKING_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("THINKING_MODEL_NAME", "gpt-4o"),
            "temperature": float(os.getenv("THINKING_TEMPERATURE", "0.7"))
        },
        "documentation": {
            "provider": os.getenv("DOCUMENTATION_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("DOCUMENTATION_MODEL_NAME", "gpt-4o-mini"),
            "temperature": float(os.getenv("DOCUMENTATION_TEMPERATURE", "0.3"))
        }
    }

    # Define tools
    tools = {
        "search_tool": search_tool,
        "calculator_tool": calculator_tool
    }

    # Create agent
    agent = LLMCompilerAgent(
        llm_configs=llm_configs,
        tools=tools
    )

    # Run task
    task = "Find the population of Tokyo and calculate what double that number would be"

    print(f"\nTask: {task}")
    print("\nExecuting LLMCompiler workflow...")

    result = agent.run(task)

    print(f"\nFinal Answer:\n{result}")


def example_2_parallel_execution():
    """Example 2: Task with parallel execution opportunities.

    Demonstrates how LLMCompiler can identify independent steps that
    can be executed in parallel.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Parallel Execution Opportunity")
    print("=" * 80)

    # Configure LLMs - use provider and models from .env
    llm_configs = {
        "thinking": {
            "provider": os.getenv("THINKING_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("THINKING_MODEL_NAME", "gpt-4o"),
            "temperature": float(os.getenv("THINKING_TEMPERATURE", "0.7"))
        },
        "documentation": {
            "provider": os.getenv("DOCUMENTATION_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("DOCUMENTATION_MODEL_NAME", "gpt-4o-mini"),
            "temperature": float(os.getenv("DOCUMENTATION_TEMPERATURE", "0.3"))
        }
    }

    tools = {
        "search_tool": search_tool,
        "weather_tool": weather_tool,
        "calculator_tool": calculator_tool
    }

    agent = LLMCompilerAgent(
        llm_configs=llm_configs,
        tools=tools
    )

    task = "Get the weather in Tokyo and Paris, then tell me which city is warmer"

    print(f"\nTask: {task}")
    print("\nExecuting LLMCompiler workflow...")
    print("Note: Weather lookups for Tokyo and Paris can execute in parallel")

    result = agent.run(task)

    print(f"\nFinal Answer:\n{result}")


def example_3_complex_workflow():
    """Example 3: Complex multi-tool workflow.

    Demonstrates a more complex scenario with multiple tool types
    and dependencies.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Complex Multi-Tool Workflow")
    print("=" * 80)

    # Configure LLMs - use provider and models from .env
    llm_configs = {
        "thinking": {
            "provider": os.getenv("THINKING_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("THINKING_MODEL_NAME", "gpt-4o"),
            "temperature": float(os.getenv("THINKING_TEMPERATURE", "0.7"))
        },
        "documentation": {
            "provider": os.getenv("DOCUMENTATION_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("DOCUMENTATION_MODEL_NAME", "gpt-4o-mini"),
            "temperature": float(os.getenv("DOCUMENTATION_TEMPERATURE", "0.3"))
        }
    }

    tools = {
        "search_tool": search_tool,
        "calculator_tool": calculator_tool,
        "weather_tool": weather_tool,
        "translation_tool": translation_tool
    }

    agent = LLMCompilerAgent(
        llm_configs=llm_configs,
        tools=tools
    )

    task = (
        "Find information about Python programming language, "
        "search for the speed of light, calculate the speed of light divided by 1000, "
        "and get the weather in Paris"
    )

    print(f"\nTask: {task}")
    print("\nExecuting LLMCompiler workflow...")
    print("Note: Multiple independent searches can execute in parallel")

    result = agent.run(task)

    print(f"\nFinal Answer:\n{result}")


def example_4_anthropic_model():
    """Example 4: Using Anthropic Claude models.

    Demonstrates how to use Claude instead of OpenAI models.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Using Anthropic Claude Models")
    print("=" * 80)

    llm_configs = {
        "thinking": {
            "provider": "anthropic",
            "model_name": os.getenv("THINKING_MODEL_NAME", "claude-opus-4-1-20250805"),
            "temperature": 0.7
        },
        "documentation": {
            "provider": "anthropic",
            "model_name": os.getenv("DOCUMENTATION_MODEL_NAME", "claude-sonnet-4-5-20250929"),
            "temperature": 0.3
        }
    }

    tools = {
        "search_tool": search_tool,
        "calculator_tool": calculator_tool,
        "weather_tool": weather_tool
    }

    agent = LLMCompilerAgent(
        llm_configs=llm_configs,
        tools=tools
    )

    task = "Find the capital of France and get the weather there"

    print(f"\nTask: {task}")
    print("\nExecuting LLMCompiler workflow with Claude...")

    result = agent.run(task)

    print(f"\nFinal Answer:\n{result}")


def main():
    """Run all examples."""
    setup_environment()

    print("\n" + "=" * 80)
    print("LLMCompiler Agent Examples")
    print("=" * 80)
    print("\nThe LLMCompiler pattern constructs an execution graph (DAG) from tasks")
    print("and tools, enabling optimized execution with parallel opportunities.")

    # Run examples
    try:
        example_1_simple_calculation()
    except Exception as e:
        print(f"\nExample 1 failed: {e}")

    try:
        example_2_parallel_execution()
    except Exception as e:
        print(f"\nExample 2 failed: {e}")

    try:
        example_3_complex_workflow()
    except Exception as e:
        print(f"\nExample 3 failed: {e}")

    # Only run Anthropic example if API key is available
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            example_4_anthropic_model()
        except Exception as e:
            print(f"\nExample 4 failed: {e}")
    else:
        print("\n" + "=" * 80)
        print("EXAMPLE 4: Skipped (ANTHROPIC_API_KEY not set)")
        print("=" * 80)

    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
