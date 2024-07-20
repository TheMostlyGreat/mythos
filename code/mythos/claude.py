from mythos.llm import LLM  # Absolute import
import anthropic
import os

class Claude(LLM):
    client = anthropic.Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
    def generate_text(self, prompt):
        print(self.system_prompt)
        print(self.max_tokens)
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=self.system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        return(message.content)