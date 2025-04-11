Getting Started
===============

Installation
-----------

You can install agent-patterns using pip:

.. code-block:: bash

   pip install agent-patterns

Basic Usage
----------

Here's a simple example of how to use the ReAct agent pattern:

.. code-block:: python

   from agent_patterns.patterns import ReActAgent
   from langchain_openai import ChatOpenAI

   # Initialize the language model
   llm = ChatOpenAI(model="gpt-4-turbo")

   # Create an agent with the ReAct pattern
   agent = ReActAgent(llm=llm)

   # Define available tools
   tools = [
       # Your tools here
   ]

   # Add tools to the agent
   agent.add_tools(tools)

   # Run the agent
   response = agent.run("What is the weather in New York?")
   print(response)

Custom Patterns
--------------

You can also create your own patterns by extending the base classes:

.. code-block:: python

   from agent_patterns.core import BaseAgent
   import langgraph as lg

   class MyCustomAgent(BaseAgent):
       def build_graph(self):
           # Define your custom graph structure here
           workflow = lg.Graph()
           # Add nodes and edges
           return workflow