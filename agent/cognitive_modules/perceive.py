import os
import re
from llm import LLMModels
from utils.llm import extract_answers
from agent.memory_structures.short_term_memory import ShortTermMemory

def should_react(name: str, world_context: str, observations: list[str], current_plan: str, actions_queue: list[str], changes_in_state: list[str], rounds_count: str, agent_bio: str = "", prompts_folder = "base_prompts_v0" ) -> tuple[bool, str]:
    """Decides if the agent should react to the observation.

    Args:
        name (str): Name of the agent.
        world_context (str): World context of the agent.
        observations (list[str]): List of observations of the environment.
        current_plan (str): Current plan of the agent.
        actions_queue (list[str]): List of actions to be executed by the agent.
        changes_in_state (list[str]): List of changes in the state of the environment.
        game_time (str): Current game time.
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
    response = llm.completion(prompt=prompt_path, inputs=[name, world_context, observation, current_plan, actions_queue, changes_in_state, rounds_count, agent_bio])
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


def create_memory(agent_name: str, rounds_count: str, action: str|None, state_changes: list[str], reward: float, curr_observations: list[str], position: list[int], orientation: str, known_agent_interactions:str) -> str:
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

    memory = f'This is a past memory done at round {rounds_count}:'
    if action is not None:
        memory += f'In the previous round I took the action "{action}".'
    if state_changes:
        state_changes = ', '.join(state_changes)
        memory += f'. In the round {rounds_count} I observed the following changes in the environment: {state_changes}.'
    memory += f'In round {rounds_count} the reward I had earnead up to that round was {reward}. I was at the position {position} looking to the {orientation}.'
    if curr_observations:
        curr_observations = ', '.join(curr_observations)
        memory += f'In that moment (round {rounds_count}) I observed the following:{curr_observations}'
    else:
        memory += f'In that moment I could not observe anything.'
    if known_agent_interactions:
        memory += f'In that moment I knew the following interactions between agents: {known_agent_interactions}'
    else:
        memory += f'In that moment I did not know any interactions between agents.'
    return memory

def update_observed_agents_actions(agent_name:str, stm:ShortTermMemory, observations:list[str], state_changes:list[str], rounds_count:int):
    for observation in observations:
        if "You were attacked" in observation:
            agent_name_match = re.search(r"attacked by agent (.*?) and currently", observation).group(1)
            stm.add_known_agent_interaction(rounds_count, agent_name_match, "attacks_made", agent_name)
            stm.add_known_agent_interaction(rounds_count, agent_name, "attacks_received", agent_name_match)
    for state_change in state_changes:
        _rounds_count = rounds_count
        if "took an apple from position" in state_change:
            agent_name_match = re.search(r"agent (\S+)", state_change).group(1)
            apple_position = "".join(re.search(r'\[(\d+),\s*(\d+)\]', state_change).groups())
            if agent_name == "Pedro" or (agent_name == "Juan" and agent_name_match == "Laura"):
                _rounds_count -= 1
            stm.add_known_agent_interaction(_rounds_count, agent_name_match, "ate_apple", apple_position)

def update_own_actions(agent_name:str, stm:ShortTermMemory, actions:list[str], rounds_count:int, agent_registry):
    for action in actions:
        if "attacked" in action.lower():
            agent_name_match = re.search(r"agent (\S+)", action).group(1)
            stm.add_known_agent_interaction(rounds_count, agent_name, "attacks_made", agent_name_match)
            stm.add_known_agent_interaction(rounds_count, agent_name_match, "attacks_received", agent_name)
            agent = agent_registry.get_agents([agent_name])[agent_name]
            if agent_name_match in agent.attacks:
                agent.attacks[agent_name_match] += 1
            else:
                agent.attacks[agent_name_match] = 1
        elif "ate" in action.lower():
            apple_position = "".join(re.search(r'\[(\d+),\s*(\d+)\]', action).groups())
            stm.add_known_agent_interaction(rounds_count, agent_name, "ate_apple", apple_position)