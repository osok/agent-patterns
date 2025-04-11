"""
STORM (Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking) Example
with Memory and Tools

This example demonstrates how to use the STORM agent to generate a well-researched
article on a given topic using multi-perspective research, enhanced with memory
capabilities and tool integration.
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, List

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from langchain_openai import ChatOpenAI
from langchain.tools import Tool

# Import STORM agent and memory components
from agent_patterns.patterns.storm_agent import STORMAgent
from agent_patterns.core.memory import (
    SemanticMemory,
    EpisodicMemory,
    ProceduralMemory,
    CompositeMemory
)
from agent_patterns.core.memory.persistence import (
    InMemoryPersistence
)
from agent_patterns.core.tools.base import ToolProvider

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ContentResearchToolProvider(ToolProvider):
    """Tool provider for content research and data gathering."""
    
    def list_tools(self):
        """List available tools."""
        return [
            {
                "name": "web_search",
                "description": "Search the web for information on a given query",
                "parameters": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                }
            },
            {
                "name": "get_statistics",
                "description": "Get statistics about a specific topic",
                "parameters": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to get statistics for"
                    }
                }
            },
            {
                "name": "get_expert_quotes",
                "description": "Get expert quotes on a specific topic",
                "parameters": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to get expert quotes for"
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name, params):
        """Execute the requested tool with the provided parameters."""
        if tool_name == "web_search":
            query = params.get("query", "")
            return self._web_search(query)
        elif tool_name == "get_statistics":
            topic = params.get("topic", "")
            return self._get_statistics(topic)
        elif tool_name == "get_expert_quotes":
            topic = params.get("topic", "")
            return self._get_expert_quotes(topic)
        else:
            return f"Unknown tool: {tool_name}"
    
    def _web_search(self, query: str) -> str:
        """Simulate web search results."""
        logger.info(f"Searching for: {query}")
        
        # Mock search results
        if "ai" in query.lower() and "creative" in query.lower():
            return """
Results for "generative AI in creative industries":

1. According to a recent report, 37% of creative professionals are now using AI tools in their workflow.
2. Industries most impacted by generative AI include graphic design, content creation, and music production.
3. The global market for AI in creative applications is projected to reach $14.5 billion by 2026.
4. Major concerns include copyright issues, job displacement, and questions about authorship.
5. Several major creative software companies have integrated AI tools into their products in the past year.
            """
        elif "ai" in query.lower() and "future" in query.lower():
            return """
Results for "future of AI in creative work":

1. Experts predict AI will shift creative work toward more conceptual and directorial roles.
2. Emerging trends include AI-human collaboration tools that preserve creative control.
3. Ethical AI creation frameworks are being developed by several organizations.
4. Educational institutions are beginning to incorporate AI literacy into creative curricula.
5. Research suggests hybrid AI-human creative teams outperform either humans or AI working alone.
            """
        else:
            return f"General search results for: {query}\n1. Found multiple relevant resources on {query}\n2. Recent studies show increasing interest in {query}\n3. Experts have varying opinions on the implications of {query}"
    
    def _get_statistics(self, topic: str) -> str:
        """Get statistics about a specific topic."""
        logger.info(f"Getting statistics for: {topic}")
        
        # Mock statistics
        statistics = {
            "generative ai": """
Key statistics on Generative AI:
- Market size: $10.2 billion in 2022, expected to reach $44.8 billion by 2027 (CAGR of 34.3%)
- Adoption rate: 35% of businesses report using generative AI tools in 2023
- Investment: Venture capital funding for generative AI startups exceeded $5.1 billion in 2022
- Efficiency gains: Companies report 20-40% productivity improvements in content creation tasks
- Job impact: 82% of creative professionals believe AI will change their job responsibilities
            """,
            "creative industries": """
Key statistics on Creative Industries:
- Global value: $2.25 trillion market value worldwide
- Employment: Approximately 30 million jobs globally
- Growth rate: 4.3% annual growth pre-pandemic, now recovering at 5.6%
- Digital transformation: 74% of creative businesses accelerated digital adoption since 2020
- Freelance economy: 43% of creative work is performed by freelancers or contractors
            """,
            "ai art": """
Key statistics on AI Art:
- Market growth: 900% increase in AI-generated art sales since 2020
- Platform usage: Over 20 million people have used AI art generators
- Exhibition presence: 28% increase in AI art exhibitions in major galleries
- Price points: Average sale price of AI-assisted art is 35% lower than traditional art
- Creator demographics: 62% of AI artists come from non-traditional art backgrounds
            """
        }
        
        # Find the best match or return general stats
        for key, value in statistics.items():
            if key in topic.lower():
                return value
        
        return f"No specific statistics found for '{topic}', but related fields show significant growth and transformation due to technological advances."
    
    def _get_expert_quotes(self, topic: str) -> str:
        """Get expert quotes on a specific topic."""
        logger.info(f"Getting expert quotes for: {topic}")
        
        # Mock expert quotes
        quotes = {
            "generative ai": """
Expert quotes on Generative AI:

Dr. Emily Chen, AI Ethics Researcher: "The democratization of AI creation tools presents both unprecedented opportunities and ethical challenges we're only beginning to understand."

Marcus Johnson, Creative Director at DesignForward: "Rather than replacing creative professionals, we're seeing AI become a collaborative partner that handles repetitive tasks while humans focus on high-level creative direction."

