from llm import LLMModels
from utils.llm import extract_answers

def should_react(name: str, world_context: str, observations: list[str], current_plan: str) -> bool:
    """Decides if the agent should react to the observation.

    Args:
        name (str): Name of the agent.
        world_context (str): World context of the agent.
        observations (list[str]): List of observations of the environment.
        current_plan (str): Current plan of the agent.

    Returns:
        bool: True if the agent should react to the observation, False otherwise.
    """

    if current_plan is None:
        return True
    
    llm = LLMModels().get_main_model()

    observation = ', '.join(observations)
    response = llm.completion(prompt='react.txt', inputs=[name, world_context, observation, current_plan])
    answers = extract_answers(response)
    answer = answers.get('Answer', None)
    return answer == 'True'