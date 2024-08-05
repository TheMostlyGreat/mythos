import pytest
import os
import tempfile
from mythos.story_assets.base import StoryAsset

# Fixture to create a temporary directory for tests
@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname  # Provide the temporary directory to the test
        # The directory and its contents are automatically cleaned up

# Test the initialization of the StoryAsset class
def test_story_asset_initialization(temp_dir):
    asset = StoryAsset(path=temp_dir, asset_type="TestAsset")
    assert asset.name == "TestAsset"  # Check if the name is set correctly
    assert asset.asset_type == "TestAsset"  # Check if the asset type is set correctly
    assert asset.asset_path == temp_dir  # Check if the path is set correctly

# Test the set_details method of the StoryAsset class
def test_set_details(temp_dir):
    asset = StoryAsset(path=temp_dir, asset_type="TestAsset")
    details = "This is a test asset with some details."
    asset.set_details(details)
    assert asset.details == details  # Check if the details are set correctly
    assert os.path.exists(asset.details_filepath)  # Check if the details file is created

# Test the set_summary method of the StoryAsset class with mocking
def test_set_summary(temp_dir, mocker):
    asset = StoryAsset(path=temp_dir, asset_type="TestAsset")
    asset.details = "Test details"
    
    # Mock the generate_planning_text function
    mock_generate = mocker.patch('mythos.story_assets.base.generate_planning_text')
    mock_generate.return_value = "Test summary"  # Set the return value of the mock

    asset.set_summary()
    assert asset.summary == "Test summary"  # Check if the summary is set correctly
    assert os.path.exists(asset.summary_filepath)  # Check if the summary file is created

# Test the save and load methods of the StoryAsset class
def test_save_and_load(temp_dir):
    asset = StoryAsset(path=temp_dir, asset_type="TestAsset")
    asset.details = "Test details"
    asset.summary = "Test summary"
    asset.save()  # Save the asset to a file

    loaded_asset = StoryAsset.load(asset.bin_filepath)  # Load the asset from the file
    assert loaded_asset.name == asset.name  # Check if the name is loaded correctly
    assert loaded_asset.details == asset.details  # Check if the details are loaded correctly
    assert loaded_asset.summary == asset.summary  # Check if the summary is loaded correctly