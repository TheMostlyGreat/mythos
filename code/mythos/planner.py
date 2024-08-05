from mythos.story import Story
from mythos.character import Character
#from mythos.StoryAsset import StoryAsset
import json
import os
from mythos.constants import *
from mythos.story_llm import generate_planning_text, generate_json, generate_narrative_text

class Planner():

    # Initialize all elements
    def __init__(self, new_story: Story):
        print("Waking up the planner\n")
        self.story = new_story
        self.narrative_outline = None

        print("Planner is ready\n")

    def write(self, prompt):
        return generate_planning_text(prompt)
    
    def read_files(self, file_paths):
        contents = []
        print(f"Reading files: {file_paths}\n")
        for path in file_paths:
            with open(path, 'r') as file:
                contents.append(file.read())
        return contents
    
    def create_high_level_plan(self, details):
        """
        Concept and Themes:
        •	Core Idea: A one-sentence summary of the novel's main idea or concept.
        •	Genre: The genre of the novel (e.g., fantasy, science fiction, romance, thriller).
        •	Target Audience: The intended audience for the novel (e.g., young adults, adults, children).
        •	Primary Themes: The main themes or messages the novel will explore (e.g., love, betrayal, identity, justice).
        •	Secondary Themes: Additional themes that will be touched upon in the novel.
        Initial Research Notes:
        •	Historical Context: Relevant historical periods or events.
        •	Cultural Context: Important cultural backgrounds or settings.
        •	Critical Perspectives: Literary theories or critical perspectives (e.g., feminist, Marxist) that the novel will engage with.
        Inspirations and Influences:
        •	Inspirational Works: Books, movies, or other works that inspire the novel's concept or themes.
        •	Personal Experiences: Any personal experiences or knowledge to be incorporated into the novel.
        Main Characters (Initial Outline):
        •	Protagonist: Basic information about the main character (e.g., name, age, occupation).
        •	Antagonist: Basic information about the main antagonist or opposing force.
        •	Supporting Characters: Basic information about key supporting characters.
        Setting (Initial Outline):
        •	Primary Locations: Key locations where the story will take place.
        •	Time Period: The time period in which the novel is set (e.g., present day, historical, future).
        """
        self.develop_concept(details)

        self.conduct_research()

        self.collect_inspiration()

        self.define_main_characters()

        self.define_setting()

    def plan_structure(self):
        """
        Plot and Timeline Development:
        - Detailed Plot Outline: Create a detailed plot outline using a preferred structure (e.g., three-act structure, Hero's Journey), including major plot points, story arcs, and character development.
        - Chronological Timeline: Develop a chronological timeline of events, ensuring historical and cultural accuracy, and detailing specific dates or periods for key events and backstory.
        """
        high_level_plan = ""
        plot_outline = ""
        
        # Develop plot outline and intertextual references
        print("Developing plot outline and intertextual references\n")

        with open(self.story.concept, 'r') as file:
            high_level_plan = file.read() 

        prompt = (
            "Develop plot outline and intertextual references for the following high-level plan:\n" +
            high_level_plan +
            "\n" +
            "Use this framework and template:\n" +
            open('prompts/frameworks/plot_outline_framework.md').read()
        )
        plot_outline = self.write(prompt)
        print(f"Here's the plot outline:\n {plot_outline}\n")

        self.story.set_plot_outline(plot_outline)
        
        print("Plot outline saved to " + self.story.plot_outline + "\n")

        """  # Create chronological timeline of events
        print("Creating chronological timeline of events\n")

        prompt = (
            "Create a chronological timeline of events for the following concept and plot outline:\n" +
            self.story.concept +
            "\n\n" +
            plot_outline +
            "\n" +
            "Use this framework and template:\n" +
            open('prompts/frameworks/timeline_framework.md').read()
        )
        timeline = self.write(prompt)
        print(f"Here's the timeline:\n {timeline}\n") 
        self.story.set_timeline(timeline)
        print("Timeline saved to " + self.story.timeline + "\n")"""

    def develop_characters(self):
        """
        Develops detailed profiles for main and supporting characters.

        Steps:
        1. Reads the story concept and plot outline.
        2. Generates a JSON list of characters using the LLM.
        3. Validates and parses the JSON.
        4. Creates detailed character profiles for each character.
        5. Saves the profiles and updates the story object.

        Character Profiles Include:
        - Background: Personal history and context.
        - Goals: Objectives and motivations.
        - Conflicts: Internal and external conflicts.
        - Arcs: Character development and transformation over the story.

        Cultural and Historical Context:
        - Ensures characters are influenced by relevant cultural and historical factors.
        """

        characters_json = ""
        character_list = []

        # Developing character profiles
        print("Developing character profiles\n")

        with open(self.story.concept, 'r') as concept_file:
            concept_content = concept_file.read()

        with open(self.story.plot_outline, 'r') as plot_file:
            plot_content = plot_file.read()

        prompt = (
            "Define a JSON complete list of main characters and supporting characters for the following concept and plot outline:\n" +
            concept_content +
            "\n\n" +
            plot_content +
            "\n" +
            "Ensure the JSON is well-formed and does not include any extraneous characters or formatting.Use this JSON template:\n" + 
            open('prompts/frameworks/characters_json.txt').read()
        )

        # Retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            characters_json = generate_json(prompt)
            print(f"Attempt {attempt + 1}: Here's the characters:\n {characters_json}\n")

            # Check if characters_json is empty or invalid
            if not characters_json.strip():
                print("The generated characters JSON is empty or invalid. Retrying...\n")
                continue
            
            # Validate JSON format
            try:
                characters_dict = json.loads(characters_json)
                # Pretty-print the JSON for inspection
                print("Parsed JSON:\n", json.dumps(characters_dict, indent=4))
                break  # Exit loop if JSON is valid
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
                print("Invalid JSON:\n", characters_json)
                print("Retrying...\n")
                prompt = (
                    "Please correct the following JSON to be valid JSON and do not include any extraneous characters or formatting.:\n" +
                    characters_json +
                    "\n" +
                    "Use this framework and template:\n" +
                    open('prompts/frameworks/characters_json.txt').read()
                )
        else:
            raise ValueError("Failed to generate valid characters JSON after multiple attempts.")

        characters_path = os.path.join(self.story.path, CHARACTERS_DIR)

        for character in characters_dict['characters']:
            print(f"Developing character: {character['name']}\n")

            char_instance = Character(path=characters_path, name=character['name'], description=character['description'])
            
            # Build character profile
            prompt = (
                "Build a character profile for the following character:\n" +
                f"Name: {character['name']}\n" +
                f"Description: {character['description']}\n" +
                "For reference:" +
                f"Concept: {self.story.concept}\n" +
                f"Plot Outline: {self.story.plot_outline}\n" +
                f"Cast of characters: {characters_json}\n" +
                "Use this template:\n" +
                open('prompts/frameworks/character_profile_template.md').read()
            )

            char_profile = self.write(prompt)

            print(f"Here's a new character profile:\n {char_profile}\n")
            # Save character profile to their file
            char_instance.set_profile(char_profile)
            print(f"Character profile saved to {char_instance.filepath}\n")
            
            # Add character to list
            character_list.append(char_instance)
        
        print(f"{len(character_list)} characters developed.\n")

        self.story.characters = character_list

    def develop_setting(self):
        """
        **Setting Descriptions:**
        - Detailed descriptions of locations, reflecting historical and cultural accuracy.
        - Include social, economic, and political context relevant to Marxist analysis.
        - Ensure settings accurately reflect cultural and historical contexts, including customs, traditions, and social structures.
        """
        setting = ""

        # Developing setting
        print("Developing the setting\n")

        with open(self.story.concept, 'r') as concept_file:
            concept_content = concept_file.read()

        with open(self.story.plot_outline, 'r') as plot_file:
            plot_content = plot_file.read()

        prompt = (
            "Develop setting for the following concept and plot:\n" +
            concept_content +
            "\n" +
            plot_content +
            "\n" +
            "Use this framework and template:\n" +
            open('prompts/frameworks/setting_template.md').read()
        )
        setting = self.write(prompt)
        print(f"Here's the setting:\n {setting}\n")

        self.story.set_setting(setting)
        
        print("Setting saved to " + self.story.setting + "\n")

    # Develop Themes and Motifs
    def develop_themes_and_motifs(self):
        """
        **Themes and Motifs:**
        - Identify and develop central themes and motifs.
        - Ensure themes reflect the cultural, historical, and social context.
        - Integrate motifs that reinforce the themes and enhance the narrative.
        """
        themes_and_motifs = ""

        # Developing themes and motifs
        print("Developing themes and motifs\n")

        with open(self.story.concept, 'r') as concept_file:
            concept_content = concept_file.read()

        with open(self.story.plot_outline, 'r') as plot_file:
            plot_content = plot_file.read()

        prompt = (
            "Develop themes and motifs for the following concept and plot:\n" +
            concept_content +
            "\n" +
            plot_content +
            "\n" +
            "Use this framework and template:\n" +
            open('prompts/frameworks/themes_motifs_template.md').read()
        )
        print(f"Here's the prompt: {prompt}")
        themes_and_motifs = self.write(prompt)
        print(f"Here are the themes and motifs:\n {themes_and_motifs}\n")

        self.story.set_themes_and_motifs(themes_and_motifs)
        asset_path = os.path.join(self.story.path, ASSETS_DIR)
        StoryAsset(path=asset_path, name=THEMES_AND_MOTIFS, content=themes_and_motifs)
        print("Themes and motifs saved to " + self.story.themes_and_motifs + "\n")

    def develop_writing_style(self):
        """
        **Writing Style:**
        - Define the narrative voice, tone, and style.
        - Ensure consistency in language, pacing, and mood.
        - Integrate stylistic elements that enhance the story's themes and motifs.
        """
        writing_style = ""

        # Developing writing style
        print("Developing writing style\n")

        with open(self.story.concept, 'r') as concept_file:
            concept_content = concept_file.read()

        with open(self.story.plot_outline, 'r') as plot_file:
            plot_content = plot_file.read()

        prompt = (
            "Develop a writing style guide for the following concept and plot outline:\n" +
            concept_content +
            "\n\n" +
            plot_content +
            "\n" +
            "Use this template:\n" +
            open('prompts/frameworks/writing_style_template.md').read()
        )
        writing_style = self.write(prompt)
        print(f"Here's the writing style guide:\n {writing_style}\n")

        self.story.set_writing_style(writing_style)
        asset_path = os.path.join(self.story.path, ASSETS_DIR)
        StoryAsset(path=asset_path, name=WRITING_STYLE, content=writing_style)

        print("Writing style guide saved to " + self.story.writing_style + "\n")

    # Create the concept for the Story   
    def develop_concept(self, details):
        print("Drafting the concept\n")
        prompt = (
            "Draft a brief for a story with the following details:\n" +
            "\n".join(f"{key}: {value}" for key, value in details.items()) +
            "\n" +
            "Use this framework and template:\n" +
            open('prompts/frameworks/concept_framework.md').read()
        )

        
        concept = (
            "\n # User Input: \n" +
            "\n".join(f"{key}: {value}" for key, value in details.items()) + "\n"
        ) + generate_planning_text(prompt)
        
        print(f"Here's the concept:\n {concept}\n")

        # Extract the title from the concept
        title = concept.split('Title: ')[1].split('\n')[0]

        #self.story.set_title(title)
        self.story.set_title(title)
        self.story.set_concept(concept)

        print("Concept save to " + self.story.concept + "\n")

    def conduct_research(self):
        research_notes = ""
        # Gather historical, cultural info, summarize critical theories
        print("Conducting research...")
        
        with open(self.story.concept, 'r') as file:
            content = file.read()  
        
        prompt = (
            "Conduct research on the following concept:\n" +
            content +
            "\n" +
            "Use this framework and template:\n" +
            open('prompts/frameworks/research_framework.md').read()
        )
        research_notes = self.write(prompt)

        print(f"Here's the research:\n {research_notes}\n")

        with open(self.story.concept, 'a') as file:
            file.write("\n\n")
            file.write(research_notes)

        print("Research appended to " + self.story.concept + "\n")
    
    def collect_inspiration(self):
        inspiration = ""

        print("Collecting inspiration and influences\n")

        with open(self.story.concept, 'r') as file:
            content = file.read() 

        prompt = (
            "Collect inspiration and influences for the following concept:\n" +
            content +
            "Use this framework and template:\n" +
            open('prompts/frameworks/inspirations_framework.md').read()
        )
        inspiration = self.write(prompt)

        print(f"Here's the inspiration:\n {inspiration}\n")

        with open(self.story.concept, 'a') as file:
            file.write("\n\n")
            file.write(inspiration)
        print("Inspirations appended to " + self.story.concept + "\n")

    def define_main_characters(self):
        print("Defining main characters\n")

        with open(self.story.concept, 'r') as file:
            content = file.read() 

        prompt = (
            "Define the main characters for the following concept:\n" +
            content +
            "\n" +
            "Use this framework and template:\n" +
            open('prompts/frameworks/main_characters_framework.md').read()
        )
        characters = self.write(prompt)

        print(f"Here's the characters:\n {characters}\n")
        with open(self.story.path + "/concept.md", 'a') as file:
            file.write("\n\n")
            file.write(characters)

        print("Main characters appended to " + self.story.concept + "\n")
        #self.story.set_main_characters(characters)
        #print("Main characters saved to " + self.story.path + "/main_characters.md")

    def define_setting(self):
        print("Defining the setting\n")

        with open(self.story.concept, 'r') as file:
            content = file.read() 

        prompt = (
            "Define the setting for the following concept:\n" +
            content +
            "\n" +
            "Use this framework and template:\n" +
            open('prompts/frameworks/setting_framework.md').read()
        )
        setting = self.write(prompt)
        print(f"Here's the setting:\n {setting}\n")
        with open(self.story.path + "/concept.md", 'a') as file:
            file.write("\n\n")
            file.write(setting)
        print("Main characters appended to " + self.story.path + "/concept.md")

    def develop_narrative_outline(self):
        """
        Develops detailed narrative outline for the story.

        Steps:
        1. Reads the story concept and plot outline.
        2. Generates a detailed list of chapters using the LLM.
        3. Validates and parses the generated content.
        4. Saves the chapters to the story object.
        """

        narrative_outline = ""

        # Developing chapters and scenes
        print("Developing chapter outline\n")

        with open(self.story.concept, 'r') as concept_file:
            concept_content = concept_file.read()

        with open(self.story.plot_outline, 'r') as plot_file:
            plot_content = plot_file.read()

        prompt = (
            "Develop a detailed list of chapters for the following concept and plot outline:\n" +
            concept_content +
            "\n\n" +
            plot_content +
            "\n" +
            "Use this template:\n" +
            open('prompts/frameworks/narrative_outline_template.md').read()
        )
        narrative_outline_content = generate_planning_text(prompt)
        print(f"Here's the chapters:\n {narrative_outline_content}\n")


        #self.story.set_chapters(chapters)   
        self.story.narrative_outline = StoryAsset(path=os.path.join(self.story.path, ASSETS_DIR), name=NARRATIVE_OUTLINE, content=narrative_outline_content)       
        print("Narrative outline saved\n")

    def developer_chapter_summary(self):
        """
        Drafts a summary for each chapter of the story.
        """
        #Get the narrative outline
        with open(self.story.narrative_outline.full_version_file, 'r') as file:
            narrative_outline_content = file.read()

        #turn it into JSON by calling generate_json_from_text(narrative_outline)
        prompt = (
            "Turn the following narrative outline into a JSON object:\n" +
            narrative_outline_content +
            "\n" +
            "Use this template:\n" +
            open('prompts/frameworks/narrative_outline_template.json').read()
        )
        narrative_outline_json = generate_json(prompt)
        print(f"Here's the narrative outline:\n {narrative_outline_json}\n")

        #For each chapter in the json, generate a summary
        for chapter in narrative_outline_json:
            print(f"Here's the chapter:\n {chapter}\n")

            #Send the concept, plot, outline, and the chapter to the generate_narrative_summary function
            prompt = (
                "Draft a summary for the following chapter based "
                f"the concept:\n {self.story.concept} \n "
                f"the plot outline:\n {self.story.plot_outline} \n"
                f"the narrative outline:\n {self.narrative_outline} \n"
                f"and the chapter:\n {chapter} \n"
                "Use this template:\n" +
                open('prompts/frameworks/chapter_summary_template.md').read()
            )
            chapter_summary_content = generate_planning_text(prompt)
            print(f"Here's the narrative summary:\n {chapter_summary_content}\n")

            self.chapter_summary = StoryAsset(path=self.story.path, name=CHAPTER_SUMMARY, content=chapter_summary_content)
            print(f"Here's the narrative summary:\n {chapter_summary_content}\n")

            return self.chapter_summary.full_content



    def draft_opening_scene(self):
        """
        Drafts the opening scene of the story.
        """

        chapter_summary = self.developer_chapter_summary()
        print(f"\n\nCHECK: Here's the chapter summary:\n {chapter_summary}\n")

        prompt = (
            "Draft a compelling 500 word opening scene for the following chapter summary. " 
            "Ensure that it grips the reader so that they want to read more of the story.\n" +
            "Here is the broader context for the story:\n" +
            self.story.concept +
            "\n"
        )
        if chapter_summary:
            prompt += (
                "Here is the chapter summary:\n" +
                chapter_summary +
                "\n"
            )
        if self.story.writing_style:
            prompt += (
                "Here is the writing style:\n" +
                self.story.writing_style +
                "\n"
            )
        opening_scene = generate_narrative_text(prompt)[0].text
        print(f"Here's the opening scene:\n {opening_scene}\n")

        with open(os.path.join(self.story.path, 'opening_scene.md'), 'w') as file:
            file.write(opening_scene)
        print("Opening scene saved to " + os.path.join(self.story.path, 'opening_scene.md') + "\n")


    def develop_timeline(self):
        """
        Develops a chronological timeline of events for the story.

        Steps:
        1. Reads the story concept and plot outline.
        2. Generates a detailed timeline using the LLM.
        3. Validates and parses the generated content.
        4. Saves the timeline to the story object.
        """

        timeline = ""

        # Developing the timeline
        print("Developing the timeline\n")

        with open(self.story.concept, 'r') as concept_file:
            concept_content = concept_file.read()

        with open(self.story.plot_outline, 'r') as plot_file:
            plot_content = plot_file.read()

        prompt = (
            "Develop a detailed chronological timeline of events for the following concept and plot outline:\n" +
            concept_content +
            "\n\n" +
            plot_content +
            "\n" +
            "Use this framework and template:\n" +
            open('prompts/frameworks/timeline_template.md').read()
        )
        timeline = self.write(prompt)
        print(f"Here's the timeline:\n {timeline}\n")

        self.story.set_timeline(timeline)
        
        print("Timeline saved to " + self.story.timeline + "\n")

