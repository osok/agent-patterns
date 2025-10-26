"""Example usage of the REWOOAgent pattern.

This script demonstrates how to use the REWOO (Reason Without Observation) pattern
to separate planning from execution for cost-effective multi-tool workflows.
"""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from agent_patterns.patterns.rewoo_agent import REWOOAgent


def setup_environment():
    """Load environment variables from .env file."""
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
    # Simulated search responses
    responses = {
        "ceo of openai": "Sam Altman is the CEO of OpenAI.",
        "ceo of anthropic": "Dario Amodei is the CEO of Anthropic.",
        "ceo of microsoft": "Satya Nadella is the CEO of Microsoft.",
        "sam altman": "Sam Altman is an American entrepreneur and investor, CEO of OpenAI since 2019.",
        "dario amodei": "Dario Amodei is the CEO of Anthropic, former VP of Research at OpenAI.",
        "population of tokyo": "Tokyo has a population of approximately 14 million people in the city proper, and 37 million in the metropolitan area.",
        "capital of france": "Paris is the capital of France.",
        "latest ai announcements": "Recent AI announcements include GPT-4 Turbo, Claude 3, and Gemini Pro.",
    }

    # Check for keyword matches
    query_lower = query.lower()
    for key, value in responses.items():
        if key in query_lower:
            return value

    return f"Search results for '{query}': [Simulated search - no specific data]"


def calculator_tool(expression: str) -> float:
    """Simulated calculator tool.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Result of the calculation
    """
    try:
        # Handle common text patterns
        expression = expression.replace("million", "* 1000000")
        expression = expression.replace("approximately", "")

        result = eval(expression)
        return float(result)
    except Exception as e:
        return f"Error: {str(e)}"


def stock_lookup_tool(symbol: str) -> str:
    """Simulated stock lookup tool.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Stock price information
    """
    stocks = {
        "MSFT": "$378.91 (Microsoft Corporation)",
        "GOOGL": "$141.80 (Alphabet Inc.)",
        "AAPL": "$189.95 (Apple Inc.)",
        "NVDA": "$495.22 (NVIDIA Corporation)",
    }

    symbol_upper = symbol.upper()
    if symbol_upper in stocks:
        return stocks[symbol_upper]

    return f"Stock price for {symbol}: [Simulated data - $100.00]"


def company_info_tool(company_name: str) -> str:
    """Simulated company information tool.

    Args:
        company_name: Name of the company

    Returns:
        Company information
    """
    companies = {
        "openai": {
            "founded": "2015",
            "headquarters": "San Francisco, California",
            "focus": "Artificial Intelligence research and deployment"
        },
        "microsoft": {
            "founded": "1975",
            "headquarters": "Redmond, Washington",
            "focus": "Software, cloud computing, and AI"
        },
        "anthropic": {
            "founded": "2021",
            "headquarters": "San Francisco, California",
            "focus": "AI safety and research"
        }
    }

    company_lower = company_name.lower()
    for key, info in companies.items():
        if key in company_lower:
            return f"{company_name} was founded in {info['founded']}, headquartered in {info['headquarters']}, focusing on {info['focus']}."

    return f"Company information for {company_name}: [Simulated data]"


def example_1_simple_workflow():
    """Example 1: Simple multi-step query with placeholders.

    Demonstrates basic REWOO workflow where the Worker plans with
    placeholders, Solver executes, and Worker integrates results.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Simple Multi-Step Query")
    print("=" * 80)

    llm_configs = {
        "thinking": {
            "provider": "openai",
            "model": os.getenv("OPENAI_THINKING_MODEL", "gpt-4"),
            "temperature": 0.7
        },
        "solver": {
            "provider": "openai",
            "model": os.getenv("OPENAI_SOLVER_MODEL", "gpt-3.5-turbo"),
            "temperature": 0.3
        }
    }

    tools = {
        "search_tool": search_tool,
        "calculator_tool": calculator_tool
    }

    agent = REWOOAgent(
        llm_configs=llm_configs,
        tools=tools
    )

    task = "Find the CEO of OpenAI and tell me about them"

    print(f"\nTask: {task}")
    print("\nREWOO Workflow:")
    print("1. Worker plans with placeholder: {ceo_name}")
    print("2. Solver executes search tool")
    print("3. Worker integrates actual result")
    print("\nExecuting...")

    result = agent.run(task)

    print(f"\nFinal Answer:\n{result}")


def example_2_dependent_queries():
    """Example 2: Dependent queries where results feed into next steps.

    Demonstrates how REWOO handles dependencies where one query's
    result is used as input for subsequent queries.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Dependent Queries")
    print("=" * 80)

    llm_configs = {
        "thinking": {
            "provider": "openai",
            "model": os.getenv("OPENAI_THINKING_MODEL", "gpt-4"),
            "temperature": 0.7
        },
        "solver": {
            "provider": "openai",
            "model": os.getenv("OPENAI_SOLVER_MODEL", "gpt-3.5-turbo"),
            "temperature": 0.3
        }
    }

    tools = {
        "search_tool": search_tool,
        "company_info_tool": company_info_tool
    }

    agent = REWOOAgent(
        llm_configs=llm_configs,
        tools=tools
    )

    task = "Find the CEO of Anthropic and get company information about Anthropic"

    print(f"\nTask: {task}")
    print("\nREWOO Workflow:")
    print("1. Worker creates plan: find CEO -> {ceo}, get company info -> {company_info}")
    print("2. Solver executes both tools (can be parallel)")
    print("3. Worker combines results")
    print("\nExecuting...")

    result = agent.run(task)

    print(f"\nFinal Answer:\n{result}")


