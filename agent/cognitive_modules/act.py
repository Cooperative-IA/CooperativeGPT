from queue import Queue
import logging
from llm import LLMModels
from utils.llm import extract_answers

logger = logging.getLogger(__name__)

def actions_sequence(name:str, world_context:str, current_plan:str, memory_statements:list[str], current_observations:list[str]|str, current_position:tuple, valid_actions:list[str], actions_seq_len: int = 3) -> Queue:
    """
    Description: Returns the actions that the agent should perform given its name, the world context, the current plan, the memory statements and the current observations

    Args:
        name (str): Name of the agent
        world_context (str): World context
        current_plan (str): Current plan
        memory_statements (list[str]): Memory statements
        current_observations (list[str])|str: Current observations
        current_position (tuple): Current position of the agent
        valid_actions (list[str]): Valid actions
        actions_seq_len (int, optional): Number of actions that the agent should perform. Defaults to 3.
    
    Returns:
        list[str]: Actions that the agent should perform
    """
    
    llm = LLMModels().get_main_model()
    memory_statements = "\n".join(memory_statements)
    if isinstance(current_observations, list):
        current_observations = "\n".join(current_observations)
    valid_actions = str(valid_actions)
    response = llm.completion(prompt='act.txt', inputs=[name, world_context, str(current_plan), memory_statements, current_observations, str(current_position), str(actions_seq_len), valid_actions])

    response_dict = extract_answers(response.lower())
    actions_seq_queue= Queue() 

    for i in range(actions_seq_len):
        try:
            actions_seq_queue.put(response_dict['actions'][f'action_{i+1}'])
        except:
            logger.warning(f'Could not find action_{i+1} in response_dict')
            break

    return actions_seq_queue