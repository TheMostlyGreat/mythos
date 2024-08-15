import os
import json
from openai import OpenAI
from anthropic import Anthropic
from mythos.constants import SYSTEM_PROMPT_PLANNING, SYSTEM_PROMPT_NARRATIVE, SYSTEM_PROMPT_JSON

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
    max_tokens = 4000  # Maximum number of tokens for the response
    temperature = 1     # Controls randomness of the output

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  # Initialize OpenAI client

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},  # System message
            {"role": "user", "content": prompt}            # User prompt
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
    max_tokens = 4000  # Maximum number of tokens for the response
    temperature = 1    # Controls randomness of the output

    client = Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))  # Initialize Anthropic client
    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,  # System message
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt  # User prompt
                    }
                ]
            }
        ]
    )
    return message.content  # Return the generated text

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
    max_tokens = 4000  # Maximum number of tokens for the response
    temperature = 1     # Controls randomness of the output

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  # Initialize OpenAI client

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=max_tokens,
        temperature=temperature,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": system_prompt},  # System message
            {"role": "user", "content": prompt}            # User prompt
        ]
    )
    response = completion.choices[0].message  # Get the response message

    # Validate the generated JSON
    if not is_valid_json(response.content):
        # If the JSON is not valid, try generating again
        prompt = "Please generate a valid JSON object for the following prompt: " + response.content
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},  # System message
                {"role": "user", "content": prompt}            # User prompt
            ]
        )
        response = completion.choices[0].message  # Get the response message

    return response.content  # Return the generated text