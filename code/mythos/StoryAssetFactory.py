class StoryAssetFactory:
    @staticmethod
    def create_asset(asset_type):
        if asset_type == "character":
            return Character()
        elif asset_type == "setting":
            return Setting()
        # Add more conditions for each subclass
        else:
            raise ValueError(f"Unknown asset type: {asset_type}")