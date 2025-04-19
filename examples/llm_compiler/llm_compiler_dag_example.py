"""Advanced example visualizing the LLM Compiler's task graph.

This example demonstrates the directed acyclic graph (DAG) of tasks created by
the LLM Compiler pattern and visualizes the dependencies between tasks.
"""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



import os
import sys
import logging
import time
from typing import Dict, Any, List
import json
from dotenv import load_dotenv
from langchain_core.tools import tool

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the LLMCompilerAgent
from agent_patterns.patterns import LLMCompilerAgent

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define tools for our complex workflow
@tool
def search_academic_papers(query: str) -> str:
    """Search for academic papers on a topic."""
    logger.info(f"Searching academic papers for: {query}")
    time.sleep(0.5)  # Simulate API call
    return f"Found 3 relevant papers on {query}: Paper1, Paper2, Paper3."

@tool
def extract_paper_details(paper_id: str) -> str:
    """Extract details from a specific academic paper."""
    logger.info(f"Extracting details from paper: {paper_id}")
    time.sleep(0.5)  # Simulate processing
    details = {
        "Paper1": {
            "title": "Advances in AI Planning",
            "authors": "Smith J, Johnson K",
            "year": 2023,
            "abstract": "This paper discusses recent advances in AI planning algorithms."
        },
        "Paper2": {
            "title": "Machine Learning for Decision Making",
            "authors": "Brown R, Davis M",
            "year": 2022,
            "abstract": "An overview of ML techniques for decision-making processes."
        },
        "Paper3": {
            "title": "Deep Learning Applications",
            "authors": "Wilson A, Thomas B",
            "year": 2021,
            "abstract": "A survey of deep learning applications in various domains."
        }
    }
    return json.dumps(details.get(paper_id, {"title": f"Unknown paper {paper_id}", "year": 2023}))

@tool
def analyze_sentiment(text: str) -> str:
    """Analyze the sentiment of a text passage."""
    logger.info(f"Analyzing sentiment of text")
    time.sleep(0.5)  # Simulate processing
    # Simple keyword-based sentiment (in real life, use a proper NLP model)
    positive_words = ["advances", "improved", "effective", "success", "beneficial"]
    negative_words = ["challenges", "difficult", "problems", "limitations", "issues"]
    
    positive_count = sum(1 for word in positive_words if word.lower() in text.lower())
    negative_count = sum(1 for word in negative_words if word.lower() in text.lower())
    
    if positive_count > negative_count:
        return "Positive sentiment (score: 0.8)"
    elif negative_count > positive_count:
        return "Negative sentiment (score: 0.3)"
    else:
        return "Neutral sentiment (score: 0.5)"

@tool
def compare_papers(papers_json: str) -> str:
    """Compare multiple papers and find commonalities and differences."""
    logger.info(f"Comparing papers")
    time.sleep(0.7)  # Simulate complex analysis
    try:
        papers = json.loads(papers_json)
        return f"Comparison of {len(papers)} papers: Found common themes in {', '.join(p.get('title', 'Unknown') for p in papers)}"
    except:
        return "Error comparing papers. Please provide valid JSON array of paper details."

@tool
def generate_summary(text: str) -> str:
    """Generate a concise summary of the provided text."""
    logger.info(f"Generating summary")
    time.sleep(0.5)  # Simulate processing
    # In a real implementation, use an actual summarization model
    return f"Summary: {text[:100]}..." if len(text) > 100 else text

