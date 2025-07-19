import time
from typing import Optional, Dict, Any, Union
from openai import OpenAI
from anthropic import Anthropic
from mythos.config.settings import OPENAI_MODEL, MAX_RETRIES, ANTHROPIC_MODEL, JSON_SYSTEM_PROMPT
from mythos.utils.logger import get_logger
from mythos.utils.token_counter import TokenCounter

logger = get_logger(__name__)
token_counter = TokenCounter()

def call_OpenAI_API(
    prompt: str, 
    system_prompt: str, 
    json_output: bool = True,
    json_schema: Optional[Dict[str, Any]] = None,
    previous_response_id: Optional[str] = None,
    tools: Optional[list] = None,
    return_response_id: bool = False
) -> Union[str, tuple[str, str]]:
    """
    Call OpenAI Responses API - the new stateful API that replaces Chat Completions.
    
    Args:
        prompt: The user prompt
        system_prompt: The system prompt (uses instructions parameter)
        json_output: Whether to expect JSON output
        json_schema: Optional JSON schema for Structured Outputs (recommended)
        previous_response_id: ID from previous response for conversation continuity
        tools: Optional list of tools to enable (e.g., web_search, file_search)
        return_response_id: If True, returns (content, response_id) tuple
    
    Returns:
        If return_response_id is False: The API response as a string
        If return_response_id is True: Tuple of (response_string, response_id)
    """
    max_tokens = 4000  # Maximum number of tokens for the response
    temperature = 1    # Controls randomness of the output

    client = OpenAI()

    for attempt in range(MAX_RETRIES):
        try:
            # Prepare text format for structured outputs
            text_format = None
            if json_output:
                if json_schema:
                    # Use enhanced Structured Outputs (recommended)
                    text_format = {
                        "format": {
                            "type": "json_schema",
                            "name": "response",
                            "schema": json_schema,
                            "strict": True
                        }
                    }
                else:
                    # Fall back to basic JSON mode
                    text_format = {"format": {"type": "json_object"}}

            # Ensure prompt contains "json" when JSON output is requested
            input_prompt = prompt
            if json_output and "json" not in prompt.lower():
                input_prompt = f"{prompt}\n\nPlease provide your response in JSON format."
            
            # Build the request parameters
            request_params = {
                "model": OPENAI_MODEL,
                "input": input_prompt,
                "instructions": system_prompt if not (json_output and not json_schema) else system_prompt + JSON_SYSTEM_PROMPT,
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            }
            
            # Add text format if JSON output is requested
            if text_format:
                request_params["text"] = text_format
                
            # Add previous response ID for conversation continuity
            if previous_response_id:
                request_params["previous_response_id"] = previous_response_id
                
            # Add tools if provided (e.g., web search, file search)
            if tools:
                request_params["tools"] = tools

            # Call the Responses API
            response = client.responses.create(**request_params)
            
            # Track token usage
            if hasattr(response, 'usage') and response.usage:
                # Check if this is the new responses API or old chat completions
                if hasattr(response.usage, 'total_tokens'):
                    token_counter.add_tokens(response.usage.total_tokens)
                else:
                    # Fallback for newer API versions that separate input/output tokens
                    input_tokens = getattr(response.usage, 'input_tokens', 0)
                    output_tokens = getattr(response.usage, 'output_tokens', 0)
                    total_tokens = input_tokens + output_tokens
                    token_counter.add_tokens(total_tokens)
            
            # With Structured Outputs, no manual JSON validation needed!
            # The Responses API guarantees valid JSON when using schemas
            
            if return_response_id:
                return response.output_text, response.id
            else:
                return response.output_text
            
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                logger.error(f"Error generating LLM content with OpenAI Responses API (attempt {attempt + 1}): {e}")
                time.sleep(2 ** (attempt + 1))
            else:
                logger.error(f"Failed to generate LLM content with OpenAI Responses API after {MAX_RETRIES} attempts: {e}")
                error_msg = "Error: Unable to generate LLM content with OpenAI Responses API after multiple attempts."
                if return_response_id:
                    return error_msg, None
                else:
                    return error_msg

def call_Anthropic_API(
    prompt: str, 
    system_prompt: str, 
    use_web_search: bool = False,
    structured_output: bool = False
) -> str:
    """
    Calls the Anthropic Claude API.

    Args:
        prompt (str): The user prompt to send to the API.
        system_prompt (str): The system-level instructions for the API.
        use_web_search (bool): Enable web search tool for research tasks.
        structured_output (bool): Request more structured, consistent output.

    Returns:
        str: The generated text from Claude.

    Raises:
        Exception: If the API call fails after the maximum retries.
    """
    max_tokens = 4000  # Maximum number of tokens for the response
    temperature = 1    # Controls randomness of the output

    client = Anthropic()

    # Build tools array for Claude
    tools = []
    if use_web_search:
        tools.append({
            "type": "web_search_20250305",
            "name": "web_search", 
            "max_uses": 3  # Limit searches for cost control
        })

    # Prepare request parameters
    request_params = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt,
        "messages": [
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
    }

    # Add tools if specified
    if tools:
        request_params["tools"] = tools

    # Enhance system prompt for structured output if requested
    if structured_output:
        request_params["system"] = f"{system_prompt}\n\nPlease provide well-structured, organized output with clear sections and formatting."

    for attempt in range(MAX_RETRIES):
        try:
            logger.debug(f"Claude API call with web_search={use_web_search}")
            
            message = client.messages.create(**request_params)
            
            # Track token usage - Updated for new Claude API structure
            if hasattr(message, 'usage') and message.usage:
                # New Claude API structure: usage has input_tokens + output_tokens
                input_tokens = getattr(message.usage, 'input_tokens', 0)
                output_tokens = getattr(message.usage, 'output_tokens', 0)
                total_tokens = input_tokens + output_tokens
                logger.debug(f"Claude tokens - Input: {input_tokens}, Output: {output_tokens}, Total: {total_tokens}")
                token_counter.add_tokens(total_tokens)
            
            # Handle Claude refusal responses
            if message.stop_reason == "refusal":
                logger.warning("Claude refused to generate content for safety reasons")
                return "Error: Content generation was declined for safety reasons. Please try rephrasing your request."
            
            # Handle tool use responses
            if message.stop_reason == "tool_use":
                logger.info("Claude used tools (web search) to enhance response")
            
            logger.debug(f"Claude API response: {message.content}")
            logger.debug(f"Stop reason: {message.stop_reason}")
            
            # Extract and concatenate text from the response
            return_text = ' '.join(block.text for block in message.content if hasattr(block, 'text'))
            logger.debug(f"Claude API return text: {return_text}")

            return return_text
            
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                logger.error(f"Error generating LLM content with Claude (attempt {attempt + 1}): {e}")
                time.sleep(2 ** (attempt + 1))
            else:
                logger.error(f"Failed to generate LLM content with Claude after {MAX_RETRIES} attempts: {e}")
                return "Error: Unable to generate LLM content with Claude after multiple attempts."
            
def get_total_token_usage() -> int:
    """
    Retrieve the total tokens used across all API calls.

    Returns:
        int: Total tokens count.
    """
    return token_counter.get_total_tokens()