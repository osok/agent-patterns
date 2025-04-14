# Memory Integration Example

This example demonstrates how to integrate memory capabilities with agent patterns.

## Overview

The `memory_example.py` example shows how to set up a ReAct agent with all three types of memory:
- **Semantic Memory**: Stores factual information about entities (like user preferences)
- **Episodic Memory**: Records past interactions and experiences
- **Procedural Memory**: Maintains patterns and procedures for common tasks

## Features Demonstrated

- Setting up individual memory types with InMemoryPersistence
- Creating a CompositeMemory to manage all memory types
- Pre-populating semantic memories with user information
- Creating procedural memories for concept explanation
- Using all memory types in a ReAct agent
- Running multi-turn interactions that leverage memory
- Retrieving and displaying stored memories

## Running the Example

To run this example from the project root:

```bash
# Set your OpenAI API key if not already in .env
export OPENAI_API_KEY=your-api-key-here

# Run the example
python examples/memory_example.py
```

## What to Expect

The example runs three interactions:
1. A query about black holes (stores this interaction in episodic memory)
2. A follow-up query asking what was just discussed (uses episodic memory)
3. A query about the user's interests (uses semantic memory)

After the interactions, it displays the contents of all memory types to show what was stored. 