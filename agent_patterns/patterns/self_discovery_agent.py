"""Self-Discovery Pattern Implementation.

The Self-Discovery pattern allows agents to dynamically select and adapt reasoning
modules from a library of problem-solving heuristics. The agent discovers which
approaches are relevant, adapts them to the specific task, plans their application,
and executes the customized reasoning strategy.

Reference: https://arxiv.org/abs/2402.03620
"""

from typing import Any, Dict, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent_patterns.core.base_agent import BaseAgent


# Default reasoning module library
DEFAULT_REASONING_MODULES = [
    {
        "name": "break_down_problem",
        "description": "Decompose complex problems into smaller, manageable sub-problems",
        "template": "Break down '{task}' into distinct sub-problems that can be solved independently"
    },
    {
        "name": "identify_constraints",
        "description": "Identify and analyze constraints, requirements, and limitations",
        "template": "List all constraints, requirements, and limitations for '{task}'"
    },
    {
        "name": "analogical_reasoning",
        "description": "Find similar problems or situations and apply lessons learned",
        "template": "Find analogies to '{task}' from related domains and apply insights"
    },
    {
        "name": "first_principles",
        "description": "Reason from fundamental truths and build up the solution",
        "template": "Identify fundamental principles underlying '{task}' and reason from first principles"
    },
    {
        "name": "step_by_step",
        "description": "Proceed through the problem systematically, step by step",
        "template": "Solve '{task}' step by step, showing work at each stage"
    },
    {
        "name": "pros_and_cons",
        "description": "Evaluate different approaches by listing pros and cons",
        "template": "For each approach to '{task}', list pros and cons systematically"
    },
    {
        "name": "critical_analysis",
        "description": "Critically examine assumptions, evidence, and reasoning",
        "template": "Critically analyze the assumptions and evidence related to '{task}'"
    },
    {
        "name": "pattern_recognition",
        "description": "Identify patterns, trends, or regularities in the problem",
        "template": "Identify patterns or trends in '{task}' that suggest solutions"
    },
    {
        "name": "hypothesis_testing",
        "description": "Form hypotheses and test them systematically",
        "template": "Generate hypotheses about '{task}' and design tests to validate them"
    },
    {
        "name": "visualization",
        "description": "Create mental models or diagrams to understand the problem",
        "template": "Visualize '{task}' using diagrams, charts, or mental models"
    }
]


