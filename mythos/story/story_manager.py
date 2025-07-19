import json
from pathlib import Path
from typing import Optional
from mythos.story import Story
from mythos.story_asset import StoryAsset, AssetMetadata
from mythos.utils.logger import get_logger
from mythos.config import settings
from mythos.utils.data_utils import (
    serialize_to_json,
    deserialize_from_json,
    sanitize_string,
    get_unique_path
)
import shutil

class StoryManager:
    """
    Manages operations for the Story dataclass, including creation, updates, versioning, and persistence.
    """

    def __init__(self):
        """
        Initializes the StoryManager with the directory to store story files.
        """
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing StoryManager")

    # def create_story(self, story: Story) -> Story:
    #     """
    #     Creates a new Story instance.

    #     Args:
    #         story (Story): Initial story object.

    #     Returns:
    #         Story: A new Story instance.
    #     """
    #     story = self.setup_directories(story)
        
    #     story = self.save_story(story)

    # #     return story

    # def setup_directories(self, story: Story) -> Story:
    #     """
    #     Sets up directories for the given story.

    #     Creates a unique directory based on the story's title and initializes
    #     subdirectories for JSON data and assets.

    #     Args:
    #         story (Story): The story object for which directories are being set up.

    #     Returns:
    #         Story: The updated Story object with directory paths set.
    #     """
    #     dir_path = create_unique_directory(Path(settings.STORY_DIR), story.title)
    #     story.story_dir = Path(dir_path)
    #     story.json_dir = Path(dir_path, settings.JSON_DIR)

    #     # Initialize the JSON directory
    #     story.json_dir.mkdir(parents=True, exist_ok=True)
        
    #     return story
    
    def set_story_title(self, story: Story, title: str) -> Story:
        """
        Updates the story title and renames associated directories and files.

        Args:
            story (Story): The story object to update.
            title (str): The new title for the story.

        Returns:
            Story: The updated story object.
        """
        # Update the old path before changing title
        old_sanitized_title = sanitize_string(story.title)
        old_story_dir = story.story_dir

        # Update the story title
        story.title = title
        
        # Generate new path based on new title
        new_sanitized_title = sanitize_string(title)
        new_story_dir = Path(settings.STORY_DIR) / new_sanitized_title

        # If directories are different, rename the directory
        if old_story_dir != new_story_dir and old_story_dir.exists():
            # Get a unique path if the target already exists
            unique_new_dir = get_unique_path(Path(settings.STORY_DIR), new_sanitized_title)
            shutil.move(str(old_story_dir), str(unique_new_dir))
            story.story_dir = unique_new_dir
            self.logger.info(f"Renamed story directory from '{old_story_dir}' to '{unique_new_dir}'")
        else:
            story.story_dir = new_story_dir

        return story

    def save_story(self, story: Story, use_new_format: bool = True) -> Story:
        """
        Saves story and its assets metadata to the story file.
        
        Args:
            story (Story): The story to save.
            use_new_format (bool): If True, save using new metadata format. If False, use legacy format.
        """
        # Serialize story data excluding assets if using new format
        if use_new_format:
            story_data_json = story.model_dump_json(
                exclude={'assets': ..., 'manuscript': ...},
                by_alias=True,
            )
        else:
            # Legacy format - exclude new metadata fields
            story_data_json = story.model_dump_json(
                exclude={'asset_metadata': ..., 'manuscript_metadata': ...},
                by_alias=True,
            )
        
        # Convert the JSON string to a dictionary
        story_data = json.loads(story_data_json)

        self.logger.debug(f"Story data: {story_data}")

        if use_new_format:
            # Save asset metadata directly in story file (new format)
            story_data['asset_metadata'] = {
                key: metadata.model_dump() for key, metadata in story.asset_metadata.items()
            }
            story_data['manuscript_metadata'] = {
                key: metadata.model_dump() for key, metadata in story.manuscript_metadata.items()
            }
            self.logger.debug("Saved asset metadata in new format")
        else:
            # Legacy format - save asset references
            serialized_assets = {
                key: asset.model_dump_json(
                    include={'title', 'relative_file_path'},
                )
                for key, asset in story.assets.items()
            }
            story_data['assets'] = serialized_assets
            self.logger.debug(f"Serialized assets (legacy): {serialized_assets}")

        # **Updated: Use sanitized title instead of UUID for the story file name**
        sanitized_title = sanitize_string(story.title)
        story_filename = f"{sanitized_title}.story"
        story_path = Path(story.story_dir, story_filename)
        
        # Serialize to JSON
        serialize_to_json(obj=story_data, file_path=str(story_path))
        self.logger.info(f"Saved story to {story_path}")
        
        return story

    def load_story(self, story_title: str, story_dir: str = None) -> Optional[Story]:
        """
        Loads story and its assets from JSON files based on the story title.
        Supports both new metadata format and legacy format.

        Args:
            story_title (str): The title of the story to load.
            story_dir (str): Optional directory where the story is located. If None, uses default location.

        Returns:
            Optional[Story]: The loaded Story instance or None if failed.
        """
        try:
            sanitized_title = sanitize_string(story_title)
            
            if story_dir:
                # Use provided directory
                story_path = Path(story_dir, f"{sanitized_title}.story")
            else:
                # Use default location
                story_path = Path(settings.STORY_DIR, sanitized_title, f"{sanitized_title}.story")
            
            # Load main story data directly
            with open(story_path, 'r') as file:
                story_data = json.load(file)
            
            # Check if this is new format (has asset_metadata) or legacy format
            if 'asset_metadata' in story_data or 'manuscript_metadata' in story_data:
                # New format - load metadata and reconstruct assets
                story = Story(**story_data)
                
                # Reconstruct StoryAsset objects from metadata + markdown content
                from mythos.story_asset import StoryAssetManager
                asset_manager = StoryAssetManager()
                
                # Load assets
                for key, metadata_dict in story_data.get('asset_metadata', {}).items():
                    metadata = AssetMetadata(**metadata_dict)
                    content = asset_manager.get_asset_content(metadata, str(story.story_dir))
                    story.assets[key] = asset_manager.create_story_asset_from_metadata(metadata, content)
                
                # Load manuscript
                for key, metadata_dict in story_data.get('manuscript_metadata', {}).items():
                    metadata = AssetMetadata(**metadata_dict)
                    content = asset_manager.get_asset_content(metadata, str(story.story_dir))
                    story.manuscript[key] = asset_manager.create_story_asset_from_metadata(metadata, content)
                
                self.logger.info(f"Loaded story '{story_title}' using new format")
                return story
            else:
                # Legacy format - load asset paths and reconstruct
                asset_paths = story_data.pop("asset_paths", {})
                story = Story(**story_data)
                
                # Load each asset from its path (legacy)
                for asset_key, asset_path in asset_paths.items():
                    asset_full_path = Path(asset_path)
                    if asset_full_path.exists():
                        asset = deserialize_from_json(str(asset_full_path), StoryAsset)
                        story.assets[asset_key] = asset
                        
                        # Create metadata for migration
                        story.asset_metadata[asset_key] = AssetMetadata(
                            asset_type=asset.asset_type,
                            title=asset.title,
                            summary=asset.summary,
                            relative_file_path=asset.relative_file_path
                        )
                    else:
                        self.logger.warning(f"Asset file not found: {asset_full_path}")
                
                self.logger.info(f"Loaded story '{story_title}' using legacy format")
                return story
                
        except Exception as e:
            self.logger.error(f"Failed to load story '{story_title}': {e}")
            return None

    def update_story(self, story: Story) -> None:
        """
        Updates an existing Story instance and saves changes.

        Args:
            story (Story): The Story instance to update.
        """
        self.save_story(story)
        self.logger.info(f"Story '{story.title}' updated to version {story.current_version_num}")

    def delete_story(self, story_title: str) -> bool:
        """
        Deletes a Story instance by its title.

        Args:
            story_title (str): The title of the story to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        sanitized_title = sanitize_string(story_title)
        story_dir = Path(settings.STORY_DIR, sanitized_title)
        if story_dir.exists():
            shutil.rmtree(story_dir)
            self.logger.info(f"Deleted story directory at {story_dir}")
            return True
        self.logger.warning(f"Story directory not found: {story_dir}")
        return False
    
    def get_synopsis(self, story: Story) -> str:
        """
        Builds and returns a synopsis for the story by combining the story's title, concept, and all its assets.

        Args:
            story (Story): The story object.

        Returns:
            str: The synopsis of the story.
        """
        self.logger.debug(f"Building synopsis for story: '{story.title}'\n"
                          f"Story assets: {story.assets}"
                          )
        
        synopsis = f"## Story Title:\n{story.title}\n"

        for key, asset in story.assets.items():
            if key in settings.SYNOPSIS_ASSET_TYPE:
                synopsis += f"## {asset.title}:\n{asset.summary}\n"
            
        self.logger.debug(f"Synopsis: \n{synopsis}")
        return synopsis
