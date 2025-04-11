# Building a Research Assistant

This tutorial guides you through building a research assistant agent that can search for information, analyze findings, and generate comprehensive reports.

## Overview

Research assistants need to:

1. Search for information from multiple sources
2. Evaluate the reliability of sources
3. Extract key information and insights
4. Organize findings into a coherent structure
5. Generate well-formatted reports with citations

For this use case, we'll use the STORM agent pattern, which excels at careful reasoning and self-evaluation.

## Prerequisites

- Agent Patterns library installed
- OpenAI API key (or other supported LLM provider)
- Basic Python knowledge

## Step 1: Setting Up the Project

Create a new Python file called `research_assistant.py`:

```python
import os
import asyncio
from dotenv import load_dotenv
from agent_patterns.patterns.storm_agent import StormAgent
from agent_patterns.core.memory import SemanticMemory, EpisodicMemory, CompositeMemory
from agent_patterns.core.memory.persistence import InMemoryPersistence
from agent_patterns.core.tools.providers.composite_provider import CompositeToolProvider
from agent_patterns.core.tools.providers.search_provider import SearchToolProvider
from agent_patterns.core.tools.providers.wikipedia_provider import WikipediaToolProvider
from agent_patterns.core.tools.providers.file_provider import FileToolProvider

# Load environment variables
load_dotenv()
```

## Step 2: Setting Up Memory

Our research assistant will benefit from both:
- Semantic memory: to store facts and findings
- Episodic memory: to remember search history and the research process

```python
# Set up memory persistence
persistence = InMemoryPersistence()
asyncio.run(persistence.initialize())

# Create memory components
semantic_memory = SemanticMemory(
    persistence, 
    namespace="research_findings"
)

episodic_memory = EpisodicMemory(
    persistence, 
    namespace="research_process"
)

# Create composite memory
memory = CompositeMemory({
    "semantic": semantic_memory,
    "episodic": episodic_memory
})
```

## Step 3: Setting Up Tools

Our research assistant needs tools for:
1. Web search
2. Wikipedia lookup
3. File operations (to save research findings)

```python
# Create tool providers
search_provider = SearchToolProvider()
wikipedia_provider = WikipediaToolProvider()
file_provider = FileToolProvider(workspace_dir="./research_workspace")

# Combine tool providers
tool_provider = CompositeToolProvider([
    search_provider, 
    wikipedia_provider, 
    file_provider
])
```

## Step 4: Creating the Research Agent

Now, let's create our STORM-based research assistant:

```python
# Configure LLM settings
llm_configs = {
    "default": {
        "provider": os.getenv("DEFAULT_MODEL_PROVIDER", "openai"),
        "model_name": os.getenv("DEFAULT_MODEL_NAME", "gpt-4o")
    },
    "evaluation": {
        "provider": os.getenv("EVALUATION_MODEL_PROVIDER", "anthropic"),
        "model_name": os.getenv("EVALUATION_MODEL_NAME", "claude-3-opus-20240229")
    }
}

# Create the research agent
research_agent = StormAgent(
    llm_configs=llm_configs,
    memory=memory,
    memory_config={
        "semantic": True,
        "episodic": True
    },
    tool_provider=tool_provider,
    storm_config={
        "evaluation_threshold": 0.8,  # Higher threshold for careful research
        "max_self_evaluations": 3,     # Allow multiple rounds of evaluation
        "options_to_generate": 5       # Consider more options for research paths
    }
)
```

## Step 5: Creating a Research Manager

Let's wrap our research agent with a manager class that provides a more user-friendly interface:

