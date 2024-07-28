from .base import StoryAsset

class Character(StoryAsset):

    @property
    def ASSET_TYPE(self):
        return "character"

    CHARACTER_DIR = "characters" ## need to figure out loading and character dir
    
    def __init__(self, summary_length: int = 100) -> None:
        self.summary_length = summary_length
        super().__init__(summary_length=self.summary_length)
    

