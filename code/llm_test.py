from mythos.claude import Claude
from mythos.openai import OpenAI

def test_llm_classes():
    # Create instances of the LLM subclasses
    claude_instance = Claude()
    openai_instance = OpenAI()

    # Define a test prompt
    test_prompt = "What is the meaning of life?"

    # Generate text using Claude
    print("Claude's response:")
    claude_instance.generate_text(test_prompt)

    # Generate text using OpenAI
    print("OpenAI's response:")
    openai_instance.generate_text(test_prompt)


if __name__ == "__main__":
    test_llm_classes()
