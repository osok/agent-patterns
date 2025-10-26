"""REWOO (Reason Without Observation) Pattern Implementation.

The REWOO pattern separates planning from execution by using a Worker LLM to create
a plan with placeholders, then a Solver executes the tools, and finally the Worker
integrates the real results. This reduces costs by minimizing expensive LLM calls.

Reference: https://arxiv.org/abs/2305.18323
"""

from typing import Any, Callable, Dict, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent_patterns.core.base_agent import BaseAgent


class REWOOAgent(BaseAgent):
    """REWOO agent that separates reasoning (Worker) from execution (Solver).

    This pattern is cost-effective for complex tasks requiring multiple tool calls,
    as it minimizes expensive LLM usage by planning with placeholders and only
    integrating actual results at the end.

    Workflow:
        1. Worker Plan: LLM creates plan with placeholders for results
        2. Dispatch: Prepare solver requests
        3. Solver Execute: Run all tools (can be parallelized)
        4. Collect Results: Gather all solver outputs
        5. Worker Integrate: LLM combines results into final answer

    Args:
        llm_configs: Dictionary mapping role names to LLM configuration
        tools: Dictionary mapping tool names to callable functions
        solver_llm_role: Role name for solver LLM (default: "solver")
        prompt_dir: Directory containing prompt templates (default: "prompts")

    Example:
        >>> def search_tool(query: str) -> str:
        ...     return f"Search results for: {query}"
        >>>
        >>> agent = REWOOAgent(
        ...     llm_configs={
        ...         "thinking": {"provider": "openai", "model": "gpt-4"},
        ...         "solver": {"provider": "openai", "model": "gpt-3.5-turbo"}
        ...     },
        ...     tools={"search_tool": search_tool}
        ... )
        >>> result = agent.run("Find CEO of OpenAI and their latest announcement")
    """

    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        tools: Optional[Dict[str, Callable]] = None,
        solver_llm_role: str = "solver",
        prompt_dir: str = "prompts",
        custom_instructions: Optional[str] = None,
        prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
    ):
        """Initialize the REWOO agent.

        Args:
            llm_configs: Dictionary mapping role names to LLM configuration
            tools: Dictionary mapping tool names to callable functions
            solver_llm_role: Role name for solver LLM
            prompt_dir: Directory containing prompt templates
            custom_instructions: Custom instructions appended to all system prompts
            prompt_overrides: Dictionary mapping step names to prompt overrides
        """
        self.tools = tools or {}
        self.solver_llm_role = solver_llm_role
        super().__init__(
            llm_configs=llm_configs,
            prompt_dir=prompt_dir,
            custom_instructions=custom_instructions,
            prompt_overrides=prompt_overrides
        )

    def build_graph(self) -> None:
        """Build the LangGraph StateGraph for the REWOO pattern.

        Creates a graph with the following nodes:
            - worker_plan: Creates plan with placeholders
            - dispatch_to_solvers: Prepares solver requests
            - solver_execute: Executes all tools
            - collect_solver_results: Gathers results
            - worker_integrate: Combines results into final answer
        """
        workflow = StateGraph(dict)

        # Add nodes
        workflow.add_node("worker_plan", self._worker_plan)
        workflow.add_node("dispatch_to_solvers", self._dispatch_to_solvers)
        workflow.add_node("solver_execute", self._solver_execute)
        workflow.add_node("collect_solver_results", self._collect_solver_results)
        workflow.add_node("worker_integrate", self._worker_integrate)

        # Set entry point
        workflow.set_entry_point("worker_plan")

        # Add edges (linear flow)
        workflow.add_edge("worker_plan", "dispatch_to_solvers")
        workflow.add_edge("dispatch_to_solvers", "solver_execute")
        workflow.add_edge("solver_execute", "collect_solver_results")
        workflow.add_edge("collect_solver_results", "worker_integrate")
        workflow.add_edge("worker_integrate", "__end__")

        self.graph: CompiledStateGraph = workflow.compile()

    def run(self, input_data: Any) -> Any:
        """Execute the REWOO workflow.

        Args:
            input_data: The user's task or query

        Returns:
            The final integrated answer

        Raises:
            Exception: If graph execution fails
        """
        self.on_start(input_data)

        try:
            state = {
                "input_task": input_data,
                "worker_plan_template": "",  # Plan with placeholders
                "solver_requests": [],  # List of tool calls to make
                "solver_results": {},  # Mapping of placeholders to results
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

    def _worker_plan(self, state: Dict) -> Dict:
        """Worker LLM creates a plan with placeholders.

        The Worker (expensive LLM) analyzes the task and creates a plan
        describing what needs to be done, using placeholders like {result1}
        for solver outputs it hasn't seen yet.

        Args:
            state: Current state containing input_task

        Returns:
            Updated state with worker_plan_template and solver_requests
        """
        try:
            prompt_data = self._load_prompt("WorkerPlan")
            worker_llm: BaseChatModel = self._get_llm("thinking")

            # Format available tools
            tools_description = self._format_tools()

            # Build messages
            system_prompt = prompt_data["system"]
            user_prompt = prompt_data["user"].format(
                task=state["input_task"],
                tools=tools_description
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # Get plan from Worker LLM
            response = worker_llm.invoke(messages)
            plan_text = response.content

            # Parse the plan into template and solver requests
            plan_template, solver_requests = self._parse_worker_plan(plan_text)

            state["worker_plan_template"] = plan_template
            state["solver_requests"] = solver_requests

        except Exception as e:
            state["error"] = f"Worker plan error: {str(e)}"

        return state

    def _format_tools(self) -> str:
        """Format available tools for inclusion in prompts.

        Returns:
            Formatted string describing available tools
        """
        if not self.tools:
            return "No tools available"

        lines = []
        for tool_name, tool_func in self.tools.items():
            doc = tool_func.__doc__ or "No description"
            lines.append(f"- **{tool_name}**: {doc.strip()}")

        return "\n".join(lines)

    def _parse_worker_plan(
        self,
        plan_text: str
    ) -> tuple[str, List[Dict[str, Any]]]:
        """Parse Worker's plan text into template and solver requests.

        Expected format from Worker LLM:
            PLAN: Find CEO of Company X -> {ceo_name}, then search for announcements by {ceo_name} -> {announcements}

            SOLVER: ceo_name
            TOOL: search_tool
            PARAMS: {"query": "CEO of Company X"}

            SOLVER: announcements
            TOOL: search_tool
            PARAMS: {"query": "latest announcements by {ceo_name}"}

        Args:
            plan_text: The plan generated by Worker LLM

        Returns:
            Tuple of (plan_template, solver_requests)
        """
        lines = plan_text.strip().split("\n")
        plan_template = ""
        solver_requests = []
        current_solver = {}

        for line in lines:
            line = line.strip()
            if not line:
                if current_solver and "placeholder" in current_solver:
                    solver_requests.append(current_solver)
                    current_solver = {}
                continue

            if line.startswith("PLAN:"):
                plan_template = line.split(":", 1)[1].strip()

            elif line.startswith("SOLVER:"):
                if current_solver and "placeholder" in current_solver:
                    solver_requests.append(current_solver)
                current_solver = {"placeholder": line.split(":", 1)[1].strip()}

            elif line.startswith("TOOL:"):
                current_solver["tool"] = line.split(":", 1)[1].strip()

            elif line.startswith("PARAMS:"):
                params_str = line.split(":", 1)[1].strip()
                try:
                    import json
                    current_solver["params"] = json.loads(params_str)
                except:
                    current_solver["params"] = {"raw": params_str}

        # Add last solver if exists
        if current_solver and "placeholder" in current_solver:
            solver_requests.append(current_solver)

        # Fallback if parsing failed
        if not plan_template:
            plan_template = "Execute task: " + plan_text[:100]

        if not solver_requests and self.tools:
            # Create a default solver request
            tool_name = list(self.tools.keys())[0]
            solver_requests = [{
                "placeholder": "result1",
                "tool": tool_name,
                "params": {}
            }]

        return plan_template, solver_requests

    def _dispatch_to_solvers(self, state: Dict) -> Dict:
        """Prepare solver requests for execution.

        This step could coordinate parallel execution in advanced implementations.
        For now, it's a pass-through that validates requests.

        Args:
            state: Current state with solver_requests

        Returns:
            Updated state
        """
        if state.get("error"):
            return state

        # Validate solver requests
        solver_requests = state.get("solver_requests", [])

        for req in solver_requests:
            if "tool" not in req:
                state["error"] = f"Invalid solver request: missing tool in {req}"
                return state

            if "placeholder" not in req:
                state["error"] = f"Invalid solver request: missing placeholder in {req}"
                return state

        return state

    def _solver_execute(self, state: Dict) -> Dict:
        """Execute all solver requests using tools or solver LLM.

        The Solver can be a cheaper LLM or direct tool calls. This step
        runs all the planned operations and stores results.

        Args:
            state: Current state with solver_requests

        Returns:
            Updated state with solver_results populated
        """
        if state.get("error"):
            return state

        try:
            solver_requests = state["solver_requests"]
            solver_results = state["solver_results"]

            # Execute each solver request
            for req in solver_requests:
                placeholder = req["placeholder"]
                tool_name = req["tool"]
                params = req.get("params", {})

                # Resolve any placeholders in params
                resolved_params = self._resolve_params(params, solver_results)

                # Execute the tool
                result = self._call_solver(tool_name, resolved_params)

                # Store result
                solver_results[placeholder] = result

            state["solver_results"] = solver_results

        except Exception as e:
            state["error"] = f"Solver execution error: {str(e)}"

        return state

    def _resolve_params(
        self,
        params: Dict[str, Any],
        solver_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve placeholder references in parameters.

        If a parameter value contains {placeholder}, replace it with
        the actual result from a previous solver execution.

        Args:
            params: Original parameters
            solver_results: Results from previous solvers

        Returns:
            Parameters with placeholders resolved
        """
        resolved = {}

        for key, value in params.items():
            if isinstance(value, str):
                # Replace all {placeholder} patterns
                resolved_value = value
                for placeholder, result in solver_results.items():
                    pattern = f"{{{placeholder}}}"
                    if pattern in resolved_value:
                        resolved_value = resolved_value.replace(pattern, str(result))
                resolved[key] = resolved_value
            else:
                resolved[key] = value

        return resolved

    def _call_solver(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a single solver request.

        Can use either a direct tool call or a solver LLM depending on
        the tool type and configuration.

        Args:
            tool_name: Name of the tool to execute
            params: Parameters for the tool

        Returns:
            Result from the tool or solver LLM

        Raises:
            ValueError: If tool is not found
        """
        # First try direct tool execution
        if tool_name in self.tools:
            tool_func = self.tools[tool_name]
            try:
                result = tool_func(**params)
                return result
            except Exception as e:
                return f"Error executing {tool_name}: {str(e)}"

        # Fallback: use solver LLM if configured
        if self.solver_llm_role in self.llm_configs:
            try:
                solver_llm = self._get_llm(self.solver_llm_role)
                prompt = f"Execute {tool_name} with parameters: {params}"
                response = solver_llm.invoke([HumanMessage(content=prompt)])
                return response.content
            except Exception as e:
                return f"Solver LLM error for {tool_name}: {str(e)}"

        return f"Error: Tool '{tool_name}' not found"

    def _collect_solver_results(self, state: Dict) -> Dict:
        """Collect and validate all solver results.

        In parallel implementations, this would wait for all solvers to complete.
        For now, results are already collected synchronously.

        Args:
            state: Current state with solver_results

        Returns:
            Updated state
        """
        if state.get("error"):
            return state

        # Verify all placeholders have results
        solver_requests = state.get("solver_requests", [])
        solver_results = state.get("solver_results", {})

        missing = []
        for req in solver_requests:
            placeholder = req["placeholder"]
            if placeholder not in solver_results:
                missing.append(placeholder)

        if missing:
            state["error"] = f"Missing results for placeholders: {missing}"

        return state

    def _worker_integrate(self, state: Dict) -> Dict:
        """Worker LLM integrates solver results into final answer.

        The Worker now sees the actual results and combines them with
        the original plan to produce a coherent final answer.

        Args:
            state: Current state with plan_template and solver_results

        Returns:
            Updated state with final_answer
        """
        if state.get("error"):
            state["final_answer"] = f"Error: {state['error']}"
            return state

        try:
            prompt_data = self._load_prompt("WorkerIntegrate")
            worker_llm: BaseChatModel = self._get_llm("thinking")

            # Fill in the plan template with actual results
            plan_template = state["worker_plan_template"]
            solver_results = state["solver_results"]

            filled_plan = plan_template
            for placeholder, result in solver_results.items():
                pattern = f"{{{placeholder}}}"
                filled_plan = filled_plan.replace(pattern, str(result))

            # Build messages for integration
            system_prompt = prompt_data["system"]
            user_prompt = prompt_data["user"].format(
                task=state["input_task"],
                plan=filled_plan,
                results=self._format_results(solver_results)
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # Get final answer from Worker LLM
            response = worker_llm.invoke(messages)
            state["final_answer"] = response.content

        except Exception as e:
            state["final_answer"] = f"Integration error: {str(e)}"

        return state

    def _format_results(self, solver_results: Dict[str, Any]) -> str:
        """Format solver results for the integration prompt.

        Args:
            solver_results: Dictionary of placeholder -> result

        Returns:
            Formatted string of results
        """
        lines = []
        for placeholder, result in solver_results.items():
            lines.append(f"- **{placeholder}**: {result}")

        return "\n".join(lines)
