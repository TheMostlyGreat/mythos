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
    
    #create the concept for the Story   
    def draft_concept(self, details):
        print("Drafting the concept\n")
        prompt = (
            "Draft a brief for a story with the following details:\n" +
            "\n".join(f"{key}: {value}" for key, value in details.items())
        )
        concept = self.write(prompt)

        print(f"Here's the concept:\n {concept}\n")

        # Extract the title from the concept
        title = self.write(f"What is the title of this story? {concept}")

        print(f"Title: {title}\n")

        #self.story.set_title(title)
        self.story.set_title(title)
        self.story.set_concept(concept)
    
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
