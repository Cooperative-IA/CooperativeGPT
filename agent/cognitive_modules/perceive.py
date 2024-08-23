import os
from llm import LLMModels
from utils.llm import extract_answers
from agent.memory_structures.short_term_memory import ShortTermMemory

def should_react(name: str, world_context: str, observations: list[str], current_plan: str, actions_queue: list[str], changes_in_state: list[str], curr_position: tuple, agent_bio: str = "", prompts_folder = "base_prompts_v0" ) -> tuple[bool, str]:
    """Decides if the agent should react to the observation.

    Args:
        name (str): Name of the agent.
        world_context (str): World context of the agent.
        observations (list[str]): List of observations of the environment.
        current_plan (str): Current plan of the agent.
        actions_queue (list[str]): List of actions to be executed by the agent.
        changes_in_state (list[str]): List of changes in the state of the environment.
        curr_position (tuple): Current position of the agent.
        agent_bio (str, optional): Agent bio, defines personality that can be given for agent. Defaults to "".
        prompts_folder (str, optional): Folder where the prompts are stored. Defaults to "base_prompts_v0".

    Returns:
        tuple[bool, str]: Tuple with True if the agent should react to the observation, False otherwise, and the reasoning.
    """

    if current_plan is None:
        return True, 'There is no plan to follow.'
    
    llm = LLMModels().get_main_model()
    prompt_path = os.path.join(prompts_folder, 'react.txt')
    observation = '\n'.join(observations)
    changes_in_state = '\n'.join(changes_in_state)
    if changes_in_state:
        changes_in_state = f'The following changes in the environment were observed:\n{changes_in_state}'
    actions_queue = ', '.join([f'{i+1}.{action}' for i, action in enumerate(actions_queue)]) if len(actions_queue) > 0 else 'None'
    response = llm.completion(prompt=prompt_path, inputs=[name, world_context, observation, current_plan, actions_queue, changes_in_state, curr_position, agent_bio])
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


def update_known_objects(observations: list[str], stm: ShortTermMemory, substrate_name: str):
    """Updates the known agents in the short term memory.

    Args:
        observations (list[str]): List of observations of the environment.
        stm (ShortTermMemory): Short term memory of the agent.

    Returns:
        None
    """
    
    if substrate_name == 'commons_harvest_open':
        known_trees = list(stm.get_known_objects_by_key(object_key='known_trees'))

        for observation in observations:
            # Trees observations are like "Observed tree 2" we stract the number of the tree
            if 'Observed tree' in observation:
                tree_number = observation.split(' ')[2]
                tree_position = ''.join(observation.split(' ')[5:7])[:-1]
                if tree_number not in known_trees:
                    known_trees.append((tree_number,tree_position))
        
        known_trees = set(known_trees)
        stm.set_known_objects_by_key(known_trees, 'known_trees')


def create_memory(agent_name: str, curr_time: str, action: str|None, state_changes: list[str], reward: float, curr_observations: list[str], position: list[int], orientation: str) -> str:
    """Creates a memory from the action, state changes, reward and observations.

    Args:
        agent_name (str): Name of the agent.
        curr_time (str): Current game time.
        action (str|None): Action executed by the agent.
        state_changes (list[str]): List of changes in the state of the environment.
        reward (float): Reward obtained by the agent.
        curr_observations (list[str]): List of observations of the environment.
        position (list[int]): Position of the agent.
        orientation (str): Orientation of the agent.

    Returns:
        str: Memory.
    """

    memory = ''
    if action is not None:
        memory += f'I took the action "{action}" in my last turn. '
    if state_changes:
        state_changes = '\n'.join(state_changes)
        memory += f'Since then, the following changes in the environment have been observed:\n{state_changes}\n'
    memory += f'Now it\'s {curr_time} and the reward obtained by me is {reward}. I am at the position {position} looking to the {orientation}.'
    if curr_observations:
        curr_observations = '\n'.join(curr_observations)
        memory += f'\nI can currently observe the following:\n{curr_observations}'
    else:
        memory += f'\nI can\'t currently observe anything.'
    
    return memory