from dataclasses import dataclass
from enum import Enum
# LLM Settings
OPENAI_MODEL = "o4-mini-2025-04-16"
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"

MAX_RETRIES = 2

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

#Asset Settings
ASSET_SUMMARY_LENGTH = 300

# Responses API Tools - New capabilities enabled by the Responses API
WEB_SEARCH_TOOL = {
    "type": "web_search"
}

FILE_SEARCH_TOOL = {
    "type": "file_search"
}

# Enhanced story research with web search
RESEARCH_WITH_WEB_SEARCH = False

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
    "You are a story consultant helping users develop their story ideas through simple, engaging questions. "
    "Your goal is to ask ONE clear question at a time that helps make their story more compelling, "
    "engrossing, page turner for the user that they will rave about.\n"
    "Be concise, clear, direct, and understandable. Don't use bullets or lists.\n"
    
    "Core Approach:\n"
    "- Always ask the next most important question to help flesh out the story \n"
    "- Ask simple conversational questions requiring minimal thought (yes/no, multiple choice, short answer)\n"
    "- Acknowledge each answer positively ('Great', 'Perfect', 'Nice', 'Got it')\n"
    "- When user says 'unsure' or 'don't know', offer 2-5 specific options to choose from\n"
    "- If user asks for different questions, immediately adjust your approach\n"
    "- Accept 'skip' gracefully and move to the next logical topic\n"
    "- Never ask about endings or spoil potential mysteries\n\n"
    
    "Response Format:\n"
    "- Acknowledge their answer briefly\n"
    "- Ask your next question clearly\n"
    "- Use phrases like 'Next question:' to maintain conversation flow\n"
    "- When offering options, present them as a simple list\n\n"
    
    "Example progression:\n"
    "'Great prompt. To make this story unforgettable, I need to understand your vision better.\n\n"
    "First question:\n"
    "Is the main character a [specific options based on their prompt]?'\n\n"
    
    "Always show genuine interest in their creative vision and help them build something they're excited to write."
)
# Example questions for the story questioner agent.
# These are used to guide the user in shaping their story prompt into a more compelling narrative.
# Each question is simple, specific, and easy to answer (yes/no, multiple choice, or short answer).
# These examples are for developer reference and not shown to the user.

QUESTIONER_EXAMPLE_QUESTIONS = [
    "Do you want the romance to be slow-burn, forbidden, love triangle, reunited lovers, or something else?",
    "Is the main character a man, woman, or someone else?",
    "Is she a witch, a detective, a reporter, or something else?",
    "Is she new to the magical world, or has she grown up in it?",
    "Where does the story take place—big city, small town, boarding school, or somewhere else?",
    "Does she know she's a witch at the start, or does she discover it during the story?",
    "What kind of mystery is at the center—murder, missing person, secret society, cursed object, or something else?",
    "Does she stumble into the secret society by accident, or is she drawn in on purpose?",
    "What kind of magic is this society hiding—dark and dangerous, ancient and sacred, quirky and rule-bending, or something else?",
    "Is the love interest part of the secret society?",
    "Is the love interest helping her—or hiding things from her?",
    "What’s one trait you want her to have that makes her stand out? (e.g. clever, stubborn, charming, reckless…)",
    "What’s one trait the love interest has that makes him hard to read? (e.g. aloof, witty, wounded, charming, stoic)",
    "Is the story more fast-paced and twisty, or moody and atmospheric?",
    "Do you want the magic system to feel structured and rule-based, or wild and instinctual?",
    "Should the setting feel historically accurate 1920s, or more alternate-history magical 1920s?",
    "Should the secret society be tied to something real from the 1920s, or totally invented?",
    "Is the main character originally from the city, or did she just arrive?",
    "What brought her to the city? (e.g. job, family, running from something, chasing a dream?)",
    "How old is she? (late teens, 20s, 30s?)",
    "Do you want the tone to lean more romantic and sexy, or more mysterious and tense (with romance as a subplot)?",
    "How should the story end—happy, tragic, open-ended, or twisty and unresolved?",
    "Do you want the story to be a standalone, or the first in a series?"
]   
