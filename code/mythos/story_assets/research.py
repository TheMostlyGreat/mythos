from .base import StoryAsset

class Research(StoryAsset):

    @property
    def ASSET_TYPE(self):
        return "research"
