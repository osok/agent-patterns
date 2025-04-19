"""
STORM (Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking) Example
with Streaming Support

This example demonstrates how to use the STORM agent with streaming support to generate a
well-researched article on a given topic in a streaming fashion, showing the progress in real time.
"""

# CRITICAL IMPLEMENTATION REQUIREMENT:
# UNDER NO CIRCUMSTANCES ARE YOU TO USE ASYNC ANYTHING IN ANY CODE
# This applies to ALL files in the codebase - library code, tests, and examples
# All implementations MUST be synchronous only



import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agent_patterns.patterns.storm_agent import STORMAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def stream_handler(text_chunk, context):
    """Simple stream handler that prints the text chunk and context."""
    stage = context.get("stage", "unknown")
    role = context.get("role", "unknown")
    
    # Determine the prefix based on the stage
    if stage == "outline_generation":
        prefix = "📋 Outline"
    elif stage == "perspective_identification":
        prefix = "🔍 Perspectives"
    elif stage == "research":
        prefix = f"🔎 Research ({role})"
    elif stage == "writing":
        prefix = f"✍️ Writing ({role})"
    elif stage == "editing":
        prefix = "✏️ Editing"
    else:
        prefix = f"{stage} ({role})"
    
    # Print the chunk with the appropriate prefix
    print(f"{prefix}: {text_chunk}", end="", flush=True)

def main():
    # Check if the required environment variables are set
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable not set. Please set it in your .env file.")
        return
    
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent
    
    # Check both potential prompt directory paths
    src_prompt_dir = project_root / "src" / "agent_patterns" / "prompts"
    non_src_prompt_dir = project_root / "agent_patterns" / "prompts"
    
    # Use the path that exists
    if src_prompt_dir.exists():
        prompt_dir = str(src_prompt_dir)
    else:
        prompt_dir = str(non_src_prompt_dir)
    
    # Get model names from environment variables with improved defaults using our .env file
    openai_model_high = os.getenv("THINKING_MODEL_NAME")
    openai_provider = os.getenv("THINKING_MODEL_PROVIDER")
    anthropic_model = os.getenv("DOCUMENTATION_MODEL_NAME")
    anthropic_provider = os.getenv("DOCUMENTATION_MODEL_PROVIDER")
    
    # Create LLM configurations for different roles in the STORM agent
    llm_configs = {}
    
    # Configure roles with appropriate models
    high_reasoning_roles = ["outline_generator", "perspective_identifier", "expert", "editor"]
    for role in high_reasoning_roles:
        if anthropic_model and anthropic_provider == "anthropic":
            llm_configs[role] = {
                "provider": "anthropic",
                "model_name": anthropic_model,
                "temperature": 0.5,
                "streaming": True
            }
        elif openai_model_high and openai_provider == "openai":
            llm_configs[role] = {
                "provider": "openai",
                "model_name": openai_model_high,
                "temperature": 0.5,
                "streaming": True
            }
        else:
            logger.error(f"No model defined for high reasoning role: {role}. Please set appropriate model in .env file.")
            return
    
    standard_roles = ["researcher", "writer"]
    for role in standard_roles:
        if openai_model_high and openai_provider == "openai":
            llm_configs[role] = {
                "provider": "openai",
                "model_name": openai_model_high,
                "temperature": 0.7,
                "streaming": True
            }
        elif anthropic_model and anthropic_provider == "anthropic":
            llm_configs[role] = {
                "provider": "anthropic",
                "model_name": anthropic_model,
                "temperature": 0.7,
                "streaming": True
            }
        else:
            logger.error(f"No model defined for standard role: {role}. Please set appropriate model in .env file.")
            return
    
    # Create the STORM agent with streaming support
    agent = STORMAgent(
        llm_configs=llm_configs,
        num_perspectives=3,
        max_conversation_turns=3,
        prompt_dir=prompt_dir,
        tool_provider=None,
        memory=None
    )
    
    # Define the topic to research
    topic = "The future of remote work and its impact on urban planning"
    
    # Print the topic
    print(f"\n📘 Generating article on topic: {topic}\n")
    print("=" * 80 + "\n")
    
    # Run the STORM agent to generate an article
    result = agent.run(topic)
    
    # Print a separator
    print("\n" + "=" * 80)
    
    # Print the article outline
    print("\n📋 Final Article Outline:")
    for section in result["outline"]:
        print(f"• {section['title']}")
        for subsection in section.get("subsections", []):
            print(f"  - {subsection['title']}")
    
    # Print perspectives
    print("\n🔍 Research Perspectives:")
    for perspective in result["perspectives"]:
        print(f"• {perspective}")
    
    # Print the final article
    print("\n📄 Final Article:\n")
    print(result["article"])
    
    # Save the article to a file
    with open("storm_streaming_article.md", "w") as f:
        f.write(result["article"])
    
    logger.info("Article saved to storm_streaming_article.md")

if __name__ == "__main__":
    main() 