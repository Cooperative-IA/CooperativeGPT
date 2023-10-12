from llm import LLMModels
from utils.llm import extract_answers

def plan(name: str, world_context: str, observation: str, current_plan: str, reflections: str) -> tuple[str, str]:
    """Creates a plan for the agent and its goals.

    Args:
        name (str): Name of the agent.
        world_context (str): World context of the agent.
        observation (str): Observation of the environment.
        current_plan (str): Current plan of the agent.
        reflections (str): Reflections of the agent.

    Returns:
        tuple[str, str]: New plan and new goals for the agent.
    """
    llm = LLMModels().get_main_model()
    response = llm.completion(prompt='plan.txt', inputs=[name, world_context, observation, current_plan, reflections])
    answers = extract_answers(response)

    plan = answers.get('Plan', None)
    goals = answers.get('Goals', None)

    return plan, goals