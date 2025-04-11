# Migration Guide

This guide helps you migrate from other agent frameworks to Agent Patterns.

## Migrating from LangChain Agents

LangChain is a popular framework for building LLM applications. This section covers how to migrate from LangChain Agents to Agent Patterns.

### Conceptual Mapping

| LangChain Concept | Agent Patterns Equivalent |
|-------------------|---------------------------|
| Agent | Agent Pattern (ReAct, Reflexion, etc.) |
| AgentExecutor | BaseAgent (run method) |
| Tool | Tool (from core.tools) |
| Memory | Memory Components (SemanticMemory, EpisodicMemory) |
| PromptTemplate | Externalized prompts in text files |
| LLMChain | Internal to Agent Patterns (abstracted) |
| OutputParser | Internal to Agent Patterns (abstracted) |
| ConversationChain | Not directly equivalent; use ReActAgent with memory |

### Migration Steps

1. **Tool Migration**

LangChain tools can be converted to Agent Patterns tools:

**LangChain Tool:**
```python
from langchain.tools import BaseTool
from typing import Optional, Type

class CalculatorTool(BaseTool):
    name = "calculator"
    description = "Useful for performing arithmetic calculations"
    
    def _run(self, query: str) -> str:
        try:
            return str(eval(query))
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)
```

**Agent Patterns Equivalent:**
```python
from agent_patterns.core.tools.base import BaseToolProvider, Tool

class CalculatorToolProvider(BaseToolProvider):
    def get_tools(self):
        return [
            Tool(
                name="calculator",
                description="Useful for performing arithmetic calculations",
                function=self.calculate,
                parameters={
                    "expression": {
                        "type": "string",
                        "description": "The arithmetic expression to evaluate"
                    }
                }
            )
        ]
    
    async def calculate(self, expression):
        try:
            return {"result": str(eval(expression))}
        except Exception as e:
            return {"error": str(e)}
```

2. **Memory Migration**

LangChain memory components can be migrated to Agent Patterns memory:

**LangChain Memory:**
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(return_messages=True)
memory.chat_memory.add_user_message("Hello!")
memory.chat_memory.add_ai_message("Hi there!")

# Use in agent
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True
)
```

**Agent Patterns Equivalent:**
```python
from agent_patterns.core.memory import EpisodicMemory
from agent_patterns.core.memory.persistence import InMemoryPersistence
import asyncio

# Create persistence and memory components
persistence = InMemoryPersistence()
asyncio.run(persistence.initialize())
episodic_memory = EpisodicMemory(persistence, namespace="conversation")

# Add messages
asyncio.run(episodic_memory.save({
    "role": "user",
    "content": "Hello!"
}))
asyncio.run(episodic_memory.save({
    "role": "assistant",
    "content": "Hi there!"
}))

# Use in agent
agent = ReActAgent(
    llm_configs={"default": {"provider": "openai", "model_name": "gpt-4o"}},
    memory=episodic_memory,
    memory_config={"episodic": True}
)
```

3. **Agent Migration**

Migrating a full LangChain agent:

**LangChain Agent:**
```python
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.tools import DuckDuckGoSearchRun

# Define tools
search_tool = DuckDuckGoSearchRun()
tools = [search_tool]

# Create LLM
llm = OpenAI(temperature=0)

# Create agent
agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Run agent
result = agent.run("What is the weather in New York?")
```

**Agent Patterns Equivalent:**
```python
from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.tools.providers.search_provider import SearchToolProvider

# Create tool provider
search_provider = SearchToolProvider()

# Create agent
agent = ReActAgent(
    llm_configs={"default": {"provider": "openai", "model_name": "gpt-4o"}},
    tool_provider=search_provider
)

# Run agent
result = agent.run("What is the weather in New York?")
```

### Complete Migration Example

**Original LangChain Application:**
```python
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper
from langchain.memory import ConversationBufferMemory

# Create tools
search = DuckDuckGoSearchRun()
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
tools = [search, wikipedia]

# Set up memory
memory = ConversationBufferMemory(return_messages=True)

# Create LLM
llm = OpenAI(temperature=0.7)

# Create agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory
)

# Run agent
query = "Tell me about the Eiffel Tower and then tell me how tall it is in feet."
result = agent.run(query)
print(result)
```

**Migrated Agent Patterns Application:**
```python
from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.tools.providers.search_provider import SearchToolProvider
from agent_patterns.core.tools.providers.wikipedia_provider import WikipediaToolProvider
from agent_patterns.core.memory import EpisodicMemory, CompositeMemory
from agent_patterns.core.memory.persistence import InMemoryPersistence
from agent_patterns.core.tools.providers.composite_provider import CompositeToolProvider
import asyncio

