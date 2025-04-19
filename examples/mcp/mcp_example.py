#!/usr/bin/env python3

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only

"""Example of using MCP with ReActAgent."""

import os
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv

from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.tools.providers.mcp_provider import (
    MCPToolProvider, create_mcp_server_connection
)


def main():
    """Run the example."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get LLM configuration from environment variables
    llm_configs = create_llm_configs_from_env()
    
    # Create MCP server connections from environment variables
    mcp_servers = create_mcp_servers_from_env()
    
    if not mcp_servers:
        print("No MCP servers configured in environment. See README for configuration instructions.")
        return
    
    # Create the MCP tool provider
    tool_provider = MCPToolProvider(mcp_servers)
    
    # Create the ReAct agent
    agent = ReActAgent(
        llm_configs=llm_configs,
        tool_provider=tool_provider,
        prompt_dir="prompts"  # Assumes prompts directory is in current working directory
    )
    
    # Get user input
    user_input = input("Enter your query: ")
    
    # Run the agent
    print("\nProcessing your query...\n")
    try:
        result = agent.run(user_input)
        
        # Print the result
        print("\nResult:")
        print("-------")
        print(result.get("output", "No output generated"))
        
    except Exception as e:
        print(f"Error: {e}")


def create_llm_configs_from_env() -> Dict[str, Any]:
    """Create LLM configuration dictionary from environment variables."""
    # Default to OpenAI if not specified
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    model = os.getenv("LLM_MODEL", "gpt-4o")
    
    if provider == "openai":
        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY environment variable not set.")
            print("Using default OpenAI settings, which may fail without an API key.")
        
        return {
            "default": {
                "provider": "openai",
                "model_name": model,
                "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7"))
            }
        }
    elif provider == "anthropic":
        # Check for Anthropic API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Warning: ANTHROPIC_API_KEY environment variable not set.")
            print("Using default Anthropic settings, which may fail without an API key.")
        
        return {
            "default": {
                "provider": "anthropic",
                "model_name": model or "claude-3-5-sonnet-latest",
                "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7"))
            }
        }
    else:
        # For other providers, you'd add similar logic
        print(f"Warning: Unsupported LLM provider '{provider}'. Falling back to OpenAI.")
        return {
            "default": {
                "provider": "openai",
                "model_name": "gpt-4o",
                "temperature": 0.7
            }
        }


def create_mcp_servers_from_env() -> List[Any]:
    """Create MCP server connections from environment variables."""
    servers = []
    
    # Get the number of MCP servers from environment
    server_count = int(os.getenv("MCP_SERVER_COUNT", "0"))
    
    for i in range(server_count):
        prefix = f"MCP_SERVER_{i+1}_"
        server_type = os.getenv(f"{prefix}TYPE")
        
        if not server_type:
            print(f"Warning: Server type not specified for MCP server {i+1}. Skipping.")
            continue
        
        if server_type.lower() == "stdio":
            # Get command (required)
            command_str = os.getenv(f"{prefix}COMMAND")
            if not command_str:
                print(f"Warning: Command not specified for MCP server {i+1}. Skipping.")
                continue
            
            # Split the command string into a list
            command = command_str.split()
            
            # Get working directory (optional)
            working_dir = os.getenv(f"{prefix}WORKING_DIR")
            
            # Create the server connection
            try:
                server = create_mcp_server_connection(
                    "stdio",
                    {
                        "command": command,
                        "working_dir": working_dir,
                        "id": f"server-{i+1}"
                    }
                )
                servers.append(server)
                print(f"Created MCP server {i+1} with command: {command}")
            except Exception as e:
                print(f"Error creating MCP server {i+1}: {e}")
        else:
            print(f"Warning: Unsupported server type '{server_type}' for MCP server {i+1}. Skipping.")
    
    return servers


if __name__ == "__main__":
    main() 