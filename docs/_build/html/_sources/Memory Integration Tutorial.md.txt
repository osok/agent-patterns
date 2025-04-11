# Memory Integration Tutorial

This tutorial provides step-by-step guidance on integrating memory capabilities with agent patterns in the agent-patterns library.

## Introduction

Memory systems allow agents to store and retrieve information across interactions, giving them the ability to:

- Remember past interactions and their outcomes
- Store factual knowledge for later reference
- Learn from experiences and apply that learning to new situations
- Maintain context and personalization across sessions

The agent-patterns library includes a flexible memory system with different memory types inspired by human cognitive processes.

## Memory Types

The library supports three primary types of memory:

### Semantic Memory

Stores factual knowledge and relationships. This is ideal for:
- User preferences
- Domain knowledge
- Entity attributes

### Episodic Memory

Stores experiences and events in a sequential format. This is useful for:
- Conversation history
- Previous reasoning steps
- Outcomes of past actions

### Procedural Memory

Stores processes, templates, and patterns. This helps with:
- Reasoning frameworks
- Response templates
- Problem-solving strategies

## Setup and Basic Usage

### Step 1: Create a Persistence Layer

First, choose a persistence mechanism for storing memories:

```python
import asyncio
from agent_patterns.core.memory.persistence import InMemoryPersistence

# For non-persistent storage (memory only)
persistence = InMemoryPersistence()
asyncio.run(persistence.initialize())

# For file-based persistent storage
# from agent_patterns.core.memory.persistence import FileSystemPersistence
# persistence = FileSystemPersistence(directory="./memory_data")
# asyncio.run(persistence.initialize())
```

### Step 2: Create Individual Memory Components

```python
from agent_patterns.core.memory import (
    SemanticMemory,
    EpisodicMemory,
    ProceduralMemory
)

# Create individual memory types with separate namespaces
semantic_memory = SemanticMemory(persistence, namespace="user_semantic")
episodic_memory = EpisodicMemory(persistence, namespace="user_episodic")
procedural_memory = ProceduralMemory(persistence, namespace="user_procedural")
```

### Step 3: Create a Composite Memory

Combine the individual memories into a unified interface:

```python
from agent_patterns.core.memory import CompositeMemory

memory = CompositeMemory({
    "semantic": semantic_memory,
    "episodic": episodic_memory,
    "procedural": procedural_memory
})
```

### Step 4: Store Information in Memory

```python
# Store factual knowledge in semantic memory
asyncio.run(memory.save_to(
    "semantic", 
    {"entity": "user", "attribute": "name", "value": "Alice"}
))

# Store an experience in episodic memory
asyncio.run(memory.save_to(
    "episodic",
    {
        "content": "User asked about climate change solutions",
        "importance": 0.8,
        "tags": ["climate", "question"]
    }
))

# Store a reasoning pattern in procedural memory
asyncio.run(memory.save_to(
    "procedural",
    {
        "name": "explain_concept",
        "pattern": {
            "template": """When explaining {concept}, follow these steps:
1. Start with a simple analogy
2. Define key terms
3. Provide concrete examples
4. Address common misconceptions
5. Summarize the main points"""
        },
        "description": "Template for explaining complex concepts",
        "tags": ["explanation", "teaching"]
    }
))
```

### Step 5: Retrieve Information from Memory

```python
# Get all facts about the user
user_info = asyncio.run(memory.retrieve_from("semantic", "user"))

# Get relevant memories about climate
climate_memories = asyncio.run(memory.retrieve_from("episodic", "climate change", limit=5))

# Get explanation patterns
explanation_patterns = asyncio.run(memory.retrieve_from("procedural", "explanation"))

# Retrieve from all memory types at once
all_relevant = asyncio.run(memory.retrieve_all(
    "user question climate", 
    limits={"semantic": 3, "episodic": 2, "procedural": 1}
))
```

## Integrating with Agent Patterns

All agent patterns in the library support memory integration through a consistent interface.

### Step 1: Create a Memory System

```python
# Create the memory system as shown above
memory = setup_memory()  # Your function that creates and initializes memory
```

### Step 2: Configure the Agent with Memory

```python
from agent_patterns.patterns.re_act_agent import ReActAgent

agent = ReActAgent(
    llm_configs={"default": {"provider": "openai", "model_name": "gpt-4o"}},
    memory=memory,
    memory_config={
        "semantic": True,   # Enable semantic memory
        "episodic": True,   # Enable episodic memory
        "procedural": True  # Enable procedural memory
    }
)
```

The `memory_config` parameter lets you selectively enable or disable specific memory types.

### Step 3: Run the Agent

The agent will automatically:
1. Retrieve relevant memories before processing each request
2. Save important information to memory after processing
3. Include memory context in prompts to the LLM

```python
# Run the agent (memory retrieval and saving happens automatically)
result = agent.run("Tell me about climate change solutions")
```

## Advanced Memory Usage

### Custom Memory Retrieval

For fine-grained control over memory retrieval:

```python
class CustomAgent(ReActAgent):
    async def _retrieve_relevant_memories(self, query):
        """Override to customize memory retrieval."""
        if "personal" in query.lower():
            # Focus on user-related memories for personal queries
            memories = await self.memory.retrieve_all(
                f"user {query}",
                limits={"semantic": 5, "episodic": 3, "procedural": 0}
            )
        else:
            # Use standard retrieval for other queries
            memories = await super()._retrieve_relevant_memories(query)
        
        return memories
```

