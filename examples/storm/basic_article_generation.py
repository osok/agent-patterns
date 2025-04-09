"""
STORM (Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking) Example

This example demonstrates how to use the STORM agent to generate a well-researched
article on a given topic using multi-perspective research.
"""

import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain.tools import Tool

# Import STORM agent
from agent_patterns.patterns.storm_agent import STORMAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def create_search_tool() -> Tool:
    """Create a simple web search tool using DuckDuckGo."""
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        return DuckDuckGoSearchRun()
    except ImportError:
        # Fallback to a mock search tool if DuckDuckGo is not available
        logger.warning("DuckDuckGo search tool not available. Using mock search tool.")
        def mock_search(query: str) -> str:
            return f"Mock search results for: {query}\n- Result 1: Information about {query}\n- Result 2: More details about {query}"
        
        return Tool(
            name="MockSearch",
            func=mock_search,
            description="Search the web for information on a given query"
        )

def main():
    # Check if the required environment variables are set
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable not set. Please set it in your .env file.")
        return

    # Create LLM configurations for different roles in the STORM agent
    llm_configs = {}
    
    # Use GPT-4 for roles that need high reasoning capabilities
    high_reasoning_roles = ["outline_generator", "perspective_identifier", "expert", "editor"]
    for role in high_reasoning_roles:
        llm_configs[role] = {
            "provider": "openai",
            "model": "gpt-4o",
            "temperature": 0.5
        }
    
    # Use GPT-3.5 for roles that need more standard capabilities
    standard_roles = ["researcher", "writer"]
    for role in standard_roles:
        llm_configs[role] = {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7
        }
    
    # Create the search tool
    search_tool = create_search_tool()
    
    # Create the STORM agent
    agent = STORMAgent(
        llm_configs=llm_configs,
        search_tool=search_tool,
        num_perspectives=3,
        max_conversation_turns=3,
        prompt_dir="src/agent_patterns/prompts"
    )
    
    # Define the topic to research
    topic = "The impact of generative AI on creative industries"
    
    # Run the STORM agent to generate an article
    logger.info(f"Generating article on topic: {topic}")
    result = agent.run(topic)
    
    # Print the article outline
    print("\n=== Article Outline ===")
    for section in result["outline"]:
        print(f"• {section['title']}")
        for subsection in section.get("subsections", []):
            print(f"  - {subsection['title']}")
    
    # Print perspectives
    print("\n=== Research Perspectives ===")
    for perspective in result["perspectives"]:
        print(f"• {perspective}")
    
    # Print the article
    print("\n=== Generated Article ===\n")
    print(result["article"])
    
    # Save the article to a file
    with open("storm_article.md", "w") as f:
        f.write(result["article"])
    
    logger.info("Article saved to storm_article.md")

if __name__ == "__main__":
    main() 