def example_3_calculation_workflow():
    """Example 3: Mixed workflow with search and calculations.

    Demonstrates REWOO with heterogeneous tool types including
    search and mathematical calculations.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Mixed Workflow with Calculations")
    print("=" * 80)

    llm_configs = {
        "thinking": {
            "provider": "openai",
            "model": os.getenv("OPENAI_THINKING_MODEL", "gpt-4"),
            "temperature": 0.7
        },
        "solver": {
            "provider": "openai",
            "model": os.getenv("OPENAI_SOLVER_MODEL", "gpt-3.5-turbo"),
            "temperature": 0.3
        }
    }

    tools = {
        "search_tool": search_tool,
        "calculator_tool": calculator_tool
    }

    agent = REWOOAgent(
        llm_configs=llm_configs,
        tools=tools
    )

    task = "Find the population of Tokyo and calculate what triple that number would be"

    print(f"\nTask: {task}")
    print("\nREWOO Workflow:")
    print("1. Worker plans: search population -> {population}, calculate triple -> {tripled}")
    print("2. Solver executes search first, then calculation using {population}")
    print("3. Worker presents final answer")
    print("\nExecuting...")

    result = agent.run(task)

    print(f"\nFinal Answer:\n{result}")


def example_4_cost_optimization():
    """Example 4: Cost optimization with cheaper solver model.

    Demonstrates REWOO's cost-saving benefit by using an expensive
    model (GPT-4) only for planning and integration, while using a
    cheaper model (GPT-3.5-turbo) for execution.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Cost Optimization")
    print("=" * 80)

    llm_configs = {
        "thinking": {
            "provider": "openai",
            "model": "gpt-4",  # Expensive model for planning/integration
            "temperature": 0.7
        },
        "solver": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",  # Cheaper model for execution
            "temperature": 0.3
        }
    }

    tools = {
        "search_tool": search_tool,
        "stock_lookup_tool": stock_lookup_tool,
        "calculator_tool": calculator_tool
    }

    agent = REWOOAgent(
        llm_configs=llm_configs,
        tools=tools
    )

    task = "Find the CEO of Microsoft and look up Microsoft's stock price"

    print(f"\nTask: {task}")
    print("\nCost Optimization:")
    print("- GPT-4 (expensive) used 2x: for planning and integration")
    print("- GPT-3.5 (cheap) used for tool execution")
    print("- Tools may use direct Python code (free)")
    print("\nCompare to ReAct: GPT-4 would be called at every iteration!")
    print("\nExecuting...")

    result = agent.run(task)

    print(f"\nFinal Answer:\n{result}")


def example_5_anthropic_models():
    """Example 5: Using Anthropic Claude models.

    Demonstrates REWOO with Claude models instead of OpenAI.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Using Anthropic Claude Models")
    print("=" * 80)

    llm_configs = {
        "thinking": {
            "provider": "anthropic",
            "model": os.getenv("ANTHROPIC_THINKING_MODEL", "claude-3-5-sonnet-20241022"),
            "temperature": 0.7
        },
        "solver": {
            "provider": "anthropic",
            "model": os.getenv("ANTHROPIC_SOLVER_MODEL", "claude-3-5-sonnet-20241022"),
            "temperature": 0.3
        }
    }

    tools = {
        "search_tool": search_tool,
        "company_info_tool": company_info_tool
    }

    agent = REWOOAgent(
        llm_configs=llm_configs,
        tools=tools
    )

    task = "Tell me about the CEO of Anthropic and the company itself"

    print(f"\nTask: {task}")
    print("\nUsing Claude models for both Worker and Solver...")
    print("\nExecuting...")

    result = agent.run(task)

    print(f"\nFinal Answer:\n{result}")


def main():
    """Run all examples."""
    setup_environment()

    print("\n" + "=" * 80)
    print("REWOO Agent Examples")
    print("=" * 80)
    print("\nThe REWOO pattern separates reasoning (Worker) from execution (Solver)")
    print("to reduce costs by minimizing expensive LLM calls.")
    print("\nKey Benefits:")
    print("- Worker creates plan with placeholders (1 expensive LLM call)")
    print("- Solver executes tools (cheap or free)")
    print("- Worker integrates results (1 expensive LLM call)")
    print("- Total: Only 2 expensive LLM calls regardless of complexity!")

    try:
        example_1_simple_workflow()
    except Exception as e:
        print(f"\nExample 1 failed: {e}")

    try:
        example_2_dependent_queries()
    except Exception as e:
        print(f"\nExample 2 failed: {e}")

    try:
        example_3_calculation_workflow()
    except Exception as e:
        print(f"\nExample 3 failed: {e}")

    try:
        example_4_cost_optimization()
    except Exception as e:
        print(f"\nExample 4 failed: {e}")

    # Only run Anthropic example if API key is available
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            example_5_anthropic_models()
        except Exception as e:
            print(f"\nExample 5 failed: {e}")
    else:
        print("\n" + "=" * 80)
        print("EXAMPLE 5: Skipped (ANTHROPIC_API_KEY not set)")
        print("=" * 80)

    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
