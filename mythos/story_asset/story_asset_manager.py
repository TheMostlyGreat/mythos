import os
from typing import Optional
from pathlib import Path
from mythos.story_asset import StoryAsset, AssetMetadata
from mythos.utils.logger import get_logger
from mythos.utils.data_utils import (
    serialize_to_json, 
    deserialize_from_json, 
    get_asset_type, 
    sanitize_string
)

class StoryAssetManager:
    """
    Manages CRUD operations for StoryAsset instances, including persistence to the filesystem.
    """

    def __init__(self):
        """
        Initializes the StoryAssetManager with the base directory for storing asset files.

        Args:
            base_dir (str): Base directory path for storing all story assets.
        """
        self.logger = get_logger(self.__class__.__name__)

    def create_asset(self, asset: StoryAsset, story_dir: str, use_markdown: bool = True) -> None:
        """
        Creates a new asset by writing content to a markdown file or JSON file (legacy).
        
        Args:
            asset (StoryAsset): The asset to create.
            story_dir (str): The directory where the story is stored.
            use_markdown (bool): If True, write content to .md file. If False, use legacy .asset format.
        """
        # Define the path for the asset
        asset_path = Path(story_dir, asset.relative_file_path)
        
        # Ensure the assets directory exists
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        
        if use_markdown:
            # Write only the content to markdown file
            if asset.details:
                asset_path.write_text(asset.details, encoding='utf-8')
                self.logger.info(f"Asset content '{asset.title}' written to markdown file: {asset_path}")
            else:
                self.logger.warning(f"Asset '{asset.title}' has no content to write")
        else:
            # Legacy: Serialize the full asset to JSON
            serialize_to_json(asset, asset_path)
            self.logger.info(f"Asset '{asset.title}' of type '{asset.asset_type}' created as JSON file.")

    def get_asset_content(self, asset_metadata: AssetMetadata, story_dir: str) -> str:
        """
        Retrieves asset content from markdown file using metadata.

        Args:
            asset_metadata (AssetMetadata): Metadata for the asset.
            story_dir (str): The directory where the story is stored.

        Returns:
            str: The asset content or empty string if not found.
        """
        try:
            asset_path = Path(story_dir, asset_metadata.relative_file_path)
            if asset_path.exists():
                return asset_path.read_text(encoding='utf-8')
            else:
                self.logger.warning(f"Asset file not found: {asset_path}")
                return ""
        except Exception as e:
            self.logger.error(f"Failed to read asset content from {asset_path}: {e}")
            return ""

    def create_story_asset_from_metadata(self, asset_metadata: AssetMetadata, content: str) -> StoryAsset:
        """
        Creates a StoryAsset object from metadata and content.

        Args:
            asset_metadata (AssetMetadata): The asset metadata.
            content (str): The asset content.

        Returns:
            StoryAsset: The reconstructed story asset.
        """
        return StoryAsset(
            asset_type=asset_metadata.asset_type,
            title=asset_metadata.title,
            summary=asset_metadata.summary,
            details=content,
            relative_file_path=asset_metadata.relative_file_path
        )

    def get_asset(self, asset_type: str, title: str) -> Optional[StoryAsset]:
        """
        Retrieves a StoryAsset by its type and name (legacy method for backward compatibility).

        Args:
            asset_type (str): The type of the asset.
            title (str): The title of the asset to retrieve.

        Returns:
            Optional[StoryAsset]: The retrieved StoryAsset or None if not found.
        """
        try:
            asset_type_enum = get_asset_type(asset_type)
            asset_dir = asset_type_enum.directory
            sanitized_title = sanitize_string(title)
            
            # Try new .md format first
            md_path = Path(asset_dir) / f"{sanitized_title}.md"
            if md_path.exists():
                content = md_path.read_text(encoding='utf-8')
                # For legacy compatibility, create a basic StoryAsset
                return StoryAsset(
                    asset_type=asset_type,
                    title=title,
                    details=content,
                    relative_file_path=md_path
                )
            
            # Fallback to legacy .asset format
            asset_path = Path(asset_dir) / f"{sanitized_title}.asset"
            if asset_path.exists():
                return deserialize_from_json(asset_path, StoryAsset)
                
            return None
        except Exception:
            return None

    def update_asset(self, asset_type: str, name: str, **updates) -> bool:
        """
        Updates an existing StoryAsset with provided fields.

        Args:
            asset_type (str): The type of the asset.
            name (str): The name of the asset to update.
            **updates: Key-value pairs of fields to update.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        asset = self.get_asset(asset_type, name)
        if not asset:
            return False
        
        for key, value in updates.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
            else:
                self.logger.warning(f"Attribute '{key}' does not exist on StoryAsset.")
        
        # Handle renaming if 'name' is updated
        if 'name' in updates:
            new_sanitized_name = sanitize_string(asset.name)
            old_sanitized_name = sanitize_string(name)
            if new_sanitized_name != old_sanitized_name:
                asset_dir = self._get_asset_dir(asset.asset_type)
                # Try both .md and .asset extensions
                for ext in ['.md', '.asset']:
                    old_asset_path = os.path.join(asset_dir, f"{old_sanitized_name}{ext}")
                    new_asset_path = os.path.join(asset_dir, f"{new_sanitized_name}{ext}")
                    if os.path.exists(old_asset_path):
                        os.rename(old_asset_path, new_asset_path)
                        self.logger.info(f"Asset renamed from '{old_sanitized_name}{ext}' to '{new_sanitized_name}{ext}'.")
                        break

        # Save the updated asset (detect format based on file extension)
        self.create_asset(asset, use_markdown=str(asset.relative_file_path).endswith('.md'))
        self.logger.info(f"Asset '{asset.name}' of type '{asset.asset_type}' updated successfully.")
        return True

    def _get_asset_dir(self, asset_type: str) -> str:
        """Helper method to get asset directory (legacy compatibility)."""
        try:
            asset_type_enum = get_asset_type(asset_type)
            return asset_type_enum.directory
        except ValueError:
            return "assets"  # fallback

    def delete_asset(self, asset_type: str, name: str) -> bool:
        """
        Deletes a StoryAsset by its type and name.

        Args:
            asset_type (str): The type of the asset.
            name (str): The name of the asset to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            asset_type_enum = get_asset_type(asset_type)
            asset_dir = asset_type_enum.directory
            sanitized_name = sanitize_string(name)
            
            # Try to delete both .md and .asset files
            deleted = False
            for ext in ['.md', '.asset']:
                asset_path = Path(asset_dir) / f"{sanitized_name}{ext}"
                if asset_path.exists():
                    asset_path.unlink()
                    self.logger.info(f"Deleted asset at {asset_path}")
                    deleted = True
            
            if not deleted:
                self.logger.warning(f"Asset file not found for '{name}' of type '{asset_type}'")
            return deleted
        except Exception as e:
            self.logger.error(f"Failed to delete asset '{name}': {e}")
            return False
    