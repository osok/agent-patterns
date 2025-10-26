"""LLMCompiler Pattern Implementation.

The LLMCompiler pattern treats the multi-tool workflow like a compiler, constructing
an execution graph (DAG) from the user task and available tools, then executing the
graph in an optimized order.

Reference: https://arxiv.org/abs/2312.04511
"""

from typing import Any, Callable, Dict, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent_patterns.core.base_agent import BaseAgent


class LLMCompilerAgent(BaseAgent):
    """LLMCompiler agent that creates and executes a DAG of tool calls.

    This pattern is useful for complex tasks requiring multiple tool calls that can
    potentially be executed in parallel based on their dependencies.

    Workflow:
        1. Planner: LLM generates an execution graph (DAG) of tool calls
        2. Executor: Runs nodes in topological order when dependencies are satisfied
        3. Check Completion: Determines if all nodes have been executed
        4. Synthesizer: Combines results into final answer

    Args:
        llm_configs: Dictionary mapping role names to LLM configuration
        tools: Dictionary mapping tool names to callable functions
        prompt_dir: Directory containing prompt templates (default: "prompts")

    Example:
        >>> def search_tool(query: str) -> str:
        ...     return f"Search results for: {query}"
        >>>
        >>> def calculator_tool(expression: str) -> float:
        ...     return eval(expression)
        >>>
        >>> agent = LLMCompilerAgent(
        ...     llm_configs={
        ...         "thinking": {"provider": "openai", "model": "gpt-4"},
        ...         "documentation": {"provider": "openai", "model": "gpt-4"}
        ...     },
        ...     tools={
        ...         "search_tool": search_tool,
        ...         "calculator_tool": calculator_tool
        ...     }
        ... )
        >>> result = agent.run("Find population of Tokyo and calculate double that number")
    """

    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        tools: Optional[Dict[str, Callable]] = None,
        prompt_dir: str = "prompts",
        custom_instructions: Optional[str] = None,
        prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
    ):
        """Initialize the LLMCompiler agent.

        Args:
            llm_configs: Dictionary mapping role names to LLM configuration
            tools: Dictionary mapping tool names to callable functions
            prompt_dir: Directory containing prompt templates
            custom_instructions: Custom instructions appended to all system prompts
            prompt_overrides: Dictionary mapping step names to prompt overrides
        """
        self.tools = tools or {}
        super().__init__(
            llm_configs=llm_configs,
            prompt_dir=prompt_dir,
            custom_instructions=custom_instructions,
            prompt_overrides=prompt_overrides
        )

    def build_graph(self) -> None:
        """Build the LangGraph StateGraph for the LLMCompiler pattern.

        Creates a graph with the following nodes:
            - planner_generate_graph: Creates execution DAG
            - executor_dispatch: Executes ready nodes
            - check_completion: Checks if all nodes are done
            - synthesize_result: Combines results into final answer
        """
        workflow = StateGraph(dict)

        # Add nodes
        workflow.add_node("planner_generate_graph", self._planner_generate_graph)
        workflow.add_node("executor_dispatch", self._executor_dispatch)
        workflow.add_node("check_completion", self._check_completion)
        workflow.add_node("synthesize_result", self._synthesize_result)

        # Set entry point
        workflow.set_entry_point("planner_generate_graph")

        # Add edges
        workflow.add_edge("planner_generate_graph", "executor_dispatch")
        workflow.add_edge("executor_dispatch", "check_completion")

        # Conditional edges for looping or finishing
        workflow.add_conditional_edges(
            "check_completion",
            self._route_after_check,
            {
                "continue": "executor_dispatch",
                "finish": "synthesize_result"
            }
        )

        # Synthesize is the final node
        workflow.add_edge("synthesize_result", "__end__")

        self.graph: CompiledStateGraph = workflow.compile()

    def run(self, input_data: Any) -> Any:
        """Execute the LLMCompiler workflow.

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
                "tool_schemas": self._define_tool_schemas(),
                "execution_graph": None,  # The DAG structure
                "node_results": {},  # Results keyed by node_id
                "graph_done": False,
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

    def _define_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Define formal schemas for available tools.

        Provides tool signatures to the planner LLM so it can determine
        dependencies and construct the execution graph.

        Returns:
            Dictionary mapping tool names to their schemas
        """
        schemas = {}

        for tool_name, tool_func in self.tools.items():
            # Extract basic schema from function signature
            # In production, this could be more sophisticated using inspect module
            schemas[tool_name] = {
                "name": tool_name,
                "description": tool_func.__doc__ or f"Tool: {tool_name}",
                "callable": tool_func
            }

        return schemas

    def _planner_generate_graph(self, state: Dict) -> Dict:
        """Generate execution graph (DAG) using planner LLM.

        The planner analyzes the task and available tools to create a directed
        acyclic graph of tool calls with dependencies.

        Args:
            state: Current state containing input_task and tool_schemas

        Returns:
            Updated state with execution_graph populated
        """
        try:
            prompt_data = self._load_prompt("PlanGraph")
            planner_llm: BaseChatModel = self._get_llm("thinking")

            # Format tool schemas for the prompt
            tools_description = self._format_tool_schemas(state["tool_schemas"])

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

            # Get plan from LLM
            response = planner_llm.invoke(messages)
            plan_text = response.content

            # Parse the plan into a graph structure
            execution_graph = self._parse_plan_to_graph(plan_text, state["tool_schemas"])

            state["execution_graph"] = execution_graph

        except Exception as e:
            state["error"] = f"Planner error: {str(e)}"
            state["graph_done"] = True  # Skip to end

        return state

    def _format_tool_schemas(self, tool_schemas: Dict[str, Dict[str, Any]]) -> str:
        """Format tool schemas for inclusion in prompts.

        Args:
            tool_schemas: Dictionary of tool schemas

        Returns:
            Formatted string describing available tools
        """
        lines = []
        for tool_name, schema in tool_schemas.items():
            lines.append(f"- **{tool_name}**: {schema['description']}")

        return "\n".join(lines)

    def _parse_plan_to_graph(
        self,
        plan_text: str,
        tool_schemas: Dict[str, Dict[str, Any]]
    ) -> Dict[str, List[Dict]]:
        """Parse LLM-generated plan text into a graph structure.

        Expected format from LLM:
            NODE: node1
            TOOL: search_tool
            ARGS: {"query": "Tokyo population"}
            DEPENDS_ON: []

            NODE: node2
            TOOL: calculator_tool
            ARGS: {"expression": "#node1 * 2"}
            DEPENDS_ON: [node1]

        Args:
            plan_text: The plan generated by the LLM
            tool_schemas: Available tool schemas

        Returns:
            Execution graph with list of nodes
        """
        nodes = []
        current_node = {}

        for line in plan_text.strip().split("\n"):
            line = line.strip()
            if not line:
                if current_node:
                    nodes.append(current_node)
                    current_node = {}
                continue

            if line.startswith("NODE:"):
                if current_node:
                    nodes.append(current_node)
                current_node = {"id": line.split(":", 1)[1].strip()}

            elif line.startswith("TOOL:"):
                current_node["tool"] = line.split(":", 1)[1].strip()

            elif line.startswith("ARGS:"):
                args_str = line.split(":", 1)[1].strip()
                # Simple parsing - in production use JSON parsing
                try:
                    import json
                    current_node["args"] = json.loads(args_str)
                except:
                    current_node["args"] = {"raw": args_str}

            elif line.startswith("DEPENDS_ON:"):
                deps_str = line.split(":", 1)[1].strip()
                if deps_str == "[]" or not deps_str:
                    current_node["depends_on"] = []
                else:
                    # Parse list of dependencies
                    deps = [d.strip() for d in deps_str.strip("[]").split(",") if d.strip()]
                    current_node["depends_on"] = deps

        # Add last node if exists
        if current_node:
            nodes.append(current_node)

        # Fallback: if parsing failed, create single node
        if not nodes:
            nodes = [{
                "id": "node1",
                "tool": list(tool_schemas.keys())[0] if tool_schemas else "default",
                "args": {},
                "depends_on": []
            }]

        return {"nodes": nodes}

    def _executor_dispatch(self, state: Dict) -> Dict:
        """Execute ready nodes whose dependencies are satisfied.

        Iterates through all nodes in the execution graph and executes any
        node whose dependencies have all completed.

        Args:
            state: Current state with execution_graph and node_results

        Returns:
            Updated state with new node_results
        """
        if state.get("error"):
            return state

        try:
            graph = state["execution_graph"]
            node_results = state["node_results"]

            # Find nodes that can be executed
            for node in graph["nodes"]:
                node_id = node["id"]

                # Skip if already executed
                if node_id in node_results:
                    continue

                # Check if all dependencies are satisfied
                dependencies = node.get("depends_on", [])
                if all(dep in node_results for dep in dependencies):
                    # Execute this node
                    result = self._execute_tool(
                        node["tool"],
                        node.get("args", {}),
                        node_results
                    )
                    node_results[node_id] = result

            state["node_results"] = node_results

        except Exception as e:
            state["error"] = f"Executor error: {str(e)}"
            state["graph_done"] = True

        return state

    def _check_completion(self, state: Dict) -> Dict:
        """Check if all nodes in the graph have been executed.

        Args:
            state: Current state with execution_graph and node_results

        Returns:
            Updated state with graph_done flag
        """
        if state.get("error"):
            state["graph_done"] = True
            return state

        graph = state["execution_graph"]
        node_results = state["node_results"]

        # Get all node IDs
        all_ids = [n["id"] for n in graph["nodes"]]

        # Check if all nodes have results
        state["graph_done"] = all(node_id in node_results for node_id in all_ids)

        return state

    def _route_after_check(self, state: Dict) -> str:
        """Route to either continue execution or synthesize results.

        Args:
            state: Current state

        Returns:
            "finish" if done, "continue" if more nodes to execute
        """
        if state["graph_done"]:
            return "finish"
        return "continue"

    def _synthesize_result(self, state: Dict) -> Dict:
        """Synthesize final answer from all node results.

        Uses the documentation LLM to combine intermediate results into
        a coherent final answer.

        Args:
            state: Current state with node_results

        Returns:
            Updated state with final_answer
        """
        if state.get("error"):
            state["final_answer"] = f"Error: {state['error']}"
            return state

        try:
            prompt_data = self._load_prompt("Synthesize")
            synthesis_llm: BaseChatModel = self._get_llm("documentation")

            # Format node results
            results_text = self._format_node_results(
                state["execution_graph"],
                state["node_results"]
            )

            # Build messages
            system_prompt = prompt_data["system"]
            user_prompt = prompt_data["user"].format(
                task=state["input_task"],
                results=results_text
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # Get synthesis from LLM
            response = synthesis_llm.invoke(messages)
            state["final_answer"] = response.content

        except Exception as e:
            state["final_answer"] = f"Synthesis error: {str(e)}"

        return state

    def _format_node_results(
        self,
        execution_graph: Dict,
        node_results: Dict[str, Any]
    ) -> str:
        """Format node results for synthesis prompt.

        Args:
            execution_graph: The execution graph
            node_results: Results from executed nodes

        Returns:
            Formatted string of results
        """
        lines = []
        for node in execution_graph["nodes"]:
            node_id = node["id"]
            result = node_results.get(node_id, "No result")
            lines.append(f"**{node_id}** ({node['tool']}): {result}")

        return "\n".join(lines)

    def _execute_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        node_results: Dict[str, Any]
    ) -> Any:
        """Execute a single tool with given arguments.

        Args:
            tool_name: Name of the tool to execute
            args: Arguments for the tool
            node_results: Previous node results (for dependency resolution)

        Returns:
            Result from tool execution

        Raises:
            ValueError: If tool is not found
        """
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found"

        tool_func = self.tools[tool_name]

        # Resolve any references to previous node results
        resolved_args = self._resolve_args(args, node_results)

        # Execute tool
        try:
            result = tool_func(**resolved_args)
            return result
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"

    def _resolve_args(
        self,
        args: Dict[str, Any],
        node_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve argument references to previous node results.

        If an argument value starts with '#', it's treated as a reference
        to a previous node's result (e.g., "#node1").

        Args:
            args: Original arguments
            node_results: Results from previous nodes

        Returns:
            Arguments with references resolved
        """
        resolved = {}

        for key, value in args.items():
            if isinstance(value, str) and value.startswith("#"):
                # Reference to another node
                node_id = value[1:]  # Remove '#'
                resolved[key] = node_results.get(node_id, value)
            else:
                resolved[key] = value

        return resolved
