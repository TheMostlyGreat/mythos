import os
from mythos.planner import Planner
from mythos.story import Story

story = Story()
planner = Planner(story)
max_iterations = 10
iteration_count = 0

def create_story():
    # Prompt the user for the story concept
        user_concept = input("What story do you want to tell? ")

        # Prompt the user for the setting
        user_setting = input("Where do you want it set? ")

        # Prompt the user for character details
        user_story = input("Please give me any details on characters you know you want in the story. ")

        # Prompt the user for themes
        user_themes = input("Any themes you'd like to explore? ")

        # Prompt the user for the story length
        user_length = input("How long do you want this story to be? ")

        # Prompt the user for their favorite authors or books
        user_influences = input("Who are some of your favorite authors or books and why? ")

        # You can now use user_concept, user_setting, user_influences, user_themes, user_story, and user_length as needed
        print(f"Story Concept: {user_concept}")
        print(f"Setting: {user_setting}")
        print(f"Character Details: {user_story}")
        print(f"Themes: {user_themes}")
        print(f"Story Length: {user_length}")
        print(f"Influences: {user_influences}")

        
        # Create a dictionary with the details
        story_details = {
            "concept": user_concept,
            "setting": user_setting,
            "characters": user_story,
            "themes": user_themes,
            "length": user_length,
            "influences": user_influences
        }
        print("Creating story concept")

        # Pass the dictionary to draft_concept
        planner.draft_concept(story_details)

        print("Story concept created")

def open_story():
    # List existing stories
    stories_folder = './Stories'
    existing_stories = [f for f in os.listdir(stories_folder) if os.path.isfile(os.path.join(stories_folder, f))]
    
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
            # Load the selected story (implementation depends on how stories are stored)
            # For example:
            # with open(os.path.join(stories_folder, selected_story), 'r') as file:
            #     story_content = file.read()
            #     story.load(story_content)
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
            story_menu()

def story_menu():
    while True:
        # Prompt the user for what they want to work on
        existing_choice = input(
            "What do you want to work on?\n1. Run the themes and motifs\n"
            "2. Run the setting\n3. Run the characters\n4. Run the writing style\n"
            "5. Run the narrative outline\n6. Exit story\nEnter the number of your choice: ")

        if existing_choice == '1':
            planner.draft_themes()
        elif existing_choice == '2':
            planner.draft_setting()
        elif existing_choice == '3':
            planner.draft_characters()
        elif existing_choice == '4':
            planner.draft_writing_style()
        elif existing_choice == '5':
            planner.draft_narrative_outline()
        elif existing_choice == '6':
            print("Exiting story menu.")
            break
        else:
            print("Invalid choice. Please restart and select a valid option.\n")


def alt_main():
    DEBUG = True
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

    print("Starting story high-level planning. \n")
    planner.create_high_level_plan(details)
    print("Story high-level planning completed. \n")

    print("Starting story structure planning. \n")
    planner.plan_structure()
    print("Story structure planning completed. \n")

    print("Starting character development. \n")
    planner.develop_characters()
    print("Character development completed. \n")

def main():
    #main_menu()
    alt_main()

if __name__ == "__main__":
    main()


        