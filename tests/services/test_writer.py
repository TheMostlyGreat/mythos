from mythos.services.writer import generate_narrative_text, generate_asset_text

def test_generate_narrative_text_integration():
    """
    Integration test for generate_narrative_text function.
    
    This test checks whether the function successfully generates
    narrative text by making a real API call to the Anthropic API.
    
    Parameters
    ----------
    None
    
    Assertions
    ----------
    - The returned text is a non-empty string.
    - The returned text contains expected content based on the prompt.
    """
    # Define a sample prompt for generating narrative text
    prompt = "Give me a sentence that uses the words 'sunset' and 'mountain'."
    
    # Call the generate_narrative_text function with the sample prompt
    narrative = generate_narrative_text(prompt)
    
    # Assert that the function returns a string
    assert isinstance(narrative, str), "The narrative should be a string."
    
    # Assert that the returned narrative is not empty
    assert len(narrative) > 0, "The narrative should not be empty."
    
    # Assert that the narrative contains relevant keywords from the prompt
    assert "sunset" in narrative.lower(), "The narrative should mention 'sunset'."
    assert "mountain" in narrative.lower(), "The narrative should mention 'mountain'."

def test_generate_asset_text_integration():
    """
    Integration test for generate_asset_text function.
    
    This test verifies that the generate_asset_text function successfully
    generates asset text by making a real API call to the OpenAI API.
    
    Parameters
    ----------
    None
    
    Assertions
    ----------
    - The returned text is a non-empty string.
    - The returned text follows the expected structure based on the prompt.
    """
    # Define a sample prompt for generating asset text
    prompt = "Give me a sentence that uses the words 'dragon' and 'quest'."
    
    # Call the generate_asset_text function with the sample prompt
    asset_text = generate_asset_text(prompt)
    
    # Assert that the function returns a string
    assert isinstance(asset_text, str), "The asset text should be a string."
    
    # Assert that the returned asset text is not empty
    assert len(asset_text) > 0, "The asset text should not be empty."
    
    # Optionally, assert that the asset text contains expected keywords
    assert "dragon" in asset_text.lower(), "The asset text should mention 'dragon'."
    assert "quest" in asset_text.lower(), "The asset text should mention 'quest'."
    
