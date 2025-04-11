"""Tests for the LATS (Language Agent Tree Search) agent pattern."""

import os
import unittest
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage

from agent_patterns.patterns.lats_agent import LATSAgent, LATSState


class TestLATSAgent(unittest.TestCase):
    """Test suite for the LATS agent pattern."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock LLM configs
        self.llm_configs = {
            "thinking": {
                "provider": "mock",
                "model_name": "mock-model",
            },
            "evaluation": {
                "provider": "mock",
                "model_name": "mock-model",
            }
        }
        
        # Create a mock LLM for testing
        self.mock_llm = MagicMock()
        self.mock_llm.invoke.return_value = AIMessage(content="1. First option: This is step one\n2. Second option: This is step two\n3. Third option: This is step three")
        
        # Path to test prompts
        self.test_prompts_dir = os.path.join(os.path.dirname(__file__), "test_prompts")

    def _create_initial_state(self):
        """Create a basic initial state for testing."""
        return {
            "input_task": "Test task",
            "current_node_id": None,
            "nodes": {},
            "node_values": {},
            "explored_paths": [],
            "best_path": None,
            "best_path_value": 0,
            "iterations": 0,
            "max_iterations": 10,
            "max_depth": 3,
            "exploration_weight": 1.0,
            "final_answer": None
        }

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_initialization(self, mock_load_prompt_template, mock_get_llm):
        """Test that the agent initializes correctly with default parameters."""
        agent = LATSAgent(llm_configs=self.llm_configs)
        
        # Check that the graph was compiled
        self.assertIsNotNone(agent.graph)
        
        # Check default parameters
        self.assertEqual(agent.max_iterations, 10)
        self.assertEqual(agent.max_depth, 3)
        self.assertEqual(agent.exploration_weight, 1.0)
        self.assertEqual(agent.n_expansions, 3)

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_initialize_search(self, mock_load_prompt_template, mock_get_llm):
        """Test the _initialize_search method."""
        agent = LATSAgent(llm_configs=self.llm_configs)
        
        # Create initial state
        state = self._create_initial_state()
        
        # Run initialization
        updated_state = agent._initialize_search(state)
        
        # Merge the updates back to the state for our test checks
        state.update(updated_state)
        
        # Check that a root node was created
        self.assertEqual(len(state["nodes"]), 1)
        
        # Get the root node
        root_id = list(state["nodes"].keys())[0]
        root_node = state["nodes"][root_id]
        
        # Check root node properties
        self.assertEqual(root_node["content"], "Test task")
        self.assertEqual(root_node["depth"], 0)
        self.assertEqual(root_node["visits"], 0)
        self.assertEqual(root_node["parent_id"], None)
        self.assertEqual(len(root_node["children"]), 0)
        
        # Check that current_node_id points to root
        self.assertEqual(state["current_node_id"], root_id)
        
        # Check that root node has a neutral initial value
        self.assertEqual(state["node_values"][root_id], 0.5)

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_expand_node(self, mock_load_prompt_template, mock_get_llm):
        """Test the _expand_node method."""
        # Setup mocks
        mock_get_llm.return_value = self.mock_llm
        mock_template = MagicMock()
        mock_load_prompt_template.return_value = mock_template
        
        agent = LATSAgent(llm_configs=self.llm_configs, n_expansions=3)
        
        # Initialize state with a root node
        state = self._create_initial_state()
        updated_state = agent._initialize_search(state)
        state.update(updated_state)
        root_id = state["current_node_id"]
        
        # Run node expansion
        updated_state = agent._expand_node(state)
        state.update(updated_state)
        
        # Check that child nodes were created
        root_node = state["nodes"][root_id]
        self.assertEqual(len(root_node["children"]), 3)
        
        # Check properties of child nodes
        for child_id in root_node["children"]:
            child_node = state["nodes"][child_id]
            self.assertEqual(child_node["parent_id"], root_id)
            self.assertEqual(child_node["depth"], 1)
            self.assertEqual(child_node["visits"], 0)
            self.assertEqual(len(child_node["path"]), 2)
            self.assertEqual(child_node["path"][0], root_id)
            self.assertEqual(state["node_values"][child_id], 0.5)  # Initial neutral value

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_evaluate_paths(self, mock_load_prompt_template, mock_get_llm):
        """Test the _evaluate_paths method."""
        # Setup mocks
        evaluation_llm = MagicMock()
        evaluation_llm.invoke.return_value = AIMessage(content="This is a good path. Score: 0.8")
        
        mock_get_llm.side_effect = lambda role: evaluation_llm if role == "evaluation" else self.mock_llm
        
        mock_template = MagicMock()
        mock_load_prompt_template.return_value = mock_template
        
        agent = LATSAgent(llm_configs=self.llm_configs)
        
        # Initialize state with a root node and expanded children
        state = self._create_initial_state()
        updated_state = agent._initialize_search(state)
        state.update(updated_state)
        root_id = state["current_node_id"]
        
        # Run node expansion
        updated_state = agent._expand_node(state)
        state.update(updated_state)
        
        # Run path evaluation
        updated_state = agent._evaluate_paths(state)
        state.update(updated_state)
        
        # Check that paths were evaluated
        for child_id in state["nodes"][root_id]["children"]:
            self.assertEqual(state["node_values"][child_id], 0.8)
        
        # Check that explored_paths was updated
        self.assertEqual(len(state["explored_paths"]), 3)
        
        # Check that best_path was updated
        self.assertIsNotNone(state["best_path"])
        self.assertEqual(state["best_path_value"], 0.8)

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_backpropagate(self, mock_load_prompt_template, mock_get_llm):
        """Test the _backpropagate method."""
        agent = LATSAgent(llm_configs=self.llm_configs)
        
        # Create a simple tree for testing
        root_id = "root"
        child_id = "child"
        
        state = self._create_initial_state()
        state.update({
            "current_node_id": child_id,
            "nodes": {
                root_id: {
                    "id": root_id,
                    "parent_id": None,
                    "content": "Root",
                    "children": [child_id],
                    "depth": 0,
                    "visits": 0,
                    "path": [root_id],
                    "is_terminal": False
                },
                child_id: {
                    "id": child_id,
                    "parent_id": root_id,
                    "content": "Child",
                    "children": [],
                    "depth": 1,
                    "visits": 0,
                    "path": [root_id, child_id],
                    "is_terminal": False
                }
            },
            "node_values": {
                root_id: 0.5,
                child_id: 0.8
            }
        })
        
        # Run backpropagation
        updated_state = agent._backpropagate(state)
        state.update(updated_state)
        
        # Check that visits were incremented
        self.assertEqual(state["nodes"][child_id]["visits"], 1)
        self.assertEqual(state["nodes"][root_id]["visits"], 1)
        
        # Check that values were updated
        self.assertEqual(state["node_values"][child_id], 0.8)  # Child value unchanged
        self.assertEqual(state["node_values"][root_id], 0.8)  # Root value updated to child's value
        
        # Check that iteration counter was incremented
        self.assertEqual(state["iterations"], 1)

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_select_best_path(self, mock_load_prompt_template, mock_get_llm):
        """Test the _select_best_path method."""
        # Setup mocks
        thinking_llm = MagicMock()
        thinking_llm.invoke.return_value = AIMessage(content="This is the final answer synthesized from the best path.")
        
        mock_get_llm.return_value = thinking_llm
        
        mock_template = MagicMock()
        mock_load_prompt_template.return_value = mock_template
        
        agent = LATSAgent(llm_configs=self.llm_configs)
        
        # Create a state with a best path
        state = self._create_initial_state()
        root_id = "root"
        child_id = "child"
        
        state.update({
            "nodes": {
                root_id: {
                    "id": root_id,
                    "parent_id": None,
                    "content": "Root content",
                    "depth": 0
                },
                child_id: {
                    "id": child_id,
                    "parent_id": root_id,
                    "content": "Child content",
                    "depth": 1
                }
            },
            "best_path": [root_id, child_id],
            "best_path_value": 0.8
        })
        
        # Run select best path
        updated_state = agent._select_best_path(state)
        state.update(updated_state)
        
        # Check that final_answer was set
        self.assertEqual(state["final_answer"], "This is the final answer synthesized from the best path.")
        
        # Verify the correct prompt was used
        mock_load_prompt_template.assert_called_with("NodeSelection")

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_parse_expansion_response(self, mock_load_prompt_template, mock_get_llm):
        """Test the _parse_expansion_response method."""
        agent = LATSAgent(llm_configs=self.llm_configs)
        
        # Test parsing numbered list
        response = "1. First step: do this\n2. Second step: do that\n3. Third step: do something else"
        steps = agent._parse_expansion_response(response)
        
        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[0], "do this")
        self.assertEqual(steps[1], "do that")
        self.assertEqual(steps[2], "do something else")
        
        # Test parsing with 'Step' prefix
        response = "Step 1: do this\nStep 2: do that\nStep 3: do something else"
        steps = agent._parse_expansion_response(response)
        
        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[0], "do this")
        self.assertEqual(steps[1], "do that")
        self.assertEqual(steps[2], "do something else")
        
        # Test parsing with 'Option' prefix
        response = "Option 1: do this\nOption 2: do that\nOption 3: do something else"
        steps = agent._parse_expansion_response(response)
        
        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[0], "do this")
        self.assertEqual(steps[1], "do that")
        self.assertEqual(steps[2], "do something else")
        
        # Test fallback parsing (each line is a step)
        response = "do this\ndo that\ndo something else"
        steps = agent._parse_expansion_response(response)
        
        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[0], "do this")
        self.assertEqual(steps[1], "do that")
        self.assertEqual(steps[2], "do something else")

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_parse_evaluation_response(self, mock_load_prompt_template, mock_get_llm):
        """Test the _parse_evaluation_response method."""
        agent = LATSAgent(llm_configs=self.llm_configs)
        
        # Test parsing 'Score:' format
        response = "This is a good path.\nScore: 0.8"
        value = agent._parse_evaluation_response(response)
        self.assertEqual(value, 0.8)
        
        # Test parsing 'Rating:' format with denominator
        response = "This is a good path.\nRating: 8/10"
        value = agent._parse_evaluation_response(response)
        self.assertEqual(value, 0.8)
        
        # Test parsing 'Rating:' format without denominator
        response = "This is a good path.\nRating: 8"
        value = agent._parse_evaluation_response(response)
        self.assertEqual(value, 0.8)
        
        # Test parsing 'Value:' format
        response = "This is a good path.\nValue: 0.8"
        value = agent._parse_evaluation_response(response)
        self.assertEqual(value, 0.8)
        
        # Test parsing 'Evaluation:' format
        response = "This is a good path.\nEvaluation: 0.8"
        value = agent._parse_evaluation_response(response)
        self.assertEqual(value, 0.8)
        
        # Test parsing 'Assessment:' format
        response = "This is a good path.\nAssessment: 0.8"
        value = agent._parse_evaluation_response(response)
        self.assertEqual(value, 0.8)
        
        # Test parsing just a number
        response = "0.8"
        value = agent._parse_evaluation_response(response)
        self.assertEqual(value, 0.8)
        
        # Test normalization of scores > 1
        response = "Score: 8"
        value = agent._parse_evaluation_response(response)
        self.assertEqual(value, 0.8)
        
        # Test default when parsing fails
        response = "This is a good path without a score."
        value = agent._parse_evaluation_response(response)
        self.assertEqual(value, 0.5)

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_calculate_ucb(self, mock_load_prompt_template, mock_get_llm):
        """Test the UCB calculation."""
        agent = LATSAgent(llm_configs=self.llm_configs)
        
        # Create a simple state for testing
        state = self._create_initial_state()
        state.update({
            "node_values": {
                "node1": 0.7,
                "node2": 0.5
            },
            "nodes": {
                "node1": {
                    "visits": 3
                },
                "node2": {
                    "visits": 1
                }
            }
        })
        
        # Calculate UCB for node1 with parent node2
        ucb = agent._calculate_ucb("node1", "node2", state)
        
        # Expected: 0.7 + 1.0 * sqrt(ln(2)/4) ≈ 0.7 + 0.3466
        expected = 0.7 + 1.0 * (0.693147 / 4) ** 0.5
        self.assertAlmostEqual(ucb, expected, places=5)
        
        # Calculate UCB for node2 with parent node1
        ucb = agent._calculate_ucb("node2", "node1", state)
        
        # Expected: 0.5 + 1.0 * sqrt(ln(4)/2) ≈ 0.5 + 0.9803
        expected = 0.5 + 1.0 * (1.386294 / 2) ** 0.5
        self.assertAlmostEqual(ucb, expected, places=5)

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_integration_full_run(self, mock_load_prompt_template, mock_get_llm):
        """Test a complete run of the LATS agent."""
        # Setup mocks for different roles
        thinking_llm = MagicMock()
        thinking_responses = [
            AIMessage(content="1. First step: Analyze requirements\n2. Second step: Design solution\n3. Third step: Implement prototype"),
            AIMessage(content="Final answer: This is a comprehensive solution.")
        ]
        thinking_llm.invoke.side_effect = thinking_responses
        
        evaluation_llm = MagicMock()
        evaluation_llm.invoke.return_value = AIMessage(content="This is a promising path. Score: 0.8")
        
        # Return different LLMs based on role
        mock_get_llm.side_effect = lambda role: evaluation_llm if role == "evaluation" else thinking_llm
        
        # Mock prompt templates
        mock_template = MagicMock()
        mock_load_prompt_template.return_value = mock_template
        
        # Create agent with small limits for testing
        agent = LATSAgent(
            llm_configs=self.llm_configs,
            max_iterations=2,
            max_depth=2,
            n_expansions=3
        )
        
        # Create a mock graph that returns a final answer
        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {"final_answer": "Final answer: This is a comprehensive solution."}
        agent.graph = mock_graph
        
        # Run the agent
        result = agent.run("Test problem")
        
        # Check that a result was returned
        self.assertEqual(result, "Final answer: This is a comprehensive solution.")

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_memory_integration(self, mock_load_prompt_template, mock_get_llm):
        """Test memory integration in LATSAgent."""
        # Configure mocks
        thinking_llm = MagicMock()
        thinking_llm.invoke.return_value = AIMessage(content="1. First option: This is step one\n2. Second option: This is step two\n3. Third option: This is step three")
        
        evaluation_llm = MagicMock()
        evaluation_llm.invoke.return_value = AIMessage(content="This is a good path. Score: 0.8")
        
        selection_llm = MagicMock()
        selection_llm.invoke.return_value = AIMessage(content="Final answer: This is a comprehensive solution.")
        
        # Return different LLMs based on role
        mock_get_llm.side_effect = lambda role: evaluation_llm if role == "evaluation" else thinking_llm
        
        # Mock prompt templates
        mock_template = MagicMock()
        mock_load_prompt_template.return_value = mock_template
        
        # Create mock memory system
        mock_memory = MagicMock()
        mock_memory.memories = {"semantic": MagicMock(), "episodic": MagicMock()}
        
        # Mock memory retrieval and saving methods
        mock_retrieve_memories = MagicMock(return_value={
            "semantic": [{"fact": "This is a semantic memory"}],
            "episodic": [{"event": "This is an episodic memory"}]
        })
        
        mock_save_memory = MagicMock()
        
        # Create agent with memory
        agent = LATSAgent(
            llm_configs=self.llm_configs,
            memory=mock_memory,
            memory_config={"semantic": True, "episodic": True}
        )
        
        # Replace methods with mocks
        agent.sync_retrieve_memories = mock_retrieve_memories
        agent.sync_save_memory = mock_save_memory
        
        # Create initial state with a root node
        state = self._create_initial_state()
        updated_state = agent._initialize_search(state)
        state.update(updated_state)
        root_id = state["current_node_id"]
        
        # Test memory retrieval in node expansion
        result = agent._expand_node(state)
        mock_retrieve_memories.assert_called()
        
        # Update state with expansion results
        state.update(result)
        
        # Test memory in path evaluation
        mock_retrieve_memories.reset_mock()
        result = agent._evaluate_paths(state)
        mock_retrieve_memories.assert_called()
        
        # Update state with evaluation results
        state.update(result)
        
        # Update state to have a best path
        child_id = state["nodes"][root_id]["children"][0]
        state["best_path"] = [root_id, child_id]
        state["best_path_value"] = 0.8
        
        # Test memory in best path selection
        mock_retrieve_memories.reset_mock()
        mock_save_memory.reset_mock()
        
        result = agent._select_best_path(state)
        
        # Verify memory was retrieved and saved
        mock_retrieve_memories.assert_called()
        mock_save_memory.assert_called()
        
        # Verify both types of memory were saved
        calls = mock_save_memory.call_args_list
        saved_to_episodic = False
        saved_to_semantic = False
        
        for call in calls:
            args, kwargs = call
            if kwargs.get("memory_type") == "episodic":
                saved_to_episodic = True
            if kwargs.get("memory_type") == "semantic":
                saved_to_semantic = True
        
        self.assertTrue(saved_to_episodic, "Failed to save to episodic memory")
        self.assertTrue(saved_to_semantic, "Failed to save to semantic memory")
    
    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_tool_provider_integration(self, mock_load_prompt_template, mock_get_llm):
        """Test tool provider integration in LATSAgent."""
        # Configure mocks
        thinking_llm = MagicMock()
        thinking_llm.invoke.return_value = AIMessage(content="1. First option: Use tool to search\n2. Second option: This is step two\n3. Third option: This is step three")
        
        evaluation_llm = MagicMock()
        evaluation_llm.invoke.return_value = AIMessage(content="This is a good path. Score: 0.8")
        
        # Return different LLMs based on role
        mock_get_llm.side_effect = lambda role: evaluation_llm if role == "evaluation" else thinking_llm
        
        # Mock prompt templates
        mock_template = MagicMock()
        mock_load_prompt_template.return_value = mock_template
        
        # Create mock tool provider
        mock_tool_provider = MagicMock()
        
        # Configure the tool provider to return mock tools
        mock_tool_provider.list_tools.return_value = [
            {"name": "search", "description": "Search for information", "parameters": {}}
        ]
        
        # Create agent with tool provider
        agent = LATSAgent(
            llm_configs=self.llm_configs,
            tool_provider=mock_tool_provider
        )
        
        # Create initial state with a root node
        state = self._create_initial_state()
        updated_state = agent._initialize_search(state)
        state.update(updated_state)
        
        # Test tool provider in node expansion
        result = agent._expand_node(state)
        
        # Verify that tool provider's list_tools was called
        mock_tool_provider.list_tools.assert_called()
        
        # Verify that the prompt template was called with tools_context
        prompt_calls = mock_template.format.call_args_list
        tools_context_included = False
        
        for call in prompt_calls:
            args, kwargs = call
            if "tools_context" in kwargs and kwargs["tools_context"]:
                tools_context_included = True
                break
        
        self.assertTrue(tools_context_included, "tools_context not included in prompt")


if __name__ == "__main__":
    unittest.main() 