import os
from mythos.story_llm import generate_planning_text
from mythos.file_utils import create_unique_file

class Character:    
    """
    A class to represent a character in a story.

    Attributes
    ----------
    name : str
        The name of the character.
    description : str
        A brief description of the character.
    filepath : str
        The filepath where the character's profile is stored.
    base_path : str
        The base directory path for storing character profiles.
    """

    def __init__(self, path: str, name: str, description: str, filepath: str = None, summary_filepath: str = None) -> None:
        """
        Constructs all the necessary attributes for the character object.

        Parameters
        ----------
        name : str
            The name of the character.
        description : str
            A brief description of the character.
        filepath : str, optional
            The filepath where the character's profile is stored. If not provided, a new file will be created.
        """
        self.name = name
        self.description = description
        self.summary_filepath = summary_filepath
        self.filepath = filepath
        self.base_path = path

        if filepath:
            # If a filepath is provided, use it
            self.filepath = filepath
            
            temp_summary = filepath.replace(".md", "_summary.md")

            if summary_filepath:
                self.summary_filepath = summary_filepath
            elif os.path.exists(temp_summary):
                self.summary_filepath = temp_summary
            else:
                self.summary_filepath = self.summarize()

        else:
            print(f"About to save character: {self.name}\n"
                  f"Description: {self.description}\n"
                  f"Path: {self.base_path}\n")
            self.filepath = self.set_profile(self.description)

            
    def summarize(self):
        """
        Summarizes the character's profile.
        """
        prompt = (
            "Create a summary for the following character. "
            "The summary should be under 300 words. "
            "It should concise, specific, and capture the "
            "most important parts of the character that a writer will need to know "
            "to create a compelling plot, develop the character, write great dialogue: \n"
            f"Name: {self.name}\n"
            f"Description: {self.description}\n"
        )
        summary = generate_planning_text(prompt)
        print(summary)

        if self.summary_filepath and os.path.exists(self.summary_filepath):
            with open(self.summary_filepath, 'r') as file:
                summary = file.read()
            return self.summary_filepath
        else:
            temp_summary = os.path.basename(self.filepath).replace(".md", "_summary.md")
            self.summary_filepath = create_unique_file(content=summary, filename=temp_summary, path=self.base_path)

        return self.summary_filepath

    def set_profile(self, profile: str) -> None:
        """
        Sets the profile of the character.

        Parameters
        ----------
        profile : str
            The profile description to be written to the character's file.
        """
        
        if self.filepath and os.path.exists(self.filepath):
            with open(self.filepath, "w") as file:
                file.write(profile)
        else:
            self.filepath = create_unique_file(content=profile, filename=self.name, path=self.base_path)
        
        self.summary_filepath = self.summarize()

        return self.filepath

    def get_profile(self) -> str:
        """
        Gets the profile of the character.

        Returns
        -------
        str
            The profile description read from the character's file.
        """
        with open(self.filepath, "r") as file:
            return file.read()