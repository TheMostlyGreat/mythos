# Mythos - AI-Powered Story Builder

An intelligent storytelling assistant that uses multi-tier AI models to create compelling narratives with rich world-building, character development, and narrative structure.

## 🚀 Multi-Tier LLM System

Mythos uses a sophisticated multi-tier LLM system that automatically selects the best AI model for each task:

- **FAST Tier**: Quick tasks like summarization and simple analysis
- **MEDIUM Tier**: Balanced tasks like planning, research, and asset creation  
- **BIG Tier**: Complex creative work like narrative writing and deep reasoning

### Current Configuration

```python
FAST_MODEL = ("openai", "gpt-4o-mini")                    # Ultra-fast + cost-effective
MEDIUM_MODEL = ("openai", "gpt-4o")                       # Good balance of speed/cost/quality  
BIG_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")   # High quality reasoning
PREMIUM_MODEL = ("anthropic", "claude-3-5-sonnet-20241022") # Maximum capability
```

### Mix-and-Match Flexibility

You can easily customize which models to use for each tier by editing `mythos/config/settings.py`:

```python
# All OpenAI (simpler setup)
FAST_MODEL = ("openai", "gpt-4o-mini")
MEDIUM_MODEL = ("openai", "gpt-4o")
BIG_MODEL = ("openai", "gpt-4o")
PREMIUM_MODEL = ("openai", "gpt-4o")

# All Anthropic (constitutional AI focused)
FAST_MODEL = ("anthropic", "claude-3-5-haiku-20241022")
MEDIUM_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")
BIG_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")
PREMIUM_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")

# Cost-optimized (all fast models)
FAST_MODEL = ("openai", "gpt-4o-mini")
MEDIUM_MODEL = ("openai", "gpt-4o-mini")
BIG_MODEL = ("openai", "gpt-4o")
PREMIUM_MODEL = ("openai", "gpt-4o")
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/mythos.git
cd mythos
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
```

## Usage

### Command Line Interface
```bash
python -m mythos create "A story about a time-traveling detective"
```

### Python API
```python
from mythos.services.story_builder import StoryBuilder
from mythos.utils.llm_utils import call_llm

# Build a complete story
builder = StoryBuilder()
story = builder.build_story("A cyberpunk thriller set in Neo Tokyo")

# Use the unified LLM interface directly
response = call_llm("Describe a futuristic city", tier="medium")
narrative = call_llm("Write a dramatic scene", tier="big")
summary = call_llm("Summarize this text...", tier="fast")
```

## Features

- **Automated Story Structure**: Uses the Snowflake method for structured storytelling
- **Rich Asset Generation**: Creates characters, settings, plots, themes, and research
- **Multi-Provider Support**: Mix OpenAI and Anthropic models for optimal results
- **Cost Optimization**: Automatically uses appropriate model tiers to minimize costs
- **JSON Structured Outputs**: Reliable data extraction with schema validation
- **Interactive Refinement**: Conversational story development process
- **EPUB Export**: Generate professional ebook formats
- **Version Control**: Track story iterations and changes

## Architecture

The system is built with a modular architecture:

- **Configuration Layer**: Flexible model tier management
- **Unified LLM Interface**: Single API for all providers and models
- **Story Management**: Comprehensive story and asset tracking
- **Writer Services**: Specialized functions for different content types
- **Asset Management**: Organized storage of story components

## Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.