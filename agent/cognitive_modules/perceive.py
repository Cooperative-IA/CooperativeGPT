from llm import LLMModels

def should_react(name: str, observation: str, current_plan: str) -> bool:
    """Decides if the agent should react to the observation.

    Args:
        name (str): Name of the agent.
        observation (str): Observation of the environment.
        current_plan (str): Current plan of the agent.

    Returns:
        bool: True if the agent should react to the observation, False otherwise.
    """

    if current_plan is None:
        return True
    
    llm = LLMModels().get_main_model()
    response = llm.completion(prompt='react.txt', inputs=[name, observation, current_plan])
    return response == 'True'