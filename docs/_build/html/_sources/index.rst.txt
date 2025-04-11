Agent-Patterns
=============

A Python library providing reusable, extensible, and well-documented base classes for common AI agent workflows using `LangGraph <https://langchain.com/docs/langgraph>`_ and `LangChain <https://python.langchain.com/en/latest/>`_.

.. toctree::
   :maxdepth: 2
   :caption: Documentation:
   :hidden:

   guides/index
   tutorials/index
   patterns/index
   api/index
   Design
   Agent Memory Design
   Agent_Tools_Design
   Memory API Documentation
   Memory Integration Tutorial
   Tool Provider API Documentation
   MCP Tool Integration Tutorial
   memory_and_mcp_integration
   Next Steps

Overview
--------

Agent-Patterns implements proven design patterns for AI agents, reducing boilerplate and encouraging consistent best practices. The library is especially useful for developers needing to quickly build or customize advanced AI workflows without reinventing the wheel.

Installation
-----------

.. code-block:: bash

   pip install agent-patterns

Documentation
------------

For comprehensive documentation of all patterns and components, see this documentation site.

Guides
~~~~~~

- :doc:`Getting Started Guide <guides/getting_started>`: Installation and your first agent
- :doc:`Pattern Selection Guide <guides/pattern_selection>`: Choosing the right pattern for your use case
- :doc:`Advanced Customization Guide <guides/advanced_customization>`: Extending the library
- :doc:`Troubleshooting Guide <guides/troubleshooting>`: Solving common issues
- :doc:`Deployment Guide <guides/deployment>`: Deploying in production environments
- :doc:`Migration Guide <guides/migration>`: Migrating from other frameworks

See all guides in the :doc:`Guides Index <guides/index>`.

Tutorials
~~~~~~~~~

- :doc:`Research Assistant <tutorials/research_assistant>`: Building an AI research assistant
- :doc:`Customer Support Bot <tutorials/customer_support_bot>`: Creating a support agent
- :doc:`Code Generation Agent <tutorials/code_generation_agent>`: Developing a code generator
- :doc:`Multi-Agent System <tutorials/multi_agent_system>`: Building a collaborative system

See all tutorials in the :doc:`Tutorials Index <tutorials/index>`.

Supported Patterns
~~~~~~~~~~~~~~~~~

- :doc:`ReAct (Reason + Act) <patterns/re_act>`: Iterative reasoning and action for tool-based problem solving `(arXiv Paper) <https://arxiv.org/abs/2210.03629>`_
- :doc:`Plan & Solve <patterns/plan_and_solve>`: Decoupled planning and execution phases `(arXiv Paper) <https://arxiv.org/abs/2305.04091>`_
- :doc:`Reflection <patterns/reflection>`: Periodic reflection for strategic adjustments
- :doc:`Reflexion <patterns/reflexion>`: ReAct with reflection capabilities for self-improvement `(arXiv Paper) <https://arxiv.org/abs/2303.11366>`_
- :doc:`LLM Compiler <patterns/llm_compiler>`: Dynamic execution graph construction and optimization `(arXiv Paper) <https://arxiv.org/abs/2312.04511>`_
- :doc:`ReWOO <patterns/rewoo>`: Reason, World model, Observe, Outcome for simulation `(arXiv Paper) <https://arxiv.org/abs/2305.18323>`_
- :doc:`LATS <patterns/lats>`: LangChain Agents Tracing System for comprehensive observability `(arXiv Paper) <https://arxiv.org/abs/2310.04406>`_
- :doc:`STORM <patterns/storm>`: Self-evaluation, Think of options, Options for reasoning, Reason step by step, Mistake detection `(NAACL Paper) <https://aclanthology.org/2024.naacl-long.347.pdf>`_
- :doc:`Self-Discovery <patterns/self_discovery>`: Agents that discover their own capabilities
- :doc:`Reflection and Refinement <patterns/reflection_and_refinement>`: Structured reflection with explicit refinement steps

See all patterns in the :doc:`Patterns Index <patterns/index>`.

API Reference
~~~~~~~~~~~~

- :doc:`Core API <api/core>`: Base classes and core components
- :doc:`Patterns API <api/patterns>`: Pattern implementations
- :doc:`Memory API <api/memory>`: Memory system
- :doc:`Tools API <api/tools>`: Tool system

See the complete API documentation in the :doc:`API Reference Index <api/index>`.

Integrations
~~~~~~~~~~~

- **Model Context Protocol (MCP)**: Connect agents to standardized tool providers using Anthropic's `Model Context Protocol <https://modelcontextprotocol.io/>`_

Architecture
-----------

The library follows these key architectural principles:

1. **Modular Base Classes**: Abstract base classes define common agent operations and Graph structures
2. **Externalized Configuration & Prompts**: Templates and parameters stored outside core code
3. **Developer Clarity**: Clear documentation of responsibilities and extension points
4. **Testability & Extensibility**: Separated components for easy testing and maintenance

For a comprehensive overview of the architecture, see the :doc:`Design Documentation <Design>`.

Integration Descriptions
-----------------------

Model Context Protocol (MCP)
~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

The Model Context Protocol (MCP) integration allows agents to connect with standardized tool providers following Anthropic's open protocol. This integration enables agents to access a wide ecosystem of tools without having to implement custom integrations for each one.

Key features:

- Connect to any MCP-compatible server
- Automatic tool discovery and execution
- Support for multiple MCP servers simultaneously
- Standardized interface for tool providers
- Custom tool provider implementation support

For detailed documentation, see:

- :doc:`Tool Provider API Documentation <Tool Provider API Documentation>`
- :doc:`MCP Tool Integration Tutorial <MCP Tool Integration Tutorial>`
- :doc:`Agent Tools Design <Agent_Tools_Design>`

Memory Systems
~~~~~~~~~~~~~

All agent patterns include comprehensive memory capabilities that allow agents to store and retrieve information across interactions. The memory system enables agents to maintain context, learn from past interactions, and provide personalized responses.

Key features:

- **Multiple Memory Types**: Semantic (facts), Episodic (experiences), and Procedural (patterns)
- **Flexible Persistence**: In-memory, file system, and vector store backends
- **Customizable Retrieval**: Query-based memory retrieval with filtering options
- **Seamless Integration**: Works across all agent patterns with consistent API

For detailed documentation, see:

- :doc:`Memory API Documentation <Memory API Documentation>`
- :doc:`Memory Integration Tutorial <Memory Integration Tutorial>`
- :doc:`Agent Memory Design <Agent Memory Design>`
- :doc:`Memory and MCP Integration <memory_and_mcp_integration>`

Creating New Patterns
--------------------

1. Subclass ``BaseAgent`` or ``MultiAgentBase``
2. Define ``build_graph()`` with your LangGraph nodes and transitions
3. Implement node functions for each step
4. Add prompts in ``prompts/<YourPatternClass>/``
5. Create example scripts and tests

For more guidance on next steps and development, see :doc:`Next Steps <Next Steps>`.

Contributing
-----------

We welcome contributions! To add a new pattern:

1. Review existing patterns in ``patterns/`` for consistency
2. Follow the architecture principles
3. Include comprehensive documentation
4. Add tests and example usage
5. Submit a PR with your changes

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`