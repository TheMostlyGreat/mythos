from mythos.story_assets import *

class StoryAssetFactory:
    @staticmethod
    def create_asset(asset_type: str, story_path: str):
        if asset_type == "character":
            return Character(story_path=story_path, name=asset_type)
        elif asset_type == "setting":
            return Setting(story_path=story_path, name=asset_type)
        elif asset_type == "plot":
            return Plot(story_path=story_path, name=asset_type)
        elif asset_type == "themes":
            return Themes(story_path=story_path, name=asset_type)
        elif asset_type == "writing_style":
            return WritingStyle(story_path=story_path, name=asset_type)
        elif asset_type == "timeline":
            return Timeline(story_path=story_path, name=asset_type)
        elif asset_type == "research":
            return Research(story_path=story_path, name=asset_type)
        elif asset_type == "inspiration":
            return Inspiration(story_path=story_path, name=asset_type)
        elif asset_type == "narrative_outline":
            return NarrativeOutline(story_path=story_path, name=asset_type)
        elif asset_type == "chapter":
            return Chapter(story_path=story_path, name=asset_type)
        elif asset_type == "scene":
            return Scene(story_path=story_path, name=asset_type)
        else:
            raise ValueError(f"Unknown asset type: {asset_type}")