# Combined Memory and Tools Example

This example demonstrates the integration of both memory systems and tool providers in a single agent.

## Overview

The `combined_memory_tools_example.py` shows how to create a ReAct agent that uses:
1. All three types of memory (semantic, episodic, procedural)
2. MCP tool provider integration with multiple tools
3. Memory-aware tool execution that enhances tool calls with memory context

## Features Demonstrated

- Setting up a complete memory system with all memory types
- Creating a mock MCP server for demonstration purposes
- Implementing a memory-aware tool provider that enhances tool calls with memory context
- Personalizing search results based on user interests stored in memory
- Running multiple interactions using memory and tools together
- Tracking and displaying memory contents across interactions

## Tools Demonstrated

The example includes the following mock tools:
- **Search**: Information retrieval that can be personalized with memory
- **News**: Gets latest news on specific topics
- **Reminder**: Sets reminders for future events
- **Calculator**: Performs basic calculations

## Running the Example

To run this example from the project root:

```bash
# Set your OpenAI API key if not already in .env
export OPENAI_API_KEY=your-api-key-here

# Run the example
python examples/combined_memory_tools_example.py
```

## What to Expect

The example runs a series of interactions that demonstrate:
1. Personalized historical event information using memory context
2. Recipe recommendations based on user interests
3. Setting a reminder
4. Using the calculator tool
5. Searching for technology news

After all interactions, it displays the updated memory contents to show what the agent has learned and remembered. 