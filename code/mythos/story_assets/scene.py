from .base import StoryAsset

class Scene(StoryAsset):

    @property
    def ASSET_TYPE(self):
        return "scene"

    SCENE_DIR = "scenes"  ## need to figure out loading and character dir

    def __init__(self, summary_length: int = 100) -> None:
        self.summary_length = summary_length
        super().__init__(summary_length=self.summary_length)
