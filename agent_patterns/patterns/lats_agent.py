"""LATS (Language Agent Tree Search) Pattern Implementation.

The LATS pattern performs tree search over possible reasoning paths using techniques
inspired by Monte Carlo Tree Search (MCTS). Instead of following a single chain,
the agent explores multiple paths, evaluates them, and uses backpropagation to
select the best solution.

Reference: https://arxiv.org/abs/2310.04406
"""

import math
from typing import Any, Callable, Dict, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent_patterns.core.base_agent import BaseAgent


class TreeNode:
    """Represents a node in the LATS search tree.

    Attributes:
        state_description: Description of the state at this node
        action: Action taken to reach this node
        parent: Parent node reference
        children: List of child nodes
        visits: Number of times this node was visited
        value: Cumulative value/score of this node
        is_terminal: Whether this is a terminal/solution node
    """

    def __init__(
        self,
        state_description: str,
        action: Optional[str] = None,
        parent: Optional['TreeNode'] = None
    ):
        """Initialize a tree node.

        Args:
            state_description: Description of this state
            action: Action taken to reach this state
            parent: Parent node reference
        """
        self.state_description = state_description
        self.action = action
        self.parent = parent
        self.children: List[TreeNode] = []
        self.visits = 0
        self.value = 0.0
        self.is_terminal = False

    def ucb_score(self, exploration_weight: float = 1.41) -> float:
        """Calculate Upper Confidence Bound (UCB) score for node selection.

        Args:
            exploration_weight: Weight for exploration vs exploitation

        Returns:
            UCB score for this node
        """
        if self.visits == 0:
            return float('inf')  # Unvisited nodes have highest priority

        if self.parent is None:
            return self.value / self.visits

        exploitation = self.value / self.visits
        exploration = exploration_weight * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )

        return exploitation + exploration

    def average_value(self) -> float:
        """Calculate average value of this node.

        Returns:
            Average value across all visits
        """
        if self.visits == 0:
            return 0.0
        return self.value / self.visits