```python
class ResearchAssistant:
    def __init__(self):
        # Configure and create the agent (code from above)
        self.agent = research_agent
        self.current_topic = None
        self.findings = {}
    
    def research_topic(self, topic, depth="medium"):
        """Conduct research on a specific topic."""
        self.current_topic = topic
        
        # Map depth to number of research iterations
        depth_map = {
            "brief": 1,
            "medium": 2,
            "deep": 3
        }
        research_iterations = depth_map.get(depth, 2)
        
        findings = []
        
        # First, get an overview
        overview_query = f"Provide a brief overview of {topic}. What are the key aspects I should research?"
        overview = self.agent.run(overview_query)
        findings.append({"phase": "overview", "content": overview})
        
        # Then, explore key aspects
        for i in range(research_iterations):
            if i == 0:
                # First iteration focuses on main facts
                query = f"Research the main facts about {topic}. Focus on verified information from reliable sources."
            elif i == 1:
                # Second iteration looks for different perspectives
                query = f"Research different perspectives on {topic}. Look for contrasting viewpoints from credible sources."
            else:
                # Third iteration goes deeper
                query = f"Conduct in-depth research on {topic}, focusing on recent developments and specialized information."
            
            result = self.agent.run(query)
            findings.append({"phase": f"research_{i+1}", "content": result})
        
        # Save findings
        self.findings[topic] = findings
        
        return findings
    
    def generate_report(self, topic=None, format_type="comprehensive"):
        """Generate a formatted report based on research findings."""
        if topic is None:
            topic = self.current_topic
        
        if topic not in self.findings:
            return "No research findings available for this topic."
        
        # Create a prompt based on format type
        if format_type == "comprehensive":
            prompt = f"""
            Create a comprehensive research report on {topic} based on our research findings.
            Include:
            1. Executive summary
            2. Introduction to the topic
            3. Methodology
            4. Key findings (with citations)
            5. Analysis of different perspectives
            6. Conclusions
            7. References
            
            Our research findings:
            {self.findings[topic]}
            
            Format the report professionally with appropriate headings and structure.
            """
        elif format_type == "brief":
            prompt = f"""
            Create a brief research summary on {topic} based on our research findings.
            Include:
            1. Summary of key points
            2. Most important findings
            3. Brief list of sources
            
            Our research findings:
            {self.findings[topic]}
            
            Keep the report concise and to the point.
            """
        else:  # presentation
            prompt = f"""
            Create a presentation outline on {topic} based on our research findings.
            Include:
            1. Title slide
            2. Introduction to the topic
            3. 5-7 key points with supporting evidence
            4. Contrasting perspectives
            5. Conclusions and implications
            6. References
            
            Our research findings:
            {self.findings[topic]}
            
            Format as a presentation outline with key talking points.
            """
        
        # Generate the report
        report = self.agent.run(prompt)
        
        # Save the report
        file_name = f"{topic.replace(' ', '_').lower()}_report.md"
        
        try:
            import os
            os.makedirs("./research_outputs", exist_ok=True)
            with open(f"./research_outputs/{file_name}", "w") as f:
                f.write(report)
        except Exception as e:
            print(f"Error saving report: {str(e)}")
        
        return report
    
    def save_findings_to_memory(self, topic=None):
        """Save research findings to semantic memory for future reference."""
        if topic is None:
            topic = self.current_topic
        
        if topic not in self.findings:
            return "No research findings available for this topic."
        
        # Extract key facts and save to semantic memory
        prompt = f"""
        Extract 10-15 key facts from our research on {topic}.
        Format each fact as a simple statement.
        
        Our research findings:
        {self.findings[topic]}
        """
        
        facts = self.agent.run(prompt)
        
        # Parse facts and save to memory
        import re
        fact_list = re.findall(r'^\s*\d+\.\s*(.+)$', facts, re.MULTILINE)
        
        for fact in fact_list:
            asyncio.run(semantic_memory.save({
                "entity": topic,
                "attribute": "fact",
                "value": fact.strip()
            }))
        
        return f"Saved {len(fact_list)} facts to memory for topic: {topic}"
```

## Step 6: Using the Research Assistant

Now let's create a simple interface to use our research assistant:

