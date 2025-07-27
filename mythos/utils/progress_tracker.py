import time
from typing import Optional, Dict, Any
from enum import Enum
from contextlib import contextmanager
from mythos.utils.logger import get_logger


class ProgressLevel(Enum):
    """Progress verbosity levels."""
    MINIMAL = 1    # Only major phases (Resume Assets, Chapter Writing, etc.)
    NORMAL = 2     # Major phases + key milestones (Default)
    DETAILED = 3   # Everything (for debugging/development)


class ProgressTracker:
    """
    Centralized progress tracking with configurable verbosity levels.
    
    Supports three levels of progress detail:
    - MINIMAL: Only major phases
    - NORMAL: Major phases + key milestones (default)
    - DETAILED: All operations (debug mode)
    """
    
    def __init__(self, story_title: str = "", level: ProgressLevel = ProgressLevel.NORMAL):
        """
        Initialize progress tracker.
        
        Args:
            story_title: Title of the story being generated
            level: Progress verbosity level
        """
        self.story_title = story_title
        self.level = level
        self.current_phase = ""
        self.step_count = 0
        self.session_start_time = None
        self.step_start_time = None
        self.completed_steps = []
        self.logger = get_logger(self.__class__.__name__)
        
    def set_level(self, level: ProgressLevel):
        """Set the progress verbosity level."""
        self.level = level
        
    def start_session(self, phase: str = "Story Generation"):
        """
        Start a new progress tracking session.
        
        Args:
            phase: Name of the generation phase
        """
        self.current_phase = phase
        self.step_count = 0
        self.session_start_time = time.time()
        self.completed_steps = []
        
        if self.level.value >= ProgressLevel.MINIMAL.value:
            title_part = self._format_title()
            print(f"\n🚀 {phase}{title_part}")
        
    def start_step(self, step_name: str, description: str = "", min_level: ProgressLevel = ProgressLevel.NORMAL):
        """
        Start a new step within the current session.
        
        Args:
            step_name: Name of the step
            description: Optional description
            min_level: Minimum verbosity level to show this step
        """
        if self.session_start_time is None:
            return  # No active session
            
        # Only show if current level meets minimum requirement
        if self.level.value < min_level.value:
            return
            
        self.step_count += 1
        self.step_start_time = time.time()
        
        if description:
            print(f"\n🔄 Step {self.step_count}: {step_name}")
            print(f"   {description}")
        else:
            print(f"\n🔄 Step {self.step_count}: {step_name}...")
    
    def complete_step(self, step_name: str, result_summary: str = "", min_level: ProgressLevel = ProgressLevel.NORMAL):
        """
        Mark a step as complete.
        
        Args:
            step_name: Name of completed step
            result_summary: Optional summary of results
            min_level: Minimum verbosity level to show this completion
        """
        if self.session_start_time is None:
            return  # No active session
            
        # Only show if current level meets minimum requirement
        if self.level.value < min_level.value:
            return
            
        duration = ""
        if self.step_start_time:
            elapsed = time.time() - self.step_start_time
            if elapsed > 1:  # Only show duration for steps taking > 1 second
                duration = f" ({self._format_duration(elapsed)})"
                
        self.completed_steps.append({
            'name': step_name,
            'summary': result_summary,
            'duration': duration
        })
        
        if result_summary:
            print(f"✅ {step_name} completed{duration}")
            print(f"   {result_summary}")
        else:
            print(f"✅ {step_name} completed{duration}")
    
    def show_progress_summary(self):
        """Show a summary of the completed session."""
        if self.session_start_time is None or self.level.value < ProgressLevel.MINIMAL.value:
            return
            
        total_duration = time.time() - self.session_start_time
        title_part = self._format_title()
        
        print(f"\n📊 {self.current_phase} Summary{title_part}")
        print(f"   ⏱️  Total time: {self._format_duration(total_duration)}")
        print(f"   ✅ Steps completed: {len(self.completed_steps)}")
        
        # Show step details only in DETAILED mode
        if self.level == ProgressLevel.DETAILED and self.completed_steps:
            print("   📋 Steps:")
            for step in self.completed_steps:
                print(f"      • {step['name']}{step['duration']}")
    
    def show_chapter_progress(self, current_chapter: int, total_chapters: int, chapter_title: str):
        """
        Show progress for chapter writing with a simple progress indicator.
        
        Args:
            current_chapter: Current chapter number
            total_chapters: Total number of chapters
            chapter_title: Title of current chapter
        """
        if self.level.value < ProgressLevel.MINIMAL.value:
            return
            
        percentage = (current_chapter / total_chapters) * 100
        progress_bar = self._create_progress_bar(current_chapter, total_chapters)
        
        print(f"\n📖 Writing Chapter {current_chapter}/{total_chapters} ({percentage:.0f}%)")
        print(f"   {progress_bar}")
        print(f"   📝 {chapter_title}")
    
    def _create_progress_bar(self, current: int, total: int, width: int = 20) -> str:
        """Create a simple text progress bar."""
        filled = int((current / total) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def _format_title(self) -> str:
        """Format the story title for display."""
        if self.story_title:
            return f" - {self.story_title}"
        return ""
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in a readable way."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"


# Global progress tracker instance
_global_tracker = None


@contextmanager
def progress_session(story_title: str = "", operation: str = "Story Generation", level: ProgressLevel = ProgressLevel.NORMAL):
    """
    Context manager for progress sessions with automatic cleanup.
    
    Args:
        story_title: Title of the story
        operation: Name of the operation
        level: Progress verbosity level
        
    Usage:
        with progress_session("My Story", "Story Generation") as tracker:
            tracker.start_step("Generate Assets")
            # ... do work ...
            tracker.complete_step("Generate Assets")
    """
    global _global_tracker
    
    # Store previous tracker state
    previous_tracker = _global_tracker
    
    try:
        # Create new tracker for this session
        _global_tracker = ProgressTracker(story_title, level)
        _global_tracker.start_session(operation)
        yield _global_tracker
        
        # Show summary on successful completion
        _global_tracker.show_progress_summary()
        
    except Exception as e:
        # Clean up on error
        if _global_tracker:
            _global_tracker.logger.error(f"Progress session failed: {e}")
        raise
    finally:
        # Restore previous tracker state
        _global_tracker = previous_tracker


def get_progress_tracker() -> Optional[ProgressTracker]:
    """Get the current global progress tracker instance."""
    return _global_tracker


def reset_progress_tracker():
    """Reset the global progress tracker - useful for testing."""
    global _global_tracker
    _global_tracker = None


# Legacy compatibility functions (simplified)
def start_story_progress(story_title: str = "", level: ProgressLevel = ProgressLevel.NORMAL):
    """Legacy function - use progress_session() context manager instead."""
    global _global_tracker
    _global_tracker = ProgressTracker(story_title, level)
    _global_tracker.start_session("Story Generation")
    return _global_tracker


def start_chapter_progress(story_title: str = "", level: ProgressLevel = ProgressLevel.NORMAL):
    """Legacy function - use progress_session() context manager instead."""
    global _global_tracker
    _global_tracker = ProgressTracker(story_title, level)
    _global_tracker.start_session("Chapter Writing")
    return _global_tracker


def end_current_session():
    """Legacy function - use progress_session() context manager instead."""
    global _global_tracker
    if _global_tracker and _global_tracker.session_start_time is not None:
        _global_tracker.show_progress_summary()
    reset_progress_tracker() 