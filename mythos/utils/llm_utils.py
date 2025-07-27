import os
import time
import json
import requests
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Literal, Union, Tuple
from mythos.config.settings import (
    OPENAI_API_KEY, ANTHROPIC_API_KEY,
    OPENAI_BASE_URL, ANTHROPIC_BASE_URL,
    FAST_MODEL, MEDIUM_MODEL, BIG_MODEL,
    PLANNING_SYSTEM_PROMPT, MAX_RETRIES, STANDARD_TIMEOUT,
    CONCEPT_TIMEOUT, LLM_CONFIG
)
from mythos.utils.logger import get_logger
from mythos.utils.token_counter import TokenCounter

# Import UI utilities for user feedback
from mythos.utils.ui_utils import print_thinking

logger = get_logger(__name__)
token_counter = TokenCounter()

# Exception Classes
class LLMError(Exception):
    """Base exception for LLM-related errors"""
    pass

class ProviderError(LLMError):
    """Provider-specific API errors"""
    pass

class ConfigurationError(LLMError):
    """Configuration or setup errors"""
    pass

class ContentRefusalError(LLMError):
    """Raised when content is refused due to safety policies"""
    pass

def call_llm(
    prompt: str,
    system_prompt: str = PLANNING_SYSTEM_PROMPT,
    tier: Literal["fast", "medium", "big"] = "medium",
    json_output: bool = False,
    json_schema: Optional[Dict[str, Any]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    thinking_mode: Optional[Literal["fast", "extended"]] = None,
    temperature: float = 1.0,
    max_tokens: int = 4000,
    **kwargs
) -> str:
    """Unified interface for all LLM providers and tiers
    
    This function provides a clean, consistent interface for calling any LLM provider
    while handling provider-specific differences internally.
    
    Args:
        prompt: The user prompt/question to send to the LLM
        system_prompt: System instructions that define the LLM's role and behavior
        tier: Model performance tier - determines which model is used
        json_output: Whether to request structured JSON output
        json_schema: JSON schema for strict structured output (OpenAI only)
        tools: Tool definitions for function calling capabilities
        thinking_mode: Reasoning mode for supported models ("fast" or "extended")
        temperature: Randomness level (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in the response
        **kwargs: Additional provider-specific parameters
        
    Returns:
        Generated text response from the LLM
        
    Raises:
        ConfigurationError: Missing API keys or invalid configuration
        ProviderError: API communication or provider-specific errors
        ContentRefusalError: Content was refused due to safety policies
        ValueError: Invalid tier or parameter values
    """
    # Show thinking indicator immediately when LLM call starts
    print_thinking("AI is processing...")
    
    # Map tier names to configured model providers and names
    tier_models = {
        "fast": FAST_MODEL,
        "medium": MEDIUM_MODEL,
        "big": BIG_MODEL
    }
    
    if tier not in tier_models:
        raise ValueError(f"Invalid tier '{tier}'. Must be one of: {list(tier_models.keys())}")
    
    provider, model_name = tier_models[tier]
    
    try:
        logger.info(f"Calling {provider}:{model_name} for tier '{tier}'")
        
        # Route to appropriate provider implementation
        if provider == "openai":
            result = _call_openai(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model_name,
                json_output=json_output,
                json_schema=json_schema,
                tools=tools,
                thinking_mode=thinking_mode,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        elif provider == "anthropic":
            result = _call_anthropic(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model_name,
                json_output=json_output,
                json_schema=json_schema,
                tools=tools,
                thinking_mode=thinking_mode,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        logger.debug(f"LLM call successful, response length: {len(result)}")
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error calling {provider}: {e}")
        raise ProviderError(f"Failed to connect to {provider}: {e}")
    except ContentRefusalError:
        # Content refusals should not be retried - re-raise immediately
        raise
    except Exception as e:
        logger.error(f"Unexpected error in LLM call: {e}")
        raise LLMError(f"LLM call failed: {e}")

def _call_openai(
    prompt: str,
    system_prompt: str,
    model: str,
    json_output: bool = False,
    json_schema: Optional[Dict[str, Any]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    thinking_mode: Optional[Literal["fast", "extended"]] = None,
    temperature: float = 1.0,
    max_tokens: int = 4000,
    **kwargs
) -> str:
    """Call OpenAI Responses API as specified in .cursorrules
    
    Uses the official OpenAI Responses API format with proper structured outputs,
    reasoning configuration, and error handling.
    """
    
    if not OPENAI_API_KEY:
        raise ConfigurationError("OPENAI_API_KEY environment variable is required")
    
    # Build request payload according to Responses API specification (.cursorrules)
    payload = {
        "model": model,
        "input": prompt,
        "temperature": temperature,
        "stream": False,
        "store": False  # Don't store responses for privacy
    }
    
    # Add system instructions using the instructions parameter
    if system_prompt:
        payload["instructions"] = system_prompt
    
    # Set max_output_tokens (Responses API parameter name)
    if max_tokens:
        payload["max_output_tokens"] = max_tokens
    
    # Configure JSON output using the text parameter (.cursorrules specification)
    if json_output:
        if json_schema:
            # Structured outputs with strict schema validation
            payload["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": "response_schema", 
                    "schema": {
                        **json_schema,
                        "additionalProperties": False  # Required for strict mode
                    },
                    "strict": True  # Ensures 100% adherence to schema
                }
            }
        else:
            # Basic JSON object mode without strict schema
            payload["text"] = {"format": {"type": "json_object"}}
    
    # Configure reasoning for o-series models (o1, o3, o4)
    if any(reasoning_model in model for reasoning_model in ["o1", "o3", "o4"]):
        if thinking_mode == "extended":
            payload["reasoning"] = {"effort": "high"}
        elif thinking_mode == "fast":
            payload["reasoning"] = {"effort": "medium"}
    
    # Add function calling tools if provided
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"  # Let model decide when to use tools
    
    # Set appropriate timeout based on operation complexity
    timeout = CONCEPT_TIMEOUT if "concept" in prompt.lower() else STANDARD_TIMEOUT
    
    # Execute API call with exponential backoff retry logic
    for attempt in range(MAX_RETRIES):
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Log the exact request we're sending (for debugging)
            logger.debug(f"OpenAI API Request:")
            logger.debug(f"  URL: https://api.openai.com/v1/responses")
            logger.debug(f"  Headers: {headers}")
            logger.debug(f"  Payload: {payload}")
            
            # Use the correct Responses API endpoint (.cursorrules)
            response = requests.post(
                "https://api.openai.com/v1/responses",
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            # Log the exact response we get back (for debugging)
            logger.debug(f"OpenAI API Response:")
            logger.debug(f"  Status Code: {response.status_code}")
            logger.debug(f"  Headers: {dict(response.headers)}")
            logger.debug(f"  Raw Text: {response.text}")
            
            # Check for HTTP errors
            if response.status_code != 200:
                error_msg = f"OpenAI Responses API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise ProviderError(error_msg)
            
            result = response.json()
            logger.debug(f"Parsed JSON: {result}")
            
            # Check for API-level errors in response
            if result.get("error"):
                error_msg = f"OpenAI Responses API error: {result['error']}"
                logger.error(error_msg)
                raise ProviderError(error_msg)
            
            # Handle refusal detection for safety policies (.cursorrules)
            if "refusal" in result and result["refusal"]:
                raise ContentRefusalError(f"Content generation refused: {result['refusal']}")
            
            # Extract content from successful response
            content = ""
            if result.get("status") == "completed":
                # Primary method: get content from output_text field (.cursorrules)
                content = result.get("output_text", "")
                
                # Fallback: extract from output array structure
                if not content:
                    output = result.get("output", [])
                    if output and len(output) > 0:
                        first_output = output[0]
                        if first_output.get("type") == "message":
                            message_content = first_output.get("content", [])
                            if message_content and len(message_content) > 0:
                                content = message_content[0].get("text", "")
            else:
                error_msg = f"OpenAI Responses API failed with status: {result.get('status', 'unknown')}"
                logger.error(error_msg)
                raise ProviderError(error_msg)
            
            # Check for empty response before returning (.cursorrules best practices)
            if not content or content.strip() == "":
                raise ProviderError("OpenAI returned empty response - likely service issue")
            
            # Track token usage for cost monitoring and optimization
            if "usage" in result:
                usage = result["usage"]
                total_tokens = usage.get("total_tokens", 0)
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                reasoning_tokens = usage.get("output_tokens_details", {}).get("reasoning_tokens", 0)
                
                logger.debug(f"OpenAI tokens - Input: {input_tokens}, "
                           f"Output: {output_tokens}, Reasoning: {reasoning_tokens}, Total: {total_tokens}")
                token_counter.add_tokens(total_tokens)
            
            return content
            
        except ContentRefusalError:
            # Don't retry content refusals - re-raise immediately
            raise
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                # Exponential backoff: wait 2, 4, 8 seconds between retries
                wait_time = 2 ** (attempt + 1)
                logger.warning(f"OpenAI API call failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                raise ProviderError(f"OpenAI Responses API failed after {MAX_RETRIES} attempts: {e}")

def _call_anthropic(
    prompt: str,
    system_prompt: str,
    model: str,
    json_output: bool = False,
    json_schema: Optional[Dict[str, Any]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    thinking_mode: Optional[Literal["fast", "extended"]] = None,
    temperature: float = 1.0,
    max_tokens: int = 4000,
    **kwargs
) -> str:
    """Call Anthropic Messages API as specified in .cursorrules
    
    Supports Claude 4 models with extended thinking, tool use, and proper
    refusal handling according to .cursorrules specifications.
    """
    
    if not ANTHROPIC_API_KEY:
        raise ConfigurationError("ANTHROPIC_API_KEY environment variable is required")
    
    # Build base request payload for Messages API (.cursorrules)
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    # Add any additional provider-specific parameters
    payload.update(kwargs)
    
    # Configure JSON output through system prompt enhancement
    if json_output:
        if json_schema:
            # Include the specific JSON schema in the system prompt for Anthropic
            import json as json_module
            schema_str = json_module.dumps(json_schema, indent=2)
            payload["system"] += f"\n\nRespond with valid JSON only following this exact schema:\n{schema_str}\n\nEnsure all required fields are present and the JSON is properly formatted."
        else:
            payload["system"] += "\n\nRespond with valid JSON only. Ensure all JSON is properly formatted and valid."
    
    # Configure extended thinking for Claude 4 and 3.7 models (.cursorrules)
    if thinking_mode == "extended":
        # Check if this is a Claude 4 or 3.7 model that supports native extended thinking
        if any(claude_model in model for claude_model in ["claude-opus-4", "claude-sonnet-4", "claude-3-7"]):
            # Native extended thinking configuration for Claude 4/3.7
            payload["thinking"] = {
                "type": "enabled",
                "budget_tokens": int(max_tokens * 0.6)  # 40-60% of max_tokens as recommended
            }
        else:
            # Fallback: enhance system prompt for older Claude models
            payload["system"] += ("\n\nTake time to think through this step by step. "
                                "Use extended reasoning to analyze the problem thoroughly.")
    
    # Add function calling tools if provided
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = {"type": "auto"}
    
    # Set appropriate timeout based on operation complexity
    timeout = CONCEPT_TIMEOUT if "concept" in prompt.lower() else STANDARD_TIMEOUT
    
    # Execute API call with exponential backoff retry logic
    for attempt in range(MAX_RETRIES):
        try:
            # Headers as specified in .cursorrules
            headers = {
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",  # Current stable API version
                "content-type": "application/json"
            }
            
            # Add beta header for interleaved thinking with tools if needed
            if thinking_mode == "extended" and tools:
                headers["anthropic-beta"] = "interleaved-thinking-2025-05-14"
            
            # Log the exact request we're sending (for debugging)
            logger.debug(f"Anthropic API Request:")
            logger.debug(f"  URL: https://api.anthropic.com/v1/messages")
            logger.debug(f"  Headers: {headers}")
            logger.debug(f"  Payload: {payload}")
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            # Log the exact response we get back (for debugging)
            logger.debug(f"Anthropic API Response:")
            logger.debug(f"  Status Code: {response.status_code}")
            logger.debug(f"  Headers: {dict(response.headers)}")
            logger.debug(f"  Raw Text: {response.text}")
            
            # Check for HTTP errors
            if response.status_code != 200:
                error_msg = f"Anthropic API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise ProviderError(error_msg)
            
            result = response.json()
            logger.debug(f"Parsed JSON: {result}")
            
            # Check for refusal using stop_reason first (2025 API format)
            if result.get("stop_reason") == "refusal":
                raise ContentRefusalError("Content generation was declined for safety reasons")
            
            # Handle content refusal detection (.cursorrules pattern)
            content_blocks = result.get("content", [])
            text_content = ""
            
            # Check for refusal patterns in content (fallback for older API responses)
            for block in content_blocks:
                # Handle both official API format {"type": "text", "text": "..."} and test format {"text": "..."}
                if block.get("type") == "text" or (block.get("type") is None and "text" in block):
                    block_text = block.get("text", "")
                    
                    # Check for common refusal patterns (.cursorrules)
                    refusal_indicators = [
                        "I can't assist with",
                        "I cannot help with",
                        "I'm not able to",
                        "I don't feel comfortable",
                        "That request could be harmful"
                    ]
                    
                    if any(indicator in block_text for indicator in refusal_indicators):
                        raise ContentRefusalError(f"Content generation refused: {block_text}")
                    
                    text_content += block_text
                elif block.get("type") == "thinking":
                    # Extended thinking block - skip but could log for debugging
                    logger.debug("Received thinking block from Claude (extended reasoning)")
                    continue
                elif block.get("type") == "tool_use":
                    # Tool use block - would need special handling in tool-enabled scenarios
                    logger.debug(f"Received tool use block: {block.get('name', 'unknown')}")
                    continue

            # Check for empty response before returning (.cursorrules best practices)
            if not text_content or text_content.strip() == "":
                raise ProviderError("Anthropic returned empty response - likely service issue")
            
            # Extract JSON from markdown code blocks if present (Claude often wraps JSON in ```json blocks)
            if json_output and text_content.strip().startswith("```"):
                import re
                # Extract content between ```json and ``` or ``` and ```
                json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text_content, re.DOTALL)
                if json_match:
                    text_content = json_match.group(1).strip()
                    logger.debug("Extracted JSON from markdown code blocks")

            # Track token usage for cost monitoring and optimization
            if "usage" in result:
                usage = result["usage"]
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                total_tokens = input_tokens + output_tokens
                
                logger.debug(f"Anthropic tokens - Input: {input_tokens}, "
                           f"Output: {output_tokens}, Total: {total_tokens}")
                token_counter.add_tokens(total_tokens)
            
            return text_content
            
        except ContentRefusalError:
            # Don't retry content refusals - re-raise immediately
            raise
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                # Exponential backoff: wait 2, 4, 8 seconds between retries
                wait_time = 2 ** (attempt + 1)
                logger.warning(f"Anthropic API call failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                raise ProviderError(f"Anthropic API failed after {MAX_RETRIES} attempts: {e}")

# Backward compatibility functions for legacy code
def call_OpenAI_API(
    input: Union[str, List[Dict[str, Any]]],
    json_output: bool = False,
    json_schema: Optional[Dict[str, Any]] = None,
    previous_response_id: Optional[str] = None,
    tools: Optional[list] = None,
    return_response_id: bool = False
) -> Union[str, Tuple[str, str]]:
    """Legacy OpenAI function - redirects to unified interface
    
    Maintained for backward compatibility with existing code.
    New code should use call_llm() directly.
    """
    
    # Convert legacy input formats to new interface
    if isinstance(input, str):
        prompt = input
        system_prompt = PLANNING_SYSTEM_PROMPT
    elif isinstance(input, list):
        # Extract system and user messages from message list
        system_prompt = ""
        prompt = ""
        for msg in input:
            if msg.get("role") == "system":
                system_prompt = msg.get("content", "")
            elif msg.get("role") == "user":
                prompt = msg.get("content", "")
    else:
        raise ValueError("Input must be string or list of messages")
    
    try:
        result = call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            tier="medium",  # Use medium tier for legacy calls
            json_output=json_output,
            json_schema=json_schema,
            tools=tools
        )
        
        # Return format depends on legacy expectation
        if return_response_id:
            return result, "legacy_response_id"
        else:
            return result
            
    except Exception as e:
        error_msg = f"Error: Unable to generate LLM content with OpenAI API: {e}"
        if return_response_id:
            return error_msg, None
        else:
            return error_msg

def call_Anthropic_API(
    prompt: str, 
    system_prompt: str = PLANNING_SYSTEM_PROMPT,
    use_web_search: bool = False,
    structured_output: bool = False,
    thinking_mode: bool = False,
    thinking_budget_tokens: int = 4000
) -> str:
    """Legacy Anthropic function - redirects to unified interface
    
    Maintained for backward compatibility with existing code.
    New code should use call_llm() directly.
    """
    
    # Convert legacy web search parameter to tools format
    tools = None
    if use_web_search:
        tools = [{
            "type": "web_search_20250305",
            "name": "web_search", 
            "max_uses": 3
        }]
    
    # Convert legacy thinking mode boolean to new format
    thinking_param = "extended" if thinking_mode else None
    
    try:
        return call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            tier="big",  # Use big tier for legacy Anthropic calls
            json_output=structured_output,
            tools=tools,
            thinking_mode=thinking_param
        )
    except Exception as e:
        raise ContentRefusalError(f"Unable to generate LLM content with Claude: {e}")

# Helper functions
def create_messages(prompt: str, system_prompt: Optional[str] = None) -> List[Dict[str, Any]]:
    """Helper function to convert prompt + system_prompt to message format.
    
    Useful for preparing message arrays for APIs that expect chat format.
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    return messages

def get_total_token_usage() -> int:
    """Retrieve the total tokens used across all API calls.
    
    Useful for monitoring costs and usage patterns across the application.
    """
    return token_counter.get_total_tokens()

def _has_refusal(response) -> bool:
    """Legacy function for backward compatibility
    
    Simplified implementation - new code should catch ContentRefusalError instead.
    """
    return False