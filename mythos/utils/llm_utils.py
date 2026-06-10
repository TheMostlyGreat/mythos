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
    CONCEPT_TIMEOUT, ENABLE_PROMPT_CACHING, DEFAULT_THINKING_BUDGET,
    ENABLE_INTERLEAVED_THINKING, DEFAULT_REASONING_EFFORT, DEFAULT_VERBOSITY
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
    thinking_budget: Optional[int] = None,
    enable_caching: bool = True,
    temperature: float = 1.0,
    max_tokens: int = 4000,
    **kwargs
) -> str:
    """Unified interface for all LLM providers and tiers (2025 Best Practices)

    This function provides a clean, consistent interface for calling any LLM provider
    while handling provider-specific differences internally. Implements latest best practices:
    - Prompt caching for Anthropic (up to 90% cost savings)
    - Extended thinking budgets for Claude 3.7/4.x
    - Structured outputs with proper parallel_tool_calls handling
    - Specific model versions for consistency

    Args:
        prompt: The user prompt/question to send to the LLM
        system_prompt: System instructions that define the LLM's role and behavior
        tier: Model performance tier - determines which model is used
        json_output: Whether to request structured JSON output
        json_schema: JSON schema for strict structured output
        tools: Tool definitions for function calling capabilities
        thinking_mode: Reasoning mode for supported models ("fast" or "extended")
        thinking_budget: Thinking budget in tokens (min: 1024, max: 128000) for Claude extended thinking
        enable_caching: Enable prompt caching for Anthropic (default: True)
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
                thinking_budget=thinking_budget or DEFAULT_THINKING_BUDGET,
                enable_caching=enable_caching and ENABLE_PROMPT_CACHING,
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
    """Call OpenAI Chat Completions API (the actual official API)

    Uses the official OpenAI Chat Completions API endpoint with proper structured outputs,
    reasoning configuration, and error handling.
    """

    if not OPENAI_API_KEY:
        raise ConfigurationError("OPENAI_API_KEY environment variable is required")

    # Build messages array for Chat Completions API
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    # Build request payload according to Chat Completions API specification
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    # Set max tokens parameter (GPT-5 uses different parameter name)
    if max_tokens:
        # GPT-5 and newer models use max_completion_tokens
        if "gpt-5" in model or "o3" in model or "o4" in model:
            payload["max_completion_tokens"] = max_tokens
        else:
            # GPT-4o and older use max_tokens
            payload["max_tokens"] = max_tokens

    # Configure JSON output using response_format parameter
    if json_output:
        if json_schema:
            # Structured outputs with strict schema validation
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
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
            payload["response_format"] = {"type": "json_object"}

    # Add function calling tools if provided
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"  # Let model decide when to use tools

    # BEST PRACTICE (2025): Disable parallel tool calls when using structured outputs
    # Structured Outputs is NOT compatible with parallel function calls
    if json_output and json_schema and tools:
        payload["parallel_tool_calls"] = False
        logger.debug("Disabled parallel_tool_calls for structured outputs compatibility")

    # GPT-5 specific parameters (if using gpt-5 model)
    if "gpt-5" in model:
        payload["reasoning_effort"] = DEFAULT_REASONING_EFFORT
        payload["verbosity"] = DEFAULT_VERBOSITY
        logger.debug(f"GPT-5 parameters - reasoning_effort: {DEFAULT_REASONING_EFFORT}, verbosity: {DEFAULT_VERBOSITY}")

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
            logger.debug(f"  URL: https://api.openai.com/v1/chat/completions")
            logger.debug(f"  Headers: {headers}")
            logger.debug(f"  Payload: {payload}")

            # Use the correct Chat Completions API endpoint
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
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
                error_msg = f"OpenAI Chat Completions API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise ProviderError(error_msg)

            result = response.json()
            logger.debug(f"Parsed JSON: {result}")

            # Check for API-level errors in response
            if result.get("error"):
                error_msg = f"OpenAI Chat Completions API error: {result['error']}"
                logger.error(error_msg)
                raise ProviderError(error_msg)

            # Extract content from successful response
            choices = result.get("choices", [])
            if not choices:
                raise ProviderError("OpenAI returned no choices in response")

            first_choice = choices[0]
            finish_reason = first_choice.get("finish_reason")

            # Handle content refusal detection
            if finish_reason == "content_filter":
                raise ContentRefusalError("Content generation refused due to content filter")

            message = first_choice.get("message", {})

            # Check for refusal in message
            if message.get("refusal"):
                raise ContentRefusalError(f"Content generation refused: {message['refusal']}")

            content = message.get("content", "")

            # Check for empty response before returning
            if not content or content.strip() == "":
                raise ProviderError("OpenAI returned empty response - likely service issue")

            # Track token usage for cost monitoring and optimization
            if "usage" in result:
                usage = result["usage"]
                total_tokens = usage.get("total_tokens", 0)
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)

                logger.debug(f"OpenAI tokens - Prompt: {prompt_tokens}, "
                           f"Completion: {completion_tokens}, Total: {total_tokens}")
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
                raise ProviderError(f"OpenAI Chat Completions API failed after {MAX_RETRIES} attempts: {e}")

def _call_anthropic(
    prompt: str,
    system_prompt: str,
    model: str,
    json_output: bool = False,
    json_schema: Optional[Dict[str, Any]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    thinking_mode: Optional[Literal["fast", "extended"]] = None,
    thinking_budget: int = DEFAULT_THINKING_BUDGET,
    enable_caching: bool = True,
    temperature: float = 1.0,
    max_tokens: int = 4000,
    **kwargs
) -> str:
    """Call Anthropic Messages API with 2025 Best Practices

    Implements latest Anthropic features (Oct 2025):
    - Prompt caching for up to 90% cost savings
    - Extended thinking with configurable budgets
    - Interleaved thinking with tool calls (Claude 4+)
    - Claude 3.7 hybrid reasoning support
    """
    
    if not ANTHROPIC_API_KEY:
        raise ConfigurationError("ANTHROPIC_API_KEY environment variable is required")

    # Build base request payload for Messages API with prompt caching
    # BEST PRACTICE (2025): Use cache_control to mark cacheable content
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    # Add system prompt with caching if enabled
    if system_prompt:
        if enable_caching:
            # Cache system prompt (saves up to 90% on repeated calls)
            payload["system"] = [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}  # Mark for caching
                }
            ]
        else:
            payload["system"] = system_prompt
    
    # Add any additional provider-specific parameters
    payload.update(kwargs)
    
    # Configure JSON output through system prompt enhancement
    if json_output:
        if json_schema:
            # Include the specific JSON schema in the system prompt for Anthropic
            import json as json_module
            schema_str = json_module.dumps(json_schema, indent=2)
            json_instruction = f"\n\nRespond with valid JSON only following this exact schema:\n{schema_str}\n\nEnsure all required fields are present and the JSON is properly formatted."
        else:
            json_instruction = "\n\nRespond with valid JSON only. Ensure all JSON is properly formatted and valid."

        # Append to system prompt (handle both string and list formats)
        if isinstance(payload.get("system"), list):
            # Caching enabled: system is a list with cache_control
            payload["system"].append({
                "type": "text",
                "text": json_instruction.strip()
            })
        else:
            # Caching disabled: system is a string
            payload["system"] += json_instruction
    
    # Configure extended thinking for Claude 4 models (October 2025)
    if thinking_mode == "extended":
        # Check if this is a Claude 4 model that supports native extended thinking
        if any(claude_model in model for claude_model in ["claude-opus-4", "claude-sonnet-4"]):
            # Native extended thinking configuration for Claude 4
            budget = max(1024, min(thinking_budget, 128000))  # Clamp to valid range
            payload["thinking"] = {
                "type": "enabled",
                "budget_tokens": budget
            }
            logger.debug(f"Extended thinking enabled with budget: {budget} tokens")
        else:
            # Fallback: enhance system prompt for older Claude models
            if isinstance(payload.get("system"), list):
                payload["system"][0]["text"] += ("\n\nTake time to think through this step by step. "
                                                  "Use extended reasoning to analyze the problem thoroughly.")
            else:
                if payload.get("system"):
                    payload["system"] += ("\n\nTake time to think through this step by step. "
                                        "Use extended reasoning to analyze the problem thoroughly.")
    
    # Add function calling tools if provided with caching support
    if tools:
        if enable_caching:
            # Cache tool definitions (saves tokens on repeated calls)
            cached_tools = []
            for i, tool in enumerate(tools):
                # Add cache_control to last tool (up to 4 cache breakpoints allowed)
                if i == len(tools) - 1:
                    tool_with_cache = {**tool, "cache_control": {"type": "ephemeral"}}
                    cached_tools.append(tool_with_cache)
                else:
                    cached_tools.append(tool)
            payload["tools"] = cached_tools
        else:
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
            
            # Add beta headers for latest features (October 2025)
            beta_features = []
            if thinking_mode == "extended" and tools and ENABLE_INTERLEAVED_THINKING:
                beta_features.append("interleaved-thinking-2025-05-14")
            if enable_caching:
                beta_features.append("prompt-caching-2024-07-31")
            if beta_features:
                headers["anthropic-beta"] = ",".join(beta_features)
            
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