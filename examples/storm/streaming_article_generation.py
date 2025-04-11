"""
STORM (Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking) Example
with Streaming API

This example demonstrates how to use the STORM agent's streaming capabilities to get
real-time updates as the agent progresses through different stages of article generation.
"""

import os
import time
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

def display_step_progress(step_name: str) -> None:
    """Display step transition with a visual indicator."""
    print(f"\n{'=' * 50}")
    print(f"Starting: {step_name}")
    print(f"{'=' * 50}\n")

def main():
    # Check if the required environment variables are set
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable not set. Please set it in your .env file.")
        return

    # Create LLM configurations for different roles in the STORM agent
    llm_configs = {}
    
    # For demonstration purposes, use a simpler model configuration
    # In production, you might want different models for different roles
    for role in ["outline_generator", "perspective_identifier", "expert", "researcher", "writer", "editor"]:
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
        num_perspectives=2,  # Use fewer perspectives for faster demonstration
        max_conversation_turns=2,  # Use fewer turns for faster demonstration
        prompt_dir="agent_patterns/prompts"
    )
    
    # Define the topic to research
    topic = "The future of remote work"
    
    # Use the streaming API to get real-time updates
    print(f"\nGenerating article on topic: {topic}")
    print("Streaming progress in real-time...")
    
    # Track the current step to show transitions
    current_step = None
    
    # Use a simple placeholder to track the outline
    outline = []
    
    # Collect the final article content
    final_article = None
    
    # Stream the STORM agent execution
    for state in agent.stream(topic):
        # Show step transitions
        if current_step != state["current_step"]:
            current_step = state["current_step"]
            display_step_progress(current_step)
        
        # For outline generation and refinement, show the evolving outline
        if current_step in ["generate_initial_outline", "refine_outline"] and state.get("outline"):
            if state["outline"] != outline:
                outline = state["outline"]
                print("\nCurrent outline:")
                for section in outline:
                    print(f"• {section['title']}")
                    for subsection in section.get("subsections", []):
                        print(f"  - {subsection['title']}")
                print()
        
        # For perspective identification, show the perspectives
        elif current_step == "identify_perspectives" and state.get("perspectives"):
            print("\nIdentified perspectives:")
            for perspective in state["perspectives"]:
                print(f"• {perspective}")
            print()
        
        # For section writing, show progress
        elif current_step == "write_sections" and state.get("sections"):
            section_count = len(state["sections"])
            print(f"\rWriting sections: {section_count} completed", end="")
        
        # For finalization, show completion
        elif current_step == "finalize_article" and state.get("final_article"):
            final_article = state["final_article"]
            print("\nArticle finalized!")
        
        # Simulate some processing time to make the streaming more visible
        time.sleep(0.1)
    
    # Print and save the final article
    if final_article:
        print("\n\n=== Final Article ===\n")
        print(final_article)
        
        # Save the article to a file
        with open("storm_streaming_article.md", "w") as f:
            f.write(final_article)
        
        logger.info("Article saved to storm_streaming_article.md")
    else:
        print("\nNo article was generated.")

if __name__ == "__main__":
    main() 