# Set up memory
persistence = InMemoryPersistence()
asyncio.run(persistence.initialize())
memory = CompositeMemory({
    "episodic": EpisodicMemory(persistence, namespace="conversation")
})

# Set up tool providers
search_provider = SearchToolProvider()
wikipedia_provider = WikipediaToolProvider()
tool_provider = CompositeToolProvider([search_provider, wikipedia_provider])

# Create agent
agent = ReActAgent(
    llm_configs={"default": {"provider": "openai", "model_name": "gpt-4o", "temperature": 0.7}},
    memory=memory,
    memory_config={"episodic": True},
    tool_provider=tool_provider
)

# Run agent
query = "Tell me about the Eiffel Tower and then tell me how tall it is in feet."
result = agent.run(query)
print(result)
```

## Migrating from AutoGPT

AutoGPT is an autonomous agent framework. This section covers migration from AutoGPT to Agent Patterns.

### Conceptual Mapping

| AutoGPT Concept | Agent Patterns Equivalent |
|-----------------|---------------------------|
| Agent | Self-Discovery or LATS agent |
| Memory | CompositeMemory with SemanticMemory |
| Commands | Tools |
| Autonomous Mode | Self-Discovery agent with continuous runs |
| Browsing | Web search tools |
| File Operations | File operation tools |
| Planning | Plan & Solve or LLM Compiler agent |

### Migration Steps

1. **Command Migration**

AutoGPT commands can be converted to Agent Patterns tools:

**AutoGPT Command:**
```python
def google_search(query, num_results=8):
    """Perform a Google search and return the results."""
    search_results = []
    try:
        from duckduckgo_search import ddg
        results = ddg(query, max_results=num_results)
        for result in results:
            search_results.append({
                "title": result["title"],
                "href": result["href"],
                "body": result["body"]
            })
    except Exception as e:
        return f"Error: {str(e)}"
    return search_results
```

**Agent Patterns Equivalent:**
```python
from agent_patterns.core.tools.base import BaseToolProvider, Tool

class SearchToolProvider(BaseToolProvider):
    def get_tools(self):
        return [
            Tool(
                name="search",
                description="Search the web for information",
                function=self.search,
                parameters={
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 8
                    }
                }
            )
        ]
    
    async def search(self, query, num_results=8):
        try:
            from duckduckgo_search import ddg
            results = ddg(query, max_results=num_results)
            search_results = []
            for result in results:
                search_results.append({
                    "title": result["title"],
                    "url": result["href"],
                    "snippet": result["body"]
                })
            return {"results": search_results}
        except Exception as e:
            return {"error": str(e)}
```

2. **Memory Migration**

AutoGPT memory can be migrated to Agent Patterns memory:

**AutoGPT Memory:**
```python
from autogpt.memory import LocalCache
from autogpt.workspace import Workspace

workspace = Workspace("workspace")
memory = LocalCache(workspace.root)

# Store information
memory.add("Eiffel Tower", "The Eiffel Tower is 330 meters tall.")

# Retrieve information
results = memory.get("Eiffel Tower")
```

**Agent Patterns Equivalent:**
```python
from agent_patterns.core.memory import SemanticMemory
from agent_patterns.core.memory.persistence import FilePersistence
import asyncio

# Create persistence and memory
persistence = FilePersistence(directory="./memory_store")
asyncio.run(persistence.initialize())
memory = SemanticMemory(persistence, namespace="knowledge")

# Store information
asyncio.run(memory.save({
    "entity": "Eiffel Tower",
    "attribute": "height",
    "value": "330 meters"
}))

# Retrieve information
results = asyncio.run(memory.retrieve("Eiffel Tower height"))
```

3. **Autonomous Agent Migration**

Migrating an AutoGPT agent:

**AutoGPT-like Agent:**
```python
# Pseudocode based on AutoGPT concepts
from autogpt.agent import Agent
from autogpt.config import Config
from autogpt.memory import LocalCache
from autogpt.workspace import Workspace

# Configure agent
config = Config()
config.set_continuous_mode(True)
config.set_memory_backend("local")

# Set up workspace and memory
workspace = Workspace("workspace")
memory = LocalCache(workspace.root)

# Create agent
agent = Agent(
    ai_name="Research Assistant",
    ai_role="A research assistant that finds information on the web.",
    tools=["google", "memory", "write_file"],
    memory=memory,
    config=config
)

