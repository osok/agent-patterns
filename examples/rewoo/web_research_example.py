"""
Web Research Example using the REWOO agent pattern.

This example demonstrates how to use the REWOO (Reasoning Without Observation) agent pattern
for conducting structured web research on a topic.
"""

import os
import sys
import logging
import time
from typing import Dict, Any, List
import json

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agent_patterns.patterns.rewoo_agent import REWOOAgent
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSearchTool:
    """Web search tool that returns mock results for different tech topics."""
    
    def __init__(self):
        self.search_results = {
            "quantum computing": """
Quantum computing is an emerging technology that uses quantum mechanics to solve problems 
too complex for classical computers. Key concepts include:

1. Qubits: Unlike classical bits (0 or 1), qubits can exist in multiple states simultaneously (superposition).
2. Quantum entanglement: Qubits can be interdependent, even at a distance.
3. Quantum gates: These are the building blocks of quantum circuits.

Current leaders in quantum computing include IBM, Google, Microsoft, and D-Wave.
IBM's quantum computers are available through their cloud service.
Google claimed "quantum supremacy" in 2019 when their 53-qubit Sycamore processor performed a specific task faster than the world's most powerful supercomputer.

Challenges include quantum decoherence, error correction, and scaling up systems.
            """,
            "quantum algorithms": """
Notable quantum algorithms include:

1. Shor's algorithm: Can factor large numbers exponentially faster than classical algorithms, threatening current encryption.
2. Grover's algorithm: Provides quadratic speedup for unstructured search problems.
3. Quantum Fourier Transform: The foundation for many quantum algorithms.
4. Quantum simulation algorithms: Can model quantum systems efficiently.
5. QAOA (Quantum Approximate Optimization Algorithm): Tackles combinatorial optimization problems.
6. VQE (Variational Quantum Eigensolver): Used for quantum chemistry calculations.

These algorithms demonstrate quantum advantage in specific domains but require fault-tolerant quantum computers for practical implementation at scale.
            """,
            "quantum hardware": """
Current quantum hardware approaches include:

1. Superconducting qubits: Used by IBM, Google. Operates at extremely cold temperatures (near absolute zero).
2. Trapped ions: Used by IonQ, Honeywell. Known for high fidelity but slower operation.
3. Photonic quantum computers: Use light particles, can operate at room temperature.
4. Topological qubits: Microsoft's approach, aiming for more stable qubits.
5. Neutral atoms: Arranged in arrays using optical tweezers.

Most current systems have between 50-100 qubits with limited coherence times.
Error rates are still high, requiring error correction techniques.
Quantum volume and other benchmarks are used to compare different systems beyond just qubit count.
            """,
            "quantum applications": """
Promising quantum computing applications include:

1. Cryptography: Breaking current encryption (threat) and creating quantum-secure encryption (opportunity).
2. Drug discovery: Simulating molecular interactions accurately could revolutionize pharmaceutical research.
3. Materials science: Designing new materials with specific properties.
4. Financial modeling: Portfolio optimization and risk analysis.
5. AI and machine learning: Potentially faster training for specific algorithms.
6. Supply chain optimization: Solving complex logistics problems.
7. Weather forecasting: More accurate long-term predictions through better modeling.

Most applications are still theoretical or in early research stages, with practical advantage expected in 5-10 years.
            """,
            "quantum programming": """
Quantum programming languages and frameworks include:

1. Qiskit: IBM's open-source SDK for quantum computing.
2. Cirq: Google's framework for quantum algorithms.
3. Q#: Microsoft's quantum programming language.
4. Pennylane: Quantum machine learning library.
5. PyQuil: Rigetti's Python library for quantum programming.
6. Quipper: Functional programming language for quantum computing.
7. OpenQASM: Open Quantum Assembly Language for low-level programming.

These tools provide different abstractions for building quantum circuits, running simulations, and interfacing with quantum hardware.
Programming paradigms differ significantly from classical computing, requiring new approaches.
            """
        }
        
    def __call__(self, query: str, **kwargs) -> str:
        """Search for information based on query."""
        # Log the search
        logger.info(f"Searching for: {query}")
        
        # Find the best match in our mock database
        best_match = None
        best_score = 0
        
        for key, value in self.search_results.items():
            # Simple keyword matching (in a real implementation, use proper search)
            if key in query.lower():
                score = len(key)
                if score > best_score:
                    best_score = score
                    best_match = value
        
        # Return either the best match or a default response
        if best_match:
            return best_match
        
        return """
Quantum computing is an emerging field that uses quantum mechanical phenomena to perform 
computations. Unlike classical computers that use bits (0 or 1), quantum computers use
quantum bits or qubits that can exist in multiple states simultaneously, allowing them
to potentially solve certain problems much faster than classical computers.
        """


