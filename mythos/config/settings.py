"""
Mythos Project Configuration Settings

This configuration file adheres to the .cursorrules specifications:
- OpenAI: ALWAYS use Responses API (https://api.openai.com/v1/responses)
- Anthropic: Use Messages API (https://api.anthropic.com/v1/messages)
- Environment: Pull API keys from shell (no .env files) 
- Parameters: Named only, never positional
- JSON Schemas: Include additionalProperties: False for strict mode
- Error Handling: ProviderError (retry) vs ContentRefusalError (no retry)
- Comments: Thorough explanations for everything
"""

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Tuple

# Logging Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()  # Default to INFO, allow DEBUG for development

# Multi-Tier LLM Configuration
# Model configuration based on .cursorrules specifications - using latest 2025 models

# Production Models (Primary Configuration)
FAST_MODEL = ("openai", "gpt-4.1-nano")                       # Ultra-fast tasks, very low cost
MEDIUM_MODEL = ("anthropic", "claude-sonnet-4-20250514")      # Balanced production work
BIG_MODEL = ("anthropic", "claude-opus-4-20250514")           # Main production logic

# Backup Models
BACKUP_FAST_MODEL = ("openai", "gpt-4.1-mini")
BACKUP_MEDIUM_MODEL = ("openai", "gpt-4.1") #"claude-sonnet-4-20250514"
BACKUP_BIG_MODEL = ("openai", "gpt-4.5")

# Reasoning Models (For Complex Analysis)
REASONING_FAST = ("openai", "o4-mini")                         # Fast reasoning
REASONING_MEDIUM = ("openai", "o3-mini")                       # Cost-effective reasoning  
REASONING_MAX = ("openai", "o3")                               # Maximum reasoning capability
REASONING_ORIGINAL = ("openai", "o1")                          # Original reasoning model

# Specialized Models
IMAGE_GENERATION_MODEL = ("openai", "gpt-image-1")             # Text-to-image, editing
IMAGE_STANDALONE_MODEL = ("openai", "dall-e-3")               # Standalone image generation
SPEECH_TO_TEXT_MODEL = ("openai", "whisper-1")                # Audio transcription
EMBEDDINGS_MODEL = ("openai", "text-embedding-3-large")       # Semantic search

# Alternative configurations - uncomment to use:

# All OpenAI (latest 4.1 series)
#FAST_MODEL = ("openai", "gpt-4.1-nano")
#MEDIUM_MODEL = ("openai", "gpt-4.1-mini")
#BIG_MODEL = ("openai", "gpt-4.1")
#PREMIUM_MODEL = ("openai", "gpt-4.1")

# All Anthropic (Claude 3.5 series - real available models)
#FAST_MODEL = ("anthropic", "claude-3-5-haiku-20241022")
#MEDIUM_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")
#BIG_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")
#PREMIUM_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")

# Claude 4 Series (Latest - May 2025) - When available
#PREMIUM_MODEL = ("anthropic", "claude-opus-4-20250514")       # Most capable (ASL-3 safety)
#BIG_MODEL = ("anthropic", "claude-sonnet-4-20250514")         # Balanced (ASL-2 safety)

# Claude 3.7 Series (Hybrid Reasoning) - When available  
#REASONING_HYBRID = ("anthropic", "claude-3-7-sonnet-20250219") # First hybrid reasoning model

# Cost-optimized (all fast models)
#FAST_MODEL = ("openai", "gpt-4o-mini")
#MEDIUM_MODEL = ("openai", "gpt-4o-mini")
#BIG_MODEL = ("openai", "gpt-4o")
#PREMIUM_MODEL = ("openai", "gpt-4o")

# Quality-first (all premium models)
#FAST_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")
#MEDIUM_MODEL = ("anthropic", "claude-3-5-sonnet-20241022") 
#BIG_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")
#PREMIUM_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")

