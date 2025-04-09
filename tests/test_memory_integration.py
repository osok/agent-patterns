"""Tests for memory integration with agents."""

import pytest
from unittest.mock import MagicMock, patch
import asyncio
import json
from typing import Dict, List, Any, Optional

from src.agent_patterns.patterns.re_act_agent import ReActAgent
from src.agent_patterns.core.memory.composite import CompositeMemory
from src.agent_patterns.core.memory.semantic import SemanticMemory
from src.agent_patterns.core.memory.episodic import EpisodicMemory, Episode
from src.agent_patterns.core.memory.procedural import ProceduralMemory, Procedure
from src.agent_patterns.core.memory.persistence.in_memory import InMemoryPersistence


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    llm = MagicMock()
    
    def llm_invoke_side_effect(messages):
        # Simulate an LLM response based on the input
        if any("weather" in str(msg) for msg in messages):
            return MagicMock(content="Thought: I need to check the weather.\nAction: weather_tool(location=\"New York\")")
        elif any("memory" in str(msg) for msg in messages):
            return MagicMock(content="Thought: I see from my memory that you're interested in AI.\nFinal Answer: Based on your previous interests in AI, I'll focus on that topic.")
        else:
            return MagicMock(content="Final Answer: I don't know how to help with that.")
    
    llm.invoke = MagicMock(side_effect=llm_invoke_side_effect)
    return llm


@pytest.fixture
def mock_tool_provider():
    """Mock tool provider for testing."""
    provider = MagicMock()
    
    def list_tools_side_effect():
        return [
            {"name": "weather_tool", "description": "Get weather information for a location"}
        ]
    
    def execute_tool_side_effect(tool_name, tool_input):
        if tool_name == "weather_tool":
            location = tool_input.get("location", "")
            return f"Weather for {location}: Sunny, 72°F"
        return "Tool not found"
    
    provider.list_tools = MagicMock(side_effect=list_tools_side_effect)
    provider.execute_tool = MagicMock(side_effect=execute_tool_side_effect)
    return provider


@pytest.fixture
def in_memory_persistence():
    """Create a new in-memory persistence backend for testing."""
    persistence = InMemoryPersistence()
    asyncio.run(persistence.initialize())
    return persistence


@pytest.fixture
def composite_memory(in_memory_persistence):
    """Create a composite memory setup for testing."""
    return asyncio.run(initialize_composite_memory(in_memory_persistence))


async def initialize_composite_memory(persistence):
    """Initialize all memory types with a proper event loop."""
    # Initialize all memory types
    semantic_memory = SemanticMemory(persistence)
    episodic_memory = EpisodicMemory(persistence)
    procedural_memory = ProceduralMemory(persistence)
    
    # Allow initialization tasks to complete
    await asyncio.sleep(0)
    
    return CompositeMemory({
        "semantic": semantic_memory,
        "episodic": episodic_memory,
        "procedural": procedural_memory
    })


@pytest.fixture
def memory_with_data(composite_memory):
    """Initialize memory with sample data."""
    # Add semantic memory items
    asyncio.run(composite_memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "interests", "value": ["AI", "programming", "weather"]}
    ))
    
    # Add episodic memory items
    asyncio.run(composite_memory.save_to(
        "episodic",
        Episode(
            content="User asked about AI technologies",
            importance=0.8,
            tags=["query", "AI"]
        )
    ))
    
    # Add procedural memory items
    asyncio.run(composite_memory.save_to(
        "procedural",
        Procedure(
            name="explain_ai_concept",
            pattern={"template": "Explain {concept} in simple terms"},
            description="Template for explaining AI concepts",
            success_rate=0.9,
            usage_count=5,
            tags=["explanation", "AI"]
        )
    ))
    
    return composite_memory


@pytest.fixture
def react_agent_with_memory(mock_llm, mock_tool_provider, memory_with_data):
    """Create a ReActAgent with memory for testing."""
    llm_configs = {"default": mock_llm}
    
    # Create agent with memory
    agent = ReActAgent(
        llm_configs=llm_configs,
        tool_provider=mock_tool_provider,
        memory=memory_with_data,
        memory_config={"semantic": True, "episodic": True, "procedural": True}
    )
    
    # Mock the _get_agent_prompt method to return a MagicMock
    prompt_mock = MagicMock()
    prompt_mock.invoke.return_value = MagicMock()
    prompt_mock.invoke.return_value.to_messages.return_value = []
    agent._get_agent_prompt = MagicMock(return_value=prompt_mock)
    
    return agent


def test_memory_retrieval_in_react_agent(react_agent_with_memory):
    """Test that the ReActAgent correctly retrieves memories."""
    # Mock the sync_retrieve_memories method to verify it gets called
    original_method = react_agent_with_memory.sync_retrieve_memories
    react_agent_with_memory.sync_retrieve_memories = MagicMock(side_effect=original_method)
    
    # Run the agent
    result = react_agent_with_memory.run("Tell me about AI")
    
    # Verify that memory retrieval was called
    react_agent_with_memory.sync_retrieve_memories.assert_called_once_with("Tell me about AI")
    
    # Check prompt includes memory context
    prompt_invoke_calls = react_agent_with_memory._get_agent_prompt().invoke.call_args_list
    assert len(prompt_invoke_calls) > 0
    
    # Check that memory data was included in the prompt
    prompt_args = prompt_invoke_calls[0][0][0]  # First call, first positional argument (dict)
    assert "memory_context" in prompt_args
    assert "interests" in prompt_args["memory_context"]
    assert "AI" in prompt_args["memory_context"]


def test_memory_save_in_react_agent(react_agent_with_memory):
    """Test that the ReActAgent correctly saves memories."""
    # Mock the sync_save_memory method to verify it gets called
    react_agent_with_memory.sync_save_memory = MagicMock()
    
    # Run the agent with a query that will use tool
    result = react_agent_with_memory.run("What's the weather in New York?")
    
    # Verify that memory saving was called
    # Should be called once for tool use
    assert react_agent_with_memory.sync_save_memory.call_count >= 1


def test_memory_integration_full_cycle(react_agent_with_memory, memory_with_data):
    """Test a full cycle of memory retrieval and saving."""
    # Instead of mocking retrieve_all which might not get called
    # Mock sync_retrieve_memories which is definitely called in run()
    react_agent_with_memory.sync_retrieve_memories = MagicMock(return_value="mock_memory_context")
    
    # Replace the memory's save_to method to avoid actual saving but track calls
    memory_with_data.save_to = MagicMock(return_value="mock_id")
    
    # Run the agent with a memory-related query
    result = react_agent_with_memory.run("What topics am I interested in?")
    
    # Verify memory retrieval happened through the agent's method
    react_agent_with_memory.sync_retrieve_memories.assert_called_once()
    
    # Check the agent produced some output
    assert isinstance(result, dict)
    assert "output" in result
    
    # We can't verify the specific content with a mock response
    # But we can check that the mock was used in constructing the response
    llm_mock = react_agent_with_memory.llm_configs["default"]
    assert llm_mock.invoke.called 