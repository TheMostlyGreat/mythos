def excerpt_finder(text):
   #this function will take a theme or a motif and Find excerpts from the novel 
   # that clearly illustrate each theme and motif. Then Note the context in
   # which these passages appear and their significance
   
    excerpt_prompt = f"""
    Here is a theme/motif. Please find excerpts from the novel that clearly illustrate it. 
    Note the context in which these passages appear and their significance. Theme/Motif: {text}
    """
    
    #send the prompt to the LLM and get the response
    response = llm_call(excerpt_prompt)
    return response


def process_markdown(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    current_item = ""
    for line in lines:
        if line.strip().isdigit() and line.strip().endswith('.'):
            current_item = line.strip()
        elif line.strip().startswith('-'):
            sub_bullet = line.strip().lstrip('-').strip()
            merged_string = f"{current_item} {sub_bullet}"
            excerpt_finder(merged_string)

# Example usage
process_markdown('path/to/your/markdown/file.md')