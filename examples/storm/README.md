# STORM Agent Examples

The STORM (Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking) agent is designed to generate comprehensive, well-researched articles on any topic. It implements the STORM pattern developed by Stanford researchers.

## How STORM Works

STORM breaks down the article generation process into several key steps:

1. **Generate Initial Outline**: Creates a structured outline for the article
2. **Identify Diverse Perspectives**: Identifies different viewpoints to ensure comprehensive coverage
3. **Simulated Conversations**: Conducts "interviews" between researchers with different perspectives and topic experts, gathering information and references
4. **Refine Outline**: Updates the outline based on research findings
5. **Write Sections**: Generates content for each section using the gathered references
6. **Finalize Article**: Integrates all sections into a cohesive article with proper citations

## Examples

### Basic Article Generation

The `basic_article_generation.py` example demonstrates how to use the STORM agent to generate a complete article. It:

- Configures different LLM models for different roles within the STORM agent
- Integrates a web search tool for information retrieval
- Generates a comprehensive article with a well-structured outline
- Saves the article to a markdown file

Run the example:

```bash
python examples/storm/basic_article_generation.py
```

### Streaming Article Generation

The `streaming_article_generation.py` example shows how to use the STORM agent's streaming capabilities to get real-time updates as the article generation progresses. This is useful for long-running generations where you want to see intermediate results.

Run the example:

```bash
python examples/storm/streaming_article_generation.py
```

## Requirements

To run these examples, you need:

1. OpenAI API key set in your environment variables or `.env` file
2. Required Python packages (install with `pip install -r requirements.txt`):
   - langchain
   - langchain-openai
   - langchain-community (for search tools)
   - python-dotenv

## Customization

You can customize the STORM agent by:

- Using different LLM models for different roles
- Adjusting the number of perspectives
- Changing the number of conversation turns
- Implementing different search tools
- Modifying the prompt templates in `src/agent_patterns/prompts/STORMAgent/`

## References

- Stanford STORM Research Paper: [STORM: Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking](https://aclanthology.org/2024.naacl-long.347.pdf)
- Stanford STORM GitHub Repository: [stanford-oval/storm](https://github.com/stanford-oval/storm) 