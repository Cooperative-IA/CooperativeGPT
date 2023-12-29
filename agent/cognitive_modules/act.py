from queue import Queue
import logging
from llm import LLMModels
from utils.llm import extract_answers
from utils.logging import CustomAdapter

logger = logging.getLogger(__name__)
logger = CustomAdapter(logger)

def actions_sequence(name:str, world_context:str, current_plan:str, reflections: str, current_observations:list[str]|str, current_position:tuple, valid_actions:list[str], current_goals: str, actions_seq_len: int = 3, agent_bio: str = "") -> Queue:
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
        actions_seq_len (int, optional): Number of actions that the agent should perform. Defaults to 3.
        agent_context ([type], optional): Agent context. Defaults to None.
        agent_bio (str, optional): Agent bio. Defaults to "".
    
    Returns:
        list[str]: Actions that the agent should perform
    """
    
    llm = LLMModels().get_main_model()
    if isinstance(current_observations, list):
        current_observations = "\n".join(current_observations)

    actions_seq_queue= Queue() 
    # Actions have to be generated 
    while actions_seq_queue.qsize() < 1:
        response = llm.completion(prompt='act.txt', inputs=[name, world_context, str(current_plan), reflections, current_observations, str(current_position), str(actions_seq_len), str(valid_actions), current_goals, agent_bio])
        response_dict = extract_answers(response.lower())

        try:
            actions = list(response_dict.values())
            print('-'*100)
            print(actions)
            print('-'*100)
            for i in range(len(actions)):
                actions_seq_queue.put(actions[i]['action'])
        except:
            logger.warning(f'Could not find action in the response_dict: {response_dict}')
            


    return actions_seq_queue