# API Keys (only sensitive data in environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Legacy model settings for backward compatibility
# These are calculated but never imported anywhere
OPENAI_MODEL = MEDIUM_MODEL[1] if MEDIUM_MODEL[0] == "openai" else "gpt-4o"
ANTHROPIC_MODEL = BIG_MODEL[1] if BIG_MODEL[0] == "anthropic" else "claude-3-5-sonnet-20241022"

MAX_RETRIES = 3  # Increased from 2 to 3 for better reliability

# Timeout settings for different types of operations
STANDARD_TIMEOUT = 180  # 3 minutes for standard operations (increased from 120)
CONCEPT_TIMEOUT = 300   # 5 minutes for concept generation (longer timeout)
NARRATIVE_TIMEOUT = 240 # 4 minutes for narrative generation

# API Endpoint Configuration (Based on .cursorrules specifications)
# These are hardcoded in llm_utils.py and not imported
OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_RESPONSES_ENDPOINT = f"{OPENAI_BASE_URL}/responses"
ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1"
ANTHROPIC_MESSAGES_ENDPOINT = f"{ANTHROPIC_BASE_URL}/messages"
ANTHROPIC_VERSION = "2023-06-01"

# Error Classes for Proper Exception Handling
# These are redefined in llm_utils.py
class ProviderError(Exception):
    """Base exception for API provider errors that should trigger retries."""
    pass

class ContentRefusalError(Exception):
    """Exception for content refusals that should NOT trigger retries."""
    pass

PLANNING_SYSTEM_PROMPT = (
            "You are world class storyteller assisting the user to plan their story. Focus on clarity, structure, "
            "and emotional resonance. Open with a compelling hook and maintain flow. "
            "Develop multifaceted characters who drive conflict and growth. Show, don't tell: use sensory details "
            "and subtext over direct exposition. Maintain a consistent voice while embracing creative language. "
            "Give each scene purpose, advancing plot or revealing character. Stay authentic, yet avoid clichés; "
            "experiment with fresh ideas. Engage all senses to immerse the reader in the narrative. "
            "trim unnecessary words and refine pacing. Write with purpose. Balance action with reflection to sustain "
            "momentum and depth. Remember, readers crave connection—craft stories that linger in their minds."
)

NARRATIVE_SYSTEM_PROMPT = (
    "You are writing engaging narrative copy based on the style expressed in "
    "the prompt. Stick to that style. Show, don't tell. Don't be cliche. Output in markdown format."
)

JSON_SYSTEM_PROMPT = (
    "You are a machine that only returns and replies with valid, iterable RFC8259 compliant"
    "JSON in your responses. "
    "Ensure the JSON is well-formed and does not include any extraneous characters or formatting"
    "Your responses should be in the following format: "
    "{'key': 'value'}"
)

#Directory Names
STORY_DIR = "./stories"
JSON_DIR = "json"
ASSETS_DIR = "assets"
CHAPTER_DIR = f"{ASSETS_DIR}/chapters"
MANUSCRIPT_DIR = "manuscript"
RESEARCH_DIR = f"{ASSETS_DIR}/research"  # New research directory
SETTINGS_DIR = f"{ASSETS_DIR}/settings"  # New settings directory
CRITICAL_ANALYSIS_DIR = f"{ASSETS_DIR}/critical-analysis"  # Critical analysis directory

# Critical Perspective Constants
META_TEMPLATE_PATH = Path("templates/critical_perspective_template_generator.md")
TEMPLATE_SUBDIR = "templates"

# Asset Settings
ASSET_SUMMARY_LENGTH = 300

# Responses API Tools - Enhanced capabilities enabled by the Responses API
# Based on .cursorrules specifications for built-in tools

# These are never imported in llm_utils.py
WEB_SEARCH_TOOL = {"type": "web_search_preview"}
FILE_SEARCH_TOOL = {"type": "file_search"}
IMAGE_GENERATION_TOOL = {"type": "image_generation"}
MCP_TOOL_TEMPLATE = {"type": "mcp"}
FUNCTION_CALL_TOOL_TEMPLATE = {"type": "function"}

