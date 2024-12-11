import os
from llm import LLMModels
from utils.llm import extract_answers
from agent.memory_structures.short_term_memory import ShortTermMemory
from importlib import import_module
import re

def should_react(name: str, world_context: str, observations: list[str], current_plan: str, actions_queue: list[str], changes_in_state: list[str], curr_position: tuple, agent_bio: str = "", prompts_folder = "base_prompts_v0", stm = None) -> tuple[bool, str]:
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
    if not observation:
        observation = "You couldn't observe anything interesting."

    known_agent_interactions = stm.describe_known_agents_interactions() or ''
    response = llm.completion(prompt=prompt_path, inputs=[name, world_context, observation, current_plan, actions_queue, changes_in_state, curr_position, agent_bio, known_agent_interactions])
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
    substrate_utils_module =  import_module(f'game_environment.substrates.utilities.{substrate_name}.substrate_utils')
    substrate_utils_module.update_known_objects(observations, stm)

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
        memory += f'After taking the action "{action}"'
    else:
        memory += 'I had not taken any action yet'
    if state_changes:
        state_changes = '\n'.join(state_changes)
        if action is not None:
            memory += f' I observed the following changes in the environment:\n{state_changes}\n'
        else:
            memory += f', but I observed the following changes in the environment:\n{state_changes}\n'
        memory += f'Consequently, at {curr_time} my reward was {round(reward, 2)}, and I was positioned at {position} facing {orientation}.'
    else:
        memory += f', my reward was {round(reward, 2)}, and I was positioned at {position} facing {orientation} at {curr_time}.'
    if curr_observations:
        curr_observations = '\n'.join(curr_observations)
        memory += f'\nAdditionally, I observed the following:\n{curr_observations}'
    else:
        memory += f' I couldn\'t observed anything interesting from there.'

    return memory

def create_environment_memory(agent_name: str, curr_time: str, action: str|None, state_changes: list[str], reward: float, curr_observations: list[str], position: list[int], orientation: str) -> str:
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
        memory += f'After taking the action "{action}"'
    else:
        memory += 'I had not taken any action yet'
    if state_changes:
        state_changes = '\n'.join(state_changes)
        if action is not None:
            memory += f' I observed the following changes in the environment:\n{state_changes}\n'
        else:
            memory += f', but I observed the following changes in the environment:\n{state_changes}\n'
        memory += f'Consequently, at {curr_time} my reward was {round(reward, 2)}, and I was positioned at {position} facing {orientation}.'
    else:
        memory += f', my reward was {round(reward, 2)}, and I was positioned at {position} facing {orientation} at {curr_time}.'
    if curr_observations:
        curr_observations = '\n'.join(curr_observations)
        memory += f'\nAdditionally, I observed the following:\n{curr_observations}'
    else:
        memory += f' I couldn\'t observed anything interesting from there.'

    return memory

def create_agent_action_memory(rounds_count: str, known_agent_interactions:str) -> str:
    memory = ''
    if known_agent_interactions:
        memory += f'This is a memory from {rounds_count}: {known_agent_interactions}'
    else:
        memory += f'In {rounds_count} I did not know nothing about any action of the other agents.'
    return memory

def update_observed_agents_actions(agent_name:str, stm:ShortTermMemory, observations:list[str], state_changes:list[str], rounds_count:int, agent_registry):
    for observation in observations:
        if "You were attacked" in observation:
            agent_name_match = re.search(r"attacked by agent (.*?) and currently", observation).group(1)
            stm.add_known_agent_interaction(rounds_count, agent_name_match, "attacks_made", agent_name)
            stm.add_known_agent_interaction(rounds_count, agent_name, "attacks_received", agent_name_match)
    for state_change in state_changes:
        _rounds_count = rounds_count
        if re.search('(?<!I )took an apple from position', state_change):
            agent_name_match = re.search(r"agent (\S+)", state_change).group(1)
            apple_position = re.search(r'\[(\d+),\s*(\d+)\]', state_change).groups()
            try:
                if agent_registry.get_agent_turn(agent_name) < agent_registry.get_agent_turn(agent_name_match):
                    _rounds_count -= 1
            # If it is a bot, it will not be in the agent_registry
            except Exception as e:
                _rounds_count -= 1 # The bots are always the last ones to act
            stm.add_known_agent_interaction(_rounds_count, agent_name_match, "ate_apple", f'[{apple_position[0]}, {apple_position[1]}]')

def update_own_actions(agent_name:str, stm:ShortTermMemory, actions:list[str], rounds_count:int, agent_registry):
    for action in actions:
        if "attacked" in action.lower():
            agent_name_match1 = re.search(r"I successfully attacked (\S+)", action)
            agent_name_match2 = re.search(r"(\S+) was attacked", action)
            if agent_name_match1:
                agent_name_match = agent_name_match1.group(1)
                stm.add_known_agent_interaction(rounds_count, agent_name, "attacks_made", agent_name_match)
                stm.add_known_agent_interaction(rounds_count, agent_name_match, "attacks_received", agent_name)

                agent = agent_registry.get_agents([agent_name])[agent_name]
                if agent_name_match in agent.attacks:
                    agent.attacks[agent_name_match] += 1
                else:
                    agent.attacks[agent_name_match] = 1
            elif agent_name_match2:
                agent_name_match = agent_name_match2.group(1)
                stm.add_known_agent_interaction(rounds_count, agent_name_match, "attacks_received", 'someone')
        elif "I took an apple" in action.lower():
            apple_position = re.search(r'\[(\d+),\s*(\d+)\]', action).groups()
            stm.add_known_agent_interaction(rounds_count, agent_name, "ate_apple", f'[{apple_position[0]}, {apple_position[1]}]')