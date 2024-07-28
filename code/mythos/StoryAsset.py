import os
from mythos.constants import ASSETS_DIR, ASSET_SUMMARY_LENGTH
from mythos.story_llm import generate_planning_text
from mythos.file_utils import ensure_unique_directory, create_unique_file

class StoryAsset:
    """
    A class to represent a story asset with full and brief versions.

    Attributes:
    ----------
    name : str
        The name of the story asset.
    full_version_file : str
        The file path for the full version of the story asset.
    summary_file : str
        The file path for the summary version of the story asset.
    """

    def __init__(self, path: str, name: str, content: str, full_version_file: str = None, summary_file: str = None) -> None:
        """
        Constructs all the necessary attributes for the StoryAsset object.

        Parameters:
        ----------
        name : str
            The name of the story asset.
        content : str
            The content of the story asset.
        full_version_file : str
            The file path for the full version of the story asset.
        summary_file : str
            The file path for the summary version of the story asset.
        """
        self.name = name
        self.details = content
        self.details_filepath = None
        self.summary = None
        self.summary_filepath = None

        self.base_path = path
        self.full_version_file = full_version_file
        self.summary_file = summary_file
        self.full_content = content

        # If a full version file is provided, use it to initialize the Asset
        if full_version_file:
            self.name = os.path.basename(full_version_file).replace('.md', '').rsplit('_', 1)[0]
            self.full_content = self.load_full_version()

            # If a summary file is provided, use it to initialize the summary
            if summary_file:
                self.summary = self.load_summary()

            # If no summary file is provided, create a new one
            else:
                summary_content = self.generate_summary_content(self.content)
                self.save_summary(summary_content)
        
        else:
            # If no full version file is provided, create a new one
            self.full_version_file = os.path.join(self.base_path, self.name.replace(' ', '_'), ".md") #set the filename
        
            # Save the full version content
            self.save_full_version(content)

    def generate_details(self, context):
        #raise NotImplementedError("This method should be overridden by subclasses.")
        return self.details
    
    def generate_summary(self, context):
        #raise NotImplementedError("This method should be overridden by subclasses.")
        return self.summary

    def load_full_version(self):
        """
        Loads the full version of the story asset from the file.

        Returns:
        -------
        str
            The content of the full version file.
        """
        with open(self.full_version_file, 'r') as file:
            return file.read()

    def load_summary(self):
        """
        Loads the summary version of the story asset from the file.

        Returns:
        -------
        str
            The content of the summary version file.
        """
        with open(self.summary_file, 'r') as file:
            return file.read()

    def generate_summary_content(self, content):
        """
        Generates a summary version of the given content.

        Parameters:
        ----------
        content : str
            The content to be summarized.

        Returns:
        -------
        str
            The summary version of the content.
        """
        return generate_planning_text(f"Create a {ASSET_SUMMARY_LENGTH} word summary of the following content."
                             "Focus on brevity, clarity, and specificity. Focus on the details most important "
                             "to the writer who will use this to draft the story:\n"
                             "\n{content}"
                             )

    def save_full_version(self, content):
        """
        Saves the content to the full version file and generates the summary version.

        Parameters:
        ----------
        content : str
            The content to be written to the full version file.
        """
        self.full_content = content

        # Ensure the assets directory exists
        ensure_unique_directory(self.base_path)  
        
        # Save the full version content
        self.full_version_file = create_unique_file(content, self.base_path, self.name.replace(' ', '_'), ".md")
        
        # Generate the summary version content
        summary_content = self.generate_summary_content(content)
        
        # Save the summary version content
        self.save_summary(summary_content)

    def save_summary(self, content):
        """
        Saves the content to the summary version file.

        Parameters:
        ----------
        content : str
            The content to be written to the summary version file.
        """
        self.summary_file = create_unique_file(content, self.base_path, self.name.replace(' ', '_')+"_summary", ".md")