```python
def main():
    # Create the research assistant
    assistant = ResearchAssistant()
    
    # Get topic from user
    topic = input("What topic would you like to research? ")
    
    # Get research depth
    print("\nResearch depth:")
    print("1. Brief")
    print("2. Medium")
    print("3. Deep")
    depth_choice = input("Choose a research depth (1-3): ")
    
    depth_map = {
        "1": "brief",
        "2": "medium",
        "3": "deep"
    }
    depth = depth_map.get(depth_choice, "medium")
    
    # Conduct research
    print(f"\nResearching {topic} at {depth} depth...")
    findings = assistant.research_topic(topic, depth)
    
    # Get report type
    print("\nReport format:")
    print("1. Comprehensive")
    print("2. Brief")
    print("3. Presentation")
    format_choice = input("Choose a report format (1-3): ")
    
    format_map = {
        "1": "comprehensive",
        "2": "brief",
        "3": "presentation"
    }
    format_type = format_map.get(format_choice, "comprehensive")
    
    # Generate report
    print(f"\nGenerating {format_type} report...")
    report = assistant.generate_report(format_type=format_type)
    
    # Save findings to memory
    assistant.save_findings_to_memory()
    
    print(f"\nReport generated and saved to ./research_outputs/{topic.replace(' ', '_').lower()}_report.md")
    
    # Show the first 500 characters of the report
    print("\nReport preview:")
    print("-" * 80)
    print(report[:500] + "...")
    print("-" * 80)

if __name__ == "__main__":
    main()
```

## Step 7: Enhancing with Source Evaluation

Let's add a source evaluation capability to our research assistant:

```python
# Add this method to the ResearchAssistant class
def evaluate_sources(self, sources):
    """Evaluate the reliability and credibility of a list of sources."""
    if not sources:
        return "No sources provided for evaluation."
    
    # Format sources as a string
    sources_text = "\n".join([f"- {source}" for source in sources])
    
    # Create evaluation prompt
    prompt = f"""
    Evaluate the following sources in terms of reliability and credibility:
    
    {sources_text}
    
    For each source, provide:
    1. Source name/URL
    2. Reliability score (1-10)
    3. Credibility assessment
    4. Potential biases
    5. Recommendation on how to use this source
    
    Format your response as a structured evaluation.
    """
    
    # Run evaluation
    evaluation = self.agent.run(prompt)
    
    return evaluation
```

## Complete Code

Here's the complete code for our research assistant:

