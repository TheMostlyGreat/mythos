from mythos.story import Story
from mythos.story_assets import StoryAsset
from mythos.story_llm import generate_planning_text, generate_narrative_text, generate_json
import os
import json

class StoryManager:
    """
    A class to manage the interactions between Story and StoryAsset.
        1. Generate concept
        2. Build first pass
            1. Research
            2. Inspiration
            3. Plot
            4. Characters
            5. Setting
            6. Writing Style
            7. Chapters Breakdown
            8. Key scenes
        3. Iterate
    """
    def __init__(self, story: Story):
        #self.story = story if story is not None else Story()
        self.story = story
        # List of asset types in the order they should be processed
        self.asset_types = [
            "research",
            "inspiration",
            "plot",
            "characters",
            "setting",
            "writing_style",
            "chapters_breakdown",
            "key_scenes"
        ]
        
        self.assets = {}

        print("New Story initialized\n")

    def generate_concept(self):
        print("Drafting the concept\n")
        prompt = (
            "Draft a brief for a story with the following details:\n" +
            f"{self.story.user_prompt}" +
            "\n" +
            "Use this template:\n" +
            #open('prompts/frameworks/character_profile_template.md').read()
            open('templates/concept_template.md').read()
        )
        concept = generate_planning_text(prompt)
        
        print(f"Here's the concept:\n {concept}\n")

        # Extract the title from the concept
        title = concept.split('Title: ')[1].split('\n')[0]

        #self.story.set_title(title)
        self.story.set_title(title)
        self.story.concept = StoryAsset(path=self.story.path, asset_type="concept")
        self.story.concept.set_details(concept)
        print("Concept complete")

        print(f"Concept: {self.story.concept.details}")
        return self.story.concept
    
    def run_initial_pass(self):
        print("Generating first pass\n")
        
        for asset_type in self.asset_types:
            self.generate_initial_asset(type=asset_type)
        

    def generate_initial_asset(self, type: str, name: str = None):
        
        content = ""

        print(f"Drafting a {type} asset\n")
        
        if name is not None:
            print(f"for {type}: {name}\n")
        
        if self.story.concept is None: 
            print("No concept set!")

        prompt = (
            f"Please help me create a short version of the {type} for the story. "
            "Provide the essential details with a focus on brevity, clarity, and specificity.\n" +
            f"Here is the concept: \n"
            f"{self.story.concept.details}" +
            "\n" 
            # +
            # "Use this template:\n" +
            # open(f'templates/initial_{type}_template.md').read()
        )
        
        content = generate_planning_text(prompt=prompt)

        asset = StoryAsset(path=self.story.path, asset_type=type)

        asset.set_summary(content=content)

        self.story.add_asset(asset)
        
        print(f"{type} asset complete\n")

    def iterate(self):
        #print(f"Generating iteration {self.story.current_version_num+1}\n")
        print(f"Here are all the assets: {', '.join(self.story.assets.keys())}\n")

        self.story.current_version_num += 1
        
        print(f"Iterating on {self.story.title}\n")

        for asset_type in self.asset_types:
            print(f"Starting with {asset_type}\n")
            self.regenerate_asset(type=asset_type)
            print(f"Done drafting {asset_type}\n")

        print("Done regenerating all the assets\n")
        self.draft_chapters()

    def regenerate_asset(self, type:str, name:str=None):
        content = ""
        print(f"Current asset keys: {list(self.story.assets.keys())}\n")
        asset = self.story.assets[type]

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
        print("Drafting Chapters\n")
        # Get the story chapter breakdown
        chapter_breakdown = self.story.assets['chapters_breakdown']
        if not chapter_breakdown:
            print("No chapter breakdown found.")
            return

        # Turn it into JSON
        with open('code/templates/chapter_breakdown_template.json', 'r') as file:
            chapter_breakdown_template = file.read()

        json_prompt = (
            f"Please generate JSON in this format:\n{chapter_breakdown_template}\n"
            f"Based on the following chapter breakdown details:\n{chapter_breakdown.details}"
        )
        chapter_json = generate_json(json_prompt)

        print(f"Here is the Json:\n {chapter_json}\n")
        #validate the json
        try:
            chapter_data = json.loads(chapter_json)
            print("Chapter JSON is valid.")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON format: {e}")
            return

        # Ensure we have the chapters list
        chapters = chapter_data.get('chapters', [])
        if not chapters:
            print("No chapters found in the JSON data.")
            return

        story_so_far = ""
        chapter_counter = 1

        # Iterate through the JSON and for each chapter
        for chapter in chapters:
            print(f"Drafting chapter {chapter_counter}\n")
            # 1. Create a prompt with the chapter json + the synopsis + story_so_far
            prompt = (
                f"Create a detailed narrative for the following chapter:\n{json.dumps(chapter, indent=2)}\n"
                f"Here is the synopsis of the story:\n{self.story.synopsis}\n"
                f"Here is the story so far:\n{story_so_far}\n"
            )

            # 2. Send the prompt to the generate_narrative_text function
            chapter_content = generate_narrative_text(prompt)[0].text

            # 3. Create a StoryAsset with that as the content
            chapter_asset = StoryAsset(path=os.path.join(self.story.path, 'manuscript'), asset_type="chapter")

            # 4. Extract the title and set it as the StoryAsset name
            title = chapter.get('title', f"Chapter {chapter_counter}")
            chapter_asset.name = title

            # 5. Set StoryAsset type as chapter
            chapter_asset.set_details(chapter_content)

            # 6. Set the path as story.path + 'manuscript'
            chapter_asset.path = os.path.join(self.story.path, 'manuscript', f"{title}.md")

            # 8. Add this StoryAsset summary to story_so_far
            story_so_far += f"\n\n{chapter_content}"

            # Add the chapter asset to the story
            self.story.add_asset(chapter_asset)

            print(f"Completed chapter {chapter_counter}")

            # Update the chapter counter by one
            chapter_counter += 1

        print("Chapters drafted successfully.")

    def draft_opening_scene(self):
        """
        Drafts the opening scene of the story.
        """

        prompt = (
            "Draft a compelling 500 word opening scene for the following chapter summary. " 
            "Ensure that it grips the reader so that they want to read more of the story.\n" +
            "Here is the broader context for the story:\n" +
            self.story.synopsis +
            "\n"
        )
        # if self.story.assets['writing_style']:
        #     prompt += (
        #         "Here is the writing style:\n" +
        #         self.story.assets['writing_style'].de +
        #         "\n"
        #     )
        opening_scene = generate_narrative_text(prompt)[0].text
        print(f"Here's the opening scene:\n {opening_scene}\n")

        with open(os.path.join(self.story.path, 'opening_scene.md'), 'w') as file:
            file.write(opening_scene)
        print("Opening scene saved to " + os.path.join(self.story.path, 'opening_scene.md') + "\n")

        