# Run agent
agent.run("Research the impact of climate change on agriculture and write a report.")
```

**Agent Patterns Equivalent:**
```python
from agent_patterns.patterns.self_discovery_agent import SelfDiscoveryAgent
from agent_patterns.core.memory import SemanticMemory, CompositeMemory
from agent_patterns.core.memory.persistence import FilePersistence
from agent_patterns.core.tools.providers.composite_provider import CompositeToolProvider
from agent_patterns.core.tools.providers.search_provider import SearchToolProvider
from agent_patterns.core.tools.providers.file_provider import FileToolProvider
import asyncio

# Set up memory
persistence = FilePersistence(directory="./memory_store")
asyncio.run(persistence.initialize())
memory = CompositeMemory({
    "semantic": SemanticMemory(persistence, namespace="knowledge")
})

# Set up tools
search_provider = SearchToolProvider()
file_provider = FileToolProvider(workspace_dir="./workspace")
tool_provider = CompositeToolProvider([search_provider, file_provider])

# Create agent
agent = SelfDiscoveryAgent(
    llm_configs={
        "default": {"provider": "openai", "model_name": "gpt-4o"},
        "planning": {"provider": "anthropic", "model_name": "claude-3-opus-20240229"}
    },
    memory=memory,
    memory_config={"semantic": True},
    tool_provider=tool_provider,
    max_iterations=15  # Control autonomous behavior
)

# Run agent
result = agent.run("Research the impact of climate change on agriculture and write a report.")
```

### Complete Migration Example

**Original AutoGPT-style Application:**
```python
# Pseudocode based on AutoGPT concepts
from autogpt.agent import Agent
from autogpt.config import Config
from autogpt.memory import LocalCache
from autogpt.workspace import Workspace
from autogpt.commands import google_search, write_file, read_file

# Configure agent
config = Config()
config.set_continuous_mode(True)
config.set_memory_backend("local")
config.set_max_iterations(15)

# Set up workspace and memory
workspace = Workspace("workspace")
memory = LocalCache(workspace.root)

# Define custom commands
def analyze_sentiment(text):
    # Simplified sentiment analysis
    positive_words = ["good", "great", "excellent", "positive", "beneficial"]
    negative_words = ["bad", "terrible", "negative", "harmful", "poor"]
    
    positive_count = sum(word in text.lower() for word in positive_words)
    negative_count = sum(word in text.lower() for word in negative_words)
    
    if positive_count > negative_count:
        return "Positive"
    elif negative_count > positive_count:
        return "Negative"
    else:
        return "Neutral"

# Register commands
commands = {
    "google": google_search,
    "write_file": write_file,
    "read_file": read_file,
    "analyze_sentiment": analyze_sentiment
}

# Create agent
agent = Agent(
    ai_name="Research Assistant",
    ai_role="A research assistant that analyzes sentiment in news articles.",
    tools=commands,
    memory=memory,
    config=config
)

# Run agent
agent.run("Research recent news about climate change, analyze the sentiment of articles, and write a summary report.")
```

**Migrated Agent Patterns Application:**
```python
from agent_patterns.patterns.self_discovery_agent import SelfDiscoveryAgent
from agent_patterns.core.memory import SemanticMemory, CompositeMemory
from agent_patterns.core.memory.persistence import FilePersistence
from agent_patterns.core.tools.providers.composite_provider import CompositeToolProvider
from agent_patterns.core.tools.providers.search_provider import SearchToolProvider
from agent_patterns.core.tools.providers.file_provider import FileToolProvider
from agent_patterns.core.tools.base import BaseToolProvider, Tool
import asyncio

# Custom sentiment analysis tool provider
class SentimentToolProvider(BaseToolProvider):
    def get_tools(self):
        return [
            Tool(
                name="analyze_sentiment",
                description="Analyze the sentiment of a text as positive, negative, or neutral",
                function=self.analyze_sentiment,
                parameters={
                    "text": {
                        "type": "string",
                        "description": "The text to analyze"
                    }
                }
            )
        ]
    
    async def analyze_sentiment(self, text):
        # Simplified sentiment analysis
        positive_words = ["good", "great", "excellent", "positive", "beneficial"]
        negative_words = ["bad", "terrible", "negative", "harmful", "poor"]
        
        positive_count = sum(word in text.lower() for word in positive_words)
        negative_count = sum(word in text.lower() for word in negative_words)
        
        if positive_count > negative_count:
            sentiment = "Positive"
        elif negative_count > positive_count:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        
        return {
            "sentiment": sentiment,
            "positive_score": positive_count,
            "negative_score": negative_count
        }

