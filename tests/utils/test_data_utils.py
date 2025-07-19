import pytest
import json
from mythos.utils.data_utils import (
    sanitize_string,
    serialize_to_json,
    deserialize_from_json,
    create_unique_directory,
    get_asset_type,
)
from mythos.config.settings import AssetTypes

def test_sanitize_string():
    """
    Test sanitize_string to ensure it replaces disallowed characters with underscores.
    """
    # Test with default allowed characters
    input_str = "Hello@World!"
    expected = "Hello_World_"
    result = sanitize_string(input_str)
    assert result == expected, "sanitize_string did not replace disallowed characters correctly."

    # Test with custom allowed characters
    input_str = "foo#bar$baz"
    allowed = r'[^a-zA-Z#\$]'
    expected = "foo#bar$baz"
    result = sanitize_string(input_str, allowed_chars=allowed)
    assert result == expected, "sanitize_string did not respect custom allowed characters."

def test_serialize_to_json(tmp_path):
    """
    Test serialize_to_json to ensure an object is correctly written to a JSON file.
    """
    obj = {'name': 'Test', 'value': 123}
    file_path = tmp_path / "test.json"

    serialize_to_json(obj, str(file_path))

    with open(file_path, 'r') as f:
        data = json.load(f)
    assert data == obj, "serialize_to_json did not correctly serialize the object."

def test_deserialize_from_json(tmp_path):
    """
    Test deserialize_from_json to ensure a JSON file is correctly read into an object.
    """
    class Sample:
        def __init__(self, name, value):
            self.name = name
            self.value = value

        @classmethod
        def from_dict(cls, data):
            return cls(**data)

    obj = {'name': 'Test', 'value': 123}
    file_path = tmp_path / "test.json"
    with open(file_path, 'w') as f:
        json.dump(obj, f)

    result = deserialize_from_json(str(file_path), Sample)

    assert isinstance(result, Sample), "deserialize_from_json did not return an instance of Sample."
    assert result.name == obj['name'], "Name attribute mismatch."
    assert result.value == obj['value'], "Value attribute mismatch."

def test_create_unique_directory(tmp_path):
    """
    Test create_unique_directory to ensure it creates a unique directory, appending a counter if needed.
    """
    base_path = tmp_path
    dir_name = "unique_dir"

    dir_path1 = create_unique_directory(base_path, dir_name)
    assert dir_path1.exists(), "First unique directory was not created."
    assert dir_path1.name == dir_name, "Directory name mismatch."

    dir_path2 = create_unique_directory(base_path, dir_name)
    assert dir_path2.exists(), "Second unique directory was not created."
    assert dir_path2.name == f"{dir_name}_1", "Directory counter was not appended correctly."

def test_get_asset_type():
    """
    Test get_asset_type to ensure it retrieves the correct AssetType or raises ValueError 
    for undefined keys.
    """
    # Valid asset types from settings.py
    asset_key_research = "RESEARCH"
    expected_research = AssetTypes.RESEARCH
    assert get_asset_type(asset_key_research) == expected_research, "Incorrect AssetType for 'RESEARCH'."

    asset_key_plot = "PLOT"
    expected_plot = AssetTypes.PLOT
    assert get_asset_type(asset_key_plot) == expected_plot, "Incorrect AssetType for 'PLOT'."

    # Invalid asset type
    asset_key_invalid = "unknown"
    with pytest.raises(ValueError, match=f"Asset type '{asset_key_invalid}' is not defined."):
        get_asset_type(asset_key_invalid) 