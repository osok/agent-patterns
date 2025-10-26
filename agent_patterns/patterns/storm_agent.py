"""STORM (Synthesis of Topic Outlines through Retrieval and Multi-perspective) Pattern.

The STORM pattern creates comprehensive, multi-perspective articles or reports by:
1. Generating a topic outline
2. Creating questions from multiple viewpoints/personas
3. Retrieving information for each question
4. Synthesizing all data into a structured document

Reference: https://arxiv.org/abs/2402.14207
"""

from typing import Any, Callable, Dict, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent_patterns.core.base_agent import BaseAgent


# Default perspectives for multi-viewpoint questioning
DEFAULT_PERSPECTIVES = [
    {"name": "expert", "description": "Technical expert with deep domain knowledge"},
    {"name": "practitioner", "description": "Professional practitioner applying the concepts"},
    {"name": "researcher", "description": "Academic researcher studying the topic"},
    {"name": "critic", "description": "Critical analyst examining limitations and challenges"}
]


class STORMAgent(BaseAgent):
    """STORM agent for creating comprehensive multi-perspective reports.

    This pattern systematically generates structured, well-researched content by
    exploring a topic from multiple viewpoints, retrieving relevant information,
    and synthesizing it into a cohesive document.

    Workflow:
        1. Generate Outline: Create hierarchical structure
        2. Generate Perspectives: Identify relevant viewpoints
        3. Generate Questions: Create questions from each perspective
        4. Execute Search: Retrieve information for all questions
        5. Synthesize Sections: Combine information for each section
        6. Compile Report: Assemble final document

    Args:
        llm_configs: Dictionary mapping role names to LLM configuration
        retrieval_tools: Dictionary mapping tool names to callable functions
        perspectives: Custom perspective definitions (optional)
        prompt_dir: Directory containing prompt templates (default: "prompts")

    Example:
        >>> def search_tool(query: str) -> str:
        ...     return f"Research about: {query}"
        >>>
        >>> agent = STORMAgent(
        ...     llm_configs={
        ...         "thinking": {"provider": "openai", "model": "gpt-4"},
        ...         "documentation": {"provider": "openai", "model": "gpt-4"}
        ...     },
        ...     retrieval_tools={"search": search_tool}
        ... )
        >>> report = agent.run("Artificial Intelligence in Healthcare")
    """

    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        retrieval_tools: Optional[Dict[str, Callable]] = None,
        perspectives: Optional[List[Dict[str, str]]] = None,
        prompt_dir: str = "prompts",
        custom_instructions: Optional[str] = None,
        prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
    ):
        """Initialize the STORM agent.

        Args:
            llm_configs: Dictionary mapping role names to LLM configuration
            retrieval_tools: Dictionary mapping tool names to retrieval functions
            perspectives: Custom perspective definitions
            prompt_dir: Directory containing prompt templates
            custom_instructions: Custom instructions appended to all system prompts
            prompt_overrides: Dictionary mapping step names to prompt overrides
        """
        self.retrieval_tools = retrieval_tools or {}
        self.perspectives = perspectives or DEFAULT_PERSPECTIVES
        super().__init__(
            llm_configs=llm_configs,
            prompt_dir=prompt_dir,
            custom_instructions=custom_instructions,
            prompt_overrides=prompt_overrides
        )

    def build_graph(self) -> None:
        """Build the LangGraph StateGraph for the STORM pattern.

        Creates a graph with the following nodes:
            - generate_outline: Creates document structure
            - generate_perspectives: Identifies relevant viewpoints
            - generate_questions: Creates questions from each perspective
            - dispatch_queries: Prepares search queries
            - execute_search: Retrieves information
            - collect_results: Organizes retrieved data
            - synthesize_sections: Creates content for each section
            - compile_report: Assembles final document
        """
        workflow = StateGraph(dict)

        # Stage 1: Planning nodes
        workflow.add_node("generate_outline", self._generate_outline)
        workflow.add_node("generate_perspectives", self._generate_perspectives)
        workflow.add_node("generate_questions", self._generate_questions)

        # Stage 2: Retrieval nodes
        workflow.add_node("dispatch_queries", self._dispatch_queries)
        workflow.add_node("execute_search", self._execute_search)
        workflow.add_node("collect_results", self._collect_results)

        # Stage 3: Synthesis nodes
        workflow.add_node("synthesize_sections", self._synthesize_sections)
        workflow.add_node("compile_report", self._compile_report)

        # Set entry point
        workflow.set_entry_point("generate_outline")

        # Stage 1 edges
        workflow.add_edge("generate_outline", "generate_perspectives")
        workflow.add_edge("generate_perspectives", "generate_questions")

        # Stage 2 edges
        workflow.add_edge("generate_questions", "dispatch_queries")
        workflow.add_edge("dispatch_queries", "execute_search")
        workflow.add_edge("execute_search", "collect_results")

        # Stage 3 edges
        workflow.add_edge("collect_results", "synthesize_sections")
        workflow.add_edge("synthesize_sections", "compile_report")
        workflow.add_edge("compile_report", "__end__")

        self.graph: CompiledStateGraph = workflow.compile()

    def run(self, input_data: Any) -> Any:
        """Execute the STORM workflow to create a comprehensive report.

        Args:
            input_data: The topic for the report

        Returns:
            The final compiled report

        Raises:
            Exception: If graph execution fails
        """
        self.on_start(input_data)

        try:
            state = {
                "topic": input_data,
                "outline": {},
                "active_perspectives": [],
                "questions": {},
                "queries": [],
                "search_results": {},
                "synthesized_sections": {},
                "final_report": None,
                "error": None
            }

            final_state = self.graph.invoke(state)

            if final_state.get("error"):
                raise Exception(final_state["error"])

            result = final_state["final_report"]
            self.on_finish(result)
            return result

        except Exception as e:
            self.on_error(e)
            raise

    def _generate_outline(self, state: Dict) -> Dict:
        """Generate hierarchical outline for the topic.

        Creates a structured outline with sections and subsections.

        Args:
            state: Current state with topic

        Returns:
            Updated state with outline
        """
        if state.get("error"):
            return state

        try:
            prompt_data = self._load_prompt("GenerateOutline")
            outline_llm: BaseChatModel = self._get_llm("thinking")

            # Build messages
            system_prompt = prompt_data["system"]
            user_prompt = prompt_data["user"].format(topic=state["topic"])

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # Get outline
            response = outline_llm.invoke(messages)
            outline_text = response.content

            # Parse outline
            outline = self._parse_outline(outline_text)
            state["outline"] = outline

        except Exception as e:
            state["error"] = f"Outline generation error: {str(e)}"

        return state

    def _parse_outline(self, outline_text: str) -> Dict[str, List[str]]:
        """Parse outline text into structured format.

        Expected format:
            SECTION: Introduction
            SUBSECTION: Background
            SUBSECTION: Objectives

            SECTION: Main Body
            SUBSECTION: Topic 1
            SUBSECTION: Topic 2

        Args:
            outline_text: LLM output

        Returns:
            Dictionary mapping sections to subsections
        """
        outline = {}
        current_section = None

        for line in outline_text.split("\n"):
            line = line.strip()
            if not line:
                continue

            if line.startswith("SECTION:"):
                current_section = line.split(":", 1)[1].strip()
                outline[current_section] = []

            elif line.startswith("SUBSECTION:") and current_section:
                subsection = line.split(":", 1)[1].strip()
                outline[current_section].append(subsection)

        # Fallback: create basic outline
        if not outline:
            topic = outline_text[:50]
            outline = {
                "Introduction": [],
                "Main Content": [f"Overview of {topic}"],
                "Conclusion": []
            }

        return outline

    def _generate_perspectives(self, state: Dict) -> Dict:
        """Generate or select relevant perspectives for the topic.

        Args:
            state: Current state with topic

        Returns:
            Updated state with active_perspectives
        """
        if state.get("error"):
            return state

        try:
            prompt_data = self._load_prompt("GeneratePerspectives")
            perspective_llm: BaseChatModel = self._get_llm("thinking")

            # Format available perspectives
            perspectives_text = self._format_perspectives()

            # Build messages
            system_prompt = prompt_data["system"]
            user_prompt = prompt_data["user"].format(
                topic=state["topic"],
                perspectives=perspectives_text
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # Get perspective selection
            response = perspective_llm.invoke(messages)
            selection_text = response.content

            # Parse selected perspectives
            selected = self._parse_perspectives(selection_text)
            state["active_perspectives"] = selected

        except Exception as e:
            state["error"] = f"Perspective generation error: {str(e)}"

        return state

    def _format_perspectives(self) -> str:
        """Format perspective options for prompt.

        Returns:
            Formatted string of perspectives
        """
        lines = []
        for i, p in enumerate(self.perspectives, 1):
            lines.append(f"{i}. **{p['name']}**: {p['description']}")
        return "\n".join(lines)

    def _parse_perspectives(self, selection_text: str) -> List[Dict[str, str]]:
        """Parse selected perspectives from LLM output.

        Args:
            selection_text: LLM output

        Returns:
            List of selected perspective dictionaries
        """
        selected = []
        perspective_dict = {p["name"]: p for p in self.perspectives}

        for line in selection_text.split("\n"):
            if line.strip().startswith("PERSPECTIVE:"):
                name = line.split(":", 1)[1].strip()
                if name in perspective_dict:
                    selected.append(perspective_dict[name])

        # Fallback: use first few perspectives
        if not selected:
            selected = self.perspectives[:min(3, len(self.perspectives))]

        return selected

    def _generate_questions(self, state: Dict) -> Dict:
        """Generate questions for each section from each perspective.

        Args:
            state: Current state with outline and perspectives

        Returns:
            Updated state with questions
        """
        if state.get("error"):
            return state

        try:
            prompt_data = self._load_prompt("GenerateQuestions")
            question_llm: BaseChatModel = self._get_llm("thinking")

            questions = {}

            # For each section
            for section, subsections in state["outline"].items():
                questions[section] = {}

                # For each perspective
                for perspective in state["active_perspectives"]:
                    # Build messages
                    system_prompt = prompt_data["system"]
                    user_prompt = prompt_data["user"].format(
                        topic=state["topic"],
                        section=section,
                        subsections=", ".join(subsections) if subsections else "N/A",
                        perspective_name=perspective["name"],
                        perspective_description=perspective["description"]
                    )

                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_prompt)
                    ]

                    # Get questions
                    response = question_llm.invoke(messages)
                    question_text = response.content

                    # Parse questions
                    q_list = self._parse_questions(question_text)
                    questions[section][perspective["name"]] = q_list

            state["questions"] = questions

        except Exception as e:
            state["error"] = f"Question generation error: {str(e)}"

        return state

    def _parse_questions(self, question_text: str) -> List[str]:
        """Parse questions from LLM output.

        Args:
            question_text: LLM output

        Returns:
            List of questions
        """
        questions = []

        for line in question_text.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("Q:") or line.startswith("-")):
                # Remove numbering/markers
                question = line.lstrip("0123456789.-:Q ").strip()
                if question:
                    questions.append(question)

        # Fallback
        if not questions:
            questions = [question_text.strip()]

        return questions[:5]  # Limit to 5 questions per section/perspective

    def _dispatch_queries(self, state: Dict) -> Dict:
        """Prepare all queries for retrieval.

        Args:
            state: Current state with questions

        Returns:
            Updated state with queries list
        """
        if state.get("error"):
            return state

        queries = []

        for section, perspectives_dict in state["questions"].items():
            for perspective, question_list in perspectives_dict.items():
                for question in question_list:
                    queries.append({
                        "section": section,
                        "perspective": perspective,
                        "question": question
                    })

        state["queries"] = queries
        return state

    def _execute_search(self, state: Dict) -> Dict:
        """Execute retrieval for all queries.

        Args:
            state: Current state with queries

        Returns:
            Updated state with search_results
        """
        if state.get("error"):
            return state

        try:
            results = {}

            for query_item in state["queries"]:
                section = query_item["section"]
                perspective = query_item["perspective"]
                question = query_item["question"]

                # Execute retrieval
                retrieved = self._retrieve_information(question)

                # Store results
                if section not in results:
                    results[section] = {}
                if perspective not in results[section]:
                    results[section][perspective] = []

                results[section][perspective].append({
                    "question": question,
                    "information": retrieved
                })

            state["search_results"] = results

        except Exception as e:
            state["error"] = f"Search execution error: {str(e)}"

        return state

    def _retrieve_information(self, query: str) -> str:
        """Retrieve information for a query.

        Args:
            query: Search query

        Returns:
            Retrieved information
        """
        # Try to use retrieval tools
        if "search" in self.retrieval_tools:
            try:
                return self.retrieval_tools["search"](query)
            except:
                pass

        # Fallback: simulated retrieval
        return f"Information retrieved about: {query}"

    def _collect_results(self, state: Dict) -> Dict:
        """Collect and organize search results.

        Args:
            state: Current state with search_results

        Returns:
            Updated state (results already organized)
        """
        # Results are already organized by section and perspective
        return state

    def _synthesize_sections(self, state: Dict) -> Dict:
        """Synthesize content for each section from all perspectives.

        Args:
            state: Current state with search_results

        Returns:
            Updated state with synthesized_sections
        """
        if state.get("error"):
            return state

        try:
            prompt_data = self._load_prompt("SynthesizeSection")
            synthesis_llm: BaseChatModel = self._get_llm("documentation")

            synthesized = {}

            for section, perspective_results in state["search_results"].items():
                # Gather all information for this section
                all_info = []
                for perspective, results_list in perspective_results.items():
                    for result in results_list:
                        all_info.append(f"[{perspective}] {result['information']}")

                combined_info = "\n".join(all_info)

                # Build messages
                system_prompt = prompt_data["system"]
                user_prompt = prompt_data["user"].format(
                    topic=state["topic"],
                    section=section,
                    information=combined_info
                )

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ]

                # Synthesize section
                response = synthesis_llm.invoke(messages)
                synthesized[section] = response.content

            state["synthesized_sections"] = synthesized

        except Exception as e:
            state["error"] = f"Section synthesis error: {str(e)}"

        return state

    def _compile_report(self, state: Dict) -> Dict:
        """Compile all sections into final report.

        Args:
            state: Current state with synthesized_sections

        Returns:
            Updated state with final_report
        """
        if state.get("error"):
            state["final_report"] = f"Error: {state['error']}"
            return state

        try:
            prompt_data = self._load_prompt("CompileReport")
            compilation_llm: BaseChatModel = self._get_llm("documentation")

            # Format sections
            sections_text = []
            for section, content in state["synthesized_sections"].items():
                sections_text.append(f"## {section}\n\n{content}")

            all_sections = "\n\n".join(sections_text)

            # Build messages
            system_prompt = prompt_data["system"]
            user_prompt = prompt_data["user"].format(
                topic=state["topic"],
                sections=all_sections
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # Compile final report
            response = compilation_llm.invoke(messages)
            state["final_report"] = response.content

        except Exception as e:
            state["final_report"] = f"Compilation error: {str(e)}"

        return state
