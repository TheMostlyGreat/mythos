from dataclasses import dataclass
from enum import Enum
# LLM Settings
OPENAI_MODEL = "o4-mini-2025-04-16"
ANTHROPIC_MODEL = "claude-opus-4-20250514"

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

# Enhanced research schema for web-augmented story development
RESEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "research_topic": {"type": "string"},
        "key_findings": {
            "type": "array",
            "items": {"type": "string"}
        },
        "historical_context": {"type": "string"},
        "cultural_elements": {
            "type": "array",
            "items": {"type": "string"}
        },
        "authenticity_notes": {"type": "string"},
        "source_credibility": {"type": "string"}
    },
    "required": ["research_topic", "key_findings", "historical_context", "cultural_elements", "authenticity_notes", "source_credibility"],
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
            "directory": ASSETS_DIR,
            "file_extension": ".md",
            "template_path": "templates/research_template.md",
            "summary_length": ASSET_SUMMARY_LENGTH
        },
        {
            "key": AssetTypeNames.SETTINGS.name,
            "title": AssetTypeNames.SETTINGS.value,
            "directory": ASSETS_DIR,
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