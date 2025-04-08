"""
Simple example of using the REWOO agent pattern.

This example demonstrates how to use the REWOO (Reasoning Without Observation) agent pattern
to perform a research task with a structured plan.
"""

import os
import sys
import logging
import time
from typing import Dict, Any, List

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agent_patterns.patterns.rewoo_agent import REWOOAgent
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleSearchTool:
    """Simple search tool that returns mock results."""
    
    def __init__(self):
        self.search_results = {
            "climate change": """
Climate change refers to long-term shifts in temperatures and weather patterns. 
These shifts may be natural, but since the 1800s, human activities have been 
the main driver of climate change, primarily due to the burning of fossil fuels 
like coal, oil, and gas, which produces heat-trapping gases.

Key effects include:
1. Rising global temperatures
2. Sea level rise
3. Increasing frequency and intensity of extreme weather events
4. Changes in precipitation patterns
5. Ocean acidification
6. Loss of biodiversity
            """,
            "global warming": """
Global warming is the long-term heating of Earth's climate system observed since 
the pre-industrial period due to human activities, primarily fossil fuel burning.

The average global temperature has increased by about 1.1°C since the pre-industrial era.
Scientists project that without significant mitigation, global warming could reach 
3-5°C by the end of the century.
            """,
            "climate solutions": """
Climate solutions include:
1. Transitioning to renewable energy sources (solar, wind, hydro)
2. Improving energy efficiency
3. Electrifying transportation
4. Sustainable agriculture practices
5. Reforestation and protecting existing forests
6. Carbon capture and storage technologies
7. Policy measures like carbon pricing
            """,
            "extreme weather": """
Extreme weather events related to climate change include:
1. More frequent and intense heat waves
2. Longer and more severe droughts
3. Increased flooding
4. More powerful hurricanes and tropical storms
5. Wildfires affecting larger areas
6. Reduced snowpack and earlier snowmelt
            """
        }
        
    def __call__(self, query: str, **kwargs) -> str:
        """Search for information based on query."""
        # Log the search
        logger.info(f"Searching for: {query}")
        
        # Find the best match in our mock database
        best_match = None
        best_score = 0
        
        for key, value in self.search_results.items():
            # Simple keyword matching (in a real implementation, use proper search)
            if key in query.lower():
                score = len(key)
                if score > best_score:
                    best_score = score
                    best_match = value
        
        # Return either the best match or a default response
        if best_match:
            return best_match
        
        return """
Climate change is a complex global issue. The Earth's average temperature
has increased by about 1.1°C since the pre-industrial era, causing various
environmental impacts. Solutions include reducing greenhouse gas emissions
and adapting to the changing climate.
        """


class SimpleCalculatorTool:
    """Simple calculator tool that evaluates mathematical expressions."""
    
    def __call__(self, expression: str, **kwargs) -> str:
        """Evaluate a mathematical expression."""
        try:
            # Log the calculation
            logger.info(f"Calculating: {expression}")
            
            # Use safe eval (in a real implementation, use a proper expression evaluator)
            allowed_names = {"abs": abs, "round": round, "max": max, "min": min}
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"The result of {expression} is {result}"
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"


def main():
    """Run the example."""
    # Get API key from environment
    api_key = None  # Always use mock mode for testing
    
    if not api_key:
        logger.warning("OPENAI_API_KEY not set. Using mock mode.")
        # Create mock implementation
        from unittest.mock import MagicMock
        
        # Create a mock LLM that gives pre-scripted responses
        mock_responses = {
            "planning": """
Step 1: Research basic information about climate change
Use the search tool to find general information about climate change.

Step 2: Research the specific effects of climate change
Use the search tool to find information about the effects of climate change, such as global warming, extreme weather, etc.

Step 3: Research potential solutions to climate change
Use the search tool to find information about potential solutions and mitigation strategies.

Step 4: Synthesize the information
Combine all the gathered information into a comprehensive summary.
            """,
            "execution": """
I'll search for basic information about climate change.

TOOL: search
query: climate change
            """,
            "final": """
# Effects of Climate Change: A Summary

Based on my research, climate change is having significant global impacts across multiple systems:

## Key Findings

1. **Global Temperature Rise**: The Earth's average temperature has increased by approximately 1.1°C since the pre-industrial era, primarily due to human activities like burning fossil fuels.

2. **Environmental Impacts**:
   - Rising sea levels threatening coastal communities
   - Increasing frequency and intensity of extreme weather events like hurricanes, floods, and droughts
   - Ocean acidification harming marine ecosystems
   - Loss of biodiversity and ecosystem disruption

3. **Potential Solutions**:
   - Transition to renewable energy sources (solar, wind, hydro)
   - Improve energy efficiency in buildings and transportation
   - Implement sustainable agriculture and forestry practices
   - Develop carbon capture technologies
   - Establish effective policy measures like carbon pricing

The scientific consensus indicates that immediate action is necessary to mitigate the most severe potential impacts, though some degree of adaptation will be required regardless of mitigation efforts.
            """
        }
        
        class MockLLM:
            def __init__(self, responses):
                self.responses = responses
                
            def invoke(self, messages):
                message_str = str(messages)
                
                if "planning" in message_str.lower() or "plan" in message_str.lower():
                    return mock_responses["planning"]
                elif "step" in message_str.lower() and "execution" in message_str.lower():
                    return mock_responses["execution"]
                elif "final" in message_str.lower() or "synthesize" in message_str.lower():
                    return mock_responses["final"]
                    
                return "Default response based on: " + str(messages)
        
        # Create mock LLMs
        planner_llm = MockLLM(mock_responses)
        solver_llm = MockLLM(mock_responses)
    else:
        # Create real OpenAI LLMs
        planner_llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=api_key
        )
        
        solver_llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.2,
            api_key=api_key
        )
    
    # Create tools
    search_tool = SimpleSearchTool()
    calculator_tool = SimpleCalculatorTool()
    
    # Create REWOO agent
    agent = REWOOAgent(
        llm_configs={
            "planner": planner_llm,
            "solver": solver_llm
        },
        tool_registry={
            "search": search_tool,
            "calculator": calculator_tool
        },
        prompt_dir="src/agent_patterns/prompts/REWOOAgent"
    )
    
    # Run the agent
    query = "Research the effects of climate change and summarize your findings."
    print(f"\nQuery: {query}\n")
    print("-" * 50)
    print("Starting REWOO agent execution...\n")
    
    start_time = time.time()
    result = agent.run(query)
    elapsed_time = time.time() - start_time
    
    print("\nResult:")
    print("-" * 50)
    print(result)
    print("-" * 50)
    print(f"Execution completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    main() 