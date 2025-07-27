"""
UI utilities for terminal output with colors and special formatting.
"""

# ANSI color codes for terminal output
class Colors:
    RED = '\033[31m'
    YELLOW = '\033[33m'
    GREEN = '\033[32m'
    CYAN = '\033[36m'
    RESET = '\033[0m'


def print_error(message: str):
    """Print error message in red color."""
    print(f"{Colors.RED}{message}{Colors.RESET}")


def print_warning(message: str):
    """Print warning message in yellow color."""
    print(f"{Colors.YELLOW}{message}{Colors.RESET}")


def print_thinking(message: str = "Thinking..."):
    """Print thinking indicator for LLM calls."""
    print(f"\n🤔 {message}")


def print_progress_step(step_name: str, description: str = "", min_level = None):
    """
    Enhanced progress indicator that works with the new ProgressTracker.

    Args:
        step_name: Name of the step being performed
        description: Optional description of what's happening
        min_level: Minimum verbosity level (ProgressLevel enum)
    """
    try:
        from mythos.utils.progress_tracker import get_progress_tracker, ProgressLevel
        
        # Set default level if not specified
        if min_level is None:
            min_level = ProgressLevel.NORMAL
            
        tracker = get_progress_tracker()

        # If we have an active session, use progress tracking
        if tracker and tracker.session_start_time is not None:
            tracker.start_step(step_name, description, min_level)
        else:
            # Fallback to enhanced print_thinking style
            if description:
                print(f"\n🔄 {step_name}")
                print(f"   {description}")
            else:
                print(f"\n🔄 {step_name}...")
    except Exception:
        # Ultimate fallback to simple print_thinking
        print_thinking(step_name)


def complete_progress_step(step_name: str, result_summary: str = "", min_level = None):
    """
    Mark a progress step as complete.

    Args:
        step_name: Name of completed step
        result_summary: Optional summary of what was accomplished
        min_level: Minimum verbosity level (ProgressLevel enum)
    """
    try:
        from mythos.utils.progress_tracker import get_progress_tracker, ProgressLevel
        
        # Set default level if not specified
        if min_level is None:
            min_level = ProgressLevel.NORMAL
            
        tracker = get_progress_tracker()

        # If we have an active session, use progress tracking
        if tracker and tracker.session_start_time is not None:
            tracker.complete_step(step_name, result_summary, min_level)
        else:
            # Fallback to simple completion message
            if result_summary:
                print(f"✅ {step_name} completed")
                print(f"   {result_summary}")
            else:
                print(f"✅ {step_name} completed")
    except Exception:
        # Ultimate fallback - just print completion
        print(f"✅ {step_name} completed")


def confirm_next_step(current_step: str, next_step: str, story_title: str = "") -> bool:
    """
    Ask user if they want to proceed to the next step in story creation.
    
    Args:
        current_step (str): Description of what was just completed
        next_step (str): Description of what will happen next
        story_title (str): Optional story title for context
        
    Returns:
        bool: True if user wants to continue, False otherwise
    """
    title_context = f" for '{story_title}'" if story_title else ""
    
    print(f"\n✅ {current_step} completed{title_context}!")
    print(f"📋 Next step: {next_step}")
    print("\nWould you like to continue to the next step?")
    print("1. ✅ Yes, continue")
    print("2. 📋 No, stop here (you can resume later)")
    
    while True:
        try:
            choice = input("\nEnter your choice (1 or 2): ").strip()
            if choice == "1":
                return True
            elif choice == "2":
                print(f"\n📋 Stopping here. You can resume this story later by selecting 'Resume an existing story'.")
                return False
            else:
                print_warning("Please enter 1 or 2.")
        except KeyboardInterrupt:
            print_warning("\n\nExiting Mythos. Happy writing! ✨")
            exit(0) 