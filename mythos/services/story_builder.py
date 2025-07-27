from pathlib import Path
from mythos.story_asset import StoryAsset, StoryAssetManager, AssetMetadata
from mythos.story import Story, StoryManager
from mythos.config.settings import (
    AssetTypes, AssetTypeNames, CRITICAL_PERSPECTIVES_SCHEMA, CRITICAL_ANALYSIS_DIR,
    META_TEMPLATE_PATH, TEMPLATE_SUBDIR
)
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
from typing import Optional, List, Dict
from mythos.utils.epub import create_epub
import concurrent.futures
import re
from mythos.utils.llm_utils import call_llm, call_OpenAI_API, create_messages, ContentRefusalError

# Import UI utilities from shared utils
from mythos.utils.ui_utils import print_thinking, print_progress_step, complete_progress_step, confirm_next_step

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
        self.story_manager = StoryManager()
        self.asset_manager = StoryAssetManager()

    @staticmethod
    def _make_safe_filename(name: str) -> str:
        """Create a safe filename from a perspective name."""
        return re.sub(r'[^\w\-_]', '_', name.lower().replace(" ", "_"))

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
            complete_progress_step("Story Concept", f"Created concept for '{new_title}'")

            # Step 1 Complete: Concept generated
            # Ask if user wants to continue to assets generation
            if not confirm_next_step(
                current_step="Story concept created",
                next_step="Generate planning assets (characters, settings, plot, etc.)",
                story_title=story.title
            ):
                return story

            self._generate_related_assets(story)
            
            # Set baseline for change detection after asset generation
            self.story_manager.update_asset_baseline(story)
            
            # Step 2 Complete: Assets generated
            # Stop here if requested (for user review of assets)
            if stop_after_assets:
                self.logger.info(f"Stopping after asset generation as requested: '{story.title}'")
                return story

            # Ask before continuing to story generation (chapters + content)
            if not confirm_next_step(
                current_step="Planning assets complete",
                next_step="Generate story content (outlines and chapters)",
                story_title=story.title
            ):
                return story

            # Generate story content (outlines and chapters)
            story = self._generate_story_content(story)

            self.story_manager.update_story(story)
            self.logger.info(f"Successfully built story: '{story.title}'")
            
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
                # Ask before continuing asset generation
                if not confirm_next_step(
                    current_step="Story partially complete",
                    next_step="Continue generating missing planning assets",
                    story_title=story.title
                ):
                    return story
                    
                self.logger.info("Continuing asset generation...")
                print_progress_step("Resume Assets", "Continuing generation of missing planning assets")
                self._resume_asset_generation(story)
                complete_progress_step("Resume Assets", "Missing planning assets completed")
                
            elif state == "chapters_not_outlined":
                # Ask before generating chapter outlines
                if not confirm_next_step(
                    current_step="Planning assets complete",
                    next_step="Generate chapter outlines",
                    story_title=story.title
                ):
                    return story
                    
                self.logger.info("Generating chapter outlines...")
                print_progress_step("Chapter Outlines", "Generating chapter structure and outlines")
                self.generate_chapter_assets(story)
                complete_progress_step("Chapter Outlines", "All chapter outlines completed")
                
            elif state in ["chapters_not_written", "chapters_partial"]:
                # Ask before writing chapters
                chapter_status = "some chapters written" if state == "chapters_partial" else "chapter outlines ready"
                if not confirm_next_step(
                    current_step=f"Story ready for writing ({chapter_status})",
                    next_step="Write remaining manuscript chapters",
                    story_title=story.title
                ):
                    return story
                    
                self.logger.info("Writing manuscript chapters...")
                print_progress_step("Chapter Writing", "Writing remaining manuscript chapters")
                self._resume_chapter_writing(story)
                complete_progress_step("Chapter Writing", "All chapters completed")
                
            elif state == "finalization_needed":
                # Ask before finalizing
                if not confirm_next_step(
                    current_step="All chapters written",
                    next_step="Create final draft and EPUB",
                    story_title=story.title
                ):
                    return story
                    
                self.logger.info("Finalizing story...")
                print_progress_step("Final Draft", "Creating final manuscript and EPUB file")
                story.draft = self._create_manuscript_draft(story)
                create_epub(story)
                complete_progress_step("Final Draft", "Story completed and EPUB created")
                
            elif state == "complete":
                self.logger.info("Story is already complete!")
                return story
                
            else:
                raise StoryBuildException(f"Unknown story state: {state}")
                
            # Always save progress and update baseline
            self.story_manager.update_story(story)
            self.story_manager.update_asset_baseline(story)
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
            AssetTypeNames.CRITICAL_PERSPECTIVES,
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
                
        # Check if deep dive research is needed
        if self.analyze_research_depth_needs(story):
            print_progress_step("Deep Dive Research", "Generating detailed research for complex topics")
            self.generate_deep_dive_research(story)
            complete_progress_step("Deep Dive Research", "Deep dive research completed")
            
        # Check if deep dive settings are needed  
        if self.analyze_settings_depth_needs(story):
            print_progress_step("Deep Dive Settings", "Generating detailed world-building settings")
            self.generate_deep_dive_settings(story)
            complete_progress_step("Deep Dive Settings", "Deep dive settings completed")

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

                # Extract chapter number for progress display
                chapter_num = self._extract_chapter_number(chapter_title)
                total_chapters = len(chapters_to_write)
                
                # Show chapter-specific progress
                from mythos.utils.progress_tracker import get_progress_tracker
                tracker = get_progress_tracker()
                tracker.show_chapter_progress(chapter_num, total_chapters, chapter_title)
                
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
        
        print_progress_step("Story Concept", "Analyzing your story idea and creating the concept")
        
        try:
            # Get structured JSON with title + markdown content
            concept_json = generate_story_concept(prompt=prompt)
            concept_data = json.loads(concept_json)
            
            # Extract title and markdown separately
            title = concept_data.get('title', 'Untitled Story')
            markdown_content = concept_data.get('concept_markdown', '')
            
            # Store the extracted title for later use
            self._extracted_title = title
            
        except ContentRefusalError as e:
            # Content was refused by AI safety policies - stop story creation
            self.logger.error(f"Story concept creation refused: {e}")
            raise StoryBuildException(f"Unable to create story concept: {e}") from e
            
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
            
            # After generating baseline research, create deep dive research
            if asset_type == AssetTypeNames.RESEARCH:
                self.logger.info("Baseline research complete. Analyzing need for deep dive research...")
                try:
                    self.generate_deep_dive_research(story)
                    self.logger.info("Deep dive research generation completed")
                except Exception as e:
                    self.logger.warning(f"Deep dive research generation failed, continuing with story: {e}")
                    # Don't fail the entire story generation if deep dive research fails
                
                # After research is complete, generate critical perspectives
                self.logger.info("Research complete. Generating critical perspectives analysis...")
                try:
                    self.generate_critical_perspectives(story)
                    self.logger.info("Critical perspectives generation completed")
                except Exception as e:
                    self.logger.warning(f"Critical perspectives generation failed, continuing with story: {e}")
                    # Don't fail the entire story generation if critical perspectives fails
            
            # After generating baseline settings, create deep dive settings  
            if asset_type == AssetTypeNames.SETTINGS:
                self.logger.info("Baseline settings complete. Analyzing need for deep dive settings...")
                try:
                    self.generate_deep_dive_settings(story)
                    self.logger.info("Deep dive settings generation completed")
                except Exception as e:
                    self.logger.warning(f"Deep dive settings generation failed, continuing with story: {e}")
                    # Don't fail the entire story generation if deep dive settings fails
            
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
        
        # Show progress indicator with specific asset type
        print_progress_step(asset_type.title, f"Creating detailed {asset_type.title.lower()}")
        
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
            
        complete_progress_step(asset_type.title)
            
        summary = summarize_text(text=asset_text, summary_length=asset_type.summary_length)
        
        # Special handling for research and settings assets - save as baseline.md in their respective folders
        if asset_type_enum == AssetTypeNames.RESEARCH:
            file_name = "baseline.md"
        elif asset_type_enum == AssetTypeNames.SETTINGS:
            file_name = "baseline.md"
        else:
            file_name = f"{asset_type.title}.md"
        
        asset = StoryAsset(
            asset_type=asset_type_enum.name,
            title=asset_type.title,
            summary=summary,
            details=asset_text,
            relative_file_path=Path(asset_type.directory, file_name)
        )
        
        return asset

    def analyze_research_depth_needs(self, story: Story) -> List[str]:
        """
        Analyzes the story concept and baseline research to identify areas needing deep dive research.
        
        Args:
            story (Story): The story object with concept and baseline research.
            
        Returns:
            List[str]: List of research topics that need deep dive investigation.
        """
        self.logger.info(f"Analyzing research depth needs for: '{story.title}'")
        
        # Get story context
        concept_text = story.assets.get(AssetTypeNames.CONCEPT.value, {}).details or ""
        baseline_research = story.assets.get(AssetTypeNames.RESEARCH.value, {}).details or ""
        
        analysis_prompt = f"""
        Analyze this story concept and baseline research to identify 2-3 specific areas that would benefit from deep dive research.
        
        ## Story Concept:
        {concept_text}
        
        ## Baseline Research:
        {baseline_research}
        
        ## Instructions:
        - Identify the most critical areas where deeper research would enhance story authenticity
        - Focus on elements that are central to the plot, setting, or character development
        - Prioritize areas where factual accuracy or cultural sensitivity is important
        - Consider genre-specific research needs (e.g., technology for sci-fi, magic systems for fantasy)
        
        Return a JSON list of 2-3 research topics that need deep investigation:
        - Each topic should be specific and actionable
        - Use clear, descriptive names (e.g., "medieval_warfare", "quantum_physics", "japanese_folklore")
        - Topics should be substantial enough to warrant dedicated research
        
        Format: {{"research_topics": ["topic1", "topic2", "topic3"]}}
        """
        
        try:
            from mythos.services.writer import generate_planning_text
            import json
            
            # Get structured analysis
            analysis_result = generate_planning_text(
                prompt=analysis_prompt,
                json_schema={
                    "type": "object",
                    "properties": {
                        "research_topics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1,
                            "maxItems": 3
                        }
                    },
                    "required": ["research_topics"],
                    "additionalProperties": False
                }
            )
            
            analysis_data = json.loads(analysis_result)
            topics = analysis_data.get("research_topics", [])
            
            self.logger.info(f"Identified {len(topics)} research areas: {topics}")
            return topics
            
        except Exception as e:
            self.logger.error(f"Failed to analyze research depth needs: {e}")
            # Fallback to common research areas based on concept keywords
            concept_lower = concept_text.lower()
            fallback_topics = []
            
            if any(word in concept_lower for word in ["fantasy", "magic", "medieval", "kingdom"]):
                fallback_topics.append("medieval_culture")
            if any(word in concept_lower for word in ["sci-fi", "space", "future", "technology"]):
                fallback_topics.append("technology_systems")
            if any(word in concept_lower for word in ["historical", "period", "war", "ancient"]):
                fallback_topics.append("historical_context")
                
            return fallback_topics[:2] if fallback_topics else ["cultural_context"]

    def create_deep_dive_research(self, story: Story, topic: str) -> StoryAsset:
        """
        Creates a deep dive research asset for a specific topic.
        
        Args:
            story (Story): The story object.
            topic (str): The research topic to investigate.
            
        Returns:
            StoryAsset: The deep dive research asset.
        """
        self.logger.info(f"Creating deep dive research for topic: '{topic}'")
        
        # Get story context for focused research
        concept_text = story.assets.get(AssetTypeNames.CONCEPT.value, {}).details or ""
        baseline_research = story.assets.get(AssetTypeNames.RESEARCH.value, {}).details or ""
        
        research_prompt = f"""
        Create expert-level deep dive research on "{topic}" specifically for this story.
        
        ## Story Concept:
        {concept_text}
        
        ## Baseline Research Context:
        {baseline_research}
        
        ## Deep Dive Research Instructions:
        Create comprehensive, expert-level research focused specifically on "{topic}" as it relates to this story.
        
        **Research Focus Areas:**
        - Historical accuracy and factual foundations
        - Cultural authenticity and sensitivity
        - Technical/scientific accuracy (if applicable) 
        - Genre conventions and opportunities for innovation
        - Narrative implications and story integration
        
        **Structure your research as:**
        # {topic.title().replace('_', ' ')} - Deep Dive Research
        
        ## Overview
        [Brief overview of why this research is critical for the story]
        
        ## Key Findings
        [Major research discoveries and facts]
        
        ## Historical/Cultural Context
        [Detailed background information]
        
        ## Technical Details
        [Specific technical, scientific, or procedural information]
        
        ## Narrative Applications
        [How this research can be applied in the story]
        
        ## Sources and Further Reading
        [Credible sources and references]
        
        ## Story Integration Notes
        [Specific ways to weave this research into the narrative]
        
        Use web search to find current, accurate information. Focus on credible sources and expert knowledge.
        Output comprehensive, well-organized markdown that provides deep expertise for authentic storytelling.
        """
        
        try:
            from mythos.services.writer import generate_web_enhanced_research, summarize_text
            
            # Generate deep dive research with web search
            research_text = generate_web_enhanced_research(prompt=research_prompt)
            summary = summarize_text(text=research_text, summary_length=AssetTypes.RESEARCH.summary_length)
            
            # Create asset with topic-specific file name
            research_asset = StoryAsset(
                asset_type=AssetTypeNames.RESEARCH.name,
                title=f"{topic}_research",
                summary=summary,
                details=research_text,
                relative_file_path=Path(AssetTypes.RESEARCH.directory, f"{topic}.md")
            )
            
            self.logger.info(f"Successfully created deep dive research for: '{topic}'")
            return research_asset
            
        except Exception as e:
            self.logger.error(f"Failed to create deep dive research for '{topic}': {e}")
            raise StoryBuildException(f"Failed to create deep dive research for '{topic}': {e}") from e

    def generate_deep_dive_research(self, story: Story) -> Story:
        """
        Generates deep dive research for identified areas that need more detailed investigation.
        
        Args:
            story (Story): The story object with baseline research.
            
        Returns:
            Story: Updated story object with deep dive research assets.
        """
        self.logger.info(f"Generating deep dive research for: '{story.title}'")
        
        try:
            # Analyze what research areas need deep dives
            research_topics = self.analyze_research_depth_needs(story)
            
            if not research_topics:
                self.logger.info("No deep dive research areas identified")
                return story
            
            # Generate deep dive research for each identified topic
            for topic in research_topics:
                try:
                    deep_dive_asset = self.create_deep_dive_research(story, topic)
                    self._create_asset_with_metadata(story, deep_dive_asset)
                    self.logger.info(f"Generated deep dive research: '{topic}'")
                    
                except Exception as e:
                    self.logger.error(f"Failed to generate deep dive for '{topic}': {e}")
                    # Continue with other topics even if one fails
            
            # Save story with new research assets
            self.story_manager.update_story(story)
            self.logger.info(f"Successfully generated deep dive research for {len(research_topics)} topics")
            
            return story
            
        except Exception as e:
            self.logger.error(f"Failed to generate deep dive research: {e}")
            raise StoryBuildException(f"Deep dive research generation failed: {e}") from e

    def analyze_settings_depth_needs(self, story: Story) -> List[str]:
        """
        Analyzes the story concept and baseline settings to identify specific setting components needing deep dive development.
        
        Args:
            story (Story): The story object with concept and baseline settings.
            
        Returns:
            List[str]: List of setting components that need detailed development.
        """
        self.logger.info(f"Analyzing settings depth needs for: '{story.title}'")
        
        # Get story context
        concept_text = story.assets.get(AssetTypeNames.CONCEPT.value, {}).details or ""
        baseline_settings = story.assets.get(AssetTypeNames.SETTINGS.value, {}).details or ""
        
        analysis_prompt = f"""
        Analyze this story concept and baseline settings to identify which setting components need detailed development.
        
        ## Story Concept:
        {concept_text}
        
        ## Baseline Settings:
        {baseline_settings}
        
        ## Analysis Instructions:
        Based on the story concept and genre, identify 2-4 setting components that are CRITICAL for this specific story and need expert-level detail. Consider:
        
        **Possible Setting Components:**
        - geography (physical landscape, climate, natural features)
        - locations (specific places, buildings, landmarks) 
        - culture (customs, traditions, social norms, religion)
        - politics (government, laws, political tensions)
        - economy (trade, currency, class systems, economics)
        - technology (tech level, magic systems, innovations)
        - daily_life (occupations, clothing, food, entertainment)
        - history (past events, conflicts, founding myths)
        
        **Selection Criteria:**
        - Which components are central to the plot or character development?
        - Which components need authentic detail for reader immersion?
        - Which components present unique challenges or opportunities?
        - Which components are most likely to be researched by readers?
        
        Return ONLY a comma-separated list of 2-4 component names from the list above.
        Example: "geography, politics, technology"
        """
        
        try:
            result = generate_planning_text(prompt=analysis_prompt)
            
            # Parse the result to extract component names
            if result and not result.startswith("Error"):
                # Clean and split the result
                components = [comp.strip().lower() for comp in result.replace('\n', '').split(',')]
                # Validate components against known types
                valid_components = ['geography', 'locations', 'culture', 'politics', 'economy', 'technology', 'daily_life', 'history']
                selected_components = [comp for comp in components if comp in valid_components]
                
                self.logger.info(f"Selected setting components for deep dive: {selected_components}")
                return selected_components[:4]  # Limit to max 4 components
            else:
                self.logger.warning(f"Failed to analyze settings depth needs: {result}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error analyzing settings depth needs: {e}")
            return []

    def generate_deep_dive_settings(self, story: Story) -> None:
        """
        Generates deep dive settings for components identified as needing detailed development.
        
        Args:
            story (Story): The story object.
        """
        self.logger.info(f"Generating deep dive settings for: '{story.title}'")
        
        # Analyze which setting components need deep dive research
        setting_components = self.analyze_settings_depth_needs(story)
        
        if not setting_components:
            self.logger.info("No specific setting components identified for deep dive development")
            return
            
        self.logger.info(f"Generating deep dive settings for: {', '.join(setting_components)}")
        
        # Generate deep dive settings for each identified component
        for component in setting_components:
            try:
                deep_dive_asset = self.create_deep_dive_settings(story, component)
                self._create_asset_with_metadata(story, deep_dive_asset)
                self.logger.info(f"Generated deep dive settings: '{component}'")
                
            except Exception as e:
                self.logger.error(f"Failed to generate deep dive settings for '{component}': {e}")
                # Continue with other components even if one fails

    def create_deep_dive_settings(self, story: Story, component: str) -> StoryAsset:
        """
        Creates a deep dive settings asset for a specific setting component.
        
        Args:
            story (Story): The story object.
            component (str): The setting component to develop in detail.
            
        Returns:
            StoryAsset: The deep dive settings asset.
        """
        self.logger.info(f"Creating deep dive settings for component: '{component}'")
        
        # Get story context for focused settings development
        concept_text = story.assets.get(AssetTypeNames.CONCEPT.value, {}).details or ""
        baseline_settings = story.assets.get(AssetTypeNames.SETTINGS.value, {}).details or ""
        baseline_research = story.assets.get(AssetTypeNames.RESEARCH.value, {}).details or ""
        
        settings_prompt = f"""
        Create detailed, expert-level setting development for "{component}" specifically for this story.
        
        ## Story Concept:
        {concept_text}
        
        ## Baseline Settings Context:
        {baseline_settings}
        
        ## Research Context:
        {baseline_research}
        
        ## Deep Dive Settings Instructions:
        Create comprehensive, detailed world-building for "{component}" as it relates to this story.
        
        **Setting Development Focus Areas:**
        - Authentic detail that enhances reader immersion
        - Story-relevant elements that support plot and character development
        - Cultural accuracy and sensitivity (if based on real-world cultures)
        - Internal consistency within the story world
        - Practical considerations for narrative integration
        
        **Structure your settings as:**
        # {component.title().replace('_', ' ')} Settings
        
        ## Overview
        [Brief overview of why this component is critical for the story]
        
        ## Detailed Description
        [Comprehensive details about this setting component]
        
        ## Story Integration
        [How this component directly supports the plot and characters]
        
        ## Cultural Context
        [Cultural background and authenticity considerations]
        
        ## Practical Details
        [Specific details that writers can use in scenes]
        
        ## Visual Elements
        [Sensory details for immersive description]
        
        ## Character Interaction
        [How characters would realistically interact with this component]
        
        ## Plot Implications
        [How this component creates opportunities or constraints for the story]
        
        Focus on practical, story-relevant details that enhance authenticity and support narrative goals.
        Output comprehensive, well-organized markdown that provides detailed world-building for compelling storytelling.
        """
        
        # Generate the deep dive settings content
        settings_content = generate_planning_text(prompt=settings_prompt)
        
        if not settings_content or settings_content.startswith("Error"):
            raise ValueError(f"Failed to generate settings content for component '{component}': {settings_content}")
        
        summary = summarize_text(text=settings_content, summary_length=AssetTypes.SETTINGS.summary_length)
        
        # Create settings asset in the settings folder
        deep_dive_asset = StoryAsset(
            asset_type=AssetTypeNames.SETTINGS.name,
            title=f"{component}_settings",
            summary=summary,
            details=settings_content,
            relative_file_path=Path(AssetTypes.SETTINGS.directory, f"{component}.md")
        )
        
        return deep_dive_asset

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

                # Extract chapter number for progress display  
                chapter_num = self._extract_chapter_number(chapter_title)
                
                # Show chapter-specific progress
                from mythos.utils.progress_tracker import get_progress_tracker
                tracker = get_progress_tracker()
                
                # Get total from sorted chapters
                total_chapters = len(sorted_chapters)
                tracker.show_chapter_progress(chapter_num, total_chapters, chapter_title)
                
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

        print_progress_step(f"Chapter {chapter_num} Outline", f"Creating detailed outline for Chapter {chapter_num}")
        chapter_asset.details = generate_planning_text(prompt=chapter_prompt)
        chapter_asset.summary = summarize_text(
            text=chapter_asset.details,
            summary_length=AssetTypes.CHAPTER_OUTLINE.summary_length
        )

        self._create_asset_with_metadata(story, chapter_asset)
        self.story_manager.update_story(story)
        complete_progress_step(f"Chapter {chapter_num} Outline")
        self.logger.debug(f"Chapter {chapter_num} outline generated and saved.")
        
        return chapter_asset
    
    def _generate_story_content(self, story: Story) -> Story:
        """Generates chapter structure and content."""
        self.generate_chapter_assets(story)
        
        # Set baseline after chapter outline generation
        self.story_manager.update_asset_baseline(story)
        
        # Step 3 Complete: Chapter outlines generated
        # Ask if user wants to continue to writing chapters
        if not confirm_next_step(
            current_step="Chapter outlines created",
            next_step="Write full manuscript chapters",
            story_title=story.title
        ):
            # Save story and return early
            self.story_manager.update_story(story)
            return story
        
        self.write_chapters(story)
        
        # Set baseline after chapter writing
        self.story_manager.update_asset_baseline(story)
        
        # Step 4 Complete: Chapters written
        # Ask if user wants to continue to finalization
        if not confirm_next_step(
            current_step="All chapters written",
            next_step="Create final draft and EPUB",
            story_title=story.title
        ):
            # Save story and return early
            self.story_manager.update_story(story)
            return story
            
        return story

    def _extract_chapter_number(self, chapter_title: str) -> int:
        """
        Extract chapter number from chapter title.
        
        Args:
            chapter_title: Title like "chapter_1" or "Chapter 1"
            
        Returns:
            Chapter number as integer, defaulting to 1 if not found
        """
        import re
        # Try to extract number from various formats
        match = re.search(r'(\d+)', chapter_title)
        return int(match.group(1)) if match else 1
    
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
                draft_content += f"\n\n{asset.details}\n\n"
        
        # Define the directory and file name for the draft markdown
        draft_directory = Path(story.story_dir, AssetTypes.MANUSCRIPT_DRAFT.directory)
        draft_file_name = "draft.md"
        draft_file_path = draft_directory / draft_file_name
        
        try:
            # Ensure the draft directory exists
            draft_directory.mkdir(parents=True, exist_ok=True)
            
            # Write the compiled content to the markdown file
            draft_file_path.write_text(draft_content.strip(), encoding='utf-8')

            self.logger.info(f"Created complete manuscript draft markdown file at {draft_file_path}")
        except Exception as e:
            self.logger.error(f"Failed to write draft markdown file: {e}")
            raise StoryBuildException(f"Failed to write draft markdown file: {e}") from e
        
        return draft_file_path

    def generate_critical_perspectives(self, story: Story) -> None:
        """
        Generates critical perspectives analysis for the story.
        
        Args:
            story (Story): The story object with existing assets.
        """
        self.logger.info(f"Generating critical perspectives for: '{story.title}'")
        
        try:
            # Select relevant critical perspectives using LLM analysis
            selected_perspectives = self._select_critical_perspectives(story)
            
            if not selected_perspectives:
                self.logger.info("No critical perspectives identified")
                return
            
            # Ensure templates exist for selected perspectives in this story's directory
            self._ensure_perspective_templates_exist(story, selected_perspectives)
            
            # Generate individual critical analysis assets in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [
                    executor.submit(self._create_critical_perspective_asset, story, perspective)
                    for perspective in selected_perspectives
                ]
                
                # Wait for all analyses to complete
                for future in concurrent.futures.as_completed(futures):
                    try:
                        asset = future.result()
                        if asset:
                            self._create_asset_with_metadata(story, asset)
                            self.logger.info(f"Generated critical analysis: '{asset.title}'")
                    except Exception as e:
                        self.logger.error(f"Failed to generate critical analysis: {e}")
                        continue
            
            # Save story with new critical analysis assets
            self.story_manager.update_story(story)
            self.logger.info(f"Successfully generated critical perspectives analysis")
            
        except Exception as e:
            self.logger.error(f"Failed to generate critical perspectives: {e}")
            raise StoryBuildException(f"Critical perspectives generation failed: {e}") from e

    def _select_critical_perspectives(self, story: Story) -> List[str]:
        """
        Uses LLM to select 1-3 relevant critical perspectives based on story synopsis.
        
        Args:
            story (Story): The story object with existing assets.
            
        Returns:
            List[str]: List of selected critical perspective names.
        """
        self.logger.info(f"Selecting critical perspectives for: '{story.title}'")
        
        # Get full story synopsis for analysis
        synopsis = self.story_manager.get_synopsis(story)
        
        selection_prompt = f"""
        Analyze this story synopsis and select 1-3 critical perspectives that would provide the most valuable insights for improving this story.

        ## Story Synopsis:
        {synopsis}



        ## Selection Criteria:
        - Choose perspectives most relevant to the story's themes and conflicts
        - Prioritize those that will reveal actionable insights for the writer
        - Consider the story's genre, setting, and character dynamics

        Respond with your selected perspectives and brief rationale.
        """
        
        try:
            # Use unified LLM interface with MEDIUM tier for critical analysis
            response = call_llm(
                prompt=selection_prompt,
                system_prompt=PLANNING_SYSTEM_PROMPT,
                tier="medium",
                json_output=True,
                json_schema=CRITICAL_PERSPECTIVES_SCHEMA
            )
            
            self.logger.debug(f"Raw LLM response: {response} (type: {type(response)})")
            
            # Handle both dict and string responses (same pattern as questioner)
            if isinstance(response, dict):
                perspectives = response.get("selected_perspectives", [])
                rationale = response.get("rationale", "No rationale provided")
                self.logger.info(f"Selected {len(perspectives)} perspectives: {', '.join(perspectives)}")
                self.logger.debug(f"Selection rationale: {rationale}")
                return perspectives
            else:
                # Try to parse JSON string
                try:
                    parsed_response = json.loads(response)
                    perspectives = parsed_response.get("selected_perspectives", [])
                    rationale = parsed_response.get("rationale", "No rationale provided")
                    self.logger.info(f"Selected {len(perspectives)} perspectives: {', '.join(perspectives)}")
                    self.logger.debug(f"Selection rationale: {rationale}")
                    return perspectives
                except (json.JSONDecodeError, AttributeError) as je:
                    self.logger.warning(f"Could not parse JSON from response: {je}. Response: {response}")
                    return []
                
        except Exception as e:
            self.logger.error(f"Failed to select critical perspectives: {e}")
            return []

    def _create_critical_perspective_asset(self, story: Story, perspective: str) -> Optional[StoryAsset]:
        """
        Creates a focused critical analysis asset for a specific perspective using pre-generated templates.
        
        Args:
            story (Story): The story object.
            perspective (str): The name of the critical perspective.
            
        Returns:
            Optional[StoryAsset]: The created critical analysis asset, or None if failed.
        """
        self.logger.info(f"Creating critical analysis for perspective: '{perspective}'")
        
        try:
            # Get full story synopsis for analysis
            synopsis = self.story_manager.get_synopsis(story)
            
            # Check if we have a pre-generated template for this perspective in the story's directory
            safe_perspective_name = self._make_safe_filename(perspective)
            templates_dir = Path(story.story_dir, CRITICAL_ANALYSIS_DIR, TEMPLATE_SUBDIR)
            template_path = templates_dir / f"{safe_perspective_name}_template.md"
            
            if template_path.exists():
                # Use the pre-generated template
                template_content = template_path.read_text()
                self.logger.info(f"Using pre-generated template: {template_path}")
                
                analysis_prompt = f"""
                Using the {perspective} framework below, analyze this story and provide specific, actionable insights.

                ## {perspective} Framework:
                {template_content}

                ## Story to Analyze:
                {synopsis}

                ## Analysis Instructions:
                Apply the framework above to analyze this story. Provide:

                1. **Analysis**: Detailed examination using the framework questions
                2. **Strengths**: What the story does well from this perspective  
                3. **Areas for Improvement**: Specific issues or gaps identified
                4. **Recommendations**: Concrete suggestions for the writer
                5. **Implementation Notes**: How to apply these insights during writing

                Be specific, practical, and actionable. Focus on improving the story.
                Use the framework questions as a guide but don't just repeat them - provide actual analysis.
                """
                
            else:
                # Fallback to generating a framework on-the-fly (existing behavior)
                self.logger.warning(f"No template found for '{perspective}', generating framework on-the-fly")
                
                framework_prompt = f"""
                Create a focused critical analysis framework for applying {perspective} to story development.

                ## Story Synopsis:
                {synopsis}

                ## Instructions:
                Create a practical framework specifically for analyzing THIS story through the lens of {perspective}. Include:

                1. **Core Analytical Focus**: What this perspective examines in THIS specific story
                2. **Key Questions**: 5-7 specific questions about this story's elements
                3. **Story Elements to Examine**: Which characters, relationships, settings, themes to analyze
                4. **Actionable Insights**: What the writer should look for to improve the story
                5. **Potential Issues**: What problems this lens might reveal
                6. **Recommendations**: Specific suggestions for strengthening the story

                Make this practical and actionable for the writer, not academic theory.
                Focus on how to improve THIS specific story.
                """
                
                framework = generate_planning_text(prompt=framework_prompt)
                
                # Apply the framework to analyze the story
                analysis_prompt = f"""
                Using the framework below, analyze this story and provide specific, actionable insights.

                ## Critical Framework ({perspective}):
                {framework}

                ## Story to Analyze:
                {synopsis}

                ## Analysis Instructions:
                Apply the framework above to analyze this story. Provide:

                1. **Analysis**: Detailed examination using the framework questions
                2. **Strengths**: What the story does well from this perspective  
                3. **Areas for Improvement**: Specific issues or gaps identified
                4. **Recommendations**: Concrete suggestions for the writer
                5. **Implementation Notes**: How to apply these insights during writing

                Be specific, practical, and actionable. Focus on improving the story.
                """
            
            # Generate the analysis
            analysis = generate_planning_text(prompt=analysis_prompt)
            
            # Create the asset summary
            summary = summarize_text(text=analysis, summary_length=AssetTypes.CRITICAL_PERSPECTIVES.summary_length)
            
            # Create the asset with a safe filename
            filename = f"{safe_perspective_name}_analysis.md"
            
            asset = StoryAsset(
                asset_type=AssetTypeNames.CRITICAL_PERSPECTIVES.name,
                title=f"{perspective} Analysis",
                summary=summary,
                details=analysis,
                relative_file_path=Path(AssetTypes.CRITICAL_PERSPECTIVES.directory, filename)
            )
            
            return asset
            
        except Exception as e:
            self.logger.error(f"Failed to create critical perspective asset for '{perspective}': {e}")
            return None

    def generate_critical_perspective_templates(self, story: Story, perspectives: List[str]) -> None:
        """
        Generates reusable critical perspective templates from the meta-template for a specific story.
        
        Args:
            story (Story): The story object to generate templates for.
            perspectives (List[str]): Specific perspectives to generate.
        """
        self.logger.info(f"Generating {len(perspectives)} critical perspective templates for story: '{story.title}'")
        
        # Create templates directory
        templates_dir = Path(story.story_dir, CRITICAL_ANALYSIS_DIR, TEMPLATE_SUBDIR)
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Read the meta-template
        try:
            meta_template_text = META_TEMPLATE_PATH.read_text(encoding='utf-8')
        except FileNotFoundError:
            self.logger.error(f"Meta-template not found: {META_TEMPLATE_PATH}")
            raise
        except IOError as e:
            self.logger.error(f"Failed to read meta-template: {e}")
            raise
        
        # Generate templates in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self._generate_single_perspective_template, perspective, meta_template_text, templates_dir)
                for perspective in perspectives
            ]
            
            # Wait for all templates to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    template_path = future.result()
                    if template_path:
                        self.logger.info(f"Generated template: {template_path}")
                except Exception as e:
                    self.logger.error(f"Failed to generate perspective template: {e}")
                    continue
        
        self.logger.info("Critical perspective template generation completed")

    def _generate_single_perspective_template(self, perspective: str, meta_template_text: str, templates_dir: Path) -> Optional[str]:
        """
        Generates a single critical perspective template.
        
        Args:
            perspective (str): The name of the critical perspective.
            meta_template_text (str): The meta-template content.
            templates_dir (Path): Directory to save the template in.
            
        Returns:
            Optional[str]: The path to the generated template file, or None if failed.
        """
        try:
            # Create the generation prompt
            generation_prompt = f"""
            Using the Critical Perspective Template Generator, create a comprehensive analytical framework for {perspective}. 
            Focus on practical questions that help writers apply this critical lens while creating stories. 
            Balance theoretical insights with hands-on storytelling guidance, making the perspective accessible to working writers.

            ## Meta-Template:
            {meta_template_text}

            ## Instructions:
            Replace all [VARIABLES] in the template structure with {perspective}-specific content while maintaining the exact structure and formatting.
            Make this a reusable template that writers can apply to any story, not specific to one story.
            """
            
            # Generate the template using the planning text function
            template_content = generate_planning_text(prompt=generation_prompt)
            
            # Create safe filename
            safe_perspective_name = self._make_safe_filename(perspective)
            template_filename = f"{safe_perspective_name}_template.md"
            template_path = templates_dir / template_filename
            
            # Write the template file
            try:
                template_path.write_text(template_content, encoding='utf-8')
            except IOError as e:
                self.logger.error(f"Failed to write template file {template_path}: {e}")
                raise
            
            return str(template_path)
            
        except Exception as e:
            self.logger.error(f"Failed to generate template for '{perspective}': {e}")
            return None

    def _ensure_perspective_templates_exist(self, story: Story, perspectives: List[str]) -> None:
        """
        Ensures that templates exist for the specified perspectives, generating them if needed.
        
        Args:
            story (Story): The story object.
            perspectives (List[str]): List of perspective names to check.
        """
        missing_perspectives = []
        
        # Create templates directory if it doesn't exist
        templates_dir = Path(story.story_dir, CRITICAL_ANALYSIS_DIR, TEMPLATE_SUBDIR)
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        for perspective in perspectives:
            safe_perspective_name = self._make_safe_filename(perspective)
            template_path = templates_dir / f"{safe_perspective_name}_template.md"
            
            if not template_path.exists():
                missing_perspectives.append(perspective)
        
        if missing_perspectives:
            self.logger.info(f"Generating missing templates for: {', '.join(missing_perspectives)}")
            self.generate_critical_perspective_templates(story, missing_perspectives)
        else:
            self.logger.info("All required perspective templates already exist")

    def generate_critical_perspective_templates_cli(self, perspectives: List[str]) -> None:
        """
        Generates reusable critical perspective templates for CLI usage (saves to global templates directory).
        
        Args:
            perspectives (List[str]): Specific perspectives to generate.
        """
        self.logger.info(f"Generating {len(perspectives)} critical perspective templates (CLI mode)")
        
        # Create global templates directory
        templates_dir = Path("templates")
        templates_dir.mkdir(exist_ok=True)
        
        # Read the meta-template
        try:
            meta_template_text = META_TEMPLATE_PATH.read_text(encoding='utf-8')
        except FileNotFoundError:
            self.logger.error(f"Meta-template not found: {META_TEMPLATE_PATH}")
            raise
        except IOError as e:
            self.logger.error(f"Failed to read meta-template: {e}")
            raise
        
        # Generate templates in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self._generate_single_perspective_template, perspective, meta_template_text, templates_dir)
                for perspective in perspectives
            ]
            
            # Wait for all templates to complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    template_path = future.result()
                    if template_path:
                        self.logger.info(f"Generated template: {template_path}")
                except Exception as e:
                    self.logger.error(f"Failed to generate perspective template: {e}")
                    continue
        
        self.logger.info("Critical perspective template generation completed (CLI mode)")