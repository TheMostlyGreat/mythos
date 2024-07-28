import os
import pickle
from mythos.story_llm import generate_planning_text
from mythos.file_utils import ensure_unique_directory, create_unique_file, save_file


class StoryAsset:
    @property
    def ASSET_TYPE(self):
        pass

    ASSET_DIR = "asset"
    ASSET_BIN_DIR = os.path.join(ASSET_DIR, "bin")

    def __init__(self, story_path: str, name: str=ASSET_TYPE, details_filepath: str = None, summary_filepath: str = None, summary_length: int = 300) -> None:
        """
        Initializes a StoryAsset instance with the given parameters.

        This constructor sets up the StoryAsset with the provided story path, name, 
        details file path, summary file path, and summary length. It also initializes 
        the asset and binary file paths. If a summary file path is provided, it loads 
        the asset from the file.

        Parameters
        ----------
        story_path : str
            The path to the story directory.
        name : str, optional
            The name of the asset. Defaults to ASSET_TYPE.
        details_filepath : str, optional
            The file path to the asset's details. Defaults to None.
        summary_filepath : str, optional
            The file path to the asset's summary. Defaults to None.
        summary_length : int, optional
            The maximum length of the summary in words. Defaults to 300.

        Returns
        -------
        None

        Raises
        ------
        None

        Examples
        --------
        Creating a StoryAsset instance:

        >>> asset = StoryAsset(story_path="/path/to/story", name="MyAsset")
        >>> print(asset.name)
        MyAsset
        """
        self.name = name
        self.details = None
        self.details_filepath = details_filepath
        self.summary = None
        self.summary_filepath = summary_filepath
        self.summary_length = summary_length
        self.asset_path = os.path.join(story_path, self.ASSET_DIR)
        self.bin_filepath = os.path.join(story_path, self.ASSET_BIN_DIR, self.name.replace(' ', '_')+".pkl")

        # If a details filepath is provided, use it to initialize the Asset
        if summary_filepath:
            self = self.load(summary_filepath) 

    def generate_details(self, context):

        print(f"Generating details for {self.name}.'\n")

        with open(context, 'r') as context:
            context_content = context.read()

        prompt = (
            f"Develop a details for {self.name} for my story using the following context:\n" +
            context_content +
            "\n\n" +
            "Use this template:\n" +
            open(f'prompts/templates/{self.ASSET_TYPE}_template.md').read()
        )
        self.details = generate_planning_text(prompt)
        print(f"Here are the details for {self.name}:\n {self.details}\n")

        save_file(content=self.details, filepath=self.details_filepath)
        self.save()

        print(f"{self.name} details saved to {self.details_filepath}\n"
              f"{self.name} pickle saved to {self.bin_filepath}\n")

    def generate_summary(self, context):

        print(f"Generating summary of {self.name}.\n")

        with open(context, 'r') as context:
            context_content = context.read()

        prompt = (
            f"Develop a summary for {self.name} for my story using the following context\n" +
            f"Please keep it under {self.summary_length} words.\n" +
            context_content +
            "\n\n" +
            "Use this template:\n" +
            open(f'prompts/templates/{self.ASSET_TYPE}_summary_template.md').read()
        )
        self.summary = generate_planning_text(prompt)
        print(f"Here is the summary for {self.name}:\n {self.summary}\n")

        save_file(content=self.summary, filepath=self.summary_filepath)
        self.save()


        print(f"{self.name} summary saved to {self.summary_filepath}\n"
              f"{self.name} pickle saved to {self.bin_filepath}\n")

    
    def save(self):
        with open(self.bin_filepath, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load(filepath):
        with open(filepath, 'rb') as file:
            return pickle.load(file)