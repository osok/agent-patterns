"""
Reflection Agent Pattern.

This module implements the Reflection pattern where an agent generates an initial response,
critiques it, and optionally refines it based on the critique.
"""

from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from agent_patterns.core.base_agent import BaseAgent


class ReflectionAgent(BaseAgent):
    """
    Reflection agent pattern.

    This agent implements a generate-reflect-refine cycle:
    1. Generate: Create an initial response to the task
    2. Reflect: Critique the initial response
    3. Refine: Improve the response based on the critique (if needed)

    This pattern is particularly effective for tasks requiring high-quality outputs
    where self-critique can lead to meaningful improvements.

    State Keys:
        - input_task (str): The user's task or request
        - initial_output (str): First attempt at solving the task
        - reflection (str): Critique of the initial output
        - refined_output (str): Improved output after reflection
        - needs_refinement (bool): Whether refinement is necessary
        - final_answer (str): The final output to return
        - max_reflection_cycles (int): Maximum number of reflect-refine iterations

    Example:
        >>> agent = ReflectionAgent(llm_configs=configs)
        >>> result = agent.run("Write a short story about a robot dog")
    """

    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        max_reflection_cycles: int = 1,
        prompt_dir: str = "prompts",
        custom_instructions: Optional[str] = None,
        prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
    ):
        """
        Initialize the Reflection agent.

        Args:
            llm_configs: Configuration for LLM roles (should include 'documentation' and 'reflection')
            max_reflection_cycles: Maximum number of times to refine (default 1)
            prompt_dir: Directory containing prompt templates
            custom_instructions: Custom instructions appended to all system prompts
            prompt_overrides: Dictionary mapping step names to prompt overrides
        """
        self.max_reflection_cycles = max_reflection_cycles
        super().__init__(
            llm_configs=llm_configs,
            prompt_dir=prompt_dir,
            custom_instructions=custom_instructions,
            prompt_overrides=prompt_overrides
        )

    def build_graph(self) -> None:
        """
        Build the Reflection state graph.

        Graph structure:
            generate_initial -> reflect -> check_refine
            check_refine -> refine (if needs refinement) or final_output (if done)
            refine -> check_cycle_limit
            check_cycle_limit -> reflect (if under limit) or final_output (if at limit)
        """
        workflow = StateGraph(dict)

        # Add nodes
        workflow.add_node("generate_initial", self._generate_initial_output)
        workflow.add_node("reflect", self._reflect_on_output)
        workflow.add_node("check_refine", self._check_refinement_needed)
        workflow.add_node("refine", self._refine_output)
        workflow.add_node("check_cycle_limit", self._check_cycle_limit)
        workflow.add_node("final_output", lambda s: s)

        # Set entry point
        workflow.set_entry_point("generate_initial")

        # Add edges
        workflow.add_edge("generate_initial", "reflect")
        workflow.add_edge("reflect", "check_refine")

        # Conditional edge from check_refine
        workflow.add_conditional_edges(
            "check_refine",
            lambda s: "refine" if s.get("needs_refinement", False) else "done",
            {
                "refine": "refine",
                "done": "final_output",
            },
        )

        # After refine, check if we should do another cycle
        workflow.add_edge("refine", "check_cycle_limit")

        # Conditional edge from check_cycle_limit
        workflow.add_conditional_edges(
            "check_cycle_limit",
            lambda s: "continue" if s.get("continue_reflection", False) else "done",
            {
                "continue": "reflect",
                "done": "final_output",
            },
        )

        # Final edge
        workflow.add_edge("final_output", END)

        # Compile
        self.graph = workflow.compile()

    def run(self, input_data: str) -> str:
        """
        Execute the Reflection pattern on the given input.

        Args:
            input_data: The user's task or request

        Returns:
            The final refined output

        Raises:
            ValueError: If the graph hasn't been built
        """
        if self.graph is None:
            raise ValueError("Graph has not been built. Call build_graph() first.")

        # Initialize state
        initial_state = {
            "input_task": input_data,
            "initial_output": None,
            "reflection": None,
            "refined_output": None,
            "needs_refinement": False,
            "final_answer": None,
            "reflection_cycle": 0,
            "max_reflection_cycles": self.max_reflection_cycles,
            "continue_reflection": False,
        }

        # Invoke lifecycle hooks
        self.on_start(input_data)

        try:
            # Run the graph
            result_state = self.graph.invoke(initial_state)
            final_answer = result_state.get("final_answer")

            # If no final_answer set, use refined or initial output
            if not final_answer:
                final_answer = (
                    result_state.get("refined_output")
                    or result_state.get("initial_output")
                    or "No output generated"
                )

            # Invoke lifecycle hook
            self.on_finish(final_answer)

            return final_answer

        except Exception as e:
            self.on_error(e)
            raise

    def _generate_initial_output(self, state: Dict) -> Dict:
        """
        Generate the initial output using the documentation LLM.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with initial output
        """
        # Load prompts
        prompts = self._load_prompt("Generate")
        system_prompt = prompts.get(
            "system",
            "You are a helpful assistant that produces high-quality responses to user requests.",
        )
        user_prompt_template = prompts.get(
            "user", "Task: {task}\n\nProvide a comprehensive response."
        )

        # Format user prompt
        user_prompt = user_prompt_template.format(task=state["input_task"])

        # Get LLM
        llm = self._get_llm("documentation")

        # Generate initial output
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        initial_output = response.content

        # Update state
        state["initial_output"] = initial_output

        return state

    def _reflect_on_output(self, state: Dict) -> Dict:
        """
        Critique the current output using the reflection LLM.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with reflection/critique
        """
        # Increment reflection cycle counter
        state["reflection_cycle"] = state.get("reflection_cycle", 0) + 1

        # Determine what to reflect on
        output_to_reflect = state.get("refined_output") or state.get("initial_output")

        # Load prompts
        prompts = self._load_prompt("Reflect")
        system_prompt = prompts.get(
            "system",
            "You are a thoughtful critic who provides constructive feedback "
            "to improve responses. Focus on accuracy, completeness, clarity, and usefulness.",
        )
        user_prompt_template = prompts.get(
            "user",
            "Original task: {task}\n\nCurrent response:\n{output}\n\n"
            "Provide a detailed critique. What could be improved? "
            "What's missing? What's excellent about it?",
        )

        # Format user prompt
        user_prompt = user_prompt_template.format(
            task=state["input_task"], output=output_to_reflect
        )

        # Get reflection LLM
        llm = self._get_llm("reflection")

        # Generate reflection
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        reflection = response.content

        # Update state
        state["reflection"] = reflection

        return state

    def _check_refinement_needed(self, state: Dict) -> Dict:
        """
        Determine if refinement is necessary based on the reflection.

        This uses simple heuristics. Subclasses can override for more sophisticated logic.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with needs_refinement flag
        """
        reflection = state.get("reflection", "").lower()

        # Simple heuristics to determine if refinement is needed
        negative_indicators = [
            "incomplete",
            "missing",
            "incorrect",
            "inaccurate",
            "could be improved",
            "should add",
            "needs more",
            "lacks",
            "insufficient",
            "vague",
            "unclear",
        ]

        positive_indicators = [
            "excellent",
            "comprehensive",
            "well done",
            "thorough",
            "accurate",
            "complete",
            "no improvements needed",
            "perfect",
        ]

        # Count indicators
        negative_count = sum(1 for indicator in negative_indicators if indicator in reflection)
        positive_count = sum(1 for indicator in positive_indicators if indicator in reflection)

        # Decide if refinement is needed
        needs_refinement = negative_count > positive_count

        state["needs_refinement"] = needs_refinement

        return state

    def _refine_output(self, state: Dict) -> Dict:
        """
        Generate a refined output incorporating the reflection feedback.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with refined output
        """
        # Get the output to refine
        output_to_refine = state.get("refined_output") or state.get("initial_output")

        # Load prompts
        prompts = self._load_prompt("Refine")
        system_prompt = prompts.get(
            "system",
            "You are a skilled editor who improves responses based on feedback. "
            "Address all points raised in the critique while maintaining what works well.",
        )
        user_prompt_template = prompts.get(
            "user",
            "Original task: {task}\n\nCurrent response:\n{output}\n\n"
            "Critique:\n{reflection}\n\n"
            "Produce an improved version that addresses the critique.",
        )

        # Format user prompt
        user_prompt = user_prompt_template.format(
            task=state["input_task"],
            output=output_to_refine,
            reflection=state["reflection"],
        )

        # Get LLM (using documentation model for generation)
        llm = self._get_llm("documentation")

        # Generate refined output
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        refined_output = response.content

        # Update state
        state["refined_output"] = refined_output
        state["final_answer"] = refined_output

        return state

    def _check_cycle_limit(self, state: Dict) -> Dict:
        """
        Check if we should continue with another reflection cycle.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with continue_reflection flag
        """
        current_cycle = state.get("reflection_cycle", 0)
        max_cycles = state.get("max_reflection_cycles", 1)

        # Continue if we haven't hit the limit
        state["continue_reflection"] = current_cycle < max_cycles

        return state
