import os
import pickle
from mythos.story_llm import generate_planning_text
from mythos.file_utils import save_file

class StoryAsset:
    ASSET_DIR = "asset"
    ASSET_BIN_DIR = "bin"

    def __init__(self, path: str, asset_type: str, name: str=None, 
                 summary_length: int = 300) -> None:
        """
        Initializes a StoryAsset instance with the given parameters.

        Parameters
        ----------
        path : str
            The path to the story directory.
        asset_type : str
            The type of the asset.
        name : str, optional
            The name of the asset. Defaults to the asset type.
        summary_length : int, optional
            The maximum length of the summary in words. Defaults to 300.

        Returns
        -------
        None

        Examples
        --------
        Creating a StoryAsset instance:

        >>> asset = StoryAsset(path="/path/to/story", asset_type="MyAsset")
        >>> print(asset.name)
        MyAsset
        """
        self.name = name if name else asset_type  # Set the name of the asset
        self.asset_type = asset_type  # Set the type of the asset
        self.asset_path = path  # Set the path to the asset
        self.bin_filepath = os.path.join(path, self.ASSET_BIN_DIR, self.name.replace(' ', '_')+".pkl")  # Path to save binary file

        self.details = None  # Initialize details to None
        self.details_filepath = os.path.join(path, self.name.replace(' ', '_')+".md")  # Path to save details

        self.summary = None  # Initialize summary to None
        self.summary_filepath = os.path.join(path, self.name.replace(' ', '_')+"_summary.md")  # Path to save summary
        self.summary_length = summary_length  # Set the maximum length of the summary
        
    def set_details(self, content):
        """
        Sets the details of the asset and saves it to the details file.

        Parameters
        ----------
        content : str
            The content to be set as the details of the asset.

        Returns
        -------
        None
        """
        print(f"Setting details for {self.name}.'\n")

        self.details = content  # Set the details of the asset
        
        save_file(content=self.details, filepath=self.details_filepath)  # Save details to file
        self.save()  # Save the current state of the asset

        print(f"{self.name} details saved to {self.details_filepath}\n"
              f"{self.name} pickle saved to {self.bin_filepath}\n")
        
        self.set_summary()  # Generate and save the summary

    def set_summary(self, content=None):
        """
        Sets the summary of the asset and saves it to the summary file.

        Parameters
        ----------
        content : str, optional
            The content to be set as the summary of the asset. If not provided, 
            a summary will be generated based on the details.

        Returns
        -------
        None
        """
        print(f"Setting the summary of {self.name}.\n")

        if content:
            self.summary = content  # Set the summary if content is provided
        else:
            prompt = (
                f"Write a summary for {self.name} for the story."
                 "Focus on clarity, brevity, and specificity."
                 "Please keep it under {self.summary_length} words."
                 "Ensure the most important details are captured."
                 f"Here is the details for {self.name}:\n"
                 f"{self.details}\n\n"
            )

            self.summary = generate_planning_text(prompt)  # Generate summary using the prompt

            print(f"Here is the summary for {self.name}:\n {self.summary}\n")

        save_file(content=self.summary, filepath=self.summary_filepath)  # Save summary to file
        self.save()  # Save the current state of the asset

        print(f"{self.name} summary saved to {self.summary_filepath}\n"
              f"{self.name} pickle saved to {self.bin_filepath}\n")

    def save(self):
        """
        Saves the current state of the asset to a binary file.

        Returns
        -------
        None
        """
        os.makedirs(os.path.dirname(self.bin_filepath), exist_ok=True)
        
        with open(self.bin_filepath, 'wb') as file:
            pickle.dump(self, file)  # Save the asset instance to a binary file

    @staticmethod
    def load(filepath):
        """
        Loads a StoryAsset instance from a binary file.

        Parameters
        ----------
        filepath : str
            The path to the binary file.

        Returns
        -------
        StoryAsset
            The loaded StoryAsset instance.
        """
        with open(filepath, 'rb') as file:
            return pickle.load(file)  # Load the asset instance from a binary file