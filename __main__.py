from mythos.services.story_builder import StoryBuilder
from mythos.story.story_manager import StoryManager
from mythos.utils.llm_utils import get_total_token_usage
from pathlib import Path
import os


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


def display_welcome():
    """Display welcome message and project explanation."""
    print("\n" + "="*60)
    print("          🌟 MYTHOS: AI Story Writing Assistant 🌟")
    print("="*60)
    print("\nWelcome to Mythos! This AI-powered tool helps you transform")
    print("your story ideas into fully developed narratives.")
    print("\nHow it works:")
    print("• Share your story concept (any length - from a sentence to a paragraph)")
    print("• Mythos generates detailed story assets: characters, plot, themes, etc.")
    print("• Creates a complete chapter-by-chapter manuscript")
    print("• Exports your story as an EPUB file")
    print("\nExamples of good prompts:")
    print("• 'A detective who can see memories by touching objects'")
    print("• 'Two rival chefs forced to work together during an alien invasion'")
    print("• 'A coming-of-age story set in a world where music has magical powers'")
    print("\n" + "-"*60)


def get_user_concept():
    """Prompt user for their story concept."""
    print("\nPlease describe your story concept:")
    print("(Press Enter twice when finished, or Ctrl+C to exit)\n")
    
    lines = []
    empty_line_count = 0
    
    try:
        while True:
            line = input()
            if line.strip() == "":
                empty_line_count += 1
                if empty_line_count >= 2:
                    break
                lines.append(line)
            else:
                empty_line_count = 0
                lines.append(line)
        
        concept = "\n".join(lines).strip()
        
        if not concept:
            print_error("\nNo concept provided. Please try again.\n")
            return get_user_concept()
            
        return concept
        
    except KeyboardInterrupt:
        print("\n\nExiting Mythos. Happy writing! ✨")
        exit(0)


