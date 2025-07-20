import json
from pathlib import Path
from typing import Any
from pydantic import BaseModel
from mythos.utils.logger import get_logger
from mythos.config.settings import AssetTypes, AssetType
from slugify import slugify


logger = get_logger(__name__)

def is_valid_json(json_string: str) -> bool:
    """Check if a string is valid JSON."""
    try:
        json.loads(json_string)
        return True
    except ValueError:
        return False

def sanitize_string(input_string: str) -> str:
    """
    Convert the input string to a slugified version.

    Args:
        input_string (str): The string to sanitize.

    Returns:
        str: A slugified version of the input string.
    """
    return slugify(input_string)

def get_unique_path(base_path: Path, name: str) -> Path:
    """
    Generate a unique path by appending a counter if the path already exists.

    Args:
        base_path (Path): The base directory path.
        name (str): The name to base the unique path on.

    Returns:
        Path: A unique path.
    """
    sanitized_name = sanitize_string(name)
    unique_path = base_path / sanitized_name
    counter = 1

    # Append a counter until a unique path is found
    while unique_path.exists():
        unique_path = Path(f"{base_path}/{sanitized_name}_{counter}")
        counter += 1

    return unique_path

def serialize_to_json(obj, file_path: str) -> None:
    """
    Serialize a Pydantic model or dictionary to a JSON file.

    For Pydantic models, utilizes built-in serialization.
    For dictionaries, performs a standard JSON dump.

    Args:
        obj: The object to serialize (Pydantic model or dictionary).
        file_path: Path to the output JSON file.

    Raises:
        ValueError: If a circular reference is detected in a Pydantic model.
        Exception: If serialization fails.
    """
    try:
        if isinstance(obj, BaseModel):
            logger.debug("Object is a Pydantic model. Using built-in serialization.")
            json_content = obj.model_dump_json(indent=4)
        else:
            logger.debug("Object is a dictionary. Using standard JSON serialization.")
            json_content = json.dumps(obj, indent=4)

        with open(file_path, 'w') as file:
            file.write(json_content)
        
        logger.info(f"Object serialized to {file_path} successfully.")
    
    except Exception as e:
        logger.error(f"Failed to serialize object to {file_path}: {e}")
        raise

def deserialize_from_json(file_path: str, cls) -> Any:
    """Deserialize a JSON file into an object of the specified class."""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        logger.info(f"Object deserialized from {file_path} successfully.")
        
        # Check if it's a Pydantic model
        if hasattr(cls, 'model_validate'):
            # Use Pydantic's model_validate for v2
            return cls.model_validate(data)
        elif hasattr(cls, '__pydantic_model__'):
            # Use Pydantic's constructor for v1/v2
            return cls(**data)
        elif hasattr(cls, 'from_dict'):
            # Use from_dict method if available
            return cls.from_dict(data)
        else:
            # Try direct constructor as fallback
            return cls(**data)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to deserialize object from {file_path}: {e}")
        raise

def create_unique_directory(base_path: Path, name: str) -> Path:
    """
    Create a unique directory by appending a counter if needed.

    Args:
        base_path (Path): The base directory where the new directory will be created.
        name (str): The name for the new directory.

    Returns:
        Path: The path to the newly created unique directory.

    Raises:
        Exception: If directory creation fails.
    """
    # Get a unique path without creating the directory
    unique_path = get_unique_path(base_path, name)
    try:
        unique_path.mkdir(parents=True, exist_ok=False)
        logger.info(f"Directory created at {unique_path}")
    except Exception as e:
        logger.error(f"Failed to create directory {unique_path}: {e}")
        raise
    return unique_path 

def get_asset_type(asset_key: str) -> AssetType:
    """Retrieve the AssetType enum based on the asset key."""
    asset_type_enum = getattr(AssetTypes, asset_key.upper(), None)
    if not isinstance(asset_type_enum, AssetType):
        logger.error(f"Asset type '{asset_key}' is not defined.")
        raise ValueError(f"Asset type '{asset_key}' is not defined.")
    return asset_type_enum 