"""
Example demonstrating the use of memory with PlanAndSolveAgent.

This example shows how to set up a PlanAndSolve agent with semantic, episodic, and procedural memory
and how the agent can use this memory during planning and execution.
"""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



import os
import sys
from dotenv import load_dotenv
from pprint import pprint
import asyncio

# Add the parent directory to sys.path to import agent_patterns
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Load environment variables
load_dotenv()

from agent_patterns.patterns.plan_and_solve_agent import PlanAndSolveAgent
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
from examples.utils.model_config import get_llm_configs, get_model_config

# Define a simple calculator tool
def calculate(expression):
    """Simple calculator tool."""
    try:
        # Safely evaluate mathematical expressions
        allowed_names = {"abs": abs, "max": max, "min": min, "sum": sum}
        return eval(expression, {"__builtins__": {}}, allowed_names)
    except Exception as e:
        return f"Error: {str(e)}"

class CalculatorTool(ToolProvider):
    """Calculator tool provider for the agent."""
    
    def list_tools(self):
        """List the available tools."""
        return [{
            "name": "calculator",
            "description": "Perform basic mathematical operations",
            "parameters": {
                "expression": {
                    "type": "string", 
                    "description": "The mathematical expression to evaluate"
                }
            }
        }]
    
    def execute_tool(self, tool_name, params):
        """Execute the calculator tool."""
        if tool_name != "calculator":
            return f"Unknown tool: {tool_name}"
            
        expression = params.get("expression", "")
        return calculate(expression)

async def setup_memory_async():
    """Set up a composite memory system asynchronously."""
    # Create persistence backend (in-memory for this example)
    persistence = InMemoryPersistence()
    await persistence.initialize()
    
    # Create individual memory types
    semantic_memory = SemanticMemory(persistence, namespace="user_semantic")
    episodic_memory = EpisodicMemory(persistence, namespace="user_episodic")
    procedural_memory = ProceduralMemory(persistence, namespace="user_procedural")
    
    # Create composite memory
    memory = CompositeMemory({
        "semantic": semantic_memory,
        "episodic": episodic_memory,
        "procedural": procedural_memory
    })
    
    # Pre-populate with some semantic memories about the user
    await memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "name", "value": "Alex"}
    )
    
    await memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "occupation", "value": "Data Scientist"}
    )
    
    await memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "math_skill_level", "value": "advanced"}
    )
    
    # Create a procedural memory for mathematical problems
    await memory.save_to(
        "procedural",
        {
            "name": "solve_math_problem",
            "pattern": {
                "template": """When solving {problem_type} problems:
1. Break down complex problems into smaller steps
2. Use appropriate formulas
3. Consider edge cases
4. Verify the solution"""
            },
            "description": "Template for solving mathematical problems systematically",
            "tags": ["math", "problem-solving"]
        }
    )
    
    return memory

def setup_memory():
    """Wrapper to run the async setup_memory_async function."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    memory = loop.run_until_complete(setup_memory_async())
    loop.close()
    return memory

def main():
    """Run the PlanAndSolve with memory example."""
    # Set up memory using the new helper function
    memory = setup_memory()
    
    # Configure LLM 
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in .env file.")
    
    # Setup LLM configs using the utility function
    base_configs = get_llm_configs()
    llm_configs = {
        "planner": {
            **base_configs.get("planning", base_configs["default"]),
            "temperature": 0.7
        },
        "executor": {
            **base_configs.get("planning", base_configs["default"]),
            "temperature": 0.5
        }
    }
    
    # Get the project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '../..'))
    prompt_dir = os.path.join(project_root, "src", "agent_patterns", "prompts")
    
    # Create a calculator tool
    calculator_tool = CalculatorTool()
    
    # Create PlanAndSolve agent with memory
    agent = PlanAndSolveAgent(
        llm_configs=llm_configs,
        prompt_dir=prompt_dir,
        tool_provider=calculator_tool,
        memory=memory,
        memory_config={
            "semantic": True,  # Enable semantic memory
            "episodic": True,  # Enable episodic memory
            "procedural": True  # Enable procedural memory
        }
    )
    
    # Run a sequence of interactions to demonstrate memory usage
    print("\n======= FIRST INTERACTION =======")
    print("User: What's the square root of 144?")
    
    result = agent.run("What's the square root of 144?")
    print("\nAgent response:")
    print(result["output"])
    
    # Let's check what the agent stored in episodic memory
    print("\nEpisodic memories after first interaction:")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    episodes = loop.run_until_complete(memory.retrieve_from("episodic", "square root 144", limit=5))
    loop.close()
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode.content}")
    
    # Run a second query that builds on the first interaction
    print("\n======= SECOND INTERACTION =======")
    print("User: What mathematical problem did I ask you to solve earlier?")
    
    result = agent.run("What mathematical problem did I ask you to solve earlier?")
    print("\nAgent response:")
    print(result["output"])
    
    # Add semantic memory about the user's interest
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "interests", "value": ["statistics", "machine learning", "data visualization"]}
    ))
    loop.close()
    
    # Run a third query that leverages semantic memory
    print("\n======= THIRD INTERACTION =======")
    print("User: Can you suggest a mathematical concept related to my interests?")
    
    result = agent.run("Can you suggest a mathematical concept related to my interests?")
    print("\nAgent response:")
    print(result["output"])
    
    # Let's examine all memories to see what the agent has learned and stored
    print("\n======= MEMORY CONTENTS =======")
    print("Semantic memories:")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    facts = loop.run_until_complete(memory.retrieve_from("semantic", "", limit=10))
    loop.close()
    for i, fact in enumerate(facts):
        print(f"{i+1}. {fact}")
    
    print("\nEpisodic memories:")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    episodes = loop.run_until_complete(memory.retrieve_from("episodic", "", limit=10))
    loop.close()
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode.content}")
    
    print("\nProcedural memories:")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    procedures = loop.run_until_complete(memory.retrieve_from("procedural", "", limit=10))
    loop.close()
    for i, proc in enumerate(procedures):
        print(f"{i+1}. {proc.name}: {proc.description}")

if __name__ == "__main__":
    main() 