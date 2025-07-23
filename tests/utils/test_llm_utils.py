import pytest
from unittest.mock import patch, MagicMock
from mythos.utils.llm_utils import call_llm, LLMError, ProviderError, ConfigurationError
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
    
    def test_unsupported_provider(self):
        """Test handling of unsupported providers"""
        # Temporarily modify a model config to test error handling
        from mythos.config import settings
        original = settings.FAST_MODEL
        settings.FAST_MODEL = ("unsupported", "model")
        
        try:
            with pytest.raises(ValueError, match="Unsupported provider: unsupported"):
                call_llm("test", tier="fast")
        finally:
            settings.FAST_MODEL = original
    
    @patch('mythos.utils.llm_utils._call_openai')
    def test_network_error_handling(self, mock_openai):
        """Test network error handling"""
        mock_openai.side_effect = ProviderError("Network error")
        
        with pytest.raises(ProviderError, match="Network error"):
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
    
    @patch('mythos.utils.llm_utils.call_llm')
    def test_planning_text_uses_medium_tier(self, mock_call_llm):
        """Test that generate_planning_text uses medium tier"""
        mock_call_llm.return_value = "planning response"
        
        from mythos.services.writer import generate_planning_text
        result = generate_planning_text("test prompt")
        
        mock_call_llm.assert_called_once()
        args, kwargs = mock_call_llm.call_args
        assert kwargs['tier'] == "medium"
        assert result == "planning response"
    
    @patch('mythos.utils.llm_utils.call_llm')
    def test_narrative_text_uses_big_tier(self, mock_call_llm):
        """Test that generate_narrative_text uses big tier"""
        mock_call_llm.return_value = "narrative response"
        
        from mythos.services.writer import generate_narrative_text
        result = generate_narrative_text("test prompt")
        
        mock_call_llm.assert_called_once()
        args, kwargs = mock_call_llm.call_args
        assert kwargs['tier'] == "big"
        assert result == "narrative response"
    
    @patch('mythos.utils.llm_utils.call_llm')
    def test_summarize_text_uses_fast_tier(self, mock_call_llm):
        """Test that summarize_text uses fast tier"""
        mock_call_llm.return_value = "summary response"
        
        from mythos.services.writer import summarize_text
        result = summarize_text("long text to summarize")
        
        mock_call_llm.assert_called_once()
        args, kwargs = mock_call_llm.call_args
        assert kwargs['tier'] == "fast"
        assert result == "summary response" 
