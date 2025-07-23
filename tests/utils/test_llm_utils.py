import pytest
from unittest.mock import patch, MagicMock
from mythos.utils.llm_utils import call_llm, LLMError, ProviderError, ConfigurationError, ContentRefusalError
from mythos.config.settings import FAST_MODEL, MEDIUM_MODEL, BIG_MODEL, PREMIUM_MODEL

class TestModelConfiguration:
    """Test model tier configuration with verified 2025 models"""
    
    def test_model_tier_structure(self):
        """Test that all tier models are properly structured"""
        for model_config in [FAST_MODEL, MEDIUM_MODEL, BIG_MODEL, PREMIUM_MODEL]:
            assert isinstance(model_config, tuple)
            assert len(model_config) == 2
            provider, model_name = model_config
            assert provider in ["openai", "anthropic"]
            assert isinstance(model_name, str)
            assert len(model_name) > 0
    
    def test_mix_and_match_capability(self):
        """Test that we can have different providers per tier"""
        providers = {FAST_MODEL[0], MEDIUM_MODEL[0], BIG_MODEL[0], PREMIUM_MODEL[0]}
        # Should work with all same provider or mixed providers
        assert providers.issubset({"openai", "anthropic"})

class TestProviderSwapping:
    """Test dynamic provider swapping capabilities"""
    
    @patch('mythos.utils.llm_utils._call_openai')
    @patch('mythos.utils.llm_utils._call_anthropic')
    def test_swap_openai_to_anthropic(self, mock_anthropic, mock_openai):
        """Test swapping from OpenAI to Anthropic for a tier"""
        mock_openai.return_value = "OpenAI response"
        mock_anthropic.return_value = "Anthropic response"
        
        # Original configuration
        original_fast = FAST_MODEL
        
        # Test with OpenAI fast tier
        if FAST_MODEL[0] == "openai":
            result1 = call_llm("test", tier="fast")
            assert result1 == "OpenAI response"
            assert mock_openai.called
            assert not mock_anthropic.called
            
        # Reset mocks
        mock_openai.reset_mock()
        mock_anthropic.reset_mock()
        
        # Swap to Anthropic
        with patch('mythos.utils.llm_utils.FAST_MODEL', ("anthropic", "claude-3-5-haiku-20241022")):
            result2 = call_llm("test", tier="fast")
            assert result2 == "Anthropic response"
            assert not mock_openai.called
            assert mock_anthropic.called
    
    @patch('mythos.utils.llm_utils._call_openai')
    @patch('mythos.utils.llm_utils._call_anthropic')
    def test_swap_anthropic_to_openai(self, mock_anthropic, mock_openai):
        """Test swapping from Anthropic to OpenAI for a tier"""
        mock_openai.return_value = "OpenAI response"
        mock_anthropic.return_value = "Anthropic response"
        
        # Test with Anthropic big tier
        if BIG_MODEL[0] == "anthropic":
            result1 = call_llm("test", tier="big")
            assert result1 == "Anthropic response"
            assert not mock_openai.called
            assert mock_anthropic.called
            
        # Reset mocks
        mock_openai.reset_mock()
        mock_anthropic.reset_mock()
        
        # Swap to OpenAI
        with patch('mythos.utils.llm_utils.BIG_MODEL', ("openai", "gpt-4o")):
            result2 = call_llm("test", tier="big")
            assert result2 == "OpenAI response"
            assert mock_openai.called
            assert not mock_anthropic.called
    
    @patch('mythos.utils.llm_utils._call_openai')
    @patch('mythos.utils.llm_utils._call_anthropic')
    def test_all_openai_configuration(self, mock_anthropic, mock_openai):
        """Test configuration with all OpenAI models"""
        mock_openai.return_value = "OpenAI response"
        mock_anthropic.return_value = "Anthropic response"
        
        # Configure all tiers to use OpenAI
        with patch('mythos.utils.llm_utils.FAST_MODEL', ("openai", "gpt-4o-mini")), \
             patch('mythos.utils.llm_utils.MEDIUM_MODEL', ("openai", "gpt-4o")), \
             patch('mythos.utils.llm_utils.BIG_MODEL', ("openai", "gpt-4o")), \
             patch('mythos.utils.llm_utils.PREMIUM_MODEL', ("openai", "gpt-4o")):
            
            # Test all tiers
            for tier in ["fast", "medium", "big", "premium"]:
                result = call_llm("test", tier=tier)
                assert result == "OpenAI response"
            
            # Verify only OpenAI was called
            assert mock_openai.call_count == 4
            assert mock_anthropic.call_count == 0
    
    @patch('mythos.utils.llm_utils._call_openai')
    @patch('mythos.utils.llm_utils._call_anthropic')
    def test_all_anthropic_configuration(self, mock_anthropic, mock_openai):
        """Test configuration with all Anthropic models"""
        mock_openai.return_value = "OpenAI response"
        mock_anthropic.return_value = "Anthropic response"
        
        # Configure all tiers to use Anthropic
        with patch('mythos.utils.llm_utils.FAST_MODEL', ("anthropic", "claude-3-5-haiku-20241022")), \
             patch('mythos.utils.llm_utils.MEDIUM_MODEL', ("anthropic", "claude-3-5-sonnet-20241022")), \
             patch('mythos.utils.llm_utils.BIG_MODEL', ("anthropic", "claude-3-5-sonnet-20241022")), \
             patch('mythos.utils.llm_utils.PREMIUM_MODEL', ("anthropic", "claude-3-5-sonnet-20241022")):
            
            # Test all tiers
            for tier in ["fast", "medium", "big", "premium"]:
                result = call_llm("test", tier=tier)
                assert result == "Anthropic response"
            
            # Verify only Anthropic was called
            assert mock_openai.call_count == 0
            assert mock_anthropic.call_count == 4

