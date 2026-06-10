# 🚀 **Multi-Tier LLM Implementation Plan**

## **🎯 Architecture Overview**

### **Goal**

Create an elegant, minimal, maximum developer experience system for mixing and matching the best OpenAI and Anthropic models across three performance tiers.

### **Design Principles**

1. **Zero Breaking Changes**: Existing code continues to work unchanged
2. **Maximum DX**: Simple configuration in version-controlled settings
3. **Minimal Code**: Single unified interface for all providers
4. **Correct Implementation**: Based on cursorrules and latest 2025 API documentation
5. **Elegant Abstraction**: Hide provider complexity behind clean interface
6. **Security Best Practice**: Only sensitive data (API keys) in environment variables

---

## **📋 Implementation Steps**

### **Phase 1: Core Infrastructure** (45 minutes)

#### **Step 1.1: Update Configuration** (10 minutes)

```python
# mythos/config/settings.py

import os
from typing import Tuple

# Mix-and-match model configuration - verified 2025 models from cursorrules
FAST_MODEL = ("openai", "gpt-4.1-nano")                       # Ultra-fast + cost-effective
MEDIUM_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")    # Good balance of speed/cost/quality
BIG_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")       # High quality reasoning
PREMIUM_MODEL = ("openai", "gpt-4.1")                         # Latest flagship model (OpenAI)

# Alternative configurations - uncomment to use:

# All OpenAI (latest series from cursorrules)
#FAST_MODEL = ("openai", "gpt-4.1-nano")
#MEDIUM_MODEL = ("openai", "gpt-4.1-mini")
#BIG_MODEL = ("openai", "gpt-4.1")
#PREMIUM_MODEL = ("openai", "o3")

# All Anthropic (Claude 4 and 3.5 series)
#FAST_MODEL = ("anthropic", "claude-3-5-haiku-20241022")
#MEDIUM_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")
#BIG_MODEL = ("anthropic", "claude-sonnet-4-20250514")
#PREMIUM_MODEL = ("anthropic", "claude-opus-4-20250514")

# Reasoning-focused (o-series + Claude 4)
#FAST_MODEL = ("openai", "gpt-4o-mini")
#MEDIUM_MODEL = ("openai", "o3-mini")
#BIG_MODEL = ("anthropic", "claude-3-7-sonnet-20250219")  # Hybrid reasoning
#PREMIUM_MODEL = ("anthropic", "claude-opus-4-20250514")

# Cost-optimized (all fast models)
#FAST_MODEL = ("openai", "gpt-4o-mini")
#MEDIUM_MODEL = ("openai", "gpt-4o-mini")
#BIG_MODEL = ("openai", "gpt-4o")
#PREMIUM_MODEL = ("openai", "gpt-4o")

# API Keys (only sensitive data in environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
```

#### **Step 1.2: Create Unified LLM Interface** (25 minutes)

