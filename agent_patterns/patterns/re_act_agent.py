"""
ReAct (Reason + Act) Agent Pattern.

This module implements the ReAct pattern which iteratively reasons about a problem
and takes actions (tool calls) until arriving at a final answer.
"""

from typing import Any, Callable, Dict, List, Tuple, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from agent_patterns.core.base_agent import BaseAgent


class ReActAgent(BaseAgent):
    """
    ReAct (Reason + Act) agent pattern.

    This agent alternates between reasoning (thinking about what to do next) and
    acting (calling tools to gather information or perform actions). It continues
    this cycle until it determines it has enough information to provide a final answer.

    State Keys:
        - input (str): The user's query or problem statement
        - thought (str): Current reasoning step
        - action (Dict): Action to execute {"tool_name": str, "tool_input": Any}
        - observation (Any): Result from executing the action
        - intermediate_steps (List[Tuple]): History of (thought, action, observation)
        - final_answer (str): The final answer to return
        - iteration_count (int): Number of reasoning cycles performed
        - max_iterations (int): Maximum allowed iterations

    Example:
        >>> tools = {"search": search_func, "calculator": calc_func}
        >>> agent = ReActAgent(llm_configs=configs, tools=tools, max_iterations=5)
        >>> result = agent.run("What is the weather in Paris?")
    """

    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        tools: Optional[Dict[str, Callable]] = None,
        max_iterations: int = 5,
        prompt_dir: str = "prompts",
        custom_instructions: Optional[str] = None,
        prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
    ):
        """
        Initialize the ReAct agent.

        Args:
            llm_configs: Configuration for LLM roles
            tools: Dictionary mapping tool names to callable functions
            max_iterations: Maximum number of thought-action cycles
            prompt_dir: Directory containing prompt templates
            custom_instructions: Custom instructions appended to all system prompts
            prompt_overrides: Dictionary mapping step names to prompt overrides
        """
        self.tools = tools or {}
        self.max_iterations = max_iterations
        super().__init__(
            llm_configs=llm_configs,
            prompt_dir=prompt_dir,
            custom_instructions=custom_instructions,
            prompt_overrides=prompt_overrides
        )

    def build_graph(self) -> None:
        """
        Build the ReAct state graph.

        Graph structure:
            thought_step -> action_step -> observation_step -> decision
            decision -> thought_step (if continue) or final_answer (if done)
        """
        # Initialize state graph with state type annotation
        workflow = StateGraph(dict)

        # Add nodes
        workflow.add_node("thought_step", self._generate_thought_and_action)
        workflow.add_node("action_step", self._execute_action)
        workflow.add_node("observation_step", self._observation_handler)
        workflow.add_node("final_answer", self._format_final_answer)

        # Set entry point
        workflow.set_entry_point("thought_step")

        # Add edges
        workflow.add_edge("thought_step", "action_step")
        workflow.add_edge("action_step", "observation_step")

        # Conditional edge from observation_step
        workflow.add_conditional_edges(
            "observation_step",
            self._should_continue,
            {
                "continue": "thought_step",
                "finish": "final_answer",
            },
        )

        # Final answer goes to END
        workflow.add_edge("final_answer", END)

        # Compile the graph
        self.graph = workflow.compile()

    def run(self, input_data: str) -> str:
        """
        Execute the ReAct pattern on the given input.

        Args:
            input_data: The user's query or problem statement

        Returns:
            The final answer after reasoning and acting

        Raises:
            ValueError: If the graph hasn't been built
        """
        if self.graph is None:
            raise ValueError("Graph has not been built. Call build_graph() first.")

        # Initialize state
        initial_state = {
            "input": input_data,
            "thought": "",
            "action": {},
            "observation": None,
            "intermediate_steps": [],
            "final_answer": None,
            "iteration_count": 0,
            "max_iterations": self.max_iterations,
        }

        # Invoke lifecycle hook
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

    def _generate_thought_and_action(self, state: Dict) -> Dict:
        """
        Generate the next thought and action using the LLM.

        This step reasons about the current state and decides what action to take next.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with thought and action
        """
        # Increment iteration counter
        state["iteration_count"] = state.get("iteration_count", 0) + 1

        # Load prompts
        prompts = self._load_prompt("ThoughtStep")
        system_prompt = prompts.get("system", "You are a helpful AI assistant.")
        user_prompt_template = prompts.get(
            "user",
            "Task: {input}\n\nPrevious steps: {history}\n\nWhat should I do next?",
        )

        # Format history
        history = self._format_history(state.get("intermediate_steps", []))

        # Format user prompt
        user_prompt = user_prompt_template.format(
            input=state["input"],
            history=history,
            available_tools=", ".join(self.tools.keys()) if self.tools else "None",
        )

        # Get LLM
        llm = self._get_llm("thinking")

        # Generate response
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = llm.invoke(messages)
        response_text = response.content

        # Parse response into thought and action
        thought, action = self._parse_llm_response(response_text)

        # Update state
        state["thought"] = thought
        state["action"] = action

        return state

    def _execute_action(self, state: Dict) -> Dict:
        """
        Execute the action specified in the state.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with observation from action execution
        """
        action = state.get("action", {})
        tool_name = action.get("tool_name", "")
        tool_input = action.get("tool_input", "")

        # Check if this is a final answer action
        if tool_name.lower() == "final_answer":
            state["observation"] = "FINAL_ANSWER"
            state["final_answer"] = tool_input
            return state

        # Execute the tool
        if tool_name in self.tools:
            try:
                observation = self.tools[tool_name](tool_input)
            except Exception as e:
                observation = f"Error executing tool {tool_name}: {str(e)}"
        else:
            observation = f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"

        state["observation"] = observation
        return state

    def _observation_handler(self, state: Dict) -> Dict:
        """
        Process the observation and update intermediate steps.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with observation recorded in history
        """
        # Record this step in history
        step = (
            state.get("thought", ""),
            state.get("action", {}),
            state.get("observation"),
        )
        state["intermediate_steps"].append(step)

        return state

    def _should_continue(self, state: Dict) -> str:
        """
        Decide whether to continue the ReAct loop or finish.

        Args:
            state: Current state dictionary

        Returns:
            "continue" to keep reasoning, "finish" to stop
        """
        # Check if we have a final answer
        if state.get("observation") == "FINAL_ANSWER":
            return "finish"

        # Check if we've hit max iterations
        if state.get("iteration_count", 0) >= state.get("max_iterations", 5):
            # Force a final answer
            state["final_answer"] = self._generate_fallback_answer(state)
            return "finish"

        # Check if the thought indicates we're done
        thought = state.get("thought", "").lower()
        if "final answer" in thought or "conclude" in thought:
            return "finish"

        return "continue"

    def _format_final_answer(self, state: Dict) -> Dict:
        """
        Format the final answer for the user.

        Args:
            state: Current state dictionary

        Returns:
            Updated state with formatted final answer
        """
        # If we don't have a final answer yet, generate one from the history
        if not state.get("final_answer"):
            state["final_answer"] = self._generate_fallback_answer(state)

        return state

    def _parse_llm_response(self, response: str) -> Tuple[str, Dict]:
        """
        Parse the LLM response into thought and action components.

        Expected format:
            Thought: <reasoning>
            Action: <tool_name>
            Action Input: <input>

        Args:
            response: Raw LLM response text

        Returns:
            Tuple of (thought, action_dict)
        """
        thought = ""
        action = {"tool_name": "", "tool_input": ""}

        lines = response.strip().split("\n")
        current_section = None

        for line in lines:
            line = line.strip()
            if line.lower().startswith("thought:"):
                current_section = "thought"
                thought = line.split(":", 1)[1].strip()
            elif line.lower().startswith("action:"):
                current_section = "action"
                action["tool_name"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("action input:"):
                current_section = "action_input"
                action["tool_input"] = line.split(":", 1)[1].strip()
            elif current_section == "thought" and line:
                thought += " " + line
            elif current_section == "action_input" and line:
                action["tool_input"] += " " + line

        return thought, action

    def _format_history(self, steps: List[Tuple]) -> str:
        """
        Format intermediate steps into a readable history string.

        Args:
            steps: List of (thought, action, observation) tuples

        Returns:
            Formatted history string
        """
        if not steps:
            return "No previous steps."

        history_lines = []
        for i, (thought, action, observation) in enumerate(steps, 1):
            history_lines.append(f"Step {i}:")
            history_lines.append(f"  Thought: {thought}")
            history_lines.append(f"  Action: {action.get('tool_name', 'N/A')}")
            history_lines.append(f"  Action Input: {action.get('tool_input', 'N/A')}")
            history_lines.append(f"  Observation: {observation}")

        return "\n".join(history_lines)

    def _generate_fallback_answer(self, state: Dict) -> str:
        """
        Generate a fallback answer when max iterations are reached.

        Args:
            state: Current state dictionary

        Returns:
            Fallback answer string
        """
        last_observation = None
        if state.get("intermediate_steps"):
            _, _, last_observation = state["intermediate_steps"][-1]

        if last_observation:
            return f"Based on my investigation: {last_observation}"
        else:
            return f"I was unable to find a definitive answer to: {state.get('input', 'the query')}"

    def add_tool(self, name: str, func: Callable) -> None:
        """
        Add a tool to the agent's toolbox.

        Args:
            name: Name of the tool
            func: Callable function that takes input and returns output
        """
        self.tools[name] = func

    def remove_tool(self, name: str) -> None:
        """
        Remove a tool from the agent's toolbox.

        Args:
            name: Name of the tool to remove

        Raises:
            KeyError: If the tool doesn't exist
        """
        del self.tools[name]

    def list_tools(self) -> List[str]:
        """
        Get a list of available tool names.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())