class TestStructuredOutput:
    """Test JSON structured output functionality"""
    
    @patch('requests.post')
    def test_openai_json_schema_structured_output(self, mock_post):
        """Test OpenAI structured outputs with JSON schema"""
        # Mock successful OpenAI API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"name": "John", "age": 30}'}}],
            "usage": {"total_tokens": 50}
        }
        mock_post.return_value = mock_response
        
        # Test schema
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name", "age"]
        }
        
        # Make call with JSON schema
        result = call_llm(
            "Generate a person",
            tier="medium",
            json_output=True,
            json_schema=schema
        )
        
        assert result == '{"name": "John", "age": 30}'
        
        # Verify the API call included structured outputs
        call_args = mock_post.call_args
        request_data = call_args[1]['json']
        assert 'response_format' in request_data
        assert request_data['response_format']['type'] == 'json_schema'
        assert request_data['response_format']['json_schema']['strict'] == True
        assert request_data['response_format']['json_schema']['schema']['additionalProperties'] == False
    
    @patch('requests.post')
    def test_openai_basic_json_output(self, mock_post):
        """Test OpenAI basic JSON output without schema"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": '{"result": "success"}'}}],
            "usage": {"total_tokens": 30}
        }
        mock_post.return_value = mock_response
        
        result = call_llm(
            "Generate JSON",
            tier="medium",
            json_output=True
        )
        
        assert result == '{"result": "success"}'
        
        # Verify basic JSON mode was used
        call_args = mock_post.call_args
        request_data = call_args[1]['json']
        assert request_data['response_format']['type'] == 'json_object'
    
    @patch('requests.post')
    def test_anthropic_json_output(self, mock_post):
        """Test Anthropic JSON output via system prompt"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": '{"data": "json_response"}'}],
            "usage": {"input_tokens": 20, "output_tokens": 15}
        }
        mock_post.return_value = mock_response
        
        result = call_llm(
            "Generate data",
            tier="big",
            json_output=True
        )
        
        assert result == '{"data": "json_response"}'
        
        # Verify JSON instruction was added to system prompt
        call_args = mock_post.call_args
        request_data = call_args[1]['json']
        assert "Respond with valid JSON only" in request_data['system']