```python
# mythos/utils/llm_utils.py

import os
import json
import requests
from typing import Dict, Any, Optional, List, Literal
from mythos.config.settings import (
    OPENAI_API_KEY, ANTHROPIC_API_KEY,
    FAST_MODEL, MEDIUM_MODEL, BIG_MODEL, PREMIUM_MODEL, PLANNING_SYSTEM_PROMPT
)

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

    # Route to appropriate provider
    if provider == "openai":
        return _call_openai(
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
        return _call_anthropic(
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
    """Call OpenAI Responses API as specified in cursorrules"""

    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    # Build request payload for Responses API (NOT Chat Completions)
    payload = {
        "model": model,
        "input": prompt,
        "instructions": system_prompt,
        "temperature": temperature,
        "max_tokens": max_tokens,
        **kwargs
    }

    # Add structured outputs for JSON according to cursorrules
    if json_output:
        if json_schema:
            # Structured outputs with strict mode (from cursorrules)
            payload["text"] = {
                "format": {
                    "type": "json_schema",
                    "name": "response_schema",
                    "schema": {
                        **json_schema,
                        "additionalProperties": False  # Required for strict mode
                    },
                    "strict": True  # Ensures 100% adherence
                }
            }
        else:
            # Basic JSON mode
            payload["text"] = {
                "format": {"type": "json"}
            }

    # Add tools if provided
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    # Make API call to Responses API (CORRECT endpoint per cursorrules)
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://api.openai.com/v1/responses",  # Responses API as per cursorrules
        headers=headers,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(f"OpenAI API error {response.status_code}: {response.text}")

    result = response.json()

    # Handle refusal detection (from cursorrules)
    if "refusal" in result and result["refusal"]:
        raise Exception(f"Content refused: {result['refusal']}")

    # Access content via output_text attribute (from cursorrules)
    return result["output_text"]

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
    """Call Anthropic Messages API as specified in cursorrules"""

    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")

    # Build request payload according to cursorrules
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

    # Handle JSON output (Anthropic uses system prompt enhancement)
    if json_output:
        payload["system"] += "\n\nRespond with valid JSON only. Ensure all JSON is properly formatted and valid."

    # Handle extended thinking for Claude 4 and 3.7 models (from cursorrules)
    if thinking_mode == "extended":
        # Check for models with native extended thinking support
        if any(claude_model in model for claude_model in ["claude-opus-4", "claude-sonnet-4", "claude-3-7"]):
            payload["thinking"] = {
                "type": "enabled",
                "budget_tokens": int(max_tokens * 0.5)  # 40-60% of max_tokens as recommended
            }
        else:
            # Fallback for older models
            payload["system"] += "\n\nTake time to think through this step by step. Use extended reasoning to analyze the problem thoroughly."

    # Add tools if provided
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = {"type": "auto"}

    # Make API call with cursorrules headers
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",  # Current stable version from cursorrules
        "content-type": "application/json"
    }

    # Add beta header for interleaved thinking with tools if needed
    if thinking_mode == "extended" and tools:
        headers["anthropic-beta"] = "interleaved-thinking-2025-05-14"

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=payload,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(f"Anthropic API error {response.status_code}: {response.text}")

    result = response.json()

    # Extract content handling thinking blocks (from cursorrules)
    content_blocks = result.get("content", [])
    text_content = ""

    for block in content_blocks:
        if block.get("type") == "text":
            text_content += block.get("text", "")
        elif block.get("type") == "thinking":
            # Skip thinking blocks but could log for debugging
            continue

    return text_content

# Backward compatibility functions
def call_OpenAI_API(prompt, system_prompt=PLANNING_SYSTEM_PROMPT, **kwargs):
    """Legacy function - redirects to new unified interface"""
    return call_llm(prompt, system_prompt, tier="medium", **kwargs)

def call_Anthropic_API(prompt, system_prompt=PLANNING_SYSTEM_PROMPT, **kwargs):
    """Legacy function - redirects to new unified interface"""
    return call_llm(prompt, system_prompt, tier="medium", **kwargs)
```

#### **Step 1.3: Add Error Handling & Logging** (10 minutes)

```python
# Add to mythos/utils/llm_utils.py

import logging

logger = logging.getLogger(__name__)

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
    """Content was refused due to safety policies"""
    pass

# Update call_llm function to add error handling:
def call_llm(prompt: str, **kwargs) -> str:
    try:
        # ... existing code ...
        logger.info(f"Calling {provider}:{model_name} for tier '{tier}'")
        result = # ... API call ...
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
```

---

### **Phase 2: Update Existing Functions** (30 minutes)

#### **Step 2.1: Update Writer Functions** (15 minutes)

```python
# mythos/services/writer.py

from mythos.utils.llm_utils import call_llm

def generate_planning_text(prompt: str, **kwargs) -> str:
    """Generate planning text using MEDIUM tier model"""
    return call_llm(prompt, tier="medium", **kwargs)

def generate_narrative_text(prompt: str, **kwargs) -> str:
    """Generate narrative text using BIG tier model"""
    return call_llm(prompt, tier="big", **kwargs)

def summarize_text(text: str, **kwargs) -> str:
    """Summarize text using FAST tier model"""
    prompt = f"Summarize the following text concisely:\n\n{text}"
    return call_llm(prompt, tier="fast", **kwargs)

def generate_character_list(prompt: str, **kwargs) -> str:
    """Generate character list using MEDIUM tier model"""
    return call_llm(prompt, tier="medium", json_output=True, **kwargs)

def generate_chapter_list(prompt: str, **kwargs) -> str:
    """Generate chapter list using MEDIUM tier model"""
    return call_llm(prompt, tier="medium", json_output=True, **kwargs)

def generate_story_concept(prompt: str, **kwargs) -> str:
    """Generate story concept using MEDIUM tier model"""
    return call_llm(prompt, tier="medium", **kwargs)

def generate_web_enhanced_research(prompt: str, **kwargs) -> str:
    """Generate research using MEDIUM tier model"""
    return call_llm(prompt, tier="medium", **kwargs)
```

