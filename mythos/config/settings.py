import os
from dataclasses import dataclass
from enum import Enum

# Logging Settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()  # Default to INFO, allow DEBUG for development

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