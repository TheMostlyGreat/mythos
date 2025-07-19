import uuid
from typing import Dict, Optional
from pydantic import BaseModel, Field
from pathlib import Path
from mythos.story_asset import StoryAsset, AssetMetadata


class Story(BaseModel):
    """
    Represents a story with various components and metadata.

    Attributes:
        title (str): The title of the story. Defaults to "Untitled".
        user_prompt (str): The initial prompt provided by the user.
        synopsis (Optional[str]): A brief summary of the story.
        assets (Dict[str, StoryAsset]): A dictionary of story assets keyed by asset type.
        asset_metadata (Dict[str, AssetMetadata]): Metadata for assets (content in separate .md files).
        manuscript (Dict[str, StoryAsset]): The manuscript content, organized by sections or chapters.
        manuscript_metadata (Dict[str, AssetMetadata]): Metadata for manuscript chapters.
        current_version_num (int): The current version number of the story.
        older_versions (Dict[int, Dict]): Previous version data for version control.
        path (str): Directory path related to the story.
        story_id (str): The unique identifier for the story, generated using UUID4.
    """

    story_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Untitled"  # The title of the story.
    user_prompt: str = ""  # The initial prompt provided by the user.
    story_dir: Path = Field(default_factory=lambda: Path("stories") / str(uuid.uuid4()))
        
    # Legacy assets (for backward compatibility)
    assets: Dict[str, StoryAsset] = {}
    manuscript: Dict[str, StoryAsset] = {}
    
    # New metadata-only storage
    asset_metadata: Dict[str, AssetMetadata] = {}
    manuscript_metadata: Dict[str, AssetMetadata] = {}
    
    current_version_num: int = 1
    draft: Optional[Path] = None
    