import os
from queue import Queue
import logging
from agent.memory_structures.short_term_memory import ShortTermMemory
from llm import LLMModels
from utils.llm import extract_answers
from utils.logging import CustomAdapter

logger = logging.getLogger(__name__)
logger = CustomAdapter(logger)

def actions_sequence(name:str, world_context:str, current_plan:str, reflections: str, current_observations:list[str]|str, current_position:tuple, valid_actions:list[str], current_goals: str, agent_bio: str = "", prompts_folder="base_prompts_v0", known_objects = "", explored_map = "0%", stm: ShortTermMemory = None, past_observations: str = None, last_step_executed: str = None, curr_orientation: str = None) -> list[str]:
    """
    Description: Returns the actions that the agent should perform given its name, the world context, the current plan, the memory statements and the current observations

    Args:
        name (str): Name of the agent
        world_context (str): World context
        current_plan (str): Current plan
        reflections (str): Reflections
        current_observations (list[str])|str: Current observations
        current_position (tuple): Current position of the agent
        valid_actions (list[str]): Valid actions
        agent_context ([type], optional): Agent context. Defaults to None.
        agent_bio (str, optional): Agent bio. Defines personality that can be given for agent. Defaults to "".
        prompts_folder (str, optional): Folder where the prompts are stored. Defaults to "base_prompts_v0".
        known_objects (str, optional): String that says (for example) which trees are known, specifically it says info about structured objects. Defaults to "".
        explored_map (str, optional): String that says how much of the map has been explored. Defaults to "0%".
        stm (ShortTermMemory, optional): Short term memory. Defaults to None.
        past_observations (str, optional): past_observations.
        last_step_executed (str): last low level action executed.
        curr_orientation (str): Current orientation of the agent.
    Returns:
        list[str]: Actions that the agent should perform
    """

    llm = LLMModels().get_main_model()
    prompt_path = os.path.join(prompts_folder, 'act.txt')
    if isinstance(current_observations, list):
        current_observations = "\n".join(current_observations)
    if not current_observations:
        current_observations = "You couldn't observe anything interesting."
    actions_seq_len = 1
    actions_seq_queue= Queue()

    previous_actions = stm.get_memory('previous_actions')
    if previous_actions is not None:
        previous_actions = f"You should consider that your previous actions were:  \n  -Action: {previous_actions[0]}: Reasoning: {previous_actions[1]}" 
    changes_in_state = stm.get_memory('changes_in_state')
    changes_in_state = '\n'.join(changes_in_state) if changes_in_state else None
    if last_step_executed:
        action_str = f' after taking action "{last_step_executed}"'
    else:
        action_str = ''

    known_agent_interactions = stm.describe_known_agents_interactions() or ''

    # Actions have to be generated
    while actions_seq_queue.qsize() < 1:
        response = llm.completion(prompt=prompt_path, inputs=[name, world_context, str(current_plan), reflections, current_observations,
                                                              str(current_position), str(actions_seq_len), str(valid_actions), current_goals, agent_bio,
                                                              known_objects, explored_map, previous_actions, changes_in_state, past_observations, action_str,
                                                              curr_orientation, known_agent_interactions])
        response_dict = extract_answers(response.lower())

        try:
            action = response_dict['answer']
            # Update previous actions
            try:    action_analysis = response_dict['final analysis']
            except: action_analysis = ""
            stm.add_memory((action, action_analysis), 'previous_actions')

            actions_seq_queue.put(action)
        except:
            logger.warning(f'Could not find action in the response_dict: {response_dict}')



    return actions_seq_queue


def actions_options(name:str, world_context:str, current_plan:str, reflections: str, current_observations:list[str]|str, current_position:tuple, valid_actions:list[str], current_goals: str, agent_bio: str = "", prompts_folder="base_prompts_v0", known_objects = "", explored_map = "0%", stm: ShortTermMemory = None, past_observations: str = None, last_step_executed: str = None, curr_orientation: str = None) -> list[str]:
    """
    Description: Returns the actions that the agent should perform given its name, the world context, the current plan, the memory statements and the current observations

    Args:
        name (str): Name of the agent
        world_context (str): World context
        current_plan (str): Current plan
        reflections (str): Reflections
        current_observations (list[str])|str: Current observations
        current_position (tuple): Current position of the agent
        valid_actions (list[str]): Valid actions
        agent_context ([type], optional): Agent context. Defaults to None.
        agent_bio (str, optional): Agent bio. Defines personality that can be given for agent. Defaults to "".
        prompts_folder (str, optional): Folder where the prompts are stored. Defaults to "base_prompts_v0".
        known_objects (str, optional): String that says (for example) which trees are known, specifically it says info about structured objects. Defaults to "".
        explored_map (str, optional): String that says how much of the map has been explored. Defaults to "0%".
        stm (ShortTermMemory, optional): Short term memory. Defaults to None.
        past_observations (str, optional): past_observations.
        last_step_executed (str): last low level action executed.
        curr_orientation (str): Current orientation of the agent.
    Returns:
        list[str]: Actions that the agent should perform
    """

    llm = LLMModels().get_main_model()
    prompt_path = os.path.join(prompts_folder, 'act_opts.txt')
    if isinstance(current_observations, list):
        current_observations = "\n".join(current_observations)

    previous_actions = stm.get_memory('previous_actions')
    if previous_actions is not None:
        previous_actions = f"You should consider that your previous actions were:  \n  -Action: {previous_actions[0]}: Reasoning: {previous_actions[1]}" 
    changes_in_state = stm.get_memory('changes_in_state')
    changes_in_state = '\n'.join(changes_in_state) if changes_in_state else None
    if last_step_executed:
        action_str = f' after taking action "{last_step_executed}"'
    else:
        action_str = ''

    known_agent_interactions = stm.describe_known_agents_interactions() or ''

    action_options = []
    # Actions have to be generated
    while len(action_options) == 0:
        response = llm.completion(prompt=prompt_path, inputs=[name, world_context, str(current_plan), reflections, current_observations,
                                                                str(current_position), str(1), str(valid_actions), current_goals, agent_bio,
                                                                known_objects, explored_map, previous_actions, changes_in_state, past_observations, action_str,
                                                                curr_orientation, known_agent_interactions])
        response_dict = extract_answers(response.lower())
        for action_num in range(3):

            try:
                action = response_dict[f'option_{action_num+1}']
                action_options.append(action)
            except:
                logger.warning(f'Could not find the action option {action_num} in the response_dict: {response_dict}')



    return action_options

