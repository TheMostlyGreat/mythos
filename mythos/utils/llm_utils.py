import time
from typing import Optional, Dict, Any, Union, List
from openai import OpenAI
from anthropic import Anthropic
from mythos.config.settings import OPENAI_MODEL, MAX_RETRIES, ANTHROPIC_MODEL, JSON_SYSTEM_PROMPT
from mythos.utils.logger import get_logger
from mythos.utils.token_counter import TokenCounter

logger = get_logger(__name__)
token_counter = TokenCounter()

def _has_refusal(response) -> bool:
    """
    Check for official OpenAI Responses API refusal fields.
    
    Based on the latest OpenAI Responses API documentation (2025), refusals appear as:
    1. Content items with refusal field in message outputs
    2. Specific error conditions related to safety/content policy
    
    Args:
        response: The response object from OpenAI Responses API
        
    Returns:
        True if the response contains an official refusal
    """
    if not response:
        return False
    
    # Check for refusal in output items (Responses API)
    if hasattr(response, 'output') and response.output:
        for item in response.output:
            # Check message-type items for refusal content
            if hasattr(item, 'type') and item.type == 'message':
                if hasattr(item, 'content') and item.content:
                    for content_item in item.content:
                        # Primary refusal detection: official refusal field
                        if hasattr(content_item, 'refusal') and content_item.refusal:
                            return True
                        # Also check if content item itself has a refusal field
                        if hasattr(content_item, 'type') and content_item.type == 'refusal':
                            return True
            
            # Check for explicit refusal output types
            if hasattr(item, 'type') and item.type == 'refusal':
                return True
    
    # Check for safety-related errors that indicate content refusal
    if hasattr(response, 'error') and response.error:
        error_obj = response.error
        if hasattr(error_obj, 'type'):
            # Only specific error types indicate content refusal
            if error_obj.type == 'content_policy_violation':
                return True
        if hasattr(error_obj, 'code'):
            # Specific error codes for refusals
            if error_obj.code in ['content_filter', 'policy_violation']:
                return True
    
    return False

def create_messages(prompt: str, system_prompt: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Helper function to convert prompt + system_prompt to message format.
    
    Args:
        prompt: The user prompt
        system_prompt: Optional system prompt
        
    Returns:
        List of messages in the format expected by the Responses API
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    return messages

def call_OpenAI_API(
    input: List[Dict[str, Any]],
    json_output: bool = False,
    json_schema: Optional[Dict[str, Any]] = None,
    previous_response_id: Optional[str] = None,
    tools: Optional[list] = None,
    return_response_id: bool = False
) -> Union[str, tuple[str, str]]:
    """
    Call OpenAI Responses API using message-based input format.
    
    Args:
        input: List of messages with roles (developer, system, user, assistant)
        json_output: Whether to expect JSON output
        json_schema: Optional JSON schema for Structured Outputs
        previous_response_id: ID from previous response for conversation continuity
        tools: Optional list of tools to enable (e.g., web_search, file_search)
        return_response_id: If True, returns (content, response_id) tuple
    
    Returns:
        If return_response_id is False: The API response as a string
        If return_response_id is True: Tuple of (response_string, response_id)
    """
    max_output_tokens = 4000
    temperature = 1
    client = OpenAI()

    for attempt in range(MAX_RETRIES):
        try:
            # Build request parameters
            request_params = {
                "model": OPENAI_MODEL,
                "input": input,
                "max_output_tokens": max_output_tokens,
                "temperature": temperature,
            }
            
            # Add JSON format if requested
            if json_output:
                if json_schema:
                    # Structured outputs
                    validated_schema = json_schema.copy()
                    if "additionalProperties" not in validated_schema:
                        validated_schema["additionalProperties"] = False
                    
                    request_params["text"] = {
                        "format": {
                            "type": "json_schema",
                            "name": "response",
                            "schema": validated_schema,
                            "strict": True
                        }
                    }
                else:
                    # Basic JSON mode
                    request_params["text"] = {
                        "format": {"type": "json_object"}
                    }
                
            # Add optional parameters
            if previous_response_id:
                request_params["previous_response_id"] = previous_response_id
            if tools:
                request_params["tools"] = tools

            # Call the Responses API
            response = client.responses.create(**request_params)
            
            # Handle refusals according to latest OpenAI Responses API docs
            if _has_refusal(response):
                logger.warning("OpenAI API refused to generate content for safety reasons")
                refusal_msg = "Error: Content generation was declined for safety reasons. Please try rephrasing your request."
                if return_response_id:
                    return refusal_msg, response.id if hasattr(response, 'id') else None
                else:
                    return refusal_msg
            
            # Track token usage
            if hasattr(response, 'usage') and response.usage:
                input_tokens = getattr(response.usage, 'input_tokens', 0)
                output_tokens = getattr(response.usage, 'output_tokens', 0)
                total_tokens = input_tokens + output_tokens
                logger.debug(f"OpenAI Responses API tokens - Input: {input_tokens}, Output: {output_tokens}, Total: {total_tokens}")
                token_counter.add_tokens(total_tokens)
            
            # Get response content
            response_content = response.output_text
            
            if return_response_id:
                return response_content, response.id
            else:
                return response_content
                
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
    structured_output: bool = False,
    thinking_mode: bool = False,
    thinking_budget_tokens: int = 4000
) -> str:
    """
    Calls the Anthropic Claude API.

    Args:
        prompt (str): The user prompt to send to the API.
        system_prompt (str): The system-level instructions for the API.
        use_web_search (bool): Enable web search tool for research tasks.
        structured_output (bool): Request more structured, consistent output.
        thinking_mode (bool): Enable Claude's extended thinking capabilities.
        thinking_budget_tokens (int): Token budget for thinking (min 1024, max < max_tokens).

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

    # Add thinking mode if enabled
    if thinking_mode:
        # Ensure thinking budget is within valid range
        thinking_budget = max(1024, min(thinking_budget_tokens, max_tokens - 100))
        request_params["thinking"] = {
            "type": "enabled",
            "budget_tokens": thinking_budget
        }

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
            
            logger.debug(f"Stop reason: {message.stop_reason}")
            
            # Extract and concatenate text from the response
            return_text = ' '.join(block.text for block in message.content if hasattr(block, 'text'))

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