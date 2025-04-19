"""
Advanced example demonstrating the ReActAgent for complex reasoning with multiple tools.

This example shows how to use the ReAct Agent to solve a multi-step reasoning problem
that requires coordination between multiple specialized tools.
"""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



import os
import logging
import re
import json
import sys
from pathlib import Path
from typing import Union, Dict, Any, List, Tuple, Optional
from dotenv import load_dotenv

from langchain_core.tools import Tool
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import AIMessage
from agent_patterns.patterns.re_act_agent import ReActAgent

# Add the parent directory to sys.path to import from examples.utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from examples.utils.model_config import get_llm_configs

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tool implementations
def search_encyclopedia(query):
    """Simulated encyclopedia search tool."""
    encyclopedia = {
        "artificial intelligence": "Artificial intelligence (AI) is intelligence demonstrated by machines, "
                                  "as opposed to intelligence displayed by humans or animals. Major AI "
                                  "applications include advanced web search engines, recommendation systems, "
                                  "content production, and self-driving cars.",
        "machine learning": "Machine learning (ML) is a field of inquiry devoted to understanding and "
                           "building methods that 'learn', that is, methods that leverage data to improve "
                           "performance on some set of tasks. It is seen as a part of artificial intelligence.",
        "neural network": "Artificial neural networks (ANNs) are computing systems vaguely inspired by the "
                         "biological neural networks that constitute animal brains. An ANN is based on a "
                         "collection of connected units or nodes called artificial neurons.",
        "deep learning": "Deep learning is part of a broader family of machine learning methods based "
                        "on artificial neural networks with representation learning. Learning can be "
                        "supervised, semi-supervised or unsupervised.",
        "reinforcement learning": "Reinforcement learning (RL) is an area of machine learning concerned with "
                                 "how intelligent agents ought to take actions in an environment in order to "
                                 "maximize the notion of cumulative reward.",
        "large language model": "A large language model (LLM) is a language model consisting of a neural "
                               "network with many parameters, trained on large quantities of text. LLMs "
                               "emerged around 2018 and perform well at a wide variety of tasks.",
        "transformer": "A transformer is a deep learning model that adopts the mechanism of self-attention, "
                      "differentially weighting the significance of each part of the input data. It is used "
                      "primarily in natural language processing and computer vision.",
        "attention mechanism": "The attention mechanism is a part of a neural network architecture that "
                             "allows the model to focus on specific parts of the input sequence when "
                             "producing an output. It's a key component of transformer models."
    }
    
    # Simple keyword-based search
    results = []
    for key, value in encyclopedia.items():
        if query.lower() in key.lower() or any(word in value.lower() for word in query.lower().split()):
            results.append(f"{key.title()}: {value}")
    
    if results:
        return "\n\n".join(results)
    else:
        return "No information found on that topic."

def extract_concepts(text):
    """Extract key AI concepts from a text."""
    concepts = [
        "artificial intelligence", "machine learning", "neural network", "deep learning",
        "reinforcement learning", "large language model", "transformer", "attention mechanism"
    ]
    
    found_concepts = []
    for concept in concepts:
        if re.search(r'\b' + re.escape(concept) + r'\b', text.lower()):
            found_concepts.append(concept)
    
    if found_concepts:
        return f"Key concepts identified: {', '.join(found_concepts)}"
    else:
        return "No key AI concepts identified in the text."

