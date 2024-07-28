from .base import StoryAsset

class WritingStyle(StoryAsset):

    @property
    def ASSET_TYPE(self):
        return "writing_style"