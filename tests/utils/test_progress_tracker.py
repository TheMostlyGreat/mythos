import pytest
import time
from mythos.utils.progress_tracker import (
    ProgressTracker, 
    ProgressLevel,
    get_progress_tracker, 
    progress_session,
    reset_progress_tracker,
    start_story_progress
)


class TestProgressTracker:
    
    def setup_method(self):
        """Reset progress tracker before each test."""
        reset_progress_tracker()
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_progress_tracker()
    
    def test_progress_levels(self):
        """Test that progress levels work correctly."""
        tracker = ProgressTracker("Test Story", ProgressLevel.MINIMAL)
        
        # Start a session
        tracker.start_session("Test Phase")
        
        # MINIMAL level should not show normal steps
        tracker.start_step("Normal Step", "Should not show", ProgressLevel.NORMAL)
        tracker.complete_step("Normal Step", "Should not show", ProgressLevel.NORMAL)
        
        # MINIMAL level should show minimal steps
        tracker.start_step("Major Phase", "Should show", ProgressLevel.MINIMAL)
        tracker.complete_step("Major Phase", "Should show", ProgressLevel.MINIMAL)
        
        assert len(tracker.completed_steps) == 1
        assert tracker.completed_steps[0]['name'] == "Major Phase"
    
    def test_context_manager_session(self):
        """Test the context manager for progress sessions."""
        with progress_session("Test Story", "Test Operation", ProgressLevel.NORMAL) as tracker:
            assert tracker.story_title == "Test Story"
            assert tracker.current_phase == "Test Operation"
            assert tracker.session_start_time is not None
            
            tracker.start_step("Test Step")
            tracker.complete_step("Test Step", "Success")
            
        # After context exit, global tracker should be reset
        global_tracker = get_progress_tracker()
        assert global_tracker is None
    
    def test_nested_sessions_isolation(self):
        """Test that nested sessions are properly isolated."""
        with progress_session("Story 1", "Operation 1") as tracker1:
            tracker1.start_step("Step 1")
            
            with progress_session("Story 2", "Operation 2") as tracker2:
                assert tracker2.story_title == "Story 2"
                assert tracker2.current_phase == "Operation 2"
                tracker2.start_step("Step 2")
                
            # After nested session, original tracker should be restored
            current_tracker = get_progress_tracker()
            assert current_tracker is tracker1  # Original tracker should be restored
            
        # After outer context, global tracker should be reset
        final_tracker = get_progress_tracker()
        assert final_tracker is None
    
    def test_error_handling_in_session(self):
        """Test that errors in sessions are handled properly."""
        with pytest.raises(ValueError):
            with progress_session("Test Story", "Test Operation") as tracker:
                tracker.start_step("Test Step")
                raise ValueError("Test error")
                
        # Tracker should be cleaned up even after error
        global_tracker = get_progress_tracker()
        assert global_tracker is None
    
    def test_chapter_progress_display(self):
        """Test chapter progress display with different levels."""
        # MINIMAL level should show chapter progress
        tracker = ProgressTracker("Test Story", ProgressLevel.MINIMAL)
        tracker.start_session("Chapter Writing")
        tracker.show_chapter_progress(3, 10, "Chapter 3: The Journey")
        
        # DETAILED level should also show
        tracker.set_level(ProgressLevel.DETAILED)
        tracker.show_chapter_progress(4, 10, "Chapter 4: The Discovery")
    
    def test_progress_bar_creation(self):
        """Test progress bar creation."""
        tracker = ProgressTracker()
        
        # Test various progress levels
        bar1 = tracker._create_progress_bar(1, 4, 20)
        assert len(bar1) == 22  # [20 chars + 2 brackets]
        assert bar1.count("█") == 5  # 1/4 * 20 = 5
        
        bar2 = tracker._create_progress_bar(3, 4, 20)
        assert bar2.count("█") == 15  # 3/4 * 20 = 15
        
        bar3 = tracker._create_progress_bar(4, 4, 20)
        assert bar3.count("█") == 20  # Full bar
    
    def test_duration_formatting(self):
        """Test duration formatting."""
        tracker = ProgressTracker()
        
        assert tracker._format_duration(30.5) == "30.5s"
        assert tracker._format_duration(90) == "1m 30s"
        assert tracker._format_duration(3661) == "1h 1m"
    
    def test_legacy_compatibility(self):
        """Test that legacy functions still work."""
        # Test legacy start function
        tracker = start_story_progress("Legacy Test", ProgressLevel.NORMAL)
        assert tracker.story_title == "Legacy Test"
        assert tracker.current_phase == "Story Generation"
        
        # Clean up
        reset_progress_tracker()


class TestEnhancedUIUtils:
    
    def setup_method(self):
        """Reset progress tracker before each test."""
        reset_progress_tracker()
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_progress_tracker()
    
    def test_ui_utils_with_context_manager(self):
        """Test UI utilities work with context manager sessions."""
        from mythos.utils.ui_utils import print_progress_step, complete_progress_step
        
        with progress_session("Test Story", "Test Operation") as tracker:
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
    
    def test_ui_utils_with_verbosity_levels(self):
        """Test UI utilities respect verbosity levels."""
        from mythos.utils.ui_utils import print_progress_step, complete_progress_step
        
        with progress_session("Test Story", "Test Operation", ProgressLevel.MINIMAL) as tracker:
            # NORMAL level step should not show in MINIMAL mode
            print_progress_step("Normal Step", "Should not show", ProgressLevel.NORMAL)
            complete_progress_step("Normal Step", "Should not show", ProgressLevel.NORMAL)
            
            # MINIMAL level step should show
            print_progress_step("Major Step", "Should show", ProgressLevel.MINIMAL)
            complete_progress_step("Major Step", "Should show", ProgressLevel.MINIMAL)
            
            assert len(tracker.completed_steps) == 1
            assert tracker.completed_steps[0]['name'] == "Major Step"
    
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
    """Integration tests for the complete progress system."""
    
    def setup_method(self):
        """Reset progress tracker before each test."""
        reset_progress_tracker()
    
    def teardown_method(self):
        """Clean up after each test."""
        reset_progress_tracker()
    
    def test_complete_workflow_simulation(self):
        """Test a complete workflow simulation with context manager."""
        with progress_session("Integration Test Story", "Story Creation", ProgressLevel.NORMAL) as tracker:
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
    
    def test_error_recovery_workflow(self):
        """Test workflow with error recovery."""
        try:
            with progress_session("Error Test Story", "Story Creation") as tracker:
                tracker.start_step("Good Step", "This should work")
                tracker.complete_step("Good Step", "Success")
                
                tracker.start_step("Bad Step", "This will fail")
                raise RuntimeError("Simulated failure")
                
        except RuntimeError:
            pass  # Expected
            
        # Verify cleanup happened properly
        assert get_progress_tracker() is None
    
    def test_multiple_sequential_sessions(self):
        """Test multiple sequential sessions work correctly."""
        # First session
        with progress_session("Story 1", "Creation") as tracker1:
            tracker1.start_step("Step 1")
            tracker1.complete_step("Step 1")
            assert len(tracker1.completed_steps) == 1
            
        # Second session should be clean
        with progress_session("Story 2", "Resume") as tracker2:
            tracker2.start_step("Resume Step")
            tracker2.complete_step("Resume Step")
            assert len(tracker2.completed_steps) == 1
            assert tracker2.story_title == "Story 2"
            
        # No global tracker should remain
        assert get_progress_tracker() is None 