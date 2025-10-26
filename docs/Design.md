# **Agent-Patterns Project: Design Document** 

**Version:** 2.1  
**Date:** April 7, 2025  
**Author:** *Michael Caughey*

**Status:** Draft

---

# CRITICAL IMPLEMENTATION REQUIREMENT
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only

---

## **1\. Overview and Goals**

### **1.1. Project Purpose**

The *agent-patterns* project provides a Python library of **reusable, extensible, and well-documented base classes** that encapsulate common AI agent workflows (or "patterns"). These patterns are implemented using [**LangGraph**](https://langchain.com/docs/langgraph) and rely on [**LangChain**](https://python.langchain.com/en/latest/) for Large Language Model (LLM) integrations, prompt management, and tool usage.

### **1.2. Scope**

We focus on **single-agent** and **multi-agent** design patterns that have proven useful across AI tasks, including:

* **ReAct (Tool Use)**

* **Plan & Solve**

* **Reflection**

* **Reflexion**

* **LLM Compiler**

* **REWOO (Worker-Solver)**

* **LATS (Language Agent Tree Search)**

* **Self-Discovery**

* **STORM (Topic Outlines + Multi-perspective Retrieval)**

Each pattern's goal is to reduce boilerplate and encourage consistent best practices. The library is especially useful for developers needing to quickly build or customize advanced AI workflows without reinventing the wheel.

### **1.3. Architectural Philosophy**

1. **Modular Base Classes:** One or more abstract base classes define common agent operations and Graph structures. Each pattern extends these bases to add specialized logic (e.g., planning steps, reflection loops).

2. **Externalized Configuration & Prompts:** Prompt templates, environment variables (e.g., model keys), and certain runtime parameters (e.g., max steps) are stored outside core code for easier customization.

3. **Developer Clarity:** Each pattern's responsibilities, methods, and usage are clearly documented so users know exactly which methods to override, how to pass custom prompts, and how to plug in specialized logic.

4. **Testability & Extensibility:** By separating pattern logic, tool definitions, and LLM configurations, the library is designed to be straightforward to test, maintain, and extend with new patterns.

---

## **2\. Repository & File Structure**

Here's a recommended layout for the *agent-patterns* repository. You can customize as needed, but we strongly recommend separating core abstractions, pattern implementations, prompts, and examples:

agent_patterns/  
├── core/  
│   ├── base_agent.py  
│   └── multi_agent_base.py  
├── patterns/  
│   ├── re_act_agent.py  
│   ├── plan_and_solve_agent.py  
│   ├── reflection_agent.py  
│   ├── reflexion_agent.py  
│   ├── llm_compiler_agent.py  
│   ├── rewoo_agent.py  
│   ├── lats_agent.py  
│   ├── self_discovery_agent.py  
│   └── storm_agent.py  
├── prompts/  
│   ├── reflection/  
│   │   ├── critic_prompt.md  
│   │   └── revision_prompt.md  
│   └── ...  
├── examples/  
│   ├── reflection_example.py  
│   └── plan_example.py  
├── tests/  
│   ├── test_reflection.py  
│   └── ...  
├── .env  
├── pyproject.toml  
└── README.md

**Key Directories**:

* `core/`: Abstract base classes and shared utilities (like prompt loading or logging).

* `patterns/`: Concrete agent patterns, each defined in its own file or sub-package.

* `prompts/`: Externalized prompt templates. Organized by pattern and step name.

* `examples/`: Minimal working examples of each pattern with usage instructions.

* `tests/`: Unit tests and integration tests for each pattern.

---

## **3\. Base Classes**

### **3.1. `BaseAgent` (Abstract)**

**Responsibility**: Provide core logic for orchestrating a single agent's workflow, including:

* Initializing an LLM or set of LLM roles (thinking, critic, etc.).

* Loading external prompt templates.

* Defining or compiling a [LangGraph](https://langchain.com/docs/langgraph) graph.

* Running or streaming the agent's process from input to output.

**Typical Usage**:

1. Subclass `BaseAgent` to create a new pattern.

2. Override required abstract methods (e.g., `build_graph()`, `run()`).

3. Use `self._get_llm(role)` to fetch the correct LLM for a particular role.

4. Use `self._load_prompt(step_name)` to retrieve external prompt templates.

5. Optionally override lifecycle hooks (`on_start()`, `on_finish()`) for logging.

\# core/base_agent.py  
import abc  
from typing import Any, Iterator  
from langgraph import CompiledGraph

class BaseAgent(abc.ABC):  
    def \_\_init\_\_(self, llm_configs: dict, prompt_dir: str = "prompts"):  
        """  
        :param llm_configs: Dictionary specifying provider, model, and roles.  
        :param prompt_dir: Directory for prompt templates.  
        """  
        self.llm_configs \= llm_configs  
        self.prompt_dir \= prompt_dir  
        self.graph: CompiledGraph \= None  \# set by self.build_graph()

        \# Subclass is expected to build/compile its graph  
        self.build_graph()

    @abc.abstractmethod  
    def build_graph(self) \-\> None:  
        """Construct or compile the LangGraph used by this agent pattern."""  
        pass

    @abc.abstractmethod  
    def run(self, input_data: Any) \-\> Any:  
        """  
        Run the agent to completion with the given input.  
        :param input_data: The user query or initial state.  
        :return: The final output or answer.  
        """  
        pass

    def stream(self, input_data: Any) \-\> Iterator\[Any\]:  
        """Optional streaming interface. Subclasses can override."""  
        yield self.run(input_data)

    def \_get_llm(self, role: str):  
        """Returns an LLM object for a given role based on llm_configs."""  
        \# Implementation detail: parse self.llm_configs to create the LLM.  
        \# E.g., llm_configs might have THINKING_MODEL_NAME, CRITIC_MODEL_NAME, etc.  
        pass

    def \_load_prompt(self, step_name: str) \-\> dict:  
        """  
        Loads a prompt template (system/user) from the prompts/ directory.  
        Subclasses can override to implement custom logic or fallback.  
        """  
        \# E.g. read from f"{self.prompt_dir}/{self.\_\_class\_\_.\_\_name\_\_}/{step_name}/\*.md"  
        \# Return a dict with {"system_prompt": "...", "user_prompt": "..."} or similar  
        return {}

**Design Notes**:

* `_get_llm(role)` and `_load_prompt(step_name)` are placeholders for actual prompt and LLM loading. This keeps the base class generic.

* `build_graph()` is where the pattern sets up its LangGraph nodes and transitions. The base class doesn't know the pattern's structure; that's left to subclasses.

* `run(input_data)` is the main method. Many patterns also define specialized sub-steps, but `run()` is the entry point from a developer's perspective.

### **3.2. `MultiAgentBase` (Abstract)**

**Responsibility**: Coordinates multiple sub-agents or roles. Provides:

* A container or registry for sub-agents.

* Methods for distributing tasks among them.

* Common logic for collating results.

\# core/multi_agent_base.py  
import abc  
from typing import List, Dict  
from .base_agent import BaseAgent

class MultiAgentBase(BaseAgent, abc.ABC):  
    def \_\_init\_\_(self, sub_agents: Dict\[str, BaseAgent\], \*\*kwargs):  
        """  
        :param sub_agents: Mapping of role \-\> agent instance (or agent class).  
        :param kwargs: Additional arguments passed to BaseAgent.  
        """  
        super().\_\_init\_\_(\*\*kwargs)  
        self.sub_agents \= sub_agents

    @abc.abstractmethod  
    def coordinate(self, task: str) \-\> str:  
        """  
        High-level method for distributing a task among sub-agents  
        and returning a unified final result.  
        """  
        pass

**Design Notes**:

* Like `BaseAgent`, but specialized for multi-agent workflows.

* Subclasses might override `run()` to call `coordinate()` under the hood.

* The `sub_agents` could be distinct specialized patterns (e.g., a coder agent, a researcher agent).

---

## **4\. Pattern Implementations**

Below are the core patterns. Each pattern extends `BaseAgent` (or `MultiAgentBase` if it needs multi-agent capabilities). We focus on prescriptive instructions so a developer knows exactly which methods to implement, how to handle prompts, etc.

### **4.1. ReAct (Reason + Act) Pattern**

#### **4.1.1. Overview**

**Goal**: Enable an agent to iteratively reason (produce a thought) and act (call a tool) until it arrives at a final answer. Particularly good for question-answering that requires external information or tools.

#### **4.1.2. Class: `ReActAgent`**

\# patterns/re_act_agent.py  
from typing import Any, Dict  
from agent_patterns.core.base_agent import BaseAgent  
from langgraph import StateGraph, CompiledGraph

class ReActAgent(BaseAgent):  
    def build_graph(self) \-\> None:  
        """  
        Construct a StateGraph for the ReAct cycle:  
          (thought) \-\> (action) \-\> (observation) \-\> check if done \-\> (thought) ...  
        """  
        sg \= StateGraph()

        \# Node definitions (Pseudo-code)  
        sg.add_node("thought_step", func=self.\_generate_thought_and_action)  
        sg.add_node("action_step", func=self.\_execute_action)  
        sg.add_node("observation_step", func=self.\_observation_handler)  
        sg.add_node("final_answer", func=self.\_format_final_answer)

        \# Edges & transitions  
        sg.add_edge("thought_step", "action_step")  
        sg.add_edge("action_step", "observation_step")  
        sg.add_edge("observation_step", "thought_step", condition=self.\_check_continue)  
        sg.add_edge("observation_step", "final_answer", condition=self.\_check_if_done)

        self.graph \= sg.compile()

    def run(self, input_data: Any) \-\> Any:  
        """  
        Entry point for the ReAct pattern.  
        Input: user query or problem statement.  
        Output: final answer after possibly multiple cycles.  
        """  
        initial_state \= {  
            "input": input_data,  
            "thought": "",  
            "action": {},  
            "observation": None,  
            "intermediate_steps": \[\],  
            "final_answer": None  
        }  
        result_state \= self.graph.run(initial_state)  
        return result_state\["final_answer"\]

    def \_generate_thought_and_action(self, state: Dict) \-\> Dict:  
        """  
        1\. Summarize current state & query LLM for next thought & action.  
        2\. Action is typically {tool_name: str, tool_input: str}.  
        """  
        prompt_data \= self.\_load_prompt("ThoughtStep")  \# system, user prompts  
        llm \= self.\_get_llm("thinking")  
        \# Compose a prompt, e.g. prompt_data\["system"\] + user info + state  
        \# LLM returns something like "Thought: I need to look up weather \-\> Action: search_tool('weather in Paris')"  
        \# Parse it into \`thought\` and \`action\` dict  
        \# ...  
        \# For illustration, assume we parse it:  
        thought_str \= "I need to check the weather"  
        action_dict \= {"tool_name": "search_tool", "tool_input": "weather in Paris"}  
        state\["thought"\] \= thought_str  
        state\["action"\] \= action_dict  
        state\["intermediate_steps"\].append((thought_str, action_dict, None))  
        return state

    def \_execute_action(self, state: Dict) \-\> Dict:  
        """Call the actual tool with the specified input."""  
        action \= state\["action"\]  
        tool_name \= action\["tool_name"\]  
        tool_input \= action\["tool_input"\]  
        \# Assume we have a tool registry or something similar  
        observation \= self.\_call_tool(tool_name, tool_input)  
        state\["observation"\] \= observation  
        \# Update the last step in intermediate_steps with the observation  
        if state\["intermediate_steps"\]:  
            last_thought, last_action, \_ \= state\["intermediate_steps"\]\[-1\]  
            state\["intermediate_steps"\]\[-1\] \= (last_thought, last_action, observation)  
        return state

    def \_observation_handler(self, state: Dict) \-\> Dict:  
        """We could do additional processing of the observation if needed."""  
        return state

    def \_check_continue(self, state: Dict) \-\> bool:  
        """Check if we should keep going. For now, always True unless found a final answer marker."""  
        \# Could parse state\["thought"\] for a 'FINAL ANSWER' marker, etc.  
        return not self.\_is_done(state)

    def \_check_if_done(self, state: Dict) \-\> bool:  
        return self.\_is_done(state)

    def \_is_done(self, state: Dict) \-\> bool:  
        """  
        Condition to exit the cycle: e.g. thought or observation indicates completion,  
        or a maximum step limit reached.  
        """  
        \# Implement custom logic, e.g., if "FINAL ANSWER:" in state\["thought"\] or step_count \> ...  
        return False

    def \_format_final_answer(self, state: Dict) \-\> Dict:  
        """  
        Optionally reformat or finalize the answer for the user.  
        """  
        \# E.g., parse the last thought for final answer  
        final \= "Here's the final answer from the chain of thought..."  
        state\["final_answer"\] \= final  
        return state

    def \_call_tool(self, tool_name: str, tool_input: Any) \-\> Any:  
        """Implement or delegate to a registry for tool calls."""  
        \# ...  
        return f"Mock result for {tool_input}"

#### **4.1.3. Implementation Notes:**

* **Prompts**: Stored in `prompts/ReActAgent/ThoughtStep/system.md` and `prompts/ReActAgent/ThoughtStep/user.md`.

* **Tool Integration**: `_call_tool()` is a stub that calls a registry. Implementation details can be externalized to a `ToolRegistry` utility.

* **Stop Condition**: `_check_continue()` vs. `_check_if_done()` demonstrate how to branch in LangGraph.

---

### **4.2. Plan & Solve Pattern**

#### **4.2.1. Overview**

**Goal**: Decouple planning from execution. Generate a multi-step plan, then sequentially (or in parallel) execute each step. Great for tasks that can be broken down predictably.

#### **4.2.2. Class: `PlanAndSolveAgent`**

\# patterns/plan_and_solve_agent.py  
from typing import Any, Dict, List  
from agent_patterns.core.base_agent import BaseAgent  
from langgraph import StateGraph

class PlanAndSolveAgent(BaseAgent):

    def build_graph(self) \-\> None:  
        sg \= StateGraph()  
        sg.add_node("plan_step", func=self.\_generate_plan)  
        sg.add_node("execute_step", func=self.\_execute_plan_step)  
        sg.add_node("check_completion", func=self.\_check_plan_completion)  
        sg.add_node("aggregate_results", func=self.\_aggregate_results)

        sg.add_edge("plan_step", "execute_step")  
        sg.add_edge("execute_step", "check_completion")  
        sg.add_edge("check_completion", "execute_step", condition=lambda s: not s\["plan_done"\])  
        sg.add_edge("check_completion", "aggregate_results", condition=lambda s: s\["plan_done"\])

        self.graph \= sg.compile()

    def run(self, input_data: Any) \-\> Any:  
        state \= {  
            "input_task": input_data,  
            "plan": \[\],  
            "current_step_index": 0,  
            "step_results": \[\],  
            "plan_done": False,  
            "final_result": None  
        }  
        final_state \= self.graph.run(state)  
        return final_state\["final_result"\]

    def \_generate_plan(self, state: Dict) \-\> Dict:  
        """  
        Use an LLM to create a structured plan (list of steps).  
        """  
        prompt_data \= self.\_load_prompt("PlanStep")  
        llm \= self.\_get_llm("planning")  
        \# e.g., plan_text \= llm.generate(...)  
        \# parse plan_text into a list of step dicts  
        plan \= \[{"step_description": "Step 1: Do X"}, {"step_description": "Step 2: Do Y"}\]  
        state\["plan"\] \= plan  
        return state

    def \_execute_plan_step(self, state: Dict) \-\> Dict:  
        idx \= state\["current_step_index"\]  
        plan \= state\["plan"\]  
        if idx \< len(plan):  
            step \= plan\[idx\]  
            result \= self.\_run_single_step(step, state)  
            state\["step_results"\].append(result)  
            state\["current_step_index"\] \+= 1  
        return state

    def \_check_plan_completion(self, state: Dict) \-\> Dict:  
        if state\["current_step_index"\] \>= len(state\["plan"\]):  
            state\["plan_done"\] \= True  
        return state

    def \_aggregate_results(self, state: Dict) \-\> Dict:  
        """  
        Combine step results into a final answer, possibly using another LLM or direct logic.  
        """  
        final \= " ".join(state\["step_results"\])  
        state\["final_result"\] \= f"Plan & Solve final answer:\\n{final}"  
        return state

    def \_run_single_step(self, step: Dict, state: Dict) \-\> Any:  
        """  
        Could call an LLM or a tool depending on step content.  
        """  
        \# e.g., parse step\["step_description"\], do the action  
        return f"Executed: {step\['step_description'\]}"

#### **4.2.3. Implementation Details**

* **Plan Representation**: A list of dictionaries in `state["plan"]`. Each item is one sub-task. Could contain tool calls, LLM prompts, etc.

* **Prompt Step**: `_load_prompt("PlanStep")` retrieves the planning instructions (system and user prompts).

* **Execution Logic**: `_run_single_step` can handle a wide variety of actions. This is a key customization point.

* **Parallel Execution**: For advanced usage, you can extend `_execute_plan_step` to dispatch multiple steps in parallel if they have no dependencies. That is an optional future enhancement.

---

### **4.3. Reflection Pattern**

#### **4.3.1. Overview**

**Goal**: After generating an initial answer, the agent critiques it and refines if necessary. Typically uses a separate LLM or prompt for critique.

#### **4.3.2. Class: `ReflectionAgent`**

\# patterns/reflection_agent.py  
from agent_patterns.core.base_agent import BaseAgent  
from langgraph import StateGraph

class ReflectionAgent(BaseAgent):

    def build_graph(self) \-\> None:  
        sg \= StateGraph()  
        sg.add_node("generate_initial", func=self.\_generate_initial_output)  
        sg.add_node("reflect", func=self.\_reflect_on_output)  
        sg.add_node("check_refine", func=self.\_check_refinement_needed)  
        sg.add_node("refine", func=self.\_refine_output)  
        sg.add_node("final_output", func=lambda s: s)

        \# Edges  
        sg.add_edge("generate_initial", "reflect")  
        sg.add_edge("reflect", "check_refine")  
        sg.add_edge("check_refine", "refine", condition=lambda s: s\["needs_refinement"\])  
        sg.add_edge("check_refine", "final_output", condition=lambda s: not s\["needs_refinement"\])  
        sg.add_edge("refine", "final_output")

        self.graph \= sg.compile()

    def run(self, input_data: str):  
        state \= {  
            "input_task": input_data,  
            "initial_output": None,  
            "reflection": None,  
            "refined_output": None,  
            "needs_refinement": False,  
            "final_answer": None  
        }  
        final_state \= self.graph.run(state)  
        return final_state.get("final_answer")

    def \_generate_initial_output(self, state):  
        """Generate a first attempt using the main LLM."""  
        prompt_data \= self.\_load_prompt("Generate")  
        llm \= self.\_get_llm("documentation")  \# or "thinking", depending  
        \# result \= llm.predict(...)  
        result \= f"Initial answer to {state\['input_task'\]}"  
        state\["initial_output"\] \= result  
        return state

    def \_reflect_on_output(self, state):  
        """Use a separate reflection model to critique the initial output."""  
        critic_prompt \= self.\_load_prompt("Reflect")  
        critic_llm \= self.\_get_llm("reflection")  
        \# reflection_text \= critic_llm.predict(state\["initial_output"\])  
        reflection_text \= "Critique: The answer is incomplete; mention more details."  
        state\["reflection"\] \= reflection_text  
        return state

    def \_check_refinement_needed(self, state):  
        """Decide if refinement is necessary."""  
        \# simple heuristic: if 'incomplete' in reflection \-\> refine  
        state\["needs_refinement"\] \= "incomplete" in state\["reflection"\].lower()  
        return state

    def \_refine_output(self, state):  
        """Generate a refined output using the reflection text."""  
        refine_prompt \= self.\_load_prompt("Refine")  
        llm \= self.\_get_llm("documentation")  
        \# refined \= llm.predict(f"{state\['initial_output'\]}\\nCritique: {state\['reflection'\]}")  
        refined \= f"Refined answer (added details) for {state\['input_task'\]}"  
        state\["refined_output"\] \= refined  
        state\["final_answer"\] \= refined  
        return state

#### **4.3.3. Implementation Guidelines**

* **Prompts**:

  * `Generate`: The system and user prompts for initial answer generation.

  * `Reflect`: The system/user prompts for the critic LLM to generate self-critique.

  * `Refine`: The system/user prompts for how to incorporate the critique into a new answer.

* **Refinement Iterations**: For now, only one cycle is shown. You can add loopback edges to allow multiple iterations up to a max count.

* **Logic Externalization**: `_check_refinement_needed` can be external or read from a config if the logic is more complex.

---

## **4.4. Reflexion Pattern**

### **4.4.1. Overview**

**Goal:** Enable iterative problem-solving where the agent revisits past mistakes and successes across *multiple trials*, storing "lessons" in a persistent "reflection memory." After each trial (or "episode"), the agent logs insights—why something worked or failed—so that next time it encounters a similar situation, it can consult those insights to improve performance.

This differs from a simple one-pass "Reflection" pattern by introducing:

* **Reflection Memory**: A structured store of lessons or heuristics the agent can read before generating the next attempt.

* **Multi-Trial Loop**: The agent repeatedly attempts a task (or sub-task), reflecting after each attempt and incorporating those reflections into a persistent memory.

It's most useful when:

* The agent must refine a partial solution over many tries.

* We want a "learning effect" across attempts (although it's local to the session, not a global learned model).

  ### **4.4.2. Class: `ReflexionAgent`**

Below is a sketch for a builder's guide, showing how to build the LangGraph for multiple attempts:

\# patterns/reflexion_agent.py

from typing import Any, Dict

from agent_patterns.core.base_agent import BaseAgent

from langgraph import StateGraph, CompiledGraph

class ReflexionAgent(BaseAgent):

    def build_graph(self) \-\> None:

        sg \= StateGraph()

        

        \# 1\) plan_action_with_memory \-\> 2\) execute_action \-\> 3\) evaluate_outcome

        \#    \-\> 4\) reflect_on_trial \-\> 5\) update_reflection_memory 

        \#    \-\> check if done or not \-\> loop or final

        \#

        \# We illustrate a loop from a 'trial' node back to the top, up to a max trial count

        \# or until the agent decides it's done.

        

        sg.add_node("plan_action_with_memory", func=self.\_plan_action_with_memory)

        sg.add_node("execute_action", func=self.\_execute_action)

        sg.add_node("evaluate_outcome", func=self.\_evaluate_outcome)

        sg.add_node("reflect_on_trial", func=self.\_reflect_on_trial)

        sg.add_node("update_reflection_memory", func=self.\_update_reflection_memory)

        sg.add_node("final_output", func=lambda s: s)

        \# Edges for the trial loop:

        sg.add_edge("plan_action_with_memory", "execute_action")

        sg.add_edge("execute_action", "evaluate_outcome")

        sg.add_edge("evaluate_outcome", "reflect_on_trial")

        sg.add_edge("reflect_on_trial", "update_reflection_memory")

        \# Condition: either loop to "plan_action_with_memory" (new trial) or exit

        sg.add_edge("update_reflection_memory", "plan_action_with_memory",

                    condition=self.\_continue_trials)

        sg.add_edge("update_reflection_memory", "final_output",

                    condition=lambda s: not self.\_continue_trials(s))

        self.graph \= sg.compile()

    def run(self, input_data: Any) \-\> Any:

        \# The agent will attempt multiple trials, storing reflection each time

        initial_state \= {

            "input_task": input_data,

            "reflection_memory": \[\],     \# list of string insights or structured data

            "trial_count": 0,

            "max_trials": 3,            \# or read from config

            "outcome": None,

            "final_answer": None

        }

        final_state \= self.graph.run(initial_state)

        return final_state\["final_answer"\]

    def \_plan_action_with_memory(self, state: Dict) \-\> Dict:

        """

        Reads reflection_memory to inform the next planned action or approach.

        Typically uses a 'thinking' LLM or specialized role.

        """

        \# Combine the user input \+ reflection memory in a prompt

        \# e.g., "Here are your previous lessons: \[...\]. Now plan your next step for the task."

        \# ...

        state\["trial_count"\] \+= 1

        return state

    def \_execute_action(self, state: Dict) \-\> Dict:

        """

        Actually try to solve the task, possibly by calling a tool or generating text.

        """

        \# ...

        \# store a raw result in state\["outcome"\]

        state\["outcome"\] \= "Attempt result or partial solution"

        return state

    def \_evaluate_outcome(self, state: Dict) \-\> Dict:

        """

        Critically evaluate how the attempt went. 

        Could be LLM-based or an environment check if we have a known correct result.

        """

        \# ...

        \# e.g. store 'success', 'failure', or details in state

        state\["evaluation"\] \= "failure"  \# or success

        return state

    def \_reflect_on_trial(self, state: Dict) \-\> Dict:

        """

        Summarize what was learned from the outcome to be stored in reflection memory.

        Typically a reflection LLM is used here.

        """

        reflection_llm \= self.\_get_llm("reflection")

        \# reflection_text \= reflection_llm.predict( ... )

        reflection_text \= "If outcome is X, we should do Y next time."

        state\["trial_reflection"\] \= reflection_text

        return state

    def \_update_reflection_memory(self, state: Dict) \-\> Dict:

        """

        Append newly generated reflection to reflection_memory.

        """

        state\["reflection_memory"\].append(state\["trial_reflection"\])

        return state

    def \_continue_trials(self, state: Dict\]) \-\> bool:

        """

        Decide if we need another trial: e.g. not done or trial_count \< max_trials

        or outcome wasn't successful.

        """

        if state\["trial_count"\] \>= state\["max_trials"\]:

            \# finalize or forcibly stop

            state\["final_answer"\] \= f"Best attempt result: {state\['outcome'\]}"

            return False

        \# If outcome was 'success', we can stop early:

        if state.get("evaluation") \== "success":

            state\["final_answer"\] \= f"Successful result: {state\['outcome'\]}"

            return False

        \# Otherwise, do another trial

        return True

**Builder Tips:**

1. **Memory Format**: Store reflections as a list of strings or structured JSON, so future prompts can incorporate them easily.

2. **Trial Loop**: Provide a `max_trials` guard. Another approach is to let an LLM decide to continue or not by analyzing the outcome.

3. **Prompts**:

   * *PlanActionWithMemory* step: merges `reflection_memory` with the current task to plan the next move.

   * *ReflectOnTrial* step: a specialized prompt for self-critique.

   ---

   ## **4.5. LLMCompiler Pattern**

   ### **4.5.1. Overview**

**Goal:** Treat your entire multi-tool workflow like a "compiler." The agent constructs an **execution graph** from the user task and the available tools, then **executes** the graph in an optimized order—possibly in parallel. This can speed up tasks requiring multiple independent tool calls or sub-queries.

### **4.5.2. Key Components**

1. **Planner**: An LLM that inspects the user's request plus the "tool signatures" to generate a DAG (Directed Acyclic Graph) describing the execution sequence.

2. **Executor**: Runs each node in topological order (or parallel if no dependencies).

3. **Synthesis**: After all nodes are complete, merges the intermediate results into a final answer.

   ### **4.5.3. Class: `LLMCompilerAgent`**

\# patterns/llm_compiler_agent.py

from typing import Any, Dict

from agent_patterns.core.base_agent import BaseAgent

from langgraph import StateGraph

class LLMCompilerAgent(BaseAgent):

    def build_graph(self) \-\> None:

        sg \= StateGraph()

        \# We'll define a simplified approach:

        \# 1\) planner_generate_graph \-\> 2\) executor_dispatch

        \# \-\> 3\) check_if_done \-\> 4\) synthesize_result

        \# \-\> loop back to executor_dispatch if not done.

        sg.add_node("planner_generate_graph", func=self.\_planner_generate_graph)

        sg.add_node("executor_dispatch", func=self.\_executor_dispatch)

        sg.add_node("check_completion", func=self.\_check_completion)

        sg.add_node("synthesize_result", func=self.\_synthesize_result)

        sg.add_edge("planner_generate_graph", "executor_dispatch")

        sg.add_edge("executor_dispatch", "check_completion")

        sg.add_edge("check_completion", "executor_dispatch", condition=lambda s: not s\["graph_done"\])

        sg.add_edge("check_completion", "synthesize_result", condition=lambda s: s\["graph_done"\])

        self.graph \= sg.compile()

    def run(self, input_data: Any) \-\> Any:

        state \= {

            "input_task": input_data,

            "tool_schemas": self.\_define_tool_schemas(),

            "execution_graph": None,       \# The DAG structure

            "node_results": {},

            "graph_done": False,

            "final_answer": None

        }

        final_state \= self.graph.run(state)

        return final_state\["final_answer"\]

    def \_define_tool_schemas(self) \-\> Dict:

        """

        Provide formal definitions (JSON schemas, parameter types, etc.) for each tool.

        The planner LLM can see these definitions to figure out node dependencies.

        """

        \# Example: a search tool \+ calculator, each with some required inputs

        return {

            "search_tool": {

                "input_params": \["query"\],

                "output": "search_results"

            },

            "calculator_tool": {

                "input_params": \["expression"\],

                "output": "numeric_result"

            }

        }

    def \_planner_generate_graph(self, state: Dict) \-\> Dict:

        """

        Calls an LLM to produce a plan or DAG (like a JSON specifying the needed tools,

        the order, and any dependencies).

        """

        planner_llm \= self.\_get_llm("thinking")

        \# plan_json \= planner_llm.predict( ... ) 

        \# parse as Python structure

        \# For demonstration:

        example_graph \= {

            "nodes": \[

                {"id": "node1", "tool": "search_tool", "depends_on": \[\], "args": {"query": "some query"}},

                {"id": "node2", "tool": "calculator_tool", "depends_on": \["node1"\], "args": {"expression": "2+2"}}

            \]

        }

        state\["execution_graph"\] \= example_graph

        return state

    def \_executor_dispatch(self, state: Dict) \-\> Dict:

        """

        Look for any nodes whose dependencies are satisfied and haven't been run yet.

        Execute them in parallel or one by one, storing results in node_results.

        """

        graph \= state\["execution_graph"\]

        node_results \= state\["node_results"\]

        for node in graph\["nodes"\]:

            node_id \= node\["id"\]

            if node_id in node_results:

                continue  \# already executed

            \# check dependencies

            if all(dep in node_results for dep in node\["depends_on"\]):

                \# we can execute this node

                res \= self.\_execute_tool(node\["tool"\], node\["args"\])

                node_results\[node_id\] \= res

        return state

    def \_check_completion(self, state: Dict) \-\> Dict:

        graph \= state\["execution_graph"\]

        node_results \= state\["node_results"\]

        all_ids \= \[n\["id"\] for n in graph\["nodes"\]\]

        \# If we've computed results for all nodes, we are done

        state\["graph_done"\] \= all(id_ in node_results for id_ in all_ids)

        return state

    def \_synthesize_result(self, state: Dict) \-\> Dict:

        """

        Combine the final node outputs into a human-readable or LLM-based answer.

        """

        \# E.g., we can ask an LLM to produce a final summary:

        summary_llm \= self.\_get_llm("documentation")

        \# final_answer \= summary_llm.predict(...)

        final_answer \= "Final result compiled from node outputs."

        state\["final_answer"\] \= final_answer

        return state

    def \_execute_tool(self, tool_name: str, args: Dict) \-\> Any:

        """

        Actually run the named tool. Could be direct Python or an API call. 

        """

        \# ...

        return f"Mock result of {tool_name} with {args}"

**Builder Tips:**

* **Tool Schemas**: Provide enough detail so the planner LLM can figure out the dependency graph.

* **Parallelization**: For real concurrency, consider LangGraph's parallel node support or an async approach.

* **Graph Representation**: A typical structure is `{"nodes": [ {id, tool, depends_on, args}, ... ]}`.

  ---

  ## **4.6. REWOO (Reason Without Observation / Worker-Solver) Pattern**

  ### **4.6.1. Overview**

**Goal:** Separate the "thinking" LLM (the Worker) from the actual tool-execution step (the Solver). The Worker plans out calls and placeholders for results *without* seeing their real outputs initially; then the Solver (often a cheaper or specialized model, or direct code) executes them. Finally, the Worker integrates the actual results back in a final pass.

This can reduce cost or latency if the main LLM is expensive—because you can run multiple Solver calls in parallel, only calling the expensive Worker again once all results are ready.

### **4.6.2. Class: `REWOOAgent`**

\# patterns/rewoo_agent.py

from typing import Any, Dict, List

from agent_patterns.core.base_agent import BaseAgent

from langgraph import StateGraph

class REWOOAgent(BaseAgent):

    def build_graph(self) \-\> None:

        sg \= StateGraph()

        

        \# 1\) worker_plan \-\> 2\) dispatch_to_solvers \-\> 3\) solver_execute (parallel or batch)

        \# 4\) collect_solver_results \-\> 5\) worker_integrate \-\> final

        sg.add_node("worker_plan", func=self.\_worker_plan)

        sg.add_node("dispatch_to_solvers", func=self.\_dispatch_to_solvers)

        sg.add_node("solver_execute", func=self.\_solver_execute)    \# could also be multiple parallel nodes

        sg.add_node("collect_solver_results", func=self.\_collect_solver_results)

        sg.add_node("worker_integrate", func=self.\_worker_integrate)

        sg.add_node("final_output", func=lambda s: s)

        sg.add_edge("worker_plan", "dispatch_to_solvers")

        sg.add_edge("dispatch_to_solvers", "solver_execute")

        sg.add_edge("solver_execute", "collect_solver_results")

        sg.add_edge("collect_solver_results", "worker_integrate")

        sg.add_edge("worker_integrate", "final_output")

        self.graph \= sg.compile()

    def run(self, input_data: Any) \-\> Any:

        state \= {

            "input_task": input_data,

            "worker_plan_template": "",    \# e.g. "Find CEO \-\> {ceo}, also get Stock \-\> {price}"

            "solver_requests": \[\],         \# list of tool calls

            "solver_results": {},          \# mapping placeholders \-\> real data

            "final_answer": None

        }

        final_state \= self.graph.run(state)

        return final_state\["final_answer"\]

    def \_worker_plan(self, state: Dict) \-\> Dict:

        """

        The 'thinking' LLM: produce a plan with placeholders for solver outputs.

        """

        thinking_llm \= self.\_get_llm("thinking")

        \# Example: 

        \# plan_template \= thinking_llm.predict("Given the user request, lay out the steps 

        \#   with placeholders for each solver call result...")

        plan_template \= "Find CEO \-\> {ceo_name}; Check stock \-\> {stock_price}"

        solver_requests \= \[

            {"placeholder": "ceo_name", "tool": "search_tool", "params": {"query": "CEO of Company X"}},

            {"placeholder": "stock_price", "tool": "stock_api_tool", "params": {"symbol": "COMPX"}}

        \]

        state\["worker_plan_template"\] \= plan_template

        state\["solver_requests"\] \= solver_requests

        return state

    def \_dispatch_to_solvers(self, state: Dict) \-\> Dict:

        """

        Possibly break solver_requests into parallel tasks. We'll keep it simple.

        """

        return state

    def \_solver_execute(self, state: Dict) \-\> Dict:

        """

        Let each solver_request be executed, presumably by a cheaper model or direct code.

        """

        for req in state\["solver_requests"\]:

            placeholder \= req\["placeholder"\]

            tool_name \= req\["tool"\]

            params \= req\["params"\]

            \# call the solver

            result \= self.\_call_solver(tool_name, params)

            state\["solver_results"\]\[placeholder\] \= result

        return state

    def \_collect_solver_results(self, state: Dict) \-\> Dict:

        """

        If parallel tasks were used, gather them here. We're just storing them in solver_results. 

        """

        return state

    def \_worker_integrate(self, state: Dict) \-\> Dict:

        """

        The Worker LLM now sees the actual solver results inserted into the original plan template.

        """

        integration_llm \= self.\_get_llm("thinking")

        plan_template \= state\["worker_plan_template"\]

        solver_data \= state\["solver_results"\]

        \# e.g. "Find CEO \-\> {ceo_name}; ..." \-\> "Find CEO \-\> Jane Doe; ..." 

        \# Then feed that to the LLM for final phrasing or formatting

        filled_in_text \= plan_template

        for placeholder, val in solver_data.items():

            filled_in_text \= filled_in_text.replace(f"{{{placeholder}}}", str(val))

        \# final_answer \= integration_llm.predict(f"Integrate the following filled plan:\\n {filled_in_text}")

        final_answer \= f"Final integrated result:\\n{filled_in_text}"

        state\["final_answer"\] \= final_answer

        return state

    def \_call_solver(self, tool_name: str, params: Dict):

        """

        Actually run the solver step. For example, direct Python calls or a smaller LLM.

        """

        return f"Mock result for {tool_name} with {params}"

**Builder Tips:**

1. **Worker vs. Solver**:

   * The Worker uses a more capable (and expensive) LLM to *plan* and *integrate*.

   * The Solver might be a cheaper model or direct code.

2. **Placeholders**: Represent them as `{ceo_name}`, etc. The Worker never sees real data until the final integration step.

3. **Parallel Execution**: You can spin off a parallel sub-graph for each solver request if desired.

   ---

   ## **4.7. LATS (Language Agent Tree Search) Pattern**

   ### **4.7.1. Overview**

**Goal:** Perform a **tree search** over possible reasoning paths. This is inspired by techniques like Monte Carlo Tree Search (MCTS). Instead of following a single ReAct chain, the agent can **expand** multiple possible next steps, **evaluate** them, and use **backpropagation** of scores to select the best path.

### **4.7.2. Class: `LATSAgent`**

\# patterns/lats_agent.py

from typing import Any, Dict

from agent_patterns.core.base_agent import BaseAgent

from langgraph import StateGraph

class LATSAgent(BaseAgent):

    def build_graph(self) \-\> None:

        sg \= StateGraph()

        

        \# Minimal skeleton:

        \# 1\) select_node \-\> 2\) expand_node \-\> 3\) evaluate_node \-\> 4\) backpropagate

        \#    \-\> check_search_budget \-\> loop or choose_best_path \-\> generate_final_output

        sg.add_node("select_node", func=self.\_select_node)

        sg.add_node("expand_node", func=self.\_expand_node)

        sg.add_node("evaluate_node", func=self.\_evaluate_node)

        sg.add_node("backpropagate", func=self.\_backpropagate)

        sg.add_node("check_budget", func=self.\_check_budget)

        sg.add_node("choose_best_path", func=self.\_choose_best_path)

        sg.add_node("generate_final_output", func=self.\_generate_final_output)

        sg.add_edge("select_node", "expand_node")

        sg.add_edge("expand_node", "evaluate_node")

        sg.add_edge("evaluate_node", "backpropagate")

        sg.add_edge("backpropagate", "check_budget")

        sg.add_edge("check_budget", "select_node", condition=lambda s: not s\["budget_exhausted"\])

        sg.add_edge("check_budget", "choose_best_path", condition=lambda s: s\["budget_exhausted"\])

        sg.add_edge("choose_best_path", "generate_final_output")

        self.graph \= sg.compile()

    def run(self, input_data: Any) \-\> Any:

        state \= {

            "input_task": input_data,

            "search_tree": self.\_init_tree(input_data),

            "budget_exhausted": False,

            "iterations": 0,

            "max_iterations": 10,

            "best_path": None,

            "final_answer": None

        }

        final_state \= self.graph.run(state)

        return final_state\["final_answer"\]

    def \_init_tree(self, input_data):

        """Create the root of the search tree with the initial problem state."""

        return {

            "root": {

                "state_description": f"Start for {input_data}",

                "children": \[\],

                "visits": 0,

                "value": 0.0

            }

        }

    def \_select_node(self, state: Dict) \-\> Dict:

        """

        Picks a promising node to expand based on a policy (e.g., UCB).

        """

        \# ...

        state\["current_node"\] \= "root"  \# or some selection logic

        return state

    def \_expand_node(self, state: Dict) \-\> Dict:

        """

        Use an LLM to propose next steps (child nodes).

        """

        \# ...

        \# children \= LLM call to generate possible next actions

        \# attach them to the selected node

        return state

    def \_evaluate_node(self, state: Dict) \-\> Dict:

        """

        For each newly expanded node, run an LLM or heuristic to estimate a 'value'

        indicating how promising that path is.

        """

        \# ...

        return state

    def \_backpropagate(self, state: Dict) \-\> Dict:

        """

        Update ancestors' values and visits. 

        """

        \# ...

        return state

    def \_check_budget(self, state: Dict) \-\> Dict:

        """

        If we've done enough iterations, mark budget_exhausted.

        """

        state\["iterations"\] \+= 1

        if state\["iterations"\] \>= state\["max_iterations"\]:

            state\["budget_exhausted"\] \= True

        return state

    def \_choose_best_path(self, state: Dict) \-\> Dict:

        """

        From the root, pick the child with the highest average value or visits, etc.

        """

        state\["best_path"\] \= "some best path"

        return state

    def \_generate_final_output(self, state: Dict) \-\> Dict:

        """

        Possibly run a final LLM to write up the chosen path or final solution.

        """

        final_llm \= self.\_get_llm("thinking")

        \# final_text \= final_llm.predict(...)

        final_text \= f"Final answer based on best path: {state\['best_path'\]}"

        state\["final_answer"\] \= final_text

        return state

**Builder Tips:**

* **Search Tree Representation**: Usually a nested dict or custom Node class with fields like `children`, `value`, `visits`, etc.

* **LLM Usage**:

  * `_expand_node` might call an LLM to propose 2–5 possible next steps (like partial solutions).

  * `_evaluate_node` might call a different "evaluation" or "reflection" LLM to score each child's outcome.

* **Iteration Limit**: `max_iterations` or a time budget.

* **Backpropagation**: Summarize child values up to the parent.

  ---

  ## **4.8. Self-Discovery Pattern**

  ### **4.8.1. Overview**

**Goal:** Let the agent *dynamically create or select "reasoning modules"* for the current task. It first identifies which known problem-solving heuristics or "modules" apply, then **adapts** them to the specifics of the query, and **executes** them in a structured manner. Think of it as an agent that "pulls in relevant internal methods" (some big library of ways it's learned to reason) before diving in.

### **4.8.2. Class: `SelfDiscoveryAgent`**

\# patterns/self_discovery_agent.py

from typing import Any, Dict, List

from agent_patterns.core.base_agent import BaseAgent

from langgraph import StateGraph

class SelfDiscoveryAgent(BaseAgent):

    def build_graph(self) \-\> None:

        sg \= StateGraph()

        \# 1\) discover_or_select_modules \-\> 2\) adapt_modules \-\> 3\) plan_reasoning_steps

        \# \-\> 4\) execute_reasoning_step (loop for each step) \-\> final

        sg.add_node("discover_or_select_modules", func=self.\_discover_or_select_modules)

        sg.add_node("adapt_modules", func=self.\_adapt_modules)

        sg.add_node("plan_reasoning_steps", func=self.\_plan_reasoning_steps)

        sg.add_node("execute_reasoning_step", func=self.\_execute_reasoning_step)

        sg.add_node("check_completion", func=self.\_check_completion)

        sg.add_node("final_output", func=lambda s: s)

        \# Linear up to planning

        sg.add_edge("discover_or_select_modules", "adapt_modules")

        sg.add_edge("adapt_modules", "plan_reasoning_steps")

        

        \# Now, for each step in the plan, call execute_reasoning_step \-\> check_completion

        sg.add_edge("plan_reasoning_steps", "execute_reasoning_step")

        sg.add_edge("execute_reasoning_step", "check_completion")

        \# If not done, loop back

        sg.add_edge("check_completion", "execute_reasoning_step", condition=lambda s: not s\["done_with_plan"\])

        sg.add_edge("check_completion", "final_output", condition=lambda s: s\["done_with_plan"\])

        self.graph \= sg.compile()

    def run(self, input_data: Any) \-\> Any:

        state \= {

            "input_task": input_data,

            "available_modules": self.\_load_module_library(),

            "selected_modules": \[\],

            "adapted_modules": \[\],

            "reasoning_plan": \[\],

            "plan_index": 0,

            "done_with_plan": False,

            "final_answer": None

        }

        final_state \= self.graph.run(state)

        return final_state\["final_answer"\]

    def \_load_module_library(self) \-\> List\[str\]:

        """

        Potentially a big library of reasoning heuristics or re-usable code fragments.

        In a real system, these might be external knowledge or local 'playbooks.'

        """

        return \["moduleA", "moduleB", "moduleC"\]

    def \_discover_or_select_modules(self, state: Dict) \-\> Dict:

        """

        The agent picks relevant modules from the library for this task, possibly via an LLM.

        """

        \# ...

        state\["selected_modules"\] \= \["moduleA"\]

        return state

    def \_adapt_modules(self, state: Dict) \-\> Dict:

        """

        Tailor the selected modules to the specifics of the input task, e.g. rewriting them 

        or customizing them with domain knowledge.

        """

        \# ...

        state\["adapted_modules"\] \= \["moduleA_for_this_task"\]

        return state

    def \_plan_reasoning_steps(self, state: Dict) \-\> Dict:

        """

        Create a step-by-step plan applying the adapted modules in a certain order.

        """

        \# ...

        state\["reasoning_plan"\] \= \[

            {"description": "Apply moduleA_for_this_task to parse the input"},

            {"description": "Analyze the partial result for solution"}

        \]

        state\["plan_index"\] \= 0

        return state

    def \_execute_reasoning_step(self, state: Dict) \-\> Dict:

        plan \= state\["reasoning_plan"\]

        i \= state\["plan_index"\]

        if i \< len(plan):

            step_desc \= plan\[i\]\["description"\]

            \# Possibly call an LLM or function representing the adapted module

            \# e.g.: step_output \= self.\_call_module(step_desc)

            step_output \= f"Executed step: {step_desc}"

            state\["plan_index"\] \+= 1

            \# optional: store partial results

        return state

    def \_check_completion(self, state: Dict) \-\> Dict:

        if state\["plan_index"\] \>= len(state\["reasoning_plan"\]):

            state\["done_with_plan"\] \= True

            state\["final_answer"\] \= "All modules applied, final result here\!"

        else:

            state\["done_with_plan"\] \= False

        return state

**Builder Tips:**

* **Module Library**: Could be a real database or a file with multiple "functions" or heuristics.

* **Selection**: Use a specialized LLM prompt: "Given the user's goal, pick the best modules from this list."

* **Adaptation**: Another LLM prompt that modifies or extends the selected module for the user's domain.

* **Plan**: Then proceed like a "Plan & Solve," but specifically using your newly discovered/adapted modules.

  ---

  ## **4.9. STORM (Synthesis of Topic Outlines Through Retrieval and Multi-perspective Questioning)**

  ### **4.9.1. Overview**

**Goal:** Produce long-form, multi-perspective articles or reports on a topic by systematically:

1. Generating a **topic outline**.

2. Creating **questions** from multiple viewpoints or "personas" (scientist, policymaker, etc.).

3. **Retrieving** relevant info for each question (via tools or a knowledge base).

4. **Synthesizing** all retrieved data into a structured output.

   ### **4.9.2. Class: `STORMAgent`**

\# patterns/storm_agent.py

from typing import Any, Dict, List

from agent_patterns.core.base_agent import BaseAgent

from langgraph import StateGraph

class STORMAgent(BaseAgent):

    def build_graph(self) \-\> None:

        sg \= StateGraph()

        

        \# Stage 1: (outline) \-\> (generate_perspectives) \-\> (generate_questions)

        sg.add_node("generate_outline", func=self.\_generate_outline)

        sg.add_node("generate_perspectives", func=self.\_generate_perspectives)

        sg.add_node("generate_questions", func=self.\_generate_questions)

        \# Stage 2: (dispatch_queries) \-\> (execute_search) \-\> (collect_search_results)

        sg.add_node("dispatch_queries", func=self.\_dispatch_queries)

        sg.add_node("execute_search", func=self.\_execute_search)

        sg.add_node("collect_search_results", func=self.\_collect_search_results)

        \# Stage 3: (synthesize_section) \-\> possibly loop over sections \-\> (compile_report)

        sg.add_node("synthesize_sections", func=self.\_synthesize_sections)

        sg.add_node("compile_report", func=self.\_compile_report)

        sg.add_node("final_output", func=lambda s: s)

        \# Edges for stage 1

        sg.add_edge("generate_outline", "generate_perspectives")

        sg.add_edge("generate_perspectives", "generate_questions")

        \# Edges for stage 2

        sg.add_edge("generate_questions", "dispatch_queries")

        sg.add_edge("dispatch_queries", "execute_search")

        sg.add_edge("execute_search", "collect_search_results")

        \# Edges for stage 3

        sg.add_edge("collect_search_results", "synthesize_sections")

        sg.add_edge("synthesize_sections", "compile_report")

        sg.add_edge("compile_report", "final_output")

        self.graph \= sg.compile()

    def run(self, input_data: Any) \-\> Any:

        state \= {

            "topic": input_data,

            "outline": {},

            "perspectives": \[\],

            "questions": {},

            "search_results": {},

            "synthesized_sections": {},

            "final_report": None

        }

        final_state \= self.graph.run(state)

        return final_state\["final_report"\]

    def \_generate_outline(self, state: Dict) \-\> Dict:

        """

        Create a hierarchical outline (sections/sub-sections) for the topic.

        Typically uses a planning or documentation LLM.

        """

        \# ...

        state\["outline"\] \= {

            "Introduction": \[\],

            "MainBody": \["Subtopic1", "Subtopic2"\],

            "Conclusion": \[\]

        }

        return state

    def \_generate_perspectives(self, state: Dict) \-\> Dict:

        """

        Identify relevant viewpoints/personas from which to question the topic (e.g. 

        'scientist', 'economist', 'policymaker').

        """

        \# ...

        state\["perspectives"\] \= \["scientist", "policymaker"\]

        return state

    def \_generate_questions(self, state: Dict) \-\> Dict:

        """

        For each outline section and perspective, produce a list of questions to research.

        """

        questions_dict \= {}

        for section in state\["outline"\]:

            questions_dict\[section\] \= {}

            for p in state\["perspectives"\]:

                \# e.g. LLM call to generate relevant Qs

                questions_dict\[section\]\[p\] \= \[f"Key {p} question about {section}"\]

        state\["questions"\] \= questions_dict

        return state

    def \_dispatch_queries(self, state: Dict) \-\> Dict:

        """

        Possibly prepare parallel queries for each question. 

        """

        \# ...

        return state

    def \_execute_search(self, state: Dict) \-\> Dict:

        """

        Execute all queries, presumably via a search or retrieval tool. 

        Results stored in search_results\[section\]\[perspective\].

        """

        results \= {}

        for section, pers_map in state\["questions"\].items():

            results\[section\] \= {}

            for p, q_list in pers_map.items():

                \# call the knowledge base, gather text

                results\[section\]\[p\] \= \[f"Mock retrieved info for {q}" for q in q_list\]

        state\["search_results"\] \= results

        return state

    def \_collect_search_results(self, state: Dict) \-\> Dict:

        """

        Summarize or store them (if needed). Right now we just keep them in state.

        """

        return state

    def \_synthesize_sections(self, state: Dict) \-\> Dict:

        """

        For each outline section, merge all relevant info from different perspectives

        into a cohesive draft.

        """

        synthesized \= {}

        for section in state\["outline"\]:

            \# gather the search results for that section from all perspectives

            \# feed them to a 'documentation' LLM to produce a combined text

            \# ...

            synthesized\[section\] \= f"Synthesized content for {section} from all perspective data."

        state\["synthesized_sections"\] \= synthesized

        return state

    def \_compile_report(self, state: Dict) \-\> Dict:

        """

        Combine section texts into a final coherent report.

        """

        final_text \= \[\]

        for section in \["Introduction", "MainBody", "Conclusion"\]:

            sec_content \= state\["synthesized_sections"\].get(section, "")

            final_text.append(f"{section}:\\n{sec_content}")

        state\["final_report"\] \= "\\n\\n".join(final_text)

        return state

**Builder Tips:**

1. **Outline & Perspectives**: Provide separate prompts to generate a structured outline and the relevant expert viewpoints ("personas").

2. **Multi-Question Generation**: A for-loop approach over (section × perspective). The LLM can produce targeted queries for each vantage point.

3. **Retrieval**: Any search or knowledge-base calls happen in `_execute_search`. Could be parallel tasks in LangGraph if desired.

4. **Synthesis**: Merges the retrieved data from multiple angles, typically with a "documentation" model specialized for summarizing large text.

5. **Customization**:

   * Expand the outline with sub-sections.

   * For deeply technical writing, add additional reflection or re-check steps.

   ---

See `patterns/` directory for each pattern's reference implementation. The sections in this document serve as a template, ensuring consistency across patterns.

---

## **5\. Prompt Management**

All patterns load prompt templates from the `prompts/` folder. **Recommended structure**:

prompts/  
├── ReActAgent/  
│   ├── ThoughtStep/  
│   │   ├── system.md  
│   │   └── user.md  
│   └── ...  
├── ReflectionAgent/  
│   ├── Generate/  
│   │   ├── system.md  
│   │   └── user.md  
│   ├── Reflect/  
│   │   ├── system.md  
│   │   └── user.md  
│   └── Refine/  
│       ├── system.md  
│       └── user.md  
└── ...

**`_load_prompt(step_name)`** in each pattern will look for `system.md` and `user.md` in the subfolder matching `self.__class__.__name__/step_name`. This keeps prompts versioned separately from code, so you can adjust them without editing Python files.

---

## **6\. Environment Configuration**

We use a `.env` file for keys, model names, and provider details. Example:

OPENAI_API_KEY= "your-key"  
THINKING_MODEL_PROVIDER=openai  
THINKING_MODEL_NAME="gpt-4-turbo"  
REFLECTION_MODEL_PROVIDER=anthropic  
REFLECTION_MODEL_NAME="claude-3.5"

**`llm_configs`** can be built by parsing `.env`:

import os  
from dotenv import load_dotenv

load_dotenv()  
llm_configs \= {  
    "thinking": {  
        "provider": os.getenv("THINKING_MODEL_PROVIDER"),  
        "model_name": os.getenv("THINKING_MODEL_NAME"),  
    },  
    \# ... likewise for reflection, documentation, etc.  
}

Then pass `llm_configs` to each pattern's constructor:

my_reflection_agent \= ReflectionAgent(llm_configs=llm_configs, prompt_dir="prompts")  
result \= my_reflection_agent.run("Explain quantum entanglement in simple terms.")

---

## **7\. Testing & Example Usage**

### **7.1. Example Scripts**

Each pattern has a dedicated example script in `examples/`. For instance, `reflection_example.py` might look like:

\# examples/reflection_example.py  
import os  
from dotenv import load_dotenv  
from agent_patterns.patterns.reflection_agent import ReflectionAgent

def main():  
    load_dotenv()  
    llm_configs \= {  
        "documentation": {  
            "provider": os.getenv("DOCUMENTATION_MODEL_PROVIDER"),  
            "model_name": os.getenv("DOCUMENTATION_MODEL_NAME"),  
        },  
        "reflection": {  
            "provider": os.getenv("REFLECTION_MODEL_PROVIDER"),  
            "model_name": os.getenv("REFLECTION_MODEL_NAME"),  
        }  
    }

    agent \= ReflectionAgent(llm_configs=llm_configs)  
    final_answer \= agent.run("Write a short story about a robot dog.")  
    print(final_answer)

if \_\_name\_\_ \== "\_\_main\_\_":  
    main()

### **7.2. Tests**

Under `tests/`, create unit tests ensuring each pattern handles typical and edge cases. Use mocks or stubs for LLM calls:

\# tests/test_reflection.py  
import pytest  
from unittest.mock import patch  
from agent_patterns.patterns.reflection_agent import ReflectionAgent

def test_reflection_agent_basic():  
    agent \= ReflectionAgent(llm_configs={}, prompt_dir="prompts")  
    with patch.object(agent, "\_get_llm", return_value=lambda x: "mock_llm_response"):  
        output \= agent.run("Test input")  
        assert "mock" in output  \# simplistic check

---

## **8\. Notes on Extensibility & Best Practices**

1. **Externalize Tools**: Patterns like ReAct rely on multiple external tools (e.g., web search, calculator). Provide a `ToolRegistry` or pass a `tools` dictionary into the agent's constructor so new tools can be added easily.

2. **Parallel Execution**: LangGraph supports parallel nodes. Use them for multi-step or multi-agent tasks if beneficial.

3. **Prompt Tuning**: Encourage domain-specific prompts. This design expects developers to refine their prompts in `.md` files.

4. **Iteration Limits & Safety**: Patterns like Reflection can loop. Always define a max iteration or safe stop condition to avoid infinite loops or excessive token usage.

5. **Logging & Observability**: Consider hooking into the agent's lifecycle with logs for each node (e.g., logging the LLM's output at each step). This helps debug or interpret the agent's chain-of-thought.

---

## **9\. How to Create a New Pattern**

1. **Subclass** either `BaseAgent` or `MultiAgentBase`.

2. **Define `build_graph()`**: Create a `StateGraph`, add your nodes, transitions, and compile it.

3. **Implement** all node functions (the "steps"):

   * Each step function takes and returns a `state: dict`.

   * Include the logic or LLM calls needed.

4. **Handle** prompts for each step with `_load_prompt(step_name)`. Provide step-specific subfolders in `prompts/<YourPatternClass>/`.

5. **Write** at least one example script and unit test to demonstrate usage and confirm correctness.

This approach ensures **all** patterns follow a consistent lifecycle and are easy to pick up by new developers.

---

## **Conclusion**

This updated design document aims to be a **comprehensive reference** for implementing and extending the *agent-patterns* library. By combining **clear base abstractions**, **externalized prompts**, **detailed pattern examples**, and **robust environment configuration**, we ensure that developers understand precisely how to **code new agent patterns** and **customize existing ones**.

For questions or contributions:

* See [**examples/**](https://chatgpt.com/c/examples) for usage demos.

* Consult each pattern's docstrings for detailed instructions.

* Submit issues or PRs on our GitHub repository to propose improvements or new patterns.

**Happy coding with agent-patterns\!**
