import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set
from mythos.utils.logger import get_logger


class FileChangeTracker:
    """
    Tracks changes to story asset markdown files using modification timestamps.
    
    Uses separate storage (.mythos/changes.json) to avoid modifying Story model.
    Focuses on minimal, fast detection with proper error handling.
    """
    
    def __init__(self):
        """Initialize the file change tracker."""
        self.logger = get_logger(self.__class__.__name__)
    
    def _get_cache_file_path(self, story_dir: Path) -> Path:
        """
        Get the path to the changes cache file for a story.
        
        Args:
            story_dir: Path to the story directory
            
        Returns:
            Path to the .mythos/changes.json file
        """
        mythos_dir = story_dir / ".mythos"
        return mythos_dir / "changes.json"
    
    def _ensure_cache_directory(self, story_dir: Path) -> None:
        """
        Ensure the .mythos directory exists for storing change tracking data.
        
        Args:
            story_dir: Path to the story directory
        """
        mythos_dir = story_dir / ".mythos"
        try:
            mythos_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            self.logger.error(f"Failed to create .mythos directory in {story_dir}: {e}")
            raise
    
    def _get_markdown_files(self, story_dir: Path) -> List[Path]:
        """
        Get all markdown files in the story's asset directories.
        
        Args:
            story_dir: Path to the story directory
            
        Returns:
            List of paths to markdown files
        """
        markdown_files = []
        
        # Define directories to scan for markdown files
        asset_dirs = [
            story_dir / "assets",
            story_dir / "manuscript",
        ]
        
        for asset_dir in asset_dirs:
            if asset_dir.exists() and asset_dir.is_dir():
                try:
                    # Recursively find all .md files
                    for md_file in asset_dir.rglob("*.md"):
                        if md_file.is_file():
                            markdown_files.append(md_file)
                except OSError as e:
                    self.logger.warning(f"Error scanning directory {asset_dir}: {e}")
                    continue
        
        return markdown_files
    
    def _get_file_mtime(self, file_path: Path) -> Optional[float]:
        """
        Get the modification time of a file with error handling.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Modification time as float timestamp, or None if error
        """
        try:
            return file_path.stat().st_mtime
        except (OSError, FileNotFoundError) as e:
            self.logger.warning(f"Cannot get modification time for {file_path}: {e}")
            return None
    
    def _load_cached_timestamps(self, story_dir: Path) -> Dict[str, float]:
        """
        Load previously cached file timestamps.
        
        Args:
            story_dir: Path to the story directory
            
        Returns:
            Dictionary mapping relative file paths to timestamps
        """
        cache_file = self._get_cache_file_path(story_dir)
        
        if not cache_file.exists():
            return {}
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('file_timestamps', {})
        except (json.JSONDecodeError, OSError, KeyError) as e:
            self.logger.warning(f"Failed to load cached timestamps from {cache_file}: {e}")
            return {}
    
    def _save_timestamps(self, story_dir: Path, timestamps: Dict[str, float]) -> None:
        """
        Save file timestamps to cache.
        
        Args:
            story_dir: Path to the story directory
            timestamps: Dictionary mapping relative file paths to timestamps
        """
        self._ensure_cache_directory(story_dir)
        cache_file = self._get_cache_file_path(story_dir)
        
        cache_data = {
            'file_timestamps': timestamps,
            'last_updated': self._get_file_mtime(Path.cwd()) or 0  # Current time fallback
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
        except OSError as e:
            self.logger.error(f"Failed to save timestamps to {cache_file}: {e}")
            raise
    
    def check_for_changes(self, story_dir: Path) -> Dict[str, bool]:
        """
        Check which story asset markdown files have changed since last check.
        
        Args:
            story_dir: Path to the story directory
            
        Returns:
            Dictionary mapping relative file paths to change status (True = changed)
        """
        try:
            # Convert to Path object if string
            if isinstance(story_dir, str):
                story_dir = Path(story_dir)
            
            # Get current markdown files
            current_files = self._get_markdown_files(story_dir)
            
            # Load cached timestamps
            cached_timestamps = self._load_cached_timestamps(story_dir)
            
            # Check for changes
            changes = {}
            
            for file_path in current_files:
                # Get relative path from story directory for consistent keys
                try:
                    relative_path = str(file_path.relative_to(story_dir))
                except ValueError:
                    # File is not under story_dir, skip it
                    continue
                
                current_mtime = self._get_file_mtime(file_path)
                
                if current_mtime is None:
                    # File exists but can't read mtime - treat as changed
                    changes[relative_path] = True
                    continue
                
                cached_mtime = cached_timestamps.get(relative_path)
                
                if cached_mtime is None:
                    # New file - treat as changed
                    changes[relative_path] = True
                else:
                    # Compare timestamps (with small tolerance for filesystem precision)
                    changes[relative_path] = abs(current_mtime - cached_mtime) > 1.0
            
            # Check for deleted files
            for cached_path in cached_timestamps:
                if cached_path not in changes:
                    # File was deleted - treat as changed
                    changes[cached_path] = True
            
            return changes
            
        except Exception as e:
            self.logger.error(f"Error checking for changes in {story_dir}: {e}")
            return {}
    
    def update_baseline(self, story_dir: Path) -> None:
        """
        Update the baseline timestamps for all current markdown files.
        
        Args:
            story_dir: Path to the story directory
        """
        try:
            # Convert to Path object if string
            if isinstance(story_dir, str):
                story_dir = Path(story_dir)
            
            # Get current markdown files and their timestamps
            current_files = self._get_markdown_files(story_dir)
            timestamps = {}
            
            for file_path in current_files:
                try:
                    relative_path = str(file_path.relative_to(story_dir))
                    mtime = self._get_file_mtime(file_path)
                    
                    if mtime is not None:
                        timestamps[relative_path] = mtime
                    
                except ValueError:
                    # File is not under story_dir, skip it
                    continue
            
            # Save updated timestamps
            self._save_timestamps(story_dir, timestamps)
            self.logger.info(f"Updated baseline timestamps for {len(timestamps)} files in {story_dir}")
            
        except Exception as e:
            self.logger.error(f"Error updating baseline for {story_dir}: {e}")
            raise
    
    def get_changed_files(self, story_dir: Path) -> List[str]:
        """
        Get list of files that have changed since last baseline.
        
        Args:
            story_dir: Path to the story directory
            
        Returns:
            List of relative file paths that have changed
        """
        changes = self.check_for_changes(story_dir)
        return [path for path, changed in changes.items() if changed]
    
    def has_any_changes(self, story_dir: Path) -> bool:
        """
        Check if any files have changed since last baseline.
        
        Args:
            story_dir: Path to the story directory
            
        Returns:
            True if any files have changed, False otherwise
        """
        changes = self.check_for_changes(story_dir)
        return any(changes.values()) 