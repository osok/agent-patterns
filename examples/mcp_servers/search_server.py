#!/usr/bin/env python3

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only

"""Simple MCP search server example."""

import json
import sys
import logging
import re
import random
from typing import Dict, List, Any, Optional, Union

# Configure logging to file to avoid interfering with stdio communication
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='search_server.log',
    filemode='w'
)
logger = logging.getLogger("SearchMCPServer")

# Mock search database - in a real application, this would be a search engine API
SEARCH_DB = {
    "weather": [
        "The weather in New York is currently sunny with a high of 75°F.",
        "Tomorrow's forecast for Chicago: Rain with temperatures around 60°F.",
        "Weather in Los Angeles remains consistently sunny with temperatures in the 80s.",
    ],
    "python": [
        "Python is a high-level, interpreted programming language known for its readability.",
        "Python 3.11 introduced significant performance improvements over previous versions.",
        "Popular Python frameworks include Django, Flask, and FastAPI for web development.",
    ],
    "machine learning": [
        "Machine learning is a subset of artificial intelligence focused on building systems that learn from data.",
        "Common machine learning algorithms include linear regression, decision trees, and neural networks.",
        "TensorFlow and PyTorch are popular frameworks for deep learning in Python.",
    ],
    "climate change": [
        "Climate change refers to long-term shifts in temperatures and weather patterns.",
        "The main driver of climate change is fossil fuel burning, which increases heat-trapping greenhouse gases.",
        "Effects of climate change include rising sea levels, more frequent extreme weather events, and ecosystem disruptions.",
    ],
    "default": [
        "No specific information found for this query.",
        "Try searching for more common topics like 'weather', 'python', or 'machine learning'.",
    ]
}

# Define tool specifications
TOOLS = [
    {
        "name": "search",
        "description": "Search for information on a given topic",
        "parameters": {
            "query": {"type": "string", "description": "The search query"}
        }
    },
    {
        "name": "get_random_fact",
        "description": "Get a random fact about any topic",
        "parameters": {}
    }
]


def search(query: str) -> str:
    """
    Search for information on a given topic.
    
    Args:
        query: The search query
        
    Returns:
        A string containing search results
    """
    logger.info(f"Searching for: {query}")
    
    # Normalize query
    query_lower = query.lower()
    
    # Find the best matching topic
    best_match = "default"
    for topic in SEARCH_DB.keys():
        if topic != "default" and topic in query_lower:
            best_match = topic
            break
    
    # Get results for the best matching topic
    results = SEARCH_DB[best_match]
    
    # Format the results
    formatted_results = f"Search results for '{query}':\n\n"
    for i, result in enumerate(results, 1):
        formatted_results += f"{i}. {result}\n"
    
    return formatted_results


def get_random_fact() -> str:
    """
    Get a random fact from the search database.
    
    Returns:
        A random fact string
    """
    # Get a random topic
    topics = list(SEARCH_DB.keys())
    if "default" in topics:
        topics.remove("default")
    
    topic = random.choice(topics)
    
    # Get a random fact from that topic
    fact = random.choice(SEARCH_DB[topic])
    
    return f"Random fact: {fact}"


# Map of tool names to functions
TOOL_MAP = {
    "search": search,
    "get_random_fact": get_random_fact
}


def handle_handshake() -> Dict[str, Any]:
    """Handle handshake request."""
    logger.info("Handling handshake")
    return {
        "type": "handshake_response",
        "status": "success",
        "version": "v1"
    }


def handle_list_tools() -> Dict[str, Any]:
    """Handle list_tools request."""
    logger.info("Handling list_tools")
    return {
        "type": "list_tools_response",
        "status": "success",
        "tools": TOOLS
    }


def handle_call_tool(message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle call_tool request."""
    tool_name = message.get("tool")
    params = message.get("params", {})
    
    logger.info(f"Handling call_tool for {tool_name} with params {params}")
    
    # Check if the tool exists
    if tool_name not in TOOL_MAP:
        logger.error(f"Tool {tool_name} not found")
        return {
            "type": "call_tool_response",
            "status": "error",
            "error_type": "tool_not_found",
            "error": f"Tool '{tool_name}' not found"
        }
    
    # Get the tool function
    tool_func = TOOL_MAP[tool_name]
    
    try:
        # Call the function with the parameters
        result = tool_func(**params)
        
        logger.info(f"Tool {tool_name} executed successfully")
        
        return {
            "type": "call_tool_response",
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        return {
            "type": "call_tool_response",
            "status": "error",
            "error_type": "execution_error",
            "error": f"Error executing tool: {str(e)}"
        }


def handle_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Handle incoming message."""
    message_type = message.get("type")
    
    if message_type == "handshake":
        return handle_handshake()
    elif message_type == "list_tools":
        return handle_list_tools()
    elif message_type == "call_tool":
        return handle_call_tool(message)
    else:
        logger.error(f"Unknown message type: {message_type}")
        return {
            "type": "error",
            "error": f"Unknown message type: {message_type}"
        }


def main():
    """Main MCP server loop."""
    logger.info("Starting search MCP server")
    
    # Continuously read from stdin and write to stdout
    while True:
        try:
            # Read a line from stdin
            line = sys.stdin.readline()
            
            # Check for EOF
            if not line:
                logger.info("Received EOF, exiting")
                break
                
            # Parse the JSON message
            try:
                message = json.loads(line)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                response = {
                    "type": "error",
                    "error": f"Invalid JSON: {str(e)}"
                }
            else:
                # Handle the message
                response = handle_message(message)
            
            # Write the response to stdout
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            try:
                # Try to send an error response
                response = {
                    "type": "error",
                    "error": f"Unexpected error: {str(e)}"
                }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            except:
                # If we can't even send an error response, log it and continue
                logger.error("Failed to send error response")


if __name__ == "__main__":
    main() 