def visualize_task_graph(task_graph: Dict[str, Any]) -> None:
    """Visualize the task graph as a simple text-based representation."""
    if not task_graph:
        print("No task graph to visualize.")
        return
    
    print("\n=== TASK GRAPH VISUALIZATION ===")
    
    # Get all node IDs
    node_ids = set(task_graph.keys())
    
    # Build an adjacency list from dependencies
    adjacency_list = {node_id: [] for node_id in node_ids}
    for node_id, node_data in task_graph.items():
        for dep_id in node_data.get("depends_on", []):
            if dep_id in adjacency_list:
                adjacency_list[dep_id].append(node_id)
    
    # Find root nodes (no dependencies)
    root_nodes = [node_id for node_id, node_data in task_graph.items() 
                  if not node_data.get("depends_on", [])]
    
    # Print a simple ASCII visualization of the graph
    print("\n┌─" + "─" * 50 + "┐")
    print("│ TASK DEPENDENCIES (arrows point from dependency to dependent) │")
    print("└─" + "─" * 50 + "┘")
    
    # Print node details
    for node_id, node_data in sorted(task_graph.items(), key=lambda x: int(x[0])):
        tool_name = node_data.get("tool", "unknown")
        dependencies = node_data.get("depends_on", [])
        inputs = node_data.get("inputs", {})
        
        print(f"\nTask {node_id}: [{tool_name}]")
        print(f"  Inputs: {inputs}")
        if dependencies:
            print(f"  Depends on: {', '.join(dependencies)}")
        else:
            print("  Depends on: None (root task)")
    
    # Visualize as a simple text DAG
    print("\n┌─" + "─" * 30 + "┐")
    print("│ GRAPH STRUCTURE (→ shows direction) │")
    print("└─" + "─" * 30 + "┘")
    
    # Helper function to print the graph
    def print_graph_from_roots(roots, level=0, visited=None):
        if visited is None:
            visited = set()
        
        for root in sorted(roots, key=int):
            if root in visited:
                continue
            
            visited.add(root)
            indent = "  " * level
            dependents = adjacency_list[root]
            
            if dependents:
                connector = "┬→ " if len(dependents) > 1 else "─→ "
                tool_name = task_graph[root]["tool"]
                print(f"{indent}{root}[{tool_name}] {connector}", end="")
                print_graph_from_roots(dependents, level+1, visited)
            else:
                tool_name = task_graph[root]["tool"]
                print(f"{indent}{root}[{tool_name}]")
    
    print_graph_from_roots(root_nodes)

def main():
    """Run the LLM Compiler agent with a complex task and visualize the result."""
    # Configure LLMs for different roles
    llm_configs = {
        'planner': {
            'provider': 'openai',
            'model': 'gpt-3.5-turbo',
            'temperature': 0.2
        },
        'executor': {
            'provider': 'openai',
            'model': 'gpt-3.5-turbo',
            'temperature': 0.1
        },
        'joiner': {
            'provider': 'openai',
            'model': 'gpt-3.5-turbo',
            'temperature': 0.2
        }
    }
    
    # Create a list of tools
    tools = [search_academic_papers, extract_paper_details, analyze_sentiment, 
             compare_papers, generate_summary]
    
    # Initialize the LLM Compiler agent
    agent = LLMCompilerAgent(
        llm_configs=llm_configs,
        tools=tools,
        prompt_dir="/ai/work/agents/agent-patterns/src/agent_patterns/prompts",
        log_level=logging.INFO
    )
    
    # Complex query that requires task dependencies
    query = """
    I need a research summary. Please:
    1. Search for academic papers on "AI planning"
    2. Extract details from the found papers
    3. Analyze the sentiment of each paper's abstract
    4. Compare the papers to find common themes
    5. Generate a summary of your findings
    """
    
    # Run the agent
    logger.info(f"Running LLM Compiler agent with complex query")
    start_time = time.time()
    result = agent.run(query.strip())
    end_time = time.time()
    
    # Display the result
    print("\n=== EXECUTION RESULTS ===")
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    print(f"Tasks planned: {result['metadata']['tasks_planned']}")
    print(f"Tasks completed: {result['metadata']['tasks_completed']}")
    
    print("\n=== FINAL ANSWER ===")
    print(result['output'])
    
    # Visualize the task graph
    visualize_task_graph(result.get("metadata", {}).get("task_graph", {}))

if __name__ == "__main__":
    main() 