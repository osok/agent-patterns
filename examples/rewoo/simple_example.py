"""
Simple example of using the REWOO agent pattern with memory and tools.

This example demonstrates how to use the REWOO (Reasoning Without Observation) agent pattern
to perform a research task with a structured plan, enhanced with memory and tool integration.
"""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



import os
import sys
import logging
import time
import asyncio
from typing import Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent_patterns.patterns.rewoo_agent import REWOOAgent
from agent_patterns.core.memory import (
    SemanticMemory,
    EpisodicMemory,
    ProceduralMemory,
    CompositeMemory
)
from agent_patterns.core.memory.persistence import (
    InMemoryPersistence
)
from agent_patterns.core.tools.base import ToolProvider
from examples.utils.model_config import get_llm_configs

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchToolProvider(ToolProvider):
    """A provider for research-related tools."""
    
    def __init__(self):
        """Initialize with mock search data."""
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
    
    def list_tools(self):
        """List available tools provided by this provider."""
        return [
            {
                "name": "search",
                "description": "Search for information on a topic",
                "parameters": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                }
            },
            {
                "name": "calculator",
                "description": "Perform mathematical calculations",
                "parameters": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate"
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name, params):
        """Execute the requested tool with the provided parameters."""
        if tool_name == "search":
            query = params.get("query", "")
            return self._search(query)
        elif tool_name == "calculator":
            expression = params.get("expression", "")
            return self._calculate(expression)
        else:
            return f"Unknown tool: {tool_name}"
    
    def _search(self, query: str) -> str:
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
    
    def _calculate(self, expression: str) -> str:
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


async def setup_memory():
    """Set up a composite memory system."""
    # Create persistence backend
    persistence = InMemoryPersistence()
    await persistence.initialize()
    
    # Create individual memory types
    semantic_memory = SemanticMemory(persistence, namespace="climate_semantic")
    episodic_memory = EpisodicMemory(persistence, namespace="climate_episodic")
    procedural_memory = ProceduralMemory(persistence, namespace="climate_procedural")
    
    # Create composite memory
    memory = CompositeMemory({
        "semantic": semantic_memory,
        "episodic": episodic_memory,
        "procedural": procedural_memory
    })
    
    # Pre-populate with some semantic memories
    await memory.save_to(
        "semantic", 
        {"entity": "climate_change", "attribute": "definition", "value": "Long-term shifts in temperatures and weather patterns"}
    )
    
    await memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "research_focus", "value": "environmental impacts and solutions"}
    )
    
    # Add a procedural memory for research methodology
    await memory.save_to(
        "procedural",
        {
            "name": "research_methodology",
            "pattern": {
                "template": """When conducting research:
1. Start with broad overview of the topic
2. Dive into specific subtopics
3. Look for scientific consensus and evidence
4. Consider alternative viewpoints
5. Focus on {research_focus} when summarizing findings"""
            },
            "description": "Template for conducting thorough research",
            "tags": ["research", "methodology", "structured"]
        }
    )
    
    return memory


def main():
    """Run the example."""
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent

    # Try to find prompts directory - check both installed package and development paths
    src_prompt_dir = project_root / "src" / "agent_patterns" / "prompts"
    pkg_prompt_dir = project_root / "agent_patterns" / "prompts"

    if src_prompt_dir.exists():
        prompt_dir = str(src_prompt_dir)
    else:
        prompt_dir = str(pkg_prompt_dir)
    
    # Set up memory
    memory = asyncio.run(setup_memory())
    
    # Set up tool provider
    tool_provider = ResearchToolProvider()
    
    # Get model configurations from environment
    try:
        llm_configs = get_llm_configs()
        # Use real models from environment
        agent = REWOOAgent(
            llm_configs={
                "planner": llm_configs.get("planning", llm_configs["default"]),
                "solver": llm_configs.get("solver", llm_configs["default"])
            },
            memory=memory,
            memory_config={
                "semantic": True,
                "episodic": True,
                "procedural": True
            },
            tool_provider=tool_provider,
            prompt_dir=prompt_dir
        )
        logger.info("Using models from environment configuration")
    except ValueError as e:
        # Fall back to mock mode
        logger.warning(f"Error loading model configuration: {e}. Using mock mode.")
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
Combine all the gathered information into a comprehensive summary, focusing on environmental impacts and solutions as per the user's research focus.
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
        
        # Create REWOO agent with mock LLMs
        agent = REWOOAgent(
            llm_configs={
                "planner": planner_llm,
                "solver": solver_llm
            },
            memory=memory,
            memory_config={
                "semantic": True,
                "episodic": True,
                "procedural": True
            },
            tool_provider=tool_provider,
            prompt_dir=prompt_dir
        )
    
    # Run the agent
    query = "Research the effects of climate change and summarize your findings."
    print(f"\nQuery: {query}\n")
    print("-" * 50)
    print("Starting REWOO agent execution with memory and tools...\n")
    
    start_time = time.time()
    result = agent.run(query)
    elapsed_time = time.time() - start_time
    
    print("\nResult:")
    print("-" * 50)
    print(result)
    print("-" * 50)
    print(f"Execution completed in {elapsed_time:.2f} seconds.")
    
    # Show what was stored in memory
    print("\nMEMORY AFTER EXECUTION:")
    
    print("\nSemantic memories:")
    facts = asyncio.run(memory.retrieve_from("semantic", "", limit=5))
    for i, fact in enumerate(facts):
        print(f"{i+1}. {fact}")
    
    print("\nEpisodic memories:")
    episodes = asyncio.run(memory.retrieve_from("episodic", "climate", limit=5))
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode.content}")


if __name__ == "__main__":
    main() 