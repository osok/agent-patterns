"""
Language Agent Tree Search (LATS) agent pattern implementation.

This pattern implements a tree search approach to reasoning where an agent:
1. Explores multiple reasoning paths through a tree structure
2. Evaluates paths using a value function
3. Selects nodes using UCB (Upper Confidence Bound) for exploration-exploitation balance
4. Backpropagates results to find the optimal solution path

LATS unifies reasoning, acting, and planning capabilities in language models.
"""
import math
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, TypedDict, Sequence

from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage

from agent_patterns.core.base_agent import BaseAgent

class LATSState(TypedDict):
    """State representation for the LATS agent.
    
    Attributes:
        input_task: The original problem or query to solve.
        current_node_id: ID of the current node being processed.
        nodes: Dictionary mapping node IDs to node objects.
        node_values: Dictionary mapping node IDs to their value scores.
        explored_paths: List of paths that have been explored.
        best_path: The current best path found.
        best_path_value: The value of the best path.
        iterations: Number of iterations performed.
        max_iterations: Maximum allowed iterations.
        max_depth: Maximum depth of tree exploration.
        exploration_weight: Parameter for UCB formula balancing exploration vs exploitation.
        final_answer: The final answer from the best path.
    """
    input_task: str
    current_node_id: Optional[str]
    nodes: Dict[str, Dict[str, Any]]
    node_values: Dict[str, float]
    explored_paths: List[Dict[str, Any]]
    best_path: Optional[List[str]]
    best_path_value: float
    iterations: int
    max_iterations: int
    max_depth: int
    exploration_weight: float
    final_answer: Optional[str]