# Enhanced story research with web search (when enabled)
# Never imported in llm_utils.py
RESEARCH_WITH_WEB_SEARCH = False

# Background task configuration for long-running operations (o-series models)
# Never imported in llm_utils.py
ENABLE_BACKGROUND_TASKS = True

# Streaming configuration for real-time responses
# Never imported in llm_utils.py
ENABLE_STREAMING = True

# JSON Schemas for Structured Outputs
# These provide 100% reliable JSON generation with OpenAI Responses API

CHARACTER_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "characters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["name", "description"],
                "additionalProperties": False
            }
        }
    },
    "required": ["characters"],
    "additionalProperties": False
}

CHAPTER_LIST_SCHEMA = {
    "type": "object",
    "properties": {
        "chapters": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "chapter_number": {"type": "integer"},
                    "title": {"type": "string"},
                    "summary": {
                        "type": "object",
                        "properties": {
                            "overview": {"type": "string"}
                        },
                        "required": ["overview"],
                        "additionalProperties": False
                    },
                    "key_points": {
                        "type": "object",
                        "properties": {
                            "event_1": {"type": "string"},
                            "event_2": {"type": "string"},
                            "event_3": {"type": "string"}
                        },
                        "required": ["event_1", "event_2", "event_3"],
                        "additionalProperties": False
                    },
                    "hook": {"type": "string"}
                },
                "required": ["chapter_number", "title", "summary", "key_points", "hook"],
                "additionalProperties": False
            }
        }
    },
    "required": ["chapters"],
    "additionalProperties": False
}

STORY_CONCEPT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "genre": {"type": "string"},
        "setting": {"type": "string"},
        "premise": {"type": "string"},
        "themes": {
            "type": "array",
            "items": {"type": "string"}
        },
        "target_audience": {"type": "string"}
    },
    "required": ["title", "genre", "setting", "premise", "themes", "target_audience"],
    "additionalProperties": False
}

# Lightweight concept schema - extracts title reliably while keeping rich markdown content
CONCEPT_TITLE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "concept_markdown": {"type": "string"}
    },
    "required": ["title", "concept_markdown"],
    "additionalProperties": False
}

# Simple questioner response schema
QUESTIONER_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "response": {"type": "string"},
        "ready_to_stop": {"type": "boolean"}
    },
    "required": ["response", "ready_to_stop"],
    "additionalProperties": False
}

# Critical perspectives selection schema
CRITICAL_PERSPECTIVES_SCHEMA = {
    "type": "object",
    "properties": {
        "selected_perspectives": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 3
        },
        "rationale": {"type": "string"}
    },
    "required": ["selected_perspectives", "rationale"],
    "additionalProperties": False
}

# Asset Type Names. Example usage: AssetTypesNames.RESEARCH.value outputs "research"
class AssetTypeNames(str, Enum):
    CONCEPT = "concept"
    RESEARCH = "research"
    SETTINGS = "settings"
    PLOT = "plot"
    THEMES = "themes"
    CHARACTERS = "characters"
    TIMELINE = "timeline"
    CHAPTER_LIST = "chapter_list"
    WRITING_STYLE = "writing_style"
    CRITICAL_PERSPECTIVES = "critical_perspectives"
    CHAPTER_OUTLINE = "chapter_outline"
    MANUSCRIPT_CHAPTER = "manuscript_chapter"
    MANUSCRIPT_DRAFT = "manuscript_draft"

@dataclass(frozen=True)
class AssetType:
    """
    Automated registration of all story assets.

    Assets are defined in the `_assets_data` list and automatically registered
    as class attributes for easy access throughout the project.

    Example Access:
        - AssetTypes.RESEARCH.summary_length
        - AssetTypes.PLOT.template_path
    """
    title: str
    directory: str
    template_path: str
    summary_length: int