class TestThinkingMode:
    """Test thinking mode functionality for reasoning models"""
    
    @patch('requests.post')
    def test_openai_extended_thinking_o3_model(self, mock_post):
        """Test OpenAI o3 model with extended thinking"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Thoughtful response after reasoning"}}],
            "usage": {"total_tokens": 100}
        }
        mock_post.return_value = mock_response
        
        # Test with o3 model and extended thinking
        with patch('mythos.utils.llm_utils.MEDIUM_MODEL', ("openai", "o3-mini")):
            result = call_llm(
                "Complex reasoning task",
                tier="medium",
                thinking_mode="extended"
            )
            
            assert result == "Thoughtful response after reasoning"
            
            # Verify reasoning configuration was added
            call_args = mock_post.call_args
            request_data = call_args[1]['json']
            assert 'reasoning' in request_data
            assert request_data['reasoning']['effort'] == 'high'
    
    @patch('requests.post')
    def test_openai_fast_thinking_o4_model(self, mock_post):
        """Test OpenAI o4 model with fast thinking"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Quick reasoning response"}}],
            "usage": {"total_tokens": 75}
        }
        mock_post.return_value = mock_response
        
        # Test with o4 model and fast thinking
        with patch('mythos.utils.llm_utils.BIG_MODEL', ("openai", "o4-mini")):
            result = call_llm(
                "Reasoning task",
                tier="big",
                thinking_mode="fast"
            )
            
            assert result == "Quick reasoning response"
            
            # Verify fast reasoning configuration
            call_args = mock_post.call_args
            request_data = call_args[1]['json']
            assert 'reasoning' in request_data
            assert request_data['reasoning']['effort'] == 'medium'
    
    @patch('requests.post')
    def test_anthropic_extended_thinking(self, mock_post):
        """Test Anthropic Claude extended thinking via system prompt"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": "Carefully reasoned response"}],
            "usage": {"input_tokens": 30, "output_tokens": 25}
        }
        mock_post.return_value = mock_response
        
        # Test Anthropic with extended thinking
        result = call_llm(
            "Complex analysis task",
            tier="big",
            thinking_mode="extended"
        )
        
        assert result == "Carefully reasoned response"
        
        # Verify extended thinking prompt was added
        call_args = mock_post.call_args
        request_data = call_args[1]['json']
        assert "Take time to think through this step by step" in request_data['system']
    
    @patch('requests.post')
    def test_no_thinking_mode_for_regular_models(self, mock_post):
        """Test that thinking mode doesn't affect regular models"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Regular response"}}],
            "usage": {"total_tokens": 40}
        }
        mock_post.return_value = mock_response
        
        # Test regular model (should ignore thinking mode)
        result = call_llm(
            "Regular task",
            tier="medium",  # Uses gpt-4o by default
            thinking_mode="extended"
        )
        
        assert result == "Regular response"
        
        # Verify no reasoning configuration was added
        call_args = mock_post.call_args
        request_data = call_args[1]['json']
        assert 'reasoning' not in request_data