class LATSAgent(BaseAgent):
    """
    Language Agent Tree Search (LATS) agent pattern implementation.
    
    LATS uses a tree search approach to find optimal reasoning paths
    by exploring multiple options and evaluating their value.
    
    Args:
        llm_configs: Dictionary with LLM configurations for different roles
        max_iterations: Maximum number of search iterations
        max_depth: Maximum depth of tree exploration
        exploration_weight: C parameter for UCB formula (exploration vs exploitation)
        n_expansions: Number of child nodes to generate per expansion
        prompt_dir: Directory for prompt templates
        tool_provider: Optional provider for tools the agent can use
        memory: Optional composite memory instance
        memory_config: Configuration for which memory types to use
    """
    
    def __init__(
        self,
        llm_configs: Dict[str, Dict[str, str]],
        max_iterations: int = 10,
        max_depth: int = 3,
        exploration_weight: float = 1.0,
        n_expansions: int = 3,
        prompt_dir: str = "src/agent_patterns/prompts",
        tool_provider: Optional[Any] = None,
        memory: Optional[Any] = None,
        memory_config: Optional[Dict[str, bool]] = None,
    ):
        """Initialize the LATS agent."""
        super().__init__(
            llm_configs=llm_configs, 
            prompt_dir=prompt_dir,
            tool_provider=tool_provider,
            memory=memory,
            memory_config=memory_config
        )
        self.max_iterations = max_iterations
        self.max_depth = max_depth
        self.exploration_weight = exploration_weight
        self.n_expansions = n_expansions
    
    def build_graph(self) -> None:
        """
        Construct the StateGraph for the LATS algorithm with nodes for:
        - Initialization
        - Node selection
        - Node expansion
        - Path evaluation
        - Backpropagation
        - Termination check
        - Final path selection
        """
        # Create the graph with our state type
        sg = StateGraph(LATSState)
        
        # Define nodes in the graph
        sg.add_node("initialize_search", self._initialize_search)
        sg.add_node("select_node", self._select_node)
        sg.add_node("expand_node", self._expand_node)
        sg.add_node("evaluate_paths", self._evaluate_paths)
        sg.add_node("backpropagate", self._backpropagate)
        sg.add_node("check_termination", self._check_termination)
        sg.add_node("select_best_path", self._select_best_path)
        
        # Define edges in the graph
        sg.set_entry_point("initialize_search")
        sg.add_edge("initialize_search", "select_node")
        sg.add_edge("select_node", "expand_node")
        sg.add_edge("expand_node", "evaluate_paths")
        sg.add_edge("evaluate_paths", "backpropagate")
        sg.add_edge("backpropagate", "check_termination")
        
        # Conditional edges based on whether to continue or finish
        sg.add_conditional_edges(
            "check_termination",
            self._get_next_step,
            {
                "continue": "select_node",
                "finish": "select_best_path",
            }
        )
        
        sg.add_edge("select_best_path", END)
        
        # Compile the graph
        self.graph = sg.compile()
    
    def run(self, input_data: Any, config: Optional[Dict[str, Any]] = None) -> Any:
        """
        Run the LATS algorithm to find the best solution path.
        
        Args:
            input_data: The problem or query to solve
            config: Optional configuration for the run, can include recursion_limit
            
        Returns:
            The final answer after tree search
        """
        # Initialize the starting state
        initial_state: LATSState = {
            "input_task": input_data,
            "current_node_id": None,
            "nodes": {},              # Dictionary of all nodes in the tree
            "node_values": {},        # Value assessments for nodes
            "explored_paths": [],     # Paths already explored
            "best_path": None,        # Current best path
            "best_path_value": 0,     # Value of best path
            "iterations": 0,          # Number of iterations performed
            "max_iterations": self.max_iterations,
            "max_depth": self.max_depth,
            "exploration_weight": self.exploration_weight,
            "final_answer": None      # Final selected solution
        }
        
        # Use config if provided, otherwise create one
        if config is None:
            config = {}
        
        # Run the graph with the initial state
        # Add recursion_limit to config if not already present
        if "recursion_limit" not in config:
            config["recursion_limit"] = 50  # Higher than the default 25
            
        final_state = self.graph.invoke(initial_state, config=config)
        return final_state["final_answer"]
    
    def _initialize_search(self, state: LATSState) -> Dict[str, Any]:
        """
        Initialize the search tree with the root node.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with initialized root node
        """
        # Create root node
        root_id = str(uuid.uuid4())
        root_node = {
            "id": root_id,
            "parent_id": None,
            "content": state["input_task"],
            "children": [],
            "depth": 0,
            "visits": 0,
            "path": [root_id],
            "is_terminal": False
        }
        
        # Update state
        nodes = dict(state["nodes"])
        nodes[root_id] = root_node
        
        node_values = dict(state["node_values"])
        node_values[root_id] = 0.5  # Initial neutral value
        
        return {
            "nodes": nodes,
            "node_values": node_values,
            "current_node_id": root_id
        }
    
    def _select_node(self, state: LATSState) -> Dict[str, Any]:
        """
        Select the next node to explore using UCB.
        
        This traverses the tree from the root to a leaf, selecting
        nodes according to the UCB formula to balance exploration and exploitation.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with selected node
        """
        current_id = list(state["nodes"].keys())[0]  # Start at root
        
        # Traverse tree until we reach a leaf or unexpanded node
        while (
            current_id is not None and 
            state["nodes"][current_id]["children"] and
            not state["nodes"][current_id]["is_terminal"]
        ):
            # If node has unexplored children, select one of them
            unexplored = [
                child_id for child_id in state["nodes"][current_id]["children"]
                if state["nodes"][child_id]["visits"] == 0
            ]
            
            if unexplored:
                # Select an unexplored child
                current_id = unexplored[0]
            else:
                # Use UCB to select among visited children
                best_score = -float("inf")
                best_child = None
                
                for child_id in state["nodes"][current_id]["children"]:
                    ucb_score = self._calculate_ucb(child_id, current_id, state)
                    if ucb_score > best_score:
                        best_score = ucb_score
                        best_child = child_id
                
                current_id = best_child
        
        return {"current_node_id": current_id}
    
    def _expand_node(self, state: LATSState) -> Dict[str, Any]:
        """
        Generate child nodes for the current node.
        
        This uses the LLM to propose possible next steps or 
        reasoning paths from the current node.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with new child nodes
        """
        current_id = state["current_node_id"]
        current_node = state["nodes"][current_id]
        
        # If we've reached max depth or node is terminal, don't expand
        if current_node["depth"] >= state["max_depth"] or current_node["is_terminal"]:
            return {}
        
        # If node already has children, no need to expand again
        if current_node["children"]:
            return {}
        
        # Retrieve relevant memories if memory is enabled
        memory_context = ""
        if self.memory:
            # Construct a query based on the path so far
            path_query = []
            for node_id in current_node["path"]:
                node = state["nodes"][node_id]
                path_query.append(node["content"])
            
            query = state["input_task"] + " " + " ".join(path_query)
            memories = self.sync_retrieve_memories(query)
            
            # Format memories for inclusion in the prompt
            if memories:
                memory_sections = []
                for memory_type, items in memories.items():
                    if items:
                        items_text = "\n- ".join([str(item) for item in items])
                        memory_sections.append(f"### {memory_type.capitalize()} Memories:\n- {items_text}")
                
                if memory_sections:
                    memory_context = "Relevant information from memory:\n\n" + "\n\n".join(memory_sections) + "\n\n"
                    self.logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for node expansion")
        
        # Get available tools information if tool_provider is available
        tools_context = ""
        if self.tool_provider:
            try:
                provider_tools = self.tool_provider.list_tools()
                if provider_tools:
                    tool_descriptions = []
                    for tool in provider_tools:
                        tool_name = tool.get("name", "")
                        tool_desc = tool.get("description", "")
                        tool_descriptions.append(f"- {tool_name}: {tool_desc}")
                    
                    if tool_descriptions:
                        tools_context = "Available tools that you can use:\n" + "\n".join(tool_descriptions) + "\n\n"
                        self.logger.info(f"Added {len(tool_descriptions)} tools from tool provider")
            except Exception as e:
                self.logger.warning(f"Error retrieving tools from tool_provider: {str(e)}")
        
        # Generate expansion options using LLM
        prompt_template = self._load_prompt_template("NodeExpansion")
        llm = self._get_llm("thinking")
        
        # Build context of the path so far
        path_context = []
        for node_id in current_node["path"]:
            node = state["nodes"][node_id]
            path_context.append(f"Step {node['depth']}: {node['content']}")
        
        # Format system and user prompts
        path_context_str = "\n".join(path_context)
        
        # Generate next steps with the LLM
        response = llm.invoke(prompt_template.format(
            input_task=state["input_task"],
            path_so_far=path_context_str,
            current_step=current_node["content"],
            n_expansions=self.n_expansions,
            memory_context=memory_context,
            tools_context=tools_context
        ))
        
        # Parse the response to extract the generated steps
        # In a real implementation, you would add more robust parsing
        steps = self._parse_expansion_response(response.content)
        
        # Make copies of the dictionaries to modify
        nodes = dict(state["nodes"])
        node_values = dict(state["node_values"])
        
        # Create child nodes
        children = []
        for step_content in steps:
            child_id = str(uuid.uuid4())
            children.append(child_id)
            
            # Create new node
            child_node = {
                "id": child_id,
                "parent_id": current_id,
                "content": step_content,
                "children": [],
                "depth": current_node["depth"] + 1,
                "visits": 0,
                "path": current_node["path"] + [child_id],
                "is_terminal": current_node["depth"] + 1 >= state["max_depth"]
            }
            
            # Add to state
            nodes[child_id] = child_node
            node_values[child_id] = 0.5  # Initial neutral value
        
        # Update the current node's children
        nodes[current_id] = dict(nodes[current_id])
        nodes[current_id]["children"] = children
        
        return {
            "nodes": nodes,
            "node_values": node_values
        }
    
    def _evaluate_paths(self, state: LATSState) -> Dict[str, Any]:
        """
        Evaluate the newly expanded paths.
        
        This uses the LLM to assign value scores to the paths.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with evaluated paths
        """
        current_id = state["current_node_id"]
        current_node = state["nodes"][current_id]
        
        # Make copies of the dictionaries to modify
        node_values = dict(state["node_values"])
        explored_paths = list(state["explored_paths"])
        best_path = state["best_path"]
        best_path_value = state["best_path_value"]
        
        # Retrieve relevant memories for evaluation context
        memory_context = ""
        if self.memory:
            memories = self.sync_retrieve_memories(state["input_task"])
            
            # Format memories for inclusion in the prompt
            if memories:
                memory_sections = []
                for memory_type, items in memories.items():
                    if items:
                        items_text = "\n- ".join([str(item) for item in items])
                        memory_sections.append(f"### {memory_type.capitalize()} Memories:\n- {items_text}")
                
                if memory_sections:
                    memory_context = "Relevant information from memory:\n\n" + "\n\n".join(memory_sections) + "\n\n"
                    self.logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for path evaluation")
        
        # Evaluate each child path if they exist and haven't been evaluated yet
        for child_id in state["nodes"][current_id]["children"]:
            child_node = state["nodes"][child_id]
            
            # Skip if already evaluated
            if child_id in state["node_values"] and state["nodes"][child_id]["visits"] > 0:
                continue
            
            # Construct the full path for evaluation
            path_steps = []
            for node_id in child_node["path"]:
                node = state["nodes"][node_id]
                path_steps.append(f"Step {node['depth']}: {node['content']}")
            
            # Get evaluation from LLM
            prompt_template = self._load_prompt_template("PathEvaluation")
            llm = self._get_llm("evaluation")
            
            path_content = "\n".join(path_steps)
            
            response = llm.invoke(prompt_template.format(
                input_task=state["input_task"],
                path=path_content,
                memory_context=memory_context
            ))
            
            # Parse evaluation to get a value between 0 and 1
            value = self._parse_evaluation_response(response.content)
            
            # Store the value
            node_values[child_id] = value
            
            # Add to explored paths
            explored_paths.append({
                "path": child_node["path"],
                "value": value
            })
            
            # Update best path if this is better
            if value > best_path_value:
                best_path = child_node["path"]
                best_path_value = value
        
        return {
            "node_values": node_values,
            "explored_paths": explored_paths,
            "best_path": best_path,
            "best_path_value": best_path_value
        }
    
    def _backpropagate(self, state: LATSState) -> Dict[str, Any]:
        """
        Backpropagate the evaluation results up the tree.
        
        Updates the visit counts and values of all nodes in the path.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with backpropagated values
        """
        current_id = state["current_node_id"]
        current_node = state["nodes"][current_id]
        
        # Make copies of the dictionaries to modify
        nodes = dict(state["nodes"])
        node_values = dict(state["node_values"])
        iterations = state["iterations"] + 1
        
        # Get the value to backpropagate
        # If node has children, use the max value of children
        # Otherwise use the node's own value
        if current_node["children"]:
            child_values = [state["node_values"].get(child_id, 0) 
                          for child_id in current_node["children"]]
            value = max(child_values) if child_values else state["node_values"].get(current_id, 0)
        else:
            value = state["node_values"].get(current_id, 0)
        
        # Backpropagate up the tree
        node_id = current_id
        while node_id is not None:
            # Increment visit count
            nodes[node_id] = dict(nodes[node_id])
            nodes[node_id]["visits"] += 1
            
            # Update value (average of current value and new value)
            visits = nodes[node_id]["visits"]
            current_value = node_values.get(node_id, 0)
            
            # Update formula: weighted average based on visits
            updated_value = (current_value * (visits - 1) + value) / visits
            node_values[node_id] = updated_value
            
            # Move to parent
            node_id = nodes[node_id]["parent_id"]
        
        return {
            "nodes": nodes,
            "node_values": node_values,
            "iterations": iterations
        }
    
    def _check_termination(self, state: LATSState) -> Dict[str, Any]:
        """
        Check if the search should terminate.
        
        Termination occurs when:
        - Maximum iterations reached
        - A path with a sufficiently high value is found
        - All possible paths are explored
        
        Args:
            state: The current state
            
        Returns:
            Updated state
        """
        # No changes needed - just a pass-through
        return {}
    
    def _get_next_step(self, state: LATSState) -> str:
        """
        Determine the next step in the graph based on termination criteria.
        
        Args:
            state: Current state
            
        Returns:
            String indicating the next step: "continue" or "finish"
        """
        if self._should_continue(state):
            return "continue"
        else:
            return "finish"
    
    def _should_continue(self, state: LATSState) -> bool:
        """
        Determine if the search should continue.
        
        Args:
            state: The current state
            
        Returns:
            True if search should continue, False otherwise
        """
        # Check iteration limit
        if state["iterations"] >= state["max_iterations"]:
            return False
        
        # Check if we found a very good solution already
        if state["best_path_value"] >= 0.95:
            return False
        
        # Check if we have unexplored nodes
        has_unexplored = False
        for node_id, node in state["nodes"].items():
            if (node["visits"] == 0 or 
                (not node["is_terminal"] and not node["children"] and node["depth"] < state["max_depth"])):
                has_unexplored = True
                break
        
        if not has_unexplored:
            return False
        
        return True
    
    def _select_best_path(self, state: LATSState) -> Dict[str, Any]:
        """
        Select the best path as the final solution.
        
        This synthesizes the final answer from the highest-value path.
        
        Args:
            state: The current state
            
        Returns:
            Updated state with final answer
        """
        # Get the best path
        best_path = state["best_path"]
        
        # Retrieve relevant memories if memory is enabled
        memory_context = ""
        if self.memory:
            memories = self.sync_retrieve_memories(state["input_task"])
            
            # Format memories for inclusion in the prompt
            if memories:
                memory_sections = []
                for memory_type, items in memories.items():
                    if items:
                        items_text = "\n- ".join([str(item) for item in items])
                        memory_sections.append(f"### {memory_type.capitalize()} Memories:\n- {items_text}")
                
                if memory_sections:
                    memory_context = "Relevant information from memory:\n\n" + "\n\n".join(memory_sections) + "\n\n"
                    self.logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for final synthesis")
        
        if best_path:
            # Construct solution from the path
            solution_steps = []
            for node_id in best_path:
                node = state["nodes"][node_id]
                solution_steps.append(f"Step {node['depth']}: {node['content']}")
            
            # Get final solution from LLM
            prompt_template = self._load_prompt_template("NodeSelection")
            llm = self._get_llm("thinking")
            
            solution_content = "\n".join(solution_steps)
            
            response = llm.invoke(prompt_template.format(
                input_task=state["input_task"],
                best_path=solution_content,
                memory_context=memory_context
            ))
            
            final_answer = response.content
        else:
            # Fallback if no path was found
            final_answer = "No solution path was found."
        
        # Save the path and solution to memory if enabled
        if self.memory and best_path:
            # Get path content
            path_content = []
            for node_id in best_path:
                node = state["nodes"][node_id]
                path_content.append(node["content"])
            
            # Save to episodic memory
            self.sync_save_memory(
                memory_type="episodic",
                item={
                    "event_type": "path_search",
                    "task": state["input_task"],
                    "path": path_content,
                    "path_value": state["best_path_value"],
                    "iterations": state["iterations"],
                    "explored_paths": len(state["explored_paths"]),
                    "final_answer": final_answer
                },
                task=state["input_task"]
            )
            
            # Save to semantic memory
            self.sync_save_memory(
                memory_type="semantic",
                item={
                    "task_type": state["input_task"].split()[:5],  # Use first few words as task type
                    "solution": final_answer,
                    "path_value": state["best_path_value"],
                    "successful": state["best_path_value"] >= 0.8  # Consider it successful if score is high
                },
                task=state["input_task"]
            )
        
        return {"final_answer": final_answer}
    
    def _calculate_ucb(self, node_id: str, parent_id: str, state: LATSState) -> float:
        """
        Calculate the UCB value for a node.
        
        UCB formula: value(v) + c * sqrt(ln(N(u)) / N(v))
        where v is the node, u is the parent
        N(v) is the number of visits to node v
        c is the exploration parameter
        
        Args:
            node_id: ID of the node
            parent_id: ID of the parent node
            state: Current state
            
        Returns:
            UCB score
        """
        c = state["exploration_weight"]
        node_value = state["node_values"].get(node_id, 0)
        node_visits = state["nodes"][node_id]["visits"] + 1  # Add 1 to avoid division by zero
        parent_visits = state["nodes"][parent_id]["visits"] + 1
        
        exploration_term = c * math.sqrt(math.log(parent_visits) / node_visits)
        return node_value + exploration_term
    
    def _parse_expansion_response(self, response: str) -> List[str]:
        """
        Parse the LLM response for node expansion.
        
        Args:
            response: Raw LLM response
            
        Returns:
            List of expansion steps
        """
        # In a production environment, you'd want more robust parsing
        # This is a simplified version that assumes a numbered list
        lines = response.strip().split('\n')
        steps = []
        
        for line in lines:
            line = line.strip()
            # Look for lines that start with a number or have a step prefix
            if (line and (line[0].isdigit() or line.lower().startswith('step') 
                         or line.lower().startswith('option'))):
                # Remove numbers and prefixes
                parts = line.split(':', 1)
                if len(parts) > 1:
                    steps.append(parts[1].strip())
                else:
                    steps.append(line.strip())
        
        # If no steps were found, treat each line as a separate step
        if not steps and lines:
            steps = [line.strip() for line in lines if line.strip()]
        
        # Limit to the configured number of expansions
        return steps[:self.n_expansions]
    
    def _parse_evaluation_response(self, response: str) -> float:
        """
        Parse the LLM response for path evaluation.
        
        Args:
            response: Raw LLM evaluation response
            
        Returns:
            Evaluation score between 0 and 1
        """
        # In a production environment, you'd want more robust parsing
        # This is a simplified version that looks for a score
        try:
            # Look for patterns like "Score: 0.85" or "Rating: 8.5/10"
            for line in response.strip().split('\n'):
                line = line.lower()
                
                # Try to find rating or score patterns
                if 'score:' in line:
                    parts = line.split('score:')
                    if len(parts) > 1:
                        score_text = parts[1].strip()
                        score = float(score_text)
                        # Normalize to 0-1 if needed
                        if score > 1:
                            score = score / 10
                        return min(max(score, 0), 1)
                
                # Try to find a rating out of 10
                elif 'rating:' in line:
                    parts = line.split('rating:')
                    if len(parts) > 1:
                        rating_text = parts[1].strip()
                        if '/' in rating_text:
                            num, denom = rating_text.split('/', 1)
                            return min(max(float(num) / float(denom), 0), 1)
                        else:
                            rating = float(rating_text)
                            # Normalize to 0-1 if needed
                            if rating > 1:
                                rating = rating / 10
                            return min(max(rating, 0), 1)
                
                # Look for a direct number
                elif any(term in line for term in ['value:', 'evaluation:', 'assessment:']):
                    for term in ['value:', 'evaluation:', 'assessment:']:
                        if term in line:
                            parts = line.split(term)
                            if len(parts) > 1:
                                try:
                                    value = float(parts[1].strip())
                                    # Normalize to 0-1 if needed
                                    if value > 1:
                                        value = value / 10
                                    return min(max(value, 0), 1)
                                except ValueError:
                                    continue
            
            # If no explicit score found, look for just a number
            for line in response.strip().split('\n'):
                line = line.strip()
                if line and line[0].isdigit():
                    try:
                        value = float(line)
                        # Normalize to 0-1 if needed
                        if value > 1:
                            value = value / 10
                        return min(max(value, 0), 1)
                    except ValueError:
                        continue
            
            # Default score if parsing fails
            return 0.5
        
        except Exception:
            # Fallback - on any error return neutral score
            return 0.5 