```python
import os
import asyncio
import re
from dotenv import load_dotenv
from agent_patterns.patterns.storm_agent import StormAgent
from agent_patterns.core.memory import SemanticMemory, EpisodicMemory, CompositeMemory
from agent_patterns.core.memory.persistence import InMemoryPersistence
from agent_patterns.core.tools.providers.composite_provider import CompositeToolProvider
from agent_patterns.core.tools.providers.search_provider import SearchToolProvider
from agent_patterns.core.tools.providers.wikipedia_provider import WikipediaToolProvider
from agent_patterns.core.tools.providers.file_provider import FileToolProvider

# Load environment variables
load_dotenv()

# Set up memory persistence
persistence = InMemoryPersistence()
asyncio.run(persistence.initialize())

# Create memory components
semantic_memory = SemanticMemory(
    persistence, 
    namespace="research_findings"
)

episodic_memory = EpisodicMemory(
    persistence, 
    namespace="research_process"
)

# Create composite memory
memory = CompositeMemory({
    "semantic": semantic_memory,
    "episodic": episodic_memory
})

# Create tool providers
search_provider = SearchToolProvider()
wikipedia_provider = WikipediaToolProvider()
file_provider = FileToolProvider(workspace_dir="./research_workspace")

# Combine tool providers
tool_provider = CompositeToolProvider([
    search_provider, 
    wikipedia_provider, 
    file_provider
])

# Configure LLM settings
llm_configs = {
    "default": {
        "provider": os.getenv("DEFAULT_MODEL_PROVIDER", "openai"),
        "model_name": os.getenv("DEFAULT_MODEL_NAME", "gpt-4o")
    },
    "evaluation": {
        "provider": os.getenv("EVALUATION_MODEL_PROVIDER", "anthropic"),
        "model_name": os.getenv("EVALUATION_MODEL_NAME", "claude-3-opus-20240229")
    }
}

# Create the STORM research agent
research_agent = StormAgent(
    llm_configs=llm_configs,
    memory=memory,
    memory_config={
        "semantic": True,
        "episodic": True
    },
    tool_provider=tool_provider,
    storm_config={
        "evaluation_threshold": 0.8,
        "max_self_evaluations": 3,
        "options_to_generate": 5
    }
)

class ResearchAssistant:
    def __init__(self):
        self.agent = research_agent
        self.current_topic = None
        self.findings = {}
    
    def research_topic(self, topic, depth="medium"):
        """Conduct research on a specific topic."""
        self.current_topic = topic
        
        # Map depth to number of research iterations
        depth_map = {
            "brief": 1,
            "medium": 2,
            "deep": 3
        }
        research_iterations = depth_map.get(depth, 2)
        
        findings = []
        
        # First, get an overview
        overview_query = f"Provide a brief overview of {topic}. What are the key aspects I should research?"
        overview = self.agent.run(overview_query)
        findings.append({"phase": "overview", "content": overview})
        
        # Then, explore key aspects
        for i in range(research_iterations):
            if i == 0:
                # First iteration focuses on main facts
                query = f"Research the main facts about {topic}. Focus on verified information from reliable sources."
            elif i == 1:
                # Second iteration looks for different perspectives
                query = f"Research different perspectives on {topic}. Look for contrasting viewpoints from credible sources."
            else:
                # Third iteration goes deeper
                query = f"Conduct in-depth research on {topic}, focusing on recent developments and specialized information."
            
            result = self.agent.run(query)
            findings.append({"phase": f"research_{i+1}", "content": result})
        
        # Save findings
        self.findings[topic] = findings
        
        return findings
    
    def generate_report(self, topic=None, format_type="comprehensive"):
        """Generate a formatted report based on research findings."""
        if topic is None:
            topic = self.current_topic
        
        if topic not in self.findings:
            return "No research findings available for this topic."
        
        # Create a prompt based on format type
        if format_type == "comprehensive":
            prompt = f"""
            Create a comprehensive research report on {topic} based on our research findings.
            Include:
            1. Executive summary
            2. Introduction to the topic
            3. Methodology
            4. Key findings (with citations)
            5. Analysis of different perspectives
            6. Conclusions
            7. References
            
            Our research findings:
            {self.findings[topic]}
            
            Format the report professionally with appropriate headings and structure.
            """
        elif format_type == "brief":
            prompt = f"""
            Create a brief research summary on {topic} based on our research findings.
            Include:
            1. Summary of key points
            2. Most important findings
            3. Brief list of sources
            
            Our research findings:
            {self.findings[topic]}
            
            Keep the report concise and to the point.
            """
        else:  # presentation
            prompt = f"""
            Create a presentation outline on {topic} based on our research findings.
            Include:
            1. Title slide
            2. Introduction to the topic
            3. 5-7 key points with supporting evidence
            4. Contrasting perspectives
            5. Conclusions and implications
            6. References
            
            Our research findings:
            {self.findings[topic]}
            
            Format as a presentation outline with key talking points.
            """
        
        # Generate the report
        report = self.agent.run(prompt)
        
        # Save the report
        file_name = f"{topic.replace(' ', '_').lower()}_report.md"
        
        try:
            import os
            os.makedirs("./research_outputs", exist_ok=True)
            with open(f"./research_outputs/{file_name}", "w") as f:
                f.write(report)
        except Exception as e:
            print(f"Error saving report: {str(e)}")
        
        return report
    
    def save_findings_to_memory(self, topic=None):
        """Save research findings to semantic memory for future reference."""
        if topic is None:
            topic = self.current_topic
        
        if topic not in self.findings:
            return "No research findings available for this topic."
        
        # Extract key facts and save to semantic memory
        prompt = f"""
        Extract 10-15 key facts from our research on {topic}.
        Format each fact as a simple statement.
        
        Our research findings:
        {self.findings[topic]}
        """
        
        facts = self.agent.run(prompt)
        
        # Parse facts and save to memory
        fact_list = re.findall(r'^\s*\d+\.\s*(.+)$', facts, re.MULTILINE)
        
        for fact in fact_list:
            asyncio.run(semantic_memory.save({
                "entity": topic,
                "attribute": "fact",
                "value": fact.strip()
            }))
        
        return f"Saved {len(fact_list)} facts to memory for topic: {topic}"
    
    def evaluate_sources(self, sources):
        """Evaluate the reliability and credibility of a list of sources."""
        if not sources:
            return "No sources provided for evaluation."
        
        # Format sources as a string
        sources_text = "\n".join([f"- {source}" for source in sources])
        
        # Create evaluation prompt
        prompt = f"""
        Evaluate the following sources in terms of reliability and credibility:
        
        {sources_text}
        
        For each source, provide:
        1. Source name/URL
        2. Reliability score (1-10)
        3. Credibility assessment
        4. Potential biases
        5. Recommendation on how to use this source
        
        Format your response as a structured evaluation.
        """
        
        # Run evaluation
        evaluation = self.agent.run(prompt)
        
        return evaluation

def main():
    # Create the research assistant
    assistant = ResearchAssistant()
    
    # Get topic from user
    topic = input("What topic would you like to research? ")
    
    # Get research depth
    print("\nResearch depth:")
    print("1. Brief")
    print("2. Medium")
    print("3. Deep")
    depth_choice = input("Choose a research depth (1-3): ")
    
    depth_map = {
        "1": "brief",
        "2": "medium",
        "3": "deep"
    }
    depth = depth_map.get(depth_choice, "medium")
    
    # Conduct research
    print(f"\nResearching {topic} at {depth} depth...")
    findings = assistant.research_topic(topic, depth)
    
    # Get report type
    print("\nReport format:")
    print("1. Comprehensive")
    print("2. Brief")
    print("3. Presentation")
    format_choice = input("Choose a report format (1-3): ")
    
    format_map = {
        "1": "comprehensive",
        "2": "brief",
        "3": "presentation"
    }
    format_type = format_map.get(format_choice, "comprehensive")
    
    # Generate report
    print(f"\nGenerating {format_type} report...")
    report = assistant.generate_report(format_type=format_type)
    
    # Save findings to memory
    assistant.save_findings_to_memory()
    
    print(f"\nReport generated and saved to ./research_outputs/{topic.replace(' ', '_').lower()}_report.md")
    
    # Show the first 500 characters of the report
    print("\nReport preview:")
    print("-" * 80)
    print(report[:500] + "...")
    print("-" * 80)
    
    # Option to evaluate sources
    evaluate_choice = input("\nWould you like to evaluate the sources used? (y/n): ")
    if evaluate_choice.lower() == 'y':
        # Extract sources from report (simplified approach)
        sources = re.findall(r'https?://[^\s\)]+', report)
        sources = list(set(sources))  # Remove duplicates
        
        if sources:
            print("\nEvaluating sources...")
            evaluation = assistant.evaluate_sources(sources)
            print("\nSource Evaluation:")
            print("-" * 80)
            print(evaluation)
            print("-" * 80)
        else:
            print("\nNo URLs found in the report to evaluate.")

if __name__ == "__main__":
    main()
```

## Architecture Diagram

```mermaid
graph TD
    A[User Interface] --> B[Research Assistant]
    B --> C[STORM Agent]
    C --> D[Tool Provider]
    C --> E[Memory System]
    
    D --> F[Search Provider]
    D --> G[Wikipedia Provider]
    D --> H[File Provider]
    
    E --> I[Semantic Memory]
    E --> J[Episodic Memory]
    
    B --> K[Research Topic]
    B --> L[Generate Report]
    B --> M[Evaluate Sources]
    B --> N[Save Findings]
```

## Next Steps

You can enhance this research assistant with:

1. **PDF processing**: Add capability to analyze academic papers and PDFs
2. **Citation management**: Implement proper citation tracking and formatting
3. **Multi-agent research**: Create specialized agents for different research tasks
4. **Custom domain knowledge**: Pre-populate memory with domain-specific information
5. **Interactive research**: Allow users to guide the research process interactively

By using the STORM agent pattern, our research assistant benefits from:
- Careful self-evaluation of research findings
- Multiple options considered for research approaches
- Step-by-step reasoning for high-quality research
- Mistake detection to avoid inaccuracies

This approach creates a research assistant that not only finds information but evaluates it critically and produces well-structured reports.