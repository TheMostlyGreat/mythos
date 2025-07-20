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
                # Legacy format - assets stored as JSON strings
                legacy_assets = story_data.pop("assets", {})
                legacy_manuscript = story_data.pop("manuscript", {})
                
                # Create story without assets first
                story = Story(**story_data)
                
                # Load each asset from its JSON string and .asset file (legacy)
                for asset_key, asset_json_str in legacy_assets.items():
                    try:
                        asset_info = json.loads(asset_json_str)
                        asset_path = Path(story.story_dir, asset_info["relative_file_path"])
                        
                        if asset_path.exists():
                            asset = deserialize_from_json(str(asset_path), StoryAsset)
                            story.assets[asset_key] = asset
                            
                            # Create metadata for migration
                            story.asset_metadata[asset_key] = AssetMetadata(
                                asset_type=asset.asset_type,
                                title=asset.title,
                                summary=asset.summary,
                                relative_file_path=asset.relative_file_path
                            )
                        else:
                            self.logger.warning(f"Legacy asset file not found: {asset_path}")
                    except (json.JSONDecodeError, KeyError) as e:
                        self.logger.warning(f"Failed to parse legacy asset '{asset_key}': {e}")
                
                # Load legacy manuscript assets if any
                for manuscript_key, manuscript_json_str in legacy_manuscript.items():
                    try:
                        manuscript_info = json.loads(manuscript_json_str)
                        manuscript_path = Path(story.story_dir, manuscript_info["relative_file_path"])
                        
                        if manuscript_path.exists():
                            manuscript_asset = deserialize_from_json(str(manuscript_path), StoryAsset)
                            story.manuscript[manuscript_key] = manuscript_asset
                            
                            # Create metadata for migration
                            story.manuscript_metadata[manuscript_key] = AssetMetadata(
                                asset_type=manuscript_asset.asset_type,
                                title=manuscript_asset.title,
                                summary=manuscript_asset.summary,
                                relative_file_path=manuscript_asset.relative_file_path
                            )
                        else:
                            self.logger.warning(f"Legacy manuscript file not found: {manuscript_path}")
                    except (json.JSONDecodeError, KeyError) as e:
                        self.logger.warning(f"Failed to parse legacy manuscript '{manuscript_key}': {e}")
                
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
        
        For the concept asset, includes full details to preserve character names and key specifics.
        For other assets, uses summaries to keep the synopsis manageable.

        Args:
            story (Story): The story object.

        Returns:
            str: The synopsis of the story.
        """
        synopsis = f"## Story Title:\n{story.title}\n"

        for key, asset in story.assets.items():
            if key in settings.SYNOPSIS_ASSET_TYPE:
                # For concept, include full details to preserve character names and specifics
                if key == settings.AssetTypeNames.CONCEPT.value:
                    synopsis += f"## {asset.title}:\n{asset.details}\n"
                else:
                    # For other assets, use summaries to keep synopsis manageable
                    synopsis += f"## {asset.title}:\n{asset.summary}\n"
            
        return synopsis

    def get_story_state(self, story: Story) -> tuple[str, str]:
        """
        Determines the current completion state of a story to enable smart resumption.
        
        Args:
            story (Story): The story object to analyze.
            
        Returns:
            tuple[str, str]: A tuple of (state, description) where state is the key and description is user-friendly.
        """
        from mythos.config.settings import AssetTypeNames
        
        # Required planning assets (in order of generation)
        required_assets = [
            AssetTypeNames.CONCEPT.value,
            AssetTypeNames.RESEARCH.value, 
            AssetTypeNames.SETTINGS.value,
            AssetTypeNames.PLOT.value,
            AssetTypeNames.THEMES.value,
            AssetTypeNames.CHARACTERS.value,
            AssetTypeNames.TIMELINE.value,
            AssetTypeNames.CHAPTER_LIST.value,
            AssetTypeNames.WRITING_STYLE.value
        ]
        
        # Check if story has basic assets
        if not story.assets:
            return "empty", "Story has no assets (this shouldn't happen for existing stories)"
        
        # Check for missing planning assets
        missing_assets = []
        for asset_name in required_assets:
            if asset_name not in story.assets:
                missing_assets.append(asset_name)
        
        if missing_assets:
            return "assets_incomplete", f"Missing assets: {', '.join(missing_assets)}"
        
        # Check if chapter outlines exist
        chapter_outlines = {
            key: asset for key, asset in story.assets.items() 
            if asset.asset_type == AssetTypeNames.CHAPTER_OUTLINE.name
        }
        
        if not chapter_outlines:
            return "chapters_not_outlined", "Planning complete, but no chapter outlines exist"
        
        # Check manuscript chapters vs chapter outlines
        manuscript_chapters = {
            key: asset for key, asset in story.manuscript.items()
            if asset.asset_type == AssetTypeNames.MANUSCRIPT_CHAPTER.name
        }
        
        if not manuscript_chapters:
            return "chapters_not_written", f"Chapter outlines ready ({len(chapter_outlines)} chapters), but no manuscript chapters written"
        
        if len(manuscript_chapters) < len(chapter_outlines):
            return "chapters_partial", f"Writing in progress: {len(manuscript_chapters)}/{len(chapter_outlines)} chapters complete"
        
        # Check for final draft
        if not story.draft or not story.draft.exists():
            return "finalization_needed", "All chapters written, needs final draft compilation and EPUB creation"
        
        return "complete", "Story is fully complete with draft and EPUB"

    def get_story_progress_summary(self, story: Story) -> str:
        """
        Gets a user-friendly progress summary for display in menus.
        
        Args:
            story (Story): The story object.
            
        Returns:
            str: A concise progress description with emoji.
        """
        state, description = self.get_story_state(story)
        
        # Map states to user-friendly summaries with emojis
        progress_map = {
            "empty": "🔴 Empty",
            "assets_incomplete": "🟡 Planning in progress",
            "chapters_not_outlined": "🟡 Ready for chapter outlines", 
            "chapters_not_written": "🟠 Ready to write chapters",
            "chapters_partial": "🟠 Writing chapters",
            "finalization_needed": "🔵 Ready to finalize",
            "complete": "✅ Complete"
        }
        
        return progress_map.get(state, "❓ Unknown state")
