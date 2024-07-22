import os

import re

class Story():
    base_path = "../stories"

    def __init__(self):
        #high-level_planning
        self.title = False
        self.path = "New Story"
        self.concept = False
        self.themes = False
        self.genre = False
        self.audience = False
        self.plot_outline = False
        self.research_notes = False
        self.character_profiles = False
        self.setting_descriptions = False
        self.themes_symbols = False
        self.chapter_breakdown = False
        self.scene_list = False
        self.dialogue_snippets = False
        self.narrative_voice = False
        self.timeline = False
        self.inspiration = False
        self.tone_mood = False
        self.syntax_rhythm = False
        self.feedback = False
        self.older_versions = []
        self.current_version = 0

    
    
    # Set concept
    def set_concept(self, concept):

        self.concept = self.save_file("concept", concept)

    def set_research_notes(self, research):
        self.research_notes = self.save_file("research_notes", research)

    def set_inspiration(self, inspiration):
        self.inspiration = self.save_file("inspiration", inspiration)

    def set_themes(self, themes):
        self.themes = self.save_file("themes", themes)

    def set_setting(self, setting):
        self.setting = self.save_file("setting", setting)

    def set_characters(self, characters):
        self.characters = self.save_file("characters", characters)

    def set_plot_outline(self, plot_outline):
        self.plot_outline = self.save_file("plot_outline", plot_outline)
    
    def set_timeline(self, timeline):
        self.timeline = self.save_file("timeline", timeline)

    def set_writing_style(self, writing_style):
        self.writing_style = self.save_file("writing_style", writing_style)

    def set_length(self, length):
        self.length = length

    def set_narrative_outline(self, narrative_outline):
        self.narrative_outline = narrative_outline

        self.save_file("narrative_outline", self.narrative_outline)

    def set_plot(self, plot):
        self.plot = plot

        self.save_file("plot", self.plot)

    def set_title(self, title):
        self.title = title
        main_title = title.split(':')[0]  # Use only the main title
        main_title = re.sub(r'[^a-zA-Z0-9\s]', '', main_title.strip())  # Remove special characters, keep alphanumeric and spaces
        self.path = os.path.join(self.base_path, main_title.replace(' ', '_'))

    # Save file to New Story directory
    def save_file(self, filename, content):

        # Create directory if it doesn't exist
        os.makedirs(self.path, exist_ok=True)
            
        # Determine file name
        base_filename = f"{self.path}/{filename}"
        extension = ".md"
        filename = base_filename + extension
        counter = 1
        
        while os.path.exists(filename):
            # Use the base filename and append '-counter' before the extension
            filename = f"{base_filename}-{counter}{extension}"
            counter += 1
        
        # Write to file
        with open(filename, "w") as file:
            file.write(content)

        # Return the relative file path
        return filename

    