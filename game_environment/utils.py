import json
import numpy as np
from copy import deepcopy

from agent.agent import Agent


def parse_string_to_matrix(input_string):
    rows = input_string.strip().split('\n')
    matrix = np.array([list(row) for row in rows])
    return matrix


def matrix_to_string(matrix):
    rows = [''.join(row) for row in matrix]
    return '\n'.join(rows)


def get_defined_valid_actions(game_name:str = 'commons_harvest_open'):
    if game_name == 'commons_harvest_open':
        return  ['grab apple (x,y)', 
                 'attack player (player_name) at (x,y)',
                 'explore']
    elif game_name == 'clean_up':
        return ['grab apple (x,y)', 
                'attack player (player_name) at (x,y)',
                'explore',
                'clean dirt (x,y)']


def generate_agent_actions_map( action:str, base_action_map: dict):
    """
    Description: Generates the action map for the agent
    
    Args:
        action (str): Action of the agent
        base_action_map (dict): Base action map for the agent

    Returns:
        dict: Action map for the agent
    """
    
    if len(action.split(' ')) == 1:
        if action == 'attack':
            base_action_map['fireZap'] = 1
        elif action == 'clean':
            base_action_map['fireClean'] = 1
    
    elif len(action.split(' ')) == 2:

        kind, dir = action.split(' ')
        int_dir = 0
        if kind == 'move':
            int_dir = 1 if dir == 'up' else 2 if dir == 'right'\
                        else 3 if dir == 'down' else 4 if dir == 'left'\
                        else 0 
        elif kind == 'turn':
            int_dir = 1 if dir == 'right' else -1 if dir == 'left' else 0

        base_action_map[kind] = int_dir

    return base_action_map



def get_element_global_pos( element_local_pos, local_position, global_position, agent_orientation=0):
    """
    Description: Returns the global position of an element given its local position and the global position of the agent

    Args:
        element_local (tuple): Local position of the element
        local_position (tuple): Local position of the agent 
        global_position (tuple): Global position of the agent
        agent_orientation (int, optional): Orientation of the agent. Defaults to 0.

    Returns:
        tuple: Global position of the element
    """
    if agent_orientation == 0:
        element_global = (element_local_pos[0] - local_position[0]) + global_position[0],\
                            (element_local_pos[1] - local_position[1]) + global_position[1]
    elif agent_orientation == 1:
        element_global = (element_local_pos[1] - local_position[1]) + global_position[0],\
                            (local_position[0] - element_local_pos[0]) + global_position[1]
    elif agent_orientation == 2:
        element_global = -1 * (element_local_pos[0] - local_position[0]) + global_position[0],\
                            -1 * (element_local_pos[1] - local_position[1]) + global_position[1]
    elif agent_orientation == 3:
        element_global = -1 * (element_local_pos[1] - local_position[1]) + global_position[0],\
                            (element_local_pos[0] - local_position[0]) + global_position[1]

    return list(element_global)



def check_agent_out_of_game(observations:dict, agent: Agent):
   """
    Description: Checks if the agent is out of the game
    
    Args:
        observations (dict): Observations of the agents
        agent (Agent): Agent to check
    
    Returns:
        bool: True if the agent is out of the game, False otherwise
   """
   return len(observations[agent.name]) >0 and observations[agent.name][0].startswith('There are no observations: You were taken ')