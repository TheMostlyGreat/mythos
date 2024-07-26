import os

#Story Asset Names
PLOT_OUTLINE = "plot_outline"
OVERVIEW = "concept"
CONCEPT = "concept"
SETTING = "setting"
CAST = "cast"
THEMES_AND_MOTIFS = "themes_and_motifs"
WORLD_RULES = "world_rules"
CHARACTER_RULES = "character_rules"
WRITING_STYLE = "writing_style"
NARRATIVE_OUTLINE = "narrative_outline"
CHAPTER_SUMMARY = "chapter_summary"

#Directory Names
STORY_DIR = "../stories"
CHARACTERS_DIR = "characters"
ASSETS_DIR = "assets"

#Other Settings
ASSET_SUMMARY_LENGTH = 300
CORE_PERSPECTIVES = [
        "structual", "formalism", "psychoanalytical", "linguistic", 
        "cultural", "historical", "intertextuality", "reader-response"]
SYSTEM_PROMPT_PLANNING = (
            "You are a renowned Harvard literature professor, NYT bestselling book editor, "
            "and world-class storyteller. Your expertise lies in crafting brief, clear, and "
            "specific narratives that captivate readers. Help me outline an entertaining and "
            "engaging story. Keep your responses concise and clear."
        )
SYSTEM_PROMPT_NARRATIVE = "Write in the style of Cormac McCarthy"
SYSTEM_PROMPT_JSON = (
    "You are a machine that only returns and replies with valid, iterable RFC8259 compliant"
    "JSON in your responses. "
    "Ensure the JSON is well-formed and does not include any extraneous characters or formatting"
    "Your responses should be in the following format: "
    "{'key': 'value'}"
)