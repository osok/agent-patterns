"""Example demonstrating the PlanAndSolveAgent with memory and MCP tools."""

import os
import logging
import asyncio
from pathlib import Path
import sys

# Add the parent directory to sys.path to import agent_patterns
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

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

# Simple calculator tool implementation
class CalculatorTool(ToolProvider):
    """A simple calculator tool provider."""
    
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
        try:
            # Safely evaluate the expression
            restricted_globals = {"__builtins__": {}}
            allowed_names = {
                "abs": abs, "round": round, "min": min, "max": max,
                "sum": sum, "pow": pow, "len": len
            }
            
            # This is just for demonstration, in a real app you would want more validation
            result = eval(expression, restricted_globals, allowed_names)
            return f"Result: {result}"
        except Exception as e:
            return f"Error calculating: {str(e)}"

def setup_memory():
    """Set up a composite memory system."""
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
    
    # Pre-populate with some semantic memories
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "learning_style", "value": "visual and hands-on"}
    ))
    
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "experience", "value": "beginner in programming"}
    ))
    
    # Add a procedural memory for creating study plans
    asyncio.run(memory.save_to(
        "procedural",
        {
            "name": "create_study_plan",
            "pattern": {
                "template": """When creating a study plan:
1. Start with fundamentals before advancing
2. Include regular practice exercises
3. Incorporate project-based learning
4. Schedule regular review sessions
5. Adapt to the user's learning style: {learning_style}"""
            },
            "description": "Template for creating effective study plans",
            "tags": ["learning", "study", "plan"]
        }
    ))
    
    return memory

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # Setup LLM configs
    # Make sure your environment variables are set (e.g., OPENAI_API_KEY)
    llm_configs = {
        "planner": {
            "model_name": "gpt-4-turbo-preview",  # More powerful model for planning
            "provider": "openai",
            "temperature": 0.7
        },
        "executor": {
            "model_name": "gpt-4o",  # Using gpt-4o for execution
            "provider": "openai",
            "temperature": 0.5
        }
    }
    
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent
    prompt_dir = str(project_root / "src" / "agent_patterns" / "prompts")
    
    # Set up memory
    memory = setup_memory()
    
    # Set up calculator tool
    calculator_tool = CalculatorTool()
    
    # Initialize the agent with memory and tools
    agent = PlanAndSolveAgent(
        llm_configs=llm_configs,
        prompt_dir=prompt_dir,
        memory=memory,
        memory_config={
            "semantic": True,
            "episodic": True,
            "procedural": True
        },
        tool_provider=calculator_tool,
        log_level=logging.INFO
    )
    
    # Example task
    task = "Create a comprehensive study plan for learning Python programming from scratch to advanced level in 3 months."
    
    logger.info(f"Running Plan and Solve agent with task: {task}")
    
    # Run the agent
    result = agent.run(task)
    
    # Display the result
    if "error" in result:
        logger.error(f"Agent execution failed: {result['error']}")
    else:
        logger.info("Agent execution completed successfully")
        print("\n" + "="*80 + "\n")
        print("TASK:")
        print(task)
        print("\n" + "="*80 + "\n")
        print("RESULT:")
        print(result["output"])
        print("\n" + "="*80 + "\n")
    
    # Show what the agent stored in memory
    print("MEMORY AFTER EXECUTION:")
    
    print("\nSemantic memories:")
    facts = asyncio.run(memory.retrieve_from("semantic", "", limit=5))
    for i, fact in enumerate(facts):
        print(f"{i+1}. {fact}")
    
    print("\nEpisodic memories:")
    episodes = asyncio.run(memory.retrieve_from("episodic", "Python study plan", limit=5))
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode.content}")

if __name__ == "__main__":
    main()