""" # Main iterative process
Function PrepareNovel():
    While iteration_count < max_iterations:
        # Step 1: High-Level Planning
        DevelopConceptAndThemes()
        ConductResearch()

        # Step 2: Structural Planning
        CreatePlotOutlineAndTimeline()

        # Step 3: Character and Setting Development
        DevelopCharactersAndSettings()

        # Step 4: Theme and Motif Integration
        IntegrateThemesAndSymbols()

        # Step 5: Detailed Plot Development
        DevelopChaptersAndScenes()

        # Step 6: Dialogue and Language
        WriteDialogueAndDefineNarrativeVoice()

        # Step 7: Execution and Flexibility
        DraftOpeningAndEstablishSchedule()

        # Step 8: Revision and Feedback
        IntegrateFeedbackAndRevise()

        # Step 9: Backup and Organization
        BackupWork()

        # Increment iteration count and check readiness
        iteration_count += 1
        if CheckReadiness():
            Break
    EndWhile

# Define individual steps with progress tracking and dependencies
Function DevelopConceptAndThemes():
    Define core idea and central themes
    Mark progress as complete if well-developed

Function ConductResearch():
    Gather historical, cultural info, summarize critical theories
    Mark progress as complete if sufficient

Function CreatePlotOutlineAndTimeline():
    Develop plot outline and intertextual references
    Create chronological timeline of events
    Mark progress as complete if detailed

Function DevelopCharactersAndSettings():
    Create detailed character profiles and arcs
    Write setting descriptions ensuring cultural, historical accuracy
    Mark progress as complete if robust

Function IntegrateThemesAndSymbols():
    List primary, secondary themes and recurring symbols
    Mark progress as complete if integrated

Function DevelopChaptersAndScenes():
    Create chapter summaries and detailed scene list
    Mark progress as complete if aligned

Function WriteDialogueAndDefineNarrativeVoice():
    Write key dialogues, define narrative voice and techniques
    Plan tone and mood for story parts
    Mark progress as complete if defined

Function DraftOpeningAndEstablishSchedule():
    Draft prologue or first chapter, set writing routine and goals
    Mark progress as complete if established

Function IntegrateFeedbackAndRevise():
    Share manuscript with beta readers, revise based on feedback
    Mark progress as complete if integrated

Function BackupWork():
    Schedule regular backups using cloud storage or external drives
    Mark progress as complete if backed up

# Function to perform a readiness check
Function CheckReadiness():
    Define readiness criteria for each element
    Return True if all elements meet criteria, otherwise return False

# Execute the main function
PrepareNovel() """