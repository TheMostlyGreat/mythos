from .writer import Writer

def generate_section():
    writer = Writer()

    prompt = "Please write this section based on the section outline below./n"
    with open('./prompts/section1.md', 'r') as file:
        prompt += file.read()
        print(prompt)
    generated_text = writer.write(prompt)
    
    with open('./prompts/section1-draft.md', 'w') as output_file:
        output_file.write(generated_text)
    
    return generated_text

