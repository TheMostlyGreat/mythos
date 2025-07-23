from typing import Optional, Dict, Any, List
from mythos.utils.llm_utils import call_llm, call_Anthropic_API, call_OpenAI_API, create_messages
from mythos.config.settings import (
    NARRATIVE_SYSTEM_PROMPT, 
    PLANNING_SYSTEM_PROMPT,
    CHARACTER_LIST_SCHEMA,
    CHAPTER_LIST_SCHEMA,
    STORY_CONCEPT_SCHEMA,
    CONCEPT_TITLE_SCHEMA,
    WEB_SEARCH_TOOL,
    RESEARCH_WITH_WEB_SEARCH
)

def generate_planning_text(
    prompt: str, 
    system_prompt: str = PLANNING_SYSTEM_PROMPT,
    json_schema: Optional[Dict[str, Any]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    **kwargs
) -> str:
    """
    Generates planning text using MEDIUM tier model for balanced cost/quality.

    Utilizes the unified LLM interface to create structured planning content that can be 
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
    **kwargs : additional parameters passed to call_llm

    Returns
    -------
    str
        The generated planning text or an error message if generation fails.
    """
    return call_llm(
        prompt=prompt,
        system_prompt=system_prompt,
        tier="medium",
        json_output=json_schema is not None,
        json_schema=json_schema,
        tools=tools,
        **kwargs
    )

def generate_narrative_text(prompt: str, system_prompt: str = NARRATIVE_SYSTEM_PROMPT, **kwargs) -> str:
    """
    Generates narrative text using BIG tier model for maximum quality.

    Uses the highest quality tier for better storytelling and narrative flow.

    Parameters
    ----------
    prompt : str
        The user prompt to generate narrative text for.
    system_prompt : str, optional
        The system prompt to guide the generation (default is NARRATIVE_SYSTEM_PROMPT).
    **kwargs : additional parameters passed to call_llm

    Returns
    -------
    str
        The generated narrative text with improved quality from BIG tier model.
    """
    return call_llm(
        prompt=prompt,
        system_prompt=system_prompt,
        tier="big",
        **kwargs
    )

def summarize_text(text: str, summary_length: Optional[int] = None, **kwargs) -> str:
    """
    Summarize text using FAST tier model for cost-effective processing.

    Parameters
    ----------
    text : str
        The text to summarize.
    summary_length : int, optional
        Target length for the summary.
    **kwargs : additional parameters passed to call_llm

    Returns
    -------
    str
        The summarized text.
    """
    length_instruction = f" in approximately {summary_length} words" if summary_length else ""
    prompt = f"Summarize the following text concisely{length_instruction}:\n\n{text}"
    
    return call_llm(
        prompt=prompt,
        system_prompt=PLANNING_SYSTEM_PROMPT,
        tier="fast",
        **kwargs
    )

def generate_character_list(prompt: str, **kwargs) -> str:
    """
    Generate character list using MEDIUM tier model with JSON output.

    Parameters
    ----------
    prompt : str
        The prompt for character generation.
    **kwargs : additional parameters passed to call_llm

    Returns
    -------
    str
        JSON-formatted character list.
    """
    return call_llm(
        prompt=prompt,
        system_prompt=PLANNING_SYSTEM_PROMPT,
        tier="medium",
        json_output=True,
        json_schema=CHARACTER_LIST_SCHEMA,
        **kwargs
    )

def generate_chapter_list(prompt: str, **kwargs) -> str:
    """
    Generate chapter list using MEDIUM tier model with JSON output.

    Parameters
    ----------
    prompt : str
        The prompt for chapter list generation.
    **kwargs : additional parameters passed to call_llm

    Returns
    -------
    str
        JSON-formatted chapter list.
    """
    return call_llm(
        prompt=prompt,
        system_prompt=PLANNING_SYSTEM_PROMPT,
        tier="medium",
        json_output=True,
        json_schema=CHAPTER_LIST_SCHEMA,
        **kwargs
    )

def generate_story_concept(prompt: str, **kwargs) -> str:
    """
    Generate story concept using MEDIUM tier model.

    Parameters
    ----------
    prompt : str
        The prompt for story concept generation.
    **kwargs : additional parameters passed to call_llm

    Returns
    -------
    str
        The generated story concept.
    """
    return call_llm(
        prompt=prompt,
        system_prompt=PLANNING_SYSTEM_PROMPT,
        tier="medium",
        **kwargs
    )

def generate_web_enhanced_research(prompt: str, **kwargs) -> str:
    """
    Generate research using MEDIUM tier model with optional web search.

    Parameters
    ----------
    prompt : str
        The research prompt.
    **kwargs : additional parameters passed to call_llm

    Returns
    -------
    str
        The generated research content.
    """
    # Add web search tool if research enhancement is enabled
    tools = None
    if RESEARCH_WITH_WEB_SEARCH:
        tools = [WEB_SEARCH_TOOL]
    
    return call_llm(
        prompt=prompt,
        system_prompt=PLANNING_SYSTEM_PROMPT,
        tier="medium",
        tools=tools,
        **kwargs
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
    # Convert to message format using helper function
    messages = create_messages(prompt, system_prompt)
    
    # Use the enhanced API to get both content and response ID
    result = call_OpenAI_API(
        input=messages,
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