#### **Step 2.2: Update Story Builder Direct Calls** (10 minutes)

```python
# Update mythos/services/story_builder.py

# Replace direct API calls with tier-appropriate calls:
# Old: call_OpenAI_API(prompt)
# New: call_llm(prompt, tier="medium")

# Example updates:
def generate_critical_perspectives(self, story_name: str) -> None:
    # ... existing code ...
    response_text = call_llm(prompt, tier="medium", json_output=True)
    # ... rest of function ...

def _generate_single_perspective_template(self, perspective: str, story_context: str) -> str:
    # ... existing code ...
    return call_llm(prompt, tier="medium")
```

#### **Step 2.3: Update Story Questioner** (5 minutes)

```python
# Update mythos/services/story_questioner.py

# Replace API calls with appropriate tiers:
# For quick interactions: tier="fast"
# For complex reasoning: tier="medium"
```

---

### **Phase 3: Comprehensive Testing** (55 minutes)

#### **Step 3.1: Unit Tests** (25 minutes)

```python
# tests/utils/test_llm_utils.py

import pytest
from unittest.mock import patch, MagicMock
from mythos.utils.llm_utils import call_llm, LLMError, ProviderError
from mythos.config.settings import FAST_MODEL, MEDIUM_MODEL, BIG_MODEL, PREMIUM_MODEL

class TestModelConfiguration:
    """Test model tier configuration with verified 2025 models from cursorrules"""

    def test_model_tier_structure(self):
        """Test that all tier models are properly structured"""
        for model_config in [FAST_MODEL, MEDIUM_MODEL, BIG_MODEL, PREMIUM_MODEL]:
            assert isinstance(model_config, tuple)
            assert len(model_config) == 2
            provider, model_name = model_config
            assert provider in ["openai", "anthropic"]
            assert isinstance(model_name, str)
            assert len(model_name) > 0

    def test_verified_cursorrules_models(self):
        """Test that we're using models verified in cursorrules"""
        verified_models = {
            "openai": [
                # GPT-4.1 Series
                "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano",
                # GPT-4o Series
                "gpt-4o", "gpt-4o-mini",
                # Reasoning Models
                "o3", "o3-mini", "o3-pro", "o4-mini", "o1", "o1-mini", "o1-preview",
                # Legacy
                "gpt-4", "gpt-3.5-turbo"
            ],
            "anthropic": [
                # Claude 4 Series (May 2025)
                "claude-opus-4-20250514", "claude-sonnet-4-20250514",
                # Claude 3.7 Series (Hybrid Reasoning)
                "claude-3-7-sonnet-20250219",
                # Claude 3.5 Series (Current Production)
                "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"
            ]
        }

        for model_config in [FAST_MODEL, MEDIUM_MODEL, BIG_MODEL, PREMIUM_MODEL]:
            provider, model_name = model_config
            assert model_name in verified_models[provider], f"Unverified model: {model_name}"

class TestProviderFunctions:
    """Test individual provider functions"""

    @patch('requests.post')
    def test_openai_responses_api(self, mock_post):
        """Test OpenAI Responses API success response handling"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "output_text": "Test response"
        }
        mock_post.return_value = mock_response

        from mythos.utils.llm_utils import _call_openai
        result = _call_openai("test", "system", "gpt-4.1")

        # Verify it used the Responses endpoint (NOT Chat Completions)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.openai.com/v1/responses"
        assert result == "Test response"

        # Verify request structure matches cursorrules
        request_json = kwargs['json']
        assert "input" in request_json  # NOT "messages"
        assert "instructions" in request_json  # NOT "system" message
        assert request_json["model"] == "gpt-4.1"

    @patch('requests.post')
    def test_anthropic_messages_api(self, mock_post):
        """Test Anthropic Messages API success response handling"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"type": "text", "text": "Test response"}]
        }
        mock_post.return_value = mock_response

        from mythos.utils.llm_utils import _call_anthropic
        result = _call_anthropic("test", "system", "claude-3-5-sonnet-20241022")

        # Verify it used the Messages endpoint
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.anthropic.com/v1/messages"
        assert result == "Test response"

    @patch('requests.post')
    def test_structured_outputs_openai(self, mock_post):
        """Test OpenAI structured outputs as specified in cursorrules"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "output_text": '{"test": "value"}'
        }
        mock_post.return_value = mock_response

        from mythos.utils.llm_utils import _call_openai

        schema = {
            "type": "object",
            "properties": {"test": {"type": "string"}},
            "required": ["test"],
            "additionalProperties": False
        }

        result = _call_openai("test", "system", "gpt-4.1", json_output=True, json_schema=schema)

        # Check that request used text.format.json_schema with strict mode
        call_args = mock_post.call_args[1]['json']
        assert "text" in call_args
        assert call_args["text"]["format"]["type"] == "json_schema"
        assert call_args["text"]["format"]["strict"] == True
        assert call_args["text"]["format"]["schema"]["additionalProperties"] == False

class TestErrorHandling:
    """Test error handling and edge cases"""

    @patch('requests.post')
    def test_openai_refusal_handling(self, mock_post):
        """Test OpenAI refusal detection as specified in cursorrules"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "refusal": "I cannot assist with that request."
        }
        mock_post.return_value = mock_response

        from mythos.utils.llm_utils import _call_openai

        with pytest.raises(Exception, match="Content refused"):
            _call_openai("harmful request", "system", "gpt-4.1")

class TestBackwardCompatibility:
    """Test backward compatibility functions"""

    @patch('mythos.utils.llm_utils.call_llm')
    def test_legacy_openai_function(self, mock_call_llm):
        """Test legacy call_OpenAI_API function"""
        mock_call_llm.return_value = "response"

        from mythos.utils.llm_utils import call_OpenAI_API
        result = call_OpenAI_API("test prompt")

        mock_call_llm.assert_called_once_with("test prompt", tier="medium")
        assert result == "response"
```

