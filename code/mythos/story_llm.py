import os
import json
from openai import OpenAI
from anthropic import Anthropic
from mythos.constants import SYSTEM_PROMPT_PLANNING, SYSTEM_PROMPT_NARRATIVE, SYSTEM_PROMPT_JSON

# Initialize clients at module level
OPENAI_CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ANTHROPIC_CLIENT = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

# Set global model names
OPENAI_MODEL = "gpt-4o-mini"
ANTHROPIC_MODEL = "claude-3-5-sonnet-20240620"  # Updated to a current model name

DEFAULT_MAX_TOKENS = 4000
DEFAULT_TEMPERATURE = 1.0

def generate_planning_text(prompt: str, system_prompt: str = SYSTEM_PROMPT_PLANNING) -> str:
    """
    Generates planning text based on the provided prompt and system prompt.

    Parameters
    ----------
    prompt : str
        The user prompt to generate planning text for.
    system_prompt : str, optional
        The system prompt to guide the generation (default is SYSTEM_PROMPT_PLANNING).

    Returns
    -------
    str
        The generated planning text.
    """
    max_tokens = DEFAULT_MAX_TOKENS
    temperature = DEFAULT_TEMPERATURE

    completion = OPENAI_CLIENT.chat.completions.create(
        model=OPENAI_MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    response = completion.choices[0].message  # Get the response message

    return response.content  # Return the generated text


def is_valid_json(json_string: str) -> bool:
    """
    Checks if the provided string is valid JSON.

    Parameters
    ----------
    json_string : str
        The JSON string to validate.

    Returns
    -------
    bool
        True if the string is valid JSON, False otherwise.
    """
    try:
        json.loads(json_string)
        return True
    except ValueError:
        return False


def generate_narrative_text(prompt: str, system_prompt: str = SYSTEM_PROMPT_NARRATIVE) -> str:
    """
    Generates narrative text based on the provided prompt and system prompt.

    Parameters
    ----------
    prompt : str
        The user prompt to generate narrative text for.
    system_prompt : str, optional
        The system prompt to guide the generation (default is SYSTEM_PROMPT_NARRATIVE).

    Returns
    -------
    str
        The generated narrative text.
    """
    max_tokens = DEFAULT_MAX_TOKENS
    temperature = DEFAULT_TEMPERATURE

    message = ANTHROPIC_CLIENT.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )
    return message.content[0].text  # Return the generated text


def _generate_json_response(prompt: str, system_prompt: str, max_tokens: int, temperature: float) -> str:
    completion = OPENAI_CLIENT.chat.completions.create(
        model=OPENAI_MODEL,
        max_tokens=max_tokens,
        temperature=temperature,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content


def generate_json(prompt: str, system_prompt: str = SYSTEM_PROMPT_JSON) -> str:
    """
    Generates json based on the provided prompt and system prompt.

    Parameters
    ----------
    prompt : str
        The user prompt to generate json for.
    system_prompt : str, optional
        The system prompt to guide the generation (default is SYSTEM_PROMPT_JSON).

    Returns
    -------
    str
        The generated json.
    """
    max_tokens = DEFAULT_MAX_TOKENS
    temperature = DEFAULT_TEMPERATURE
    response = _generate_json_response(prompt, system_prompt, max_tokens, temperature)
    
    if not is_valid_json(response):
        prompt = f"Please generate a valid JSON object for the following prompt: {response}"
        response = _generate_json_response(prompt, system_prompt, max_tokens, temperature)
    
    return response