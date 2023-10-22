from llm import LLMModels
from utils.llm import extract_answers

def should_react(name: str, world_context: str, observations: list[str], current_plan: str, actions_queue: list[str]) -> bool:
    """Decides if the agent should react to the observation.

    Args:
        name (str): Name of the agent.
        world_context (str): World context of the agent.
        observations (list[str]): List of observations of the environment.
        current_plan (str): Current plan of the agent.
        actions_queue (list[str]): List of actions to be executed by the agent.

    Returns:
        bool: True if the agent should react to the observation, False otherwise.
    """

    if current_plan is None:
        return True
    
    llm = LLMModels().get_main_model()

    observation = '.\n'.join(observations)
    actions_queue = ', '.join([f'{i+1}.{action}' for i, action in enumerate(actions_queue)]) if len(actions_queue) > 0 else 'None'
    response = llm.completion(prompt='react.txt', inputs=[name, world_context, observation, current_plan, actions_queue])
    answers = extract_answers(response)
    answer = answers.get('Answer', False)
    return answer