#### **Step 3.2: Integration Tests** (15 minutes)

```python
# tests/integration/test_llm_integration.py

import pytest
import os
from mythos.utils.llm_utils import call_llm

class TestLLMIntegration:
    """Integration tests requiring actual API keys"""

    @pytest.fixture(autouse=True)
    def check_api_keys(self):
        """Skip tests if API keys are not available"""
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("No API keys available for integration tests")

    @pytest.mark.integration
    def test_fast_tier_integration(self):
        """Test fast tier with real API call"""
        try:
            response = call_llm("Say 'Hello World'", tier="fast", max_tokens=10)
            assert isinstance(response, str)
            assert len(response) > 0
        except Exception as e:
            pytest.fail(f"Fast tier integration test failed: {e}")

    @pytest.mark.integration
    def test_claude_4_extended_thinking(self):
        """Test Claude 4 extended thinking if available"""
        try:
            # Only test if using Claude 4 models
            from mythos.config.settings import PREMIUM_MODEL
            if "claude-opus-4" in PREMIUM_MODEL[1] or "claude-sonnet-4" in PREMIUM_MODEL[1]:
                response = call_llm(
                    "Solve this logic puzzle step by step: If all roses are flowers and some flowers are red, can we conclude that some roses are red?",
                    tier="premium",
                    thinking_mode="extended",
                    max_tokens=200
                )
                assert isinstance(response, str)
                assert len(response) > 50  # Should have detailed reasoning
        except Exception as e:
            pytest.fail(f"Claude 4 extended thinking test failed: {e}")
```

#### **Step 3.3: API Compliance Tests** (10 minutes)

```python
# tests/api/test_api_compliance.py

import pytest
from unittest.mock import patch, MagicMock
from mythos.utils.llm_utils import _call_openai, _call_anthropic

class TestAPIsCompliance:
    """Test API compliance with cursorrules specifications"""

    @patch('requests.post')
    def test_openai_uses_responses_api(self, mock_post):
        """Verify OpenAI calls use Responses API, NOT Chat Completions API"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "output_text": "test"
        }
        mock_post.return_value = mock_response

        _call_openai("test", "system", "gpt-4.1")

        # Must use Responses endpoint
        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.openai.com/v1/responses"

        # Must use input/instructions format, NOT messages
        request_json = kwargs['json']
        assert "input" in request_json
        assert "instructions" in request_json
        assert "messages" not in request_json  # This would be Chat Completions

    @patch('requests.post')
    def test_anthropic_headers_compliance(self, mock_post):
        """Verify Anthropic uses correct headers from cursorrules"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"type": "text", "text": "test"}]
        }
        mock_post.return_value = mock_response

        _call_anthropic("test", "system", "claude-3-5-sonnet-20241022")

        # Check headers match cursorrules specification
        args, kwargs = mock_post.call_args
        headers = kwargs['headers']
        assert headers["x-api-key"] is not None
        assert headers["anthropic-version"] == "2023-06-01"
        assert headers["content-type"] == "application/json"
```

