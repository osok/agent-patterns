"""Tests for the STORM (Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking) agent pattern."""

import os
import unittest
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage

from agent_patterns.patterns.storm_agent import STORMAgent, STORMState


class TestSTORMAgent(unittest.TestCase):
    """Test suite for the STORM agent pattern."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock LLM configs with all necessary roles
        self.llm_configs = {
            "outline_generator": {"provider": "mock", "model": "mock-model"},
            "perspective_identifier": {"provider": "mock", "model": "mock-model"},
            "expert": {"provider": "mock", "model": "mock-model"},
            "researcher": {"provider": "mock", "model": "mock-model"},
            "writer": {"provider": "mock", "model": "mock-model"},
            "editor": {"provider": "mock", "model": "mock-model"}
        }
        
        # Create mock responses for different LLM roles
        self.mock_outline_response = AIMessage(content=(
            "# Introduction\nThis section introduces the topic.\n\n"
            "# Background\nThis section provides context.\n\n"
            "# Main Points\nThis section covers key aspects.\n\n"
            "# Conclusions\nThis section summarizes findings."
        ))
        
        self.mock_perspectives_response = AIMessage(content=(
            "1. Historical perspective\n"
            "2. Scientific perspective\n"
            "3. Social impact perspective"
        ))
        
        self.mock_expert_response = AIMessage(content=(
            "From the scientific perspective, there are several key points to consider:\n\n"
            "1. The underlying mechanisms are well-documented [1] Smith et al. (2020).\n"
            "2. Recent studies have shown a correlation between X and Y.\n"
            "3. The 'standard model' is currently being challenged by new findings."
        ))
        
        self.mock_researcher_response = AIMessage(content=(
            "Given what you've explained, I'm curious about how these findings apply to real-world scenarios. "
            "Could you elaborate on the practical applications of this research?"
        ))
        
        self.mock_writer_response = AIMessage(content=(
            "This section examines the scientific perspective on the topic. According to Smith et al. (2020), "
            "the underlying mechanisms are well-documented. Recent studies have revealed correlations between "
            "X and Y, suggesting causal relationships that warrant further investigation. Interestingly, the "
            "'standard model' that has guided research for decades is now being challenged by new findings, "
            "creating opportunities for paradigm shifts in our understanding of the subject."
        ))
        
        self.mock_editor_response = AIMessage(content=(
            "# Title: Comprehensive Analysis of the Topic\n\n"
            "## Introduction\nThis section introduces the topic.\n\n"
            "## Background\nThis section provides context.\n\n"
            "## Main Points\nThis section covers key aspects.\n\n"
            "## Conclusions\nThis section summarizes findings.\n\n"
            "## References\n[1] Smith et al. (2020). Key findings about the topic. Journal of Research."
        ))
        
        # Mock search tool
        self.mock_search_tool = MagicMock()
        self.mock_search_tool.run.return_value = "Relevant search results about the topic."
        
        # Path to test prompts
        self.test_prompts_dir = os.path.join(os.path.dirname(__file__), "test_prompts")

    def _create_initial_state(self):
        """Create a basic initial state for testing."""
        return {
            "input_topic": "Test topic",
            "outline": [],
            "perspectives": [],
            "references": {},
            "conversations": [],
            "sections": {},
            "final_article": None,
            "current_step": "generate_initial_outline"
        }

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_initialization(self, mock_load_prompt_template, mock_get_llm):
        """Test agent initialization with all required configurations."""
        agent = STORMAgent(llm_configs=self.llm_configs)
        
        # Check that the graph was compiled
        self.assertIsNotNone(agent.graph)
        
        # Check default parameters
        self.assertEqual(agent.num_perspectives, 3)
        self.assertEqual(agent.max_conversation_turns, 5)
        self.assertIsNone(agent.search_tool)

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_initialization_with_search_tool(self, mock_load_prompt_template, mock_get_llm):
        """Test agent initialization with a search tool."""
        agent = STORMAgent(
            llm_configs=self.llm_configs, 
            search_tool=self.mock_search_tool
        )
        
        # Verify search tool was set
        self.assertEqual(agent.search_tool, self.mock_search_tool)

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_initialization_with_missing_roles(self, mock_load_prompt_template, mock_get_llm):
        """Test that initialization fails when required roles are missing and no default is provided."""
        # Create incomplete configs
        incomplete_configs = {
            "outline_generator": {"provider": "mock", "model": "mock-model"}
            # Missing other required roles
        }
        
        # Check that proper error is raised
        with self.assertRaises(ValueError):
            STORMAgent(llm_configs=incomplete_configs)

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_initialization_with_default_role(self, mock_load_prompt_template, mock_get_llm):
        """Test that initialization succeeds with a default role when specific roles are missing."""
        # Create configs with only default
        default_configs = {
            "default": {"provider": "mock", "model": "mock-model"}
        }
        
        # Should not raise error
        agent = STORMAgent(llm_configs=default_configs)
        self.assertIsNotNone(agent)

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_generate_initial_outline(self, mock_load_prompt_template, mock_get_llm):
        """Test the _generate_initial_outline method."""
        # Setup mocks
        mock_get_llm.return_value = MagicMock()
        mock_get_llm.return_value.invoke.return_value = self.mock_outline_response
        
        mock_template = MagicMock()
        mock_load_prompt_template.return_value = mock_template
        
        # Create agent
        agent = STORMAgent(llm_configs=self.llm_configs)
        
        # Initialize state
        state = self._create_initial_state()
        
        # Run outline generation
        updated_state = agent._generate_initial_outline(state)
        
        # Verify results
        self.assertEqual(updated_state["current_step"], "identify_perspectives")
        self.assertGreater(len(updated_state["outline"]), 0)
        
        # Check that outline has expected structure
        self.assertEqual(len(updated_state["outline"]), 4)  # 4 sections
        self.assertEqual(updated_state["outline"][0]["title"], "Introduction")
        self.assertEqual(updated_state["outline"][1]["title"], "Background")
        self.assertEqual(updated_state["outline"][2]["title"], "Main Points")
        self.assertEqual(updated_state["outline"][3]["title"], "Conclusions")

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_identify_perspectives(self, mock_load_prompt_template, mock_get_llm):
        """Test the _identify_perspectives method."""
        # Setup mocks
        mock_get_llm.return_value = MagicMock()
        mock_get_llm.return_value.invoke.return_value = self.mock_perspectives_response
        
        mock_template = MagicMock()
        mock_load_prompt_template.return_value = mock_template
        
        # Create agent
        agent = STORMAgent(llm_configs=self.llm_configs)
        
        # Initialize state with an outline
        state = self._create_initial_state()
        state["outline"] = [
            {
                "id": "1",
                "title": "Introduction",
                "description": "This is an introduction",
                "subsections": []
            }
        ]
        
        # Run perspective identification
        updated_state = agent._identify_perspectives(state)
        
        # Verify results
        self.assertEqual(updated_state["current_step"], "simulate_conversations")
        self.assertEqual(len(updated_state["perspectives"]), 3)
        self.assertEqual(updated_state["perspectives"][0], "Historical perspective")
        self.assertEqual(updated_state["perspectives"][1], "Scientific perspective")
        self.assertEqual(updated_state["perspectives"][2], "Social impact perspective")

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_simulate_conversations(self, mock_load_prompt_template, mock_get_llm):
        """Test the _simulate_conversations method."""
        # Setup mocks with different responses for expert and researcher
        def mock_get_llm_side_effect(role):
            mock = MagicMock()
            if role == "expert":
                mock.invoke.return_value = self.mock_expert_response
            elif role == "researcher":
                mock.invoke.return_value = self.mock_researcher_response
            return mock
        
        mock_get_llm.side_effect = mock_get_llm_side_effect
        
        mock_template = MagicMock()
        mock_load_prompt_template.return_value = mock_template
        
        # Create agent with a single conversation turn for testing
        agent = STORMAgent(
            llm_configs=self.llm_configs,
            search_tool=self.mock_search_tool,
            max_conversation_turns=1
        )
        
        # Initialize state with an outline and perspectives
        state = self._create_initial_state()
        state["outline"] = [
            {
                "id": "1",
                "title": "Scientific Findings",
                "description": "Overview of scientific research",
                "subsections": []
            }
        ]
        state["perspectives"] = ["Scientific perspective"]
        
        # Run conversation simulation
        updated_state = agent._simulate_conversations(state)
        
        # Verify results
        self.assertEqual(updated_state["current_step"], "refine_outline")
        self.assertEqual(len(updated_state["conversations"]), 1)
        self.assertEqual(updated_state["conversations"][0]["perspective"], "Scientific perspective")
        
        # Check messages
        self.assertEqual(len(updated_state["conversations"][0]["messages"]), 2)
        self.assertEqual(updated_state["conversations"][0]["messages"][0]["role"], "researcher")
        self.assertEqual(updated_state["conversations"][0]["messages"][1]["role"], "expert")
        
        # Check references
        self.assertTrue(len(updated_state["conversations"][0]["references"]) > 0)
        
        # Verify references were linked to outline sections
        self.assertTrue("1" in updated_state["references"])

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_refine_outline(self, mock_load_prompt_template, mock_get_llm):
        """Test the _refine_outline method."""
        # Setup mocks
        mock_get_llm.return_value = MagicMock()
        mock_get_llm.return_value.invoke.return_value = self.mock_outline_response
        
        mock_template = MagicMock()
        mock_load_prompt_template.return_value = mock_template
        
        # Create agent
        agent = STORMAgent(llm_configs=self.llm_configs)
        
        # Initialize state with outline, perspectives, conversations, and references
        state = self._create_initial_state()
        state["outline"] = [
            {
                "id": "1",
                "title": "Original Section",
                "description": "Original description",
                "subsections": []
            }
        ]
        state["perspectives"] = ["Scientific perspective"]
        state["conversations"] = [{
            "perspective": "Scientific perspective",
            "messages": [
                {"role": "researcher", "content": "Question?"},
                {"role": "expert", "content": "Answer."}
            ],
            "references": [{"title": "Reference", "content": "Content"}]
        }]
        state["references"] = {
            "1": [{"title": "Reference", "content": "Content"}]
        }
        
        # Run outline refinement
        updated_state = agent._refine_outline(state)
        
        # Verify results
        self.assertEqual(updated_state["current_step"], "write_sections")
        self.assertEqual(len(updated_state["outline"]), 4)  # New outline has 4 sections
        
        # Verify each section has an ID
        for section in updated_state["outline"]:
            self.assertIn("id", section)

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_write_sections(self, mock_load_prompt_template, mock_get_llm):
        """Test the _write_sections method."""
        # Setup mocks
        mock_get_llm.return_value = MagicMock()
        mock_get_llm.return_value.invoke.return_value = self.mock_writer_response
        
        mock_template = MagicMock()
        mock_load_prompt_template.return_value = mock_template
        
        # Create agent
        agent = STORMAgent(llm_configs=self.llm_configs)
        
        # Initialize state with outline and references
        state = self._create_initial_state()
        state["outline"] = [
            {
                "id": "1",
                "title": "Section One",
                "description": "Description of section one",
                "subsections": []
            },
            {
                "id": "2",
                "title": "Section Two",
                "description": "Description of section two",
                "subsections": []
            }
        ]
        state["references"] = {
            "1": [{"title": "Reference 1", "content": "Content 1"}],
            "2": [{"title": "Reference 2", "content": "Content 2"}]
        }
        
        # Run section writing
        updated_state = agent._write_sections(state)
        
        # Verify results
        self.assertEqual(updated_state["current_step"], "finalize_article")
        self.assertEqual(len(updated_state["sections"]), 2)
        self.assertIn("1", updated_state["sections"])
        self.assertIn("2", updated_state["sections"])
        
        # Check content of sections
        self.assertEqual(updated_state["sections"]["1"], self.mock_writer_response.content)
        self.assertEqual(updated_state["sections"]["2"], self.mock_writer_response.content)

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_finalize_article(self, mock_load_prompt_template, mock_get_llm):
        """Test the _finalize_article method."""
        # Setup mocks
        mock_get_llm.return_value = MagicMock()
        mock_get_llm.return_value.invoke.return_value = self.mock_editor_response
        
        mock_template = MagicMock()
        mock_load_prompt_template.return_value = mock_template
        
        # Create agent
        agent = STORMAgent(llm_configs=self.llm_configs)
        
        # Initialize state with outline, sections, and references
        state = self._create_initial_state()
        state["outline"] = [
            {
                "id": "1",
                "title": "Section One",
                "description": "Description of section one",
                "subsections": []
            },
            {
                "id": "2",
                "title": "Section Two",
                "description": "Description of section two",
                "subsections": []
            }
        ]
        state["sections"] = {
            "1": "Content for section one.",
            "2": "Content for section two."
        }
        state["references"] = {
            "1": [{"title": "Reference 1", "content": "Content 1", "source": "Source 1"}],
            "2": [{"title": "Reference 2", "content": "Content 2", "source": "Source 2"}]
        }
        
        # Run article finalization
        updated_state = agent._finalize_article(state)
        
        # Verify results
        self.assertEqual(updated_state["current_step"], "finished")
        self.assertEqual(updated_state["final_article"], self.mock_editor_response.content)

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_parse_outline(self, mock_load_prompt_template, mock_get_llm):
        """Test the _parse_outline method."""
        # Create agent
        agent = STORMAgent(llm_configs=self.llm_configs)
        
        # Test parsing a simple outline
        outline_text = (
            "# Introduction\nThis is an introduction.\n\n"
            "# Methods\nThese are the methods.\n\n"
            "### Subsection 1\nThis is a subsection.\n\n"
            "# Results\nThese are the results."
        )
        
        outline = agent._parse_outline(outline_text)
        
        # Print the outline for debugging
        import json
        print("\nOUTLINE TEST DEBUG:")
        print(json.dumps(outline, indent=2))
        
        # Verify results
        self.assertEqual(len(outline), 3)  # Three main sections
        self.assertEqual(outline[0]["title"], "Introduction")
        self.assertEqual(outline[0]["description"], "This is an introduction.")
        self.assertEqual(outline[1]["title"], "Methods")
        # Debug the actual description
        print(f"\nExpected: 'These are the methods.'")
        print(f"Actual  : '{outline[1]['description']}'")
        self.assertEqual(outline[1]["description"], "These are the methods.")
        self.assertEqual(len(outline[1]["subsections"]), 1)  # One subsection
        self.assertEqual(outline[1]["subsections"][0]["title"], "Subsection 1")

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_parse_perspectives(self, mock_load_prompt_template, mock_get_llm):
        """Test the _parse_perspectives method."""
        # Create agent
        agent = STORMAgent(llm_configs=self.llm_configs)
        
        # Test parsing different perspective formats
        
        # Numbered list
        numbered_list = (
            "1. Historical perspective\n"
            "2. Scientific perspective\n"
            "3. Social impact perspective"
        )
        perspectives = agent._parse_perspectives(numbered_list)
        self.assertEqual(len(perspectives), 3)
        self.assertEqual(perspectives[0], "Historical perspective")
        
        # Bulleted list
        bulleted_list = (
            "* Historical perspective\n"
            "* Scientific perspective\n"
            "* Social impact perspective"
        )
        perspectives = agent._parse_perspectives(bulleted_list)
        self.assertEqual(len(perspectives), 3)
        self.assertEqual(perspectives[0], "Historical perspective")
        
        # Simple lines
        simple_lines = (
            "Historical perspective\n"
            "Scientific perspective\n"
            "Social impact perspective"
        )
        perspectives = agent._parse_perspectives(simple_lines)
        self.assertEqual(len(perspectives), 3)
        self.assertEqual(perspectives[0], "Historical perspective")

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_extract_references(self, mock_load_prompt_template, mock_get_llm):
        """Test the _extract_references method."""
        # Create agent
        agent = STORMAgent(llm_configs=self.llm_configs)
        
        # Test extracting references
        text_with_refs = (
            "This is a point with a reference [1] Smith et al. (2020).\n"
            "Here's another reference [2] Johnson (2018)."
        )
        
        references = agent._extract_references(text_with_refs)
        
        # Verify results
        self.assertEqual(len(references), 2)
        self.assertEqual(references[0]["id"], "1")
        self.assertEqual(references[0]["content"], "Smith et al. (2020).")
        self.assertEqual(references[1]["id"], "2")
        self.assertEqual(references[1]["content"], "Johnson (2018).")
        
        # Test extracting quotes when no numbered references
        text_with_quotes = (
            'This contains a quote "This is an important finding" that should be referenced.\n'
            'And another quote "Secondary observation" is here.'
        )
        
        references = agent._extract_references(text_with_quotes)
        
        # Verify results
        self.assertEqual(len(references), 2)
        self.assertEqual(references[0]["content"], "This is an important finding")
        self.assertEqual(references[1]["content"], "Secondary observation")

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.patterns.storm_agent.STORMAgent._generate_initial_outline")
    @patch("agent_patterns.patterns.storm_agent.STORMAgent._identify_perspectives")
    @patch("agent_patterns.patterns.storm_agent.STORMAgent._simulate_conversations")
    @patch("agent_patterns.patterns.storm_agent.STORMAgent._refine_outline")
    @patch("agent_patterns.patterns.storm_agent.STORMAgent._write_sections")
    @patch("agent_patterns.patterns.storm_agent.STORMAgent._finalize_article")
    def test_run_integration(self, mock_finalize, mock_write, mock_refine, mock_simulate, 
                            mock_identify, mock_generate, mock_get_llm):
        """Test the full run method with mocked component functions."""
        # Setup return values for each step
        mock_generate.return_value = {"outline": [{"id": "1", "title": "Section"}], "current_step": "identify_perspectives"}
        mock_identify.return_value = {"perspectives": ["Perspective 1"], "current_step": "simulate_conversations"}
        mock_simulate.return_value = {"conversations": [{}], "references": {"1": []}, "current_step": "refine_outline"}
        mock_refine.return_value = {"outline": [{"id": "1", "title": "Refined Section"}], "current_step": "write_sections"}
        mock_write.return_value = {"sections": {"1": "Content"}, "current_step": "finalize_article"}
        mock_finalize.return_value = {"final_article": "Final article content", "current_step": "finished"}
        
        # Create agent
        agent = STORMAgent(llm_configs=self.llm_configs)
        
        # Mock graph invoke
        agent.graph.invoke = MagicMock()
        agent.graph.invoke.return_value = {
            "input_topic": "Test topic",
            "outline": [{"id": "1", "title": "Refined Section"}],
            "perspectives": ["Perspective 1"],
            "references": {"1": []},
            "conversations": [{}],
            "sections": {"1": "Content"},
            "final_article": "Final article content",
            "current_step": "finished"
        }
        
        # Run the agent
        result = agent.run("Test topic")
        
        # Verify the result structure
        self.assertIn("article", result)
        self.assertEqual(result["article"], "Final article content")
        self.assertIn("outline", result)
        self.assertIn("references", result)
        self.assertIn("perspectives", result)

    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_memory_integration(self, mock_load_prompt_template, mock_get_llm):
        """Test memory integration in the agent."""
        # Create mock memory components
        mock_memory = MagicMock()
        mock_memory.memories = {"semantic": MagicMock(), "episodic": MagicMock()}
        
        # Configure mock memory retrieval
        mock_retrieve_memories = MagicMock(return_value={
            "semantic": [{"fact": "Previous article on similar topic covered XYZ"}],
            "episodic": [{"event": "Researched this topic last month"}]
        })
        
        mock_save_memory = MagicMock()
        
        # Create a mock template
        mock_template = MagicMock()
        mock_load_prompt_template.return_value = mock_template
        
        # Create mock LLM with preset response
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = self.mock_outline_response
        mock_get_llm.return_value = mock_llm
        
        # Create agent with memory
        agent = STORMAgent(
            llm_configs=self.llm_configs,
            memory=mock_memory
        )
        
        # Replace memory methods with mocks
        agent.sync_retrieve_memories = mock_retrieve_memories
        agent.sync_save_memory = mock_save_memory
        
        # Test initial outline generation with memory
        state = self._create_initial_state()
        
        # Run the outline generation method
        agent._generate_initial_outline(state)
        
        # Verify memory was retrieved
        mock_retrieve_memories.assert_called_with(state["input_topic"])
        
        # Verify prompt was formatted with memory context
        mock_template.format.assert_called_once()
        call_args = mock_template.format.call_args[1]
        self.assertIn("memory_context", call_args)
        
        # Test finalization with memory saving
        finalize_state = self._create_initial_state()
        finalize_state["outline"] = [{"id": "1", "title": "Test Section"}]
        finalize_state["sections"] = {"1": "Test content"}
        finalize_state["references"] = {"1": [{"title": "Ref", "source": "Source"}]}
        finalize_state["perspectives"] = ["Test perspective"]
        
        # Clear the mock counters
        mock_retrieve_memories.reset_mock()
        mock_save_memory.reset_mock()
        
        # Run the finalization method
        agent._finalize_article(finalize_state)
        
        # Verify memory was saved
        self.assertEqual(mock_save_memory.call_count, 2)  # Once for episodic, once for semantic
        
        # Check that the correct memory types were used
        memory_calls = mock_save_memory.call_args_list
        memory_types = [call[1]["memory_type"] for call in memory_calls]
        self.assertIn("episodic", memory_types)
        self.assertIn("semantic", memory_types)
    
    @patch("agent_patterns.core.base_agent.BaseAgent._get_llm")
    @patch("agent_patterns.core.base_agent.BaseAgent._load_prompt_template")
    def test_tool_provider_integration(self, mock_load_prompt_template, mock_get_llm):
        """Test tool provider integration in the agent."""
        # Create mock tool provider
        mock_tool_provider = MagicMock()
        
        # Configure the tool provider to return mock tools
        mock_tool_provider.list_tools.return_value = [
            {
                "name": "search",
                "description": "Search for information",
                "parameters": {"query": "string"}
            }
        ]
        
        # Mock the tool execution
        mock_tool_provider.execute_tool.return_value = "Tool search result"
        
        # Create mock template
        mock_template = MagicMock()
        mock_load_prompt_template.return_value = mock_template
        
        # Create mock LLM with tool request in response
        mock_expert_llm = MagicMock()
        mock_expert_llm.invoke.return_value = AIMessage(content="Let me search for that.\n\nUSE TOOL: search(test query)\n\nBased on what I can find...")
        
        # Create mock researcher LLM
        mock_researcher_llm = MagicMock()
        mock_researcher_llm.invoke.return_value = AIMessage(content="Next question")
        
        # Setup the mock_get_llm to return different LLMs based on role
        def get_llm_side_effect(role):
            if role == "expert":
                return mock_expert_llm
            else:
                return mock_researcher_llm
        
        mock_get_llm.side_effect = get_llm_side_effect
        
        # Create agent with tool provider
        agent = STORMAgent(
            llm_configs=self.llm_configs,
            tool_provider=mock_tool_provider,
            max_conversation_turns=1  # Limit to one turn for testing
        )
        
        # Test conversation simulation with tool use
        state = self._create_initial_state()
        state["perspectives"] = ["Test perspective"]
        state["outline"] = [{"id": "1", "title": "Test Section"}]
        
        # Run the conversation simulation method
        result = agent._simulate_conversations(state)
        
        # Verify tool provider was used to list tools
        mock_tool_provider.list_tools.assert_called()
        
        # Verify tool was executed
        mock_tool_provider.execute_tool.assert_called_with("search", {"query": "test query"})
        
        # Verify the conversation includes the tool result
        self.assertIn("TOOL RESULT:", result["conversations"][0]["messages"][1]["content"])
    
    def test_process_tool_requests(self):
        """Test the _process_tool_requests method."""
        # Create mock tool provider
        mock_tool_provider = MagicMock()
        mock_tool_provider.execute_tool.return_value = "Tool execution result"
        
        # Create agent with tool provider
        agent = STORMAgent(
            llm_configs=self.llm_configs,
            tool_provider=mock_tool_provider
        )
        
        # Test text with a tool request
        text = "Let me look that up.\n\nUSE TOOL: search(test query)\n\nBased on these results..."
        
        result = agent._process_tool_requests(text)
        
        # Verify the tool was executed
        mock_tool_provider.execute_tool.assert_called_with("search", {"query": "test query"})
        
        # Verify the result contains both original text and tool result
        self.assertIn("Let me look that up.", result)
        self.assertIn("USE TOOL: search(test query)", result)
        self.assertIn("TOOL RESULT:", result)
        self.assertIn("Tool execution result", result)
        self.assertIn("Based on these results...", result)
        
        # Test with invalid tool request format
        text_with_invalid_request = "USE TOOL: invalid request format"
        
        result = agent._process_tool_requests(text_with_invalid_request)
        
        # Verify error message is included
        self.assertIn("ERROR: Invalid tool request format", result)
        
        # Test with tool execution error
        mock_tool_provider.execute_tool.side_effect = Exception("Tool error")
        
        text = "USE TOOL: search(test query)"
        
        result = agent._process_tool_requests(text)
        
        # Verify error message is included
        self.assertIn("ERROR: Failed to execute tool search", result)


if __name__ == '__main__':
    unittest.main() 