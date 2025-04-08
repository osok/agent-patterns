"""Tests for the PlanAndSolveAgent class."""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import asyncio

from agent_patterns.patterns.plan_and_solve_agent import PlanAndSolveAgent, PlanAndSolveState
from langchain_core.messages import AIMessage, HumanMessage


@pytest.fixture
def test_prompts_dir(tmp_path):
    """Create a temporary directory with test prompts for Plan and Solve agent."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    
    # Create directory structure for PlanAndSolveAgent
    plan_solve_dir = prompts_dir / "PlanAndSolveAgent"
    plan_solve_dir.mkdir()
    
    plan_step_dir = plan_solve_dir / "PlanStep"
    plan_step_dir.mkdir()
    execute_step_dir = plan_solve_dir / "ExecuteStep"
    execute_step_dir.mkdir()
    
    # Create test prompt files for PlanStep
    plan_system_content = """You are a planning assistant that creates a detailed step-by-step plan to solve complex tasks."""
    plan_user_content = """Create a clear, step-by-step plan to solve the following task:

Task: {input}"""
    
    # Create test prompt files for ExecuteStep
    execute_system_content = """You are an execution assistant that carries out individual steps from a plan with precision and thoroughness."""
    execute_user_content = """Please execute the following step from our plan:

Step to execute: {current_step}

Context from previous steps: {previous_results}

