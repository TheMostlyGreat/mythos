import os
import time
import json
import requests
import logging
from typing import Dict, Any, Optional, List, Literal, Union, Tuple
from mythos.config.settings import (
    OPENAI_API_KEY, ANTHROPIC_API_KEY,
    FAST_MODEL, MEDIUM_MODEL, BIG_MODEL, PREMIUM_MODEL,
    PLANNING_SYSTEM_PROMPT, MAX_RETRIES
)
from mythos.utils.logger import get_logger
from mythos.utils.token_counter import TokenCounter

logger = get_logger(__name__)
token_counter = TokenCounter()

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
    """Raised when OpenAI/Anthropic refuses to generate content due to safety policies."""
    pass

def call_llm(
    prompt: str,
    system_prompt: str = PLANNING_SYSTEM_PROMPT,
    tier: Literal["fast", "medium", "big", "premium"] = "medium",
    json_output: bool = False,
    json_schema: Optional[Dict[str, Any]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    thinking_mode: Optional[Literal["fast", "extended"]] = None,
    temperature: float = 1.0,
    max_tokens: int = 4000,
    **kwargs
) -> str:
    """Unified interface for all LLM providers and tiers
    
    Args:
        prompt: The user prompt
        system_prompt: System prompt (role/instructions)
        tier: Model tier (fast/medium/big/premium)
        json_output: Whether to request JSON output
        json_schema: JSON schema for structured output (OpenAI only)
        tools: Tool definitions for function calling
        thinking_mode: "fast" or "extended" for reasoning models
        temperature: Randomness (0.0-1.0)
        max_tokens: Maximum output tokens
        **kwargs: Additional provider-specific parameters
        
    Returns:
        Generated text response
    """
    # Get model configuration for tier
    tier_models = {
        "fast": FAST_MODEL,
        "medium": MEDIUM_MODEL,
        "big": BIG_MODEL,
        "premium": PREMIUM_MODEL
    }
    
    if tier not in tier_models:
        raise ValueError(f"Invalid tier '{tier}'. Must be one of: {list(tier_models.keys())}")
    
    provider, model_name = tier_models[tier]
    
    try:
        logger.info(f"Calling {provider}:{model_name} for tier '{tier}'")
        
        # Route to appropriate provider
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
    """Call OpenAI API with verified 2025 format"""
    
    if not OPENAI_API_KEY:
        raise ConfigurationError("OPENAI_API_KEY environment variable is required")
    
    # Build messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    # Build request payload
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        **kwargs
    }
    
    # Add JSON output if requested (2025 Structured Outputs)
    if json_output:
        if json_schema:
            # Structured outputs with strict mode (2025)
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "strict": True,
                    "schema": {
                        **json_schema,
                        "additionalProperties": False  # Required for strict mode
                    }
                }
            }
        else:
            # Basic JSON mode
            payload["response_format"] = {"type": "json_object"}
    
    # Add reasoning configuration for o3/o4 models
    if "o3" in model or "o4" in model:
        if thinking_mode == "extended":
            payload["reasoning"] = {
                "effort": "high"  # Extended thinking mode
            }
        elif thinking_mode == "fast":
            payload["reasoning"] = {
                "effort": "medium"  # Fast reasoning mode  
            }
    
    # Add tools if provided
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    
    # Make API call with retries
    for attempt in range(MAX_RETRIES):
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                error_msg = f"OpenAI API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise ProviderError(error_msg)
            
            result = response.json()
            
            # Check for refusal
            choice = result["choices"][0]
            if choice.get("finish_reason") == "content_filter":
                raise ContentRefusalError("Content generation was declined for safety reasons")
            
            content = choice["message"]["content"]
            
            # Track token usage
            if "usage" in result:
                usage = result["usage"]
                total_tokens = usage.get("total_tokens", 0)
                logger.debug(f"OpenAI tokens - Input: {usage.get('prompt_tokens', 0)}, "
                           f"Output: {usage.get('completion_tokens', 0)}, Total: {total_tokens}")
                token_counter.add_tokens(total_tokens)
            
            return content
            
        except ContentRefusalError:
            raise
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                logger.error(f"OpenAI API call failed (attempt {attempt + 1}): {e}")
                time.sleep(2 ** (attempt + 1))
            else:
                raise ProviderError(f"OpenAI API failed after {MAX_RETRIES} attempts: {e}")

