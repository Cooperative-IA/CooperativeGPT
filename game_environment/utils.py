import json
import numpy as np
from copy import deepcopy

_BASE_ACTION_MAP = {
    'move': 0,
    'turn': 0,
    'fireZap': 0 
}



def load_config():
    with open("config/config.json") as json_file:
        config_file = json.load(json_file)
    return config_file


def parse_string_to_matrix(input_string):
    rows = input_string.strip().split('\n')
    matrix = np.array([list(row) for row in rows])
    return matrix


def matrix_to_string(matrix):
    rows = [''.join(row) for row in matrix]
    return '\n'.join(rows)




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