class AssetTypes:
    _assets_data = [
        {
            "key": AssetTypeNames.CONCEPT.name,
            "title": AssetTypeNames.CONCEPT.value,
            "directory": ASSETS_DIR,
            "file_extension": ".md",
            "template_path": "templates/concept_template.md",
            "summary_length": ASSET_SUMMARY_LENGTH
        },
        {
            "key": AssetTypeNames.RESEARCH.name,
            "title": AssetTypeNames.RESEARCH.value,
            "directory": RESEARCH_DIR,
            "file_extension": ".md",
            "template_path": "templates/research_template.md",
            "summary_length": ASSET_SUMMARY_LENGTH
        },
        {
            "key": AssetTypeNames.SETTINGS.name,
            "title": AssetTypeNames.SETTINGS.value,
            "directory": SETTINGS_DIR,
            "file_extension": ".md",
            "template_path": "templates/setting_template.md",
            "summary_length": ASSET_SUMMARY_LENGTH
        },
        {
            "key": AssetTypeNames.PLOT.name,
            "title": AssetTypeNames.PLOT.value,
            "directory": ASSETS_DIR,
            "file_extension": ".md",
            "template_path": "templates/plot_template.md",
            "summary_length": ASSET_SUMMARY_LENGTH
        },
        {
            "key": AssetTypeNames.THEMES.name,
            "title": AssetTypeNames.THEMES.value,
            "directory": ASSETS_DIR,
            "file_extension": ".md",
            "template_path": "templates/themes_template.md",
            "summary_length": ASSET_SUMMARY_LENGTH
        },
        {
            "key": AssetTypeNames.CHARACTERS.name,
            "title": AssetTypeNames.CHARACTERS.value,
            "directory": ASSETS_DIR,
            "file_extension": ".md",
            "template_path": "templates/characters_list_json.txt",
            "summary_length": ASSET_SUMMARY_LENGTH
        },
        {
            "key": AssetTypeNames.TIMELINE.name,
            "title": AssetTypeNames.TIMELINE.value,
            "directory": ASSETS_DIR,
            "file_extension": ".md",
            "template_path": "templates/timeline_template.md",
            "summary_length": ASSET_SUMMARY_LENGTH
        },
        {
            "key": AssetTypeNames.CHAPTER_LIST.name,
            "title": AssetTypeNames.CHAPTER_LIST.value,
            "directory": ASSETS_DIR,
            "file_extension": ".md",
            "template_path": "templates/chapter_list_json.txt",
            "summary_length": ASSET_SUMMARY_LENGTH
        },
        {
            "key": AssetTypeNames.WRITING_STYLE.name,
            "title": AssetTypeNames.WRITING_STYLE.value,
            "directory": ASSETS_DIR,
            "file_extension": ".md",
            "template_path": "templates/writing_style_template.md",
            "summary_length": ASSET_SUMMARY_LENGTH
        },
        {
            "key": AssetTypeNames.CRITICAL_PERSPECTIVES.name,
            "title": AssetTypeNames.CRITICAL_PERSPECTIVES.value,
            "directory": CRITICAL_ANALYSIS_DIR,
            "file_extension": ".md",
            "template_path": "templates/critical_perspective_template_generator.md",
            "summary_length": ASSET_SUMMARY_LENGTH
        },
        {
            "key": AssetTypeNames.CHAPTER_OUTLINE.name,
            "title": AssetTypeNames.CHAPTER_OUTLINE.value,
            "directory": CHAPTER_DIR,
            "file_extension": ".md",
            "template_path": "templates/chapter_template.md",
            "summary_length": ASSET_SUMMARY_LENGTH
        },
        {
            "key": AssetTypeNames.MANUSCRIPT_CHAPTER.name,
            "title": AssetTypeNames.MANUSCRIPT_CHAPTER.value,
            "directory": MANUSCRIPT_DIR,
            "file_extension": ".md",
            "template_path": None,
            "summary_length": ASSET_SUMMARY_LENGTH
        },
        {
            "key": AssetTypeNames.MANUSCRIPT_DRAFT.name,
            "title": "manuscript",
            "directory": MANUSCRIPT_DIR,
            "file_extension": ".md",
            "template_path": None,
            "summary_length": ASSET_SUMMARY_LENGTH
        }
    ]

    # Dynamically create class attributes for each asset
    for asset in _assets_data:
        vars()[asset["key"]] = AssetType(
            title=asset["title"],
            directory=asset["directory"],
            template_path=asset["template_path"],
            summary_length=asset["summary_length"]
        )