def confirm_concept(concept):
    """Ask user to confirm their concept before processing."""
    print("\n" + "-"*60)
    print("YOUR STORY CONCEPT:")
    print("-"*20)
    print(f'"{concept}"')
    print("-"*60)
    
    while True:
        response = input("\nProceed with this concept? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print_warning("Please enter 'y' for yes or 'n' for no.")


def display_story_assets(story):
    """Display generated story assets for user review."""
    print("\n" + "="*60)
    print("📋 STORY ASSETS GENERATED")
    print("="*60)
    print(f"\n📖 Story Title: {story.title}")
    print(f"💭 Original Concept: {story.user_prompt}")
    
    # Display key assets with summaries
    asset_order = [
        'Concept', 'Research', 'Settings', 'Plot', 'Themes', 
        'Characters', 'Timeline', 'Chapter List', 'Writing Style'
    ]
    
    for asset_name in asset_order:
        if asset_name in story.assets:
            asset = story.assets[asset_name]
            print(f"\n📌 {asset_name.upper()}:")
            print("-" * 40)
            if asset.summary:
                print(asset.summary)
            else:
                # If no summary, show first 200 chars of details
                details = asset.details[:200] + "..." if len(asset.details) > 200 else asset.details
                print(details)
    
    print("\n" + "="*60)


def confirm_proceed_to_chapters():
    """Ask user if they want to proceed with chapter generation."""
    print("\n🤔 Would you like to proceed with generating the full manuscript?")
    print("This will create detailed chapter content based on the assets above.")
    print("Note: Chapter generation may take several additional minutes.")
    
    while True:
        response = input("\nProceed with chapter generation? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print_warning("Please enter 'y' for yes or 'n' for no.")


def get_user_choice():
    """Ask user whether to create a new story or continue an existing one."""
    print("\nWhat would you like to do?")
    print("1. 📝 Create a new story from scratch")
    print("2. 📖 Continue writing chapters for an existing story")
    print("3. 🚪 Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1, 2, or 3): ").strip()
            if choice == "1":
                return "new"
            elif choice == "2":
                return "continue"
            elif choice == "3":
                return "exit"
            else:
                print_warning("Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print_warning("\n\nExiting Mythos. Happy writing! ✨")
            exit(0)


def list_existing_stories():
    """List all existing stories in the stories directory."""
    stories_dir = Path("./stories")
    if not stories_dir.exists():
        return []
    
    story_directories = []
    for item in stories_dir.iterdir():
        if item.is_dir():
            # Look for .story files in the directory
            story_files = list(item.glob("*.story"))
            if story_files:
                story_directories.append(item.name)
    
    return sorted(story_directories)


def select_existing_story():
    """Allow user to select an existing story to continue."""
    existing_stories = list_existing_stories()
    
    if not existing_stories:
        print_warning("\n❌ No existing stories found in the 'stories' directory.")
        print("Create a new story first, then you can continue it later.")
        return None
    
    print(f"\n📚 Found {len(existing_stories)} existing stories:")
    print("-" * 60)
    
    # Load story manager to get progress info
    story_manager = StoryManager()
    
    for i, story_name in enumerate(existing_stories, 1):
        # Try to load story to get progress
        try:
            story = story_manager.load_story(story_name)
            if story:
                progress = story_manager.get_story_progress_summary(story)
                display_title = story.title if story.title != "Untitled" else story_name.replace('-', ' ').title()
                print(f"{i}. {display_title} - {progress}")
            else:
                print(f"{i}. {story_name.replace('-', ' ').title()} - ❓ Unable to load")
        except Exception:
            print(f"{i}. {story_name.replace('-', ' ').title()} - ❌ Error loading")
    
    print(f"{len(existing_stories) + 1}. 🔙 Go back to main menu")
    
    while True:
        try:
            choice = input(f"\nSelect a story (1-{len(existing_stories) + 1}): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(existing_stories):
                selected_story = existing_stories[choice_num - 1]
                # Load story again to get the actual title for confirmation
                try:
                    story = story_manager.load_story(selected_story)
                    display_title = story.title if story and story.title != "Untitled" else selected_story.replace('-', ' ').title()
                    print(f"\n✅ Selected: {display_title}")
                except Exception:
                    print(f"\n✅ Selected: {selected_story.replace('-', ' ').title()}")
                return selected_story
            elif choice_num == len(existing_stories) + 1:
                return None
            else:
                print_warning(f"Please enter a number between 1 and {len(existing_stories) + 1}")
        except ValueError:
            print_warning("Please enter a valid number.")
        except KeyboardInterrupt:
            print_warning("\n\nExiting Mythos. Happy writing! ✨")
            exit(0)


def continue_existing_story():
    """Continue writing chapters for an existing story."""
    story_title = select_existing_story()
    if not story_title:
        return False  # User chose to go back
    
    try:
        story_manager = StoryManager()
        story_builder = StoryBuilder()
        
        # Load the existing story
        print(f"\n📂 Loading story: {story_title}")
        story = story_manager.load_story(story_title)
        
        if not story:
            print_error(f"❌ Failed to load story: {story_title}")
            print_error("The story file may be corrupted or missing.")
            return False
        
        print(f"✅ Successfully loaded: {story.title}")
        
        # Get current story state and show progress
        state, description = story_manager.get_story_state(story)
        progress_summary = story_manager.get_story_progress_summary(story)
        
        print(f"\n📊 Current Progress: {progress_summary}")
        print(f"📋 Status: {description}")
        
        # Handle complete stories
        if state == "complete":
            print("\n🎉 This story is already complete!")
            print(f"📁 Check the 'stories/{story_title}' directory for your story files")
            print("📖 Look for the .epub file to read your finished story")
            return True
        
        # Display current story assets
        display_story_assets(story)
        
        # Confirm before proceeding
        proceed = input(f"\nContinue from where you left off? (y/n): ").lower().strip()
        if proceed not in ['y', 'yes']:
            print("📋 Story continuation cancelled.")
            return False
        
        print(f"\n🚀 Resuming story from current state...")
        print("This may take a few minutes depending on what needs to be completed.")
        print("Please be patient while we continue your story!\n")
        
        # Smart resume from current state
        story = story_builder.smart_resume_story(story)
        
        total_tokens = get_total_token_usage()
        
        print("\n" + "="*60)
        print("✨ SUCCESS! Your story has been updated! ✨")
        print("="*60)
        print(f"\n📊 Total tokens used: {total_tokens:,}")
        print(f"\n📁 Check the 'stories/{story_title}' directory for your complete story files")
        
        # Check final state to customize success message
        final_state, _ = story_manager.get_story_state(story)
        if final_state == "complete":
            print("📖 Look for the .epub file to read your finished story")
        else:
            print("🔄 Run again to continue from the new progress point")
            
        print("\nThank you for using Mythos! Happy writing! 🌟\n")
        
        return True
        
    except Exception as e:
        print_error(f"\n❌ Error while continuing story: {e}")
        print_error("Please check the story files and try again.")
        return False


def create_new_story():
    """Create a new story from scratch."""
    while True:
        concept = get_user_concept()
        
        if confirm_concept(concept):
            break
        else:
            print("\nLet's try again with a different concept.\n")
    
    print("\n🚀 Starting story asset generation...")
    print("This will create the foundation for your story (characters, plot, themes, etc.)")
    print("Please be patient while the AI works its magic!\n")
    
    try:
        story_builder = StoryBuilder()
        
        # Phase 1: Generate story assets only
        story = story_builder.build_story_assets(concept)
        
        # Display assets for user review
        display_story_assets(story)
        
        # Ask user if they want to proceed to chapter generation
        if confirm_proceed_to_chapters():
            print("\n📝 Starting chapter generation...")
            print("This may take several minutes to create your complete manuscript.")
            print("Please be patient while we write your story!\n")
            
            # Phase 2: Generate chapter content
            story = story_builder.build_story_content(story)
            
            total_tokens = get_total_token_usage()
            
            print("\n" + "="*60)
            print("✨ SUCCESS! Your complete story has been generated! ✨")
            print("="*60)
            print(f"\n📊 Total tokens used: {total_tokens:,}")
            print("\n📁 Check the 'stories' directory for your complete story files")
            print("📖 Look for the .epub file to read your finished story")
            print("\nThank you for using Mythos! Happy writing! 🌟\n")
        else:
            print("\n📋 Story assets saved! You can use these as a foundation for your writing.")
            print(f"📁 Check the 'stories/{story.title}' directory for your story assets")
            print("\nTo generate chapters later, you can run Mythos again and select option 2.")
            print("\nThank you for using Mythos! Happy writing! 🌟\n")
        
        return True
        
    except Exception as e:
        print_error(f"\n❌ Error during story generation: {e}")
        print_error("Please check your configuration and try again.")
        return False


def __main__():
    """Main CLI entry point."""
    display_welcome()
    
    try:
        while True:
            choice = get_user_choice()
            
            if choice == "new":
                success = create_new_story()
                if success:
                    break  # Exit after successful story creation
            elif choice == "continue":
                success = continue_existing_story()
                if success:
                    break  # Exit after successful chapter generation
                # If not successful, return to main menu
            elif choice == "exit":
                print("\nThank you for using Mythos! Happy writing! 🌟\n")
                exit(0)
        
    except KeyboardInterrupt:
        print_warning("\n\n⚠️  Operation interrupted by user.")
        print("Exiting Mythos. Happy writing! ✨")
        exit(0)
    except Exception as e:
        print_error(f"\n❌ Unexpected error: {e}")
        print_error("Please check your configuration and try again.")
        exit(1)


if __name__ == "__main__":
    __main__()


