"""
Example demonstrating the use of a tool provider with ReActAgent.

This example shows how to set up a ReAct agent with a custom tool provider
that gives access to multiple external APIs and services.
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Add the parent directory to sys.path to import agent_patterns
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Load environment variables
load_dotenv()

from src.agent_patterns.patterns.re_act_agent import ReActAgent
from src.agent_patterns.core.tools.base import ToolProvider
from src.agent_patterns.core.tools.registry import ToolRegistry

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
    # Configure LLM
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in .env file.")
    
    llm_configs = {
        "default": {
            "provider": "openai",
            "model_name": "gpt-4o",
            "temperature": 0.7
        }
    }
    
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
    
    # Create the ReAct agent with the tool provider
    agent = ReActAgent(
        llm_configs=llm_configs,
        tool_provider=tool_provider,
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
            if len(step) >= 2:
                print(f"  Thought: {step[0]}")
                print(f"  Action: {step[1]}")
            if len(step) >= 3:
                print(f"  Observation: {step[2]}")


if __name__ == "__main__":
    main() 