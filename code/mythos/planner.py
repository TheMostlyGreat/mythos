from mythos.openai import OpenAI
from mythos.claude import Claude
from mythos.story import Story
import os

class Planner():

    def __init__(self, new_story):
        print("Waking up the planner\n")
        self.story = new_story
        #self.llm = Claude() 
        self.llm = OpenAI()
        self.llm.system_prompt =(
            "You are a renowned Harvard literature professor, NYT bestselling book editor, "
            "and world-class storyteller. Your expertise lies in crafting brief, clear, and "
            "specific narratives that captivate readers. Help me outline an entertaining and "
            "engaging story."
        )
        self.llm.max_tokens = 4000
        self.llm.temperature = 1

        print("Planner is ready\n")

    def write(self, prompt):
        return self.llm.generate_text(prompt)
    
    def read_files(self, file_paths):
        contents = []
        print(f"Reading files: {file_paths}\n")
        for path in file_paths:
            with open(path, 'r') as file:
                contents.append(file.read())
        return contents
    
    #create the concept for the Story   
    def develop_concept(self, details):
        print("Drafting the concept\n")
        prompt = (
            "Draft a brief for a story with the following details:\n" +
            "\n".join(f"{key}: {value}" for key, value in details.items()) +
            "\n" +
            "Use this framework and template:\n" +
            open('prompts/frameworks/concept_framework.md').read()
        )
        concept = self.write(prompt) + (
            "\n # User Input: \n" +
            "\n".join(f"{key}: {value}" for key, value in details.items()) + "\n"
        )
        
        print(f"Here's the concept:\n {concept}\n")

        # Extract the title from the concept
        title = concept.split('Title: ')[1].split('\n')[0]

        #self.story.set_title(title)
        self.story.set_title(title)
        self.story.set_concept(concept)

        print("Concept save to " + self.story.path + "/concept.md")

    def conduct_research(self):
        research_notes = ""
        # Gather historical, cultural info, summarize critical theories
        print("Conducting research...")
        
        with open(self.story.concept, 'r') as file:
            content = file.read()  
        
        prompt = (
            "Conduct research on the following concept:\n" +
            content +
            "\n" +
            "Use this framework and template:\n" +
            open('prompts/frameworks/research_framework.md').read()
        )
        research_notes = self.write(prompt)
        print(f"Here's the research:\n {research_notes}\n")
        with open(self.story.path + "/concept.md", 'a') as file:
            file.write("\n\n")
            file.write(research_notes)
        print("Research appended to " + self.story.path + "/concept.md")
    
    def collect_inspiration(self):
        inspiration = ""

        print(f"Collecting inspiration and influences\n")

        with open(self.story.concept, 'r') as file:
            content = file.read() 

        prompt = (
            "Collect inspiration and influences for the following concept:\n" +
            content +
            "Use this framework and template:\n" +
            open('prompts/frameworks/inspirations_framework.md').read()
        )
        inspiration = self.write(prompt)
        with open(self.story.path + "/concept.md", 'a') as file:
            file.write("\n\n")
            file.write(inspiration)
        print("Inspirations appended to " + self.story.path + "/concept.md")

    def define_main_characters(self):
        print(f"Defining main characters\n")

        with open(self.story.concept, 'r') as file:
            content = file.read() 

        prompt = (
            "Define the main characters for the following concept:\n" +
            content +
            "\n" +
            "Use this framework and template:\n" +
            open('prompts/frameworks/main_characters_framework.md').read()
        )
        characters = self.write(prompt)
        print(f"Here's the characters:\n {characters}\n")
        with open(self.story.path + "/concept.md", 'a') as file:
            file.write("\n\n")
            file.write(characters)
        print("Main characters appended to " + self.story.path + "/concept.md")
        #self.story.set_main_characters(characters)
        #print("Main characters saved to " + self.story.path + "/main_characters.md")

    def define_setting(self):
        print(f"Defining the setting\n")

        with open(self.story.concept, 'r') as file:
            content = file.read() 

        prompt = (
            "Define the setting for the following concept:\n" +
            content +
            "\n" +
            "Use this framework and template:\n" +
            open('prompts/frameworks/setting_framework.md').read()
        )
        setting = self.write(prompt)
        print(f"Here's the setting:\n {setting}\n")
        with open(self.story.path + "/concept.md", 'a') as file:
            file.write("\n\n")
            file.write(characters)
        print("Main characters appended to " + self.story.path + "/concept.md")

    def draft_themes(self):
        print(f"Drafting themes and motifs\n")

        prompt = (
            "Draft themes and motif for the following concept:\n" +
            self.story.concept
        )
        themes = self.write(prompt)

        print(f"Here's the themes and motifs:\n {themes}\n")

        self.story.set_themes(themes)
    
    def draft_setting(self):
        print(f"Drafting the setting\n")

        prompt = (
            "Draft the setting for the following concept:\n" +
            self.story.concept
        )

        print(f"Prompt: {prompt}\n")
        setting = self.write(prompt)

        print(f"Here's the setting:\n {self.story.themes}\n")

        self.story.set_setting(setting)

    def draft_characters(self):
        print(f"Drafting the characters\n")

        prompt = (
            "Draft the characters for the following concept:\n" +
            self.story.concept
        )

        characters = self.write(prompt)

        print(f"Here are the characters:\n {characters}\n")

        self.story.set_characters(characters)

    def draft_writing_style(self):
        print(f"Drafting the writing style\n")

        prompt = (
            "Draft the writing style for the following concept:\n" +
            self.story.concept
        )

        writing_style = self.write(prompt)

        print(f"Here's the writing style:\n {writing_style}\n")

        self.story.set_writing_style(writing_style)

    def draft_plot(self):
        print(f"Drafting the plot\n")

        prompt = (
            "Draft the plot for the following concept:\n" +
            self.story.concept
        )

        plot = self.write(prompt)

        print(f"Here's the plot:\n {plot}\n")

        self.story.set_plot(plot)

    def draft_narrative_outline(self):
        print(f"Drafting the narrative\n")

        prompt = (
            "Draft the narrative for the following concept:\n" +
            self.story.concept
        )
        narrative = self.write(prompt)

        print(f"Here's the narrative:\n {narrative}\n")

        self.story.set_narrative_outline(narrative)


