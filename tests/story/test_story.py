import pytest
import uuid
from mythos.story import Story
from mythos.story_asset import StoryAsset

def test_story_initialization():
    """
    Test that a Story instance is initialized with default values.
    """
    story = Story()
    assert isinstance(story.story_id, str), "story_id should be a string"
    assert uuid.UUID(story.story_id), "story_id should be a valid UUID"
    assert story.title == "Untitled", "Default title should be 'Untitled'"
    assert story.user_prompt == "", "Default user_prompt should be empty"
    assert story.concept is None, "Default concept should be None"
    assert story.synopsis is None, "Default synopsis should be None"
    assert story.assets == {}, "Default assets should be an empty dictionary"
    assert story.manuscript == {}, "Default manuscript should be an empty dictionary"
    assert story.current_version_num == 1, "Default current_version_num should be 1"
    assert story.older_versions == {}, "Default older_versions should be an empty dictionary"
    assert story.path == "", "Default path should be empty"

def test_story_from_dict_basic():
    """
    Test creating a Story instance from a basic dictionary.
    """
    data = {
        "title": "My Story",
        "user_prompt": "Once upon a time...",
        "concept": "Adventure",
        "synopsis": "A thrilling adventure story.",
        "current_version_num": 2,
        "path": "/stories/my_story",
        "manuscript": {"chapter1": "Content of chapter 1"}
    }
    story = Story.from_dict(data)
    assert story.title == "My Story", "Title should be set correctly"
    assert story.user_prompt == "Once upon a time...", "User prompt should be set correctly"
    assert story.concept == "Adventure", "Concept should be set correctly"
    assert story.synopsis == "A thrilling adventure story.", "Synopsis should be set correctly"
    assert story.current_version_num == 2, "current_version_num should be set correctly"
    assert story.path == "/stories/my_story", "Path should be set correctly"
    assert story.manuscript == {"chapter1": "Content of chapter 1"}, "Manuscript should be set correctly"

def test_story_from_dict_with_assets():
    """
    Test creating a Story instance from a dictionary with valid assets.
    """
    asset_data = {
        "asset_type": "PLOT",
        "title": "Plot",
        "summary": "A compelling plot summary",
        "details": "Detailed plot description"
    }
    data = {
        "title": "Asset Story",
        "assets": {
            "plot": asset_data
        },
    }
    story = Story.from_dict(data)
    assert "plot" in story.assets, "'plot' asset should be present in assets"
    asset = story.assets["plot"]
    assert isinstance(asset, StoryAsset), "'plot' should be an instance of StoryAsset"
    assert asset.title == "Plot", "'plot' title should be set correctly"
    assert asset.summary == "A compelling plot summary", "'plot' summary should be set correctly"
    assert asset.details == "Detailed plot description", "'plot' details should be set correctly"

def test_story_from_dict_missing_fields():
    """
    Test creating a Story instance with missing optional fields.
    """
    data = {}
    story = Story.from_dict(data)
    assert story.title == "Untitled", "Title should default to 'Untitled'"
    assert story.user_prompt == "", "user_prompt should default to empty string"
    assert story.concept is None, "Concept should default to None"
    assert story.synopsis is None, "Synopsis should default to None"
    assert story.current_version_num == 1, "current_version_num should default to 1"
    assert story.older_versions == {}, "older_versions should default to empty dictionary"
    assert story.manuscript == {}, "manuscript should default to empty dictionary"
    assert story.path == "", "Path should default to empty string"

def test_story_from_dict_invalid_asset():
    """
    Test handling invalid asset data in from_dict.
    """
    data = {
        "assets": {
            "plot": {"invalid_field": "value"}
        }
    }
    with pytest.raises(TypeError, match="__init__"):
        Story.from_dict(data)

def test_story_from_dict_unknown_asset_type(caplog):
    """
    Test that unknown asset types are logged as warnings and not added to assets.
    """
    data = {
        "assets": {
            "unknown_asset": {
                "asset_type": "UNKNOWN",
                "title": "Unknown",
                "name": "Unknown Asset",
                "description": "Unknown asset description",
                "file_path": "path/to/unknown.txt"
            }
        }
    }
    with caplog.at_level("WARNING"):
        story = Story.from_dict(data)
        assert "Unknown asset type for key: unknown_asset" in caplog.text, "Should log a warning for unknown asset type"
    assert "unknown_asset" not in story.assets, "Unknown assets should not be added to assets"

def test_story_version_control():
    """
    Test version control attributes in Story.
    """
    data = {
        "current_version_num": 3,
        "older_versions": {
            1: {"title": "Version 1"},
            2: {"title": "Version 2"}
        }
    }
    story = Story.from_dict(data)
    assert story.current_version_num == 3, "current_version_num should be updated correctly"
    assert story.older_versions == {
        1: {"title": "Version 1"},
        2: {"title": "Version 2"}
    }, "older_versions should be set correctly" 