# Set up memory
persistence = FilePersistence(directory="./memory_store")
asyncio.run(persistence.initialize())
memory = CompositeMemory({
    "semantic": SemanticMemory(persistence, namespace="knowledge")
})

# Set up tools
search_provider = SearchToolProvider()
file_provider = FileToolProvider(workspace_dir="./workspace")
sentiment_provider = SentimentToolProvider()
tool_provider = CompositeToolProvider([
    search_provider, 
    file_provider, 
    sentiment_provider
])

# Create agent
agent = SelfDiscoveryAgent(
    llm_configs={
        "default": {"provider": "openai", "model_name": "gpt-4o"},
        "planning": {"provider": "anthropic", "model_name": "claude-3-opus-20240229"}
    },
    memory=memory,
    memory_config={"semantic": True},
    tool_provider=tool_provider,
    max_iterations=15
)

# Run agent
result = agent.run("Research recent news about climate change, analyze the sentiment of articles, and write a summary report.")
print(result)
```

## Migrating from Custom Implementations

This section covers how to migrate from custom agent implementations to Agent Patterns.

### Migration Strategy

1. **Identify Components**: Break down your custom implementation into:
   - Agent logic
   - Prompting
   - Tool execution
   - Memory/state management
   - Model calling

2. **Select Appropriate Pattern**: Choose the Agent Pattern that closest matches your implementation:
   - Simple reasoning and tools: ReAct
   - Planning then execution: Plan & Solve
   - Self-improvement: Reflexion or Reflection
   - Dynamic workflows: LLM Compiler
   - Monitoring: LATS
   - Complex reasoning: STORM

3. **Map Custom Logic**: Identify places where your custom logic needs to be preserved

4. **Implement Migration**: Either:
   - Use an existing pattern with customization
   - Extend BaseAgent to create a custom pattern

### Example: Migrating a Custom Agent

**Original Custom Implementation:**
```python
import openai
import os
import json

class CustomAgent:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.conversation_history = []
        self.tools = {
            "search": self.search,
            "calculator": self.calculator
        }
    
    def search(self, query):
        # Mock search function
        return f"Search results for: {query}"
    
    def calculator(self, expression):
        try:
            return str(eval(expression))
        except Exception as e:
            return f"Error: {str(e)}"
    
    def call_model(self, prompt):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def parse_tool_calls(self, text):
        try:
            if "USE TOOL:" in text:
                parts = text.split("USE TOOL:")
                tool_part = parts[1].strip()
                tool_json = json.loads(tool_part)
                return {
                    "tool": tool_json.get("tool"),
                    "parameters": tool_json.get("parameters", {})
                }
            return None
        except Exception:
            return None
    
    def run(self, query):
        self.conversation_history.append({"role": "user", "content": query})
        
        prompt = f"""
        You are a helpful assistant that can use tools to answer questions.
        Available tools:
        - search: Search for information online. Parameters: {{"query": "search query"}}
        - calculator: Perform calculations. Parameters: {{"expression": "math expression"}}
        
        Conversation history:
        {self.format_history()}
        
        To use a tool, respond with:
        USE TOOL: {{"tool": "tool_name", "parameters": {{"param1": "value1"}}}}
        
        User query: {query}
        """
        
        max_iterations = 5
        iterations = 0
        
        while iterations < max_iterations:
            iterations += 1
            
            # Call model
            response = self.call_model(prompt)
            
            # Check for tool calls
            tool_call = self.parse_tool_calls(response)
            
            if tool_call:
                tool_name = tool_call["tool"]
                parameters = tool_call["parameters"]
                
                if tool_name in self.tools:
                    # Execute tool
                    if tool_name == "search":
                        result = self.tools[tool_name](parameters.get("query", ""))
                    elif tool_name == "calculator":
                        result = self.tools[tool_name](parameters.get("expression", ""))
                    else:
                        result = "Unknown tool"
                    
                    # Update conversation history
                    self.conversation_history.append({"role": "assistant", "content": response})
                    self.conversation_history.append({"role": "system", "content": f"Tool result: {result}"})
                    
                    # Update prompt
                    prompt = f"""
                    You are a helpful assistant that can use tools to answer questions.
                    Available tools:
                    - search: Search for information online. Parameters: {{"query": "search query"}}
                    - calculator: Perform calculations. Parameters: {{"expression": "math expression"}}
                    
                    Conversation history:
                    {self.format_history()}
                    
                    To use a tool, respond with:
                    USE TOOL: {{"tool": "tool_name", "parameters": {{"param1": "value1"}}}}
                    
                    Given the tool result, provide a final answer or use another tool if needed.
                    """
                else:
                    return f"Unknown tool: {tool_name}"
            else:
                # Final answer
                self.conversation_history.append({"role": "assistant", "content": response})
                return response
        
        return "Maximum iterations reached without final answer."
    
    def format_history(self):
        formatted = ""
        for entry in self.conversation_history:
            formatted += f"{entry['role']}: {entry['content']}\n\n"
        return formatted
