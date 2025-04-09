"""
Agent Patterns Library

A collection of reusable AI agent patterns implemented using LangGraph and LangChain.
"""

from .core.base_agent import BaseAgent
from .patterns.re_act_agent import ReActAgent
from .patterns.plan_and_solve_agent import PlanAndSolveAgent
from .patterns.reflection_agent import ReflectionAgent
from .patterns.reflexion_agent import ReflexionAgent
from .patterns.llm_compiler_agent import LLMCompilerAgent
from .patterns.rewoo_agent import REWOOAgent
from .patterns.lats_agent import LATSAgent
from .patterns.self_discovery_agent import SelfDiscoveryAgent
from .patterns.storm_agent import STORMAgent

# Import memory classes
from .core.memory import (
    BaseMemory, 
    MemoryPersistence,
    SemanticMemory,
    EpisodicMemory,
    ProceduralMemory,
    CompositeMemory
)

# Import persistence backends
from .core.memory.persistence import (
    InMemoryPersistence,
    FileSystemPersistence, 
    VectorStorePersistence
)

__version__ = "0.1.0"