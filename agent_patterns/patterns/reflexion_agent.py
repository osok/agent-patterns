"""
Reflexion Agent Pattern.

This module implements the Reflexion pattern where an agent performs multiple trials,
learns from failures and successes, and stores insights in a reflection memory that
informs subsequent attempts.
"""

from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from agent_patterns.core.base_agent import BaseAgent


class ReflexionAgent(BaseAgent):
    """
    Reflexion agent pattern.

    This agent implements multi-trial learning with persistent reflection memory:
    1. Plan: Plan the next action using previous reflection insights
    2. Execute: Attempt to solve the task
    3. Evaluate: Assess whether the attempt succeeded or failed
    4. Reflect: Generate insights about what worked or didn't work
    5. Update Memory: Store insights for future trials
    6. Repeat: Continue until success or max trials reached

    This differs from simple Reflection by maintaining memory across multiple attempts,
    enabling the agent to learn from its mistakes over multiple trials.

    State Keys:
        - input_task (str): The user's task or problem
        - reflection_memory (List[str]): Accumulated insights from previous trials
        - trial_count (int): Current trial number
        - max_trials (int): Maximum number of trials allowed
        - current_plan (str): Plan for the current trial
        - outcome (Any): Result from executing the current attempt
        - evaluation (str): Assessment of the outcome ("success" or "failure")
        - trial_reflection (str): Insight generated from the current trial
        - final_answer (str): The final output to return

    Example:
        >>> agent = ReflexionAgent(llm_configs=configs, max_trials=3)
        >>> result = agent.run("Solve this puzzle: [puzzle description]")
    """

    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        max_trials: int = 3,
        prompt_dir: str = "prompts",
        custom_instructions: Optional[str] = None,
        prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
    ):
        """
        Initialize the Reflexion agent.

        Args:
            llm_configs: Configuration for LLM roles (should include 'thinking', 'reflection', 'execution')
            max_trials: Maximum number of trial attempts
            prompt_dir: Directory containing prompt templates
            custom_instructions: Custom instructions appended to all system prompts
            prompt_overrides: Dictionary mapping step names to prompt overrides
        """
        self.max_trials = max_trials
        super().__init__(
            llm_configs=llm_configs,
            prompt_dir=prompt_dir,
            custom_instructions=custom_instructions,
            prompt_overrides=prompt_overrides
        )

    def build_graph(self) -> None:
        """
        Build the Reflexion state graph.

        Graph structure:
            plan_action_with_memory -> execute_action -> evaluate_outcome
            -> reflect_on_trial -> update_reflection_memory -> check_continue
            check_continue -> plan_action_with_memory (if continue) or final_output (if done)
        """
        workflow = StateGraph(dict)

        # Add nodes
        workflow.add_node("plan_action_with_memory", self._plan_action_with_memory)
        workflow.add_node("execute_action", self._execute_action)
        workflow.add_node("evaluate_outcome", self._evaluate_outcome)
        workflow.add_node("reflect_on_trial", self._reflect_on_trial)
        workflow.add_node("update_reflection_memory", self._update_reflection_memory)
        workflow.add_node("final_output", lambda s: s)

        # Set entry point
        workflow.set_entry_point("plan_action_with_memory")

        # Add edges
        workflow.add_edge("plan_action_with_memory", "execute_action")
        workflow.add_edge("execute_action", "evaluate_outcome")
        workflow.add_edge("evaluate_outcome", "reflect_on_trial")
        workflow.add_edge("reflect_on_trial", "update_reflection_memory")

        # Conditional edge from update_reflection_memory
        workflow.add_conditional_edges(
            "update_reflection_memory",
            self._check_continue,
            {
                "continue": "plan_action_with_memory",
                "finish": "final_output",
            },
        )

        # Final edge
        workflow.add_edge("final_output", END)

        # Compile
        self.graph = workflow.compile()

    def run(self, input_data: str) -> str:
        """
        Execute the Reflexion pattern on the given input.

        Args:
            input_data: The user's task or problem statement

        Returns:
            The final answer after multiple trial attempts

        Raises:
            ValueError: If the graph hasn't been built
        """
        if self.graph is None:
            raise ValueError("Graph has not been built. Call build_graph() first.")

        # Initialize state
        initial_state = {
            "input_task": input_data,
            "reflection_memory": [],
            "trial_count": 0,
            "max_trials": self.max_trials,
            "current_plan": None,
            "outcome": None,
            "evaluation": None,
            "trial_reflection": None,
            "final_answer": None,
        }

        # Invoke lifecycle hooks
        self.on_start(input_data)

        try:
            # Run the graph
            result_state = self.graph.invoke(initial_state)
            final_answer = result_state.get("final_answer", "No answer generated")

            # Invoke lifecycle hook
            self.on_finish(final_answer)

            return final_answer

        except Exception as e:
            self.on_error(e)
            raise

    def _plan_action_with_memory(self, state: Dict) -> Dict:
        """
        Plan the next action using reflection memory from previous trials.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with current plan
        """
        # Increment trial counter
        state["trial_count"] = state.get("trial_count", 0) + 1

        # Load prompts
        prompts = self._load_prompt("PlanWithMemory")
        system_prompt = prompts.get(
            "system_prompt",
            "You are an agent that learns from past attempts. "
            "Use insights from previous trials to plan better approaches.",
        )
        user_prompt_template = prompts.get(
            "user_prompt",
            "Task: {task}\n\nTrial: {trial_count}/{max_trials}\n\n"
            "Reflection Memory (lessons from past trials):\n{memory}\n\n"
            "Plan your next approach, incorporating what you've learned.",
        )

        # Format reflection memory
        memory_text = self._format_memory(state.get("reflection_memory", []))

        # Format user prompt
        user_prompt = user_prompt_template.format(
            task=state["input_task"],
            trial_count=state["trial_count"],
            max_trials=state["max_trials"],
            memory=memory_text,
        )

        # Get LLM
        llm = self._get_llm("thinking")

        # Generate plan
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        current_plan = response.content

        # Update state
        state["current_plan"] = current_plan

        return state

    def _execute_action(self, state: Dict) -> Dict:
        """
        Execute the current plan to attempt solving the task.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with outcome
        """
        # Load prompts
        prompts = self._load_prompt("Execute")
        system_prompt = prompts.get(
            "system_prompt",
            "You are an agent executing a specific plan to solve a task.",
        )
        user_prompt_template = prompts.get(
            "user_prompt",
            "Task: {task}\n\nPlan: {plan}\n\nExecute this plan and provide the result.",
        )

        # Format user prompt
        user_prompt = user_prompt_template.format(
            task=state["input_task"], plan=state["current_plan"]
        )

        # Get LLM
        llm = self._get_llm("execution")

        # Execute
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        outcome = response.content

        # Update state
        state["outcome"] = outcome

        return state

    def _evaluate_outcome(self, state: Dict) -> Dict:
        """
        Evaluate whether the current attempt succeeded or failed.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with evaluation
        """
        # Load prompts
        prompts = self._load_prompt("Evaluate")
        system_prompt = prompts.get(
            "system_prompt",
            "You are an evaluator who determines if a task was successfully completed. "
            "Respond with either 'SUCCESS' or 'FAILURE' followed by a brief explanation.",
        )
        user_prompt_template = prompts.get(
            "user_prompt",
            "Task: {task}\n\nAttempted Solution: {outcome}\n\n"
            "Did this successfully complete the task? Respond with SUCCESS or FAILURE and explain why.",
        )

        # Format user prompt
        user_prompt = user_prompt_template.format(
            task=state["input_task"], outcome=state["outcome"]
        )

        # Get LLM
        llm = self._get_llm("reflection")

        # Evaluate
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        evaluation_text = response.content

        # Parse evaluation (simple heuristic)
        if "success" in evaluation_text.lower():
            evaluation = "success"
        else:
            evaluation = "failure"

        # Update state
        state["evaluation"] = evaluation
        state["evaluation_detail"] = evaluation_text

        return state

    def _reflect_on_trial(self, state: Dict) -> Dict:
        """
        Generate reflection insights from the current trial.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with trial reflection
        """
        # Load prompts
        prompts = self._load_prompt("ReflectOnTrial")
        system_prompt = prompts.get(
            "system_prompt",
            "You are a reflective agent that learns from experiences. "
            "Generate actionable insights about what worked and what didn't.",
        )
        user_prompt_template = prompts.get(
            "user_prompt",
            "Task: {task}\n\nPlan: {plan}\n\nOutcome: {outcome}\n\n"
            "Evaluation: {evaluation}\n\n"
            "What insights can you extract from this trial? "
            "What should be done differently next time?",
        )

        # Format user prompt
        user_prompt = user_prompt_template.format(
            task=state["input_task"],
            plan=state["current_plan"],
            outcome=state["outcome"],
            evaluation=state.get("evaluation_detail", state.get("evaluation", "unknown")),
        )

        # Get LLM
        llm = self._get_llm("reflection")

        # Generate reflection
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        trial_reflection = response.content

        # Update state
        state["trial_reflection"] = trial_reflection

        return state

    def _update_reflection_memory(self, state: Dict) -> Dict:
        """
        Add the trial reflection to the persistent reflection memory.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with memory updated
        """
        # Add reflection to memory
        reflection_memory = state.get("reflection_memory", [])
        trial_num = state.get("trial_count", 0)
        reflection_entry = f"Trial {trial_num}: {state['trial_reflection']}"
        reflection_memory.append(reflection_entry)

        state["reflection_memory"] = reflection_memory

        return state

    def _check_continue(self, state: Dict) -> str:
        """
        Decide whether to continue with another trial or finish.

        Args:
            state: Current state dictionary

        Returns:
            "continue" to try again, "finish" to stop
        """
        # Check if we succeeded
        if state.get("evaluation") == "success":
            state["final_answer"] = state["outcome"]
            return "finish"

        # Check if we've exhausted trials
        if state.get("trial_count", 0) >= state.get("max_trials", 3):
            # Generate final answer based on best attempt
            state["final_answer"] = self._generate_final_answer(state)
            return "finish"

        # Continue with another trial
        return "continue"

    def _format_memory(self, memory: List[str]) -> str:
        """
        Format reflection memory into readable text.

        Args:
            memory: List of reflection entries

        Returns:
            Formatted memory string
        """
        if not memory:
            return "No previous trials yet. This is your first attempt."

        return "\n\n".join(memory)

    def _generate_final_answer(self, state: Dict) -> str:
        """
        Generate final answer when max trials reached without success.

        Args:
            state: Current state dictionary

        Returns:
            Final answer string
        """
        # Load prompts
        prompts = self._load_prompt("GenerateFinal")
        system_prompt = prompts.get(
            "system_prompt",
            "You are synthesizing the best possible answer from multiple attempts.",
        )
        user_prompt_template = prompts.get(
            "user_prompt",
            "Task: {task}\n\nReflection Memory:\n{memory}\n\n"
            "Last Outcome: {outcome}\n\n"
            "Generate the best possible final answer based on all attempts.",
        )

        # Format user prompt
        user_prompt = user_prompt_template.format(
            task=state["input_task"],
            memory=self._format_memory(state.get("reflection_memory", [])),
            outcome=state.get("outcome", "No outcome"),
        )

        # Get LLM
        llm = self._get_llm("documentation")

        # Generate final answer
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        final_answer = response.content

        return final_answer
