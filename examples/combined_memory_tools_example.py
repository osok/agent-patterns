"""
Example demonstrating combined use of memory and MCP tools with agent patterns.

This comprehensive example shows:
1. Setting up memory (semantic, episodic, procedural)
2. Configuring MCP tool provider
3. Using a ReActAgent that leverages both memory and tools
4. How memory helps the agent be more personalized and context-aware
"""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



import os
import sys
from dotenv import load_dotenv
import asyncio
import logging
from pprint import pprint
import json
from pathlib import Path

# Add the parent directory to sys.path to import agent_patterns
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import utility for model configuration
from examples.utils.model_config import get_llm_configs

# Load environment variables
load_dotenv()

from agent_patterns.patterns.re_act_agent import ReActAgent
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
from agent_patterns.core.tools.providers.mcp_provider import MCPToolProvider

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("combined_example")


class MockMCPServer:
    """A mock MCP server for demonstration purposes.
    
    This simulates an MCP server without requiring a real server process.
    """
    
    def __init__(self, tool_configs):
        self.tool_configs = tool_configs
        self.call_history = []
    
    def list_tools(self):
        """Return a list of available tools."""
        return self.tool_configs
    
    def call_tool(self, tool_name, params):
        """Call a tool with the given parameters."""
        self.call_history.append((tool_name, params))
        
        # Implement mock responses for each tool
        if tool_name == "search":
            query = params.get("query", "")
            memory_context = params.get("memory_context", "")
            
            # Personalized search based on memory context
            if memory_context and "history" in memory_context:
                return self._personalized_search(query, interests=["history"])
            elif memory_context and "cooking" in memory_context:
                return self._personalized_search(query, interests=["cooking"])
            else:
                return self._general_search(query)
                
        elif tool_name == "news":
            topic = params.get("topic", "")
            return self._get_news(topic)
            
        elif tool_name == "reminder":
            text = params.get("text", "")
            time = params.get("time", "")
            return f"Reminder set: '{text}' for {time}"
            
        elif tool_name == "calculator":
            expression = params.get("expression", "")
            try:
                # Safely evaluate the expression
                result = eval(expression, {"__builtins__": {}})
                return f"Result: {result}"
            except Exception as e:
                return f"Error calculating: {str(e)}"
        
        # Default response for unknown tools
        return f"Tool '{tool_name}' executed with params {params}"
    
    def _general_search(self, query):
        """Simulate a general search."""
        if "weather" in query.lower():
            return "The weather is generally pleasant today with temperatures in the mid-70s."
        elif "recipe" in query.lower():
            return "Popular recipes include pasta carbonara, chicken curry, and chocolate cake."
        elif "technology" in query.lower() or "tech" in query.lower():
            return "Recent technology trends include AI, blockchain, and quantum computing."
        else:
            return f"Search results for '{query}' (general search)"
    
    def _personalized_search(self, query, interests):
        """Simulate a personalized search based on user interests."""
        if "history" in interests and "event" in query.lower():
            return "Historical events include the Moon landing (1969), the fall of the Berlin Wall (1989), and the invention of the internet (1969-1983)."
        elif "cooking" in interests and "recipe" in query.lower():
            return "Based on your cooking interests, here are some gourmet recipes: Beef Wellington, Crème Brûlée, and Risotto."
        else:
            # Add some personalization based on interests
            interest_context = f" (personalized for {', '.join(interests)})"
            return f"Search results for '{query}'{interest_context}"


class MemoryAwareToolProvider(ToolProvider):
    """A tool provider that incorporates memory context into tool calls."""
    
    def __init__(self, mcp_provider, memory=None):
        """Initialize with an MCP provider and optional memory."""
        self.mcp_provider = mcp_provider
        self.memory = memory
        self.memory_context_cache = ""
        
    def list_tools(self):
        """List all available tools from the MCP provider."""
        return self.mcp_provider.list_tools()
    
    def execute_tool(self, tool_name, params):
        """Execute a tool, potentially enhancing the call with memory context."""
        # If we have memory and the tool is search, add memory context
        if self.memory and tool_name == "search":
            # Use the cached memory context to avoid asyncio.run() calls
            # The context cache is updated by refresh_memory_context() 
            if self.memory_context_cache:
                params = params.copy()  # Make a copy to avoid modifying the original
                params["memory_context"] = self.memory_context_cache
        
        # Execute the tool with the potentially enhanced parameters
        return self.mcp_provider.execute_tool(tool_name, params)
    
    async def refresh_memory_context(self):
        """Refresh the cached memory context."""
        if not self.memory:
            self.memory_context_cache = ""
            return
            
        # Retrieve relevant memories
        memories = await self.memory.retrieve_all("user interests preferences", limits={"semantic": 3, "episodic": 2})
        
        # Extract user interests from semantic memory
        interests = []
        for item in memories.get("semantic", []):
            if isinstance(item, dict) and item.get("attribute") == "interests":
                interests.extend(item.get("value", []))
        
        # Create a simple context string
        context_parts = []
        if interests:
            context_parts.append(f"interests: {', '.join(interests)}")
        
        # Add any relevant episodic memories
        for item in memories.get("episodic", []):
            if hasattr(item, "content"):
                context_parts.append(f"previous interaction: {item.content}")
        
        self.memory_context_cache = "; ".join(context_parts)


