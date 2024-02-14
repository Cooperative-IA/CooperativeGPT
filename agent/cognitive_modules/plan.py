from llm import LLMModels
from utils.llm import extract_answers
import os

def plan(name: str, world_context: str, observation: str, current_plan: str, reflections: str, reason_to_react: str, agent_bio: str = "", prompts_folder = "base_prompts_v0" ) -> tuple[str, str]:
    """Creates a plan for the agent and its goals.

    Args:
        name (str): Name of the agent.
        world_context (str): World context of the agent.
        observation (str): Observation of the environment.
        current_plan (str): Current plan of the agent.
        reflections (str): Reflections of the agent.
        reason_to_react (str): Reason to react and create a new plan.
        agent_bio (str, optional): Agent bio. Defines personality that can be given for agent. Defaults to "".
        prompts_folder (str, optional): Folder where the prompts are stored. Defaults to "base_prompts_v0".

    Returns:
        tuple[str, str]: New plan and new goals for the agent.
    """
    llm = LLMModels().get_main_model()

    prompt_path = os.path.join(prompts_folder, 'plan.txt')
    response = llm.completion(prompt=prompt_path, inputs=[name, world_context, observation, current_plan, reflections, reason_to_react, agent_bio], system_prompt='plan_system_prompt.txt')
    answers = extract_answers(response)

    plan = answers.get('Plan', None)
    goals = answers.get('Goals', None)

    return plan, goals