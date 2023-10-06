from queue import Queue
from llm import LLMModels
from utils.llm import extract_answers


def actions_sequence(name:str, world_context:str, current_plan:str, memory_statements:list[str], current_observations:list[str], valid_actions:list[str], actions_seq_len: int = 3) -> Queue:
    """
    Description: Returns the actions that the agent should perform given its name, the world context, the current plan, the memory statements and the current observations

    Args:
        name (str): Name of the agent
        world_context (str): World context
        current_plan (str): Current plan
        memory_statements (list[str]): Memory statements
        current_observations (list[str]): Current observations
    
    Returns:
        list[str]: Actions that the agent should perform
    """
    
    llm = LLMModels().get_main_model()
    memory_statements = "\n".join(memory_statements)
    current_observations = "\n".join(current_observations)
    valid_actions = str(valid_actions)
    response = llm.completion(prompt='act.txt', inputs=[name, world_context, current_plan, memory_statements, current_observations, valid_actions, str(actions_seq_len)])
    response_dict = extract_answers(response)
    actions_seq_queue= Queue() 

    for i in range(actions_seq_len):
        actions_seq_queue.put(response_dict['actions'][f'action_{i+1}']) 
    return actions_seq_queue