from typing import Optional, Dict, Any, List
from mythos.utils.llm_utils import call_Anthropic_API, call_OpenAI_API
from mythos.config.settings import (
    NARRATIVE_SYSTEM_PROMPT, 
    PLANNING_SYSTEM_PROMPT,
    CHARACTER_LIST_SCHEMA,
    CHAPTER_LIST_SCHEMA,
    STORY_CONCEPT_SCHEMA,
    RESEARCH_SCHEMA,
    WEB_SEARCH_TOOL,
    RESEARCH_WITH_WEB_SEARCH
)

def generate_planning_text(
    prompt: str, 
    system_prompt: str = PLANNING_SYSTEM_PROMPT,
    json_schema: Optional[Dict[str, Any]] = None,
    tools: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Generates planning text based on the provided prompt and system prompt.

    Utilizes the OpenAI Responses API to create structured planning content that can be 
    used for outlining stories, projects, or other planning needs.

    Parameters
    ----------
    prompt : str
        The user prompt to generate planning text for.
    system_prompt : str, optional
        The system prompt to guide the generation (default is PLANNING_SYSTEM_PROMPT).
    json_schema : dict, optional
        JSON schema for Structured Outputs (provides 100% reliable JSON)
    tools : list, optional
        List of tools to enable (e.g., web search for research)

    Returns
    -------
    str
        The generated planning text or an error message if generation fails.
    """
    # Use Structured Outputs and tools when provided
    return call_OpenAI_API(
        prompt=prompt, 
        system_prompt=system_prompt,
        json_output=json_schema is not None,
        json_schema=json_schema,
        tools=tools
    )

def generate_web_enhanced_research(prompt: str) -> str:
    """
    Generate enhanced research using web search capabilities of the Responses API.
    
    This function leverages the Responses API's built-in web search to provide
    real-time, up-to-date research for story development.
    
    Parameters
    ----------
    prompt : str
        The research prompt or topic
        
    Returns
    -------
    str
        JSON string with research findings following the schema
    """
    if not RESEARCH_WITH_WEB_SEARCH:
        # Fall back to regular research without web search
        return generate_planning_text(
            prompt=prompt,
            system_prompt="You are a research assistant providing detailed, accurate information for story development.",
            json_schema=RESEARCH_SCHEMA
        )
    
    research_system_prompt = """You are an expert research assistant helping with story development. 
    Use web search to find current, accurate information about the topic. 
    Focus on historical accuracy, cultural authenticity, and credible sources.
    Provide detailed findings that will help create authentic, well-researched stories."""
    
    # Use web search tool for enhanced research
    return call_OpenAI_API(
        prompt=prompt,
        system_prompt=research_system_prompt,
        json_output=True,
        json_schema=RESEARCH_SCHEMA,
        tools=[WEB_SEARCH_TOOL]
    )

def generate_character_list(prompt: str) -> str:
    """
    Generate a character list using Structured Outputs for 100% reliable JSON.
    
    Parameters
    ----------
    prompt : str
        The prompt for character generation
        
    Returns
    -------
    str
        JSON string with character list following the schema
    """
    return generate_planning_text(
        prompt=prompt,
        system_prompt="You are a creative writer creating compelling characters for a story.",
        json_schema=CHARACTER_LIST_SCHEMA
    )

def generate_chapter_list(prompt: str) -> str:
    """
    Generate a chapter list using Structured Outputs for 100% reliable JSON.
    
    Parameters
    ----------
    prompt : str
        The prompt for chapter list generation
        
    Returns
    -------
    str
        JSON string with chapter list following the schema
    """
    return generate_planning_text(
        prompt=prompt,
        system_prompt="You are a skilled story planner creating a detailed chapter outline.",
        json_schema=CHAPTER_LIST_SCHEMA
    )

def generate_story_concept(prompt: str) -> str:
    """
    Generate a story concept using markdown format.
    
    Parameters
    ----------
    prompt : str
        The prompt for story concept generation
        
    Returns
    -------
    str
        Markdown formatted story concept following the template
    """
    return generate_planning_text(
        prompt=prompt,
        system_prompt="You are a creative storyteller developing compelling story concepts. Output in markdown format following the provided template."
    )

def generate_narrative_text(prompt: str, system_prompt: str = NARRATIVE_SYSTEM_PROMPT) -> str:
    """
    Generates narrative text using Claude 4 with enhanced capabilities.

    Uses Claude 4's reasoning mode for better storytelling and narrative flow.

    Parameters
    ----------
    prompt : str
        The user prompt to generate narrative text for.
    system_prompt : str, optional
        The system prompt to guide the generation (default is SYSTEM_PROMPT_NARRATIVE).

    Returns
    -------
    str
        The generated narrative text with improved quality from Claude 4 reasoning.
    """
    # Use Claude 4's reasoning mode for better narrative quality
    return call_Anthropic_API(
        prompt=prompt, 
        system_prompt=system_prompt,
        use_reasoning=True,  # Enable reasoning for better storytelling
        structured_output=True  # Ensure well-formatted narrative output
    )

def generate_conversation_aware_content(
    prompt: str, 
    system_prompt: str = PLANNING_SYSTEM_PROMPT,
    previous_response_id: Optional[str] = None,
    json_schema: Optional[Dict[str, Any]] = None
) -> tuple[str, str]:
    """
    Generate content with conversation awareness using the Responses API's built-in state management.
    
    This function demonstrates the power of the Responses API's conversation continuity.
    
    Parameters
    ----------
    prompt : str
        The current prompt
    system_prompt : str
        The system prompt to guide generation
    previous_response_id : str, optional
        ID from previous response for conversation continuity
    json_schema : dict, optional
        JSON schema for structured outputs
        
    Returns
    -------
    tuple[str, str]
        A tuple of (generated_content, response_id) for future conversation continuity
    """
    # Use the enhanced API to get both content and response ID
    result = call_OpenAI_API(
        prompt=prompt,
        system_prompt=system_prompt,
        json_output=json_schema is not None,
        json_schema=json_schema,
        previous_response_id=previous_response_id,
        return_response_id=True
    )
    
    # Extract content and response ID from the result
    if isinstance(result, tuple):
        content, response_id = result
    else:
        # Handle error case
        content = result
        response_id = None
    
    return content, response_id

def summarize_text(text: str, summary_length: int) -> str:
    """
    Summarizes the provided text.
    """
    prompt = (f"## Text to summarize:\n{text}\n"
              f"## Prompt: Please summarize the text to {summary_length} words.")
    
    return call_OpenAI_API(prompt=prompt, system_prompt=PLANNING_SYSTEM_PROMPT)