def setup_mock_mcp():
    """Set up a mock MCP server with tools."""
    # Define tool configurations for the mock MCP server
    tool_configs = [
        {
            "name": "search",
            "description": "Search for general information on the web",
            "parameters": {
                "query": {"type": "string", "description": "The search query"}
            }
        },
        {
            "name": "personalized_search",
            "description": "Search for information considering user's interests",
            "parameters": {
                "query": {"type": "string", "description": "The search query"},
                "interests": {"type": "array", "description": "List of user interests"}
            }
        },
        {
            "name": "set_reminder",
            "description": "Set a reminder for the user",
            "parameters": {
                "description": {"type": "string", "description": "What to remind about"},
                "time": {"type": "string", "description": "When to remind (e.g., '3pm tomorrow')"}
            }
        },
        {
            "name": "calculate",
            "description": "Perform calculations",
            "parameters": {
                "expression": {"type": "string", "description": "The mathematical expression to evaluate"}
            }
        }
    ]
    
    # Create the mock MCP server
    mock_server = MockMCPServer(tool_configs)
    
    # Create the MCP provider using the mock server
    mcp_provider = MCPToolProvider([mock_server])
    
    return mcp_provider


async def setup_memory():
    """Set up a composite memory with semantic, episodic, and procedural memory."""
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
    
    # Pre-populate with some semantic memories
    await memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "name", "value": "Sam"}
    )
    
    await memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "location", "value": "New York"}
    )
    
    await memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "interests", "value": ["history", "cooking", "technology"]}
    )
    
    # Add an episodic memory
    await memory.save_to(
        "episodic",
        {
            "content": "User asked about historical events last week",
            "importance": 0.8,
            "tags": ["query", "history", "events"]
        }
    )
    
    # Add a procedural memory for answering questions
    await memory.save_to(
        "procedural",
        {
            "name": "answer_personalized",
            "pattern": {
                "template": """When answering questions:
1. Consider the user's known interests: {interests}
2. Refer to past interactions when relevant
3. Provide detailed information on topics the user has expressed interest in
4. Use appropriate tools to gather accurate information"""
            },
            "description": "Template for personalizing answers based on user profile",
            "tags": ["personalization", "answering"]
        }
    )
    
    return memory, persistence


async def main_async():
    """Run the combined memory and tools example asynchronously."""
    # Configure logging
    logger = logging.getLogger(__name__)
    
    try:
        # Get model configuration from environment
        llm_configs = get_llm_configs()
        logger.info(f"Using model configuration from environment variables")
    except ValueError as e:
        logger.error(f"Error loading model configuration: {e}")
        logger.error("Please ensure your .env file contains the necessary model configuration variables.")
        return
    
    # Set up memory system
    memory, persistence = await setup_memory()
    
    # Set up MCP tool provider
    mcp_provider = setup_mock_mcp()
    
    # Create a memory-aware tool provider
    memory_tool_provider = MemoryAwareToolProvider(mcp_provider, memory)
    
    # Pre-cache memory context to avoid asyncio.run() inside the event loop
    await memory_tool_provider.refresh_memory_context()
    
    # Get the project root directory to find prompts
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent
    
    # Try to find prompts directory - check both installed package and development paths
    src_prompt_dir = project_root / "src" / "agent_patterns" / "prompts"
    pkg_prompt_dir = project_root / "agent_patterns" / "prompts"
    
    prompt_dir = str(src_prompt_dir if src_prompt_dir.exists() else pkg_prompt_dir)
    
    # Create the ReAct agent with memory and tools
    agent = ReActAgent(
        llm_configs=llm_configs,
        tool_provider=memory_tool_provider,
        memory=memory,
        memory_config={
            "semantic": True, 
            "episodic": True,
            "procedural": True
        },
        prompt_dir=prompt_dir,
        max_steps=5  # Limit the maximum number of steps
    )
    
    # Print available tools
    print("\nAvailable tools:")
    for tool in memory_tool_provider.list_tools():
        print(f"- {tool['name']}: {tool['description']}")
    
    # Run a sequence of interactions to demonstrate memory and tool usage
    examples = [
        "Tell me about some important historical events",
        "I'd like some recipe recommendations",
        "Set a reminder for my meeting at 3pm tomorrow",
        "What's 15 * 7 + 22?",
        "Search for the latest technology news"
    ]
    
    for i, example in enumerate(examples):
        print(f"\n\n======= EXAMPLE {i+1} =======")
        print(f"User: {example}")
        
        # Refresh memory context before each run to get updated context
        await memory_tool_provider.refresh_memory_context()
        
        # Run the agent
        result = agent.run(example)
        
        # Display the result
        print("\nAgent response:")
        print(result["output"])
        
        # Print the intermediate steps to show the tool usage
        print("\nIntermediate steps:")
        for j, step in enumerate(result.get("intermediate_steps", [])):
            print(f"Step {j+1}:")
            if len(step) >= 2:
                print(f"  Thought: {step[0]}")
                print(f"  Action: {step[1]}")
            if len(step) >= 3:
                print(f"  Observation: {step[2]}")
    
    # After running all examples, examine the memory to see what was learned
    print("\n\n======= MEMORY CONTENTS AFTER INTERACTIONS =======")
    
    print("\nSemantic memories:")
    facts = await memory.retrieve_from("semantic", "", limit=10)
    for i, fact in enumerate(facts):
        print(f"{i+1}. {fact}")
    
    print("\nEpisodic memories:")
    episodes = await memory.retrieve_from("episodic", "", limit=10)
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode.content}")
    
    print("\nProcedural memories:")
    procedures = await memory.retrieve_from("procedural", "", limit=5)
    for i, proc in enumerate(procedures):
        print(f"{i+1}. {proc.name}: {proc.description}")


def main():
    """Run the async main function with proper asyncio setup."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main() 