def compare_concepts(concepts_str):
    """Compare two AI concepts and explain their relationship."""
    # Extract concepts from string like "Compare X and Y"
    concepts = re.findall(r'compare\s+([a-z\s]+)\s+and\s+([a-z\s]+)', concepts_str.lower())
    
    if not concepts:
        # For flexibility, try to extract any two concepts from the input
        all_concepts = [
            "artificial intelligence", "machine learning", "neural network", "deep learning",
            "reinforcement learning", "large language model", "transformer", "attention mechanism"
        ]
        found_concepts = []
        for concept in all_concepts:
            if concept in concepts_str.lower():
                found_concepts.append(concept)
        
        if len(found_concepts) >= 2:
            concept1, concept2 = found_concepts[0], found_concepts[1]
        else:
            return "Please specify two concepts to compare in the format: 'Compare X and Y'"
    else:
        concept1, concept2 = concepts[0]
        concept1 = concept1.strip()
        concept2 = concept2.strip()
    
    # Predefined relationships
    relationships = {
        ("artificial intelligence", "machine learning"): 
            "Machine learning is a subset of artificial intelligence. AI is the broader concept of machines being able to carry out tasks in a way that we would consider 'smart', while ML is a current application of AI based on the idea that we should be able to give machines access to data and let them learn for themselves.",
        
        ("machine learning", "neural network"): 
            "Neural networks are a type of machine learning algorithm. Machine learning encompasses many algorithms and approaches to let computers learn from data, while neural networks specifically are inspired by the human brain's structure and function.",
        
        ("neural network", "deep learning"): 
            "Deep learning is a subset of neural networks with multiple layers (deep neural networks). Neural networks can be shallow (few layers) or deep, while deep learning specifically refers to neural networks with many layers that can learn more complex patterns.",
        
        ("machine learning", "reinforcement learning"): 
            "Reinforcement learning is a type of machine learning where an agent learns to make decisions by taking actions in an environment to maximize some notion of cumulative reward. It differs from supervised learning (another ML approach) which learns from labeled examples.",
        
        ("deep learning", "large language model"): 
            "Large language models are typically implemented using deep learning techniques. Deep learning provides the architectural foundation (like transformers) that makes LLMs possible.",
        
        ("transformer", "attention mechanism"): 
            "The attention mechanism is a key component of transformer architecture. Transformers rely on self-attention mechanisms to weigh the importance of different words in a sequence, which allows them to handle long-range dependencies in text better than previous approaches.",
        
        ("large language model", "transformer"):
            "Large language models are typically built using transformer architectures. Transformers provide the mechanism (through self-attention) that allows LLMs to process and generate human-like text at scale.",
    }
    
    # Check for direct relationship
    if (concept1, concept2) in relationships:
        return relationships[(concept1, concept2)]
    # Check for reverse relationship
    elif (concept2, concept1) in relationships:
        return relationships[(concept2, concept1)]
    else:
        # Fallback if relationship not predefined
        return (f"These concepts are both related to artificial intelligence, but a detailed "
                f"comparison between {concept1} and {concept2} is not available.")

# Custom action parser for more flexible LLM responses
def custom_llm_parser(response: AIMessage) -> Union[AgentAction, AgentFinish]:
    """Custom parser to handle more flexible LLM response formats."""
    text = response.content
    logger.debug("Parsing LLM response: %s", text[:100] + "..." if len(text) > 100 else text)

    # Check for Final Answer pattern
    final_answer_match = re.search(r"(?:Final Answer:|I'll provide my final answer:)(.*)", text, re.DOTALL | re.IGNORECASE)
    if final_answer_match:
        final_answer = final_answer_match.group(1).strip()
        logger.info("LLM provided Final Answer: %s", final_answer)
        return AgentFinish({"output": final_answer}, log=text)
    
    # Check standard format: Action: tool_name(tool_input)
    action_match = re.search(r"Action:\s*(.*?)(?:\n|$)", text, re.DOTALL | re.IGNORECASE)
    if action_match:
        action_text = action_match.group(1).strip()
        tool_match = re.match(r"(\w+)\s*\((.*)\)", action_text)
        if tool_match:
            tool_name = tool_match.group(1)
            tool_input = tool_match.group(2).strip()
            if tool_input.startswith('"') and tool_input.endswith('"'):
                tool_input = tool_input[1:-1]
            return AgentAction(tool=tool_name, tool_input=tool_input, log=text)
    
    # If we can't parse the response, return a generic message
    return AgentFinish({"output": "I couldn't determine a specific action to take. Please provide more guidance on what specific information you're looking for."}, log=text)

