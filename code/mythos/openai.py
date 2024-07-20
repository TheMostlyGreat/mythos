from mythos.llm import LLM
from openai import OpenAI
import os

class OpenAI(LLM):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    # This method generates text based on the provided prompt using the OpenAI model
    def generate_text(self, prompt):
        

        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        response = completion.choices[0].message

        return(response.content)