```

**Migrated to Agent Patterns:**
```python
from agent_patterns.patterns.re_act_agent import ReActAgent
from agent_patterns.core.tools.base import BaseToolProvider, Tool
from agent_patterns.core.memory import EpisodicMemory
from agent_patterns.core.memory.persistence import InMemoryPersistence
import asyncio

class CustomToolProvider(BaseToolProvider):
    def get_tools(self):
        return [
            Tool(
                name="search",
                description="Search for information online",
                function=self.search,
                parameters={
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                }
            ),
            Tool(
                name="calculator",
                description="Perform calculations",
                function=self.calculate,
                parameters={
                    "expression": {
                        "type": "string",
                        "description": "The math expression to evaluate"
                    }
                }
            )
        ]
    
    async def search(self, query):
        # Mock search function
        return {"results": f"Search results for: {query}"}
    
    async def calculate(self, expression):
        try:
            return {"result": str(eval(expression))}
        except Exception as e:
            return {"error": str(e)}

# Set up memory
persistence = InMemoryPersistence()
asyncio.run(persistence.initialize())
memory = EpisodicMemory(persistence, namespace="conversation")

# Set up tool provider
tool_provider = CustomToolProvider()

# Create agent
agent = ReActAgent(
    llm_configs={"default": {"provider": "openai", "model_name": "gpt-4", "temperature": 0.7}},
    memory=memory,
    memory_config={"episodic": True},
    tool_provider=tool_provider
)

# Run agent
result = agent.run("What is the population of France and calculate 15% of that number.")
print(result)
```

### Advanced Migration: Custom Pattern

If your custom implementation doesn't map well to existing patterns, create a custom pattern:

```python
from agent_patterns.core.base_agent import BaseAgent
from langchain.graphs import Graph

