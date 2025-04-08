"""
REWOO Agent Pattern Implementation

This module implements the Reasoning Without Observation (REWOO) agent pattern,
which decouples planning from execution to improve efficiency and performance.

The pattern consists of two main components:
1. Planner/Worker: Generates a plan without executing tools
2. Solver/Executor: Executes the plan by following the steps

Key advantages:
- Reduces token consumption by separating reasoning from observation
- Improves performance through specialized roles
- Enables using different LLMs for planning vs. execution
"""

from typing import Any, Dict, List, Optional, TypedDict, Annotated, Sequence
import operator
import logging
from agent_patterns.core.base_agent import BaseAgent
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)

# Define the state schema using TypedDict
class REWOOState(TypedDict):
    """
    Represents the state of the REWOO agent.
    
    Attributes:
        input: The initial user input.
        plan: List of steps in the execution plan.
        current_step_index: Index of the current step being executed.
        execution_results: List of results from executing steps.
        iteration_count: Number of iterations performed.
        execution_complete: Whether execution is complete.
        final_answer: The final synthesized answer.
    """
    input: str
    plan: List[Dict[str, Any]]
    current_step_index: int
    execution_results: List[Dict[str, Any]]
    iteration_count: int
    execution_complete: bool
    final_answer: Optional[str]

