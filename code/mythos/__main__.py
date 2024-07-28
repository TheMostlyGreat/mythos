import os
from mythos.planner import Planner
from mythos.story import Story

story = Story()
planner = Planner(story)
max_iterations = 10
iteration_count = 0

def create_story():
    DEBUG = False
    concept = ""
    user_info = ""
    target_audience = ""

    concept = input(
        "Tell me about your story idea. Include any details you've thought of so \n"
        "far - characters, setting, plot, or themes. Any other stories or writers \n"
        "you're inspired by. Also consider sharing informaation about you and your \n"
        "your target audience. Share as much or as little as you like: \n"
        )
    #user_info = input("Tell me about yourself. The more the better. :)")
    #target_audience = input("Who is the target audience for this story? ")
    if DEBUG:
        concept = (
            "sleepy mom is battle some god in order to get to sleep. it's a comedic "
            "adaptation to the odessy by sophie kinsella. I'm a 38 yeard old mother of 3.  "
            "Just wound down my startup and taking a sabbatical. Target audience is other "
            "middle aged women with kids."
        )

    details = {
        "concept": concept,
        "user_info": user_info,
        "target_audience": target_audience
    }

    #Create high-level plan
    print("Starting story high-level planning. \n")
    planner.create_high_level_plan(details)
    print("Story high-level planning completed. \n")

    #Plan story structure
    print("Starting story structure planning. \n")
    planner.plan_structure()
    print("Story structure planning completed. \n")
    
    """   
    #Develop characters
    print("Starting character development. \n")
    planner.develop_characters()
    print("Character development completed. \n")

    #Develop setting
    print("Starting setting development. \n")
    planner.develop_setting()
    print("Setting development completed. \n") 
    
    #Develop themes and motifs
    print("Starting theme development. \n")
    planner.develop_themes_and_motifs()
    print("Theme development completed. \n")
    """
    # print("Starting timeline development. \n")
    # planner.develop_timeline()
    # print("Timeline development completed. \n")

    #Develop chapters and scenes
    print("Starting chapter development. \n")
    planner.develop_narrative_outline()
    print("Chapter development completed. \n")

    #Develop writing style
    print("Starting writing style development. \n")
    planner.develop_writing_style()
    print("Writing style development completed. \n")

    print("Starting draft of opening scene. \n")
    planner.draft_opening_scene()
    print("Opening scene draft completed. \n")
    
def open_story():
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
        user_choice = input("Do you want to:\n1. Create a new story\n2. Work on an existing story\nEnter the number of your choice: ")

        if user_choice == '1':

            create_story()
            
            story_menu()
        elif user_choice == '2':
            open_story()

            story_menu()


def story_menu():
    while True:
        # Prompt the user for what they want to work on
        existing_choice = input(
            "What do you want to work on?\n1. Check story status\n"
            "2. Develop characters\n3. Develop setting\n4. Develop writing style\n"
            "5. Develop narrative\n6. Exit story\nEnter the number of your choice: ")

        if existing_choice == '1':
            story.get_status()
        elif existing_choice == '2':
            planner.develop_characters()
        elif existing_choice == '3':
            planner.develop_setting()
        elif existing_choice == '4':
            pass
            #planner.develop_writing_style()
        elif existing_choice == '5':
            pass
            #planner.develop_narrative()
        elif existing_choice == '6':
            print("Exiting story menu.")
            break
        else:
            print("Invalid choice. Please restart and select a valid option.\n")

def main():
    main_menu()

if __name__ == "__main__":
    main()


        