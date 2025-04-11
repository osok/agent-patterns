"""
Example demonstrating the LATS (Language Agent Tree Search) agent pattern with memory and tools.

This example shows how to initialize and use the LATS agent for
solving problems that benefit from exploring multiple reasoning paths,
enhanced with memory capabilities and tool integration.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from langgraph.errors import GraphRecursionError

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agent_patterns.patterns.lats_agent import LATSAgent
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

# Load environment variables
load_dotenv()

class MarketResearchToolProvider(ToolProvider):
    """Tool provider for market research and analysis."""
    
    def list_tools(self):
        """List the available tools."""
        return [
            {
                "name": "market_research",
                "description": "Get market research data about user behavior on social media",
                "parameters": {
                    "platform": {
                        "type": "string",
                        "description": "The social media platform to research"
                    }
                }
            },
            {
                "name": "competitor_analysis",
                "description": "Analyze competitor strategies and results",
                "parameters": {
                    "competitor": {
                        "type": "string",
                        "description": "The competitor to analyze"
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name, params):
        """Execute the requested tool with the provided parameters."""
        if tool_name == "market_research":
            platform = params.get("platform", "general").lower()
            return self._get_market_research(platform)
        elif tool_name == "competitor_analysis":
            competitor = params.get("competitor", "general")
            return self._get_competitor_analysis(competitor)
        else:
            return f"Unknown tool: {tool_name}"
    
    def _get_market_research(self, platform):
        """Get market research data for a specific platform."""
        research_data = {
            "instagram": """
Instagram User Engagement Data:
- 63% of users check Instagram at least once daily
- Average time spent: 28 minutes per day
- Posts with faces get 38% more engagement
- Video content receives 2x more engagement than static images
- Prime posting times: 11am-1pm and 7pm-9pm
- Most engaged audience: 18-29 age group
- Hashtags can increase engagement by up to 12.6%
            """,
            "twitter": """
Twitter User Engagement Data:
- 42% of users check Twitter multiple times daily
- Average time spent: 31 minutes per day
- Tweets with images get 150% more retweets
- Tweets with videos get 10x more engagement
- Prime posting times: 8am-10am and 6pm-9pm
- Most engaged audience: 25-34 age group
- Tweets with hashtags get 100% more engagement
            """,
            "facebook": """
Facebook User Engagement Data:
- 74% of users visit Facebook daily
- Average time spent: 38 minutes per day
- Video posts get 59% more engagement than other post types
- Posts with questions get 100% more comments
- Prime posting times: 1pm-4pm
- Most engaged audience: 30-49 age group
- Posts with emojis receive 57% more likes
            """,
            "tiktok": """
TikTok User Engagement Data:
- 90% of users access TikTok daily
- Average time spent: 89 minutes per day
- Videos with trending songs get 14% more engagement
- User-generated challenges can increase engagement by 30%
- Prime posting times: 9am-11am and 7pm-11pm
- Most engaged audience: 16-24 age group
- Trending hashtags can increase views by 300%
            """,
            "general": """
General Social Media Engagement Data:
- Users spend an average of 2.5 hours daily on social media
- Visual content gets 40% more engagement across platforms
- User-generated content receives 28% higher engagement rates
- 54% of users research products on social media before purchasing
- Personalized content increases engagement by 48%
- Interactive content (polls, quizzes) gets 2x more engagement than static content
- Responding to comments can increase engagement by 89%
            """
        }
        
        return research_data.get(platform, research_data["general"])
    
    def _get_competitor_analysis(self, competitor):
        """Get analysis of a specific competitor."""
        competitor_data = {
            "tiktok": """
TikTok Strategy Analysis:
- Focuses on short-form, trend-based content
- Uses creator partnerships extensively
- Algorithm favors new creators and content types
- Strong focus on music and audio trends
- Rapid innovation in features (effects, editing tools)
- Emphasis on authenticity over polished content
            """,
            "instagram": """
Instagram Strategy Analysis:
- Balances feed posts, Stories, and Reels
- Strong emphasis on visual aesthetics
- Regular introduction of shopping features
- Uses a combination of chronological and algorithmic content surfacing
- Focuses on creator monetization tools
- Emphasizes Reels to compete with TikTok
            """,
            "twitter": """
Twitter Strategy Analysis:
- Focus on real-time content and conversations
- Strong emphasis on trending topics
- Growing focus on Communities feature
- Introduction of Twitter Blue for premium features
- Leverages lists and topics for content discovery
- Uses edit feature as premium offering
            """,
            "general": """