class InformationExtractorTool:
    """Tool that extracts structured information from text."""
    
    def __call__(self, text: str, format_type: str = "json", **kwargs) -> str:
        """Extract structured information from text."""
        logger.info(f"Extracting information in {format_type} format")
        
        # Mock implementation that returns a structured version of the input
        if "quantum computing" in text.lower():
            if format_type.lower() == "json":
                result = {
                    "technology": "Quantum Computing",
                    "key_concepts": [
                        "Qubits",
                        "Superposition",
                        "Entanglement",
                        "Quantum Gates"
                    ],
                    "major_companies": [
                        "IBM",
                        "Google",
                        "Microsoft",
                        "D-Wave"
                    ],
                    "challenges": [
                        "Decoherence",
                        "Error correction",
                        "Scaling"
                    ],
                    "current_state": "Early research phase with 50-100 qubit systems"
                }
                return json.dumps(result, indent=2)
            else:
                return """
TECHNOLOGY: Quantum Computing
KEY CONCEPTS:
- Qubits
- Superposition
- Entanglement
- Quantum Gates
MAJOR COMPANIES: IBM, Google, Microsoft, D-Wave
CHALLENGES:
- Decoherence
- Error correction
- Scaling
CURRENT STATE: Early research phase with 50-100 qubit systems
                """
        
        # Generic response for other inputs
        return "No structured information could be extracted."


class BibtexGeneratorTool:
    """Tool that generates bibliographic references in BibTeX format."""
    
    def __call__(self, topic: str, **kwargs) -> str:
        """Generate mock BibTeX references for a topic."""
        logger.info(f"Generating BibTeX references for: {topic}")
        
        if "quantum" in topic.lower():
            return """
@article{preskill2018quantum,
  title={Quantum Computing in the NISQ era and beyond},
  author={Preskill, John},
  journal={Quantum},
  volume={2},
  pages={79},
  year={2018},
  publisher={Verein zur F{\"o}rderung des Open Access Publizierens in den Quantenwissenschaften}
}

@article{arute2019quantum,
  title={Quantum supremacy using a programmable superconducting processor},
  author={Arute, Frank and Arya, Kunal and Babbush, Ryan and Bacon, Dave and Bardin, Joseph C and Barends, Rami and Biswas, Rupak and Boixo, Sergio and Brandao, Fernando GSL and Buell, David A and others},
  journal={Nature},
  volume={574},
  number={7779},
  pages={505--510},
  year={2019},
  publisher={Nature Publishing Group}
}

@book{nielsen2010quantum,
  title={Quantum computation and quantum information},
  author={Nielsen, Michael A and Chuang, Isaac L},
  year={2010},
  publisher={Cambridge university press}
}
            """
        
        return "No BibTeX references found for this topic."