class EnhancedReActAgent(ReActAgent):
    """Enhanced ReAct agent with custom parsing."""
    
    # Use the same prompt directory as ReActAgent
    _AGENT_TYPE = "ReActAgent"
    
    def _parse_llm_react_response(self, response: AIMessage) -> Union[AgentAction, AgentFinish]:
        """Override default parser with custom implementation."""
        # Print the raw response content to help with debugging
        print(f"\nRAW LLM RESPONSE:\n{response.content}\n")
        return custom_llm_parser(response)
        
    def _load_prompt_template(self, name: str) -> Any:
        """Override to use ReActAgent prompt path instead of EnhancedReActAgent."""
        from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
        
        # Use ReActAgent instead of self.__class__.__name__
        class_name = "ReActAgent"
        
        # Try to load from files
        if self.prompt_dir:
            # Construct paths to system and user prompt files
            class_prompt_dir = os.path.join(self.prompt_dir, class_name, name)
            system_path = os.path.join(class_prompt_dir, "system.md")
            user_path = os.path.join(class_prompt_dir, "user.md")
            
            # Check if both files exist
            if os.path.exists(system_path) and os.path.exists(user_path):
                # Load system prompt
                with open(system_path, "r") as f:
                    system_content = f.read()
                
                # Load user prompt
                with open(user_path, "r") as f:
                    user_content = f.read()
                
                # Create template from loaded content
                return ChatPromptTemplate.from_messages([
                    SystemMessagePromptTemplate.from_template(system_content),
                    HumanMessagePromptTemplate.from_template(user_content)
                ])
        
        # If files don't exist, raise an error
        raise FileNotFoundError(
            f"Prompt template '{name}' not found for ReActAgent. "
            f"Expected files at {self.prompt_dir}/ReActAgent/{name}/system.md and "
            f"{self.prompt_dir}/ReActAgent/{name}/user.md"
        )

def main():
    """Run the ReAct agent with multiple tools for complex reasoning."""
    
    # Load environment variables
    load_dotenv()
    
    # Setup LLM configs using the utility function
    try:
        # This will use PLANNING_MODEL_PROVIDER and PLANNING_MODEL_NAME from .env
        llm_configs = get_llm_configs()
    except ValueError as e:
        logger.error(f"Error loading model configuration: {e}")
        logger.error("Please ensure your .env file contains the necessary model configuration variables.")
        return
    
    # Define specialized tools
    tools = [
        Tool(
            name="search_encyclopedia",
            func=search_encyclopedia,
            description="Search for information about AI concepts in an encyclopedia. Input should be the concept or topic to search for."
        ),
        Tool(
            name="extract_concepts",
            func=extract_concepts,
            description="Extract key AI concepts mentioned in a text. Input should be the text to analyze."
        ),
        Tool(
            name="compare_concepts",
            func=compare_concepts,
            description="Compare two AI concepts and explain their relationship. Input should specify the two concepts to compare, e.g., 'Compare large language model and transformer'"
        )
    ]
    
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent

    # Try to find prompts directory - check both installed package and development paths
    src_prompt_dir = project_root / "src" / "agent_patterns" / "prompts"
    pkg_prompt_dir = project_root / "agent_patterns" / "prompts"

    if src_prompt_dir.exists():
        prompt_dir = str(src_prompt_dir)
    else:
        prompt_dir = str(pkg_prompt_dir)
    
    # Initialize the agent with our custom enhanced class
    agent = EnhancedReActAgent(
        llm_configs=llm_configs,
        tools=tools,
        prompt_dir=prompt_dir,
        max_steps=10,  # Allow more steps for complex reasoning
        log_level=logging.INFO
    )
    
    # Complex reasoning task with more explicit format guidance
    task = """
    I'm studying artificial intelligence and need help understanding the relationships between key concepts.
    
    IMPORTANT: You have access to exactly these three tools:
    1. search_encyclopedia - Search for information in an encyclopedia
    2. extract_concepts - Extract key AI concepts from text
    3. compare_concepts - Compare two AI concepts and explain their relationship
    
    Please follow these steps exactly:
    1. First, use the search_encyclopedia tool to search for information about "large language model transformer"
    2. Then, use the extract_concepts tool on the search results to identify key AI concepts
    3. Finally, use the compare_concepts tool to compare the two most closely related concepts (likely "large language model" and "transformer")
    
    Finish with a clear, structured explanation of how these concepts relate in modern AI.
    
    Remember to follow the proper format for each step:
    Thought: your reasoning
    Action: tool_name(tool_input)
    """
    
    logger.info("Running ReAct agent with complex reasoning task")
    
    # Run the agent
    result = agent.run(task)
    
    # Display the result
    if "error" in result:
        logger.error(f"Agent execution failed: {result['error']}")
    else:
        logger.info("Complex reasoning completed successfully")
        print("\n" + "="*80)
        print("COMPLEX REASONING TASK:")
        print(task)
        print("\n" + "="*80)
        print("REASONING RESULT:")
        print(result["output"])
        print("\n" + "="*80)
        
        if "intermediate_steps" in result:
            print("\nREASONING TRACE:")
            print("-"*50)
            for i, step in enumerate(result["intermediate_steps"]):
                print(f"Step {i+1}:")
                # Handle different step formats
                if len(step) >= 3:
                    thought, action, observation = step
                    print(f"Thought: {thought}")
                    print(f"Action: {action}")
                    print(f"Observation: {observation[:150]}..." if len(str(observation)) > 150 else f"Observation: {observation}")
                elif len(step) == 2:
                    action, observation = step
                    print(f"Action: {action}")
                    print(f"Observation: {observation[:150]}..." if len(str(observation)) > 150 else f"Observation: {observation}")
                else:
                    print(f"Step data: {step}")
                print("-"*50)

