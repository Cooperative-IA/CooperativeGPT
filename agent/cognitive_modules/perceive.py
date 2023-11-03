from llm import LLMModels
from utils.llm import extract_answers
from agent.memory_structures.short_term_memory import ShortTermMemory

def should_react(name: str, world_context: str, observations: list[str], current_plan: str, actions_queue: list[str]) -> tuple[bool, str]:
    """Decides if the agent should react to the observation.

    Args:
        name (str): Name of the agent.
        world_context (str): World context of the agent.
        observations (list[str]): List of observations of the environment.
        current_plan (str): Current plan of the agent.
        actions_queue (list[str]): List of actions to be executed by the agent.

    Returns:
        tuple[bool, str]: Tuple with True if the agent should react to the observation, False otherwise, and the reasoning.
    """

    if current_plan is None:
        return True, 'There is no plan to follow.'
    
    llm = LLMModels().get_main_model()

    observation = '.\n'.join(observations)
    actions_queue = ', '.join([f'{i+1}.{action}' for i, action in enumerate(actions_queue)]) if len(actions_queue) > 0 else 'None'
    response = llm.completion(prompt='react.txt', inputs=[name, world_context, observation, current_plan, actions_queue])
    answers = extract_answers(response)
    answer = answers.get('Answer', False)
    reasoning = answers.get('Reasoning', '')
    return answer, reasoning

def update_known_agents(observations: list[str], stm: ShortTermMemory):
    """Updates the known agents in the short term memory.

    Args:
        observations (list[str]): List of observations of the environment.
        stm (ShortTermMemory): Short term memory of the agent.

    Returns:
        None
    """
    known_agents = list(stm.get_known_agents())

    for observation in observations:
        if 'agent' in observation:
            agent_name = observation.split(' ')[2] # agent name is the third word of the observation
            if agent_name not in known_agents:
                known_agents.append(agent_name)
    
    known_agents = set(known_agents)
    stm.set_known_agents(known_agents)