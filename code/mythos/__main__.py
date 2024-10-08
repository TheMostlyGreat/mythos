import os
from mythos.story import Story
from mythos.story_manager import StoryManager

global story
global story_manager
story = Story()
story_manager = StoryManager(story)
max_iterations = 10
iteration_count = 0

def create_story():
    global story
    global story_manager
    DEBUG = False
    user_prompt = ""
    story = Story()
    story_manager = StoryManager(story)

    user_prompt = input(
        "Tell me about your story idea. Include any details you've thought of so \n"
        "far - characters, setting, plot, or themes. Any other stories or writers \n"
        "you're inspired by. Also consider sharing informaation about you and your \n"
        "your target audience. Share as much or as little as you like: \n"
        )
    #user_info = input("Tell me about yourself. The more the better. :)")
    #target_audience = input("Who is the target audience for this story? ")
    if DEBUG:
        user_prompt = (
            "sleepy mom is battle some god in order to get to sleep. it's a comedic "
            "adaptation to the odessy by sophie kinsella. I'm a 38 yeard old mother of 3.  "
            "Just wound down my startup and taking a sabbatical. Target audience is other "
            "middle aged women with kids."
        )

    story.user_prompt = user_prompt
    story_manager.generate_concept()
    story_manager.run_initial_pass()
    story_manager.draft_opening_scene()

    print(f"Checking user prompt:\n\n{story.user_prompt}")

    
def open_story():
    global story
    global story_manager
    # List existing stories
    stories_folder = story.BASE_PATH
    existing_stories = []

    for f in os.listdir(stories_folder):
        if os.path.isdir(os.path.join(stories_folder, f)):  # Changed to check for directory
            existing_stories.append(f)
    
    if not existing_stories:
        print("No existing stories found.")

    print("Existing stories:")
    for idx, story_file in enumerate(existing_stories, start=1):
        print(f"{idx}. {story_file}")

    story_choice = input("Enter the number of the story you want to work on: ")
    try:
        story_choice = int(story_choice)
        if 1 <= story_choice <= len(existing_stories):
            selected_story = existing_stories[story_choice - 1]
            print(f"You selected: {selected_story}")
            # Load the selected story 
            story.load(selected_story)        
        else:
            print("Invalid choice. Please restart and select a valid option.")
    except ValueError:
        print("Invalid input. Please enter a number.")

def main_menu():
    while True:
        # Prompt the user for what they want to work on
        user_choice = input("Do you want to:\n1. Create a new story\n2. Work on an existing story\n3. Quit\nEnter the number of your choice: ")

        if user_choice == '1':

            create_story()
            print(f"Checking user prompt:\n\n{story.user_prompt}")
            story_menu()
        elif user_choice == '2':
            open_story()

            story_menu()
        elif user_choice == '3':
            print("Quitting the app. Goodbye!")
            break
        else:
            print("Invalid choice. Please choose again.")


def story_menu():
    global story
    global story_manager
    while True:
        print(
            f"\nStory asset added. There are now currently {len(story.assets)} assets.\n"
            f"Current asset keys: {list(story.assets.keys())}\n"
              )
        # Prompt the user for what they want to work on
        existing_choice = input(
            "What do you want to work on?\n1. Check story status\n"
            "2. Iterate\n3. Exit story\nEnter the number of your choice: ")

        if existing_choice == '1':
            story.get_status()
        elif existing_choice == '2':
            # Add your iteration logic here
            story_manager.iterate()
        elif existing_choice == '3':
            print("Exiting story menu.")
            break
        else:
            print("Invalid choice. Please restart and select a valid option.\n")

def main():
    main_menu()

if __name__ == "__main__":
    main()