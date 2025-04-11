"""Reflexion agent pattern implementation."""

import operator
from typing import Any, Dict, List, Optional, Union, TypedDict, Annotated, Sequence, cast
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.language_models import BaseLanguageModel
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
import logging
from pathlib import Path
import re

from agent_patterns.core.base_agent import BaseAgent

# Define the state according to LangGraph best practices
class ReflexionState(TypedDict):
    """Represents the state of the Reflexion agent.

    Attributes:
        input_task: The original task/problem to solve.
        reflection_memory: List of reflections from previous attempts.
        trial_count: Number of trials attempted so far.
        max_trials: Maximum number of trials to attempt.
        current_plan: The current planned approach.
        action_result: Result of executed action.
        evaluation: Evaluation of the action result.
        trial_reflection: Reflection on the current trial.
        final_answer: The final output after all trials.
    """
    input_task: str
    reflection_memory: List[str]
    trial_count: int
    max_trials: int
    current_plan: Optional[str]
    action_result: Optional[str]
    evaluation: Optional[str]
    trial_reflection: Optional[str]
    final_answer: Optional[str]


class ReflexionAgent(BaseAgent):
    """Reflexion pattern implementation using LangGraph.
    
    This agent implements a multi-trial approach that:
    1. Plans an action based on reflection memory from previous attempts
    2. Executes the planned action
    3. Evaluates the outcome
    4. Reflects on what worked/didn't work
    5. Updates a reflection memory for future attempts
    6. Repeats until success or max trials reached
    
    The primary benefit is improved performance through iterative learning
    and memory of past mistakes and successes.
    """

    def __init__(
        self,
        llm_configs: Dict[str, Dict],
        max_trials: int = 3,
        prompt_dir: str = "src/agent_patterns/prompts",
        tool_provider: Optional[Any] = None,
        memory: Optional[Any] = None,
        memory_config: Optional[Dict[str, bool]] = None,
        log_level: int = logging.INFO
    ):
        """Initialize the Reflexion agent.
        
        Args:
            llm_configs: Configuration for LLM roles (e.g., {'planner': {...}, 'executor': {...}, 'evaluator': {...}, 'reflector': {...}}).
            max_trials: Maximum number of trials to attempt.
            prompt_dir: Directory containing prompt templates (relative to project root).
            tool_provider: Optional provider for tools the agent can use.
            memory: Optional composite memory instance.
            memory_config: Configuration for which memory types to use.
            log_level: Logging level.
        """
        # Call BaseAgent init
        super().__init__(
            llm_configs=llm_configs, 
            prompt_dir=prompt_dir, 
            tool_provider=tool_provider,
            memory=memory,
            memory_config=memory_config,
            log_level=log_level
        )
        
        # Initialize the LLMs for different roles
        try:
            self.planner_llm = self._get_llm('planner')
            self.executor_llm = self._get_llm('executor')
            self.evaluator_llm = self._get_llm('evaluator')
            self.reflector_llm = self._get_llm('reflector')
        except ValueError as e:
            self.logger.error("Failed to initialize LLMs: %s", e)
            raise ValueError("LLM initialization failed. Make sure required roles are defined in llm_configs.") from e

        self.max_trials = max_trials
        self.logger.info("Initialized Reflexion agent with max_trials=%d", max_trials)

    def build_graph(self) -> None:
        """Build the LangGraph state graph for the Reflexion agent.
        
        Nodes:
        - plan_action_with_memory: Generate a plan based on reflection memory.
        - execute_action: Execute the plan.
        - evaluate_outcome: Evaluate success/failure.
        - reflect_on_trial: Generate insights from the current trial.
        - update_reflection_memory: Add trial reflection to memory.
        - final_output: Format the final answer.
        
        Edges:
        - Standard path through nodes for a single trial.
        - Conditional loop back for multiple trials.
        """
        # Create the graph with our state type
        reflexion_graph = StateGraph(ReflexionState)

        # Define nodes
        reflexion_graph.add_node("plan_action_with_memory", self._plan_action_with_memory)
        reflexion_graph.add_node("execute_action", self._execute_action)
        reflexion_graph.add_node("evaluate_outcome", self._evaluate_outcome)
        reflexion_graph.add_node("reflect_on_trial", self._reflect_on_trial)
        reflexion_graph.add_node("update_reflection_memory", self._update_reflection_memory)
        reflexion_graph.add_node("final_output", self._prepare_final_output)

        # Define edges
        reflexion_graph.set_entry_point("plan_action_with_memory")
        reflexion_graph.add_edge("plan_action_with_memory", "execute_action")
        reflexion_graph.add_edge("execute_action", "evaluate_outcome")
        reflexion_graph.add_edge("evaluate_outcome", "reflect_on_trial")
        reflexion_graph.add_edge("reflect_on_trial", "update_reflection_memory")
        
        # Conditional edges from update_reflection_memory
        reflexion_graph.add_conditional_edges(
            "update_reflection_memory",
            self._should_continue_trials,
            {
                True: "plan_action_with_memory",  # If more trials needed, loop back
                False: "final_output"  # If no more trials needed, go to final output
            }
        )
        
        # Final edge
        reflexion_graph.add_edge("final_output", END)
        
        # Compile the graph
        try:
            self.graph = reflexion_graph.compile()
            self.logger.info("Reflexion agent graph compiled successfully.")
        except Exception as e:
            self.logger.error("Failed to compile Reflexion agent graph: %s", e)
            raise RuntimeError("Graph compilation failed") from e

    def _plan_action_with_memory(self, state: ReflexionState) -> Dict[str, Any]:
        """Generate a plan for the current trial based on reflection memory.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with a plan for the current trial.
        """
        self.logger.debug("Planning action for trial %d/%d", state["trial_count"], state["max_trials"])
        
        try:
            # Retrieve relevant memories if memory is enabled
            memories = self.sync_retrieve_memories(state["input_task"])
            memory_context = ""
            
            # Format memories for inclusion in the prompt
            if memories:
                memory_sections = []
                for memory_type, items in memories.items():
                    if items:
                        items_text = "\n- ".join([str(item) for item in items])
                        memory_sections.append(f"### {memory_type.capitalize()} Memories:\n- {items_text}")
                
                if memory_sections:
                    memory_context = "Relevant information from memory:\n\n" + "\n\n".join(memory_sections) + "\n\n"
                    self.logger.info(f"Retrieved {sum(len(items) for items in memories.values())} memories for planning")
            
            # Load the planning prompt template
            prompt = self._load_prompt_template("PlanActionStep")
            
            # Format the prompt with all relevant information
            formatted_prompt = prompt.invoke({
                "input_task": state["input_task"],
                "reflection_memory": "\n".join(state["reflection_memory"]) if state["reflection_memory"] else "No previous reflections available.",
                "trial_count": state["trial_count"],
                "max_trials": state["max_trials"],
                "memory_context": memory_context
            })
            
            # Get the planner response
            planner_response = self.planner_llm.invoke(formatted_prompt.to_messages())
            
            # Extract the plan from the response
            plan = planner_response.content
            
            self.logger.debug("Generated plan for trial %d: %s", state["trial_count"], 
                             plan[:100] + "..." if len(plan) > 100 else plan)
            
            # Increment trial count
            return {
                "current_plan": plan,
                "trial_count": state["trial_count"] + 1
            }
            
        except Exception as e:
            self.logger.error("Error generating plan: %s", e)
            # Return a fallback plan
            return {
                "current_plan": f"Trial {state['trial_count']}: Attempt to solve the task: {state['input_task']}",
                "trial_count": state["trial_count"] + 1
            }

    def _execute_action(self, state: ReflexionState) -> Dict[str, str]:
        """Execute the planned action.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with the result of the action.
        """
        self.logger.debug("Executing action for trial %d", state["trial_count"])
        
        try:
            # Get available tools if tool_provider is present
            tools_description = ""
            if self.tool_provider:
                tools = self.tool_provider.list_tools()
                if tools:
                    tool_descriptions = []
                    for tool in tools:
                        tool_descriptions.append(f"- {tool['name']}: {tool['description']}")
                    tools_description = "Available tools:\n" + "\n".join(tool_descriptions) + "\n\n"
                    tools_description += "To use a tool, include the following format in your response:\n"
                    tools_description += "USE_TOOL: tool_name(param1=value1, param2=value2)\n\n"
                    self.logger.info(f"Found {len(tools)} available tools for execution")
            
            # Load the execution prompt template
            prompt = self._load_prompt_template("ExecuteActionStep")
            
            # Format the prompt with the plan and task
            formatted_prompt = prompt.invoke({
                "input_task": state["input_task"],
                "current_plan": state["current_plan"],
                "tools_description": tools_description
            })
            
            # Get the executor response
            executor_response = self.executor_llm.invoke(formatted_prompt.to_messages())
            
            # Extract the action result
            action_result = executor_response.content
            
            # Check if the response contains a tool call
            if self.tool_provider:
                # Simple pattern matching for tool calls in the format: "USE_TOOL: tool_name(param1=value1, param2=value2)"
                tool_call_pattern = r"USE_TOOL:\s+(\w+)\(([^)]*)\)"
                tool_call_match = re.search(tool_call_pattern, action_result)
                
                # If a tool call is detected
                if tool_call_match:
                    tool_name = tool_call_match.group(1)
                    tool_params_str = tool_call_match.group(2)
                    
                    # Parse parameters
                    params = {}
                    param_matches = re.finditer(r"(\w+)\s*=\s*([^,]+)(?:,|$)", tool_params_str)
                    for match in param_matches:
                        param_name = match.group(1)
                        param_value = match.group(2).strip().strip('"\'')
                        params[param_name] = param_value
                    
                    try:
                        # Execute the tool
                        self.logger.info(f"Executing tool: {tool_name} with params {params}")
                        tool_result = self.tool_provider.execute_tool(tool_name, params)
                        
                        # Append tool result to the action result
                        action_result += f"\n\nTool Result: {tool_result}"
                    except Exception as e:
                        error_msg = f"\n\nError executing tool {tool_name}: {str(e)}"
                        action_result += error_msg
                        self.logger.error(f"Tool execution error: {str(e)}")
            
            self.logger.debug("Action result for trial %d: %s", state["trial_count"], 
                             action_result[:100] + "..." if len(action_result) > 100 else action_result)
            
            return {"action_result": action_result}
            
        except Exception as e:
            self.logger.error("Error executing action: %s", e)
            # Return a fallback result
            return {"action_result": "Failed to execute the planned action."}

    def _evaluate_outcome(self, state: ReflexionState) -> Dict[str, str]:
        """Evaluate the outcome of the action.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with evaluation of the action result.
        """
        self.logger.debug("Evaluating outcome for trial %d", state["trial_count"])
        
        try:
            # For a real-world task, this might involve external validation or metrics
            # Here we use an LLM to evaluate the action result
            
            # Simple evaluation prompt
            system_prompt = """You are a critical evaluator. Your task is to assess whether the provided solution 
            correctly and completely addresses the given task. Be specific about what works and what doesn't.
            Rate the solution on a scale from 1-10, where 10 is perfect."""
            
            user_prompt = f"""Task: {state['input_task']}
            
            Solution:
            {state['action_result']}
            
            Evaluate the solution. Does it correctly and completely solve the task?
            Start with a numerical rating (1-10), followed by your detailed assessment.
            """
            
            # Create messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Get evaluation response
            evaluation_response = self.evaluator_llm.invoke(messages)
            evaluation = evaluation_response.content
            
            self.logger.debug("Evaluation for trial %d: %s", state["trial_count"], 
                             evaluation[:100] + "..." if len(evaluation) > 100 else evaluation)
            
            return {"evaluation": evaluation}
            
        except Exception as e:
            self.logger.error("Error evaluating outcome: %s", e)
            # Return a fallback evaluation
            return {"evaluation": "Unable to properly evaluate the outcome."}

    def _reflect_on_trial(self, state: ReflexionState) -> Dict[str, str]:
        """Generate a reflection based on the current trial.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with reflection on the current trial.
        """
        self.logger.debug("Reflecting on trial %d", state["trial_count"])
        
        try:
            # Load the reflection prompt template
            prompt = self._load_prompt_template("ReflectionStep")
            
            # Format the prompt with all trial information
            formatted_prompt = prompt.invoke({
                "input_task": state["input_task"],
                "current_plan": state["current_plan"],
                "action_result": state["action_result"],
                "evaluation": state["evaluation"],
                "trial_count": state["trial_count"],
                "max_trials": state["max_trials"]
            })
            
            # Get the reflector response
            reflector_response = self.reflector_llm.invoke(formatted_prompt.to_messages())
            
            # Extract the reflection
            reflection = reflector_response.content
            
            # Save reflection to episodic memory if available
            if self.memory:
                self.sync_save_memory(
                    memory_type="episodic",
                    item={
                        "event_type": "reflexion_trial",
                        "task": state["input_task"],
                        "trial": state["trial_count"],
                        "plan": state["current_plan"],
                        "action_result": state["action_result"],
                        "evaluation": state["evaluation"],
                        "reflection": reflection
                    },
                    query=state["input_task"]
                )
                self.logger.debug("Saved reflection to episodic memory")
            
            self.logger.debug("Reflection for trial %d: %s", state["trial_count"], 
                             reflection[:100] + "..." if len(reflection) > 100 else reflection)
            
            return {"trial_reflection": reflection}
            
        except Exception as e:
            self.logger.error("Error generating reflection: %s", e)
            # Return a fallback reflection
            return {"trial_reflection": f"Trial {state['trial_count']} did not achieve the desired outcome."}

    def _update_reflection_memory(self, state: ReflexionState) -> Dict[str, List[str]]:
        """Update the reflection memory with the current trial reflection.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with updated reflection memory.
        """
        self.logger.debug("Updating reflection memory after trial %d", state["trial_count"])
        
        # Get the current reflection memory
        reflection_memory = state.get("reflection_memory", [])
        
        # Format the trial information for memory
        memory_entry = f"Trial {state['trial_count']} Reflection: {state['trial_reflection']}"
        
        # Add the new reflection to memory
        updated_memory = reflection_memory + [memory_entry]
        
        return {"reflection_memory": updated_memory}

    def _should_continue_trials(self, state: ReflexionState) -> bool:
        """Determine if more trials should be attempted.
        
        Args:
            state: The current graph state.
            
        Returns:
            True if more trials should be attempted, False otherwise.
        """
        # Check if we've reached the maximum number of trials
        if state["trial_count"] > state["max_trials"]:
            self.logger.info("Reached maximum number of trials (%d)", state["max_trials"])
            return False
        
        # Check if the evaluation indicates success
        # This is a simple heuristic - in a real system, you might use more sophisticated logic
        if state.get("evaluation", ""):
            evaluation = state["evaluation"].lower()
            
            # Look for indicators of success
            success_indicators = ["10/10", "9/10", "8/10", "successful", "perfect", "complete", "excellent"]
            if any(indicator in evaluation for indicator in success_indicators):
                self.logger.info("Solution appears successful, no more trials needed")
                return False
        
        # Continue with more trials
        self.logger.debug("Will continue with another trial")
        return True

    def _prepare_final_output(self, state: ReflexionState) -> Dict[str, str]:
        """Prepare the final output to return to the user.
        
        Args:
            state: The current graph state.
            
        Returns:
            Updated state with final answer.
        """
        self.logger.debug("Preparing final output after %d trials", state["trial_count"] - 1)
        
        # Use the most recent action result as the final answer
        final_answer = state.get("action_result", "No solution found.")
        
        # Save the final result to semantic memory if available
        if self.memory:
            # Determine success status based on evaluation
            success = False
            if state.get("evaluation", ""):
                evaluation = state["evaluation"].lower()
                success_indicators = ["10/10", "9/10", "8/10", "successful", "perfect", "complete", "excellent"]
                success = any(indicator in evaluation for indicator in success_indicators)
            
            self.sync_save_memory(
                memory_type="semantic",
                item={
                    "task_type": state["input_task"].split()[0:5],  # Use first few words as task type
                    "task": state["input_task"],
                    "solution": final_answer,
                    "trials": state["trial_count"] - 1,
                    "successful": success,
                    "reflection_history": state["reflection_memory"]
                },
                query=state["input_task"]
            )
            self.logger.debug("Saved final result to semantic memory")
        
        return {"final_answer": final_answer}

    def run(self, input_text: str) -> Dict[str, Any]:
        """Run the Reflexion agent on the given input.
        
        Args:
            input_text: The input task to process
            
        Returns:
            Dict containing the final result and metadata about the process.
        """
        if not self.graph:
            raise RuntimeError("Agent graph is not compiled.")
            
        # Initialize state
        initial_state: ReflexionState = {
            "input_task": input_text,
            "reflection_memory": [],
            "trial_count": 1,
            "max_trials": self.max_trials,
            "current_plan": None,
            "action_result": None,
            "evaluation": None,
            "trial_reflection": None,
            "final_answer": None
        }
        
        try:
            self.on_start()
            self.logger.info("Running Reflexion agent with input: %s", input_text[:100] + "..." if len(input_text) > 100 else input_text)
            
            # Run the graph
            final_state = self.graph.invoke(initial_state)
            
            # Extract the final result
            result = final_state.get("final_answer", "No final answer generated.")
            
            # Create metadata about the process
            metadata = {
                "trials_completed": final_state["trial_count"] - 1,
                "max_trials": final_state["max_trials"],
                "reflections": final_state["reflection_memory"]
            }
            
            self.logger.info("Reflexion agent completed successfully after %d trials", metadata["trials_completed"])
            return {
                "output": result,
                "metadata": metadata
            }
            
        except Exception as e:
            self.logger.error("Reflexion agent execution failed: %s", e, exc_info=True)
            return {"error": str(e)}
        finally:
            self.on_finish()

    def stream(self, input_text: str) -> Any:
        """Stream the Reflexion agent execution.
        
        Args:
            input_text: The input task to process
            
        Yields:
            State updates at each step of execution.
        """
        if not self.graph:
            raise RuntimeError("Agent graph is not compiled.")
            
        # Initialize state
        initial_state: ReflexionState = {
            "input_task": input_text,
            "reflection_memory": [],
            "trial_count": 1,
            "max_trials": self.max_trials,
            "current_plan": None,
            "action_result": None,
            "evaluation": None,
            "trial_reflection": None,
            "final_answer": None
        }
        
        try:
            self.on_start()
            self.logger.info("Streaming Reflexion agent with input: %s", input_text[:100] + "..." if len(input_text) > 100 else input_text)
            
            # Stream the graph execution
            for step_output in self.graph.stream(initial_state):
                yield step_output
                
        except Exception as e:
            self.logger.error("Reflexion agent streaming failed: %s", e, exc_info=True)
            yield {"error": str(e)}
        finally:
            self.on_finish()