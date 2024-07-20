class LLM:
    system_prompt = "Write in the style of Cormac McCarthy"
    max_tokens = 500
    temperature = 1

    def generate_text(self, prompt):
        raise NotImplementedError("Subclasses should implement this method")