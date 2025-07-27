import time
from typing import Optional, Dict, Any
from mythos.utils.logger import get_logger


class ProgressTracker:
    """
    Simplified progress tracking for story generation.
    
    Shows current step and basic progress without trying to predict
    total steps or exact timing due to conditional generation flows.
    """
    
    def __init__(self, story_title: str = ""):
        """
        Initialize progress tracker.
        
        Args:
            story_title: Title of the story being generated
        """
        self.story_title = story_title
        self.current_phase = ""
        self.step_count = 0
        self.session_start_time = None
        self.step_start_time = None
        self.completed_steps = []
        self.logger = get_logger(self.__class__.__name__)
        
    def start_session(self, phase: str = "Story Generation"):
        """
        Start a new progress tracking session.
        
        Args:
            phase: Name of the generation phase (e.g., "Story Generation", "Chapter Writing")
        """
        self.current_phase = phase
        self.step_count = 0
        self.session_start_time = time.time()
        self.completed_steps = []
        
        print(f"\n🚀 {phase}: {self._format_title()}")
        print("=" * 60)
        
    def start_step(self, step_name: str, description: str = ""):
        """
        Start tracking a new step.
        
        Args:
            step_name: Short name for the step
            description: Optional longer description
        """
        self.step_count += 1
        self.step_start_time = time.time()
        
        # Show progress indicator
        if description:
            print(f"\n🔄 Step {self.step_count}: {step_name}")
            print(f"   {description}")
        else:
            print(f"\n🔄 Step {self.step_count}: {step_name}...")
            
        # Flush output so user sees it immediately
        import sys
        sys.stdout.flush()
        
    def complete_step(self, step_name: str, result_summary: str = ""):
        """
        Mark current step as complete.
        
        Args:
            step_name: Name of completed step
            result_summary: Optional summary of what was accomplished
        """
        if self.step_start_time:
            elapsed = time.time() - self.step_start_time
            elapsed_str = self._format_duration(elapsed)
        else:
            elapsed_str = "unknown"
            
        self.completed_steps.append({
            'name': step_name,
            'duration': elapsed_str,
            'summary': result_summary
        })
        
        if result_summary:
            print(f"✅ {step_name} completed ({elapsed_str}) - {result_summary}")
        else:
            print(f"✅ {step_name} completed ({elapsed_str})")
            
    def show_progress_summary(self):
        """Show summary of completed steps."""
        if not self.completed_steps:
            return
            
        total_elapsed = time.time() - self.session_start_time if self.session_start_time else 0
        
        print(f"\n📊 Progress Summary - {self.current_phase}")
        print("-" * 40)
        
        for i, step in enumerate(self.completed_steps, 1):
            summary = f" - {step['summary']}" if step['summary'] else ""
            print(f"{i:2d}. ✅ {step['name']} ({step['duration']}){summary}")
            
        print(f"\n⏱️  Total time: {self._format_duration(total_elapsed)}")
        
    def show_chapter_progress(self, current_chapter: int, total_chapters: int, chapter_title: str):
        """
        Show progress for chapter writing phase.
        
        Args:
            current_chapter: Current chapter number (1-based)
            total_chapters: Total number of chapters
            chapter_title: Title of current chapter
        """
        percentage = int((current_chapter / total_chapters) * 100)
        bar_length = 40
        filled_length = int(bar_length * current_chapter / total_chapters)
        
        bar = "━" * filled_length + "─" * (bar_length - filled_length)
        
        print(f"\n📖 Writing Chapters: {self._format_title()}")
        print(f"{bar} {current_chapter}/{total_chapters} ({percentage}%)")
        print(f"🔄 Chapter {current_chapter}: {chapter_title}")
        
    def _format_title(self) -> str:
        """Format story title for display."""
        if self.story_title and self.story_title != "Untitled":
            return f'"{self.story_title}"'
        return "Your Story"
        
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{int(seconds)}s"
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


def get_progress_tracker() -> ProgressTracker:
    """Get the global progress tracker instance."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = ProgressTracker()
    return _global_tracker


def reset_progress_tracker():
    """Reset the global progress tracker - useful for testing and session cleanup."""
    global _global_tracker
    _global_tracker = None


def start_story_progress(story_title: str = ""):
    """Convenience function to start story generation progress tracking."""
    tracker = get_progress_tracker()
    tracker.story_title = story_title
    tracker.start_session("Story Generation")
    return tracker


def start_chapter_progress(story_title: str = ""):
    """Convenience function to start chapter writing progress tracking."""
    tracker = get_progress_tracker()
    tracker.story_title = story_title
    tracker.start_session("Chapter Writing")
    return tracker


def end_current_session():
    """End the current progress session and reset tracker state."""
    tracker = get_progress_tracker()
    if tracker.session_start_time is not None:
        tracker.show_progress_summary()
    reset_progress_tracker() 