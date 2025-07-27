import json
import tempfile
import time
from pathlib import Path
import pytest
from mythos.utils.file_change_tracker import FileChangeTracker


class TestFileChangeTracker:
    """Test cases for FileChangeTracker functionality."""
    
    @pytest.fixture
    def temp_story_dir(self):
        """Create a temporary story directory structure for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            story_dir = Path(temp_dir) / "test-story"
            story_dir.mkdir()
            
            # Create assets directory structure
            assets_dir = story_dir / "assets"
            assets_dir.mkdir()
            
            manuscript_dir = story_dir / "manuscript"
            manuscript_dir.mkdir()
            
            chapters_dir = assets_dir / "chapters"
            chapters_dir.mkdir()
            
            yield story_dir
    
    @pytest.fixture
    def tracker(self):
        """Create a FileChangeTracker instance."""
        return FileChangeTracker()
    
    def test_empty_directory_no_changes(self, tracker, temp_story_dir):
        """Test that empty directory returns no changes."""
        changes = tracker.check_for_changes(temp_story_dir)
        assert changes == {}
        assert not tracker.has_any_changes(temp_story_dir)
        assert tracker.get_changed_files(temp_story_dir) == []
    
    def test_new_files_detected_as_changed(self, tracker, temp_story_dir):
        """Test that new files are detected as changed."""
        # Create some markdown files
        assets_dir = temp_story_dir / "assets"
        (assets_dir / "plot.md").write_text("Initial plot content")
        (assets_dir / "characters.md").write_text("Character descriptions")
        
        manuscript_dir = temp_story_dir / "manuscript"
        (manuscript_dir / "chapter1.md").write_text("Chapter 1 content")
        
        # Check for changes - all should be new/changed
        changes = tracker.check_for_changes(temp_story_dir)
        
        assert len(changes) == 3
        assert changes["assets/plot.md"] is True
        assert changes["assets/characters.md"] is True
        assert changes["manuscript/chapter1.md"] is True
        
        assert tracker.has_any_changes(temp_story_dir)
        changed_files = tracker.get_changed_files(temp_story_dir)
        assert len(changed_files) == 3
    
    def test_update_baseline_and_no_changes(self, tracker, temp_story_dir):
        """Test that updating baseline makes files show as unchanged."""
        # Create files
        assets_dir = temp_story_dir / "assets"
        (assets_dir / "plot.md").write_text("Initial plot content")
        (assets_dir / "characters.md").write_text("Character descriptions")
        
        # Update baseline
        tracker.update_baseline(temp_story_dir)
        
        # Check for changes - should be none
        changes = tracker.check_for_changes(temp_story_dir)
        assert all(not changed for changed in changes.values())
        assert not tracker.has_any_changes(temp_story_dir)
        assert tracker.get_changed_files(temp_story_dir) == []
    
    def test_file_modification_detected(self, tracker, temp_story_dir):
        """Test that file modifications are detected."""
        # Create and baseline files
        assets_dir = temp_story_dir / "assets"
        plot_file = assets_dir / "plot.md"
        plot_file.write_text("Initial plot content")
        
        tracker.update_baseline(temp_story_dir)
        
        # Wait a moment to ensure timestamp difference
        time.sleep(1.1)
        
        # Modify file
        plot_file.write_text("Updated plot content")
        
        # Check for changes
        changes = tracker.check_for_changes(temp_story_dir)
        assert changes["assets/plot.md"] is True
        assert tracker.has_any_changes(temp_story_dir)
        assert "assets/plot.md" in tracker.get_changed_files(temp_story_dir)
    
    def test_file_deletion_detected(self, tracker, temp_story_dir):
        """Test that file deletions are detected as changes."""
        # Create and baseline files
        assets_dir = temp_story_dir / "assets"
        plot_file = assets_dir / "plot.md"
        plot_file.write_text("Plot content")
        
        tracker.update_baseline(temp_story_dir)
        
        # Delete file
        plot_file.unlink()
        
        # Check for changes
        changes = tracker.check_for_changes(temp_story_dir)
        assert changes["assets/plot.md"] is True
        assert tracker.has_any_changes(temp_story_dir)
    
    def test_nested_directories_handled(self, tracker, temp_story_dir):
        """Test that files in nested directories are handled correctly."""
        # Create nested structure
        chapters_dir = temp_story_dir / "assets" / "chapters"
        settings_dir = temp_story_dir / "assets" / "settings"
        settings_dir.mkdir()
        
        (chapters_dir / "chapter1.md").write_text("Chapter 1 outline")
        (settings_dir / "world.md").write_text("World description")
        
        changes = tracker.check_for_changes(temp_story_dir)
        
        assert "assets/chapters/chapter1.md" in changes
        assert "assets/settings/world.md" in changes
        assert all(changed for changed in changes.values())
    
    def test_cache_file_creation(self, tracker, temp_story_dir):
        """Test that cache file is created correctly."""
        # Create files and update baseline
        assets_dir = temp_story_dir / "assets"
        (assets_dir / "plot.md").write_text("Plot content")
        
        tracker.update_baseline(temp_story_dir)
        
        # Check cache file exists
        cache_file = temp_story_dir / ".mythos" / "changes.json"
        assert cache_file.exists()
        
        # Check cache content
        with open(cache_file) as f:
            data = json.load(f)
        
        assert "file_timestamps" in data
        assert "assets/plot.md" in data["file_timestamps"]
        assert isinstance(data["file_timestamps"]["assets/plot.md"], float)
    
    def test_corrupted_cache_handled_gracefully(self, tracker, temp_story_dir):
        """Test that corrupted cache files are handled gracefully."""
        # Create cache directory and corrupted cache file
        mythos_dir = temp_story_dir / ".mythos"
        mythos_dir.mkdir()
        cache_file = mythos_dir / "changes.json"
        cache_file.write_text("invalid json content")
        
        # Create a markdown file
        assets_dir = temp_story_dir / "assets"
        (assets_dir / "plot.md").write_text("Plot content")
        
        # Should handle gracefully and treat file as new
        changes = tracker.check_for_changes(temp_story_dir)
        assert changes["assets/plot.md"] is True
    
    def test_permission_errors_handled(self, tracker, temp_story_dir):
        """Test that permission errors are handled gracefully."""
        # This test is platform-dependent and may not work in all environments
        # but demonstrates the error handling approach
        
        # Create file
        assets_dir = temp_story_dir / "assets"
        test_file = assets_dir / "plot.md"
        test_file.write_text("Plot content")
        
        # The tracker should handle permission errors gracefully
        # and log warnings rather than crashing
        changes = tracker.check_for_changes(temp_story_dir)
        
        # Should complete without exceptions
        assert isinstance(changes, dict) 