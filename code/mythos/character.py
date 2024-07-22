import os
from mythos.story import Story

class Character:
    name = ""
    description = ""
    filename = ""
    base_path = "characters"
    story = None

    def __init__(self, story, name, description):
        self.story = story
        self.name = name
        self.description = description
        self.base_path = f"{self.story.path}/{self.base_path}"
        self.filename = f"{self.base_path}/{self.name.replace(' ', '_')}.md"

        # Ensure the base_path directory exists
        os.makedirs(self.base_path, exist_ok=True)

        base_filename, ext = os.path.splitext(self.filename)
        counter = 1
        while os.path.exists(self.filename):
            # Use the base filename and append '_counter' before the extension
            self.filename = f"{base_filename}_{counter}{ext}"
            counter += 1

        with open(self.filename, "w") as file:
            file.write(self.description)


    def set_profile(self, profile):
        
        with open(self.filename, "w") as file:
            file.write(profile)

    def get_profile(self):
        with open(self.filename, "r") as file:
            return file.read()