#### **Step 3.4: End-to-End Tests** (5 minutes)

```python
# tests/e2e/test_story_builder_integration.py

import pytest
from unittest.mock import patch
from mythos.services.story_builder import StoryBuilder

class TestStoryBuilderLLMIntegration:
    """Test that story builder works with new LLM system"""

    @patch('mythos.utils.llm_utils.call_llm')
    def test_story_builder_uses_correct_tiers(self, mock_call_llm):
        """Test that story builder uses appropriate tiers for different tasks"""
        mock_call_llm.return_value = "Mock response"

        # Test patterns would be implemented based on actual story_builder.py usage
        # Example: summarization should use fast tier
        # narrative generation should use big tier
```

---

### **Phase 4: Documentation & Examples** (15 minutes)

#### **Step 4.1: Update Configuration Documentation** (5 minutes)

```bash
# .env.example

# LLM API Keys (only sensitive data in environment)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Model configuration is in mythos/config/settings.py
# Mix and match providers per tier using cursorrules verified models:
# FAST_MODEL = ("openai", "gpt-4.1-nano")             # Ultra-fast + cheap
# MEDIUM_MODEL = ("anthropic", "claude-3-5-sonnet")   # Balanced
# BIG_MODEL = ("anthropic", "claude-3-5-sonnet")      # High quality
# PREMIUM_MODEL = ("anthropic", "claude-opus-4")      # Maximum capability
```

#### **Step 4.2: Usage Examples** (5 minutes)

```python
# examples/llm_usage.py

from mythos.utils.llm_utils import call_llm

# Basic usage - uses MEDIUM tier by default
response = call_llm("Explain quantum computing")

# Specify tier for cost/performance optimization
summary = call_llm("Summarize this text...", tier="fast")
narrative = call_llm("Write a story chapter...", tier="big")
premium_analysis = call_llm("Deep analysis needed...", tier="premium")

# JSON output with structured schema (OpenAI models with Responses API)
schema = {
    "type": "object",
    "properties": {
        "colors": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["colors"],
    "additionalProperties": False  # Required for strict mode
}
data = call_llm("List 5 colors", tier="fast", json_output=True, json_schema=schema)

# Extended thinking for complex reasoning (Claude 4 or o-series models)
result = call_llm(
    "Solve this complex problem step by step...",
    tier="premium",
    thinking_mode="extended"
)

# Function calling with tools (works with both APIs)
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }
    }
]
result = call_llm("What's the weather?", tools=tools, tier="big")

# Mix and match models by editing mythos/config/settings.py:
# FAST_MODEL = ("openai", "gpt-4.1-nano")      # OpenAI Responses API for speed
# MEDIUM_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")   # Anthropic Messages API for balance
# BIG_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")      # Anthropic Messages API for quality
# PREMIUM_MODEL = ("openai", "gpt-4.1")        # OpenAI Responses API for maximum capability
```

## Code Standards

### API Calls

```python
# ✅ CORRECT - OpenAI Responses API
response = requests.post(
    "https://api.openai.com/v1/responses",
    json={
        "model": "gpt-4.1",
        "input": prompt,
        "instructions": system_prompt
    }
)
content = response.json()["output_text"]

# ❌ WRONG - Don't use chat completions
response = requests.post(
    "https://api.openai.com/v1/chat/completions",  # NEVER USE
    json={"model": "gpt-4.1", "messages": [...]}
)
```

#### **Step 4.3: Quick Reference** (5 minutes)

````markdown
# Multi-Tier LLM Quick Reference

## Configuration

Set these environment variables:

- `OPENAI_API_KEY` - Your OpenAI API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key

Mix-and-match model configuration in `mythos/config/settings.py`:

- `FAST_MODEL` - (provider, model) tuple for fast tier
- `MEDIUM_MODEL` - (provider, model) tuple for medium tier
- `BIG_MODEL` - (provider, model) tuple for big tier
- `PREMIUM_MODEL` - (provider, model) tuple for premium tier

Uses verified 2025 models from cursorrules:

- **OpenAI**: gpt-4.1 series, gpt-4o series, o-series reasoning models
- **Anthropic**: Claude 4 series (May 2025), Claude 3.7 (hybrid reasoning), Claude 3.5 series

## API Implementation

