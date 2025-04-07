# **Agent-Patterns Project: Design Document** 

**Version:** 2.1  
 **Date:** April 7, 2025  
 **Author:** *Michael Caughey*

 **Status:** Draft

---

## **1\. Overview and Goals**

### **1.1. Project Purpose**

The *agent-patterns* project provides a Python library of **reusable, extensible, and well-documented base classes** that encapsulate common AI agent workflows (or “patterns”). These patterns are implemented using [**LangGraph**](https://langchain.com/docs/langgraph) and rely on [**LangChain**](https://python.langchain.com/en/latest/) for Large Language Model (LLM) integrations, prompt management, and tool usage.

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

* **STORM (Topic Outlines \+ Multi-perspective Retrieval)**

Each pattern’s goal is to reduce boilerplate and encourage consistent best practices. The library is especially useful for developers needing to quickly build or customize advanced AI workflows without reinventing the wheel.

### **1.3. Architectural Philosophy**

1. **Modular Base Classes:** One or more abstract base classes define common agent operations and Graph structures. Each pattern extends these bases to add specialized logic (e.g., planning steps, reflection loops).

2. **Externalized Configuration & Prompts:** Prompt templates, environment variables (e.g., model keys), and certain runtime parameters (e.g., max steps) are stored outside core code for easier customization.

3. **Developer Clarity:** Each pattern’s responsibilities, methods, and usage are clearly documented so users know exactly which methods to override, how to pass custom prompts, and how to plug in specialized logic.

4. **Testability & Extensibility:** By separating pattern logic, tool definitions, and LLM configurations, the library is designed to be straightforward to test, maintain, and extend with new patterns.

---

## **2\. Repository & File Structure**

Here’s a recommended layout for the *agent-patterns* repository. You can customize as needed, but we strongly recommend separating core abstractions, pattern implementations, prompts, and examples:

agent\_patterns/  
├── core/  
│   ├── base\_agent.py  
│   └── multi\_agent\_base.py  
├── patterns/  
│   ├── re\_act\_agent.py  
│   ├── plan\_and\_solve\_agent.py  
│   ├── reflection\_agent.py  
│   ├── reflexion\_agent.py  
│   ├── llm\_compiler\_agent.py  
│   ├── rewoo\_agent.py  
│   ├── lats\_agent.py  
│   ├── self\_discovery\_agent.py  
│   └── storm\_agent.py  
├── prompts/  
│   ├── reflection/  
│   │   ├── critic\_prompt.md  
│   │   └── revision\_prompt.md  
│   └── ...  
├── examples/  
│   ├── reflection\_example.py  
│   └── plan\_example.py  
├── tests/  
│   ├── test\_reflection.py  
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

**Responsibility**: Provide core logic for orchestrating a single agent’s workflow, including:

* Initializing an LLM or set of LLM roles (thinking, critic, etc.).

* Loading external prompt templates.

* Defining or compiling a [LangGraph](https://langchain.com/docs/langgraph) graph.

* Running or streaming the agent’s process from input to output.

**Typical Usage**:

1. Subclass `BaseAgent` to create a new pattern.

2. Override required abstract methods (e.g., `build_graph()`, `run()`).

3. Use `self._get_llm(role)` to fetch the correct LLM for a particular role.

4. Use `self._load_prompt(step_name)` to retrieve external prompt templates.

5. Optionally override lifecycle hooks (`on_start()`, `on_finish()`) for logging.

\# core/base\_agent.py  
import abc  
from typing import Any, Iterator  
from langgraph import CompiledGraph

class BaseAgent(abc.ABC):  
    def \_\_init\_\_(self, llm\_configs: dict, prompt\_dir: str \= "prompts"):  
        """  
        :param llm\_configs: Dictionary specifying provider, model, and roles.  
        :param prompt\_dir: Directory for prompt templates.  
        """  
        self.llm\_configs \= llm\_configs  
        self.prompt\_dir \= prompt\_dir  
        self.graph: CompiledGraph \= None  \# set by self.build\_graph()

        \# Subclass is expected to build/compile its graph  
        self.build\_graph()

    @abc.abstractmethod  
    def build\_graph(self) \-\> None:  
        """Construct or compile the LangGraph used by this agent pattern."""  
        pass

    @abc.abstractmethod  
    def run(self, input\_data: Any) \-\> Any:  
        """  
        Run the agent to completion with the given input.  
        :param input\_data: The user query or initial state.  
        :return: The final output or answer.  
        """  
        pass

    def stream(self, input\_data: Any) \-\> Iterator\[Any\]:  
        """Optional streaming interface. Subclasses can override."""  
        yield self.run(input\_data)

    def \_get\_llm(self, role: str):  
        """Returns an LLM object for a given role based on llm\_configs."""  
        \# Implementation detail: parse self.llm\_configs to create the LLM.  
        \# E.g., llm\_configs might have THINKING\_MODEL\_NAME, CRITIC\_MODEL\_NAME, etc.  
        pass

    def \_load\_prompt(self, step\_name: str) \-\> dict:  
        """  
        Loads a prompt template (system/user) from the prompts/ directory.  
        Subclasses can override to implement custom logic or fallback.  
        """  
        \# E.g. read from f"{self.prompt\_dir}/{self.\_\_class\_\_.\_\_name\_\_}/{step\_name}/\*.md"  
        \# Return a dict with {"system\_prompt": "...", "user\_prompt": "..."} or similar  
        return {}

**Design Notes**:

* `_get_llm(role)` and `_load_prompt(step_name)` are placeholders for actual prompt and LLM loading. This keeps the base class generic.

* `build_graph()` is where the pattern sets up its LangGraph nodes and transitions. The base class doesn’t know the pattern’s structure; that’s left to subclasses.

* `run(input_data)` is the main method. Many patterns also define specialized sub-steps, but `run()` is the entry point from a developer’s perspective.

### **3.2. `MultiAgentBase` (Abstract)**

**Responsibility**: Coordinates multiple sub-agents or roles. Provides:

* A container or registry for sub-agents.

* Methods for distributing tasks among them.

* Common logic for collating results.

\# core/multi\_agent\_base.py  
import abc  
from typing import List, Dict  
from .base\_agent import BaseAgent

class MultiAgentBase(BaseAgent, abc.ABC):  
    def \_\_init\_\_(self, sub\_agents: Dict\[str, BaseAgent\], \*\*kwargs):  
        """  
        :param sub\_agents: Mapping of role \-\> agent instance (or agent class).  
        :param kwargs: Additional arguments passed to BaseAgent.  
        """  
        super().\_\_init\_\_(\*\*kwargs)  
        self.sub\_agents \= sub\_agents

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

### **4.1. ReAct (Reason \+ Act) Pattern**

#### **4.1.1. Overview**

**Goal**: Enable an agent to iteratively reason (produce a thought) and act (call a tool) until it arrives at a final answer. Particularly good for question-answering that requires external information or tools.

#### **4.1.2. Class: `ReActAgent`**

\# patterns/re\_act\_agent.py  
from typing import Any, Dict  
from agent\_patterns.core.base\_agent import BaseAgent  
from langgraph import StateGraph, CompiledGraph

class ReActAgent(BaseAgent):  
    def build\_graph(self) \-\> None:  
        """  
        Construct a StateGraph for the ReAct cycle:  
          (thought) \-\> (action) \-\> (observation) \-\> check if done \-\> (thought) ...  
        """  
        sg \= StateGraph()

        \# Node definitions (Pseudo-code)  
        sg.add\_node("thought\_step", func=self.\_generate\_thought\_and\_action)  
        sg.add\_node("action\_step", func=self.\_execute\_action)  
        sg.add\_node("observation\_step", func=self.\_observation\_handler)  
        sg.add\_node("final\_answer", func=self.\_format\_final\_answer)

        \# Edges & transitions  
        sg.add\_edge("thought\_step", "action\_step")  
        sg.add\_edge("action\_step", "observation\_step")  
        sg.add\_edge("observation\_step", "thought\_step", condition=self.\_check\_continue)  
        sg.add\_edge("observation\_step", "final\_answer", condition=self.\_check\_if\_done)

        self.graph \= sg.compile()

    def run(self, input\_data: Any) \-\> Any:  
        """  
        Entry point for the ReAct pattern.  
        Input: user query or problem statement.  
        Output: final answer after possibly multiple cycles.  
        """  
        initial\_state \= {  
            "input": input\_data,  
            "thought": "",  
            "action": {},  
            "observation": None,  
            "intermediate\_steps": \[\],  
            "final\_answer": None  
        }  
        result\_state \= self.graph.run(initial\_state)  
        return result\_state\["final\_answer"\]

    def \_generate\_thought\_and\_action(self, state: Dict) \-\> Dict:  
        """  
        1\. Summarize current state & query LLM for next thought & action.  
        2\. Action is typically {tool\_name: str, tool\_input: str}.  
        """  
        prompt\_data \= self.\_load\_prompt("ThoughtStep")  \# system, user prompts  
        llm \= self.\_get\_llm("thinking")  
        \# Compose a prompt, e.g. prompt\_data\["system"\] \+ user info \+ state  
        \# LLM returns something like "Thought: I need to look up weather \-\> Action: search\_tool('weather in Paris')"  
        \# Parse it into \`thought\` and \`action\` dict  
        \# ...  
        \# For illustration, assume we parse it:  
        thought\_str \= "I need to check the weather"  
        action\_dict \= {"tool\_name": "search\_tool", "tool\_input": "weather in Paris"}  
        state\["thought"\] \= thought\_str  
        state\["action"\] \= action\_dict  
        state\["intermediate\_steps"\].append((thought\_str, action\_dict, None))  
        return state

    def \_execute\_action(self, state: Dict) \-\> Dict:  
        """Call the actual tool with the specified input."""  
        action \= state\["action"\]  
        tool\_name \= action\["tool\_name"\]  
        tool\_input \= action\["tool\_input"\]  
        \# Assume we have a tool registry or something similar  
        observation \= self.\_call\_tool(tool\_name, tool\_input)  
        state\["observation"\] \= observation  
        \# Update the last step in intermediate\_steps with the observation  
        if state\["intermediate\_steps"\]:  
            last\_thought, last\_action, \_ \= state\["intermediate\_steps"\]\[-1\]  
            state\["intermediate\_steps"\]\[-1\] \= (last\_thought, last\_action, observation)  
        return state

    def \_observation\_handler(self, state: Dict) \-\> Dict:  
        """We could do additional processing of the observation if needed."""  
        return state

    def \_check\_continue(self, state: Dict) \-\> bool:  
        """Check if we should keep going. For now, always True unless found a final answer marker."""  
        \# Could parse state\["thought"\] for a 'FINAL ANSWER' marker, etc.  
        return not self.\_is\_done(state)

    def \_check\_if\_done(self, state: Dict) \-\> bool:  
        return self.\_is\_done(state)

    def \_is\_done(self, state: Dict) \-\> bool:  
        """  
        Condition to exit the cycle: e.g. thought or observation indicates completion,  
        or a maximum step limit reached.  
        """  
        \# Implement custom logic, e.g., if "FINAL ANSWER:" in state\["thought"\] or step\_count \> ...  
        return False

    def \_format\_final\_answer(self, state: Dict) \-\> Dict:  
        """  
        Optionally reformat or finalize the answer for the user.  
        """  
        \# E.g., parse the last thought for final answer  
        final \= "Here's the final answer from the chain of thought..."  
        state\["final\_answer"\] \= final  
        return state

    def \_call\_tool(self, tool\_name: str, tool\_input: Any) \-\> Any:  
        """Implement or delegate to a registry for tool calls."""  
        \# ...  
        return f"Mock result for {tool\_input}"

#### **4.1.3. Implementation Notes:**

* **Prompts**: Stored in `prompts/ReActAgent/ThoughtStep/system.md` and `prompts/ReActAgent/ThoughtStep/user.md`.

* **Tool Integration**: `_call_tool()` is a stub that calls a registry. Implementation details can be externalized to a `ToolRegistry` utility.

* **Stop Condition**: `_check_continue()` vs. `_check_if_done()` demonstrate how to branch in LangGraph.

---

### **4.2. Plan & Solve Pattern**

#### **4.2.1. Overview**

**Goal**: Decouple planning from execution. Generate a multi-step plan, then sequentially (or in parallel) execute each step. Great for tasks that can be broken down predictably.

#### **4.2.2. Class: `PlanAndSolveAgent`**

\# patterns/plan\_and\_solve\_agent.py  
from typing import Any, Dict, List  
from agent\_patterns.core.base\_agent import BaseAgent  
from langgraph import StateGraph

class PlanAndSolveAgent(BaseAgent):

    def build\_graph(self) \-\> None:  
        sg \= StateGraph()  
        sg.add\_node("plan\_step", func=self.\_generate\_plan)  
        sg.add\_node("execute\_step", func=self.\_execute\_plan\_step)  
        sg.add\_node("check\_completion", func=self.\_check\_plan\_completion)  
        sg.add\_node("aggregate\_results", func=self.\_aggregate\_results)

        sg.add\_edge("plan\_step", "execute\_step")  
        sg.add\_edge("execute\_step", "check\_completion")  
        sg.add\_edge("check\_completion", "execute\_step", condition=lambda s: not s\["plan\_done"\])  
        sg.add\_edge("check\_completion", "aggregate\_results", condition=lambda s: s\["plan\_done"\])

        self.graph \= sg.compile()

    def run(self, input\_data: Any) \-\> Any:  
        state \= {  
            "input\_task": input\_data,  
            "plan": \[\],  
            "current\_step\_index": 0,  
            "step\_results": \[\],  
            "plan\_done": False,  
            "final\_result": None  
        }  
        final\_state \= self.graph.run(state)  
        return final\_state\["final\_result"\]

    def \_generate\_plan(self, state: Dict) \-\> Dict:  
        """  
        Use an LLM to create a structured plan (list of steps).  
        """  
        prompt\_data \= self.\_load\_prompt("PlanStep")  
        llm \= self.\_get\_llm("planning")  
        \# e.g., plan\_text \= llm.generate(...)  
        \# parse plan\_text into a list of step dicts  
        plan \= \[{"step\_description": "Step 1: Do X"}, {"step\_description": "Step 2: Do Y"}\]  
        state\["plan"\] \= plan  
        return state

    def \_execute\_plan\_step(self, state: Dict) \-\> Dict:  
        idx \= state\["current\_step\_index"\]  
        plan \= state\["plan"\]  
        if idx \< len(plan):  
            step \= plan\[idx\]  
            result \= self.\_run\_single\_step(step, state)  
            state\["step\_results"\].append(result)  
            state\["current\_step\_index"\] \+= 1  
        return state

    def \_check\_plan\_completion(self, state: Dict) \-\> Dict:  
        if state\["current\_step\_index"\] \>= len(state\["plan"\]):  
            state\["plan\_done"\] \= True  
        return state

    def \_aggregate\_results(self, state: Dict) \-\> Dict:  
        """  
        Combine step results into a final answer, possibly using another LLM or direct logic.  
        """  
        final \= " ".join(state\["step\_results"\])  
        state\["final\_result"\] \= f"Plan & Solve final answer:\\n{final}"  
        return state

    def \_run\_single\_step(self, step: Dict, state: Dict) \-\> Any:  
        """  
        Could call an LLM or a tool depending on step content.  
        """  
        \# e.g., parse step\["step\_description"\], do the action  
        return f"Executed: {step\['step\_description'\]}"

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

\# patterns/reflection\_agent.py  
from agent\_patterns.core.base\_agent import BaseAgent  
from langgraph import StateGraph

class ReflectionAgent(BaseAgent):

    def build\_graph(self) \-\> None:  
        sg \= StateGraph()  
        sg.add\_node("generate\_initial", func=self.\_generate\_initial\_output)  
        sg.add\_node("reflect", func=self.\_reflect\_on\_output)  
        sg.add\_node("check\_refine", func=self.\_check\_refinement\_needed)  
        sg.add\_node("refine", func=self.\_refine\_output)  
        sg.add\_node("final\_output", func=lambda s: s)

        \# Edges  
        sg.add\_edge("generate\_initial", "reflect")  
        sg.add\_edge("reflect", "check\_refine")  
        sg.add\_edge("check\_refine", "refine", condition=lambda s: s\["needs\_refinement"\])  
        sg.add\_edge("check\_refine", "final\_output", condition=lambda s: not s\["needs\_refinement"\])  
        sg.add\_edge("refine", "final\_output")

        self.graph \= sg.compile()

    def run(self, input\_data: str):  
        state \= {  
            "input\_task": input\_data,  
            "initial\_output": None,  
            "reflection": None,  
            "refined\_output": None,  
            "needs\_refinement": False,  
            "final\_answer": None  
        }  
        final\_state \= self.graph.run(state)  
        return final\_state.get("final\_answer")

    def \_generate\_initial\_output(self, state):  
        """Generate a first attempt using the main LLM."""  
        prompt\_data \= self.\_load\_prompt("Generate")  
        llm \= self.\_get\_llm("documentation")  \# or "thinking", depending  
        \# result \= llm.predict(...)  
        result \= f"Initial answer to {state\['input\_task'\]}"  
        state\["initial\_output"\] \= result  
        return state

    def \_reflect\_on\_output(self, state):  
        """Use a separate reflection model to critique the initial output."""  
        critic\_prompt \= self.\_load\_prompt("Reflect")  
        critic\_llm \= self.\_get\_llm("reflection")  
        \# reflection\_text \= critic\_llm.predict(state\["initial\_output"\])  
        reflection\_text \= "Critique: The answer is incomplete; mention more details."  
        state\["reflection"\] \= reflection\_text  
        return state

    def \_check\_refinement\_needed(self, state):  
        """Decide if refinement is necessary."""  
        \# simple heuristic: if 'incomplete' in reflection \-\> refine  
        state\["needs\_refinement"\] \= "incomplete" in state\["reflection"\].lower()  
        return state

    def \_refine\_output(self, state):  
        """Generate a refined output using the reflection text."""  
        refine\_prompt \= self.\_load\_prompt("Refine")  
        llm \= self.\_get\_llm("documentation")  
        \# refined \= llm.predict(f"{state\['initial\_output'\]}\\nCritique: {state\['reflection'\]}")  
        refined \= f"Refined answer (added details) for {state\['input\_task'\]}"  
        state\["refined\_output"\] \= refined  
        state\["final\_answer"\] \= refined  
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

**Goal:** Enable iterative problem-solving where the agent revisits past mistakes and successes across *multiple trials*, storing “lessons” in a persistent “reflection memory.” After each trial (or “episode”), the agent logs insights—why something worked or failed—so that next time it encounters a similar situation, it can consult those insights to improve performance.

This differs from a simple one-pass “Reflection” pattern by introducing:

* **Reflection Memory**: A structured store of lessons or heuristics the agent can read before generating the next attempt.

* **Multi-Trial Loop**: The agent repeatedly attempts a task (or sub-task), reflecting after each attempt and incorporating those reflections into a persistent memory.

It’s most useful when:

* The agent must refine a partial solution over many tries.

* We want a “learning effect” across attempts (although it’s local to the session, not a global learned model).

  ### **4.4.2. Class: `ReflexionAgent`**

Below is a sketch for a builder’s guide, showing how to build the LangGraph for multiple attempts:

\# patterns/reflexion\_agent.py

from typing import Any, Dict

from agent\_patterns.core.base\_agent import BaseAgent

from langgraph import StateGraph, CompiledGraph

class ReflexionAgent(BaseAgent):

    def build\_graph(self) \-\> None:

        sg \= StateGraph()

        

        \# 1\) plan\_action\_with\_memory \-\> 2\) execute\_action \-\> 3\) evaluate\_outcome

        \#    \-\> 4\) reflect\_on\_trial \-\> 5\) update\_reflection\_memory 

        \#    \-\> check if done or not \-\> loop or final

        \#

        \# We illustrate a loop from a 'trial' node back to the top, up to a max trial count

        \# or until the agent decides it’s done.

        

        sg.add\_node("plan\_action\_with\_memory", func=self.\_plan\_action\_with\_memory)

        sg.add\_node("execute\_action", func=self.\_execute\_action)

        sg.add\_node("evaluate\_outcome", func=self.\_evaluate\_outcome)

        sg.add\_node("reflect\_on\_trial", func=self.\_reflect\_on\_trial)

        sg.add\_node("update\_reflection\_memory", func=self.\_update\_reflection\_memory)

        sg.add\_node("final\_output", func=lambda s: s)

        \# Edges for the trial loop:

        sg.add\_edge("plan\_action\_with\_memory", "execute\_action")

        sg.add\_edge("execute\_action", "evaluate\_outcome")

        sg.add\_edge("evaluate\_outcome", "reflect\_on\_trial")

        sg.add\_edge("reflect\_on\_trial", "update\_reflection\_memory")

        \# Condition: either loop to "plan\_action\_with\_memory" (new trial) or exit

        sg.add\_edge("update\_reflection\_memory", "plan\_action\_with\_memory",

                    condition=self.\_continue\_trials)

        sg.add\_edge("update\_reflection\_memory", "final\_output",

                    condition=lambda s: not self.\_continue\_trials(s))

        self.graph \= sg.compile()

    def run(self, input\_data: Any) \-\> Any:

        \# The agent will attempt multiple trials, storing reflection each time

        initial\_state \= {

            "input\_task": input\_data,

            "reflection\_memory": \[\],     \# list of string insights or structured data

            "trial\_count": 0,

            "max\_trials": 3,            \# or read from config

            "outcome": None,

            "final\_answer": None

        }

        final\_state \= self.graph.run(initial\_state)

        return final\_state\["final\_answer"\]

    def \_plan\_action\_with\_memory(self, state: Dict) \-\> Dict:

        """

        Reads reflection\_memory to inform the next planned action or approach.

        Typically uses a 'thinking' LLM or specialized role.

        """

        \# Combine the user input \+ reflection memory in a prompt

        \# e.g., "Here are your previous lessons: \[...\]. Now plan your next step for the task."

        \# ...

        state\["trial\_count"\] \+= 1

        return state

    def \_execute\_action(self, state: Dict) \-\> Dict:

        """

        Actually try to solve the task, possibly by calling a tool or generating text.

        """

        \# ...

        \# store a raw result in state\["outcome"\]

        state\["outcome"\] \= "Attempt result or partial solution"

        return state

    def \_evaluate\_outcome(self, state: Dict) \-\> Dict:

        """

        Critically evaluate how the attempt went. 

        Could be LLM-based or an environment check if we have a known correct result.

        """

        \# ...

        \# e.g. store 'success', 'failure', or details in state

        state\["evaluation"\] \= "failure"  \# or success

        return state

    def \_reflect\_on\_trial(self, state: Dict) \-\> Dict:

        """

        Summarize what was learned from the outcome to be stored in reflection memory.

        Typically a reflection LLM is used here.

        """

        reflection\_llm \= self.\_get\_llm("reflection")

        \# reflection\_text \= reflection\_llm.predict( ... )

        reflection\_text \= "If outcome is X, we should do Y next time."

        state\["trial\_reflection"\] \= reflection\_text

        return state

    def \_update\_reflection\_memory(self, state: Dict) \-\> Dict:

        """

        Append newly generated reflection to reflection\_memory.

        """

        state\["reflection\_memory"\].append(state\["trial\_reflection"\])

        return state

    def \_continue\_trials(self, state: Dict\]) \-\> bool:

        """

        Decide if we need another trial: e.g. not done or trial\_count \< max\_trials

        or outcome wasn't successful.

        """

        if state\["trial\_count"\] \>= state\["max\_trials"\]:

            \# finalize or forcibly stop

            state\["final\_answer"\] \= f"Best attempt result: {state\['outcome'\]}"

            return False

        \# If outcome was 'success', we can stop early:

        if state.get("evaluation") \== "success":

            state\["final\_answer"\] \= f"Successful result: {state\['outcome'\]}"

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

**Goal:** Treat your entire multi-tool workflow like a “compiler.” The agent constructs an **execution graph** from the user task and the available tools, then **executes** the graph in an optimized order—possibly in parallel. This can speed up tasks requiring multiple independent tool calls or sub-queries.

### **4.5.2. Key Components**

1. **Planner**: An LLM that inspects the user’s request plus the “tool signatures” to generate a DAG (Directed Acyclic Graph) describing the execution sequence.

2. **Executor**: Runs each node in topological order (or parallel if no dependencies).

3. **Synthesis**: After all nodes are complete, merges the intermediate results into a final answer.

   ### **4.5.3. Class: `LLMCompilerAgent`**

\# patterns/llm\_compiler\_agent.py

from typing import Any, Dict

from agent\_patterns.core.base\_agent import BaseAgent

from langgraph import StateGraph

class LLMCompilerAgent(BaseAgent):

    def build\_graph(self) \-\> None:

        sg \= StateGraph()

        \# We'll define a simplified approach:

        \# 1\) planner\_generate\_graph \-\> 2\) executor\_dispatch

        \# \-\> 3\) check\_if\_done \-\> 4\) synthesize\_result

        \# \-\> loop back to executor\_dispatch if not done.

        sg.add\_node("planner\_generate\_graph", func=self.\_planner\_generate\_graph)

        sg.add\_node("executor\_dispatch", func=self.\_executor\_dispatch)

        sg.add\_node("check\_completion", func=self.\_check\_completion)

        sg.add\_node("synthesize\_result", func=self.\_synthesize\_result)

        sg.add\_edge("planner\_generate\_graph", "executor\_dispatch")

        sg.add\_edge("executor\_dispatch", "check\_completion")

        sg.add\_edge("check\_completion", "executor\_dispatch", condition=lambda s: not s\["graph\_done"\])

        sg.add\_edge("check\_completion", "synthesize\_result", condition=lambda s: s\["graph\_done"\])

        self.graph \= sg.compile()

    def run(self, input\_data: Any) \-\> Any:

        state \= {

            "input\_task": input\_data,

            "tool\_schemas": self.\_define\_tool\_schemas(),

            "execution\_graph": None,       \# The DAG structure

            "node\_results": {},

            "graph\_done": False,

            "final\_answer": None

        }

        final\_state \= self.graph.run(state)

        return final\_state\["final\_answer"\]

    def \_define\_tool\_schemas(self) \-\> Dict:

        """

        Provide formal definitions (JSON schemas, parameter types, etc.) for each tool.

        The planner LLM can see these definitions to figure out node dependencies.

        """

        \# Example: a search tool \+ calculator, each with some required inputs

        return {

            "search\_tool": {

                "input\_params": \["query"\],

                "output": "search\_results"

            },

            "calculator\_tool": {

                "input\_params": \["expression"\],

                "output": "numeric\_result"

            }

        }

    def \_planner\_generate\_graph(self, state: Dict) \-\> Dict:

        """

        Calls an LLM to produce a plan or DAG (like a JSON specifying the needed tools,

        the order, and any dependencies).

        """

        planner\_llm \= self.\_get\_llm("thinking")

        \# plan\_json \= planner\_llm.predict( ... ) 

        \# parse as Python structure

        \# For demonstration:

        example\_graph \= {

            "nodes": \[

                {"id": "node1", "tool": "search\_tool", "depends\_on": \[\], "args": {"query": "some query"}},

                {"id": "node2", "tool": "calculator\_tool", "depends\_on": \["node1"\], "args": {"expression": "2+2"}}

            \]

        }

        state\["execution\_graph"\] \= example\_graph

        return state

    def \_executor\_dispatch(self, state: Dict) \-\> Dict:

        """

        Look for any nodes whose dependencies are satisfied and haven't been run yet.

        Execute them in parallel or one by one, storing results in node\_results.

        """

        graph \= state\["execution\_graph"\]

        node\_results \= state\["node\_results"\]

        for node in graph\["nodes"\]:

            node\_id \= node\["id"\]

            if node\_id in node\_results:

                continue  \# already executed

            \# check dependencies

            if all(dep in node\_results for dep in node\["depends\_on"\]):

                \# we can execute this node

                res \= self.\_execute\_tool(node\["tool"\], node\["args"\])

                node\_results\[node\_id\] \= res

        return state

    def \_check\_completion(self, state: Dict) \-\> Dict:

        graph \= state\["execution\_graph"\]

        node\_results \= state\["node\_results"\]

        all\_ids \= \[n\["id"\] for n in graph\["nodes"\]\]

        \# If we've computed results for all nodes, we are done

        state\["graph\_done"\] \= all(id\_ in node\_results for id\_ in all\_ids)

        return state

    def \_synthesize\_result(self, state: Dict) \-\> Dict:

        """

        Combine the final node outputs into a human-readable or LLM-based answer.

        """

        \# E.g., we can ask an LLM to produce a final summary:

        summary\_llm \= self.\_get\_llm("documentation")

        \# final\_answer \= summary\_llm.predict(...)

        final\_answer \= "Final result compiled from node outputs."

        state\["final\_answer"\] \= final\_answer

        return state

    def \_execute\_tool(self, tool\_name: str, args: Dict) \-\> Any:

        """

        Actually run the named tool. Could be direct Python or an API call. 

        """

        \# ...

        return f"Mock result of {tool\_name} with {args}"

**Builder Tips:**

* **Tool Schemas**: Provide enough detail so the planner LLM can figure out the dependency graph.

* **Parallelization**: For real concurrency, consider LangGraph’s parallel node support or an async approach.

* **Graph Representation**: A typical structure is `{"nodes": [ {id, tool, depends_on, args}, ... ]}`.

  ---

  ## **4.6. REWOO (Reason Without Observation / Worker-Solver) Pattern**

  ### **4.6.1. Overview**

**Goal:** Separate the “thinking” LLM (the Worker) from the actual tool‑execution step (the Solver). The Worker plans out calls and placeholders for results *without* seeing their real outputs initially; then the Solver (often a cheaper or specialized model, or direct code) executes them. Finally, the Worker integrates the actual results back in a final pass.

This can reduce cost or latency if the main LLM is expensive—because you can run multiple Solver calls in parallel, only calling the expensive Worker again once all results are ready.

### **4.6.2. Class: `REWOOAgent`**

\# patterns/rewoo\_agent.py

from typing import Any, Dict, List

from agent\_patterns.core.base\_agent import BaseAgent

from langgraph import StateGraph

class REWOOAgent(BaseAgent):

    def build\_graph(self) \-\> None:

        sg \= StateGraph()

        

        \# 1\) worker\_plan \-\> 2\) dispatch\_to\_solvers \-\> 3\) solver\_execute (parallel or batch)

        \# 4\) collect\_solver\_results \-\> 5\) worker\_integrate \-\> final

        sg.add\_node("worker\_plan", func=self.\_worker\_plan)

        sg.add\_node("dispatch\_to\_solvers", func=self.\_dispatch\_to\_solvers)

        sg.add\_node("solver\_execute", func=self.\_solver\_execute)    \# could also be multiple parallel nodes

        sg.add\_node("collect\_solver\_results", func=self.\_collect\_solver\_results)

        sg.add\_node("worker\_integrate", func=self.\_worker\_integrate)

        sg.add\_node("final\_output", func=lambda s: s)

        sg.add\_edge("worker\_plan", "dispatch\_to\_solvers")

        sg.add\_edge("dispatch\_to\_solvers", "solver\_execute")

        sg.add\_edge("solver\_execute", "collect\_solver\_results")

        sg.add\_edge("collect\_solver\_results", "worker\_integrate")

        sg.add\_edge("worker\_integrate", "final\_output")

        self.graph \= sg.compile()

    def run(self, input\_data: Any) \-\> Any:

        state \= {

            "input\_task": input\_data,

            "worker\_plan\_template": "",    \# e.g. "Find CEO \-\> {ceo}, also get Stock \-\> {price}"

            "solver\_requests": \[\],         \# list of tool calls

            "solver\_results": {},          \# mapping placeholders \-\> real data

            "final\_answer": None

        }

        final\_state \= self.graph.run(state)

        return final\_state\["final\_answer"\]

    def \_worker\_plan(self, state: Dict) \-\> Dict:

        """

        The 'thinking' LLM: produce a plan with placeholders for solver outputs.

        """

        thinking\_llm \= self.\_get\_llm("thinking")

        \# Example: 

        \# plan\_template \= thinking\_llm.predict("Given the user request, lay out the steps 

        \#   with placeholders for each solver call result...")

        plan\_template \= "Find CEO \-\> {ceo\_name}; Check stock \-\> {stock\_price}"

        solver\_requests \= \[

            {"placeholder": "ceo\_name", "tool": "search\_tool", "params": {"query": "CEO of Company X"}},

            {"placeholder": "stock\_price", "tool": "stock\_api\_tool", "params": {"symbol": "COMPX"}}

        \]

        state\["worker\_plan\_template"\] \= plan\_template

        state\["solver\_requests"\] \= solver\_requests

        return state

    def \_dispatch\_to\_solvers(self, state: Dict) \-\> Dict:

        """

        Possibly break solver\_requests into parallel tasks. We'll keep it simple.

        """

        return state

    def \_solver\_execute(self, state: Dict) \-\> Dict:

        """

        Let each solver\_request be executed, presumably by a cheaper model or direct code.

        """

        for req in state\["solver\_requests"\]:

            placeholder \= req\["placeholder"\]

            tool\_name \= req\["tool"\]

            params \= req\["params"\]

            \# call the solver

            result \= self.\_call\_solver(tool\_name, params)

            state\["solver\_results"\]\[placeholder\] \= result

        return state

    def \_collect\_solver\_results(self, state: Dict) \-\> Dict:

        """

        If parallel tasks were used, gather them here. We’re just storing them in solver\_results. 

        """

        return state

    def \_worker\_integrate(self, state: Dict) \-\> Dict:

        """

        The Worker LLM now sees the actual solver results inserted into the original plan template.

        """

        integration\_llm \= self.\_get\_llm("thinking")

        plan\_template \= state\["worker\_plan\_template"\]

        solver\_data \= state\["solver\_results"\]

        \# e.g. "Find CEO \-\> {ceo\_name}; ..." \-\> "Find CEO \-\> Jane Doe; ..." 

        \# Then feed that to the LLM for final phrasing or formatting

        filled\_in\_text \= plan\_template

        for placeholder, val in solver\_data.items():

            filled\_in\_text \= filled\_in\_text.replace(f"{{{placeholder}}}", str(val))

        \# final\_answer \= integration\_llm.predict(f"Integrate the following filled plan:\\n {filled\_in\_text}")

        final\_answer \= f"Final integrated result:\\n{filled\_in\_text}"

        state\["final\_answer"\] \= final\_answer

        return state

    def \_call\_solver(self, tool\_name: str, params: Dict):

        """

        Actually run the solver step. For example, direct Python calls or a smaller LLM.

        """

        return f"Mock result for {tool\_name} with {params}"

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

\# patterns/lats\_agent.py

from typing import Any, Dict

from agent\_patterns.core.base\_agent import BaseAgent

from langgraph import StateGraph

class LATSAgent(BaseAgent):

    def build\_graph(self) \-\> None:

        sg \= StateGraph()

        

        \# Minimal skeleton:

        \# 1\) select\_node \-\> 2\) expand\_node \-\> 3\) evaluate\_node \-\> 4\) backpropagate

        \#    \-\> check\_search\_budget \-\> loop or choose\_best\_path \-\> generate\_final\_output

        sg.add\_node("select\_node", func=self.\_select\_node)

        sg.add\_node("expand\_node", func=self.\_expand\_node)

        sg.add\_node("evaluate\_node", func=self.\_evaluate\_node)

        sg.add\_node("backpropagate", func=self.\_backpropagate)

        sg.add\_node("check\_budget", func=self.\_check\_budget)

        sg.add\_node("choose\_best\_path", func=self.\_choose\_best\_path)

        sg.add\_node("generate\_final\_output", func=self.\_generate\_final\_output)

        sg.add\_edge("select\_node", "expand\_node")

        sg.add\_edge("expand\_node", "evaluate\_node")

        sg.add\_edge("evaluate\_node", "backpropagate")

        sg.add\_edge("backpropagate", "check\_budget")

        sg.add\_edge("check\_budget", "select\_node", condition=lambda s: not s\["budget\_exhausted"\])

        sg.add\_edge("check\_budget", "choose\_best\_path", condition=lambda s: s\["budget\_exhausted"\])

        sg.add\_edge("choose\_best\_path", "generate\_final\_output")

        self.graph \= sg.compile()

    def run(self, input\_data: Any) \-\> Any:

        state \= {

            "input\_task": input\_data,

            "search\_tree": self.\_init\_tree(input\_data),

            "budget\_exhausted": False,

            "iterations": 0,

            "max\_iterations": 10,

            "best\_path": None,

            "final\_answer": None

        }

        final\_state \= self.graph.run(state)

        return final\_state\["final\_answer"\]

    def \_init\_tree(self, input\_data):

        """Create the root of the search tree with the initial problem state."""

        return {

            "root": {

                "state\_description": f"Start for {input\_data}",

                "children": \[\],

                "visits": 0,

                "value": 0.0

            }

        }

    def \_select\_node(self, state: Dict) \-\> Dict:

        """

        Picks a promising node to expand based on a policy (e.g., UCB).

        """

        \# ...

        state\["current\_node"\] \= "root"  \# or some selection logic

        return state

    def \_expand\_node(self, state: Dict) \-\> Dict:

        """

        Use an LLM to propose next steps (child nodes).

        """

        \# ...

        \# children \= LLM call to generate possible next actions

        \# attach them to the selected node

        return state

    def \_evaluate\_node(self, state: Dict) \-\> Dict:

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

    def \_check\_budget(self, state: Dict) \-\> Dict:

        """

        If we've done enough iterations, mark budget\_exhausted.

        """

        state\["iterations"\] \+= 1

        if state\["iterations"\] \>= state\["max\_iterations"\]:

            state\["budget\_exhausted"\] \= True

        return state

    def \_choose\_best\_path(self, state: Dict) \-\> Dict:

        """

        From the root, pick the child with the highest average value or visits, etc.

        """

        state\["best\_path"\] \= "some best path"

        return state

    def \_generate\_final\_output(self, state: Dict) \-\> Dict:

        """

        Possibly run a final LLM to write up the chosen path or final solution.

        """

        final\_llm \= self.\_get\_llm("thinking")

        \# final\_text \= final\_llm.predict(...)

        final\_text \= f"Final answer based on best path: {state\['best\_path'\]}"

        state\["final\_answer"\] \= final\_text

        return state

**Builder Tips:**

* **Search Tree Representation**: Usually a nested dict or custom Node class with fields like `children`, `value`, `visits`, etc.

* **LLM Usage**:

  * `_expand_node` might call an LLM to propose 2–5 possible next steps (like partial solutions).

  * `_evaluate_node` might call a different “evaluation” or “reflection” LLM to score each child’s outcome.

* **Iteration Limit**: `max_iterations` or a time budget.

* **Backpropagation**: Summarize child values up to the parent.

  ---

  ## **4.8. Self-Discovery Pattern**

  ### **4.8.1. Overview**

**Goal:** Let the agent *dynamically create or select “reasoning modules”* for the current task. It first identifies which known problem-solving heuristics or “modules” apply, then **adapts** them to the specifics of the query, and **executes** them in a structured manner. Think of it as an agent that “pulls in relevant internal methods” (some big library of ways it’s learned to reason) before diving in.

### **4.8.2. Class: `SelfDiscoveryAgent`**

\# patterns/self\_discovery\_agent.py

from typing import Any, Dict, List

from agent\_patterns.core.base\_agent import BaseAgent

from langgraph import StateGraph

class SelfDiscoveryAgent(BaseAgent):

    def build\_graph(self) \-\> None:

        sg \= StateGraph()

        \# 1\) discover\_or\_select\_modules \-\> 2\) adapt\_modules \-\> 3\) plan\_reasoning\_steps

        \# \-\> 4\) execute\_reasoning\_step (loop for each step) \-\> final

        sg.add\_node("discover\_or\_select\_modules", func=self.\_discover\_or\_select\_modules)

        sg.add\_node("adapt\_modules", func=self.\_adapt\_modules)

        sg.add\_node("plan\_reasoning\_steps", func=self.\_plan\_reasoning\_steps)

        sg.add\_node("execute\_reasoning\_step", func=self.\_execute\_reasoning\_step)

        sg.add\_node("check\_completion", func=self.\_check\_completion)

        sg.add\_node("final\_output", func=lambda s: s)

        \# Linear up to planning

        sg.add\_edge("discover\_or\_select\_modules", "adapt\_modules")

        sg.add\_edge("adapt\_modules", "plan\_reasoning\_steps")

        

        \# Now, for each step in the plan, call execute\_reasoning\_step \-\> check\_completion

        sg.add\_edge("plan\_reasoning\_steps", "execute\_reasoning\_step")

        sg.add\_edge("execute\_reasoning\_step", "check\_completion")

        \# If not done, loop back

        sg.add\_edge("check\_completion", "execute\_reasoning\_step", condition=lambda s: not s\["done\_with\_plan"\])

        sg.add\_edge("check\_completion", "final\_output", condition=lambda s: s\["done\_with\_plan"\])

        self.graph \= sg.compile()

    def run(self, input\_data: Any) \-\> Any:

        state \= {

            "input\_task": input\_data,

            "available\_modules": self.\_load\_module\_library(),

            "selected\_modules": \[\],

            "adapted\_modules": \[\],

            "reasoning\_plan": \[\],

            "plan\_index": 0,

            "done\_with\_plan": False,

            "final\_answer": None

        }

        final\_state \= self.graph.run(state)

        return final\_state\["final\_answer"\]

    def \_load\_module\_library(self) \-\> List\[str\]:

        """

        Potentially a big library of reasoning heuristics or re-usable code fragments.

        In a real system, these might be external knowledge or local 'playbooks.'

        """

        return \["moduleA", "moduleB", "moduleC"\]

    def \_discover\_or\_select\_modules(self, state: Dict) \-\> Dict:

        """

        The agent picks relevant modules from the library for this task, possibly via an LLM.

        """

        \# ...

        state\["selected\_modules"\] \= \["moduleA"\]

        return state

    def \_adapt\_modules(self, state: Dict) \-\> Dict:

        """

        Tailor the selected modules to the specifics of the input task, e.g. rewriting them 

        or customizing them with domain knowledge.

        """

        \# ...

        state\["adapted\_modules"\] \= \["moduleA\_for\_this\_task"\]

        return state

    def \_plan\_reasoning\_steps(self, state: Dict) \-\> Dict:

        """

        Create a step-by-step plan applying the adapted modules in a certain order.

        """

        \# ...

        state\["reasoning\_plan"\] \= \[

            {"description": "Apply moduleA\_for\_this\_task to parse the input"},

            {"description": "Analyze the partial result for solution"}

        \]

        state\["plan\_index"\] \= 0

        return state

    def \_execute\_reasoning\_step(self, state: Dict) \-\> Dict:

        plan \= state\["reasoning\_plan"\]

        i \= state\["plan\_index"\]

        if i \< len(plan):

            step\_desc \= plan\[i\]\["description"\]

            \# Possibly call an LLM or function representing the adapted module

            \# e.g.: step\_output \= self.\_call\_module(step\_desc)

            step\_output \= f"Executed step: {step\_desc}"

            state\["plan\_index"\] \+= 1

            \# optional: store partial results

        return state

    def \_check\_completion(self, state: Dict) \-\> Dict:

        if state\["plan\_index"\] \>= len(state\["reasoning\_plan"\]):

            state\["done\_with\_plan"\] \= True

            state\["final\_answer"\] \= "All modules applied, final result here\!"

        else:

            state\["done\_with\_plan"\] \= False

        return state

**Builder Tips:**

* **Module Library**: Could be a real database or a file with multiple “functions” or heuristics.

* **Selection**: Use a specialized LLM prompt: “Given the user’s goal, pick the best modules from this list.”

* **Adaptation**: Another LLM prompt that modifies or extends the selected module for the user’s domain.

* **Plan**: Then proceed like a “Plan & Solve,” but specifically using your newly discovered/adapted modules.

  ---

  ## **4.9. STORM (Synthesis of Topic Outlines Through Retrieval and Multi-perspective Questioning)**

  ### **4.9.1. Overview**

**Goal:** Produce long-form, multi-perspective articles or reports on a topic by systematically:

1. Generating a **topic outline**.

2. Creating **questions** from multiple viewpoints or “personas” (scientist, policymaker, etc.).

3. **Retrieving** relevant info for each question (via tools or a knowledge base).

4. **Synthesizing** all retrieved data into a structured output.

   ### **4.9.2. Class: `STORMAgent`**

\# patterns/storm\_agent.py

from typing import Any, Dict, List

from agent\_patterns.core.base\_agent import BaseAgent

from langgraph import StateGraph

class STORMAgent(BaseAgent):

    def build\_graph(self) \-\> None:

        sg \= StateGraph()

        

        \# Stage 1: (outline) \-\> (generate\_perspectives) \-\> (generate\_questions)

        sg.add\_node("generate\_outline", func=self.\_generate\_outline)

        sg.add\_node("generate\_perspectives", func=self.\_generate\_perspectives)

        sg.add\_node("generate\_questions", func=self.\_generate\_questions)

        \# Stage 2: (dispatch\_queries) \-\> (execute\_search) \-\> (collect\_search\_results)

        sg.add\_node("dispatch\_queries", func=self.\_dispatch\_queries)

        sg.add\_node("execute\_search", func=self.\_execute\_search)

        sg.add\_node("collect\_search\_results", func=self.\_collect\_search\_results)

        \# Stage 3: (synthesize\_section) \-\> possibly loop over sections \-\> (compile\_report)

        sg.add\_node("synthesize\_sections", func=self.\_synthesize\_sections)

        sg.add\_node("compile\_report", func=self.\_compile\_report)

        sg.add\_node("final\_output", func=lambda s: s)

        \# Edges for stage 1

        sg.add\_edge("generate\_outline", "generate\_perspectives")

        sg.add\_edge("generate\_perspectives", "generate\_questions")

        \# Edges for stage 2

        sg.add\_edge("generate\_questions", "dispatch\_queries")

        sg.add\_edge("dispatch\_queries", "execute\_search")

        sg.add\_edge("execute\_search", "collect\_search\_results")

        \# Edges for stage 3

        sg.add\_edge("collect\_search\_results", "synthesize\_sections")

        sg.add\_edge("synthesize\_sections", "compile\_report")

        sg.add\_edge("compile\_report", "final\_output")

        self.graph \= sg.compile()

    def run(self, input\_data: Any) \-\> Any:

        state \= {

            "topic": input\_data,

            "outline": {},

            "perspectives": \[\],

            "questions": {},

            "search\_results": {},

            "synthesized\_sections": {},

            "final\_report": None

        }

        final\_state \= self.graph.run(state)

        return final\_state\["final\_report"\]

    def \_generate\_outline(self, state: Dict) \-\> Dict:

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

    def \_generate\_perspectives(self, state: Dict) \-\> Dict:

        """

        Identify relevant viewpoints/personas from which to question the topic (e.g. 

        'scientist', 'economist', 'policymaker').

        """

        \# ...

        state\["perspectives"\] \= \["scientist", "policymaker"\]

        return state

    def \_generate\_questions(self, state: Dict) \-\> Dict:

        """

        For each outline section and perspective, produce a list of questions to research.

        """

        questions\_dict \= {}

        for section in state\["outline"\]:

            questions\_dict\[section\] \= {}

            for p in state\["perspectives"\]:

                \# e.g. LLM call to generate relevant Qs

                questions\_dict\[section\]\[p\] \= \[f"Key {p} question about {section}"\]

        state\["questions"\] \= questions\_dict

        return state

    def \_dispatch\_queries(self, state: Dict) \-\> Dict:

        """

        Possibly prepare parallel queries for each question. 

        """

        \# ...

        return state

    def \_execute\_search(self, state: Dict) \-\> Dict:

        """

        Execute all queries, presumably via a search or retrieval tool. 

        Results stored in search\_results\[section\]\[perspective\].

        """

        results \= {}

        for section, pers\_map in state\["questions"\].items():

            results\[section\] \= {}

            for p, q\_list in pers\_map.items():

                \# call the knowledge base, gather text

                results\[section\]\[p\] \= \[f"Mock retrieved info for {q}" for q in q\_list\]

        state\["search\_results"\] \= results

        return state

    def \_collect\_search\_results(self, state: Dict) \-\> Dict:

        """

        Summarize or store them (if needed). Right now we just keep them in state.

        """

        return state

    def \_synthesize\_sections(self, state: Dict) \-\> Dict:

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

        state\["synthesized\_sections"\] \= synthesized

        return state

    def \_compile\_report(self, state: Dict) \-\> Dict:

        """

        Combine section texts into a final coherent report.

        """

        final\_text \= \[\]

        for section in \["Introduction", "MainBody", "Conclusion"\]:

            sec\_content \= state\["synthesized\_sections"\].get(section, "")

            final\_text.append(f"{section}:\\n{sec\_content}")

        state\["final\_report"\] \= "\\n\\n".join(final\_text)

        return state

**Builder Tips:**

1. **Outline & Perspectives**: Provide separate prompts to generate a structured outline and the relevant expert viewpoints (or “personas”).

2. **Multi-Question Generation**: A for-loop approach over (section × perspective). The LLM can produce targeted queries for each vantage point.

3. **Retrieval**: Any search or knowledge-base calls happen in `_execute_search`. Could be parallel tasks in LangGraph if desired.

4. **Synthesis**: Merges the retrieved data from multiple angles, typically with a “documentation” model specialized for summarizing large text.

5. **Customization**:

   * Expand the outline with sub-sections.

   * For deeply technical writing, add additional reflection or re-check steps.

   ---

See `patterns/` directory for each pattern’s reference implementation. The sections in this document serve as a template, ensuring consistency across patterns.

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

OPENAI\_API\_KEY= "your-key"  
THINKING\_MODEL\_PROVIDER=openai  
THINKING\_MODEL\_NAME="gpt-4-turbo"  
REFLECTION\_MODEL\_PROVIDER=anthropic  
REFLECTION\_MODEL\_NAME="claude-3.5"

**`llm_configs`** can be built by parsing `.env`:

import os  
from dotenv import load\_dotenv

load\_dotenv()  
llm\_configs \= {  
    "thinking": {  
        "provider": os.getenv("THINKING\_MODEL\_PROVIDER"),  
        "model\_name": os.getenv("THINKING\_MODEL\_NAME"),  
    },  
    \# ... likewise for reflection, documentation, etc.  
}

Then pass `llm_configs` to each pattern’s constructor:

my\_reflection\_agent \= ReflectionAgent(llm\_configs=llm\_configs, prompt\_dir="prompts")  
result \= my\_reflection\_agent.run("Explain quantum entanglement in simple terms.")

---

## **7\. Testing & Example Usage**

### **7.1. Example Scripts**

Each pattern has a dedicated example script in `examples/`. For instance, `reflection_example.py` might look like:

\# examples/reflection\_example.py  
import os  
from dotenv import load\_dotenv  
from agent\_patterns.patterns.reflection\_agent import ReflectionAgent

def main():  
    load\_dotenv()  
    llm\_configs \= {  
        "documentation": {  
            "provider": os.getenv("DOCUMENTATION\_MODEL\_PROVIDER"),  
            "model\_name": os.getenv("DOCUMENTATION\_MODEL\_NAME"),  
        },  
        "reflection": {  
            "provider": os.getenv("REFLECTION\_MODEL\_PROVIDER"),  
            "model\_name": os.getenv("REFLECTION\_MODEL\_NAME"),  
        }  
    }

    agent \= ReflectionAgent(llm\_configs=llm\_configs)  
    final\_answer \= agent.run("Write a short story about a robot dog.")  
    print(final\_answer)

if \_\_name\_\_ \== "\_\_main\_\_":  
    main()

### **7.2. Tests**

Under `tests/`, create unit tests ensuring each pattern handles typical and edge cases. Use mocks or stubs for LLM calls:

\# tests/test\_reflection.py  
import pytest  
from unittest.mock import patch  
from agent\_patterns.patterns.reflection\_agent import ReflectionAgent

def test\_reflection\_agent\_basic():  
    agent \= ReflectionAgent(llm\_configs={}, prompt\_dir="prompts")  
    with patch.object(agent, "\_get\_llm", return\_value=lambda x: "mock\_llm\_response"):  
        output \= agent.run("Test input")  
        assert "mock" in output  \# simplistic check

---

## **8\. Notes on Extensibility & Best Practices**

1. **Externalize Tools**: Patterns like ReAct rely on multiple external tools (e.g., web search, calculator). Provide a `ToolRegistry` or pass a `tools` dictionary into the agent’s constructor so new tools can be added easily.

2. **Parallel Execution**: LangGraph supports parallel nodes. Use them for multi-step or multi-agent tasks if beneficial.

3. **Prompt Tuning**: Encourage domain-specific prompts. This design expects developers to refine their prompts in `.md` files.

4. **Iteration Limits & Safety**: Patterns like Reflection can loop. Always define a max iteration or safe stop condition to avoid infinite loops or excessive token usage.

5. **Logging & Observability**: Consider hooking into the agent’s lifecycle with logs for each node (e.g., logging the LLM’s output at each step). This helps debug or interpret the agent’s chain-of-thought.

---

## **9\. How to Create a New Pattern**

1. **Subclass** either `BaseAgent` or `MultiAgentBase`.

2. **Define `build_graph()`**: Create a `StateGraph`, add your nodes, transitions, and compile it.

3. **Implement** all node functions (the “steps”):

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

* Consult each pattern’s docstrings for detailed instructions.

* Submit issues or PRs on our GitHub repository to propose improvements or new patterns.

**Happy coding with agent-patterns\!**