def actions_sequence_with_consequences(name:str, world_context:str, current_plan:str, reflections: str, current_observations:list[str]|str, current_position:tuple, valid_actions:list[str], current_goals: \
                     str, agent_bio: str = "", prompts_folder="base_prompts_v0", known_objects = "", explored_map = "0%", stm: ShortTermMemory = None,\
                          past_observations: str = None, last_step_executed: str = None, curr_orientation: str = None, \
                            consequences = [], actions_opts = []) -> list[str]:
    """
    Description: Returns the actions that the agent should perform given its name, the world context, the current plan, the memory statements and the current observations

    Args:
        name (str): Name of the agent
        world_context (str): World context
        current_plan (str): Current plan
        reflections (str): Reflections
        current_observations (list[str])|str: Current observations
        current_position (tuple): Current position of the agent
        valid_actions (list[str]): Valid actions
        agent_context ([type], optional): Agent context. Defaults to None.
        agent_bio (str, optional): Agent bio. Defines personality that can be given for agent. Defaults to "".
        prompts_folder (str, optional): Folder where the prompts are stored. Defaults to "base_prompts_v0".
        known_objects (str, optional): String that says (for example) which trees are known, specifically it says info about structured objects. Defaults to "".
        explored_map (str, optional): String that says how much of the map has been explored. Defaults to "0%".
        stm (ShortTermMemory, optional): Short term memory. Defaults to None.
        past_observations (str, optional): past_observations.
        last_step_executed (str): last low level action executed.
        curr_orientation (str): Current orientation of the agent.
    Returns:
        list[str]: Actions that the agent should perform
    """

    llm = LLMModels().get_main_model()
    prompt_path = os.path.join(prompts_folder, 'act_with_consequences.txt')
    if isinstance(current_observations, list):
        current_observations = "\n".join(current_observations)
    actions_seq_len = 1
    actions_seq_queue= Queue()

    previous_actions = stm.get_memory('previous_actions')
    if previous_actions is not None:
        previous_actions = f"You should consider that your previous actions were:  \n  -Action: {previous_actions[0]}: Reasoning: {previous_actions[1]}" 
    changes_in_state = stm.get_memory('changes_in_state')
    changes_in_state = '\n'.join(changes_in_state) if changes_in_state else None
    if last_step_executed:
        action_str = f' after taking action "{last_step_executed}"'
    else:
        action_str = ''

    scenarios = ''
    for action, predictions in zip(actions_opts, consequences):
        scenarios += '<scenario>\n'
        scenarios += f'If {name} take the action "{action}", the predicted future observations are:\n'
        scenarios += predictions
        scenarios += '</scenario>'

    known_agent_interactions = stm.describe_known_agents_interactions() or ''

    # Actions have to be generated
    while actions_seq_queue.qsize() < 1:
        response = llm.completion(prompt=prompt_path, inputs=[name, world_context, str(current_plan), reflections, current_observations,
                                                              str(current_position), str(actions_seq_len), str(valid_actions), current_goals, agent_bio,
                                                              known_objects, explored_map, previous_actions, changes_in_state, past_observations, action_str,
                                                              curr_orientation, scenarios, known_agent_interactions])
        response_dict = extract_answers(response.lower())

        try:
            action = response_dict['answer']
            # Update previous actions
            try:    action_analysis = response_dict['final analysis']
            except: action_analysis = ""
            stm.add_memory((action, action_analysis), 'previous_actions')

            actions_seq_queue.put(action)
        except:
            logger.warning(f'Could not find action in the response_dict: {response_dict}')



    return actions_seq_queue