### Custom Memory Saving

To customize what gets saved to memory:

```python
class CustomAgent(ReActAgent):
    async def _save_to_memory(self, query, response, memory_items=None):
        """Override to customize memory saving."""
        # Save additional semantic facts
        if "preference" in query.lower():
            # Extract and save user preferences
            # This is a simplified example - you'd use an LLM to extract preferences
            if "like" in query.lower():
                preference = query.split("like")[1].strip()
                await self.memory.save_to(
                    "semantic",
                    {"entity": "user", "attribute": "likes", "value": preference}
                )
        
        # Continue with standard memory saving
        await super()._save_to_memory(query, response, memory_items)
```

### Memory with Different Agent Patterns

Each agent pattern integrates memory at the appropriate points in its workflow:

#### ReActAgent

The ReAct agent retrieves memories before each reasoning step and saves the conversation and reasoning process to episodic memory.

```python
agent = ReActAgent(
    llm_configs=llm_configs,
    tools=tools,
    memory=memory,
    memory_config={"semantic": True, "episodic": True, "procedural": True}
)
```

#### PlanAndSolveAgent

The PlanAndSolve agent retrieves memories during both the planning and execution phases, and saves the plan and results to memory.

```python
agent = PlanAndSolveAgent(
    llm_configs=llm_configs,
    memory=memory,
    memory_config={"semantic": True, "episodic": True, "procedural": True}
)
```

#### ReflectionAgent

The Reflection agent retrieves memories before generating initial output and after reflections, saving both the output and reflections to memory.

```python
agent = ReflectionAgent(
    llm_configs=llm_configs,
    memory=memory,
    memory_config={"semantic": True, "episodic": True, "procedural": True}
)
```

#### STORMAgent

The STORM agent uses memory during outline generation, perspective identification, and content synthesis phases.

```python
agent = STORMAgent(
    llm_configs=llm_configs,
    memory=memory,
    memory_config={"semantic": True, "episodic": True, "procedural": True},
    num_perspectives=3
)
```

## Example: Building a Memory-Enhanced Agent

Here's a complete example of building a ReActAgent with memory:

```python
import os
import asyncio
from dotenv import load_dotenv

from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.memory import (
    SemanticMemory,
    EpisodicMemory,
    ProceduralMemory,
    CompositeMemory
)
from agent_patterns.core.memory.persistence import InMemoryPersistence

# Load environment variables
load_dotenv()

def setup_memory():
    """Set up a composite memory system."""
    # Create persistence backend
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
    
    # Pre-populate with some user information
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "name", "value": "Alice"}
    ))
    
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "interests", "value": ["AI", "climate science", "music"]}
    ))
    
    # Add a procedural memory for personalization
    asyncio.run(memory.save_to(
        "procedural",
        {
            "name": "personalization",
            "pattern": {
                "template": """When responding to {user_name}:
1. Consider their known interests: {interests}
2. Reference previous conversations when relevant
3. Use a friendly, conversational tone
4. Provide depth on topics they're interested in"""
            },
            "description": "Template for personalizing responses",
            "tags": ["personalization"]
        }
    ))
    
    return memory

def main():
    # Set up memory
    memory = setup_memory()
    
    # Configure LLM
    llm_configs = {
        "default": {
            "provider": "openai",
            "model_name": "gpt-4o",
            "temperature": 0.7,
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    }
    
    # Create a ReActAgent with memory
    agent = ReActAgent(
        llm_configs=llm_configs,
        memory=memory,
        memory_config={
            "semantic": True,
            "episodic": True,
            "procedural": True
        }
    )
    
    # Run a series of interactions to demonstrate memory
    print("User: Tell me about AI advances")
    result = agent.run("Tell me about AI advances")
    print(f"\nAgent: {result['output']}")
    
    print("\nUser: What was I asking about earlier?")
    result = agent.run("What was I asking about earlier?")
    print(f"\nAgent: {result['output']}")
    
    print("\nUser: Tell me something related to my interests")
    result = agent.run("Tell me something related to my interests")
    print(f"\nAgent: {result['output']}")

if __name__ == "__main__":
    main()
```

## Best Practices

1. **Use appropriate memory types** for different kinds of information:
   - Semantic memory for facts and attributes
   - Episodic memory for experiences and conversations
   - Procedural memory for templates and patterns

2. **Maintain namespaces** to organize memories by domain or function

3. **Consider memory persistence needs**:
   - InMemoryPersistence for testing and development
   - FileSystemPersistence for simple persistence
   - VectorStorePersistence for semantic search capabilities

4. **Optimize retrieval parameters**:
   - Adjust the retrieval limit based on context window sizes
   - Use more specific queries for targeted retrieval
   - Balance comprehensiveness with relevance

5. **Save important information promptly**:
   - User preferences and attributes
   - Key decisions and reasoning
   - Significant events in the conversation

6. **Respect privacy and data retention policies**:
   - Implement appropriate data retention periods
   - Clear sensitive information when appropriate
   - Consider user consent for persistent memory

## Conclusion

Memory integration transforms agents from stateless responders to context-aware assistants capable of personalization and learning. By incorporating the appropriate memory types and persistence mechanisms, you can build agents that remember past interactions, learn from experiences, and provide increasingly relevant and personalized responses over time.

For more detailed information on the memory system API, refer to the [Memory API Documentation](Memory%20API%20Documentation.md). 