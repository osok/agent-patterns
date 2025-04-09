"""Tests for the Self-Discovery Agent pattern."""

import unittest
from unittest.mock import MagicMock, patch
import json
import logging
from pathlib import Path

from agent_patterns.patterns.self_discovery_agent import SelfDiscoveryAgent, SelfDiscoveryState


class TestSelfDiscoveryAgent(unittest.TestCase):
    """Test cases for the Self-Discovery Agent implementation."""

    def setUp(self):
        """Set up test fixtures."""
        # Configure minimal LLM configs for testing
        self.llm_configs = {
            "discovery": {"provider": "openai", "model": "gpt-4"},
            "execution": {"provider": "openai", "model": "gpt-3.5-turbo"}
        }
        
        # Patch the LLM initialization to avoid actual API calls
        self.patcher = patch('agent_patterns.core.base_agent.BaseAgent._get_llm')
        self.mock_get_llm = self.patcher.start()
        
        # Create a mock LLM that returns predictable responses
        self.mock_llm = MagicMock()
        self.mock_llm.invoke.return_value = MagicMock(content="Mock response")
        self.mock_get_llm.return_value = self.mock_llm
        
        # Create a temporary reasoning modules file for testing
        self.test_modules = [
            {
                "name": "Test Module 1",
                "description": "Test description 1"
            },
            {
                "name": "Test Module 2",
                "description": "Test description 2"
            }
        ]
        
        # Patch the _load_reasoning_modules method to use test modules
        self.modules_patcher = patch.object(
            SelfDiscoveryAgent, 
            '_load_reasoning_modules', 
            return_value=self.test_modules
        )
        self.mock_load_modules = self.modules_patcher.start()
        
        # Create agent instance
        self.agent = SelfDiscoveryAgent(
            llm_configs=self.llm_configs,
            prompt_dir="src/agent_patterns/prompts",
            log_level=logging.ERROR  # Reduce logging noise during tests
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()
        self.modules_patcher.stop()
    
    def test_init(self):
        """Test agent initialization."""
        self.assertIsNotNone(self.agent)
        self.assertIsNotNone(self.agent.graph)
        self.assertEqual(len(self.agent.reasoning_modules), 2)
        self.mock_get_llm.assert_any_call('discovery')
        self.mock_get_llm.assert_any_call('execution')
    
    def test_get_default_reasoning_modules(self):
        """Test the _get_default_reasoning_modules method."""
        # Use a fresh agent without mocking _load_reasoning_modules
        self.modules_patcher.stop()
        
        # Patch open to raise an exception so it falls back to defaults
        with patch('builtins.open', side_effect=FileNotFoundError):
            agent = SelfDiscoveryAgent(
                llm_configs=self.llm_configs,
                log_level=logging.ERROR
            )
            
            # Check that we get default modules
            self.assertGreater(len(agent.reasoning_modules), 0)
            # Spot check some expected modules
            module_names = [m["name"] for m in agent.reasoning_modules]
            self.assertIn("Critical Thinking", module_names)
            self.assertIn("Step by Step Thinking", module_names)
            
        # Restart the modules patcher for subsequent tests
        self.modules_patcher = patch.object(
            SelfDiscoveryAgent, 
            '_load_reasoning_modules', 
            return_value=self.test_modules
        )
        self.mock_load_modules = self.modules_patcher.start()
    
    def test_select_reasoning_modules(self):
        """Test the _select_reasoning_modules method."""
        # Setup state
        state = {
            "input": "Test task",
            "chat_history": [],
            "reasoning_modules": self.test_modules
        }
        
        # Mock prompt loading
        with patch('agent_patterns.core.base_agent.BaseAgent._load_prompt_template') as mock_load_prompt:
            mock_prompt = MagicMock()
            mock_prompt.invoke.return_value.to_messages.return_value = []
            mock_load_prompt.return_value = mock_prompt
            
            # Mock the selection response to include module names
            # Manually set up the mock to match our parsing logic
            parse_modules_patcher = patch.object(
                self.agent,
                '_parse_selected_modules',
                return_value=["Test Module 1", "Test Module 2"]
            )
            parse_modules_mock = parse_modules_patcher.start()
            
            try:
                # Call the method
                result = self.agent._select_reasoning_modules(state)
                
                # Check results
                self.assertIn("selected_modules", result)
                self.assertIn("chat_history", result)
                self.assertEqual(len(result["selected_modules"]), 2)
                self.assertIn("Test Module 1", result["selected_modules"])
                self.assertIn("Test Module 2", result["selected_modules"])
            finally:
                parse_modules_patcher.stop()
    
    def test_parse_selected_modules(self):
        """Test the _parse_selected_modules method."""
        # Test with a well-formatted response
        response1 = """
        I recommend the following modules:
        1. Test Module 1 - This is perfect for this task
        2. Test Module 2 - This will help with analysis
        """
        result1 = self.agent._parse_selected_modules(response1)
        self.assertEqual(len(result1), 2)
        self.assertIn("Test Module 1", result1)
        self.assertIn("Test Module 2", result1)
        
        # Test with a response that doesn't contain module names
        response2 = "I recommend using critical thinking"
        result2 = self.agent._parse_selected_modules(response2)
        self.assertEqual(len(result2), 2)  # Should fall back to defaults
    
    def test_adapt_reasoning_modules(self):
        """Test the _adapt_reasoning_modules method."""
        # Setup state
        state = {
            "input": "Test task",
            "chat_history": [],
            "selected_modules": ["Test Module 1", "Test Module 2"]
        }
        
        # Mock prompt loading
        with patch('agent_patterns.core.base_agent.BaseAgent._load_prompt_template') as mock_load_prompt:
            mock_prompt = MagicMock()
            mock_prompt.invoke.return_value.to_messages.return_value = []
            mock_load_prompt.return_value = mock_prompt
            
            # Call the method
            result = self.agent._adapt_reasoning_modules(state)
            
            # Check results
            self.assertIn("adapted_modules", result)
            self.assertIn("chat_history", result)
            self.assertEqual(len(result["adapted_modules"]), 1)
            self.assertEqual(result["adapted_modules"][0], "Mock response")
    
    def test_implement_reasoning_structure(self):
        """Test the _implement_reasoning_structure method."""
        # Setup state
        state = {
            "input": "Test task",
            "chat_history": [],
            "adapted_modules": ["Adapted module descriptions go here"]
        }
        
        # Mock prompt loading
        with patch('agent_patterns.core.base_agent.BaseAgent._load_prompt_template') as mock_load_prompt:
            mock_prompt = MagicMock()
            mock_prompt.invoke.return_value.to_messages.return_value = []
            mock_load_prompt.return_value = mock_prompt
            
            # Mock a JSON response
            json_response = """
            Here's the plan:
            {
              "steps": [
                {
                  "step": 1,
                  "name": "Analyze",
                  "description": "Analyze the problem"
                },
                {
                  "step": 2,
                  "name": "Solve",
                  "description": "Solve the problem"
                }
              ]
            }
            """
            self.mock_llm.invoke.return_value = MagicMock(content=json_response)
            
            # Call the method
            result = self.agent._implement_reasoning_structure(state)
            
            # Check results
            self.assertIn("reasoning_structure", result)
            self.assertIn("chat_history", result)
            self.assertIn("steps", result["reasoning_structure"])
            self.assertEqual(len(result["reasoning_structure"]["steps"]), 2)
    
    def test_parse_reasoning_structure(self):
        """Test the _parse_reasoning_structure method."""
        # Test with JSON content
        json_text = """
        Let me create a structure:
        {
          "steps": [
            {
              "step": 1,
              "name": "Analyze",
              "description": "Analyze the problem"
            },
            {
              "step": 2,
              "name": "Solve",
              "description": "Solve the problem"
            }
          ]
        }
        """
        result1 = self.agent._parse_reasoning_structure(json_text)
        self.assertIn("steps", result1)
        self.assertEqual(len(result1["steps"]), 2)
        
        # Test with bulleted list
        list_text = """
        Here's my plan:
        1. First step
        2. Second step
        - Additional point
        • Another point
        """
        result2 = self.agent._parse_reasoning_structure(list_text)
        self.assertIn("steps", result2)
        self.assertEqual(len(result2["steps"]), 4)
        
        # Test with no structure
        no_structure = "Let me think about this..."
        result3 = self.agent._parse_reasoning_structure(no_structure)
        self.assertIn("plan", result3)
        self.assertEqual(result3["plan"], no_structure)
    
    def test_execute_reasoning_structure(self):
        """Test the _execute_reasoning_structure method."""
        # Setup state
        state = {
            "input": "Test task",
            "chat_history": [],
            "reasoning_structure": {
                "steps": [
                    {"step": 1, "name": "Analyze", "description": "Analyze the problem"},
                    {"step": 2, "name": "Solve", "description": "Solve the problem"}
                ]
            }
        }
        
        # Mock prompt loading
        with patch('agent_patterns.core.base_agent.BaseAgent._load_prompt_template') as mock_load_prompt:
            mock_prompt = MagicMock()
            mock_prompt.invoke.return_value.to_messages.return_value = []
            mock_load_prompt.return_value = mock_prompt
            
            # Set a specific execution response
            self.mock_llm.invoke.return_value = MagicMock(content="Execution result with solution")
            
            # Call the method
            result = self.agent._execute_reasoning_structure(state)
            
            # Check results
            self.assertIn("execution_result", result)
            self.assertIn("chat_history", result)
            self.assertEqual(result["execution_result"], "Execution result with solution")
    
    def test_format_final_answer(self):
        """Test the _format_final_answer method."""
        # Setup state
        state = {
            "execution_result": "Detailed execution result with final answer: 42"
        }
        
        # Call the method
        result = self.agent._format_final_answer(state)
        
        # Check results
        self.assertIn("final_answer", result)
        self.assertEqual(result["final_answer"], state["execution_result"])
    
    def test_run(self):
        """Test the run method."""
        # Mock the graph invoke method
        self.agent.graph.invoke = MagicMock(return_value={
            "final_answer": "Final test answer",
            "reasoning_structure": {"steps": ["Step 1", "Step 2"]}
        })
        
        # Call run
        result = self.agent.run("Test task")
        
        # Check results
        self.assertIn("output", result)
        self.assertIn("reasoning_structure", result)
        self.assertEqual(result["output"], "Final test answer")
        self.assertEqual(result["reasoning_structure"]["steps"], ["Step 1", "Step 2"])
    
    def test_stream(self):
        """Test the stream method."""
        # Mock the graph stream method
        mock_state1 = {"node": "select_modules", "selected_modules": ["Test Module 1"]}
        mock_state2 = {"node": "adapt_modules", "adapted_modules": ["Adapted description"]}
        mock_state3 = {"node": "final_answer", "final_answer": "Final answer"}
        
        # Setup the mock to yield three states
        self.agent.graph.stream = MagicMock(return_value=[mock_state1, mock_state2, mock_state3])
        
        # Call stream and collect results
        results = list(self.agent.stream("Test task"))
        
        # Check that we got the expected states
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], mock_state1)
        self.assertEqual(results[1], mock_state2)
        self.assertEqual(results[2], mock_state3)

    def test_error_handling_select(self):
        """Test error handling in the _select_reasoning_modules method."""
        # Setup state
        state = {
            "input": "Test task",
            "chat_history": [],
            "reasoning_modules": self.test_modules
        }
        
        # Mock prompt loading to raise an exception
        with patch('agent_patterns.core.base_agent.BaseAgent._load_prompt_template') as mock_load_prompt:
            mock_load_prompt.side_effect = Exception("Test error")
            
            # Call the method
            result = self.agent._select_reasoning_modules(state)
            
            # Check that we get fallback modules
            self.assertIn("selected_modules", result)
            self.assertEqual(len(result["selected_modules"]), 3)  # Should have 3 fallback modules
    
    def test_error_handling_adapt(self):
        """Test error handling in the _adapt_reasoning_modules method."""
        # Setup state
        state = {
            "input": "Test task",
            "chat_history": [],
            "selected_modules": ["Test Module 1"]
        }
        
        # Mock prompt loading to raise an exception
        with patch('agent_patterns.core.base_agent.BaseAgent._load_prompt_template') as mock_load_prompt:
            mock_load_prompt.side_effect = Exception("Test error")
            
            # Call the method
            result = self.agent._adapt_reasoning_modules(state)
            
            # Check that we get a fallback adaptation
            self.assertIn("adapted_modules", result)
            self.assertEqual(len(result["adapted_modules"]), 1)
            self.assertIn("Apply the selected reasoning methods", result["adapted_modules"][0])
    
    def test_error_handling_run(self):
        """Test error handling in the run method."""
        # Mock the graph invoke method to raise an exception
        self.agent.graph.invoke = MagicMock(side_effect=Exception("Test error"))
        
        # Call run
        result = self.agent.run("Test task")
        
        # Check that we get an error response
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Test error")


if __name__ == '__main__':
    unittest.main() 