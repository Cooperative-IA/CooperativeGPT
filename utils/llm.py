import re
import json

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
        answers = re.findall(patt, response)[0].strip()
        parsed_answers = json.loads(answers)
    except:
        parsed_answers = {}
    return parsed_answers