Prof. Rajiv Patel, MIT Media Lab: "The most successful implementations of generative AI don't aim to replicate human creativity but rather to extend it in new directions."

Sarah Williams, Animation Supervisor: "Our studio reduced production time by 40% using AI for in-betweening frames, allowing artists to focus on the key moments that define character and emotion."
            """,
            "copyright": """
Expert quotes on AI and Copyright:

Lawrence Miller, Intellectual Property Attorney: "Current copyright law is struggling to address AI-generated works. Who owns the output when an AI is trained on copyrighted materials?"

Dr. Helena Wong, Digital Rights Advocate: "We need a new framework that balances protecting original creators' rights while enabling innovation in AI-assisted creation."

Michael Torres, Music Producer: "The industry is facing an existential question: if an AI creates a melody trained on existing songs, at what point is it derivative versus transformative?"

Judge Rebecca Thompson: "Courts will likely establish a spectrum of AI involvement, with different copyright implications depending on the level of human creative direction."
            """,
            "future": """
Expert quotes on the Future of Creative AI:

David Levy, Futurist: "By 2030, we'll likely see creative AI systems that can understand cultural context and emotional resonance in ways that feel genuinely intuitive."

Grace Kim, Product Lead at Creative Cloud: "The future isn't AI replacing creatives - it's creatives who use AI replacing those who don't."

Prof. Thomas Wright, Oxford University: "The most profound shift will be from seeing AI as a tool to viewing it as a creative collaborator with its own strengths and perspectives."

Luna Park, Award-winning Digital Artist: "We're moving toward a future where the distinction between human and AI creativity becomes less important than the quality and impact of the work itself."
            """
        }
        
        # Find the best match or return general quotes
        for key, value in quotes.items():
            if key in topic.lower():
                return value
        
        return f"No specific expert quotes found for '{topic}', but experts generally emphasize the transformative potential balanced with ethical considerations in emerging technologies."

def setup_memory():
    """Set up a composite memory system."""
    # Create persistence backend
    persistence = InMemoryPersistence()
    asyncio.run(persistence.initialize())
    
    # Create individual memory types
    semantic_memory = SemanticMemory(persistence, namespace="article_semantic")
    episodic_memory = EpisodicMemory(persistence, namespace="article_episodic")
    procedural_memory = ProceduralMemory(persistence, namespace="article_procedural")
    
    # Create composite memory
    memory = CompositeMemory({
        "semantic": semantic_memory,
        "episodic": episodic_memory,
        "procedural": procedural_memory
    })
    
    # Pre-populate with some semantic memories
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "generative_ai", "attribute": "definition", "value": "AI systems that can create new content including text, images, code, and audio"}
    ))
    
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "article_style", "attribute": "preferences", "value": "balanced perspective, evidence-based claims, engaging narrative flow"}
    ))
    
    # Add a procedural memory for article writing
    asyncio.run(memory.save_to(
        "procedural",
        {
            "name": "article_structure",
            "pattern": {
                "template": """When writing comprehensive articles:
1. Start with an engaging hook that introduces the topic
2. Present multiple perspectives with fair representation
3. Include relevant statistics and expert opinions
4. Address counterarguments and nuances
5. Follow a narrative style that is {preferences}
6. End with implications or forward-looking conclusions"""
            },
            "description": "Template for structuring well-researched articles",
            "tags": ["writing", "research", "structure"]
        }
    ))
    
    return memory

def main():
    # Check if the required environment variables are set
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable not set. Please set it in your .env file.")
        return
    
    # Get the project root directory
    current_dir = Path(__file__).parent.absolute()
    project_root = current_dir.parent.parent
    prompt_dir = str(project_root / "src" / "agent_patterns" / "prompts")
    
    # Set up memory
    memory = setup_memory()
    
    # Set up tool provider
    tool_provider = ContentResearchToolProvider()

    # Create LLM configurations for different roles in the STORM agent
    llm_configs = {}
    
    # Use GPT-4 for roles that need high reasoning capabilities
    high_reasoning_roles = ["outline_generator", "perspective_identifier", "expert", "editor"]
    for role in high_reasoning_roles:
        llm_configs[role] = {
            "provider": "openai",
            "model_name": "gpt-4o",
            "temperature": 0.5
        }
    
    # Use GPT-3.5 for roles that need more standard capabilities
    standard_roles = ["researcher", "writer"]
    for role in standard_roles:
        llm_configs[role] = {
            "provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7
        }
    
    # Create the STORM agent with memory and tools
    agent = STORMAgent(
        llm_configs=llm_configs,
        tool_provider=tool_provider,
        memory=memory,
        memory_config={
            "semantic": True,
            "episodic": True,
            "procedural": True
        },
        num_perspectives=3,
        max_conversation_turns=3,
        prompt_dir=prompt_dir
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
    
    # Show what was stored in memory
    print("\n=== MEMORY AFTER EXECUTION ===")
    
    print("\nSemantic memories:")
    facts = asyncio.run(memory.retrieve_from("semantic", "", limit=5))
    for i, fact in enumerate(facts):
        print(f"{i+1}. {fact}")
    
    print("\nEpisodic memories:")
    episodes = asyncio.run(memory.retrieve_from("episodic", "generative AI creative", limit=5))
    for i, episode in enumerate(episodes):
        print(f"{i+1}. {episode.content}")

if __name__ == "__main__":
    main() 