class SelfDiscoveryAgent(BaseAgent):
    """Self-Discovery agent that dynamically selects reasoning strategies.

    This pattern discovers which reasoning approaches are most relevant for a task,
    adapts them to the specific context, and executes a customized reasoning plan.

    Workflow:
        1. Discover/Select: Choose relevant reasoning modules from library
        2. Adapt: Customize selected modules for the specific task
        3. Plan: Create step-by-step reasoning plan
        4. Execute: Apply each reasoning step
        5. Synthesize: Combine results into final answer

    Args:
        llm_configs: Dictionary mapping role names to LLM configuration
        reasoning_modules: Custom reasoning module library (optional)
        max_selected_modules: Maximum modules to select (default: 3)
        prompt_dir: Directory containing prompt templates (default: "prompts")

    Example:
        >>> agent = SelfDiscoveryAgent(
        ...     llm_configs={
        ...         "thinking": {"provider": "openai", "model": "gpt-4"},
        ...         "execution": {"provider": "openai", "model": "gpt-4"}
        ...     },
        ...     max_selected_modules=3
        ... )
        >>> result = agent.run("Complex reasoning problem requiring multiple strategies")
    """

    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        reasoning_modules: Optional[List[Dict[str, str]]] = None,
        max_selected_modules: int = 3,
        prompt_dir: str = "prompts",
        custom_instructions: Optional[str] = None,
        prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
    ):
        """Initialize the Self-Discovery agent.

        Args:
            llm_configs: Dictionary mapping role names to LLM configuration
            reasoning_modules: Custom reasoning module library
            max_selected_modules: Maximum modules to select
            prompt_dir: Directory containing prompt templates
            custom_instructions: Custom instructions appended to all system prompts
            prompt_overrides: Dictionary mapping step names to prompt overrides
        """
        self.reasoning_modules = reasoning_modules or DEFAULT_REASONING_MODULES
        self.max_selected_modules = max_selected_modules
        super().__init__(
            llm_configs=llm_configs,
            prompt_dir=prompt_dir,
            custom_instructions=custom_instructions,
            prompt_overrides=prompt_overrides
        )

    def build_graph(self) -> None:
        """Build the LangGraph StateGraph for the Self-Discovery pattern.

        Creates a graph with the following nodes:
            - discover_modules: Selects relevant reasoning modules
            - adapt_modules: Customizes modules for task
            - plan_reasoning: Creates execution plan
            - execute_step: Executes one reasoning step
            - check_completion: Checks if plan is complete
            - synthesize_output: Creates final answer
        """
        workflow = StateGraph(dict)

        # Add nodes
        workflow.add_node("discover_modules", self._discover_modules)
        workflow.add_node("adapt_modules", self._adapt_modules)
        workflow.add_node("plan_reasoning", self._plan_reasoning)
        workflow.add_node("execute_step", self._execute_step)
        workflow.add_node("check_completion", self._check_completion)
        workflow.add_node("synthesize_output", self._synthesize_output)

        # Set entry point
        workflow.set_entry_point("discover_modules")

        # Add edges - linear to planning
        workflow.add_edge("discover_modules", "adapt_modules")
        workflow.add_edge("adapt_modules", "plan_reasoning")
        workflow.add_edge("plan_reasoning", "execute_step")
        workflow.add_edge("execute_step", "check_completion")

        # Conditional edges for looping or finishing
        workflow.add_conditional_edges(
            "check_completion",
            self._route_after_check,
            {
                "continue": "execute_step",
                "finish": "synthesize_output"
            }
        )

        workflow.add_edge("synthesize_output", "__end__")

        self.graph: CompiledStateGraph = workflow.compile()

    def run(self, input_data: Any) -> Any:
        """Execute the Self-Discovery workflow.

        Args:
            input_data: The user's task or query

        Returns:
            The final synthesized answer

        Raises:
            Exception: If graph execution fails
        """
        self.on_start(input_data)

        try:
            state = {
                "input_task": input_data,
                "available_modules": self.reasoning_modules,
                "selected_modules": [],
                "adapted_modules": [],
                "reasoning_plan": [],
                "plan_index": 0,
                "step_results": [],
                "done_with_plan": False,
                "final_answer": None,
                "error": None
            }

            final_state = self.graph.invoke(state)

            if final_state.get("error"):
                raise Exception(final_state["error"])

            result = final_state["final_answer"]
            self.on_finish(result)
            return result

        except Exception as e:
            self.on_error(e)
            raise

    def _discover_modules(self, state: Dict) -> Dict:
        """Discover and select relevant reasoning modules.

        Uses LLM to analyze the task and select the most appropriate
        reasoning strategies from the module library.

        Args:
            state: Current state with available_modules

        Returns:
            Updated state with selected_modules
        """
        if state.get("error"):
            return state

        try:
            prompt_data = self._load_prompt("DiscoverModules")
            discovery_llm: BaseChatModel = self._get_llm("thinking")

            # Format module library
            modules_text = self._format_modules(state["available_modules"])

            # Build messages
            system_prompt = prompt_data["system"]
            user_prompt = prompt_data["user"].format(
                task=state["input_task"],
                modules=modules_text,
                max_modules=self.max_selected_modules
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # Get module selection
            response = discovery_llm.invoke(messages)
            selection_text = response.content

            # Parse selected modules
            selected = self._parse_module_selection(
                selection_text,
                state["available_modules"]
            )

            state["selected_modules"] = selected

        except Exception as e:
            state["error"] = f"Module discovery error: {str(e)}"

        return state

    def _format_modules(self, modules: List[Dict[str, str]]) -> str:
        """Format reasoning modules for prompt.

        Args:
            modules: List of module dictionaries

        Returns:
            Formatted string describing modules
        """
        lines = []
        for i, module in enumerate(modules, 1):
            lines.append(f"{i}. **{module['name']}**: {module['description']}")

        return "\n".join(lines)

    def _parse_module_selection(
        self,
        selection_text: str,
        available_modules: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Parse LLM output to extract selected modules.

        Expected format:
            SELECTED: break_down_problem
            SELECTED: first_principles
            SELECTED: step_by_step

        Args:
            selection_text: LLM output
            available_modules: Available module library

        Returns:
            List of selected module dictionaries
        """
        selected = []
        module_dict = {m["name"]: m for m in available_modules}

        for line in selection_text.split("\n"):
            line = line.strip()
            if line.startswith("SELECTED:"):
                module_name = line.split(":", 1)[1].strip()
                if module_name in module_dict:
                    selected.append(module_dict[module_name])

        # Fallback: select first few modules if parsing failed
        if not selected and available_modules:
            selected = available_modules[:min(self.max_selected_modules, len(available_modules))]

        return selected

    def _adapt_modules(self, state: Dict) -> Dict:
        """Adapt selected modules to the specific task.

        Customizes the generic reasoning modules with task-specific details.

        Args:
            state: Current state with selected_modules

        Returns:
            Updated state with adapted_modules
        """
        if state.get("error"):
            return state

        try:
            prompt_data = self._load_prompt("AdaptModules")
            adaptation_llm: BaseChatModel = self._get_llm("thinking")

            selected_modules = state["selected_modules"]
            adapted = []

            for module in selected_modules:
                # Build messages for adaptation
                system_prompt = prompt_data["system"]
                user_prompt = prompt_data["user"].format(
                    task=state["input_task"],
                    module_name=module["name"],
                    module_description=module["description"],
                    module_template=module["template"]
                )

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ]

                # Get adapted module
                response = adaptation_llm.invoke(messages)
                adapted_text = response.content

                # Store adapted module
                adapted_module = {
                    "original_name": module["name"],
                    "adapted_strategy": adapted_text.strip()
                }
                adapted.append(adapted_module)

            state["adapted_modules"] = adapted

        except Exception as e:
            state["error"] = f"Module adaptation error: {str(e)}"

        return state

    def _plan_reasoning(self, state: Dict) -> Dict:
        """Create step-by-step reasoning plan using adapted modules.

        Args:
            state: Current state with adapted_modules

        Returns:
            Updated state with reasoning_plan
        """
        if state.get("error"):
            return state

        try:
            prompt_data = self._load_prompt("PlanReasoning")
            planning_llm: BaseChatModel = self._get_llm("thinking")

            # Format adapted modules
            modules_text = self._format_adapted_modules(state["adapted_modules"])

            # Build messages
            system_prompt = prompt_data["system"]
            user_prompt = prompt_data["user"].format(
                task=state["input_task"],
                adapted_modules=modules_text
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # Get reasoning plan
            response = planning_llm.invoke(messages)
            plan_text = response.content

            # Parse plan into steps
            plan = self._parse_reasoning_plan(plan_text)

            state["reasoning_plan"] = plan
            state["plan_index"] = 0

        except Exception as e:
            state["error"] = f"Planning error: {str(e)}"

        return state

    def _format_adapted_modules(self, adapted_modules: List[Dict[str, str]]) -> str:
        """Format adapted modules for planning prompt.

        Args:
            adapted_modules: List of adapted modules

        Returns:
            Formatted string
        """
        lines = []
        for i, module in enumerate(adapted_modules, 1):
            lines.append(f"Module {i} ({module['original_name']}):")
            lines.append(f"{module['adapted_strategy']}")
            lines.append("")

        return "\n".join(lines)

    def _parse_reasoning_plan(self, plan_text: str) -> List[Dict[str, str]]:
        """Parse reasoning plan into steps.

        Expected format:
            STEP 1: Description of first step
            STEP 2: Description of second step

        Args:
            plan_text: LLM output

        Returns:
            List of step dictionaries
        """
        steps = []

        for line in plan_text.split("\n"):
            line = line.strip()
            if line.startswith("STEP"):
                # Extract step description
                if ":" in line:
                    description = line.split(":", 1)[1].strip()
                    steps.append({"description": description})

        # Fallback: create single step if parsing failed
        if not steps:
            steps = [{"description": f"Apply reasoning to solve: {plan_text[:100]}"}]

        return steps

    def _execute_step(self, state: Dict) -> Dict:
        """Execute one reasoning step from the plan.

        Args:
            state: Current state with reasoning_plan and plan_index

        Returns:
            Updated state with updated plan_index and step_results
        """
        if state.get("error"):
            return state

        try:
            plan = state["reasoning_plan"]
            index = state["plan_index"]

            if index >= len(plan):
                return state

            current_step = plan[index]

            # Execute this reasoning step
            prompt_data = self._load_prompt("ExecuteStep")
            execution_llm: BaseChatModel = self._get_llm("execution")

            # Get previous results for context
            previous_results = "\n".join(state["step_results"]) if state["step_results"] else "None yet"

            # Build messages
            system_prompt = prompt_data["system"]
            user_prompt = prompt_data["user"].format(
                task=state["input_task"],
                step_description=current_step["description"],
                previous_results=previous_results
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # Execute step
            response = execution_llm.invoke(messages)
            step_result = response.content

            # Store result
            state["step_results"].append(f"Step {index + 1}: {step_result}")
            state["plan_index"] += 1

        except Exception as e:
            state["error"] = f"Execution error at step {state['plan_index']}: {str(e)}"

        return state

    def _check_completion(self, state: Dict) -> Dict:
        """Check if all reasoning steps are complete.

        Args:
            state: Current state

        Returns:
            Updated state with done_with_plan flag
        """
        if state.get("error"):
            state["done_with_plan"] = True
            return state

        plan = state["reasoning_plan"]
        index = state["plan_index"]

        state["done_with_plan"] = index >= len(plan)

        return state

    def _route_after_check(self, state: Dict) -> str:
        """Route to either continue execution or synthesize output.

        Args:
            state: Current state

        Returns:
            "finish" if done, "continue" otherwise
        """
        if state.get("error") or state["done_with_plan"]:
            return "finish"
        return "continue"

    def _synthesize_output(self, state: Dict) -> Dict:
        """Synthesize final answer from all reasoning steps.

        Args:
            state: Current state with step_results

        Returns:
            Updated state with final_answer
        """
        if state.get("error"):
            state["final_answer"] = f"Error: {state['error']}"
            return state

        try:
            prompt_data = self._load_prompt("SynthesizeOutput")
            synthesis_llm: BaseChatModel = self._get_llm("thinking")

            # Format step results
            results_text = "\n\n".join(state["step_results"])

            # Build messages
            system_prompt = prompt_data["system"]
            user_prompt = prompt_data["user"].format(
                task=state["input_task"],
                reasoning_steps=results_text
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # Get final synthesis
            response = synthesis_llm.invoke(messages)
            state["final_answer"] = response.content

        except Exception as e:
            state["final_answer"] = f"Synthesis error: {str(e)}"

        return state
