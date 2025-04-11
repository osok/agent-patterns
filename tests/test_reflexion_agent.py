"""Tests for the Reflexion Agent pattern."""

import pytest
from unittest.mock import MagicMock, patch
import os
from typing import Dict, Any, List

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel

from agent_patterns.patterns.reflexion_agent import ReflexionAgent


@pytest.fixture
def mock_llm():
    """Create a mock LLM that returns predefined responses."""
    mock = MagicMock(spec=BaseLanguageModel)
    
    # Configure the mock to return specific responses based on the input
    def side_effect(messages):
        # Extract the last message content to determine which function called it
        last_message = messages[-1].content if hasattr(messages[-1], "content") else messages[-1]["content"]
        
        if "plan" in last_message.lower():
            return AIMessage(content="Mock plan for solving the problem.")
        elif "execute" in last_message.lower():
            return AIMessage(content="Mock solution to the problem.")
        elif "evaluate" in last_message.lower():
            return AIMessage(content="Evaluation: 7/10. The solution addresses most aspects but could be improved.")
        elif "reflect" in last_message.lower():
            return AIMessage(content="Reflection: The approach worked well but there are areas for improvement.")
        else:
            return AIMessage(content="Default mock response")
    
    mock.invoke.side_effect = side_effect
    return mock


@pytest.fixture
def mock_prompt_template():
    """Create a mock prompt template."""
    mock = MagicMock(spec=ChatPromptTemplate)
    mock.invoke.return_value.to_messages.return_value = [{"role": "user", "content": "Mock prompt"}]
    return mock


@pytest.fixture
def reflexion_agent(mock_llm, mock_prompt_template):
    """Create a ReflexionAgent with mocked components."""
    
    # Setup for LLM configs
    llm_configs = {
        "planner": {"provider": "mock", "model_name": "mock-model"},
        "executor": {"provider": "mock", "model_name": "mock-model"},
        "evaluator": {"provider": "mock", "model_name": "mock-model"},
        "reflector": {"provider": "mock", "model_name": "mock-model"}
    }
    
    # Create a custom _load_prompt_template method that returns our mock
    def mock_load_prompt_template(self, step_name):
        return mock_prompt_template
    
    with patch.object(ReflexionAgent, '_get_llm', return_value=mock_llm):
        with patch.object(ReflexionAgent, '_load_prompt_template', mock_load_prompt_template):
            agent = ReflexionAgent(llm_configs=llm_configs, max_trials=3)
            return agent


def test_reflexion_agent_initialization(reflexion_agent):
    """Test that the ReflexionAgent initializes correctly."""
    assert reflexion_agent is not None
    assert reflexion_agent.max_trials == 3
    assert reflexion_agent.graph is not None


def test_plan_action_with_memory(reflexion_agent):
    """Test the plan generation with reflection memory."""
    initial_state = {
        "input_task": "Test task",
        "reflection_memory": [],
        "trial_count": 1,
        "max_trials": 3,
        "current_plan": None,
        "action_result": None,
        "evaluation": None,
        "trial_reflection": None,
        "final_answer": None
    }
    
    result = reflexion_agent._plan_action_with_memory(initial_state)
    
    assert "current_plan" in result
    assert result["trial_count"] == 2  # Should be incremented
    # Using the mock response from the mock_llm fixture
    assert result["current_plan"] == "Mock plan for solving the problem."


def test_execute_action(reflexion_agent):
    """Test the action execution."""
    state = {
        "input_task": "Test task",
        "current_plan": "Mock plan",
        "trial_count": 1
    }
    
    result = reflexion_agent._execute_action(state)
    
    assert "action_result" in result
    # Using the mock response from the mock_llm fixture
    assert result["action_result"] == "Mock plan for solving the problem."


def test_evaluate_outcome(reflexion_agent):
    """Test the outcome evaluation."""
    state = {
        "input_task": "Test task",
        "action_result": "Mock solution",
        "trial_count": 1
    }
    
    result = reflexion_agent._evaluate_outcome(state)
    
    assert "evaluation" in result
    # The evaluate_outcome method actually uses the mocked LLM correctly
    assert "7/10" in result["evaluation"]


def test_reflect_on_trial(reflexion_agent):
    """Test the trial reflection generation."""
    state = {
        "input_task": "Test task",
        "current_plan": "Mock plan",
        "action_result": "Mock solution",
        "evaluation": "Mock evaluation",
        "trial_count": 1,
        "max_trials": 3
    }
    
    result = reflexion_agent._reflect_on_trial(state)
    
    assert "trial_reflection" in result
    # Just check that there is some content in the reflection
    assert isinstance(result["trial_reflection"], str)
    assert len(result["trial_reflection"]) > 0