Original task: {input}"""
    
    # Write PlanStep prompts
    with open(plan_step_dir / "system.md", "w") as f:
        f.write(plan_system_content)
    
    with open(plan_step_dir / "user.md", "w") as f:
        f.write(plan_user_content)
    
    # Write ExecuteStep prompts
    with open(execute_step_dir / "system.md", "w") as f:
        f.write(execute_system_content)
    
    with open(execute_step_dir / "user.md", "w") as f:
        f.write(execute_user_content)
    
    return prompts_dir


@pytest.fixture
def llm_configs():
    """Sample LLM configs for testing."""
    return {
        "planner": {
            "model_name": "gpt-4-turbo",
            "provider": "openai"
        },
        "executor": {
            "model_name": "gpt-4o",
            "provider": "openai"
        }
    }


def test_plan_and_solve_initialization(llm_configs, test_prompts_dir):
    """Test basic agent initialization."""
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        mock_openai.return_value = Mock()
        agent = PlanAndSolveAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
        assert agent.prompt_dir == str(test_prompts_dir)
        assert agent.graph is not None


def test_generate_plan(llm_configs, test_prompts_dir):
    """Test plan generation."""
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        # Setup mock response
        mock_llm = Mock()
        mock_response = AIMessage(content="1. Research the topic\n2. Analyze findings\n3. Create report")
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm
        
        agent = PlanAndSolveAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
        
        # Call _generate_plan directly
        state = {
            "input": "Write a report on climate change",
            "chat_history": []
        }
        result = agent._generate_plan(state)
        
        assert "plan" in result
        assert len(result["plan"]) > 0
        assert result["current_step_index"] == 0
        assert isinstance(result["step_results"], list)


def test_execute_plan_step(llm_configs, test_prompts_dir):
    """Test executing a plan step."""
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        # Setup mock response
        mock_llm = Mock()
        mock_response = AIMessage(content="I've researched the topic and found key information on climate change impacts.")
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm
        
        agent = PlanAndSolveAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
        
        # Call _execute_plan_step directly
        state = {
            "input": "Write a report on climate change",
            "chat_history": [],
            "plan": ["Research the topic", "Analyze findings", "Create report"],
            "current_step_index": 0,
            "step_results": []
        }
        result = agent._execute_plan_step(state)
        
        assert "step_results" in result
        assert len(result["step_results"]) == 1
        assert result["current_step_index"] == 1


def test_check_plan_completion_true(llm_configs, test_prompts_dir):
    """Test plan completion check when all steps are completed."""
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        mock_openai.return_value = Mock()
        agent = PlanAndSolveAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
        
        # Set up state where all steps are completed
        state = {
            "input": "Write a report on climate change",
            "chat_history": [],
            "plan": ["Research the topic", "Analyze findings", "Create report"],
            "current_step_index": 3,  # Completed all 3 steps
            "step_results": ["Result 1", "Result 2", "Result 3"],
            "plan_done": False  # This should be updated to True
        }
        
        result = agent._check_plan_completion(state)
        
        assert "plan_done" in result
        assert result["plan_done"] is True


def test_check_plan_completion_false(llm_configs, test_prompts_dir):
    """Test plan completion check when steps remain to be executed."""
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        mock_openai.return_value = Mock()
        agent = PlanAndSolveAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
        
        # Set up state where some steps remain
        state = {
            "input": "Write a report on climate change",
            "chat_history": [],
            "plan": ["Research the topic", "Analyze findings", "Create report"],
            "current_step_index": 1,  # Only completed first step
            "step_results": ["Result 1"],
            "plan_done": False
        }
        
        result = agent._check_plan_completion(state)
        
        assert "plan_done" in result
        assert result["plan_done"] is False


def test_should_continue_execution(llm_configs, test_prompts_dir):
    """Test the condition for continuing execution."""
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        mock_openai.return_value = Mock()
        agent = PlanAndSolveAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
        
        # Test when plan is not done
        state_not_done = {
            "plan_done": False
        }
        assert agent._should_continue_execution(state_not_done) is True
        
        # Test when plan is done
        state_done = {
            "plan_done": True
        }
        assert agent._should_continue_execution(state_done) is False


def test_aggregate_results(llm_configs, test_prompts_dir):
    """Test aggregating results into a final answer."""
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        # Setup mock response
        mock_llm = Mock()
        mock_response = AIMessage(content="Final comprehensive report on climate change.")
        mock_llm.invoke.return_value = mock_response
        mock_openai.return_value = mock_llm
        
        agent = PlanAndSolveAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
        
        # Call _aggregate_results directly
        state = {
            "input": "Write a report on climate change",
            "chat_history": [],
            "plan": ["Research the topic", "Analyze findings", "Create report"],
            "current_step_index": 3,
            "step_results": [
                "Research completed",
                "Analysis completed",
                "Report draft created"
            ],
            "plan_done": True
        }
        result = agent._aggregate_results(state)
        
        assert "final_result" in result
        assert result["final_result"] is not None


def test_execute_step_error_handling(llm_configs, test_prompts_dir):
    """Test error handling during step execution."""
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        # Setup mock to raise an exception
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("LLM error")
        mock_openai.return_value = mock_llm
        
        agent = PlanAndSolveAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
        
        # Call _execute_plan_step with state
        state = {
            "input": "Write a report on climate change",
            "chat_history": [],
            "plan": ["Research the topic"],
            "current_step_index": 0,
            "step_results": []
        }
        
        result = agent._execute_plan_step(state)
        
        # Check if error was handled gracefully
        assert "step_results" in result
        assert "Error executing step" in result["step_results"][0]
        assert result["current_step_index"] == 1  # Should still increment


def test_generate_plan_error_handling(llm_configs, test_prompts_dir):
    """Test error handling during plan generation."""
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        # Setup mock to raise an exception
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("LLM error")
        mock_openai.return_value = mock_llm
        
        agent = PlanAndSolveAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
        
        # Call _generate_plan with state
        state = {
            "input": "Write a report on climate change",
            "chat_history": []
        }
        
        result = agent._generate_plan(state)
        
        # Check if error was handled with a fallback plan
        assert "plan" in result
        assert len(result["plan"]) > 0
        assert isinstance(result["plan"], list)


def test_aggregate_results_error_handling(llm_configs, test_prompts_dir):
    """Test error handling during result aggregation."""
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        # Setup mock to raise an exception
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("LLM error")
        mock_openai.return_value = mock_llm
        
        agent = PlanAndSolveAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
        
        # Call _aggregate_results with state
        state = {
            "input": "Write a report on climate change",
            "chat_history": [],
            "plan": ["Research the topic", "Create report"],
            "current_step_index": 2,
            "step_results": ["Result 1", "Result 2"],
            "plan_done": True
        }
        
        result = agent._aggregate_results(state)
        
        # Check if error was handled with a fallback result
        assert "final_result" in result
        assert isinstance(result["final_result"], str)
        assert "Task: " in result["final_result"]


def test_edge_case_empty_plan(llm_configs, test_prompts_dir):
    """Test handling of an empty plan."""
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        mock_llm = Mock()
        # Return empty plan
        mock_llm.invoke.return_value = AIMessage(content="")
        mock_openai.return_value = mock_llm
        
        agent = PlanAndSolveAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
        
        state = {
            "input": "Write a report on climate change",
            "chat_history": []
        }
        
        result = agent._generate_plan(state)
        
        # Should handle empty plan gracefully
        assert "plan" in result
        assert len(result["plan"]) > 0  # Should have fallback plan
        

def test_run_end_to_end(llm_configs, test_prompts_dir):
    """Test running the entire agent workflow with mocked responses."""
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        # Create mocked LLMs for planner and executor
        mock_planner = Mock()
        mock_executor = Mock()
        
        # Setup responses
        plan_response = AIMessage(content="1. Research climate change\n2. Write report")
        execute_response1 = AIMessage(content="Researched climate change topics")
        execute_response2 = AIMessage(content="Wrote report on findings")
        final_response = AIMessage(content="Final comprehensive report on climate change")
        
        # Setup mock returns for different calls
        mock_planner.invoke.side_effect = [plan_response, final_response]
        mock_executor.invoke.side_effect = [execute_response1, execute_response2]
        
        # Setup mock openai to return different mocks based on parameters
        def side_effect(model=None, **kwargs):
            if model == "gpt-4-turbo":
                return mock_planner
            else:
                return mock_executor
                
        mock_openai.side_effect = side_effect
        
        # Create the agent
        agent = PlanAndSolveAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
        
        # Mock the compiled graph
        mock_graph = Mock()
        agent.graph = mock_graph
        
        # Setup the final state that would be returned by the graph
        final_state = {
            "input": "Write a report on climate change",
            "plan": ["Research climate change", "Write report"],
            "current_step_index": 2,
            "step_results": ["Researched climate change topics", "Wrote report on findings"],
            "plan_done": True,
            "final_result": "Final comprehensive report on climate change",
            "chat_history": []
        }
        mock_graph.invoke.return_value = final_state
        
        # Run the agent
        result = agent.run("Write a report on climate change")
        
        # Check results
        assert "output" in result
        assert result["output"] == "Final comprehensive report on climate change"
        
        # Verify the graph was invoked with correct initial state
        mock_graph.invoke.assert_called_once()
        call_args = mock_graph.invoke.call_args[0][0]
        assert "input" in call_args
        assert call_args["input"] == "Write a report on climate change"


def test_stream_functionality(llm_configs, test_prompts_dir):
    """Test the streaming functionality."""
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        mock_openai.return_value = Mock()
        agent = PlanAndSolveAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
        
        # Mock the compiled graph's stream method
        mock_graph = Mock()
        agent.graph = mock_graph
        
        # Create generator for stream to yield
        def mock_stream_generator():
            yield {"node": "generate_plan", "plan": ["Step 1", "Step 2"]}
            yield {"node": "execute_step", "step_results": ["Result of Step 1"]}
            yield {"node": "execute_step", "step_results": ["Result of Step 1", "Result of Step 2"]}
            yield {"node": "aggregate_results", "final_result": "Final answer"}
            
        mock_graph.stream.return_value = mock_stream_generator()
        
        # Use stream method and collect results
        results = list(agent.stream("Write a report"))
        
        # Verify streaming results
        assert len(results) == 4
        assert "plan" in results[0]
        assert "step_results" in results[1]
        assert "final_result" in results[3]
        
        # Verify the graph's stream method was called with correct initial state
        mock_graph.stream.assert_called_once()
        call_args = mock_graph.stream.call_args[0][0]
        assert "input" in call_args
        assert call_args["input"] == "Write a report"


def test_stream_error_handling(llm_configs, test_prompts_dir):
    """Test error handling in the stream method."""
    with patch("langchain_openai.ChatOpenAI") as mock_openai:
        mock_openai.return_value = Mock()
        agent = PlanAndSolveAgent(prompt_dir=str(test_prompts_dir), llm_configs=llm_configs)
        
        # Mock the compiled graph to raise an exception
        mock_graph = Mock()
        agent.graph = mock_graph
        mock_graph.stream.side_effect = Exception("Stream error")
        
        # Use stream method and collect results
        results = list(agent.stream("Write a report"))
        
        # Verify error handling
        assert len(results) == 1
        assert "error" in results[0]
        assert "Stream error" in results[0]["error"]