SYNOPSIS_ASSET_TYPE = [
    AssetTypeNames.CONCEPT.value,
    AssetTypeNames.RESEARCH.value,
    AssetTypeNames.CRITICAL_PERSPECTIVES.value,
    AssetTypeNames.SETTINGS.value,
    AssetTypeNames.PLOT.value,
    AssetTypeNames.THEMES.value,
    AssetTypeNames.CHARACTERS.value,
    AssetTypeNames.TIMELINE.value,
    AssetTypeNames.CHAPTER_LIST.value,
    AssetTypeNames.WRITING_STYLE.value
]

# Story Questioner Configuration
# Interactive story refinement through conversational AI questioning

QUESTIONER_SYSTEM_PROMPT = (
    "You are a story consultant helping users develop compelling story ideas through focused questions. "
    "Ask ONE clear question at a time to help make their story more engaging and page-turning.\n\n"

    "## Core Approach\n"
    "- Ask the next most important question to flesh out the story\n"
    "- Use simple questions (yes/no, multiple choice, short answer)\n"
    "- Acknowledge answers positively ('Great!', 'Perfect', 'Got it')\n"
    "- When user says something like 'unsure', offer 2-4 specific options\n"
    "- Accept 'skip' or something similar gracefully and move to next topic\n"
    "- STAY IN SETUP PHASE ONLY - never ask about plot twists, endings, or story surprises\n"
    "- Stop after 15-20 questions and offer to begin story development\n\n"

    "## What NOT to Ask (Preserve the Creative Journey)\n"
    "- Plot twists or surprises ('What's the big reveal?')\n"
    "- Story endings or resolutions ('How does it end?')\n"
    "- Specific plot events ('What happens in chapter 3?')\n"
    "- Character deaths or major betrayals\n"
    "- Mystery solutions or 'whodunit' answers\n"
    "- Detailed scene-by-scene breakdowns\n"
    "- Any question that would spoil the user's discovery process\n\n"

    "## What TO Ask (Foundation Elements Only)\n"
    "- Basic character traits and motivations\n"
    "- General setting and atmosphere\n"
    "- Story tone and genre\n"
    "- Relationship dynamics (not specific outcomes)\n"
    "- Central conflict type (not resolution)\n"
    "- World-building basics (magic systems, technology level)\n"
    "- Target audience and story scope\n\n"

    "## Question Priority Order\n"
    "1. Genre and tone\n"
    "2. Main character basics (age, role, personality trait)\n"
    "3. Setting (time, place, atmosphere)\n"
    "4. Central conflict or mystery\n"
    "5. Key relationships (love interest, antagonist)\n"
    "6. Story scope and pacing\n\n"

    "## Genre Adaptation\n"
    "- **Romance**: Focus on relationship dynamics, chemistry, obstacles\n"
    "- **Mystery**: Emphasize the central puzzle, clues, red herrings\n"
    "- **Fantasy**: Explore magic systems, world-building, special abilities\n"
    "- **Thriller**: Highlight danger, stakes, tension sources\n"
    "- **Science Fiction**: Focus on technology level, scientific concepts, future society\n"
    "- **Horror**: Focus on fear sources, atmosphere, what threatens characters\n"
    "- **Historical Fiction**: Focus on time period, historical accuracy vs. creative license\n"
    "- **Literary Fiction**: Focus on themes, character development, internal conflicts\n"
    "- **Adventure**: Focus on quests, journeys, obstacles to overcome\n"
    "- **Young Adult**: Focus on coming-of-age elements, school/family dynamics\n\n"

    "## Response Format\n"
    "- Brief acknowledgment of their answer\n"
    "- Clear next question\n"
    "- Use 'Next question:' or similar to maintain flow\n\n"

    "## Sample Interactions\n"

    "**Opening:**\n"
    "USER: 'Romantic mystery in 1920s with magic'\n"
    "YOU: 'Great premise! First question: Do you want the romance to be slow-burn, forbidden, or love triangle?'\n\n"

    "**Handling Uncertainty:**\n"
    "USER: 'I'm not sure about the magic system'\n"
    "YOU: 'No problem! Here are some options: Structured spells and potions, Wild emotional magic, Secret magical objects, or Hidden magical bloodlines?'\n\n"

    "**Genre Focus:**\n"
    "USER: 'It's a thriller'\n"
    "YOU: 'Perfect! What puts your main character in danger—a killer hunting them, a conspiracy they uncovered, or something they witnessed?'\n\n"

    "**Staying in Setup (Good vs. Bad):**\n"
    "✅ GOOD: 'What type of magic system—structured spells or wild instinctual power?'\n"
    "❌ BAD: 'What spell does she use to defeat the villain?'\n"
    "✅ GOOD: 'Is the love interest hiding something, or being completely honest?'\n"
    "❌ BAD: 'When does she discover he's been lying to her?'\n\n"

    "## Error Handling\n"
    "- If user asks for different questions: 'What would you prefer to focus on?'\n"
    "- If user seems overwhelmed: 'Want to take a step back and talk about the big picture?'\n"
    "- If user wants to restart: 'No problem! What's your core story idea?'\n\n"

    "## Completion\n"
    "After 15-20 focused questions, say: 'Great foundation! Ready to start developing your story concept, or do you want to explore any other aspects first?'\n\n"
    
    "## Output Format\n"
    "Always respond in JSON format with exactly these fields:\n"
    "{\n"
    "  \"response\": \"Your conversational response to the user\",\n"
    "  \"ready_to_stop\": false\n"
    "}\n\n"
    "Set ready_to_stop to true when you've gathered sufficient foundation (15-20 questions) and are ready to begin story development."
)

