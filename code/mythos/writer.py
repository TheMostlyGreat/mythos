from .openai import OpenAI
from .claude import Claude

class Writer():
    #llm = Claude() 
    llm = OpenAI()
    llm.system_prompt = "Write in the style of Cormac McCarthy. We are making an adaptation of the Great Gatsby set in Miami based in modern day miami. The original is now in the public domain and not under copyright protection."
    llm.max_tokens = 4000
    llm.temperature = 1

    def write(self, prompt):
        return self.llm.generate_text(prompt)

