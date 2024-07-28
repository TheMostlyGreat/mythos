from .base import StoryAsset

class Inspiration(StoryAsset):

    @property
    def ASSET_TYPE(self):
        return "inspiration"
