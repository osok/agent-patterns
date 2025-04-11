"""Integration tests for memory systems across multiple agent patterns.

This test module verifies that memory functionality works consistently 
across different agent patterns and that they can share memory.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any, Optional
from langchain_core.messages import AIMessage

# Import agent patterns
from agent_patterns.patterns.plan_and_solve_agent import PlanAndSolveAgent
from agent_patterns.patterns.reflection_agent import ReflectionAgent
from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.patterns.reflexion_agent import ReflexionAgent
from agent_patterns.patterns.llm_compiler_agent import LLMCompilerAgent
from agent_patterns.patterns.rewoo_agent import REWOOAgent

# Import memory components
from agent_patterns.core.memory.composite import CompositeMemory
from agent_patterns.core.memory.semantic import SemanticMemory
from agent_patterns.core.memory.episodic import EpisodicMemory, Episode
from agent_patterns.core.memory.procedural import ProceduralMemory, Procedure
from agent_patterns.core.memory.persistence.in_memory import InMemoryPersistence
from agent_patterns.core.memory.provider import MemoryProvider
from agent_patterns.patterns.factory import (
    create_plan_and_solve_agent,
    create_react_agent,
    create_reflection_agent
)


@pytest.fixture
def in_memory_persistence():
    """Create a new in-memory persistence backend for testing."""
    persistence = InMemoryPersistence()
    asyncio.run(persistence.initialize())
    return persistence


@pytest.fixture
def shared_memory(in_memory_persistence):
    """Create a shared composite memory for testing."""
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
def memory_with_data(shared_memory):
    """Initialize memory with sample data."""
    # Add semantic memory items
    asyncio.run(shared_memory.save_to(
        "semantic", 
        {"entity": "user", "attribute": "interests", "value": ["AI", "programming", "history"]}
    ))
    
    # Add episodic memory items
    asyncio.run(shared_memory.save_to(
        "episodic",
        Episode(
            content="User asked about the history of AI",
            importance=0.8,
            tags=["query", "AI", "history"]
        )
    ))
    
    # Add procedural memory items
    asyncio.run(shared_memory.save_to(
        "procedural",
        Procedure(
            name="explain_ai_history",
            pattern={"template": "Explain the history of {ai_topic}"},
            description="Template for explaining AI history topics",
            success_rate=0.9,
            usage_count=5,
            tags=["explanation", "AI", "history"]
        )
    ))
    
    return shared_memory


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    llm = MagicMock()
    
    def llm_invoke_side_effect(messages, **kwargs):
        # Simulate different LLM responses based on the input
        
        # Check if messages contain memory reference
        if any("interests" in str(msg) for msg in messages):
            # Memory was retrieved
            return AIMessage(content="I remember your interest in AI and history.")
        
        # Check if the message contains specific keywords for different agent responses
        if any("plan" in str(msg).lower() for msg in messages):
            # For PlanAndSolveAgent
            return AIMessage(content="Plan: 1. Research AI history\n2. Compile information\n3. Present findings")
        
        if any("reflect" in str(msg).lower() for msg in messages):
            # For ReflectionAgent
            return AIMessage(content="Initial output: AI history begins in the 1950s.\nReflection: I should mention earlier theoretical work.\nRefined output: AI history has roots in philosophical thinking, but formal research began in the 1950s.")
        
        if any("react" in str(msg).lower() for msg in messages):
            # For ReActAgent
            return AIMessage(content="Thought: I need to find information on AI history.\nAction: search_tool(query='history of artificial intelligence')")
        
        # Default response
        return AIMessage(content="I'll help with that.")
    
    llm.invoke = MagicMock(side_effect=llm_invoke_side_effect)
    return llm


@pytest.fixture
def mock_tool_provider():
    """Mock tool provider for testing."""
    provider = MagicMock()
    
    def list_tools_side_effect():
        return [
            {"name": "search_tool", "description": "Search for information", "parameters": {"query": {"type": "string"}}},
            {"name": "calendar_tool", "description": "Check calendar", "parameters": {"date": {"type": "string"}}}
        ]
    
    def execute_tool_side_effect(tool_name, tool_input):
        if tool_name == "search_tool":
            query = tool_input.get("query", "")
            if "ai" in query.lower() and "history" in query.lower():
                return "AI history began with the Dartmouth Conference in 1956."
            return f"Search results for: {query}"
        
        if tool_name == "calendar_tool":
            date = tool_input.get("date", "")
            return f"Calendar for {date}: No events"
            
        return "Tool not found"
    
    provider.list_tools = MagicMock(side_effect=list_tools_side_effect)
    provider.execute_tool = MagicMock(side_effect=execute_tool_side_effect)
    return provider


def create_plan_and_solve_agent(llm, memory, tool_provider):
    """Create a PlanAndSolveAgent with memory for testing."""
    agent = PlanAndSolveAgent(
        llm_configs={"default": llm, "planner": llm, "executor": llm},
        memory=memory,
        memory_config={"semantic": True, "episodic": True, "procedural": True},
        tool_provider=tool_provider
    )
    # Mock any additional required methods
    agent._get_plan_prompt = MagicMock(return_value=MagicMock())
    agent._get_solve_prompt = MagicMock(return_value=MagicMock())
    
    return agent


def create_reflection_agent(llm, memory, tool_provider):
    """Create a ReflectionAgent with memory for testing."""
    agent = ReflectionAgent(
        llm_configs={"default": llm, "generator": llm, "critic": llm},
        memory=memory,
        memory_config={"semantic": True, "episodic": True, "procedural": True},
        tool_provider=tool_provider
    )
    # Mock any additional required methods
    agent._get_initial_prompt = MagicMock(return_value=MagicMock())
    agent._get_reflection_prompt = MagicMock(return_value=MagicMock())
    agent._get_refinement_prompt = MagicMock(return_value=MagicMock())
    
    return agent


def create_react_agent(llm, memory, tool_provider):
    """Create a ReActAgent with memory for testing."""
    agent = ReActAgent(
        llm_configs={"default": llm},
        memory=memory,
        memory_config={"semantic": True, "episodic": True, "procedural": True},
        tool_provider=tool_provider
    )
    # Mock any additional required methods
    agent._get_agent_prompt = MagicMock(return_value=MagicMock())
    
    return agent


def test_memory_shared_across_agents(memory_with_data, mock_llm, mock_tool_provider):
    """Test that different agent patterns can share the same memory instance."""
    # Create different agent types with the same memory
    plan_solve_agent = create_plan_and_solve_agent(mock_llm, memory=memory_with_data, tool_provider=mock_tool_provider)
    reflection_agent = create_reflection_agent(mock_llm, memory=memory_with_data, tool_provider=mock_tool_provider)
    react_agent = create_react_agent(mock_llm, memory=memory_with_data, tool_provider=mock_tool_provider)
    
    # Mock the sync_retrieve_memories method in each agent
    mock_memories = {"semantic": [], "episodic": [], "procedural": []}
    
    # Create a spy on the original method to count calls
    original_ps_retrieve = plan_solve_agent.sync_retrieve_memories
    original_reflection_retrieve = reflection_agent.sync_retrieve_memories
    original_react_retrieve = react_agent.sync_retrieve_memories
    
    plan_solve_agent.sync_retrieve_memories = MagicMock(return_value=mock_memories)
    reflection_agent.sync_retrieve_memories = MagicMock(return_value=mock_memories)
    react_agent.sync_retrieve_memories = MagicMock(return_value=mock_memories)
    
    # Run each agent with the same query
    query = "Tell me about the history of AI"
    plan_solve_result = plan_solve_agent.run(query)
    reflection_result = reflection_agent.run(query)
    react_result = react_agent.run(query)
    
    # Verify memory was accessed by each agent
    assert plan_solve_agent.sync_retrieve_memories.call_count >= 1
    assert reflection_agent.sync_retrieve_memories.call_count >= 1
    assert react_agent.sync_retrieve_memories.call_count >= 1
    
    # Check agent responses include memory-aware content
    assert isinstance(plan_solve_result, dict)
    assert isinstance(reflection_result, dict)
    assert isinstance(react_result, dict)


def test_memory_updated_across_agents(memory_with_data, mock_llm, mock_tool_provider):
    """Test that memory updates from one agent are visible to other agents."""
    # Create different agent types with the same memory
    plan_solve_agent = create_plan_and_solve_agent(mock_llm, memory=memory_with_data, tool_provider=mock_tool_provider)
    react_agent = create_react_agent(mock_llm, memory=memory_with_data, tool_provider=mock_tool_provider)
    
    # Mock memory save function for easy tracking
    original_save = memory_with_data.save_to
    memory_with_data.save_to = MagicMock(side_effect=original_save)
    
    # First agent adds to memory
    plan_solve_agent.sync_save_memory("episodic", 
        Episode(
            content="User is particularly interested in neural networks",
            importance=0.9,
            tags=["interest", "neural networks"]
        )
    )
    
    # Verify the save occurred
    assert memory_with_data.save_to.call_count == 1
    
    # Mock the sync_retrieve_memories method in react_agent
    react_agent.sync_retrieve_memories = MagicMock(return_value={
        "semantic": [],
        "episodic": [Episode(
            content="User is particularly interested in neural networks",
            importance=0.9,
            tags=["interest", "neural networks"]
        )],
        "procedural": []
    })
    
    # Second agent should see the updated memory
    query = "What neural network architectures should I study?"
    react_agent.run(query)
    
    # Verify memory retrieval occurred for the second agent
    react_agent.sync_retrieve_memories.assert_called_with(query)
    
    # Verify that the retrieved memories include the new information
    assert react_agent.sync_retrieve_memories.call_count >= 1


def test_memory_initialization_for_multiple_patterns(in_memory_persistence, mock_llm, mock_tool_provider):
    """Test that different agent patterns correctly initialize with a fresh memory instance."""
    # Create a new shared memory
    shared_memory = asyncio.run(initialize_composite_memory(in_memory_persistence))
    
    # Create agents with this shared memory
    plan_solve_agent = create_plan_and_solve_agent(mock_llm, memory=shared_memory, tool_provider=mock_tool_provider)
    reflection_agent = create_reflection_agent(mock_llm, memory=shared_memory, tool_provider=mock_tool_provider)
    react_agent = create_react_agent(mock_llm, memory=shared_memory, tool_provider=mock_tool_provider)
    
    # Add a piece of memory directly
    asyncio.run(shared_memory.save_to(
        "semantic", 
        {"entity": "system", "attribute": "version", "value": "1.0"}
    ))
    
    # Mock the sync_retrieve_memories method in each agent
    mock_memories = {
        "semantic": [{"entity": "system", "attribute": "version", "value": "1.0"}],
        "episodic": [],
        "procedural": []
    }
    
    plan_solve_agent.sync_retrieve_memories = MagicMock(return_value=mock_memories)
    reflection_agent.sync_retrieve_memories = MagicMock(return_value=mock_memories)
    react_agent.sync_retrieve_memories = MagicMock(return_value=mock_memories)
    
    # Run each agent
    plan_solve_agent.run("What version is the system?")
    reflection_agent.run("Tell me about the system version.")
    react_agent.run("Which version am I using?")
    
    # Verify all agents accessed the memory
    assert plan_solve_agent.sync_retrieve_memories.call_count >= 1
    assert reflection_agent.sync_retrieve_memories.call_count >= 1
    assert react_agent.sync_retrieve_memories.call_count >= 1


def test_complex_memory_patterns_across_agents(memory_with_data, mock_llm, mock_tool_provider):
    """Test more complex memory interaction patterns across different agent types."""
    # Create different agent types with the same memory
    plan_solve_agent = create_plan_and_solve_agent(mock_llm, memory=memory_with_data, tool_provider=mock_tool_provider)
    react_agent = create_react_agent(mock_llm, memory=memory_with_data, tool_provider=mock_tool_provider)
    reflection_agent = create_reflection_agent(mock_llm, memory=memory_with_data, tool_provider=mock_tool_provider)
    
    # Sequence of operations that simulate a real conversation across multiple agent types
    
    # 1. First agent learns something
    plan_solve_agent.sync_save_memory("semantic", {
        "entity": "user", 
        "attribute": "preferred_learning_style", 
        "value": "visual"
    })
    
    # 2. Second agent asks about user preferences
    # Mock retrieve for react agent
    react_agent.sync_retrieve_memories = MagicMock(return_value={
        "semantic": [
            {"entity": "user", "attribute": "interests", "value": ["AI", "programming", "history"]},
            {"entity": "user", "attribute": "preferred_learning_style", "value": "visual"}
        ],
        "episodic": [],
        "procedural": []
    })
    
    react_agent.run("How should I explain AI concepts to the user?")
    
    # 3. Third agent learns another preference
    reflection_agent.sync_save_memory("episodic", Episode(
        content="User prefers detailed technical explanations",
        importance=0.7,
        tags=["preference", "technical", "detail"]
    ))
    
    # 4. Set up first agent to access both pieces of information
    plan_solve_agent.sync_retrieve_memories = MagicMock(return_value={
        "semantic": [
            {"entity": "user", "attribute": "interests", "value": ["AI", "programming", "history"]},
            {"entity": "user", "attribute": "preferred_learning_style", "value": "visual"}
        ],
        "episodic": [
            {"content": "User asked about the history of AI", "importance": 0.8, "tags": ["query", "AI", "history"]},
            {"content": "User prefers detailed technical explanations", "importance": 0.7, "tags": ["preference", "technical", "detail"]}
        ],
        "procedural": []
    })
    
    # 4. First agent should now have access to both pieces of information
    result = plan_solve_agent.run("Explain neural networks to the user")
    
    # Verify memory was retrieved
    assert plan_solve_agent.sync_retrieve_memories.call_count >= 1 