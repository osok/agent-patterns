"""
Example demonstrating the use of a tool provider with ReActAgent.

This example shows how to set up a ReAct agent with a custom tool provider
that gives access to multiple external APIs and services.
"""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



import os
import sys
from dotenv import load_dotenv
import logging

# Add the parent directory to sys.path to import agent_patterns
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from examples.utils.model_config import get_llm_configs

# Load environment variables
load_dotenv()

from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.tools.base import ToolProvider
from agent_patterns.core.tools.registry import ToolRegistry

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("react_tool_provider_example")


class WikiSearchTool:
    """A simple tool to simulate searching for information."""
    
    def __init__(self):
        self.name = "wiki_search"
    
    def run(self, args):
        """Run a simulated Wikipedia search."""
        query = args.get("query", "")
        if not query:
            return "Error: No query provided"
        
        logger.info(f"Performing wiki search for: {query}")
        
        # For this example, we'll return hardcoded responses for some queries
        if "AI" in query or "artificial intelligence" in query.lower():
            return """
            Artificial intelligence (AI) is the intelligence of machines or software, 
            as opposed to the intelligence of humans or animals. AI applications include 
            advanced web search engines, recommendation systems, speech recognition, and 
            natural language processing.
            """
        elif "python" in query.lower():
            return """
            Python is a high-level, general-purpose programming language. Its design 
            philosophy emphasizes code readability with the use of significant indentation. 
            Python is dynamically typed and garbage-collected.
            """
        else:
            return f"No specific information found for '{query}'. Please try another search term."


class WeatherTool:
    """A tool to simulate checking the weather."""
    
    def __init__(self):
        self.name = "weather"
    
    def run(self, args):
        """Get simulated weather information for a location."""
        location = args.get("location", "")
        if not location:
            return "Error: No location provided"
        
        logger.info(f"Checking weather for: {location}")
        
        # Return hardcoded responses for demo purposes
        if location.lower() in ["new york", "nyc"]:
            return "New York City: 72°F, Partly Cloudy"
        elif location.lower() in ["los angeles", "la"]:
            return "Los Angeles: 85°F, Sunny"
        elif location.lower() in ["london"]:
            return "London: 60°F, Rainy"
        else:
            return f"{location}: 70°F, Clear skies (simulated data)"


class CalculatorTool:
    """A simple calculator tool."""
    
    def __init__(self):
        self.name = "calculator"
    
    def run(self, args):
        """Perform a calculation."""
        expression = args.get("expression", "")
        if not expression:
            return "Error: No expression provided"
        
        logger.info(f"Calculating: {expression}")
        
        try:
            # Safely evaluate the expression (limited to basic math)
            allowed_names = {"abs": abs, "max": max, "min": min, "sum": sum}
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"Result: {result}"
        except Exception as e:
            return f"Error calculating {expression}: {str(e)}"


class CustomToolProvider(ToolProvider):
    """A custom tool provider that gives access to multiple tools."""
    
    def __init__(self, tools_list=None):
        """Initialize with a list of tools."""
        self.tools = tools_list or []
        self._tools_dict = {tool.name: tool for tool in self.tools}
    
    def list_tools(self):
        """List all available tools with their metadata."""
        tools_info = []
        
        for tool in self.tools:
            # Define the tool's schema based on its name
            if tool.name == "wiki_search":
                parameters = {"query": {"type": "string", "description": "The search query"}}
            elif tool.name == "weather":
                parameters = {"location": {"type": "string", "description": "The location to check weather for"}}
            elif tool.name == "calculator":
                parameters = {"expression": {"type": "string", "description": "The mathematical expression to evaluate"}}
            else:
                parameters = {}
            
            # Add the tool info
            tools_info.append({
                "name": tool.name,
                "description": f"Tool for {tool.name}",
                "parameters": parameters
            })
        
        return tools_info
    
    def execute_tool(self, tool_name, params):
        """Execute a tool with the given parameters."""
        if tool_name not in self._tools_dict:
            return f"Error: Tool '{tool_name}' not found. Available tools: {', '.join(self._tools_dict.keys())}"
        
        # Get the tool and run it
        tool = self._tools_dict[tool_name]
        result = tool.run(params)
        return result


