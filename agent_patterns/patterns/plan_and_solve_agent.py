"""
Plan & Solve Agent Pattern.

This module implements the Plan & Solve pattern which separates planning from execution.
The agent first creates a comprehensive plan, then executes each step sequentially.
"""

from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from agent_patterns.core.base_agent import BaseAgent


class PlanAndSolveAgent(BaseAgent):
    """
    Plan & Solve agent pattern.

    This agent follows a two-phase approach:
    1. Planning: Generate a multi-step plan to solve the problem
    2. Execution: Execute each step of the plan sequentially

    This pattern is particularly effective for tasks that can be decomposed
    into clear, sequential steps.

    State Keys:
        - input_task (str): The user's task or problem
        - plan (List[Dict]): List of step dictionaries with descriptions and details
        - current_step_index (int): Index of the currently executing step
        - step_results (List[str]): Results from each completed step
        - plan_done (bool): Whether all steps have been executed
        - final_result (str): The aggregated final answer

    Example:
        >>> agent = PlanAndSolveAgent(llm_configs=configs)
        >>> result = agent.run("Write a research report on renewable energy")
    """

    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        prompt_dir: str = "prompts",
        custom_instructions: Optional[str] = None,
        prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
    ):
        """
        Initialize the Plan & Solve agent.

        Args:
            llm_configs: Configuration for LLM roles (should include 'planning' and 'execution')
            prompt_dir: Directory containing prompt templates
            custom_instructions: Custom instructions appended to all system prompts
            prompt_overrides: Dictionary mapping step names to prompt overrides
        """
        super().__init__(
            llm_configs=llm_configs,
            prompt_dir=prompt_dir,
            custom_instructions=custom_instructions,
            prompt_overrides=prompt_overrides
        )

    def build_graph(self) -> None:
        """
        Build the Plan & Solve state graph.

        Graph structure:
            plan_step -> execute_step -> check_completion
            check_completion -> execute_step (if not done) or aggregate_results (if done)
        """
        workflow = StateGraph(dict)

        # Add nodes
        workflow.add_node("plan_step", self._generate_plan)
        workflow.add_node("execute_step", self._execute_plan_step)
        workflow.add_node("check_completion", self._check_plan_completion)
        workflow.add_node("aggregate_results", self._aggregate_results)

        # Set entry point
        workflow.set_entry_point("plan_step")

        # Add edges
        workflow.add_edge("plan_step", "execute_step")
        workflow.add_edge("execute_step", "check_completion")

        # Conditional edge from check_completion
        workflow.add_conditional_edges(
            "check_completion",
            lambda s: "done" if s.get("plan_done", False) else "continue",
            {
                "continue": "execute_step",
                "done": "aggregate_results",
            },
        )

        # Final edge
        workflow.add_edge("aggregate_results", END)

        # Compile
        self.graph = workflow.compile()

    def run(self, input_data: str) -> str:
        """
        Execute the Plan & Solve pattern on the given input.

        Args:
            input_data: The user's task or problem statement

        Returns:
            The final aggregated result

        Raises:
            ValueError: If the graph hasn't been built
        """
        if self.graph is None:
            raise ValueError("Graph has not been built. Call build_graph() first.")

        # Initialize state
        initial_state = {
            "input_task": input_data,
            "plan": [],
            "current_step_index": 0,
            "step_results": [],
            "plan_done": False,
            "final_result": None,
        }

        # Invoke lifecycle hooks
        self.on_start(input_data)

        try:
            # Run the graph
            result_state = self.graph.invoke(initial_state)
            final_result = result_state.get("final_result", "No result generated")

            # Invoke lifecycle hook
            self.on_finish(final_result)

            return final_result

        except Exception as e:
            self.on_error(e)
            raise

    def _generate_plan(self, state: Dict) -> Dict:
        """
        Generate a multi-step plan for the task using the planning LLM.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with generated plan
        """
        # Load prompts
        prompts = self._load_prompt("PlanStep")
        system_prompt = prompts.get(
            "system_prompt",
            "You are an expert at breaking down complex tasks into clear, actionable steps.",
        )
        user_prompt_template = prompts.get(
            "user_prompt",
            "Task: {task}\n\nCreate a detailed step-by-step plan to complete this task. "
            "Number each step and be specific.",
        )

        # Format user prompt
        user_prompt = user_prompt_template.format(task=state["input_task"])

        # Get planning LLM
        llm = self._get_llm("planning")

        # Generate plan
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        plan_text = response.content

        # Parse plan into structured format
        plan = self._parse_plan(plan_text)

        # Update state
        state["plan"] = plan
        state["current_step_index"] = 0

        return state

    def _execute_plan_step(self, state: Dict) -> Dict:
        """
        Execute the current step in the plan.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with step result
        """
        plan = state["plan"]
        idx = state["current_step_index"]

        # Check if there are more steps to execute
        if idx >= len(plan):
            return state

        # Get current step
        step = plan[idx]

        # Execute the step
        result = self._run_single_step(step, state)

        # Store result
        state["step_results"].append(result)
        state["current_step_index"] = idx + 1

        return state

    def _check_plan_completion(self, state: Dict) -> Dict:
        """
        Check if all plan steps have been completed.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with plan_done flag
        """
        if state["current_step_index"] >= len(state["plan"]):
            state["plan_done"] = True
        else:
            state["plan_done"] = False

        return state

    def _aggregate_results(self, state: Dict) -> Dict:
        """
        Aggregate the results from all steps into a final answer.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with final result
        """
        # Load prompts
        prompts = self._load_prompt("AggregateStep")
        system_prompt = prompts.get(
            "system_prompt",
            "You are an expert at synthesizing information into clear, comprehensive answers.",
        )
        user_prompt_template = prompts.get(
            "user_prompt",
            "Original task: {task}\n\nStep results:\n{results}\n\n"
            "Provide a comprehensive final answer that addresses the original task.",
        )

        # Format step results
        results_text = self._format_step_results(state["plan"], state["step_results"])

        # Format user prompt
        user_prompt = user_prompt_template.format(
            task=state["input_task"], results=results_text
        )

        # Get LLM (can use documentation or planning model)
        llm = self._get_llm("documentation")

        # Generate final answer
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        final_result = response.content

        # Update state
        state["final_result"] = final_result

        return state

    def _run_single_step(self, step: Dict, state: Dict) -> str:
        """
        Execute a single step from the plan.

        This method uses an execution LLM to carry out the step's instructions.
        Subclasses can override this to implement custom execution logic.

        Args:
            step: Dictionary containing step description and details
            state: Current state dictionary for context

        Returns:
            Result of executing the step
        """
        step_description = step.get("step_description", "")

        # Load prompts
        prompts = self._load_prompt("ExecuteStep")
        system_prompt = prompts.get(
            "system_prompt", "You are a helpful assistant executing a specific task step."
        )
        user_prompt_template = prompts.get(
            "user_prompt",
            "Original task: {task}\n\nCurrent step: {step}\n\n"
            "Previous results: {previous_results}\n\nExecute this step and provide the result.",
        )

        # Format previous results
        previous_results = "\n".join(
            f"Step {i + 1}: {result}"
            for i, result in enumerate(state.get("step_results", []))
        )

        # Format user prompt
        user_prompt = user_prompt_template.format(
            task=state["input_task"],
            step=step_description,
            previous_results=previous_results if previous_results else "None yet",
        )

        # Get execution LLM
        llm = self._get_llm("execution")

        # Execute step
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        result = response.content

        return result

    def _parse_plan(self, plan_text: str) -> List[Dict]:
        """
        Parse plan text into structured step dictionaries.

        Args:
            plan_text: Raw plan text from LLM

        Returns:
            List of step dictionaries
        """
        plan = []
        lines = plan_text.strip().split("\n")

        current_step = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this is a step line (starts with number or "Step")
            if (
                line[0].isdigit()
                or line.lower().startswith("step")
                or line.startswith("-")
                or line.startswith("*")
            ):
                # Save previous step if exists
                if current_step:
                    plan.append(current_step)

                # Start new step
                # Remove numbering/bullets
                step_text = line.lstrip("0123456789.-*) ")
                if step_text.lower().startswith("step"):
                    step_text = step_text.split(":", 1)[-1].strip()

                current_step = {"step_description": step_text}
            elif current_step:
                # Continue description of current step
                current_step["step_description"] += " " + line

        # Add last step
        if current_step:
            plan.append(current_step)

        # If parsing failed, create a single step
        if not plan:
            plan = [{"step_description": plan_text}]

        return plan

    def _format_step_results(self, plan: List[Dict], results: List[str]) -> str:
        """
        Format plan steps and their results into readable text.

        Args:
            plan: List of step dictionaries
            results: List of result strings

        Returns:
            Formatted results text
        """
        formatted_lines = []
        for i, (step, result) in enumerate(zip(plan, results), 1):
            step_desc = step.get("step_description", "")
            formatted_lines.append(f"Step {i}: {step_desc}")
            formatted_lines.append(f"Result: {result}")
            formatted_lines.append("")

        return "\n".join(formatted_lines)