class CustomPatternAgent(BaseAgent):
    """Custom agent pattern based on unique workflow."""
    
    def __init__(
        self,
        llm_configs=None,
        memory=None,
        memory_config=None,
        tool_provider=None,
        max_iterations=5,
        **kwargs
    ):
        super().__init__(
            llm_configs=llm_configs,
            memory=memory,
            memory_config=memory_config,
            tool_provider=tool_provider
        )
        self.max_iterations = max_iterations
    
    def build_graph(self):
        """Build the custom workflow graph."""
        builder = Graph()
        
        # Define nodes (steps in your workflow)
        builder.add_node("start", self.start_node)
        builder.add_node("analyze", self.analyze_node)
        builder.add_node("plan", self.plan_node)
        builder.add_node("execute", self.execute_node)
        builder.add_node("evaluate", self.evaluate_node)
        builder.add_node("final", self.final_node)
        
        # Define edges (transitions between steps)
        builder.add_edge("start", "analyze")
        builder.add_edge("analyze", "plan")
        builder.add_edge("plan", "execute")
        builder.add_edge("execute", "evaluate")
        
        # Add conditional edges
        builder.add_conditional_edges(
            "evaluate",
            self.should_continue,
            {
                True: "execute",
                False: "final"
            }
        )
        
        # Set the entry point
        builder.set_entry_point("start")
        
        # Build and return the graph
        return builder.compile()
    
    def start_node(self, state):
        """Initialize the workflow state."""
        # Get the user query
        query = state["query"]
        
        # Initialize response structure
        response = {
            "analysis": "",
            "plan": [],
            "executions": [],
            "evaluations": [],
            "final_answer": ""
        }
        
        # Add memory context if available
        if self.memory:
            response["memory_context"] = self.retrieve_from_memory(query)
        
        # Update state
        state["response"] = response
        state["iterations"] = 0
        
        return state
    
    def analyze_node(self, state):
        """Analyze the query."""
        prompt = self._get_prompt("analyze")
        formatted_prompt = prompt.format(
            query=state["query"],
            memory_context=state["response"].get("memory_context", "")
        )
        
        analysis = self._call_llm(formatted_prompt, "default")
        state["response"]["analysis"] = analysis
        
        return state
    
    def plan_node(self, state):
        """Create a plan based on analysis."""
        prompt = self._get_prompt("plan")
        formatted_prompt = prompt.format(
            query=state["query"],
            analysis=state["response"]["analysis"]
        )
        
        plan_text = self._call_llm(formatted_prompt, "default")
        
        # Parse plan into steps
        import re
        steps = re.findall(r'\d+\.\s+(.*)', plan_text)
        state["response"]["plan"] = steps
        
        return state
    
    def execute_node(self, state):
        """Execute the current step in the plan."""
        current_step_index = len(state["response"]["executions"])
        
        if current_step_index >= len(state["response"]["plan"]):
            # No more steps to execute
            return state
        
        current_step = state["response"]["plan"][current_step_index]
        
        prompt = self._get_prompt("execute")
        formatted_prompt = prompt.format(
            query=state["query"],
            step=current_step,
            previous_executions=state["response"]["executions"]
        )
        
        execution_result = self._call_llm(formatted_prompt, "default")
        
        # Check if tool use is needed
        tool_call = self._parse_tool_call(execution_result)
        if tool_call and self.tool_provider:
            tool_name = tool_call["tool"]
            params = tool_call["params"]
            
            # Execute tool
            tool_result = self.tool_provider.execute_tool(tool_name, **params)
            
            # Update execution result
            execution_result += f"\nTool result: {tool_result}"
        
        # Add to executions
        state["response"]["executions"].append({
            "step": current_step,
            "result": execution_result
        })
        
        return state
    
    def evaluate_node(self, state):
        """Evaluate the current execution."""
        prompt = self._get_prompt("evaluate")
        
        current_execution = state["response"]["executions"][-1]
        
        formatted_prompt = prompt.format(
            query=state["query"],
            step=current_execution["step"],
            result=current_execution["result"]
        )
        
        evaluation = self._call_llm(formatted_prompt, "default")
        
        # Parse evaluation score (0-10)
        import re
        score_match = re.search(r'Score:\s*(\d+)', evaluation)
        if score_match:
            score = int(score_match.group(1))
        else:
            score = 5  # Default middle score
        
        # Add to evaluations
        state["response"]["evaluations"].append({
            "step": current_execution["step"],
            "evaluation": evaluation,
            "score": score
        })
        
        # Increment iterations
        state["iterations"] += 1
        
        return state
    
    def should_continue(self, state):
        """Determine if execution should continue."""
        # Check if we've reached max iterations
        if state["iterations"] >= self.max_iterations:
            return False
        
        # Check if we've completed all plan steps
        if len(state["response"]["executions"]) >= len(state["response"]["plan"]):
            return False
        
        # Check the latest evaluation score
        latest_eval = state["response"]["evaluations"][-1]
        if latest_eval["score"] < 3:  # Low score indicates issues
            # Retry the step, which happens by returning to execute
            return True
        
        # Continue to next step
        return True
    
    def final_node(self, state):
        """Generate the final answer."""
        prompt = self._get_prompt("final")
        
        formatted_prompt = prompt.format(
            query=state["query"],
            analysis=state["response"]["analysis"],
            plan=state["response"]["plan"],
            executions=state["response"]["executions"],
            evaluations=state["response"]["evaluations"]
        )
        
        final_answer = self._call_llm(formatted_prompt, "default")
        state["response"]["final_answer"] = final_answer
        
        # Save to memory if available
        if self.memory:
            self.save_to_memory(state["query"], state["response"])
        
        return state
    
    def _parse_tool_call(self, text):
        """Parse tool calls from text."""
        import re
        import json
        
        tool_pattern = r'USE TOOL:\s*({.*})'
        match = re.search(tool_pattern, text)
        
        if match:
            try:
                tool_json = json.loads(match.group(1))
                return {
                    "tool": tool_json.get("tool"),
                    "params": tool_json.get("parameters", {})
                }
            except:
                pass
        
        return None
```

Use the custom pattern:

```python
# Create custom agent
agent = CustomPatternAgent(
    llm_configs={"default": {"provider": "openai", "model_name": "gpt-4o"}},
    tool_provider=tool_provider,
    max_iterations=5
)

# Run agent
result = agent.run("Analyze recent market trends for renewable energy and provide investment recommendations.")
print(result)
```