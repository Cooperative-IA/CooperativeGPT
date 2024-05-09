import re
import json
import os
from chromadb import Documents, EmbeddingFunction, Embeddings

from llm import LLMModels

def extract_answers(response: str) -> dict[str, str]:
    """Extracts the answers from the response. The answers are extracted by parsing the json part of the response.
    
    Args:
        response (str): Response from the LLM. The response should have a json code snippet with the answers. For example: ```json{"plan": "go to the kitchen", "goals": "go to the kitchen"}```

    Returns:
        dict[str, str]: Dictionary with the answers.
    """
    patt = re.compile(r'\s*```json\s*([\w\W\n\r\t]*?)\s*```\s*', re.MULTILINE)
    try:
        response = response.replace('\n', ' ') # Remove new lines to avoid errors on multiline double quotes
        answers = re.findall(patt, response)[0].strip() # Get the first json part of the response
        answers =  re.sub(r'(:\s*"[^"]+")\s*("[^"]+"\s*:)', r'\1, \2', answers) # Add missing commas between items
        answers = re.sub(r'"\s*,\s*}', '"}', answers) # Remove commas before the closing bracket
        parsed_answers = json.loads(answers)
    except:
        parsed_answers = {}
    return parsed_answers

def extract_text(response: str) -> str:
    """Extracts the answers from the response. The answers are extracted by parsing the ```text ``` part of the response.
    
    Args:
        response (str): Response from the LLM. The response should have a plain text snippet with the answers. For example: ```text\nHello, this is a text answer.\n```

    Returns:
        dict[str, str]: Dictionary with the answers.
    """
    patt = re.compile(r'\s*```text\s*([\w\W\n\r\t]*?)\s*```\s*', re.MULTILINE)
    try:
        response = re.findall(patt, response)[0].strip()
    except:
        response = ''
    return response

def extract_tags(response: str) -> dict:
    """Extract tags from the response. A tag is represented as <tag>content<\tag>, where in this case a dict would be return with the key anything and the value content.
    
    Args:
        response (str): Response from the LLM. The response should have tags like XML tags.

    Returns:
        dict: Dictionary with the tags as keys and the content as values.
    """
    patt = r'<(\w+)>(.*)?</\1>'
    return {k: v.strip() for k, v in re.findall(patt, response, re.DOTALL)}

class CustomEmbeddingFunction(EmbeddingFunction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = LLMModels().get_embedding_model()
    def __call__(self, texts: Documents) -> Embeddings:
        return self.model.get_embeddings(texts)
    
def load_prompt(prompt: str) -> str:
    """Load the prompt from a file or return the prompt if it is a string
    Args:
        prompt_file (str): Prompt file or string
    Returns:
        str: Prompt
    """
    prompt_file = os.path.join("prompts", prompt)

    # Check if the prompt is a string or a file
    if not os.path.isfile(prompt_file):
        if prompt_file.endswith(".txt"):
            raise ValueError("Prompt file not found", message="Prompt file: {prompt_file} not found, using the prompt as a string")
        return prompt
    
    with open(prompt_file, "r") as f:
        prompt = f.read()
    return prompt

def replace_inputs_in_prompt(prompt: str, inputs: list[str] = []) -> str:
    """Replace the inputs in the prompt. The inputs are replaced in the order they are passed in the list.
    Args:
        prompt (str): Prompt. For example: "This is a <input1> prompt with <input2> two inputs"
        inputs (list[str]): List of inputs
    Returns:
        str: Prompt with the inputs
    """
    for i, input in enumerate(inputs):
        if input is None:
            input = 'None'
        # Delete the line if the input is empty
        if str(input).strip() == "":
            regex = rf"^\s*{re.escape(f'<input{i+1}>')}[ \t\r\f\v]*\n"
            prompt = re.sub(regex, "", prompt, flags=re.MULTILINE)

        prompt = prompt.replace(f"<input{i+1}>", str(input))

    # Check if there are any <input> left
    if "<input" in prompt:
        raise ValueError("Not enough inputs passed to the prompt")
    return prompt