def test_update_reflection_memory(reflexion_agent):
    """Test updating the reflection memory."""
    state = {
        "reflection_memory": ["Previous reflection"],
        "trial_count": 1,
        "trial_reflection": "New reflection"
    }
    
    result = reflexion_agent._update_reflection_memory(state)
    
    assert "reflection_memory" in result
    assert len(result["reflection_memory"]) == 2
    assert "New reflection" in result["reflection_memory"][1]


def test_should_continue_trials(reflexion_agent):
    """Test the trial continuation decision logic."""
    # Test case 1: Already reached max trials
    state1 = {"trial_count": 4, "max_trials": 3, "evaluation": ""}
    assert not reflexion_agent._should_continue_trials(state1)
    
    # Test case 2: Good evaluation score
    state2 = {"trial_count": 2, "max_trials": 3, "evaluation": "Evaluation: 9/10. Excellent solution."}
    assert not reflexion_agent._should_continue_trials(state2)
    
    # Test case 3: Should continue
    state3 = {"trial_count": 2, "max_trials": 3, "evaluation": "Evaluation: 5/10. Needs improvement."}
    assert reflexion_agent._should_continue_trials(state3)


def test_prepare_final_output(reflexion_agent):
    """Test preparing the final output."""
    state = {
        "trial_count": 3,
        "action_result": "Final solution to the problem"
    }
    
    result = reflexion_agent._prepare_final_output(state)
    
    assert "final_answer" in result
    assert result["final_answer"] == "Final solution to the problem"


def test_run_method(reflexion_agent):
    """Test the run method of the ReflexionAgent."""
    # Patch the graph.invoke method to return a predefined state
    final_state = {
        "input_task": "Test task",
        "reflection_memory": ["Reflection 1", "Reflection 2"],
        "trial_count": 3,
        "max_trials": 3,
        "current_plan": "Final plan",
        "action_result": "Final solution",
        "evaluation": "Final evaluation",
        "trial_reflection": "Final reflection",
        "final_answer": "Final answer to the problem"
    }
    
    reflexion_agent.graph.invoke = MagicMock(return_value=final_state)
    
    result = reflexion_agent.run("Test task")
    
    assert "output" in result
    assert "metadata" in result
    assert result["output"] == "Final answer to the problem"
    assert result["metadata"]["trials_completed"] == 2
    assert len(result["metadata"]["reflections"]) == 2


def test_stream_method(reflexion_agent):
    """Test the stream method of the ReflexionAgent."""
    # Create a generator that returns some state updates
    def mock_stream(state):
        yield {"current_plan": "Plan 1"}
        yield {"action_result": "Result 1"}
        yield {"evaluation": "Evaluation 1"}
        yield {"trial_reflection": "Reflection 1"}
        yield {"final_answer": "Final answer"}
    
    reflexion_agent.graph.stream = MagicMock(side_effect=mock_stream)
    
    # Collect all yielded items from the stream
    results = list(reflexion_agent.stream("Test task"))
    
    assert len(results) == 5
    assert results[0] == {"current_plan": "Plan 1"}
    assert results[-1] == {"final_answer": "Final answer"}


def test_integration_with_mocks(reflexion_agent):
    """Test the complete flow with mocked components."""
    input_task = "Solve this complex math problem: what is 2+2?"
    
    # Create a more realistic mock for the graph invoke that simulates the full flow
    def simulate_graph_invoke(state):
        # Simulate running through all the nodes in sequence
        state = {**state, **reflexion_agent._plan_action_with_memory(state)}
        state = {**state, **reflexion_agent._execute_action(state)}
        state = {**state, **reflexion_agent._evaluate_outcome(state)}
        state = {**state, **reflexion_agent._reflect_on_trial(state)}
        state = {**state, **reflexion_agent._update_reflection_memory(state)}
        
        # Decide whether to continue or finish
        if reflexion_agent._should_continue_trials(state):
            # For testing, just do one more iteration
            state = {**state, **reflexion_agent._plan_action_with_memory(state)}
            state = {**state, **reflexion_agent._execute_action(state)}
            state = {**state, **reflexion_agent._evaluate_outcome(state)}
            state = {**state, **reflexion_agent._reflect_on_trial(state)}
            state = {**state, **reflexion_agent._update_reflection_memory(state)}
        
        # Finalize
        state = {**state, **reflexion_agent._prepare_final_output(state)}
        return state
    
    reflexion_agent.graph.invoke = MagicMock(side_effect=simulate_graph_invoke)
    
    result = reflexion_agent.run(input_task)
    
    assert "output" in result
    assert "metadata" in result
    assert result["metadata"]["trials_completed"] >= 1