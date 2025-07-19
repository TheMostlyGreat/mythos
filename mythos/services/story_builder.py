from pathlib import Path
from mythos.story_asset import StoryAsset, StoryAssetManager, AssetMetadata
from mythos.story import Story, StoryManager
from mythos.config.settings import AssetTypes, AssetTypeNames
from mythos.services.writer import (
    generate_narrative_text, 
    generate_planning_text, 
    generate_character_list,
    generate_chapter_list,
    generate_story_concept,
    generate_web_enhanced_research,
    summarize_text
)
from mythos.utils.logger import get_logger
import json
from typing import Optional
from mythos.utils.epub import create_epub

class StoryBuildException(Exception):
    """Raised when story building process fails."""
    pass


class StoryBuilder:
    """
    Handles the business logic for building a story from a user prompt using the Snowflake method.
    
    The process includes generating the concept, related assets, and chapters by leveraging
    various managers and writer services.
    """

    def __init__(self):
        """
        Initializes the StoryBuilder with necessary managers.
        """
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug("Initializing StoryBuilder")
        self.story_manager = StoryManager()
        self.asset_manager = StoryAssetManager()

    def _create_asset_with_metadata(self, story: Story, asset: StoryAsset) -> None:
        """
        Creates an asset and populates both legacy and new metadata structures.
        
        Args:
            story (Story): The story object.
            asset (StoryAsset): The asset to create.
        """
        # Create markdown file
        self.asset_manager.create_asset(asset=asset, story_dir=story.story_dir, use_markdown=True)
        
        # Populate legacy assets dict
        story.assets[asset.title] = asset
        
        # Populate new metadata dict
        story.asset_metadata[asset.title] = AssetMetadata(
            asset_type=asset.asset_type,
            title=asset.title,
            summary=asset.summary,
            relative_file_path=asset.relative_file_path
        )

    def _create_manuscript_with_metadata(self, story: Story, asset: StoryAsset) -> None:
        """
        Creates a manuscript asset and populates both legacy and new metadata structures.
        
        Args:
            story (Story): The story object.
            asset (StoryAsset): The manuscript asset to create.
        """
        # Create markdown file
        self.asset_manager.create_asset(asset=asset, story_dir=story.story_dir, use_markdown=True)
        
        # Populate legacy manuscript dict
        story.manuscript[asset.title] = asset
        
        # Populate new metadata dict
        story.manuscript_metadata[asset.title] = AssetMetadata(
            asset_type=asset.asset_type,
            title=asset.title,
            summary=asset.summary,
            relative_file_path=asset.relative_file_path
        )

    def build_story(self, user_prompt: str, iterations: int = 1, stop_after_assets: bool = False) -> Story:
        """
        Constructs a complete story from a user prompt using iterative refinement.

        Args:
            user_prompt (str): The initial prompt provided by the user.
            iterations (int): Number of iterations to refine the story.
            stop_after_assets (bool): If True, stops after generating story assets without creating chapters.

        Returns:
            Story: The story object (complete or with assets only, depending on stop_after_assets).

        Raises:
            StoryBuildException: If the story building process fails.
        """
        self.logger.info(f"Building story from prompt: '{user_prompt}'")
        
        try:
            story = Story(user_prompt=user_prompt)
            # Generate concept asset and extract title
            concept_asset = self._generate_concept_asset(story)
            new_title = self._extract_title_from_concept()
            
            self.logger.debug(f"Concept created. Extracted story title: '{new_title}'")

            self.story_manager.set_story_title(story, new_title)
            
            self._create_asset_with_metadata(story, concept_asset)
            self.logger.debug(f"Added concept asset: '{concept_asset.title}'")

            self._generate_related_assets(story)
            
            # Stop here if requested (for user review of assets)
            if stop_after_assets:
                self.logger.info(f"Story assets generated for: '{story.title}'. Stopping for user review.")
                return story
            
            # Generate chapter structure and content
            self._generate_story_content(story)
            
            self.logger.info(f"Successfully built story: '{story.title}'")

            # Abstracted draft creation
            story.draft = self._create_manuscript_draft(story)

            create_epub(story)
            
            return story

        except Exception as e:
            self.logger.error(f"Failed to build story: {e}")
            raise StoryBuildException(f"Story building failed: {e}") from e

    def build_story_assets(self, user_prompt: str) -> Story:
        """
        Builds only the story assets (concept, characters, plot, etc.) without generating chapters.
        
        Args:
            user_prompt (str): The initial prompt provided by the user.
            
        Returns:
            Story: Story object with all assets generated but no chapters.
            
        Raises:
            StoryBuildException: If the story asset building process fails.
        """
        return self.build_story(user_prompt=user_prompt, stop_after_assets=True)
    
    def build_story_content(self, story: Story) -> Story:
        """
        Generates chapter structure and content for a story that already has assets.
        
        Args:
            story (Story): Story object with assets already generated.
            
        Returns:
            Story: Complete story object with chapters and manuscript.
            
        Raises:
            StoryBuildException: If the chapter building process fails.
        """
        self.logger.info(f"Building chapter content for story: '{story.title}'")
        
        try:
            # Generate chapter structure and content
            self._generate_story_content(story)
            
            self.logger.info(f"Successfully built story content: '{story.title}'")

            # Abstracted draft creation
            story.draft = self._create_manuscript_draft(story)

            create_epub(story)
            
            return story

        except Exception as e:
            self.logger.error(f"Failed to build story content: {e}")
            raise StoryBuildException(f"Story content building failed: {e}") from e

    def smart_resume_story(self, story: Story) -> Story:
        """
        Intelligently resumes story generation from its current state.
        
        Args:
            story (Story): Story object to resume.
            
        Returns:
            Story: Updated story object with progress from current state.
            
        Raises:
            StoryBuildException: If the resumption process fails.
        """
        self.logger.info(f"Smart resuming story: '{story.title}'")
        
        # Get current state
        state, description = self.story_manager.get_story_state(story)
        self.logger.info(f"Story state: {state} - {description}")
        
        try:
            if state == "assets_incomplete":
                # Continue generating missing planning assets
                self.logger.info("Continuing asset generation...")
                self._resume_asset_generation(story)
                
            elif state == "chapters_not_outlined":
                # Generate chapter outlines
                self.logger.info("Generating chapter outlines...")
                self.generate_chapter_assets(story)
                
            elif state in ["chapters_not_written", "chapters_partial"]:
                # Write remaining chapters
                self.logger.info("Writing manuscript chapters...")
                self._resume_chapter_writing(story)
                
            elif state == "finalization_needed":
                # Create final draft and EPUB
                self.logger.info("Finalizing story...")
                story.draft = self._create_manuscript_draft(story)
                create_epub(story)
                
            elif state == "complete":
                self.logger.info("Story is already complete!")
                return story
                
            else:
                raise StoryBuildException(f"Unknown story state: {state}")
                
            # Always save progress
            self.story_manager.update_story(story)
            self.logger.info(f"Successfully resumed story: '{story.title}'")
            
            return story
            
        except Exception as e:
            self.logger.error(f"Failed to resume story: {e}")
            raise StoryBuildException(f"Story resumption failed: {e}") from e

    def _resume_asset_generation(self, story: Story) -> None:
        """
        Resumes asset generation from where it left off.
        
        Args:
            story (Story): The story object.
        """
        from mythos.config.settings import AssetTypeNames
        
        # Define the full asset generation sequence
        asset_sequence = [
            AssetTypeNames.CONCEPT,  # Should already exist for existing stories
            AssetTypeNames.RESEARCH,
            AssetTypeNames.SETTINGS,
            AssetTypeNames.PLOT,
            AssetTypeNames.THEMES,
            AssetTypeNames.CHARACTERS,
            AssetTypeNames.TIMELINE,
            AssetTypeNames.CHAPTER_LIST,
            AssetTypeNames.WRITING_STYLE
        ]
        
        # Find where to start (skip assets that already exist)
        for asset_type in asset_sequence:
            if asset_type.value not in story.assets:
                self.logger.info(f"Generating missing asset: {asset_type.value}")
                asset = self._create_single_asset(story, asset_type)
                self._create_asset_with_metadata(story, asset)
                self.story_manager.update_story(story)
                self.logger.debug(f"Generated and added asset: '{asset.title}'")

    def _resume_chapter_writing(self, story: Story) -> None:
        """
        Resumes chapter writing from where it left off.
        
        Args:
            story (Story): The story object.
        """
        from mythos.config.settings import AssetTypeNames
        
        # Get all chapter outlines
        chapter_outlines = {
            key: asset for key, asset in story.assets.items() 
            if asset.asset_type == AssetTypeNames.CHAPTER_OUTLINE.name
        }
        
        # Get existing manuscript chapters
        existing_chapters = {
            key: asset for key, asset in story.manuscript.items()
            if asset.asset_type == AssetTypeNames.MANUSCRIPT_CHAPTER.name
        }
        
        if not chapter_outlines:
            # Need to generate chapter outlines first
            self.logger.info("No chapter outlines found, generating them first...")
            self.generate_chapter_assets(story)
            chapter_outlines = {
                key: asset for key, asset in story.assets.items() 
                if asset.asset_type == AssetTypeNames.CHAPTER_OUTLINE.name
            }
        
        # Write only the missing chapters
        chapters_to_write = {
            key: asset for key, asset in chapter_outlines.items()
            if key not in existing_chapters
        }
        
        if chapters_to_write:
            self.logger.info(f"Writing {len(chapters_to_write)} remaining chapters...")
            self._write_specific_chapters(story, chapters_to_write)
        else:
            self.logger.info("All chapters are already written")

    def _write_specific_chapters(self, story: Story, chapters_to_write: dict) -> None:
        """
        Writes specific chapter outlines to manuscript chapters.
        
        Args:
            story (Story): The story object.
            chapters_to_write (dict): Dictionary of chapter outlines to write.
        """
        from mythos.config.settings import AssetTypeNames, AssetTypes
        from mythos.services.writer import generate_narrative_text, summarize_text
        import json
        
        synopsis = self.story_manager.get_synopsis(story)
        writing_style = story.assets.get(AssetTypeNames.WRITING_STYLE.value).summary if story.assets.get(AssetTypeNames.WRITING_STYLE.value) else ""
        
        # Get existing story context
        existing_chapters = {
            key: asset for key, asset in story.manuscript.items()
            if asset.asset_type == AssetTypeNames.MANUSCRIPT_CHAPTER.name
        }
        
        # Build story so far from existing chapters
        story_so_far = ""
        for _, existing_chapter in sorted(existing_chapters.items(), key=lambda x: int(''.join(filter(str.isdigit, x[0])))):
            story_so_far += existing_chapter.summary
        
        # Get chapter data from chapter list
        chapter_list_asset = story.assets.get(AssetTypeNames.CHAPTER_LIST.value)
        if chapter_list_asset:
            try:
                if isinstance(chapter_list_asset.details, str) and chapter_list_asset.details.startswith('{'):
                    chapter_list_data = json.loads(chapter_list_asset.details)
                else:
                    chapter_list_data = chapter_list_asset.details
                    if isinstance(chapter_list_data, str):
                        chapter_list_data = json.loads(chapter_list_data)
                
                chapters = chapter_list_data.get("chapters", [])
                chapters_data = {f"chapter_{ch['chapter_number']}": ch for ch in chapters}
            except (json.JSONDecodeError, TypeError):
                chapters_data = {}
        else:
            chapters_data = {}
        
        # Sort chapters to write in order
        sorted_chapters = sorted(chapters_to_write.items(), key=lambda x: int(''.join(filter(str.isdigit, x[0]))))
        
        for chapter_title, chapter_asset in sorted_chapters:
            self.logger.info(f"Writing narrative for '{chapter_title}'")
            
            try:
                # Get chapter details from the original chapter list
                chapter_details = chapters_data.get(chapter_title)
                if not chapter_details:
                    self.logger.warning(f"No chapter data found for '{chapter_title}', using outline as fallback")
                    chapter_details = {"outline": chapter_asset.details, "title": chapter_title}
                
                chapter_prompt = self._build_chapter_prompt(
                    synopsis=synopsis,
                    chapter_details=chapter_details,
                    writing_style=writing_style if writing_style else "",
                    story_so_far=story_so_far,
                    chapter_title=chapter_title
                )

                chapter_text = generate_narrative_text(prompt=chapter_prompt)
                
                if not chapter_text or chapter_text.startswith("Error:"):
                    raise ValueError(f"Failed to generate valid content for '{chapter_title}': {chapter_text}")

                chapter_summary = summarize_text(
                    text=chapter_text,
                    summary_length=AssetTypes.MANUSCRIPT_CHAPTER.summary_length
                )

                manuscript_asset = StoryAsset(
                    asset_type=AssetTypeNames.MANUSCRIPT_CHAPTER.name,
                    title=chapter_title,
                    details=chapter_text,
                    summary=chapter_summary,
                    relative_file_path=Path(AssetTypes.MANUSCRIPT_CHAPTER.directory, f"{chapter_title}.md")
                )

                self._create_manuscript_with_metadata(story, manuscript_asset)
                
                # Update story so far for next chapter
                story_so_far += chapter_summary
                
                self.logger.info(f"Successfully wrote '{chapter_title}'")

            except Exception as e:
                self.logger.error(f"Failed to write '{chapter_title}': {e}")
                raise StoryBuildException(f"Failed to write '{chapter_title}': {e}") from e

    def _generate_concept_asset(self, story: Story) -> StoryAsset:
        """
        Creates the initial concept asset with reliable title extraction.

        Args:
            story (Story): The story object.

        Returns:
            StoryAsset: The generated concept asset.
        """
        prompt = self._assemble_planning_prompt(story, AssetTypes.CONCEPT)
        
        try:
            # Get structured JSON with title + markdown content
            concept_json = generate_story_concept(prompt=prompt)
            concept_data = json.loads(concept_json)
            
            # Extract title and markdown separately
            title = concept_data.get('title', 'Untitled Story')
            markdown_content = concept_data.get('concept_markdown', '')
            
            # Store the extracted title for later use
            self._extracted_title = title
            
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.warning(f"Failed to parse concept JSON, falling back to direct generation: {e}")
            # Fallback to direct markdown generation
            markdown_content = concept_json if concept_json else "# Concept\n\nFailed to generate concept."
            self._extracted_title = "Untitled Story"
        
        summary = summarize_text(text=markdown_content, summary_length=AssetTypes.CONCEPT.summary_length)
        
        concept_asset = StoryAsset(
            asset_type=AssetTypeNames.CONCEPT.name,
            title=AssetTypes.CONCEPT.title,
            summary=summary,
            details=markdown_content,  # Use the markdown content
            relative_file_path=Path(AssetTypes.CONCEPT.directory, f"{AssetTypes.CONCEPT.title}.md")
        )
        
        return concept_asset

    def _generate_related_assets(self, story: Story) -> None:
        """
        Generates all related story assets sequentially.

        Args:
            story (Story): The story object.
        """
        asset_types = [
            AssetTypeNames.RESEARCH,
            AssetTypeNames.SETTINGS,
            AssetTypeNames.PLOT,
            AssetTypeNames.THEMES,
            AssetTypeNames.CHARACTERS,
            AssetTypeNames.TIMELINE,
            AssetTypeNames.CHAPTER_LIST,
            AssetTypeNames.WRITING_STYLE
        ]
        
        for asset_type in asset_types:
            asset = self._create_single_asset(story, asset_type)
            self._create_asset_with_metadata(story, asset)
            self.story_manager.update_story(story)
            self.logger.debug(f"Generated and added asset: '{asset.title}'")
            
        return story

    def _create_single_asset(self, story: Story, asset_type_enum: AssetTypeNames) -> StoryAsset:
        """
        Creates a single story asset of the specified type.

        Args:
            story (Story): The story object.
            asset_type_enum (AssetTypeNames): The type of asset to create.

        Returns:
            StoryAsset: The created story asset.
        """
        asset_type = getattr(AssetTypes, asset_type_enum.name)
        prompt = self._assemble_planning_prompt(story, asset_type)
        
        # Use Structured Outputs for specific asset types that need reliable JSON
        if asset_type_enum == AssetTypeNames.CHARACTERS:
            asset_text = generate_character_list(prompt=prompt)
        elif asset_type_enum == AssetTypeNames.CHAPTER_LIST:
            asset_text = generate_chapter_list(prompt=prompt)
        elif asset_type_enum == AssetTypeNames.RESEARCH:
            # Use web-enhanced research for research assets
            asset_text = generate_web_enhanced_research(prompt=prompt)
        else:
            # Use regular planning text for other asset types
            asset_text = generate_planning_text(prompt=prompt)
            
        summary = summarize_text(text=asset_text, summary_length=asset_type.summary_length)
        
        asset = StoryAsset(
            asset_type=asset_type_enum.name,
            title=asset_type.title,
            summary=summary,
            details=asset_text,
            relative_file_path=Path(asset_type.directory, f"{asset_type.title}.md")
        )
        
        return asset

    def _assemble_planning_prompt(self, story: Story, asset_type: AssetTypes, current_asset: Optional[StoryAsset] = None) -> str:
        """
        Assembles a prompt for the writer service to generate a planning asset.

        Args:
            story (Story): The story object.
            asset_type (AssetTypes): The type of asset to generate.
            current_asset (Optional[StoryAsset]): Existing asset to refine.

        Returns:
            str: The assembled prompt.
        """
        self.logger.debug(f"Assembling prompt for asset type: '{asset_type.title}'")
        
        template_text = Path(asset_type.template_path).read_text()
        current_asset_section = f"## Current version of the asset:\n{current_asset.details}\n" if current_asset else ""
        
        prompt = (
            f"## User Prompt:\n{story.user_prompt}\n"
            f"## Story Synopsis:\n{self.story_manager.get_synopsis(story)}\n"
            f"## Template for '{asset_type.title}':\n{template_text}\n"
            f"{current_asset_section}"
            f"## Prompt:\nPlease create or refine a '{asset_type.title}' for this story using the template.\n"
            "Focus on clarity, brevity, and specificity.\n"
        )
        
        self.logger.debug("Planning prompt assembled.")
        return prompt

    def _extract_title_from_concept(self) -> str:
        """
        Returns the title extracted from structured concept JSON.

        Returns:
            str: The extracted title.
        """
        try:
            return getattr(self, '_extracted_title', 'Untitled Story')
        except Exception as e:
            self.logger.warning(f"Failed to get extracted title: {e}")
            return "Untitled Story"

    def generate_chapter_assets(self, story: Story) -> Story:
        """
        Generates chapter assets based on the chapter list.

        Args:
            story (Story): The story object.
        """
        chapter_list_asset = story.assets.get(AssetTypeNames.CHAPTER_LIST.value)
        if not chapter_list_asset:
            self.logger.error("Chapter list asset is missing.")
            raise StoryBuildException("Chapter list asset is missing.")

        try:
            # Handle both legacy and new chapter list formats
            if isinstance(chapter_list_asset.details, str) and chapter_list_asset.details.startswith('{'):
                # Legacy format: details is a JSON string containing the chapter data
                chapter_list_data = json.loads(chapter_list_asset.details)
            else:
                # New format: details is already the chapter data
                chapter_list_data = chapter_list_asset.details
                if isinstance(chapter_list_data, str):
                    chapter_list_data = json.loads(chapter_list_data)
            
            synopsis = self.story_manager.get_synopsis(story)
            
            # Handle different chapter data formats
            chapters = chapter_list_data.get("chapters", [])
            
            # If no chapters found at top level, check if chapters are in a nested details field (legacy format)
            if not chapters and "details" in chapter_list_data:
                try:
                    nested_details = json.loads(chapter_list_data["details"])
                    chapters = nested_details.get("chapters", [])
                except (json.JSONDecodeError, TypeError):
                    pass
            
            if not chapters:
                self.logger.error("No chapters found in chapter list.")
                self.logger.debug(f"Chapter list data structure: {chapter_list_data}")
                raise StoryBuildException("No chapters found in chapter list.")
            
            for chapter_data in chapters:
                chapter_num = chapter_data.get("chapter_number")
                if chapter_num is None:
                    self.logger.warning(f"Chapter missing chapter_number, skipping: {chapter_data}")
                    continue
                self.generate_chapter_outline(story, chapter_num, chapter_data, synopsis)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in chapter list: {e}")
            raise StoryBuildException("Invalid JSON in chapter list.") from e
        except Exception as e:
            self.logger.error(f"Error generating chapter assets: {e}")
            raise StoryBuildException("Error generating chapter assets.") from e
        
        return story

    def write_chapters(self, story: Story) -> StoryAsset:
        """
        Writes narrative content for all chapter outlines in the story.

        Args:
            story (Story): The story object containing chapter outlines.

        Returns:
            StoryAsset: The last processed chapter asset.

        Raises:
            StoryBuildException: If chapter writing fails.
        """
        self.logger.debug("Starting chapter narrative writing process.")
        
        synopsis = self.story_manager.get_synopsis(story)
        writing_style = story.assets.get(AssetTypeNames.WRITING_STYLE.value).summary if story.assets.get(AssetTypeNames.WRITING_STYLE.value) else ""
        chapter_assets = {
            title: asset for title, asset in story.assets.items()
            if asset.asset_type == AssetTypeNames.CHAPTER_OUTLINE.name
        }
        
        if not chapter_assets:
            raise StoryBuildException("No manuscript chapter assets found.")

        # Get the original chapter data from the chapter list JSON
        chapter_list_asset = story.assets.get(AssetTypeNames.CHAPTER_LIST.value)
        if not chapter_list_asset:
            raise StoryBuildException("Chapter list asset is missing.")
        
        try:
            # Handle both legacy and new chapter list formats
            if isinstance(chapter_list_asset.details, str) and chapter_list_asset.details.startswith('{'):
                # Legacy format: details is a JSON string containing the chapter data
                chapter_list_data = json.loads(chapter_list_asset.details)
            else:
                # New format: details is already the chapter data
                chapter_list_data = chapter_list_asset.details
                if isinstance(chapter_list_data, str):
                    chapter_list_data = json.loads(chapter_list_data)
            
            # Handle different chapter data formats 
            chapters = chapter_list_data.get("chapters", [])
            
            # If no chapters found at top level, check if chapters are in a nested details field (legacy format)
            if not chapters and "details" in chapter_list_data:
                try:
                    nested_details = json.loads(chapter_list_data["details"])
                    chapters = nested_details.get("chapters", [])
                except (json.JSONDecodeError, TypeError):
                    pass
                    
            chapters_data = {f"chapter_{ch['chapter_number']}": ch for ch in chapters}
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in chapter list: {e}")
            raise StoryBuildException("Invalid JSON in chapter list.") from e

        sorted_chapters = sorted(
            chapter_assets.items(),
            key=lambda x: int(''.join(filter(str.isdigit, x[0])))
        )

        story_so_far = ""

        for chapter_title, chapter_asset in sorted_chapters:
            self.logger.debug(f"Writing narrative for '{chapter_title}'")

            story_so_far += chapter_asset.summary
            
            try:
                # Use the original chapter data from the chapter list instead of parsing the markdown outline
                chapter_details = chapters_data.get(chapter_title)
                if not chapter_details:
                    self.logger.warning(f"No chapter data found for '{chapter_title}', using outline as fallback")
                    # Fallback to using the markdown outline
                    chapter_details = {"outline": chapter_asset.details, "title": chapter_title}
                
                chapter_prompt = self._build_chapter_prompt(
                    synopsis=synopsis,
                    chapter_details=chapter_details,
                    writing_style=writing_style if writing_style else "",
                    story_so_far=story_so_far,
                    chapter_title=chapter_title
                )

                chapter_text = generate_narrative_text(prompt=chapter_prompt)
                
                # Handle Claude 4 refusal responses
                if chapter_text and chapter_text.startswith("Error: Content generation was declined"):
                    self.logger.warning(f"Claude refused to generate content for '{chapter_title}'. Trying with modified prompt.")
                    # You could implement prompt modification logic here if needed
                    chapter_text = f"[Chapter content declined for safety reasons - please review and regenerate manually]"
                
                if not chapter_text or chapter_text.startswith("Error:"):
                    raise ValueError(f"Failed to generate valid content for '{chapter_title}': {chapter_text}")

                chapter_summary = summarize_text(
                    text=chapter_text,
                    summary_length=AssetTypes.MANUSCRIPT_CHAPTER.summary_length
                )

                manuscript_asset = StoryAsset(
                    asset_type=AssetTypeNames.MANUSCRIPT_CHAPTER.name,
                    title=chapter_title,
                    details=chapter_text,
                    summary=chapter_summary,
                    relative_file_path=Path(AssetTypes.MANUSCRIPT_CHAPTER.directory, f"{chapter_title}.md")
                )

                self._create_manuscript_with_metadata(story, manuscript_asset)

                self.logger.debug(f"Narrative for '{chapter_title}' written successfully.")

            except ValueError as e:
                self.logger.error(e)
                raise StoryBuildException(e) from e
            except Exception as e:
                self.logger.error(f"Unexpected error in '{chapter_title}': {e}")
                raise StoryBuildException(f"Unexpected error in '{chapter_title}': {e}") from e
        try:
            self.story_manager.update_story(story)
            self.logger.debug("All chapters saved to the story.")
        except Exception as e:
            self.logger.error(f"Failed to save story updates: {e}")
            raise StoryBuildException(f"Failed to save story updates: {e}") from e
        
        return chapter_asset

    def generate_chapter_outline(self, story: Story, chapter_num: int, chapter_data: dict, synopsis: str) -> StoryAsset:
        """
        Generates and saves a chapter outline.

        Args:
            story (Story): The story object.
            chapter_num (int): The chapter number.
            chapter_data (dict): Data for the chapter.
            synopsis (str): The story synopsis.
        """
        self.logger.debug(f"Generating outline for Chapter {chapter_num}")
        
        chapter_title = f"chapter_{chapter_num}"        

        chapter_asset = StoryAsset(
            asset_type=AssetTypeNames.CHAPTER_OUTLINE.name,
            title=chapter_title,
            relative_file_path=Path(AssetTypes.CHAPTER_OUTLINE.directory, f"{chapter_title}.md")
        )

        template_text = Path(AssetTypes.CHAPTER_OUTLINE.template_path).read_text()
        chapter_prompt = (
            f"## Story Synopsis:\n{synopsis}\n"
            f"## Chapter Data:\n{chapter_data}\n"
            "## Template:\n"
            f"{template_text}\n"
        )

        chapter_asset.details = generate_planning_text(prompt=chapter_prompt)
        chapter_asset.summary = summarize_text(
            text=chapter_asset.details,
            summary_length=AssetTypes.CHAPTER_OUTLINE.summary_length
        )

        self._create_asset_with_metadata(story, chapter_asset)
        self.story_manager.update_story(story)
        self.logger.debug(f"Chapter {chapter_num} outline generated and saved.")
        
        return chapter_asset
    
    def _generate_story_content(self, story: Story) -> Story:
        """Generates chapter structure and content."""
        self.generate_chapter_assets(story)
        self.write_chapters(story)
        return story

    def _build_chapter_prompt(self, synopsis: str, chapter_details: dict, writing_style: str, story_so_far: str, chapter_title: str) -> str:
        """
        Builds a prompt for generating chapter narrative content.

        Args:
            synopsis (str): The story synopsis.
            chapter_details (dict): Details about the chapter.
            writing_style (str): The writing style guidelines.
            story_so_far (str): Summary of the story up to this point.
            chapter_title (str): The title of the chapter.

        Returns:
            str: The assembled chapter prompt.
        """
        prompt = (
            f"## Story Synopsis:\n{synopsis}\n\n"
            f"## Writing Style:\n{writing_style}\n\n"
            f"## Story So Far:\n{story_so_far}\n\n"
            f"## Chapter Details:\n{json.dumps(chapter_details, indent=2)}\n\n"
            f"## Prompt:\n"
            f"Write the narrative content for '{chapter_title}' based on the chapter details above. "
            f"Follow the established writing style and ensure continuity with the story so far. "
            f"Output in markdown format.\n"
        )
        
        return prompt

    def _create_manuscript_draft(self, story: Story) -> Path:
        """
        Compiles all manuscript chapters into a complete draft and saves it as a markdown file.

        Args:
            story (Story): The story object.

        Returns:
            Path: The path to the complete manuscript draft markdown file.
        """
        self.logger.debug("Combining all manuscript chapters into draft.")
        draft_content = ""
        
        # Iterate through all assets in the story
        for asset_key, asset in story.manuscript.items():
            # Only process manuscript chapter assets
            if asset.asset_type == AssetTypeNames.MANUSCRIPT_CHAPTER.name:
                self.logger.debug(f"Adding chapter content from {asset.title}")
                draft_content += f"\n\n{asset.details}\n\n"
        
        self.logger.debug(f"Draft content: {draft_content}")
        
        # Define the directory and file name for the draft markdown
        draft_directory = Path(story.story_dir, AssetTypes.MANUSCRIPT_DRAFT.directory)
        draft_file_name = "draft.md"
        draft_file_path = draft_directory / draft_file_name
        
        try:
            # Ensure the draft directory exists
            draft_directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Draft directory ensured at: {draft_directory}")
            
            # Write the compiled content to the markdown file
            draft_file_path.write_text(draft_content.strip(), encoding='utf-8')

            self.logger.info(f"Created complete manuscript draft markdown file at {draft_file_path}")
        except Exception as e:
            self.logger.error(f"Failed to write draft markdown file: {e}")
            raise StoryBuildException(f"Failed to write draft markdown file: {e}") from e
        
        return draft_file_path