class REWOOAgent(BaseAgent):
    """
    Implementation of the REWOO (Reasoning Without Observation) agent pattern.
    
    This pattern separates reasoning (planning) from observations (execution)
    to improve efficiency and performance. It consists of a planner component
    that creates a structured plan, and an executor component that follows
    the plan and uses tools to complete tasks.
    """
    
    def __init__(
        self, 
        llm_configs: dict, 
        tool_registry: Optional[Dict[str, Any]] = None,
        prompt_dir: str = "prompts",
        max_iterations: int = 10,
        **kwargs
    ):
        """
        Initialize the REWOO agent.
        
        Args:
            llm_configs: Dictionary of LLM configurations for different roles
            tool_registry: Dictionary of tools available to the agent
            prompt_dir: Directory containing prompt templates
            max_iterations: Maximum number of execution iterations
        """
        self.tool_registry = tool_registry or {}
        self.max_iterations = max_iterations
        super().__init__(llm_configs=llm_configs, prompt_dir=prompt_dir, **kwargs)
    
    def build_graph(self) -> None:
        """
        Construct the LangGraph for the REWOO pattern.
        
        The graph consists of these main nodes:
        1. plan_steps: Generate a structured plan
        2. execute_step: Execute a single step of the plan
        3. check_completion: Check if execution is complete
        4. format_final_answer: Format the final answer
        """
        # Create the graph with our state type
        sg = StateGraph(REWOOState)
        
        # Define nodes
        sg.add_node("plan_steps", self._plan_steps)
        sg.add_node("execute_step", self._execute_step)
        sg.add_node("check_completion", self._check_completion)
        sg.add_node("format_final_answer", self._format_final_answer)
        
        # Define edges
        sg.set_entry_point("plan_steps")
        sg.add_edge("plan_steps", "execute_step")
        sg.add_edge("execute_step", "check_completion")
        
        # Add conditional edges based on execution completion
        sg.add_conditional_edges(
            "check_completion",
            self._should_continue_execution,
            {
                True: "execute_step",  # If not complete, continue executing
                False: "format_final_answer"  # If complete, format final answer
            }
        )
        
        # Add edge from format_final_answer to END
        sg.add_edge("format_final_answer", END)
        
        self.graph = sg.compile()
    
    def _should_continue_execution(self, state: REWOOState) -> bool:
        """
        Check if execution should continue.
        
        Args:
            state: Current agent state
            
        Returns:
            True if execution should continue, False if complete
        """
        return not state["execution_complete"]
    
    def run(self, input_data: Any) -> Any:
        """
        Run the REWOO agent on the given input.
        
        Args:
            input_data: User query or task description
            
        Returns:
            Final response after execution
            
        Raises:
            Exception: If an error occurs during execution
        """
        initial_state: REWOOState = {
            "input": input_data,
            "plan": [],
            "current_step_index": 0,
            "execution_results": [],
            "iteration_count": 0,
            "execution_complete": False,
            "final_answer": None
        }
        
        logger.info(f"Starting REWOO agent with input: {input_data}")
        # Don't catch exceptions here to allow them to propagate
        final_state = self.graph.invoke(initial_state)
        logger.info("REWOO agent execution completed")
        
        return final_state["final_answer"]
    
    def stream(self, input_data: Any):
        """
        Stream the execution of the REWOO agent.
        
        Args:
            input_data: User query or task description
            
        Yields:
            Intermediate results during execution
        """
        initial_state: REWOOState = {
            "input": input_data,
            "plan": [],
            "current_step_index": 0,
            "execution_results": [],
            "iteration_count": 0,
            "execution_complete": False,
            "final_answer": None
        }
        
        # Note: The exact API for streaming might need to be adjusted based on the specific version
        # of LangGraph being used
        try:
            for event in self.graph.stream(initial_state):
                if "state" in event and "final_answer" in event["state"] and event["state"]["final_answer"]:
                    yield event["state"]["final_answer"]
                elif "state" in event and "current_step_index" in event["state"]:
                    current_step = event["state"].get("current_step_index", 0)
                    plan_length = len(event["state"].get("plan", []))
                    if plan_length > 0:
                        yield f"Executing step {current_step + 1} of {plan_length}..."
        except AttributeError:
            # Fall back to non-streaming if stream is not available
            result = self.run(input_data)
            yield result
            
    def _plan_steps(self, state: REWOOState) -> Dict:
        """
        Generate a structured plan without executing tools.
        
        This function uses the planner LLM to create a detailed plan
        with steps that will be executed separately.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with plan
        """
        planner_llm = self._get_llm("planner")
        prompt_template = self._load_prompt_template("PlannerPrompt")
        
        # Generate plan using the planner LLM
        logger.info(f"Generating plan for input: {state['input']}")
        
        # Format the prompt with the input
        prompt_args = {"input": state["input"]}
        
        # Get formatted messages
        messages = prompt_template.format_messages(**prompt_args)
        
        # Call the LLM
        planning_response = planner_llm.invoke(messages)
        
        # Parse the planning response into structured steps
        # Here we assume the LLM will respond with a parseable format
        # In a robust implementation, this would include error handling
        plan_text = planning_response if isinstance(planning_response, str) else planning_response.content
        
        # Parse plan text into structured steps
        # This is a simplified parsing approach - in production, you might want more robust parsing
        plan_lines = plan_text.strip().split("\n")
        structured_plan = []
        
        current_step = None
        for line in plan_lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to identify step markers (Step 1:, 1., etc.)
            if line.lower().startswith("step ") or (line[0].isdigit() and line[1:3] in [". ", ") "]):
                if current_step:
                    structured_plan.append(current_step)
                
                # Extract step number if possible
                try:
                    step_num = int(line.split()[1].rstrip(":.))")) if line.lower().startswith("step ") else int(line.split(".")[0])
                except (IndexError, ValueError):
                    step_num = len(structured_plan) + 1
                    
                current_step = {
                    "step_id": step_num,
                    "description": line,
                    "details": "",
                    "tools": [],
                    "depends_on": []
                }
            elif current_step:
                # If we already have a current step, add this line as additional details
                current_step["details"] += line + "\n"
                
                # Try to identify tool mentions
                common_tools = ["search", "calculator", "database", "api", "browser", "query"]
                for tool in common_tools:
                    if tool.lower() in line.lower() and tool not in current_step["tools"]:
                        current_step["tools"].append(tool)
        
        # Add the last step if it exists
        if current_step:
            structured_plan.append(current_step)
            
        # If no structured plan was created, create a simple default plan
        if not structured_plan:
            structured_plan = [{
                "step_id": 1,
                "description": f"Complete the task: {state['input']}",
                "details": plan_text,
                "tools": [],
                "depends_on": []
            }]
            
        logger.info(f"Generated plan with {len(structured_plan)} steps")
        return {"plan": structured_plan}
    
    def _execute_step(self, state: REWOOState) -> Dict:
        """
        Execute the current step in the plan.
        
        This function takes the current step from the plan and executes it
        using the solver LLM and available tools.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with execution results
        """
        # Increment iteration count
        iteration_count = state.get("iteration_count", 0) + 1
        
        # Ensure the state has a plan
        if "plan" not in state or not state["plan"]:
            logger.warning("No plan found in state. Cannot execute step.")
            return {"execution_complete": True, "iteration_count": iteration_count}
        
        # Get current step
        current_step_index = state["current_step_index"]
        if current_step_index >= len(state["plan"]):
            # No more steps to execute
            return {"execution_complete": True, "iteration_count": iteration_count}
            
        # Check if we've exceeded the max iterations
        if iteration_count > self.max_iterations:
            logger.warning(f"Reached maximum iterations ({self.max_iterations}). Stopping execution.")
            return {"execution_complete": True, "iteration_count": iteration_count}
            
        current_step = state["plan"][current_step_index]
        logger.info(f"Executing step {current_step_index + 1}: {current_step['description']}")
        
        # Prepare context from previous execution results
        context = ""
        for result in state["execution_results"]:
            step_id = result["step_id"]
            context += f"Step {step_id} result: {result['result']}\n"
        
        # Get solver LLM and prompt
        solver_llm = self._get_llm("solver")
        prompt_template = self._load_prompt_template("SolverPrompt")
        
        # Format the prompt with the step information
        prompt_args = {
            "step_description": current_step["description"],
            "step_details": current_step.get("details", ""),
            "context": context
        }
        
        # Get formatted messages
        messages = prompt_template.format_messages(**prompt_args)
        
        # Execute step using solver LLM
        execution_response = solver_llm.invoke(messages)
        
        # Extract execution result
        execution_result = execution_response if isinstance(execution_response, str) else execution_response.content
        
        # Check if any tools need to be called based on LLM output
        tool_calls = self._extract_tool_calls(execution_result)
        tool_outputs = []
        
        # Execute tool calls if any
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args", {})
            
            if tool_name in self.tool_registry:
                try:
                    logger.info(f"Calling tool: {tool_name} with args: {tool_args}")
                    tool_result = self.tool_registry[tool_name](**tool_args)
                    tool_outputs.append({
                        "tool": tool_name,
                        "output": tool_result
                    })
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {str(e)}")
                    tool_outputs.append({
                        "tool": tool_name,
                        "error": str(e)
                    })
            else:
                logger.warning(f"Tool not found: {tool_name}")
                tool_outputs.append({
                    "tool": tool_name, 
                    "error": "Tool not available"
                })
        
        # Build the execution result
        new_result = {
            "step_id": current_step["step_id"],
            "result": execution_result,
            "tool_outputs": tool_outputs,
            "success": True  # Assume success for now - could be determined by additional logic
        }
        
        # Get a copy of the existing execution results and append the new result
        execution_results = state["execution_results"].copy()
        execution_results.append(new_result)
        
        # Move to next step and update state
        return {
            "plan": state["plan"],  # Preserve the plan
            "execution_results": execution_results,
            "current_step_index": current_step_index + 1,
            "iteration_count": iteration_count
        }
    
    def _check_completion(self, state: REWOOState) -> Dict:
        """
        Check if all steps have been executed.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with completion status
        """
        if state["current_step_index"] >= len(state["plan"]):
            logger.info("All steps have been executed. Execution complete.")
            return {"execution_complete": True}
        else:
            logger.info(f"Execution continuing. {state['current_step_index']}/{len(state['plan'])} steps complete.")
            return {"execution_complete": False}
    
    def _format_final_answer(self, state: REWOOState) -> Dict:
        """
        Format the final answer based on execution results.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with final answer
        """
        # Get final answer LLM (can be same as solver)
        final_llm = self._get_llm("solver")
        prompt_template = self._load_prompt_template("FinalAnswerPrompt")
        
        # Format the execution results for the LLM
        execution_summary = ""
        for i, result in enumerate(state["execution_results"]):
            step_id = result["step_id"]
            step_desc = next((s["description"] for s in state["plan"] if s["step_id"] == step_id), f"Step {step_id}")
            execution_summary += f"Step {step_id}: {step_desc}\nResult: {result['result']}\n\n"
            
            # Include tool outputs
            tool_outputs = result.get("tool_outputs", [])
            if tool_outputs:
                execution_summary += "Tool outputs:\n"
                for output in tool_outputs:
                    tool_name = output.get("tool", "unknown")
                    if "output" in output:
                        execution_summary += f"- {tool_name}: {output['output']}\n"
                    else:
                        execution_summary += f"- {tool_name}: Error - {output.get('error', 'unknown error')}\n"
                execution_summary += "\n"
        
        # Format the prompt with the input and execution summary
        prompt_args = {
            "input": state["input"],
            "execution_summary": execution_summary
        }
        
        # Get formatted messages
        messages = prompt_template.format_messages(**prompt_args)
        
        # Generate final answer
        logger.info("Generating final answer")
        final_response = final_llm.invoke(messages)
        
        final_answer = final_response if isinstance(final_response, str) else final_response.content
        logger.info("Final answer generated")
        
        return {"final_answer": final_answer}
    
    def _extract_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract tool calls from LLM output.
        
        This is a simplified implementation. In a production environment,
        you'd want more robust parsing, possibly using structured outputs
        from the LLM.
        
        Args:
            text: LLM output text
            
        Returns:
            List of tool call dictionaries
        """
        tool_calls = []
        
        # Check for common tool call formats
        if "TOOL:" in text or "Tool:" in text or "tool:" in text:
            lines = text.split("\n")
            current_tool = None
            current_args = {}
            
            for line in lines:
                line = line.strip()
                
                # Look for tool markers
                if line.upper().startswith("TOOL:") or line.startswith("Tool:") or line.startswith("tool:"):
                    # Save previous tool if exists
                    if current_tool:
                        tool_calls.append({"name": current_tool, "args": current_args})
                    
                    # Start new tool
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        current_tool = parts[1].strip()
                        current_args = {}
                
                # Look for arguments
                elif ":" in line and current_tool:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        current_args[key] = value
            
            # Add the final tool if it exists
            if current_tool:
                tool_calls.append({"name": current_tool, "args": current_args})
        
        return tool_calls 