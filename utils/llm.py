import re
import json
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


class CustomEmbeddingFunction(EmbeddingFunction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = LLMModels().get_embedding_model()
    def __call__(self, texts: Documents) -> Embeddings:
        return self.model.get_embeddings(texts)