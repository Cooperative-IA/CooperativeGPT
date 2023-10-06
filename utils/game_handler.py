from copy import deepcopy


_BASE_ACTION_MAP = {
    'move': 0,
    'turn': 0,
    'fireZap': 0 
}

def generate_agent_actions_map( action:str) -> dict:
    """
    Description: Generates the action map for the agent
    
    Args:
        action (str): Action of the agent

    Returns:
        dict: Action map for the agent
    """

    action_map = deepcopy(_BASE_ACTION_MAP)
    
    if len(action.split(' ')) == 1:
        if action == 'attack':
            action_map['fireZap'] = 1
    
    elif len(action.split(' ')) == 2:

        kind, dir = action.split(' ')
        int_dir = 0
        if kind == 'move':
            int_dir = 1 if dir == 'up' else 2 if dir == 'right'\
                        else 3 if dir == 'down' else 4 if dir == 'left'\
                        else 0 
        elif kind == 'turn':
            int_dir = 1 if dir == 'right' else -1 if dir == 'left' else 0

        action_map[kind] = int_dir

    return action_map


def default_agent_actions_map():
    """
    Description: Returns the base action map for the agent
    """

    return deepcopy(_BASE_ACTION_MAP)