class TestRefusalLogic:
    """Test content refusal handling"""
    
    @patch('requests.post')
    def test_openai_content_filter_refusal(self, mock_post):
        """Test OpenAI content filter refusal handling"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": None}, "finish_reason": "content_filter"}],
            "usage": {"total_tokens": 10}
        }
        mock_post.return_value = mock_response
        
        with pytest.raises(ContentRefusalError, match="Content generation was declined for safety reasons"):
            call_llm("Harmful request", tier="medium")
    
    @patch('requests.post')
    def test_anthropic_refusal_response(self, mock_post):
        """Test Anthropic refusal response handling"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": "I cannot help with that request"}],
            "stop_reason": "refusal",
            "usage": {"input_tokens": 15, "output_tokens": 8}
        }
        mock_post.return_value = mock_response
        
        with pytest.raises(ContentRefusalError, match="Content generation was declined for safety reasons"):
            call_llm("Inappropriate request", tier="big")
    
    @patch('requests.post')
    def test_refusal_propagation_through_writers(self, mock_post):
        """Test that refusals propagate through writer functions"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": "I cannot help with that request"}],
            "stop_reason": "refusal",
            "usage": {"input_tokens": 15, "output_tokens": 8}
        }
        mock_post.return_value = mock_response
        
        from mythos.services.writer import generate_narrative_text
        
        with pytest.raises(ContentRefusalError):
            generate_narrative_text("Harmful narrative request")

class TestCallLLMFunction:
    """Test the main call_llm function"""
    
    def test_tier_validation(self):
        """Test tier parameter validation"""
        with pytest.raises(ValueError, match="Invalid tier 'invalid'"):
            call_llm("test", tier="invalid")
    
    def test_valid_tiers(self):
        """Test that all valid tiers are accepted"""
        valid_tiers = ["fast", "medium", "big", "premium"]
        
        with patch('mythos.utils.llm_utils._call_openai') as mock_openai, \
             patch('mythos.utils.llm_utils._call_anthropic') as mock_anthropic:
            
            mock_openai.return_value = "OpenAI response"
            mock_anthropic.return_value = "Anthropic response"
            
            for tier in valid_tiers:
                # Should not raise an exception
                call_llm("test prompt", tier=tier)
    
    @patch('mythos.utils.llm_utils._call_openai')
    def test_openai_routing(self, mock_openai):
        """Test that OpenAI models are routed correctly"""
        mock_openai.return_value = "OpenAI response"
        
        # Test with a tier that uses OpenAI
        if FAST_MODEL[0] == "openai":
            result = call_llm("test", tier="fast")
            mock_openai.assert_called_once()
            assert result == "OpenAI response"
    
    @patch('mythos.utils.llm_utils._call_anthropic')
    def test_anthropic_routing(self, mock_anthropic):
        """Test that Anthropic models are routed correctly"""
        mock_anthropic.return_value = "Anthropic response"
        
        # Test with a tier that uses Anthropic
        if BIG_MODEL[0] == "anthropic":
            result = call_llm("test", tier="big")
            mock_anthropic.assert_called_once()
            assert result == "Anthropic response"
    
    def test_parameter_passing(self):
        """Test that parameters are passed correctly to provider functions"""
        with patch('mythos.utils.llm_utils._call_openai') as mock_openai:
            mock_openai.return_value = "response"
            
            call_llm(
                "test prompt",
                tier="fast" if FAST_MODEL[0] == "openai" else "medium",
                temperature=0.7,
                max_tokens=100,
                json_output=True
            )
            
            # Check that parameters were passed
            mock_openai.assert_called_once()
            args, kwargs = mock_openai.call_args
            assert kwargs.get('temperature') == 0.7
            assert kwargs.get('max_tokens') == 100
            assert kwargs.get('json_output') == True

class TestProviderFunctions:
    """Test individual provider functions"""
    
    @patch('requests.post')
    def test_openai_success_response(self, mock_post):
        """Test OpenAI API success response handling"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"total_tokens": 100, "prompt_tokens": 50, "completion_tokens": 50}
        }
        mock_post.return_value = mock_response
        
        from mythos.utils.llm_utils import _call_openai
        result = _call_openai("test", "system", "gpt-4o")
        
        assert result == "Test response"
    
    @patch('requests.post')
    def test_openai_error_response(self, mock_post):
        """Test OpenAI API error response handling"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response
        
        from mythos.utils.llm_utils import _call_openai
        
        with pytest.raises(ProviderError, match="OpenAI API error 400"):
            _call_openai("test", "system", "gpt-4o")
    
    @patch('requests.post')
    def test_anthropic_success_response(self, mock_post):
        """Test Anthropic API success response handling"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": "Test response"}],
            "usage": {"input_tokens": 50, "output_tokens": 50}
        }
        mock_post.return_value = mock_response
        
        from mythos.utils.llm_utils import _call_anthropic
        result = _call_anthropic("test", "system", "claude-3-5-sonnet-20241022")
        
        assert result == "Test response"

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @patch('mythos.utils.llm_utils._call_openai')
    @patch('mythos.utils.llm_utils._call_anthropic')
    def test_unsupported_provider(self, mock_anthropic, mock_openai):
        """Test handling of unsupported providers"""
        # Test by directly patching the tier_models lookup
        with patch('mythos.utils.llm_utils.FAST_MODEL', ("unsupported", "model")):
            with pytest.raises(LLMError, match="LLM call failed: Unsupported provider: unsupported"):
                call_llm("test", tier="fast")
    
    @patch('mythos.utils.llm_utils._call_openai')
    def test_network_error_handling(self, mock_openai):
        """Test network error handling"""
        mock_openai.side_effect = ProviderError("Network error")
        
        with pytest.raises(LLMError, match="LLM call failed: Network error"):
            call_llm("test", tier="fast" if FAST_MODEL[0] == "openai" else "medium")

