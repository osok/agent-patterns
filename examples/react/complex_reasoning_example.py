"""
Advanced example demonstrating the ReActAgent for complex reasoning with multiple tools.

This example shows how to use the ReAct Agent to solve a multi-step reasoning problem
that requires coordination between multiple specialized tools.
"""

import os
import logging
import re
from pathlib import Path

from langchain_core.tools import Tool
from agent_patterns.patterns.re_act_agent import ReActAgent

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
        return "Please specify two concepts to compare in the format: 'Compare X and Y'"
    
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
            "The attention mechanism is a key component of transformer architecture. Transformers rely on self-attention mechanisms to weigh the importance of different words in a sequence, which allows them to handle long-range dependencies in text better than previous approaches."
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

def main():
    """Run the ReAct agent with multiple tools for complex reasoning."""
    
    # Setup LLM configs
    llm_configs = {
        "default": {
            "model_name": "gpt-4-turbo-preview",
            "provider": "openai",
            "temperature": 0.3  # Lower temperature for more focused reasoning
        }
    }
    
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
            description="Compare two AI concepts and explain their relationship. Input format: 'Compare X and Y'."
        )
    ]
    
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent
    prompt_dir = str(project_root / "src" / "agent_patterns" / "prompts")
    
    # Initialize the agent
    agent = ReActAgent(
        llm_configs=llm_configs,
        tools=tools,
        prompt_dir=prompt_dir,
        max_steps=10,  # Allow more steps for complex reasoning
        log_level=logging.INFO
    )
    
    # Complex reasoning task
    task = """
    I'm studying artificial intelligence and need help understanding the relationships between key concepts.
    
    First, find information about large language models and transformers.
    Then, extract the key AI concepts mentioned in that information.
    Finally, for the two most closely related concepts, explain their relationship and how they differ.
    
    Present your findings in a clear, structured way that would help a student understand the conceptual framework of modern AI.
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
                thought, action, observation = step
                print(f"Step {i+1}:")
                print(f"Thought: {thought}")
                print(f"Action: {action}")
                print(f"Observation: {observation[:150]}..." if len(str(observation)) > 150 else f"Observation: {observation}")
                print("-"*50)

if __name__ == "__main__":
    main()