- **OpenAI**: Responses API (as specified in cursorrules)
- **Anthropic**: Messages API with proper headers
- **Structured Outputs**: OpenAI strict mode with `additionalProperties: false`
- **Extended Thinking**: Claude 4 native thinking, o-series reasoning modes

## Usage

```python
from mythos.utils.llm_utils import call_llm

# Choose tier based on task complexity and cost
call_llm(prompt, tier="fast")     # Quick tasks, summaries
call_llm(prompt, tier="medium")   # Planning, analysis
call_llm(prompt, tier="big")      # Complex reasoning, narrative
call_llm(prompt, tier="premium")  # Maximum capability tasks

# Extended reasoning for complex problems
call_llm(prompt, tier="premium", thinking_mode="extended")
```
````

## Migration

- All existing functions work unchanged
- `call_OpenAI_API()` and `call_Anthropic_API()` still work
- New code should use `call_llm()` with appropriate tier
- Customize models by editing tier configurations in settings.py

````

---

## **🎯 Success Criteria**

### **Functional Requirements**
- [ ] All existing tests pass without modification
- [ ] OpenAI Responses API used (NOT Chat Completions API)
- [ ] Anthropic Messages API with cursorrules headers
- [ ] All four tiers work with both OpenAI and Anthropic
- [ ] Backward compatibility maintained
- [ ] Error handling and logging implemented

### **API Compliance**
- [ ] OpenAI structured outputs using text.format.json_schema with strict mode
- [ ] Claude 4 extended thinking support
- [ ] Reasoning models (o-series) configuration
- [ ] Proper refusal handling for both providers
- [ ] API endpoints match cursorrules specifications exactly

### **Quality Requirements**
- [ ] Zero breaking changes to existing code
- [ ] Configuration takes < 30 seconds
- [ ] Clear error messages for configuration issues
- [ ] Performance matches or exceeds current implementation

### **Developer Experience**
- [ ] Simple environment variable configuration
- [ ] Comprehensive documentation and examples
- [ ] Easy testing and validation
- [ ] Intuitive tier selection

---

## **🚀 Deployment Strategy**

### **Zero-Downtime Migration**
1. **Deploy new system alongside existing** (no behavior changes)
2. **Test thoroughly** with current environment variables
3. **Gradually optimize** by changing model configurations
4. **Monitor performance** and cost impacts
5. **Remove legacy functions** in future release

### **Rollback Plan**
- Keep existing `call_OpenAI_API()` and `call_Anthropic_API()` functions
- Simple rollback: revert function implementations
- No data migration required

---

## **🏆 Configuration Benefits**

### **Why Mix-and-Match + Settings Approach**
- **Maximum Flexibility**: Pick the best model for each tier regardless of provider
- **Cost Optimization**: Use cheap fast models + expensive quality models where needed
- **Version Controlled**: Configuration changes tracked in git
- **Discoverable**: All options visible in `settings.py` with examples
- **Secure**: Only API keys in environment (sensitive data only)
- **Maintainable**: Model updates require no user configuration changes

### **Real-World Mix-and-Match Example (Using Cursorrules Models)**
```python
# Optimal cost/quality configuration using real 2025 models from cursorrules
FAST_MODEL = ("openai", "gpt-4.1-nano")                       # Ultra-fast + cheap (Responses API)
MEDIUM_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")    # Great balance (Messages API)
BIG_MODEL = ("anthropic", "claude-3-5-sonnet-20241022")       # High quality (Messages API)
PREMIUM_MODEL = ("openai", "gpt-4.1")                         # Maximum capability (Responses API)

# Alternative: Reasoning-focused configuration
FAST_MODEL = ("openai", "gpt-4o-mini")                        # Speed (Responses API)
MEDIUM_MODEL = ("openai", "o3-mini")                          # Reasoning (Responses API)
BIG_MODEL = ("anthropic", "claude-3-7-sonnet-20250219")       # Hybrid reasoning (Messages API)
PREMIUM_MODEL = ("anthropic", "claude-opus-4-20250514")       # Claude 4 with extended thinking (Messages API)

# Result: Cost-effective speed + best-in-class reasoning + maximum capability
````

---

**Implementation Time: ~2.5 hours total**
**Benefits: API compliance with cursorrules + OpenAI Responses API + Anthropic Messages API + mix-and-match flexibility + 2025 model features + zero breaking changes + elegant configuration**

Ready to implement this cursorrules-compliant, elegant, minimal, maximum DX solution! 🚀