def main():
    """Run the example."""
    # Get API key from environment
    api_key = None  # Always use mock mode for testing
    
    if not api_key:
        logger.warning("OPENAI_API_KEY not set. Using mock mode.")
        # Create mock implementation
        from unittest.mock import MagicMock
        
        # Create a mock LLM that gives pre-scripted responses
        mock_responses = {
            "planning": """
Step 1: Research quantum computing fundamentals
Use the search tool to find general information about quantum computing.

Step 2: Research quantum algorithms
Use the search tool to find information about quantum algorithms and their applications.

Step 3: Research quantum hardware
Use the search tool to gather information about different quantum hardware approaches.

Step 4: Research practical applications
Use the search tool to find information about real-world applications of quantum computing.

Step 5: Research quantum programming
Use the search tool to learn about quantum programming languages and frameworks.

Step 6: Extract structured information
Use the information extractor tool to organize the key findings.

Step 7: Generate bibliographic references
Use the BibTeX generator to create academic references for the research.

Step 8: Synthesize the information
Combine all the gathered information into a comprehensive research report.
            """,
            "execution1": """
I'll search for fundamental information about quantum computing.

TOOL: search
query: quantum computing
            """,
            "execution2": """
Now I'll search for information about quantum algorithms.

TOOL: search
query: quantum algorithms
            """,
            "execution3": """
Let's research quantum hardware technologies.

TOOL: search
query: quantum hardware
            """,
            "execution4": """
Now I'll look for practical applications of quantum computing.

TOOL: search
query: quantum applications
            """,
            "execution5": """
Let's find information about quantum programming languages and tools.

TOOL: search
query: quantum programming
            """,
            "execution6": """
Now I'll extract structured information from our research.

TOOL: information_extractor
text: Quantum computing uses qubits instead of classical bits. Major companies include IBM, Google, Microsoft, and D-Wave. Current systems have 50-100 qubits. Applications include cryptography, drug discovery, and financial modeling.
format_type: json
            """,
            "execution7": """
Let's generate bibliographic references for our research.

TOOL: bibtex_generator
topic: quantum computing research
            """,
            "final": """
# Quantum Computing: A Comprehensive Research Report

## Introduction
Quantum computing represents a paradigm shift in computational technology, utilizing quantum mechanical phenomena to process information in ways that classical computers cannot. This report synthesizes current knowledge on quantum computing fundamentals, algorithms, hardware, applications, and programming frameworks.

## Fundamentals
Quantum computing is built on several key principles:
- **Qubits**: Unlike classical bits, quantum bits can exist in multiple states simultaneously through superposition
- **Entanglement**: Quantum particles can become correlated, linking their measurement outcomes regardless of distance
- **Quantum Gates**: Operations that manipulate qubits, analogous to classical logic gates but following quantum mechanics

## Quantum Algorithms
Several algorithms demonstrate quantum advantage:
- **Shor's Algorithm**: Factors large numbers exponentially faster than classical methods, threatening current encryption systems
- **Grover's Algorithm**: Provides quadratic speedup for searching unsorted databases
- **Quantum Fourier Transform**: Forms the foundation for many quantum algorithms
- **QAOA and VQE**: Addresses optimization and chemistry problems respectively

## Hardware Approaches
Current quantum computing hardware includes:
- **Superconducting Qubits**: Used by IBM and Google, requires extremely low temperatures
- **Trapped Ions**: Employed by IonQ and Honeywell, offers high fidelity but slower operations
- **Photonic Systems**: Leverages light particles, can potentially operate at room temperature
- **Topological Qubits**: Microsoft's approach, aiming for more stable qubits through exotic physics
- **Neutral Atoms**: Arranged in arrays using optical tweezers

## Applications
Promising applications include:
1. Cryptography (both breaking and creating secure systems)
2. Drug discovery and molecular simulation
3. Materials science
4. Financial modeling and optimization
5. Machine learning enhancements
6. Supply chain optimization
7. Weather and climate modeling

## Programming Frameworks
Developers can access quantum computing through:
- **Qiskit**: IBM's comprehensive open-source SDK
- **Cirq**: Google's framework for quantum algorithms
- **Q#**: Microsoft's quantum programming language
- **PennyLane**: Specialized for quantum machine learning
- **PyQuil, OpenQASM**: Additional tools for quantum development

## Current State of the Field
Quantum computing remains in the NISQ (Noisy Intermediate-Scale Quantum) era, with systems of 50-100 qubits that suffer from noise and limited coherence times. Practical quantum advantage for real-world problems is generally projected to be 5-10 years away, with error correction and scaling representing the primary challenges.

## References
The field is supported by seminal works including Nielsen & Chuang's "Quantum Computation and Quantum Information," Preskill's "Quantum Computing in the NISQ era and beyond," and breakthrough demonstrations like Google's 2019 quantum supremacy experiment.

## Conclusion
Quantum computing represents a frontier technology with transformative potential across multiple industries. While practical, widespread application remains years away, rapid progress in hardware, algorithms, and error correction suggests a future where quantum and classical computing will work in tandem to solve humanity's most challenging computational problems.
            """
        }
        
        class MockLLM:
            def __init__(self, responses):
                self.responses = responses
                self.call_count = 0
                
            def invoke(self, messages):
                self.call_count += 1
                message_str = str(messages)
                
                if "planning" in message_str.lower() or "plan" in message_str.lower():
                    return mock_responses["planning"]
                elif "step" in message_str.lower() and "execution" in message_str.lower():
                    # Return different responses based on the step number
                    step_mention = message_str.lower().find("step")
                    if step_mention >= 0:
                        for i in range(1, 8):
                            if f"step {i}" in message_str.lower():
                                return mock_responses.get(f"execution{i}", mock_responses["execution1"])
                    
                    # Default execution response if step number not found
                    return mock_responses["execution1"]
                elif "final" in message_str.lower() or "synthesize" in message_str.lower():
                    return mock_responses["final"]
                    
                return "Default response based on: " + str(messages)
        
        # Create mock LLMs
        planner_llm = MockLLM(mock_responses)
        solver_llm = MockLLM(mock_responses)
    else:
        # Create real OpenAI LLMs
        planner_llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            api_key=api_key
        )
        
        solver_llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.2,
            api_key=api_key
        )
    
    # Create tools
    search_tool = WebSearchTool()
    extractor_tool = InformationExtractorTool()
    bibtex_tool = BibtexGeneratorTool()
    
    # Create REWOO agent
    agent = REWOOAgent(
        llm_configs={
            "planner": planner_llm,
            "solver": solver_llm
        },
        tool_registry={
            "search": search_tool,
            "information_extractor": extractor_tool,
            "bibtex_generator": bibtex_tool
        },
        prompt_dir="src/agent_patterns/prompts/REWOOAgent"
    )
    
    # Run the agent
    query = "Conduct a comprehensive research report on quantum computing, including fundamentals, algorithms, hardware, applications, and programming frameworks."
    print(f"\nQuery: {query}\n")
    print("-" * 80)
    print("Starting REWOO agent execution...\n")
    
    start_time = time.time()
    result = agent.run(query)
    elapsed_time = time.time() - start_time
    
    print("\nResult:")
    print("-" * 80)
    print(result)
    print("-" * 80)
    print(f"Execution completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    main() 