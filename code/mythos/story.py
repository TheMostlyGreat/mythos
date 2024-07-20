import os

class Story():
    title = "Title not yet set"
    path = "Path not yet set"
    concept = "Concept not yet set"
    themes = "Themes not yet set"
    setting = "Setting not yet set"
    characters = "Characters not yet set"
    writing_style = "Writing style not yet set"
    length = "Length not yet set"
    narrative_outline = "Narrative outline not yet set"


    # Set concept
    def set_concept(self, concept):
        self.concept = concept

        self.save_file("concept", self.concept)

    def set_themes(self, themes):
        self.themes = themes

        self.save_file("themes", self.themes)

    def set_setting(self, setting):
        self.setting = setting

        self.save_file("setting", self.setting)

    def set_characters(self, characters):
        self.characters = characters

        self.save_file("characters", self.characters)

    def set_writing_style(self, writing_style):
        self.writing_style = writing_style

        self.save_file("writing_style", self.writing_style)

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

    # Save file to New Story directory
    def save_file(self, filename, content):
        # Create directory if it doesn't exist
        os.makedirs("New Story", exist_ok=True)
            
        # Determine file name
        base_filename = f"New Story/{filename}"
        extension = ".md"
        filename = base_filename + extension
        counter = 1
        
        while os.path.exists(filename):
            filename = f"{base_filename}-{counter}{extension}"
            counter += 1
        
        # Write to file
        with open(filename, "w") as file:
            file.write(content)

    