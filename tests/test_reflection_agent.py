"""Tests for the Reflection Agent pattern."""

import unittest
from unittest.mock import MagicMock, patch
import logging

from agent_patterns.patterns.reflection_agent import ReflectionAgent, ReflectionState


class TestReflectionAgent(unittest.TestCase):
    """Test cases for the Reflection Agent implementation."""

    def setUp(self):
        """Set up test fixtures."""
        # Configure minimal LLM configs for testing
        self.llm_configs = {
            "generator": {"provider": "openai", "model": "gpt-3.5-turbo"},
            "critic": {"provider": "openai", "model": "gpt-4"}
        }
        
        # Patch the LLM initialization to avoid actual API calls
        self.patcher = patch('agent_patterns.core.base_agent.BaseAgent._get_llm')
        self.mock_get_llm = self.patcher.start()
        
        # Create a mock LLM that returns predictable responses
        self.mock_llm = MagicMock()
        self.mock_llm.invoke.return_value = MagicMock(content="Mock response")
        self.mock_get_llm.return_value = self.mock_llm
        
        # Create agent instance
        self.agent = ReflectionAgent(
            llm_configs=self.llm_configs,
            prompt_dir="src/agent_patterns/prompts",
            log_level=logging.ERROR  # Reduce logging noise during tests
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()
    
    def test_init(self):
        """Test agent initialization."""
        self.assertIsNotNone(self.agent)
        self.assertIsNotNone(self.agent.graph)
        self.mock_get_llm.assert_any_call('generator')
        self.mock_get_llm.assert_any_call('critic')
    
    def test_generate_initial_output(self):
        """Test the generate_initial_output method."""
        # Setup state
        state = {
            "input": "Test query",
            "chat_history": []
        }
        
        # Mock prompt loading
        with patch('agent_patterns.core.base_agent.BaseAgent._load_prompt_template') as mock_load_prompt:
            mock_prompt = MagicMock()
            mock_prompt.invoke.return_value.to_messages.return_value = []
            mock_load_prompt.return_value = mock_prompt
            
            # Call the method
            result = self.agent._generate_initial_output(state)
            
            # Check results
            self.assertIn("initial_output", result)
            self.assertIn("chat_history", result)
            self.assertEqual(result["initial_output"], "Mock response")
    
    def test_reflect_on_output(self):
        """Test the reflect_on_output method."""
        # Setup state
        state = {
            "input": "Test query",
            "chat_history": [],
            "initial_output": "Initial test response"
        }
        
        # Mock prompt loading
        with patch('agent_patterns.core.base_agent.BaseAgent._load_prompt_template') as mock_load_prompt:
            mock_prompt = MagicMock()
            mock_prompt.invoke.return_value.to_messages.return_value = []
            mock_load_prompt.return_value = mock_prompt
            
            # Call the method
            result = self.agent._reflect_on_output(state)
            
            # Check results
            self.assertIn("reflection", result)
            self.assertIn("chat_history", result)
            self.assertEqual(result["reflection"], "Mock response")
    
    def test_check_refinement_needed(self):
        """Test the check_refinement_needed method."""
        # Test case 1: Refinement needed
        state1 = {"reflection": "This response lacks important details and is incomplete."}
        result1 = self.agent._check_refinement_needed(state1)
        self.assertTrue(result1["needs_refinement"])
        
        # Test case 2: No refinement needed
        state2 = {"reflection": "This response is comprehensive and well-structured."}
        result2 = self.agent._check_refinement_needed(state2)
        self.assertFalse(result2["needs_refinement"])
    
    def test_refine_output(self):
        """Test the refine_output method."""
        # Setup state
        state = {
            "input": "Test query",
            "chat_history": [],
            "initial_output": "Initial test response",
            "reflection": "The response needs more details."
        }
        
        # Mock prompt loading
        with patch('agent_patterns.core.base_agent.BaseAgent._load_prompt_template') as mock_load_prompt:
            mock_prompt = MagicMock()
            mock_prompt.invoke.return_value.to_messages.return_value = []
            mock_load_prompt.return_value = mock_prompt
            
            # Call the method
            result = self.agent._refine_output(state)
            
            # Check results
            self.assertIn("refined_output", result)
            self.assertIn("final_answer", result)
            self.assertIn("chat_history", result)
            self.assertEqual(result["refined_output"], "Mock response")
            self.assertEqual(result["final_answer"], "Mock response")
    
    def test_run(self):
        """Test the run method."""
        # Mock the graph invoke method
        self.agent.graph.invoke = MagicMock(return_value={
            "final_answer": "Final test answer"
        })
        
        # Call run
        result = self.agent.run("Test query")
        
        # Check results
        self.assertIn("output", result)
        self.assertEqual(result["output"], "Final test answer")

    def test_prepare_final_output_no_refinement(self):
        """Test the _prepare_final_output method when no refinement is needed."""
        # Setup state with no refinement needed
        state = {
            "needs_refinement": False,
            "initial_output": "Initial test response",
            "refined_output": None,
            "final_answer": None
        }
        
        # Call the method
        result = self.agent._prepare_final_output(state)
        
        # Check that initial_output is used as the final_answer
        self.assertIn("final_answer", result)
        self.assertEqual(result["final_answer"], "Initial test response")

    def test_prepare_final_output_with_refinement(self):
        """Test the _prepare_final_output method when refinement has been done."""
        # Setup state with refinement done
        state = {
            "needs_refinement": True,
            "initial_output": "Initial test response",
            "refined_output": "Refined test response",
            "final_answer": "Refined test response"
        }
        
        # Call the method
        result = self.agent._prepare_final_output(state)
        
        # Check that no changes are made since final_answer is already set
        self.assertEqual(result, {})

    def test_prepare_final_output_missing_answer(self):
        """Test the _prepare_final_output method when final_answer is missing."""
        # Setup state with refinement done but no final_answer set
        state = {
            "needs_refinement": True,
            "initial_output": "Initial test response",
            "refined_output": "Refined test response",
            "final_answer": None
        }
        
        # Call the method
        result = self.agent._prepare_final_output(state)
        
        # Check that refined_output is used as final_answer
        self.assertIn("final_answer", result)
        self.assertEqual(result["final_answer"], "Refined test response")

    def test_stream(self):
        """Test the stream method."""
        # Mock the graph stream method
        mock_state1 = {"node": "generate_initial", "initial_output": "First response"}
        mock_state2 = {"node": "reflect", "reflection": "Critique"}
        mock_state3 = {"node": "final_output", "final_answer": "Final answer"}
        
        # Setup the mock to yield three states
        self.agent.graph.stream = MagicMock(return_value=[mock_state1, mock_state2, mock_state3])
        
        # Call stream and collect results
        results = list(self.agent.stream("Test query"))
        
        # Check that we got the expected states
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], mock_state1)
        self.assertEqual(results[1], mock_state2)
        self.assertEqual(results[2], mock_state3)

    def test_generate_initial_output_error(self):
        """Test error handling in the generate_initial_output method."""
        # Setup state
        state = {
            "input": "Test query",
            "chat_history": []
        }
        
        # Mock prompt loading to raise an exception
        with patch('agent_patterns.core.base_agent.BaseAgent._load_prompt_template') as mock_load_prompt:
            mock_load_prompt.side_effect = Exception("Test error")
            
            # Call the method
            result = self.agent._generate_initial_output(state)
            
            # Check that we get a fallback response with the error
            self.assertIn("initial_output", result)
            self.assertIn("I apologize", result["initial_output"])
            self.assertIn("Test error", result["initial_output"])

    def test_reflect_on_output_error(self):
        """Test error handling in the reflect_on_output method."""
        # Setup state
        state = {
            "input": "Test query",
            "chat_history": [],
            "initial_output": "Initial test response"
        }
        
        # Mock prompt loading to raise an exception
        with patch('agent_patterns.core.base_agent.BaseAgent._load_prompt_template') as mock_load_prompt:
            mock_load_prompt.side_effect = Exception("Test error")
            
            # Call the method
            result = self.agent._reflect_on_output(state)
            
            # Check that we get a fallback reflection
            self.assertIn("reflection", result)
            self.assertIsNotNone(result["reflection"])
            self.assertTrue(len(result["reflection"]) > 0)

    def test_refine_output_error(self):
        """Test error handling in the refine_output method."""
        # Setup state
        state = {
            "input": "Test query",
            "chat_history": [],
            "initial_output": "Initial test response",
            "reflection": "The response needs more details."
        }
        
        # Mock prompt loading to raise an exception
        with patch('agent_patterns.core.base_agent.BaseAgent._load_prompt_template') as mock_load_prompt:
            mock_load_prompt.side_effect = Exception("Test error")
            
            # Call the method
            result = self.agent._refine_output(state)
            
            # Check that we get the initial output as fallback
            self.assertIn("refined_output", result)
            self.assertIn("final_answer", result)
            self.assertEqual(result["refined_output"], state["initial_output"])
            self.assertEqual(result["final_answer"], state["initial_output"])

    def test_run_error(self):
        """Test error handling in the run method."""
        # Mock the graph invoke method to raise an exception
        self.agent.graph.invoke = MagicMock(side_effect=Exception("Test error"))
        
        # Call run
        result = self.agent.run("Test query")
        
        # Check that we get an error response
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Test error")

    def test_edge_case_empty_input(self):
        """Test behavior with empty input."""
        # Mock the graph invoke method
        self.agent.graph.invoke = MagicMock(return_value={
            "final_answer": "I need more information to provide a helpful response."
        })
        
        # Call run with empty input
        result = self.agent.run("")
        
        # Check the response
        self.assertIn("output", result)
        self.assertTrue(len(result["output"]) > 0)


if __name__ == '__main__':
    unittest.main()