def main():
    """Run the ReAct with tool provider example."""
    # Setup LLM configs using the utility function
    try:
        # This will use PLANNING_MODEL_PROVIDER and PLANNING_MODEL_NAME from .env
        llm_configs = get_llm_configs()
    except ValueError as e:
        logger.error(f"Error loading model configuration: {e}")
        logger.error("Please ensure your .env file contains the necessary model configuration variables.")
        return
    
    # Create tools
    wiki_search = WikiSearchTool()
    weather_tool = WeatherTool()
    calculator_tool = CalculatorTool()
    
    # Create the custom tool provider with all tools
    tool_provider = CustomToolProvider([wiki_search, weather_tool, calculator_tool])
    
    # Print the available tools
    print("\nAvailable tools:")
    for tool in tool_provider.list_tools():
        print(f"- {tool['name']}: {tool['description']}")
        print(f"  Parameters: {tool['parameters']}")
    
    # Get the project root directory to find prompts
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '../..'))

    # Try to find prompts directory - check both installed package and development paths
    src_prompt_dir = os.path.join(project_root, "src", "agent_patterns", "prompts")
    pkg_prompt_dir = os.path.join(project_root, "agent_patterns", "prompts")

    if os.path.exists(src_prompt_dir):
        prompt_dir = src_prompt_dir
    else:
        prompt_dir = pkg_prompt_dir
    
    # Create the ReAct agent with the tool provider
    agent = ReActAgent(
        llm_configs=llm_configs,
        tool_provider=tool_provider,
        prompt_dir=prompt_dir,
        max_steps=5  # Limit the maximum number of steps
    )
    
    # Run a few examples to demonstrate tool usage
    examples = [
        "What is artificial intelligence?",
        "What's the weather like in New York?",
        "Calculate 25 * 4 + 10",
        "First tell me about Python, then check the weather in London."
    ]
    
    for i, example in enumerate(examples):
        print(f"\n\n======= EXAMPLE {i+1} =======")
        print(f"User: {example}")
        
        result = agent.run(example)
        print("\nAgent response:")
        print(result["output"])
        
        # Print the intermediate steps to show the tool usage
        print("\nIntermediate steps:")
        for j, step in enumerate(result.get("intermediate_steps", [])):
            print(f"Step {j+1}:")
            if isinstance(step, tuple) and len(step) >= 2:
                action, observation = step
                print(f"  Action: {action}")
                print(f"  Observation: {observation}")
            else:
                print(f"  Step data: {step}")


def fixed_example():
    """Run a fixed version of the example that doesn't rely on the agent framework."""
    # Create tools
    wiki_search = WikiSearchTool()
    weather_tool = WeatherTool()
    calculator_tool = CalculatorTool()
    
    # Create the custom tool provider with all tools
    tool_provider = CustomToolProvider([wiki_search, weather_tool, calculator_tool])
    
    # Print the available tools
    print("\n======= FIXED EXAMPLE =======")
    print("Available tools:")
    for tool in tool_provider.list_tools():
        print(f"- {tool['name']}: {tool['description']}")
        print(f"  Parameters: {tool['parameters']}")
    
    # Example 1: Wiki search for AI
    print("\n\n======= EXAMPLE 1: Wiki Search =======")
    print("Query: What is artificial intelligence?")
    result = tool_provider.execute_tool("wiki_search", {"query": "artificial intelligence"})
    print(f"Result: {result}")
    
    # Example 2: Weather in New York
    print("\n\n======= EXAMPLE 2: Weather =======")
    print("Query: What's the weather like in New York?")
    result = tool_provider.execute_tool("weather", {"location": "New York"})
    print(f"Result: {result}")
    
    # Example 3: Calculator
    print("\n\n======= EXAMPLE 3: Calculator =======")
    print("Query: Calculate 25 * 4 + 10")
    result = tool_provider.execute_tool("calculator", {"expression": "25 * 4 + 10"})
    print(f"Result: {result}")
    
    # Example 4: Multiple tools
    print("\n\n======= EXAMPLE 4: Multiple Tools =======")
    print("Query: First tell me about Python, then check the weather in London.")
    print("Step 1: Get information about Python")
    result1 = tool_provider.execute_tool("wiki_search", {"query": "python"})
    print(f"Python info result: {result1}")
    print("\nStep 2: Check weather in London")
    result2 = tool_provider.execute_tool("weather", {"location": "london"})
    print(f"London weather result: {result2}")
    print("\nCombined response:")
    print(f"Information about Python: {result1}\n\nWeather in London: {result2}")


if __name__ == "__main__":
    print("\n======= AGENT-BASED TOOL PROVIDER EXAMPLE =======")
    main()
    
    print("\n======= FIXED TOOL PROVIDER EXAMPLE =======")
    fixed_example() 