General Competitor Analysis:
- Most successful platforms emphasize content creator tools
- Trend toward short-form video content across all platforms
- Increasing focus on AR/VR experiences
- Growing emphasis on in-app shopping experiences
- Algorithm tweaks prioritize time spent over engagement counts
- Increased investment in direct messaging features
- Community-building tools showing strong growth
            """
        }
        
        return competitor_data.get(competitor.lower(), competitor_data["general"])

def setup_memory():
    """Set up a composite memory system."""
    # Create persistence backend
    persistence = InMemoryPersistence()
    asyncio.run(persistence.initialize())
    
    # Create individual memory types
    semantic_memory = SemanticMemory(persistence, namespace="engagement_semantic")
    episodic_memory = EpisodicMemory(persistence, namespace="engagement_episodic")
    procedural_memory = ProceduralMemory(persistence, namespace="engagement_procedural")
    
    # Create composite memory
    memory = CompositeMemory({
        "semantic": semantic_memory,
        "episodic": episodic_memory,
        "procedural": procedural_memory
    })
    
    # Pre-populate with some semantic memories
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "social_media", "attribute": "key_metrics", "value": ["engagement rate", "time spent", "click-through rate", "shares"]}
    ))
    
    asyncio.run(memory.save_to(
        "semantic", 
        {"entity": "target_audience", "attribute": "demographics", "value": {"age": "18-34", "interests": ["technology", "entertainment", "lifestyle"]}}
    ))
    
    # Add a procedural memory for strategy development
    asyncio.run(memory.save_to(
        "procedural",
        {
            "name": "strategy_development",
            "pattern": {
                "template": """When developing engagement strategies:
1. Consider target audience demographics: {demographics}
2. Focus on key performance metrics like engagement rate and time spent
3. Evaluate competitor approaches and differentiate
4. Prioritize content types that align with platform algorithms
5. Include both short-term tactics and long-term strategic goals"""
            },
            "description": "Template for developing effective engagement strategies",
            "tags": ["strategy", "engagement", "planning"]
        }
    ))
    
    return memory

def main():
    """Run the LATS agent example with memory and tools."""
    # Configure the LLMs for different roles
    llm_configs = {
        "thinking": {
            "provider": os.getenv("THINKING_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("THINKING_MODEL_NAME", "gpt-4-turbo"),
        },
        "evaluation": {
            "provider": os.getenv("EVALUATION_MODEL_PROVIDER", "openai"),
            "model_name": os.getenv("EVALUATION_MODEL_NAME", "gpt-4-turbo"),
        }
    }
    
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
    
    # Set up memory
    memory = setup_memory()
    
    # Set up tool provider
    tool_provider = MarketResearchToolProvider()
    
    # Create the LATS agent with custom parameters, memory and tools
    agent = LATSAgent(
        llm_configs=llm_configs,
        max_iterations=15,  # Maximum number of search iterations
        max_depth=4,        # Maximum depth of tree exploration
        exploration_weight=1.0,  # UCB exploration parameter (higher = more exploration)
        n_expansions=3,     # Number of branches to create at each node
        memory=memory,
        memory_config={
            "semantic": True,
            "episodic": True,
            "procedural": True
        },
        tool_provider=tool_provider,
        prompt_dir=prompt_dir  # Path to prompt templates
    )
    
    # Example problem
    problem = "Develop a strategy to increase user engagement on a social media platform"
    
    print("\n" + "="*80)
    print(f"PROBLEM: {problem}")
    print("="*80)
    
    # Configuration with higher recursion limit
    config = {"recursion_limit": 100}
    
    # Run the agent with error handling
    try:
        result = agent.run(problem, config=config)
        
        # Print the result
        print("\n" + "="*80)
        print("SOLUTION:")
        print("="*80)
        print(result)
        
        # Show what was stored in memory
        print("\n" + "="*80)
        print("MEMORY AFTER EXECUTION:")
        
        print("\nSemantic memories:")
        facts = asyncio.run(memory.retrieve_from("semantic", "", limit=5))
        for i, fact in enumerate(facts):
            print(f"{i+1}. {fact}")
        
        print("\nEpisodic memories:")
        episodes = asyncio.run(memory.retrieve_from("episodic", "engagement strategy", limit=5))
        for i, episode in enumerate(episodes):
            print(f"{i+1}. {episode.content}")
        
    except GraphRecursionError as e:
        print("\n" + "="*80)
        print("ERROR: Graph recursion limit reached.")
        print("The example requires a higher recursion limit to complete.")
        print("Please increase the recursion_limit parameter or reduce the max_iterations/max_depth.")
        print("="*80)

if __name__ == "__main__":
    main() 