"""
Unit tests for the REWOO (Reasoning Without Observation) agent pattern.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import sys
from typing import Dict, Any, List, Union, Optional, TypedDict

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent_patterns.patterns.rewoo_agent import REWOOAgent, REWOOState


class MockLLM:
    """Mock LLM for testing."""
    
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.invoke_calls = []
        self.should_fail = False
    
    def invoke(self, messages):
        """Mock invoke method."""
        self.invoke_calls.append(messages)
        
        # Simulate LLM failure if configured
        if self.should_fail:
            raise Exception("Mock LLM failure")
        
        # For simplicity, we'll check the messages content
        message_str = str(messages)
        
        if "planning" in message_str or "plan" in message_str.lower():
            return self.responses.get("planning", "Step 1: Test step")
            
        # Check if this is a solver prompt for execution
        if "step_description" in message_str and not "final" in message_str.lower():
            return self.responses.get("solving", "Executed step")
            
        # Check if this is a final answer prompt
        if "synthesizes" in message_str or "final" in message_str.lower() or "execution_summary" in message_str:
            return self.responses.get("final", "This is the final synthesized answer based on all the steps.")
        
        # Default response
        return "Default mock response"


class MockGraph:
    """Mock LangGraph for testing."""
    
    def __init__(self):
        self.invoke_called = False
        self.last_input = None
        self.last_config = None
        
    def invoke(self, state, config=None):
        """Mock invoke method."""
        self.invoke_called = True
        self.last_input = state
        self.last_config = config
        
        # Simulate plan_steps node execution
        # In a real graph, this would call the _plan_steps method
        # which would use the planner LLM
        if "execution_complete" not in state or not state["execution_complete"]:
            # This will trigger the exception if planner_llm.should_fail is True
            # We need to manually trigger the error to simulate what would happen
            # in the real graph when calling the planner LLM
            if hasattr(self, "planner_llm") and getattr(self.planner_llm, "should_fail", False):
                raise Exception("Mock LLM failure")
        
        # Just return a completed state
        return {
            **state,
            "execution_complete": True,
            "final_answer": "This is the final synthesized answer based on all the steps."
        }
    
    def stream(self, state, config=None):
        """Mock stream method."""
        # Store the config
        self.last_config = config
        
        # Return a simple iterator with one event
        yield {
            "state": {
                **state,
                "execution_complete": True,
                "final_answer": "This is the final synthesized answer based on all the steps."
            }
        }


class MockPromptTemplate:
    """Mock ChatPromptTemplate for testing."""
    
    def __init__(self, messages=None):
        self.messages = messages or []
    
    def format_messages(self, **kwargs):
        """Return formatted messages."""
        # Include the kwargs content in the message for the MockLLM to interpret
        arg_content = ", ".join(f"{k}: {v}" for k, v in kwargs.items())
        return [f"Formatted prompt with args: {arg_content}"]


class TestREWOOAgent(unittest.TestCase):
    """Tests for the REWOO agent pattern."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock LLMs for planner and solver roles
        self.planner_llm = MockLLM(responses={
            "planning": """
Step 1: Research basic information
Use the search tool to find general information.

Step 2: Analyze the findings
Look at the search results and analyze them.

Step 3: Summarize results
Create a summary of what was found.
"""
        })
        
        self.solver_llm = MockLLM(responses={
            "solving": """I'll execute this step by searching for information.

TOOL: search
query: test query
""",
            "final": "This is the final synthesized answer based on all the steps."
        })
        
        # Create a custom subclass that overrides problematic methods
        class TestREWOOAgent(REWOOAgent):
            """Test subclass that overrides methods for testing."""
            
            def _get_llm(self, role="default"):
                """Override _get_llm to return the mock LLMs directly."""
                if role == "planner":
                    return self.llm_configs["planner"]
                elif role == "solver":
                    return self.llm_configs["solver"]
                else:
                    return self.llm_configs.get(role, self.llm_configs["solver"])
        
        # Create agent but with mocked graph
        self.agent = TestREWOOAgent(
            llm_configs={
                "planner": self.planner_llm,
                "solver": self.solver_llm
            },
            tool_registry={"search": lambda **kwargs: "Mock search result"}
        )
        
        # Mock the _load_prompt_template method
        self.prompt_template = MockPromptTemplate()
        self.prompt_patcher = patch.object(
            self.agent, 
            '_load_prompt_template', 
            return_value=self.prompt_template
        )
        self.mock_load_prompt = self.prompt_patcher.start()
        
        # Mock the graph with our simplified version
        self.mock_graph = MockGraph()
        self.agent.graph = self.mock_graph
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.prompt_patcher.stop()
    
    def test_full_agent_run(self):
        """Test the full agent execution flow."""
        # Run the agent
        result = self.agent.run("Test task")
        
        # Verify the graph was invoked
        self.assertTrue(self.mock_graph.invoke_called)
        
        # Check if we got a result
        self.assertIsNotNone(result)
        self.assertEqual(result, "This is the final synthesized answer based on all the steps.")

    def test_edge_case_empty_input(self):
        """Test handling of empty input."""
        # Run the agent with empty input
        result = self.agent.run("")
        
        # Should still complete without errors
        self.assertIsNotNone(result)
        self.assertTrue(self.mock_graph.invoke_called)

    def test_edge_case_very_long_input(self):
        """Test handling of very long input."""
        # Create a very long input
        long_input = "Test " * 500  # 2000+ characters
        
        # Run the agent
        result = self.agent.run(long_input)
        
        # Should handle long input without issues
        self.assertIsNotNone(result)

    def test_plan_steps(self):
        """Test the planning step in isolation."""
        # Create a state for planning
        state = {
            "input": "Research quantum computing",
            "plan": [],
            "current_step_index": 0,
            "execution_results": [],
            "iteration_count": 0,
            "execution_complete": False,
            "final_answer": None
        }
        
        # Run the planning step
        result_state = self.agent._plan_steps(state)
        
        # Verify planning output
        self.assertIn("plan", result_state)
        self.assertGreater(len(result_state["plan"]), 0)
        self.assertEqual(result_state["plan"][0]["step_id"], 1)

    def test_execute_step(self):
        """Test the step execution in isolation."""
        # Create a state with a plan
        state = {
            "input": "Test task",
            "plan": [
                {
                    "step_id": 1,
                    "description": "Step 1: Search for information",
                    "details": "Use search to find data",
                    "tools": ["search"],
                    "depends_on": []
                }
            ],
            "current_step_index": 0,
            "execution_results": [],
            "iteration_count": 0,
            "execution_complete": False,
            "final_answer": None
        }
        
        # Execute the step
        result_state = self.agent._execute_step(state)
        
        # Verify execution results
        self.assertEqual(result_state["current_step_index"], 1)
        self.assertEqual(len(result_state["execution_results"]), 1)
        self.assertEqual(result_state["iteration_count"], 1)
        
    def test_check_completion(self):
        """Test the completion checking logic."""
        # Test incomplete state
        incomplete_state = {
            "plan": [{"step_id": 1}, {"step_id": 2}],
            "current_step_index": 1,
            "execution_complete": False
        }
        result = self.agent._check_completion(incomplete_state)
        self.assertFalse(result["execution_complete"])
        
        # Test complete state
        complete_state = {
            "plan": [{"step_id": 1}, {"step_id": 2}],
            "current_step_index": 2,
            "execution_complete": False
        }
        result = self.agent._check_completion(complete_state)
        self.assertTrue(result["execution_complete"])

    def test_format_final_answer(self):
        """Test the final answer formatting."""
        # Create a state with execution results
        state = {
            "input": "Research quantum computing",
            "plan": [
                {"step_id": 1, "description": "Research basics"}
            ],
            "execution_results": [
                {
                    "step_id": 1,
                    "result": "Found information about quantum computing",
                    "tool_outputs": [{"tool": "search", "output": "Quantum computing uses qubits"}],
                    "success": True
                }
            ],
            "current_step_index": 1,
            "iteration_count": 1,
            "execution_complete": True,
            "final_answer": None
        }
        
        # Generate final answer
        result_state = self.agent._format_final_answer(state)
        
        # Verify result
        self.assertIsNotNone(result_state["final_answer"])
        self.assertIn("final", result_state["final_answer"])

    def test_streaming_functionality(self):
        """Test the streaming functionality."""
        # Create a collector for streamed outputs
        outputs = []
        
        # Stream the agent execution
        for chunk in self.agent.stream("Test streaming"):
            outputs.append(chunk)
        
        # Verify we got streaming output
        self.assertGreater(len(outputs), 0)
        self.assertEqual(outputs[0], "This is the final synthesized answer based on all the steps.")

    def test_error_handling_llm_failure(self):
        """Test error handling for LLM failures."""
        # Configure the planner LLM to fail
        self.planner_llm.should_fail = True
        
        # Associate the planner LLM with the mock graph
        self.mock_graph.planner_llm = self.planner_llm
        
        try:
            # Run the agent
            result = self.agent.run("Test task with failing LLM")
            # This should fail, so we shouldn't reach this point
            self.fail("Expected an exception but none was raised")
        except Exception as e:
            # Verify we got the expected exception
            self.assertIn("Mock LLM failure", str(e))
        finally:
            # Reset for other tests
            self.planner_llm.should_fail = False

    def test_extraction_of_tool_calls(self):
        """Test extraction of tool calls from LLM output."""
        # Test with a single tool call
        single_tool_text = """I'll search for information.

TOOL: search
query: quantum computing
"""
        tool_calls = self.agent._extract_tool_calls(single_tool_text)
        self.assertEqual(len(tool_calls), 1)
        self.assertEqual(tool_calls[0]["name"], "search")
        self.assertEqual(tool_calls[0]["args"]["query"], "quantum computing")
        
        # Test with multiple tool calls
        multi_tool_text = """I'll execute multiple tools.

TOOL: search
query: first search

Now I'll use another tool:

TOOL: calculator
expression: 2+2
"""
        tool_calls = self.agent._extract_tool_calls(multi_tool_text)
        self.assertEqual(len(tool_calls), 2)
        
        # Test with no tool calls
        no_tool_text = "I don't need to use any tools for this step."
        tool_calls = self.agent._extract_tool_calls(no_tool_text)
        self.assertEqual(len(tool_calls), 0)

    def test_tool_failure_handling(self):
        """Test handling of tool failures."""
        # Create a tool that always fails
        def failing_tool(**kwargs):
            raise Exception("Tool execution failed")
            
        # Add the failing tool to the agent
        self.agent.tool_registry["failing_tool"] = failing_tool
        
        # Create a state that will use the failing tool
        state = {
            "input": "Test failing tool",
            "plan": [
                {
                    "step_id": 1,
                    "description": "Use failing tool",
                    "details": "This will fail",
                    "tools": ["failing_tool"],
                    "depends_on": []
                }
            ],
            "current_step_index": 0,
            "execution_results": [],
            "iteration_count": 0,
            "execution_complete": False,
            "final_answer": None
        }
        
        # Set up the solver to call the failing tool
        self.solver_llm.responses["solving"] = """I'll use the failing tool.

TOOL: failing_tool
param: test
"""
        
        # Execute the step
        result_state = self.agent._execute_step(state)
        
        # Verify error handling
        self.assertEqual(result_state["current_step_index"], 1)  # Should still advance
        self.assertEqual(len(result_state["execution_results"]), 1)  # Should record the result
        
        # The execution results should include the error
        tool_outputs = result_state["execution_results"][0]["tool_outputs"]
        self.assertEqual(len(tool_outputs), 1)
        self.assertTrue(any("error" in str(output) for output in tool_outputs))

    def test_max_iterations_limit(self):
        """Test that the agent respects the max iterations limit."""
        # Create an agent with a low max_iterations
        agent_with_limit = type(self.agent)(
            llm_configs={
                "planner": self.planner_llm,
                "solver": self.solver_llm
            },
            tool_registry={"search": lambda **kwargs: "Mock search result"},
            max_iterations=2
        )
        
        # Give it our mocks
        agent_with_limit._load_prompt_template = MagicMock(return_value=self.prompt_template)
        agent_with_limit.graph = self.mock_graph
        
        # Create a state that would need more than max_iterations
        state = {
            "input": "Test max iterations",
            "plan": [
                {"step_id": 1, "description": "Step 1"},
                {"step_id": 2, "description": "Step 2"},
                {"step_id": 3, "description": "Step 3"}
            ],
            "current_step_index": 0,
            "execution_results": [],
            "iteration_count": 1,  # Start at 1
            "execution_complete": False,
            "final_answer": None
        }
        
        # Execute a step
        result = agent_with_limit._execute_step(state)
        
        # Execute another step (should hit the limit)
        result = agent_with_limit._execute_step(result)
        
        # Should mark execution as complete due to hitting the limit
        self.assertTrue(result["execution_complete"])
        self.assertEqual(result["iteration_count"], 3)  # Started at 1, +2 iterations

    def test_tool_provider_integration(self):
        """Test that the agent can use tools from the tool_provider."""
        # Create a mock tool provider
        mock_tool_provider = MagicMock()
        
        # Configure the tool provider to return mock tools
        mock_tool_provider.list_tools.return_value = [
            {"name": "provider_tool", "description": "Tool from provider", "parameters": {}}
        ]
        
        # Configure tool execution to return a predictable result
        mock_tool_provider.execute_tool.return_value = "Result from provider_tool"
        
        # Create agent with the mock tool provider
        agent = type(self.agent)(
            llm_configs={
                "planner": self.planner_llm,
                "solver": self.solver_llm
            },
            tool_registry={"registry_tool": lambda **kwargs: "Result from registry_tool"},
            tool_provider=mock_tool_provider
        )
        
        # Mock the _load_prompt_template method
        agent._load_prompt_template = MagicMock(return_value=self.prompt_template)
        
        # Create a sample plan with a step that would use the provider tool
        plan = [{
            "step_id": 1,
            "description": "Test provider tool",
            "details": "Use provider_tool to get information",
            "tools": ["provider_tool"],
            "depends_on": []
        }]
        
        # Create a state for execution
        state = {
            "input": "Test provider tool",
            "plan": plan,
            "current_step_index": 0,
            "execution_results": [],
            "iteration_count": 0,
            "execution_complete": False,
            "final_answer": None
        }
        
        # Configure the solver LLM to use the provider tool
        self.solver_llm.responses["solving"] = """I'll use the provider tool.

TOOL: provider_tool
param: test
"""
        
        # Execute the step
        result_state = agent._execute_step(state)
        
        # Verify that the tool provider was used
        mock_tool_provider.execute_tool.assert_called_once()
        
        # Check that the tool output was included in the results
        self.assertEqual(len(result_state["execution_results"]), 1)
        tool_outputs = result_state["execution_results"][0]["tool_outputs"]
        self.assertEqual(len(tool_outputs), 1)
        self.assertEqual(tool_outputs[0]["tool"], "provider_tool")
        self.assertEqual(tool_outputs[0]["output"], "Result from provider_tool")

    def test_memory_integration(self):
        """Test that the agent can retrieve and save memory."""
        # Create a mock memory system
        mock_memory = MagicMock()
        mock_memory.memories = {"semantic": MagicMock(), "episodic": MagicMock()}
        
        # Configure memory retrieval to return mock results
        mock_retrieve_memories = MagicMock(return_value={
            "semantic": [{"fact": "This is a semantic memory"}],
            "episodic": [{"event": "This is an episodic memory"}]
        })
        
        # Create a mock for saving memory
        mock_save_memory = MagicMock()
        
        # Create agent with the mock memory
        agent = type(self.agent)(
            llm_configs={
                "planner": self.planner_llm,
                "solver": self.solver_llm
            },
            tool_registry={"search": lambda **kwargs: "Mock search result"},
            memory=mock_memory,
            memory_config={"semantic": True, "episodic": True}
        )
        
        # Replace memory methods with mocks
        agent.sync_retrieve_memories = mock_retrieve_memories
        agent.sync_save_memory = mock_save_memory
        
        # Mock the _load_prompt_template method
        agent._load_prompt_template = MagicMock(return_value=self.prompt_template)
        
        # Test memory in plan steps
        plan_state = {
            "input": "Test memory",
            "plan": [],
            "current_step_index": 0,
            "execution_results": [],
            "iteration_count": 0,
            "execution_complete": False,
            "final_answer": None
        }
        
        # Execute plan steps
        plan_result = agent._plan_steps(plan_state)
        
        # Verify memory was retrieved for planning
        mock_retrieve_memories.assert_called_with("Test memory")
        
        # Verify memory was saved after planning
        calls = mock_save_memory.call_args_list
        episodic_planning_call = False
        for call in calls:
            args, kwargs = call
            if kwargs.get("memory_type") == "episodic" and kwargs.get("item", {}).get("event_type") == "plan_generation":
                episodic_planning_call = True
                break
        
        self.assertTrue(episodic_planning_call, "Memory was not saved properly after planning")
        
        # Test memory in execute step
        exec_state = {
            "input": "Test memory",
            "plan": [{
                "step_id": 1,
                "description": "Test memory step",
                "details": "Use memory to find information",
                "tools": [],
                "depends_on": []
            }],
            "current_step_index": 0,
            "execution_results": [],
            "iteration_count": 0,
            "execution_complete": False,
            "final_answer": None
        }
        
        # Reset the mock to clear call history
        mock_retrieve_memories.reset_mock()
        mock_save_memory.reset_mock()
        
        # Execute a step
        exec_result = agent._execute_step(exec_state)
        
        # Verify memory was retrieved for step execution
        self.assertTrue(mock_retrieve_memories.called, "Memory was not retrieved during step execution")
        
        # Verify memory was saved after step execution
        calls = mock_save_memory.call_args_list
        episodic_step_call = False
        for call in calls:
            args, kwargs = call
            if kwargs.get("memory_type") == "episodic" and kwargs.get("item", {}).get("event_type") == "step_execution":
                episodic_step_call = True
                break
        
        self.assertTrue(episodic_step_call, "Memory was not saved properly after step execution")
        
        # Test memory in final answer
        final_state = {
            "input": "Test memory",
            "plan": [{
                "step_id": 1,
                "description": "Test memory step",
                "details": "Use memory to find information",
                "tools": [],
                "depends_on": []
            }],
            "current_step_index": 1,
            "execution_results": [{
                "step_id": 1,
                "result": "Test result",
                "tool_outputs": [],
                "success": True
            }],
            "iteration_count": 1,
            "execution_complete": True,
            "final_answer": None
        }
        
        # Reset the mock to clear call history
        mock_retrieve_memories.reset_mock()
        mock_save_memory.reset_mock()
        
        # Generate final answer
        final_result = agent._format_final_answer(final_state)
        
        # Verify memory was retrieved for final answer
        self.assertTrue(mock_retrieve_memories.called, "Memory was not retrieved during final answer generation")
        
        # Verify both types of memory were saved
        calls = mock_save_memory.call_args_list
        episodic_final_call = False
        semantic_final_call = False
        
        for call in calls:
            args, kwargs = call
            if kwargs.get("memory_type") == "episodic" and kwargs.get("item", {}).get("event_type") == "final_result":
                episodic_final_call = True
            if kwargs.get("memory_type") == "semantic":
                semantic_final_call = True
        
        self.assertTrue(episodic_final_call, "Episodic memory was not saved properly after final answer")
        self.assertTrue(semantic_final_call, "Semantic memory was not saved properly after final answer")


if __name__ == "__main__":
    unittest.main() 