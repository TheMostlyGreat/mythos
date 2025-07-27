import time
import pytest
from mythos.utils.progress_tracker import ProgressTracker, get_progress_tracker, start_story_progress
from mythos.utils.ui_utils import print_progress_step, complete_progress_step


class TestProgressTracker:
    """Test cases for ProgressTracker functionality."""
    
    def test_basic_progress_tracking(self):
        """Test basic progress tracking functionality."""
        tracker = ProgressTracker("Test Story")
        tracker.start_session("Test Generation")
        
        assert tracker.story_title == "Test Story"
        assert tracker.current_phase == "Test Generation"
        assert tracker.step_count == 0
        assert tracker.session_start_time is not None
        assert len(tracker.completed_steps) == 0
        
    def test_step_progression(self):
        """Test step start and completion."""
        tracker = ProgressTracker("Test Story")
        tracker.start_session("Test Generation")
        
        # Start a step
        tracker.start_step("Test Step", "Testing step functionality")
        assert tracker.step_count == 1
        assert tracker.step_start_time is not None
        
        # Complete the step
        time.sleep(0.1)  # Small delay to ensure measurable duration
        tracker.complete_step("Test Step", "Step completed successfully")
        
        assert len(tracker.completed_steps) == 1
        step = tracker.completed_steps[0]
        assert step['name'] == "Test Step"
        assert step['summary'] == "Step completed successfully"
        assert step['duration'] != "unknown"
        
    def test_chapter_progress_display(self):
        """Test chapter progress display functionality."""
        tracker = ProgressTracker("Test Story")
        
        # This should not raise an exception
        tracker.show_chapter_progress(2, 5, "Chapter Two")
        
    def test_duration_formatting(self):
        """Test duration formatting."""
        tracker = ProgressTracker()
        
        assert tracker._format_duration(30) == "30s"
        assert tracker._format_duration(90) == "1m 30s"
        assert tracker._format_duration(3661) == "1h 1m"
        
    def test_title_formatting(self):
        """Test story title formatting."""
        tracker = ProgressTracker("My Great Story")
        assert tracker._format_title() == '"My Great Story"'
        
        tracker = ProgressTracker("")
        assert tracker._format_title() == "Your Story"
        
        tracker = ProgressTracker("Untitled")
        assert tracker._format_title() == "Your Story"
        
    def test_global_tracker(self):
        """Test global tracker functionality."""
        tracker1 = get_progress_tracker()
        tracker2 = get_progress_tracker()
        
        # Should return the same instance
        assert tracker1 is tracker2
        
    def test_convenience_functions(self):
        """Test convenience functions for starting progress."""
        tracker = start_story_progress("Convenience Test")
        
        assert tracker.story_title == "Convenience Test"
        assert tracker.current_phase == "Story Generation"
        assert tracker.session_start_time is not None


class TestEnhancedUIUtils:
    """Test cases for enhanced UI utility functions."""
    
    def test_print_progress_step_with_tracker(self):
        """Test print_progress_step with active tracker."""
        # Start a session
        tracker = start_story_progress("UI Test")
        
        # This should use the tracker
        print_progress_step("Test Step", "Testing with active tracker")
        assert tracker.step_count == 1
        
        complete_progress_step("Test Step", "Completed with tracker")
        assert len(tracker.completed_steps) == 1
        
    def test_print_progress_step_fallback(self):
        """Test print_progress_step fallback behavior."""
        # Reset global tracker to ensure no active session
        import mythos.utils.progress_tracker
        mythos.utils.progress_tracker._global_tracker = None
        
        # This should fall back gracefully without errors
        print_progress_step("Fallback Step", "Testing fallback behavior")
        complete_progress_step("Fallback Step", "Fallback completed")
        
    def test_extraction_chapter_number(self):
        """Test the _extract_chapter_number helper function."""
        from mythos.services.story_builder import StoryBuilder
        
        builder = StoryBuilder()
        
        # Test various chapter title formats
        assert builder._extract_chapter_number("chapter_1") == 1
        assert builder._extract_chapter_number("Chapter 5") == 5
        assert builder._extract_chapter_number("chapter_10") == 10
        assert builder._extract_chapter_number("Chapter 2: The Beginning") == 2
        assert builder._extract_chapter_number("no_number_here") == 1  # Default fallback
        
    def test_session_cleanup_and_reset(self):
        """Test that session cleanup and reset functionality works correctly."""
        from mythos.utils.progress_tracker import (
            start_story_progress, 
            end_current_session, 
            get_progress_tracker,
            reset_progress_tracker
        )
        
        # Start a session
        tracker1 = start_story_progress("Test Story 1")
        tracker1.start_step("Step 1", "Testing step")
        assert tracker1.session_start_time is not None
        assert tracker1.story_title == "Test Story 1"
        
        # End session should reset state
        end_current_session()
        
        # Get new tracker should be fresh instance
        tracker2 = get_progress_tracker()
        assert tracker2.session_start_time is None
        assert tracker2.story_title == ""
        assert tracker2.step_count == 0
        
        # Manual reset should also work
        tracker3 = start_story_progress("Test Story 2")
        tracker3.start_step("Another step", "More testing")
        reset_progress_tracker()
        
        tracker4 = get_progress_tracker()
        assert tracker4.session_start_time is None
        assert tracker4.story_title == "" 