class TestBackwardCompatibility:
    """Test backward compatibility functions"""
    
    @patch('mythos.utils.llm_utils.call_llm')
    def test_legacy_openai_function(self, mock_call_llm):
        """Test legacy call_OpenAI_API function"""
        mock_call_llm.return_value = "response"
        
        from mythos.utils.llm_utils import call_OpenAI_API
        result = call_OpenAI_API("test prompt")
        
        mock_call_llm.assert_called_once()
        args, kwargs = mock_call_llm.call_args
        assert kwargs['tier'] == "medium"
        assert result == "response"
    
    @patch('mythos.utils.llm_utils.call_llm')
    def test_legacy_anthropic_function(self, mock_call_llm):
        """Test legacy call_Anthropic_API function"""
        mock_call_llm.return_value = "response"
        
        from mythos.utils.llm_utils import call_Anthropic_API
        result = call_Anthropic_API("test prompt", "system prompt")
        
        mock_call_llm.assert_called_once()
        args, kwargs = mock_call_llm.call_args
        assert kwargs['tier'] == "big"
        assert result == "response"

class TestWriterIntegration:
    """Test that writer functions use correct tiers"""
    
    @patch('mythos.services.writer.call_llm')
    def test_planning_text_uses_medium_tier(self, mock_call_llm):
        """Test that generate_planning_text uses medium tier"""
        mock_call_llm.return_value = "planning response"
        
        from mythos.services.writer import generate_planning_text
        result = generate_planning_text("test prompt")
        
        mock_call_llm.assert_called_once()
        args, kwargs = mock_call_llm.call_args
        assert kwargs['tier'] == "medium"
        assert result == "planning response"
    
    @patch('mythos.services.writer.call_llm')
    def test_narrative_text_uses_big_tier(self, mock_call_llm):
        """Test that generate_narrative_text uses big tier"""
        mock_call_llm.return_value = "narrative response"
        
        from mythos.services.writer import generate_narrative_text
        result = generate_narrative_text("test prompt")
        
        mock_call_llm.assert_called_once()
        args, kwargs = mock_call_llm.call_args
        assert kwargs['tier'] == "big"
        assert result == "narrative response"
    
    @patch('mythos.services.writer.call_llm')
    def test_summarize_text_uses_fast_tier(self, mock_call_llm):
        """Test that summarize_text uses fast tier"""
        mock_call_llm.return_value = "summary response"
        
        from mythos.services.writer import summarize_text
        result = summarize_text("long text to summarize")
        
        mock_call_llm.assert_called_once()
        args, kwargs = mock_call_llm.call_args
        assert kwargs['tier'] == "fast"
        assert result == "summary response" 
