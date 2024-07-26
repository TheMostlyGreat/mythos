import os
import re
from mythos.character import Character 
from mythos.constants import STORY_DIR, CORE_PERSPECTIVES, THEMES_AND_MOTIFS
from mythos.StoryAsset import StoryAsset
from mythos.file_utils import ensure_unique_directory, create_unique_file

class Story():
    """
    A class to represent a story.

    This class encapsulates the attributes and methods related to a story,
    including its title, concept, plot outline, characters, setting, and
    other relevant components. It provides functionality to load, save,
    and manage the story's elements.

    Attributes
    ----------
    title : str
        The title of the story.
    concept : str
        The concept of the story.
    path : str
        The path to the story files.
    brief : str
        The story brief.
    characters : list
        A list of characters in the story.
    inspiration : str
        The inspiration behind the story.
    perspectives : list
        The perspectives from which the story can be told.
    plot_outline : str
        The outline of the story's plot.
    research_notes : str
        Notes related to research for the story.
    themes_motifs : str
        The themes and motifs present in the story.
    tone_mood : str
        The tone and mood of the story.
    current_version : int
        The current version of the story.
    older_versions : list
        A list of older versions of the story.
    """
    
    def __init__(self):
        self.title = False
        self.concept = False
        self.path = f"{STORY_DIR}/new_story"
        self.brief = False
        self.characters = False
        self.inspiration = False
        self.perspectives = CORE_PERSPECTIVES
        self.plot_outline = False
        self.research_notes = False
        self.themes_and_motifs = False
        self.tone_mood = False
        
        self.current_version = 0
        self.older_versions = []
        

    def load(self, path):
        """
        Load the story from the specified path.

        This method loads the story's title, concept, plot outline, characters,
        and setting from the specified path. It raises a ValueError if the path
        is not absolute.

        Parameters
        ----------
        path : str
            The absolute path to the story files.

        Raises
        ------
        ValueError
            If the provided path is not absolute.
        """
        # Validate path to prevent directory traversal
        if not os.path.isabs(path):
            raise ValueError("Path must be absolute.")
        
        self.path = os.path.join(STORY_DIR, path)
        self.title = os.path.basename(path).replace('_', ' ').replace('.md', '')
        
        print(f"Loading story: {self.title}\n")
        print(f"Path: {path}\n")
        # Load story concept
        self.concept = self.load_file("concept.md")
        if self.concept:
            print(f"Concept loaded: {self.concept}")
        
        # Load plot outline
        self.plot_outline = self.load_file("plot_outline.md")
        if self.plot_outline:
            print(f"Plot outline loaded: {self.plot_outline}")
        
        # Load characters
        print("Loading characters")
        self.characters = self.load_characters(os.path.join(self.path, Character.BASE_PATH))
        
        # Load setting
        self.setting = self.load_file("setting.md")
        if self.setting:
            print(f"Setting loaded: {self.setting}")
    
    def load_characters(self, char_dir):
        """
        Load characters from the specified directory.

        This method retrieves all character files from the given directory and
        creates Character instances for each file.

        Parameters
        ----------
        char_dir : str
            The directory path where character files are located.

        Returns
        -------
        list
            A list of Character instances loaded from the specified directory.
        """
        characters = []
        if os.path.exists(char_dir):
            characters = [
                Character.from_file(self, os.path.join(char_dir, filename))
                for filename in os.listdir(char_dir) if filename.endswith(".md")
            ]
        return characters

    def set_concept(self, concept):
        """
        Set the story concept.

        This method saves the provided concept to a file and updates the
        internal concept state.

        Parameters
        ----------
        concept : str
            The concept of the story to be saved.
        """
        self.concept = self.save_file("concept", concept)

    def set_research_notes(self, research):
        """
        Set the research notes for the story.

        This method saves the provided research notes to a file and updates
        the internal research notes state.

        Parameters
        ----------
        research : str
            The research notes to be saved.
        """
        self.research_notes = self.save_file("research_notes", research)

    def set_inspiration(self, inspiration):
        self.inspiration = self.save_file("inspiration", inspiration)

    def set_themes_and_motifs(self, themes_motifs):
        self.themes_and_motifs = self.save_file("themes_and_motifs", themes_motifs)

    def set_setting(self, setting):
        self.setting = self.save_file("setting", setting)

    def set_plot_outline(self, plot_outline):
        self.plot_outline = self.save_file("plot_outline", plot_outline)
    
    def set_writing_style(self, writing_style):
        self.writing_style = self.save_file("writing_style", writing_style)

    def set_length(self, length):
        self.length = length

    def set_title(self, title):
        self.title = title
        main_title = title.split(':')[0]  # Use only the main title
        main_title = re.sub(r'[^a-zA-Z0-9\s]', '', main_title.strip())  # Remove special characters, keep alphanumeric and spaces
        self.path = os.path.join(STORY_DIR, main_title.replace(' ', '_'))

    # Save file to New Story directory
    def save_file(self, filename, content):

        # Ensure the story directory exists
        ensure_unique_directory(self.path)
        
        # Determine unique filename
        filename = create_unique_file(content, self.path, filename)
        
        # Return the relative file path
        return filename

    def load_file(self, filename):
        
        filepath = os.path.join(self.path, filename)
        print(f"Loading file: {filename}")
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                content = file.read().strip()
                if content:
                    print(f"File loaded: {filepath}")
                    return filepath
        return None  # Keep this as None

    def get_status(self):
        status = {
            "concept": bool(self.concept),
            "plot_outline": bool(self.plot_outline),
            "characters": bool(self.characters),
            "setting": bool(self.setting)
        }
        for key, value in status.items():
            print(f"{key.capitalize()}: {'Complete' if value else 'Incomplete'}")