def fixed_example():
    """Run a fixed version of the example that doesn't rely on the agent framework."""
    print("\n" + "="*80)
    print("FIXED COMPLEX REASONING EXAMPLE")
    print("="*80)
    
    # Step 1: Search the encyclopedia
    print("\nStep 1: Searching encyclopedia for 'large language model transformer'")
    search_results = search_encyclopedia("large language model transformer")
    print(f"Search results:\n{search_results}\n")
    
    # Step 2: Extract concepts from search results
    print("\nStep 2: Extracting concepts from search results")
    concepts = extract_concepts(search_results)
    print(f"Extracted concepts:\n{concepts}\n")
    
    # Step 3: Compare the two most relevant concepts
    print("\nStep 3: Comparing 'large language model' and 'transformer'")
    comparison = compare_concepts("Compare large language model and transformer")
    print(f"Comparison:\n{comparison}\n")
    
    # Step 4: Final answer synthesis
    print("\nStep 4: Final synthesis")
    print("""
RELATIONSHIP BETWEEN LARGE LANGUAGE MODELS AND TRANSFORMERS IN MODERN AI:

Large Language Models (LLMs) and Transformers are two closely related concepts in modern artificial intelligence, with Transformers providing the architectural foundation for LLMs.

Transformers:
- Are a specific neural network architecture introduced in 2017
- Use self-attention mechanisms to efficiently process sequences of data
- Allow models to focus on relevant parts of input regardless of position
- Enabled breakthrough capabilities in natural language processing

Large Language Models:
- Are AI systems trained on vast amounts of text data
- Use transformer architectures as their underlying structure
- Scaled up transformer designs to billions of parameters
- Examples include GPT series, Claude, and BERT-based models

The relationship is that transformers made LLMs possible through their efficient handling of sequential data and attention mechanisms. Without the transformer architecture, today's powerful language models could not exist at their current scale and capability. The transformer architecture solved key limitations of previous approaches and enabled the massive scaling that defines modern LLMs.
""")
    
if __name__ == "__main__":
    # Run both the agent-based and fixed examples
    print("\n" + "="*80)
    print("AGENT-BASED COMPLEX REASONING EXAMPLE")
    print("="*80)
    main()
    
    print("\n" + "="*80)
    print("FIXED COMPLEX REASONING EXAMPLE")
    print("="*80)
    fixed_example()