# Initialize all elements
    def __init__(self, new_story):
        print("Waking up the planner\n")
        self.story = new_story
        #self.llm = Claude() 
        self.llm = OpenAI()
        self.llm.system_prompt =(
            "You are a renowned Harvard literature professor, NYT bestselling book editor, "
            "and world-class storyteller. Your expertise lies in crafting brief, clear, and "
            "specific narratives that captivate readers. Help me outline an entertaining and "
            "engaging story."
        )
        self.llm.max_tokens = 4000
        self.llm.temperature = 1

        print("Planner is ready\n")




""" # Main iterative process
Function PrepareNovel():
    While iteration_count < max_iterations:
        # Step 1: High-Level Planning
        DevelopConceptAndThemes()
        ConductResearch()

        # Step 2: Structural Planning
        CreatePlotOutlineAndTimeline()

        # Step 3: Character and Setting Development
        DevelopCharactersAndSettings()

        # Step 4: Theme and Motif Integration
        IntegrateThemesAndSymbols()

        # Step 5: Detailed Plot Development
        DevelopChaptersAndScenes()

        # Step 6: Dialogue and Language
        WriteDialogueAndDefineNarrativeVoice()

        # Step 7: Execution and Flexibility
        DraftOpeningAndEstablishSchedule()

        # Step 8: Revision and Feedback
        IntegrateFeedbackAndRevise()

        # Step 9: Backup and Organization
        BackupWork()

        # Increment iteration count and check readiness
        iteration_count += 1
        if CheckReadiness():
            Break
    EndWhile

# Define individual steps with progress tracking and dependencies
Function DevelopConceptAndThemes():
    Define core idea and central themes
    Mark progress as complete if well-developed

Function ConductResearch():
    Gather historical, cultural info, summarize critical theories
    Mark progress as complete if sufficient

Function CreatePlotOutlineAndTimeline():
    Develop plot outline and intertextual references
    Create chronological timeline of events
    Mark progress as complete if detailed

Function DevelopCharactersAndSettings():
    Create detailed character profiles and arcs
    Write setting descriptions ensuring cultural, historical accuracy
    Mark progress as complete if robust

Function IntegrateThemesAndSymbols():
    List primary, secondary themes and recurring symbols
    Mark progress as complete if integrated

Function DevelopChaptersAndScenes():
    Create chapter summaries and detailed scene list
    Mark progress as complete if aligned

Function WriteDialogueAndDefineNarrativeVoice():
    Write key dialogues, define narrative voice and techniques
    Plan tone and mood for story parts
    Mark progress as complete if defined

Function DraftOpeningAndEstablishSchedule():
    Draft prologue or first chapter, set writing routine and goals
    Mark progress as complete if established

Function IntegrateFeedbackAndRevise():
    Share manuscript with beta readers, revise based on feedback
    Mark progress as complete if integrated

Function BackupWork():
    Schedule regular backups using cloud storage or external drives
    Mark progress as complete if backed up

# Function to perform a readiness check
Function CheckReadiness():
    Define readiness criteria for each element
    Return True if all elements meet criteria, otherwise return False

# Execute the main function
PrepareNovel() """