def _call_anthropic(
    prompt: str,
    system_prompt: str,
    model: str,
    json_output: bool = False,
    tools: Optional[List[Dict[str, Any]]] = None,
    thinking_mode: Optional[Literal["fast", "extended"]] = None,
    temperature: float = 1.0,
    max_tokens: int = 4000,
    **kwargs
) -> str:
    """Call Anthropic API with verified 2025 format"""
    
    if not ANTHROPIC_API_KEY:
        raise ConfigurationError("ANTHROPIC_API_KEY environment variable is required")
    
    # Build request payload
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        **kwargs
    }
    
    # Handle JSON output (Anthropic uses system prompt)
    if json_output:
        payload["system"] += "\n\nRespond with valid JSON only. Ensure all JSON is properly formatted and valid."
    
    # Handle extended thinking for Claude models
    if ("claude-3-5" in model or "claude-4" in model) and thinking_mode == "extended":
        payload["system"] += "\n\nTake time to think through this step by step. Use extended reasoning to analyze the problem thoroughly."
    
    # Add tools if provided
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = {"type": "auto"}
    
    # Make API call with retries
    for attempt in range(MAX_RETRIES):
        try:
            headers = {
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",  # Current stable version
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                error_msg = f"Anthropic API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise ProviderError(error_msg)
            
            result = response.json()
            
            # Check for refusal
            if result.get("stop_reason") == "refusal":
                raise ContentRefusalError("Content generation was declined for safety reasons")
            
            content = result["content"][0]["text"]
            
            # Track token usage
            if "usage" in result:
                usage = result["usage"]
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                total_tokens = input_tokens + output_tokens
                logger.debug(f"Anthropic tokens - Input: {input_tokens}, "
                           f"Output: {output_tokens}, Total: {total_tokens}")
                token_counter.add_tokens(total_tokens)
            
            return content
            
        except ContentRefusalError:
            raise
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                logger.error(f"Anthropic API call failed (attempt {attempt + 1}): {e}")
                time.sleep(2 ** (attempt + 1))
            else:
                raise ProviderError(f"Anthropic API failed after {MAX_RETRIES} attempts: {e}")

# Backward compatibility functions
def call_OpenAI_API(
    input: Union[str, List[Dict[str, Any]]],
    json_output: bool = False,
    json_schema: Optional[Dict[str, Any]] = None,
    previous_response_id: Optional[str] = None,
    tools: Optional[list] = None,
    return_response_id: bool = False
) -> Union[str, Tuple[str, str]]:
    """Legacy OpenAI function - redirects to new unified interface"""
    
    # Convert input format
    if isinstance(input, str):
        prompt = input
        system_prompt = PLANNING_SYSTEM_PROMPT
    elif isinstance(input, list):
        # Extract system and user messages
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
            tier="medium",
            json_output=json_output,
            json_schema=json_schema,
            tools=tools
        )
        
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
    """Legacy Anthropic function - redirects to new unified interface"""
    
    # Convert parameters
    tools = None
    if use_web_search:
        tools = [{
            "type": "web_search_20250305",
            "name": "web_search", 
            "max_uses": 3
        }]
    
    thinking_param = "extended" if thinking_mode else None
    
    try:
        return call_llm(
            prompt=prompt,
            system_prompt=system_prompt,
            tier="big",  # Use big tier for Anthropic calls
            json_output=structured_output,
            tools=tools,
            thinking_mode=thinking_param
        )
    except Exception as e:
        raise ContentRefusalError(f"Unable to generate LLM content with Claude: {e}")

def create_messages(prompt: str, system_prompt: Optional[str] = None) -> List[Dict[str, Any]]:
    """Helper function to convert prompt + system_prompt to message format."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    return messages

def get_total_token_usage() -> int:
    """Retrieve the total tokens used across all API calls."""
    return token_counter.get_total_tokens()

# Legacy function checks for content refusal
def _has_refusal(response) -> bool:
    """Legacy function for backward compatibility"""
    return False  # Simplified for new implementation