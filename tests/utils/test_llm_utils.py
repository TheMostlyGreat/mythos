import os
import pytest
from unittest.mock import patch, MagicMock, call
from mythos.utils.llm_utils import (
    call_OpenAI_API,
    call_Anthropic_API
)
from mythos.config.settings import OPENAI_MODEL, ANTHROPIC_MODEL, MAX_RETRIES, NARRATIVE_SYSTEM_PROMPT

@pytest.fixture(scope="module")
def test_Anthropic_api_credentials():
    """
    Fixture to provide API credentials for Anthropic API.
    Ensure that the ANTHROPIC_API_KEY environment variable is set.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.fail("ANTHROPIC_API_KEY environment variable not set.")
    return api_key

@pytest.fixture(scope="module")
def test_OpenAI_api_credentials():
    """
    Fixture to provide API credentials for OpenAI API.
    Ensure that the OPENAI_API_KEY environment variable is set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.fail("OPENAI_API_KEY environment variable not set.")
    return api_key

@patch('mythos.utils.llm_utils.OpenAI')
def test_call_OpenAI_API_success(mock_openai):
    """
    Test that call_OpenAI_API returns the expected content on successful Responses API call.
    """
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.output_text = "Generated narrative text."
    mock_response.usage = MagicMock()
    mock_response.usage.total_tokens = 100
    mock_client.responses.create.return_value = mock_response
    mock_openai.return_value = mock_client

    prompt = "Once upon a time"
    system_prompt = "You are a storyteller."
    result = call_OpenAI_API(prompt, system_prompt)

    assert result == "Generated narrative text."
    mock_client.responses.create.assert_called_once()
    
    # Verify the call was made with the correct Responses API parameters
    call_args = mock_client.responses.create.call_args
    assert call_args[1]['model'] == OPENAI_MODEL
    assert call_args[1]['input'] == prompt
    assert call_args[1]['instructions'] == system_prompt + "You are a machine that only returns and replies with valid, iterable RFC8259 compliantJSON in your responses. Ensure the JSON is well-formed and does not include any extraneous characters or formattingYour responses should be in the following format: {'key': 'value'}"
    assert call_args[1]['max_output_tokens'] == 4000
    assert call_args[1]['temperature'] == 1

@patch('mythos.utils.llm_utils.OpenAI')
def test_call_OpenAI_API_with_schema(mock_openai):
    """
    Test that call_OpenAI_API uses structured outputs when schema is provided.
    """
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.output_text = '{"name": "test"}'
    mock_response.usage = MagicMock()
    mock_response.usage.total_tokens = 50
    mock_client.responses.create.return_value = mock_response
    mock_openai.return_value = mock_client

    schema = {"type": "object", "properties": {"name": {"type": "string"}}}
    prompt = "Generate a name"
    system_prompt = "You are helpful."
    
    result = call_OpenAI_API(prompt, system_prompt, json_schema=schema)

    assert result == '{"name": "test"}'
    
    # Verify structured outputs were used
    call_args = mock_client.responses.create.call_args
    assert 'text' in call_args[1]
    assert call_args[1]['text']['format']['type'] == 'json_schema'
    assert call_args[1]['text']['format']['schema'] == schema
    assert call_args[1]['text']['format']['strict'] == True

@patch('mythos.utils.llm_utils.OpenAI')
def test_call_OpenAI_API_with_previous_response_id(mock_openai):
    """
    Test that call_OpenAI_API handles conversation continuity with previous_response_id.
    """
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.output_text = "Continuing the conversation."
    mock_response.usage = MagicMock()
    mock_response.usage.total_tokens = 75
    mock_client.responses.create.return_value = mock_response
    mock_openai.return_value = mock_client

    prompt = "Tell me more"
    system_prompt = "You are helpful."
    previous_id = "resp_123456789"
    
    result = call_OpenAI_API(prompt, system_prompt, previous_response_id=previous_id)

    assert result == "Continuing the conversation."
    
    # Verify previous_response_id was passed
    call_args = mock_client.responses.create.call_args
    assert call_args[1]['previous_response_id'] == previous_id

@patch('mythos.utils.llm_utils.OpenAI')
def test_call_OpenAI_API_failure(mock_openai):
    """
    Test that call_OpenAI_API handles failures appropriately.
    """
    mock_client = MagicMock()
    mock_client.responses.create.side_effect = Exception("API Error")
    mock_openai.return_value = mock_client

    prompt = "Test prompt"
    system_prompt = "Test system"
    result = call_OpenAI_API(prompt, system_prompt)

    assert result.startswith("Error: Unable to generate LLM content with OpenAI Responses API")
    assert mock_client.responses.create.call_count == MAX_RETRIES

@patch('mythos.utils.llm_utils.Anthropic')
def test_call_Anthropic_API_success(mock_anthropic):
    """
    Test that call_Anthropic_API returns the expected content on successful API call.
    """
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="Generated Anthropic text.")]
    mock_message.stop_reason = "end_turn"
    mock_client.messages.create.return_value = mock_message
    mock_anthropic.return_value = mock_client

    prompt = "Tell me a story"
    system_prompt = "You are a creative writer."
    result = call_Anthropic_API(prompt, system_prompt)

    assert result == "Generated Anthropic text."
    mock_client.messages.create.assert_called_once_with(
        model=ANTHROPIC_MODEL,
        max_tokens=4000,
        temperature=1,
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

@patch('mythos.utils.llm_utils.Anthropic')
def test_call_Anthropic_API_refusal(mock_anthropic):
    """
    Test that call_Anthropic_API handles refusal responses.
    """
    mock_client = MagicMock()
    mock_message = MagicMock()
    mock_message.stop_reason = "refusal"
    mock_client.messages.create.return_value = mock_message
    mock_anthropic.return_value = mock_client

    prompt = "Harmful request"
    system_prompt = "You are helpful."
    result = call_Anthropic_API(prompt, system_prompt)

    assert result == "Error: Content generation was declined for safety reasons. Please try rephrasing your request."

def test_OpenAI_API_real_api():
    """
    Integration test for OpenAI Responses API.
    
    Ensure that the OPENAI_API_KEY environment variable is set before running this test.
    """
    prompt = "Tell me a story that starts with 'In a galaxy far, far away' and includes a 'Jedi' character."
    result = call_OpenAI_API(prompt=prompt, system_prompt=NARRATIVE_SYSTEM_PROMPT)
    
    assert isinstance(result, str), "Result should be a string."
    assert len(result) > 0, "Result should not be empty."
    assert "galaxy" in result or "far away" in result or "jedi" in result, "Result should relate to the prompt text."

def test_Anthropic_API_real_api():
    """
    Integration test for Anthropic API.
    
    Ensure that the ANTHROPIC_API_KEY environment variable is set before running this test.
    """
    prompt = "Tell me a story that starts with 'In a galaxy far, far away' and includes a 'Jedi' character."
    result = call_Anthropic_API(prompt=prompt, system_prompt=NARRATIVE_SYSTEM_PROMPT)
    
    assert isinstance(result, str), "Result should be a string."
    assert len(result) > 0, "Result should not be empty."
    assert "galaxy" in result or "far away" in result or "jedi" in result, "Result should relate to the prompt text." 
