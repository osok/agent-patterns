"""
Example demonstrating the use of memory with PlanAndSolveAgent.

This example shows how to set up a PlanAndSolve agent with semantic, episodic, and procedural memory
and how the agent can use this memory during planning and execution.
"""

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

# Define a simple calculator tool
def calculate(expression):
    """Simple calculator tool."""
    try:
        # Safely evaluate mathematical expressions
        allowed_names = {"abs": abs, "max": max, "min": min, "sum": sum}
        return eval(expression, {"__builtins__": {}}, allowed_names)
    except Exception as e:
        return f"Error: {str(e)}"

class CalculatorTool:
    """Calculator tool for the agent."""
    
    def __init__(self):
        self.name = "calculator"
    
    def run(self, args):
        """Run the calculator."""
        if "expression" not in args:
            return "Error: No expression provided"
        return calculate(args["expression"])

def main():
    """Run the PlanAndSolve with memory example."""
    # Create persistence backend (in-memory for this example)
    persistence = InMemoryPersistence()
    asyncio.run(persistence.initialize())
    
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
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "name", "value": "Alex"}
    ))
    
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "occupation", "value": "Data Scientist"}
    ))
    
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "math_skill_level", "value": "advanced"}
    ))
    
    # Create a procedural memory for mathematical problems
    asyncio.run(memory.save_to(
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
    ))
    
    # Configure LLM 
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in .env file.")
    
    llm_configs = {
        "planner": {
            "provider": "openai",
            "model_name": "gpt-4o",
            "temperature": 0.7
        },
        "executor": {
            "provider": "openai",
            "model_name": "gpt-4o",
            "temperature": 0.5
        }
    }
    
    # Create a calculator tool
    calculator_tool = CalculatorTool()
    
    # Create PlanAndSolve agent with memory
    agent = PlanAndSolveAgent(
        llm_configs=llm_configs,
        tools=[calculator_tool],
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
    episodes = asyncio.run(memory.retrieve_from("episodic", "square root 144", limit=5))
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode.content}")
    
    # Run a second query that builds on the first interaction
    print("\n======= SECOND INTERACTION =======")
    print("User: What mathematical problem did I ask you to solve earlier?")
    
    result = agent.run("What mathematical problem did I ask you to solve earlier?")
    print("\nAgent response:")
    print(result["output"])
    
    # Add semantic memory about the user's interest
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "interests", "value": ["statistics", "machine learning", "data visualization"]}
    ))
    
    # Run a third query that leverages semantic memory
    print("\n======= THIRD INTERACTION =======")
    print("User: Can you suggest a mathematical concept related to my interests?")
    
    result = agent.run("Can you suggest a mathematical concept related to my interests?")
    print("\nAgent response:")
    print(result["output"])
    
    # Let's examine all memories to see what the agent has learned and stored
    print("\n======= MEMORY CONTENTS =======")
    print("Semantic memories:")
    facts = asyncio.run(memory.retrieve_from("semantic", "", limit=10))
    for i, fact in enumerate(facts):
        print(f"{i+1}. {fact}")
    
    print("\nEpisodic memories:")
    episodes = asyncio.run(memory.retrieve_from("episodic", "", limit=10))
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode.content}")
    
    print("\nProcedural memories:")
    procedures = asyncio.run(memory.retrieve_from("procedural", "", limit=10))
    for i, proc in enumerate(procedures):
        print(f"{i+1}. {proc.name}: {proc.description}")

if __name__ == "__main__":
    main() 