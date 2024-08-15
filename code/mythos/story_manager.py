from mythos.story import Story
from mythos.story_assets import StoryAsset
from mythos.story_llm import generate_planning_text, generate_narrative_text, generate_json
import os
import json
import logging

class StoryManager:
    """
    Manages the creation and iteration of a story, including its assets.
    
    The story creation process follows these steps:
    1. Generate concept
    2. Build first pass (research, plot, characters, setting, writing style, chapter list)
    3. Iterate and refine
    """
    def __init__(self, story: Story):
        self.story = story
        # Define the order of asset creation
        self.asset_types = [
            "research", "plot", "characters", "themes", "setting", "timeline", "writing_style", "chapter_list", 
        ]
        self.assets = {}
        print("New Story initialized\n")
        self.logger = logging.getLogger(__name__)

    def generate_concept(self):
        """
        Generates the initial story concept based on user input.

        Returns:
        --------
        StoryAsset
            The generated concept asset.
        """
        print("Drafting the concept\n")
        
        # Construct the prompt for concept generation
        with open('templates/concept_template.md', 'r') as template_file:
            template = template_file.read()
        
        prompt = (
            f"Draft a brief for a story with the following details:\n{self.story.user_prompt}\n"
            f"Use this template:\n{template}"
        )
        concept = generate_planning_text(prompt)
        
        print(f"Here's the concept:\n{concept}\n")

        # Extract the title from the concept and set it
        title = concept.split('Title: ')[1].split('\n')[0]
        self.story.set_title(title)

        # Create and set the concept asset
        self.story.concept = StoryAsset(path=self.story.path, asset_type="concept")
        self.story.concept.set_details(concept)
        print("Concept complete")

        print(f"Concept: {self.story.concept.details}")
        return self.story.concept
    
    def run_initial_pass(self):
        """Generates the first pass of all story assets."""
        print("Generating first pass\n")
        
        for asset_type in self.asset_types:
            self.generate_initial_asset(asset_type=asset_type)

    def generate_initial_asset(self, asset_type: str, name: str = None):
        """
        Generates an initial version of a specific story asset.
        
        Parameters:
        -----------
        asset_type : str
            The type of asset to generate (e.g., "plot", "characters")
        name : str, optional
            Optional name for the asset (used for specific characters, locations, etc.)
        """
        print(f"Drafting a {asset_type} asset")
        
        if name:
            print(f"for {asset_type}: {name}")
        
        if self.story.concept is None: 
            print("No concept set!")
            return

        prompt = (
            f"Please help me create a short version of the {asset_type} for the story. "
            "Provide the essential details with a focus on brevity, clarity, and specificity.\n"
            f"Here is the concept:\n{self.story.concept.details}\n"
        )
        
        content = generate_planning_text(prompt=prompt)

        asset = StoryAsset(path=self.story.path, asset_type=asset_type)

        asset.set_summary(content=content)

        self.story.add_asset(asset)
        
        print(f"{asset_type} asset complete\n")

    def iterate(self):
        """
        Performs an iteration on the story, refining all assets and drafting chapters.
        """
        print(f"Here are all the assets: {', '.join(self.story.assets.keys())}\n")

        self.story.current_version_num += 1
        
        print(f"Iterating on {self.story.title}\n")

        for asset_type in self.asset_types:
            print(f"Starting with {asset_type}\n")
            self.regenerate_asset(type=asset_type)
            print(f"Done drafting {asset_type}\n")

        print("Done regenerating all the assets\n")
        self.draft_chapters()

    def regenerate_asset(self, type: str, name: str = None):
        """
        Regenerates a specific story asset with more detail.
        
        :param type: The type of asset to regenerate
        :param name: Optional name for the asset (used for specific characters, locations, etc.)
        """
        content = ""
        print(f"Current asset keys: {list(self.story.assets.keys())}\n")
        asset = self.story.assets.get(type)

        if asset is None:
            print(f"No {type} asset found. Creating a new one.")
            asset = StoryAsset(path=self.story.path, asset_type=type)

        print(f"Drafting a {type} asset\n")
        
        if name is not None:
            print(f"for {type}: {name}\n")
        
        if self.story.concept is None: 
            print("No concept set!")

        template_path = os.path.join('templates', f'{type}_template.md')
        if os.path.exists(template_path):
            with open(template_path, 'r') as file:
                template = file.read()
        else:
            print(f"Template file {template_path} does not exist.")
            template = ""

        prompt = (
            f"Please build out the {type} for this story, based on this synopsis: \n"
            f"{self.story.synopsis}\n"
            f"Using this template: \n {template}"
        )
        
        content = generate_planning_text(prompt=prompt)

        asset.set_details(content=content)

        self.story.add_asset(asset)
        
        print(f"{type} asset complete")

    def draft_chapters(self):
        """
        Drafts all chapters of the story based on the chapter list and previous story elements.
        """
        self.logger.info("Starting to draft chapters")
        
        # Get and validate the chapter list
        chapter_list = self.story.assets.get('chapter_list')
        if not chapter_list:
            error_msg = "No chapter list found. Cannot draft chapters."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        # Generate JSON format for chapter list
        with open('templates/chapter_list_json.txt', 'r') as file:
            chapter_list_json = file.read()

        json_prompt = (
            f"Please generate JSON in this format:\n{chapter_list_json}\n"
            f"Based on the following chapter list details:\n{chapter_list.details}"
        )
        chapter_json = generate_json(json_prompt)

        print(f"Here is the Json:\n {chapter_json}\n")
        
        # Validate the JSON
        try:
            chapter_data = json.loads(chapter_json)
            print("Chapter JSON is valid.")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON format: {e}")
            return

        # Extract chapters from the JSON structure
        chapters = []
        for key, value in chapter_data.items():
            if key.startswith("Chapter"):
                chapters.append(value)

        if not chapters:
            error_msg = "No chapters found in the JSON data."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        story_so_far = ""
        chapter_counter = 1

        # Iterate through the chapters and generate content
        for chapter in chapters:
            print(f"Drafting chapter {chapter_counter}\n")
            print(f"Chapter {chapter_counter} JSON:")
            print(json.dumps(chapter, indent=2))
            print("\n")

            # Create a prompt for chapter generation
            prompt = (
                f"Create a detailed narrative for the following chapter:\n{json.dumps(chapter, indent=2)}\n"
                f"Here is the synopsis of the story:\n{self.story.synopsis}\n"
                f"Here is the story so far:\n{story_so_far}\n"
            )

            chapter_content = generate_narrative_text(prompt)

            # Create chapter title
            title = f"Chapter {chapter_counter}"
            if 'Title' in chapter and chapter['Title']:
                title += f"-{chapter['Title']}"
            print(f"Title: {title}\n")

            # Create and set up the chapter asset
            chapter_asset = StoryAsset(path=os.path.join(self.story.path, 'manuscript'), 
                                       asset_type="chapter", name=title)
            chapter_asset.set_details(chapter_content)
            #chapter_asset.path = os.path.join(self.story.path, 'manuscript', f"{title}.md")

            # Update story_so_far with the chapter summary instead of full content
            story_so_far += f"\n\n{chapter_asset.summary}"
            self.story.add_asset(chapter_asset)

            print(f"Completed chapter {chapter_counter}")
            chapter_counter += 1

        print("Chapters drafted successfully.")

    def draft_opening_scene(self):
        """
        Drafts a compelling 500-word opening scene for the story.
        """
        writing_style = self.story.assets.get('writing_style')
        if writing_style is None:
            raise ValueError("No writing style asset found. Cannot draft opening scene.")
        
        prompt = (
            "Draft a compelling 500 word opening scene for the following chapter summary. " 
            "Ensure that it grips the reader so that they want to read more of the story.\n" +
            "Here is the broader context for the story:\n" +
            self.story.synopsis +
            "\n" +
            f"Using this writing style:\n {writing_style}"
        )
        opening_scene = generate_narrative_text(prompt)
        print(f"Here's the opening scene:\n {opening_scene}\n")

        with open(os.path.join(self.story.path, 'opening_scene.md'), 'w') as file:
            file.write(opening_scene)
        print("Opening scene saved to " + os.path.join(self.story.path, 'opening_scene.md') + "\n")
        