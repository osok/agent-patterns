#!/usr/bin/env python3
"""Simple MCP calculator server example."""

import json
import sys
import logging
import math
from typing import Dict, List, Any, Optional, Union, Callable


# Configure logging to file to avoid interfering with stdio communication
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='calculator_server.log',
    filemode='w'
)
logger = logging.getLogger("CalculatorMCPServer")


# Define calculator functions
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def square_root(n: float) -> float:
    """Calculate the square root of a number."""
    if n < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return math.sqrt(n)


def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent."""
    return math.pow(base, exponent)


# Map of tool names to functions
TOOL_MAP: Dict[str, Callable] = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
    "square_root": square_root,
    "power": power
}


# Define tool specifications
TOOLS = [
    {
        "name": "add",
        "description": "Add two numbers",
        "parameters": {
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"}
        }
    },
    {
        "name": "subtract",
        "description": "Subtract the second number from the first",
        "parameters": {
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number to subtract"}
        }
    },
    {
        "name": "multiply",
        "description": "Multiply two numbers",
        "parameters": {
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"}
        }
    },
    {
        "name": "divide",
        "description": "Divide the first number by the second",
        "parameters": {
            "a": {"type": "number", "description": "Numerator"},
            "b": {"type": "number", "description": "Denominator (must not be zero)"}
        }
    },
    {
        "name": "square_root",
        "description": "Calculate the square root of a number",
        "parameters": {
            "n": {"type": "number", "description": "The number to find the square root of"}
        }
    },
    {
        "name": "power",
        "description": "Raise a number to a power",
        "parameters": {
            "base": {"type": "number", "description": "The base number"},
            "exponent": {"type": "number", "description": "The exponent to raise the base to"}
        }
    }
]


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
        
        logger.info(f"Tool {tool_name} returned: {result}")
        
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
    logger.info("Starting calculator MCP server")
    
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