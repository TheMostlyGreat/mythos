from pydantic import BaseModel, field_validator
from pathlib import Path
from typing import Union


class AssetMetadata(BaseModel):
    """
    Represents metadata for a story asset (content stored separately in markdown files).
    
    Attributes:
        asset_type (str): Type/category of the asset.
        title (str): Title of the asset.
        summary (str): Brief summary of the asset content.
        relative_file_path (str): Path to the markdown file containing the content (stored as string).
    """
    asset_type: str
    title: str
    summary: str = None
    relative_file_path: str = None

    @field_validator('relative_file_path', mode='before')
    @classmethod
    def convert_path_to_str(cls, v):
        if isinstance(v, Path):
            return str(v)
        return v


class StoryAsset(BaseModel):
    """
    Represents a story asset with essential details.

    Attributes:
        file_path (str): Path to the asset file.
        asset_type (str): Type/category of the asset.
        name (str): Name of the asset.
        description (Optional[str]): Additional description of the asset.
        details (Optional[str]): Additional details about the asset.
        summary (Optional[str]): A brief summary of the asset.
    """
    asset_type: str
    title: str
    summary: str = None
    details: str = None
    relative_file_path: Union[Path, str] = None

    @field_validator('relative_file_path', mode='before')
    @classmethod
    def convert_path_to_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v