# Configuration Validation Function
# get_model_for_task() - not used in llm_utils.py (tier mapping is inline)
# validate_configuration() - the validation logic is inline in llm_utils.py

# Model Selection Helper Functions
# get_model_for_task() - not used in llm_utils.py (tier mapping is inline)

# Auto-validate configuration on import
try:
    # validate_configuration() # This line is removed as per the edit hint
    pass # No longer needed as validation is inline
except ProviderError as e:
    # Log warning but don't fail import (allows testing without API keys)
    import logging
    logging.warning(f"Configuration validation failed: {e}")

# Export commonly used models for easy access
__all__ = [
    'FAST_MODEL', 'MEDIUM_MODEL', 'BIG_MODEL', 'REASONING_FAST', 'REASONING_MEDIUM', 'REASONING_MAX', 'REASONING_ORIGINAL',
    'IMAGE_GENERATION_MODEL', 'IMAGE_STANDALONE_MODEL', 'SPEECH_TO_TEXT_MODEL', 'EMBEDDINGS_MODEL',
    'OPENAI_API_KEY', 'ANTHROPIC_API_KEY',
    'OPENAI_RESPONSES_ENDPOINT', 'ANTHROPIC_MESSAGES_ENDPOINT',
    'ProviderError', 'ContentRefusalError',
    'validate_configuration', 'get_model_for_task'
]