class LATSAgent(BaseAgent):
    """LATS agent that performs tree search over reasoning paths.

    This pattern explores multiple solution paths simultaneously, evaluating
    and backpropagating scores to find the best approach.

    Workflow:
        1. Select: Choose promising node using UCB
        2. Expand: Generate possible next steps
        3. Evaluate: Score each new node
        4. Backpropagate: Update ancestor values
        5. Repeat until budget exhausted
        6. Choose best path and generate final answer

    Args:
        llm_configs: Dictionary mapping role names to LLM configuration
        tools: Dictionary mapping tool names to callable functions
        max_iterations: Maximum search iterations (default: 10)
        exploration_weight: UCB exploration parameter (default: 1.41)
        num_expansions: Number of children to generate per expansion (default: 3)
        prompt_dir: Directory containing prompt templates (default: "prompts")

    Example:
        >>> agent = LATSAgent(
        ...     llm_configs={
        ...         "thinking": {"provider": "openai", "model": "gpt-4"},
        ...         "evaluation": {"provider": "openai", "model": "gpt-4"}
        ...     },
        ...     max_iterations=15,
        ...     num_expansions=3
        ... )
        >>> result = agent.run("Solve this complex reasoning problem...")
    """

    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, Any]],
        tools: Optional[Dict[str, Callable]] = None,
        max_iterations: int = 10,
        exploration_weight: float = 1.41,
        num_expansions: int = 3,
        prompt_dir: str = "prompts",
        custom_instructions: Optional[str] = None,
        prompt_overrides: Optional[Dict[str, Dict[str, str]]] = None
    ):
        """Initialize the LATS agent.

        Args:
            llm_configs: Dictionary mapping role names to LLM configuration
            tools: Dictionary mapping tool names to callable functions
            max_iterations: Maximum search iterations
            exploration_weight: UCB exploration parameter
            num_expansions: Number of children per expansion
            prompt_dir: Directory containing prompt templates
            custom_instructions: Custom instructions appended to all system prompts
            prompt_overrides: Dictionary mapping step names to prompt overrides
        """
        self.tools = tools or {}
        self.max_iterations = max_iterations
        self.exploration_weight = exploration_weight
        self.num_expansions = num_expansions
        super().__init__(
            llm_configs=llm_configs,
            prompt_dir=prompt_dir,
            custom_instructions=custom_instructions,
            prompt_overrides=prompt_overrides
        )

    def build_graph(self) -> None:
        """Build the LangGraph StateGraph for the LATS pattern.

        Creates a graph with the following nodes:
            - select_node: Chooses node to expand using UCB
            - expand_node: Generates child nodes
            - evaluate_node: Scores new nodes
            - backpropagate: Updates ancestor values
            - check_budget: Checks if search should continue
            - choose_best_path: Selects best solution path
            - generate_final_output: Creates final answer
        """
        workflow = StateGraph(dict)

        # Add nodes
        workflow.add_node("select_node", self._select_node)
        workflow.add_node("expand_node", self._expand_node)
        workflow.add_node("evaluate_node", self._evaluate_node)
        workflow.add_node("backpropagate", self._backpropagate)
        workflow.add_node("check_budget", self._check_budget)
        workflow.add_node("choose_best_path", self._choose_best_path)
        workflow.add_node("generate_final_output", self._generate_final_output)

        # Set entry point
        workflow.set_entry_point("select_node")

        # Add edges
        workflow.add_edge("select_node", "expand_node")
        workflow.add_edge("expand_node", "evaluate_node")
        workflow.add_edge("evaluate_node", "backpropagate")
        workflow.add_edge("backpropagate", "check_budget")

        # Conditional edges
        workflow.add_conditional_edges(
            "check_budget",
            self._route_after_check,
            {
                "continue": "select_node",
                "finish": "choose_best_path"
            }
        )

        workflow.add_edge("choose_best_path", "generate_final_output")
        workflow.add_edge("generate_final_output", "__end__")

        self.graph: CompiledStateGraph = workflow.compile()

    def run(self, input_data: Any) -> Any:
        """Execute the LATS tree search workflow.

        Args:
            input_data: The user's task or query

        Returns:
            The final answer from the best path

        Raises:
            Exception: If graph execution fails
        """
        self.on_start(input_data)

        try:
            # Initialize search tree
            root = TreeNode(
                state_description=f"Initial state: {input_data}",
                action=None,
                parent=None
            )

            state = {
                "input_task": input_data,
                "root": root,
                "current_node": root,
                "expanded_children": [],
                "budget_exhausted": False,
                "iterations": 0,
                "best_path": None,
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

    def _select_node(self, state: Dict) -> Dict:
        """Select most promising node to expand using UCB.

        Uses Upper Confidence Bound to balance exploration vs exploitation.

        Args:
            state: Current state with search tree

        Returns:
            Updated state with selected current_node
        """
        if state.get("error"):
            return state

        try:
            root = state["root"]

            # Use UCB to select best leaf node
            selected = self._select_best_leaf(root)
            state["current_node"] = selected

        except Exception as e:
            state["error"] = f"Selection error: {str(e)}"

        return state

    def _select_best_leaf(self, node: TreeNode) -> TreeNode:
        """Recursively select best leaf node using UCB.

        Args:
            node: Current node to select from

        Returns:
            Selected leaf node
        """
        # If no children, this is a leaf
        if not node.children:
            return node

        # If any child is unvisited, select it
        unvisited = [child for child in node.children if child.visits == 0]
        if unvisited:
            return unvisited[0]

        # Otherwise, select child with highest UCB score
        best_child = max(
            node.children,
            key=lambda c: c.ucb_score(self.exploration_weight)
        )

        # Recursively select from best child
        return self._select_best_leaf(best_child)

    def _expand_node(self, state: Dict) -> Dict:
        """Expand selected node by generating child nodes.

        Uses LLM to propose multiple possible next steps.

        Args:
            state: Current state with current_node selected

        Returns:
            Updated state with expanded_children
        """
        if state.get("error"):
            return state

        try:
            prompt_data = self._load_prompt("Expand")
            expansion_llm: BaseChatModel = self._get_llm("thinking")

            current_node = state["current_node"]

            # Build path to current node
            path = self._get_path_to_node(current_node)
            path_text = self._format_path(path)

            # Build messages
            system_prompt = prompt_data["system"]
            user_prompt = prompt_data["user"].format(
                task=state["input_task"],
                current_state=current_node.state_description,
                path=path_text,
                num_expansions=self.num_expansions
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # Get expansions from LLM
            response = expansion_llm.invoke(messages)
            expansions_text = response.content

            # Parse expansions into child nodes
            children = self._parse_expansions(expansions_text, current_node)

            # Add children to current node
            current_node.children.extend(children)
            state["expanded_children"] = children

        except Exception as e:
            state["error"] = f"Expansion error: {str(e)}"

        return state

    def _get_path_to_node(self, node: TreeNode) -> List[TreeNode]:
        """Get path from root to given node.

        Args:
            node: Target node

        Returns:
            List of nodes from root to target
        """
        path = []
        current = node
        while current is not None:
            path.append(current)
            current = current.parent
        return list(reversed(path))

    def _format_path(self, path: List[TreeNode]) -> str:
        """Format path as readable text.

        Args:
            path: List of nodes in path

        Returns:
            Formatted path description
        """
        lines = []
        for i, node in enumerate(path):
            action = node.action or "START"
            lines.append(f"Step {i}: {action} -> {node.state_description}")
        return "\n".join(lines)

    def _parse_expansions(
        self,
        expansions_text: str,
        parent: TreeNode
    ) -> List[TreeNode]:
        """Parse LLM output into child nodes.

        Expected format:
            EXPANSION 1:
            ACTION: <action description>
            STATE: <resulting state description>

            EXPANSION 2:
            ACTION: <action description>
            STATE: <resulting state description>

        Args:
            expansions_text: LLM output text
            parent: Parent node

        Returns:
            List of child TreeNode objects
        """
        children = []
        current_expansion = {}

        for line in expansions_text.strip().split("\n"):
            line = line.strip()
            if not line:
                if current_expansion and "action" in current_expansion:
                    child = TreeNode(
                        state_description=current_expansion.get("state", "Unknown state"),
                        action=current_expansion["action"],
                        parent=parent
                    )
                    children.append(child)
                    current_expansion = {}
                continue

            if line.startswith("EXPANSION"):
                if current_expansion and "action" in current_expansion:
                    child = TreeNode(
                        state_description=current_expansion.get("state", "Unknown state"),
                        action=current_expansion["action"],
                        parent=parent
                    )
                    children.append(child)
                current_expansion = {}

            elif line.startswith("ACTION:"):
                current_expansion["action"] = line.split(":", 1)[1].strip()

            elif line.startswith("STATE:"):
                current_expansion["state"] = line.split(":", 1)[1].strip()

        # Add last expansion
        if current_expansion and "action" in current_expansion:
            child = TreeNode(
                state_description=current_expansion.get("state", "Unknown state"),
                action=current_expansion["action"],
                parent=parent
            )
            children.append(child)

        # Fallback: create default children if parsing failed
        if not children:
            for i in range(min(self.num_expansions, 2)):
                child = TreeNode(
                    state_description=f"Expansion {i+1} from {parent.state_description[:30]}...",
                    action=f"Action {i+1}",
                    parent=parent
                )
                children.append(child)

        return children

    def _evaluate_node(self, state: Dict) -> Dict:
        """Evaluate newly expanded nodes.

        Uses evaluation LLM to score each child node's promise.

        Args:
            state: Current state with expanded_children

        Returns:
            Updated state with evaluated nodes
        """
        if state.get("error"):
            return state

        try:
            prompt_data = self._load_prompt("Evaluate")
            eval_llm: BaseChatModel = self._get_llm("evaluation")

            expanded_children = state["expanded_children"]

            for child in expanded_children:
                # Build path including this child
                path = self._get_path_to_node(child)
                path_text = self._format_path(path)

                # Build messages
                system_prompt = prompt_data["system"]
                user_prompt = prompt_data["user"].format(
                    task=state["input_task"],
                    path=path_text,
                    current_state=child.state_description
                )

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ]

                # Get evaluation score
                response = eval_llm.invoke(messages)
                score = self._parse_score(response.content)

                # Store initial value (will be updated during backprop)
                child.value = score
                child.visits = 1

        except Exception as e:
            state["error"] = f"Evaluation error: {str(e)}"

        return state

    def _parse_score(self, eval_text: str) -> float:
        """Parse evaluation score from LLM output.

        Looks for SCORE: <number> format, defaults to 0.5 if not found.

        Args:
            eval_text: LLM evaluation output

        Returns:
            Score between 0.0 and 1.0
        """
        try:
            for line in eval_text.split("\n"):
                if line.strip().startswith("SCORE:"):
                    score_str = line.split(":", 1)[1].strip()
                    score = float(score_str)
                    return max(0.0, min(1.0, score))  # Clamp to [0, 1]
        except:
            pass

        # Default to neutral score
        return 0.5

    def _backpropagate(self, state: Dict) -> Dict:
        """Backpropagate values up the tree.

        Updates visit counts and values for all ancestors of expanded nodes.

        Args:
            state: Current state with expanded_children

        Returns:
            Updated state with updated tree
        """
        if state.get("error"):
            return state

        try:
            expanded_children = state["expanded_children"]

            for child in expanded_children:
                # Backpropagate from child to root
                value = child.value
                current = child.parent

                while current is not None:
                    current.visits += 1
                    current.value += value
                    current = current.parent

        except Exception as e:
            state["error"] = f"Backpropagation error: {str(e)}"

        return state

    def _check_budget(self, state: Dict) -> Dict:
        """Check if search budget is exhausted.

        Args:
            state: Current state

        Returns:
            Updated state with budget_exhausted flag
        """
        state["iterations"] += 1

        if state["iterations"] >= self.max_iterations:
            state["budget_exhausted"] = True

        return state

    def _route_after_check(self, state: Dict) -> str:
        """Route to either continue search or finish.

        Args:
            state: Current state

        Returns:
            "finish" if done, "continue" otherwise
        """
        if state.get("error") or state["budget_exhausted"]:
            return "finish"
        return "continue"

    def _choose_best_path(self, state: Dict) -> Dict:
        """Choose best path from root based on visit counts and values.

        Args:
            state: Current state with search tree

        Returns:
            Updated state with best_path
        """
        if state.get("error"):
            return state

        try:
            root = state["root"]

            # Find best leaf node based on average value
            best_leaf = self._find_best_leaf(root)

            # Get path to best leaf
            best_path = self._get_path_to_node(best_leaf)
            state["best_path"] = best_path

        except Exception as e:
            state["error"] = f"Path selection error: {str(e)}"

        return state

    def _find_best_leaf(self, node: TreeNode) -> TreeNode:
        """Recursively find leaf with highest average value.

        Args:
            node: Current node

        Returns:
            Best leaf node
        """
        if not node.children:
            return node

        # Select child with highest average value
        best_child = max(node.children, key=lambda c: c.average_value())

        return self._find_best_leaf(best_child)

    def _generate_final_output(self, state: Dict) -> Dict:
        """Generate final answer based on best path.

        Args:
            state: Current state with best_path

        Returns:
            Updated state with final_answer
        """
        if state.get("error"):
            state["final_answer"] = f"Error: {state['error']}"
            return state

        try:
            prompt_data = self._load_prompt("FinalOutput")
            final_llm: BaseChatModel = self._get_llm("thinking")

            best_path = state["best_path"]
            path_text = self._format_path(best_path)

            # Build messages
            system_prompt = prompt_data["system"]
            user_prompt = prompt_data["user"].format(
                task=state["input_task"],
                path=path_text,
                iterations=state["iterations"]
            )

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # Get final answer
            response = final_llm.invoke(messages)
            state["final_answer"] = response.content

        except Exception as e:
            state["final_answer"] = f"Final output error: {str(e)}"

        return state
