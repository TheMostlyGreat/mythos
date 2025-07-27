import pytest
import time
from mythos.utils.progress_tracker import (
    ProgressTracker, 
    get_progress_tracker, 
    reset_progress_tracker,
    start_story_progress,
    end_current_session
)


class TestProgressTracker:
    
    def setup_method(self):
        """Reset progress tracker before each test."""
        reset_progress_tracker()
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_progress_tracker()
    
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
    
    def test_session_cleanup(self):
        """Test session cleanup functionality."""
        # Start a session
        tracker = start_story_progress("Test Story")
        tracker.start_step("Test Step", "Testing")
        assert tracker.session_start_time is not None
        
        # End session should show summary and reset
        end_current_session()
        
        # Get tracker should be fresh instance
        new_tracker = get_progress_tracker()
        assert new_tracker.session_start_time is None


class TestEnhancedUIUtils:
    
    def setup_method(self):
        """Reset progress tracker before each test."""
        reset_progress_tracker()
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_progress_tracker()
    
    def test_ui_utils_with_active_tracker(self):
        """Test UI utilities work with active tracker."""
        from mythos.utils.ui_utils import print_progress_step, complete_progress_step
        
        # Start a session
        tracker = start_story_progress("UI Test")
        
        # These should work with the active session
        print_progress_step("Test Step", "Testing UI utils")
        complete_progress_step("Test Step", "Completed successfully")
        
        assert len(tracker.completed_steps) == 1
        assert tracker.completed_steps[0]['name'] == "Test Step"
    
    def test_ui_utils_fallback(self):
        """Test UI utilities fallback when no session is active."""
        from mythos.utils.ui_utils import print_progress_step, complete_progress_step
        
        # Should not raise errors when no session is active
        print_progress_step("Fallback Step", "Should use fallback")
        complete_progress_step("Fallback Step", "Should use fallback")
    
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


class TestProgressIntegration:
    """Integration tests for the simplified progress system."""
    
    def setup_method(self):
        """Reset progress tracker before each test."""
        reset_progress_tracker()
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_progress_tracker()
    
    def test_complete_workflow_simulation(self):
        """Test a complete workflow simulation."""
        tracker = start_story_progress("Integration Test Story")
        
        # Simulate story creation workflow
        tracker.start_step("Story Concept", "Creating initial concept")
        time.sleep(0.1)  # Simulate work
        tracker.complete_step("Story Concept", "Concept created successfully")
        
        tracker.start_step("Generate Assets", "Creating planning assets")
        time.sleep(0.1)  # Simulate work
        tracker.complete_step("Generate Assets", "All assets completed")
        
        tracker.start_step("Chapter Writing", "Writing manuscript chapters")
        # Simulate chapter progress
        tracker.show_chapter_progress(1, 3, "Chapter 1: Beginning")
        tracker.show_chapter_progress(2, 3, "Chapter 2: Middle")
        tracker.show_chapter_progress(3, 3, "Chapter 3: End")
        tracker.complete_step("Chapter Writing", "All chapters completed")
        
        assert len(tracker.completed_steps) == 3
        assert tracker.step_count == 3
        
        # Clean up
        end_current_session()
    
    def test_multiple_sequential_sessions(self):
        """Test multiple sequential sessions work correctly."""
        # First session
        tracker1 = start_story_progress("Story 1")
        tracker1.start_step("Step 1")
        tracker1.complete_step("Step 1")
        assert len(tracker1.completed_steps) == 1
        end_current_session()
        
        # Second session should be clean
        tracker2 = start_story_progress("Story 2")
        tracker2.start_step("Resume Step")
        tracker2.complete_step("Resume Step")
        assert len(tracker2.completed_steps) == 1
        assert tracker2.story_title == "Story 2"
        end_current_session()
        
        # No global tracker should remain active
        final_tracker = get_progress_tracker()
        assert final_tracker.session_start_time is None 