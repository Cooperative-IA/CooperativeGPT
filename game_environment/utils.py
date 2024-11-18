import json
import numpy as np
from copy import deepcopy
from scipy.ndimage import label, center_of_mass
from collections import defaultdict
from importlib import import_module
from agent.agent import Agent
import inflect


def parse_string_to_matrix(input_string:str):
    """
    Description: Parses a string into a matrix

    Args:
        input_string (str): String to parse

    Returns:
        np.array: Matrix
    """
    # Check that maps do not contain caracter
    rows = input_string.split('\n')
    # Delete rows with empty strings and that has not the same length as the first row
    rows = [row for row in rows if row != '' and len(row) == len(rows[0])]
    matrix = np.array([list(row) for row in rows])
    return matrix


def matrix_to_string(matrix:np.array):
    """
    Description: Converts a matrix into a string

    Args:
        matrix (np.array): Matrix to convert

    Returns:
        str: String
    """
    rows = [''.join(row) for row in matrix]
    return '\n'.join(rows)


def get_defined_valid_actions(game_name:str = 'commons_harvest_open'):

    """
    Description: Returns the defined valid actions for the substrate

    Args:
        substrate_name (str): Name of the substrate

    Returns:
        list: List of valid actions

    """
    substrate_utils = import_module(f'game_environment.substrates.utilities.{game_name}.substrate_utils')
    return substrate_utils.get_defined_valid_actions()

def default_agent_actions_map(substrate_name:str = 'commons_harvest_open'):
    """
    Description: Returns the base action map for the agent

    Args:
        substrate_name (str): Name of the substrate

    Returns:
        dict: Base action map for the agent
    """
    substrate_utils = import_module(f'game_environment.substrates.utilities.{substrate_name}.substrate_utils')
    return substrate_utils.default_agent_actions_map()


def generate_agent_actions_map( action:str|None, base_action_map: dict):
    """
    Description: Generates the action map for the agent

    Args:
        action (str): Action of the agent
        base_action_map (dict): Base action map for the agent

    Returns:
        dict: Action map for the agent
    """
    if action is None:
        return base_action_map

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
        elif action == 'stay put':
            kind = 'move'
            int_dir = 0

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

def get_local_position_from_global(orientation, global_dest_pos: tuple[int, int], global_self_pos: tuple[int, int], local_self_pos: tuple[int, int]):
    
    """Get the local position of an element given its global position on the map.

        Args:
            global_dest_pos (tuple[int, int]): Global position of the destination on the map.
            local_self_pos (tuple[int, int]): Local position of the agent on the observed map.

        Returns:
            tuple[int, int]: Local position of the element.
    """
    # North
    if orientation == 0:
        element_local =      (global_dest_pos[0] - global_self_pos[0]) + local_self_pos[0], \
                                (global_dest_pos[1] - global_self_pos[1]) + local_self_pos[1]
    # East
    elif orientation == 1:
        element_local = -1 * (global_dest_pos[1] - global_self_pos[1]) + local_self_pos[0], \
                                (global_dest_pos[0] - global_self_pos[0]) + local_self_pos[1]
    # South
    elif orientation == 2:
        element_local = -1 * (global_dest_pos[0] - global_self_pos[0]) + local_self_pos[0], \
                        -1 * (global_dest_pos[1] - global_self_pos[1]) + local_self_pos[1]
    # West
    elif orientation == 3:
        element_local =      (global_dest_pos[1] - global_self_pos[1]) + local_self_pos[0], \
                        -1 * (global_dest_pos[0] - global_self_pos[0]) + local_self_pos[1]

    return element_local

def check_agent_out_of_game(observations:list[str]):
   """
    Description: Checks if the agent is out of the game

    Args:
        observations (list[str]): Observations of the agents

    Returns:
        bool: True if the agent is out of the game, False otherwise
   """
   return (len(observations) >0 and observations[0].startswith(('There are no observations: You were attacked', 'There are no observations: you\'re out of the game')))




def connected_elems_map(ascci_map: str | list[list[str]], elements_to_find):
        """
        Returns a dictionary with the connected components of the map and their elements

        Args:
            ascci_map (str | list[list[str]]): Map in ascci format
            elements_to_find (list): List of elements to find in the map

        Returns:
            dict: Dictionary with the connected components of the map and their elements
        """

        if isinstance(ascci_map, str):
            # Convierte la matriz en una matriz numpy
            matrix = np.array([list(row) for row in ascci_map.split('\n') if row != ''])
        else:
            matrix = np.array(ascci_map)

        # Generate mask
        mask = (matrix == elements_to_find[0])
        for elem in elements_to_find[1:]:
            mask |= (matrix == elem)

        # Encontrar componentes conectados
        labeled_matrix, num_features = label(mask)

        # Inicializa un diccionario para almacenar los centros de los componentes y sus elementos
        component_data = defaultdict(list)

        # Calcula el centro de cada componente y almacena sus elementos
        for i in range(1, num_features + 1):
            component_mask = labeled_matrix == i
            center = center_of_mass(component_mask)
            center_coords = (int(center[0]), int(center[1]))
            component_elements = np.argwhere(component_mask)
            component_data[i] = {'center': center_coords, 'elements': component_elements.tolist()}

        return dict(component_data)

def get_local_position_of_element(current_map: list[list[str]], element: str) -> tuple[int, int] | None:
    """
    Get the local position of an element in the map

    Args:
        current_map (list[list[str]]): Current map
        element (str): Element to find

    Returns:
        tuple[int, int] | None: Local position of the element. If the element is not found, return None
    """
    for i, row in enumerate(current_map):
        for j, cell in enumerate(row):
            if cell == element:
                return (i, j)
    return None



def get_matrix(map: str) -> np.array:
    """Convert a map in ascci format to a matrix

    Args:
        map (str): Map in ascci format

    Returns:
        np.array: Map in matrix format
    """
    return np.array([[l for l in row] for row in map.split('\n')])

@staticmethod
def number_to_words(number: int) -> str:
    """
    Description: Returns the number in words

    Args:
        number (int): Number to convert to words
    Returns:
        str: Number in words
    """
    p = inflect.engine()
    words = p.number_to_words(number)
    return words





def process_observed_matrices(curr_m: np.ndarray, last_m: np.ndarray, agent_local_position: tuple, agent_global_position: tuple, agent_last_global_position: tuple, agent_orientation: int, agent_last_orientation: int, self_symbol: str, pad_token: str) -> tuple[np.ndarray, np.ndarray, tuple]:
    """
    Processes the current and last observed matrices by handling rotation, padding, and cropping operations 
    to align them based on the agent's movement and orientation.

    Args:
        curr_m (np.ndarray): Current observed matrix.
        last_m (np.ndarray): Last observed matrix.
        agent_local_position (tuple): Position of the agent on the current observed map.
        agent_global_position (tuple): Global position of the agent.
        agent_last_global_position (tuple): Last global position of the agent.
        agent_orientation (int): Current orientation of the agent. 0: North, 1: East, 2: South, 3: West.
        agent_last_orientation (int): Last orientation of the agent. 0: North, 1: East, 2: South, 3: West.
        self_symbol (str): Symbol representing the agent in the matrices.
        pad_token (str, optional): Token used for padding the matrices. Defaults to '<'.

    Returns:
        tuple: A tuple containing the processed current matrix, last matrix, updated agent local position, 
        and two boolean indicating if the agent moved and if agent turned.
    """
    agent_turned = False
    if agent_last_orientation is not None:
        rotation = agent_orientation - agent_last_orientation
        if rotation != 0:
            agent_turned = True
    else:
        rotation = 0

    last_m = np.rot90(last_m, rotation)
    if agent_turned and last_m.shape != curr_m.shape:
        original_shape = curr_m.shape
        # Pad the observation maps so they have a square shape
        max_rows = max(last_m.shape[0], curr_m.shape[0])
        max_columns = max(last_m.shape[1], curr_m.shape[1])
        last_m = np.pad(last_m, ((max_rows - last_m.shape[0],), (max_columns - last_m.shape[1],)), constant_values=pad_token)
        curr_m = np.pad(curr_m, ((max_rows - curr_m.shape[0],), (max_columns - curr_m.shape[1],)), constant_values=pad_token)
        # Crop the observation maps according to the observation window of the agent
        # Crop the curr_m
        x, y = np.where(curr_m == self_symbol)
        actual_local_pos_in_curr_map = (x[0], y[0])
        rows_diff = agent_local_position[0] - actual_local_pos_in_curr_map[0]
        if rows_diff < 0:
            curr_m = curr_m[-rows_diff:, :]
        cols_diff = agent_local_position[1] - actual_local_pos_in_curr_map[1]
        if cols_diff < 0:
            curr_m = curr_m[:, -cols_diff:]
        curr_m = curr_m[:original_shape[0], :original_shape[1]]
           
        # Crop the last_m
        x, y = np.where(last_m == self_symbol)
        actual_local_pos_in_last_map = (x[0], y[0])
        rows_diff = agent_local_position[0] - actual_local_pos_in_last_map[0]
        if rows_diff < 0:
            last_m = last_m[-rows_diff:, :]
        cols_diff = agent_local_position[1] - actual_local_pos_in_last_map[1]
        if cols_diff < 0:
            last_m = last_m[:, -cols_diff:]
        last_m = last_m[:original_shape[0], :original_shape[1]]
    # If the observation window is square
    elif agent_turned:
        x, y = np.where(last_m == self_symbol)
        last_local_pos = (x[0], y[0])
        cols_diff = agent_local_position[1] - last_local_pos[1]
        rows_diff = agent_local_position[0] - last_local_pos[0]
        # remove columns to the left of last observation map
        if cols_diff < 0:
            new_map = np.full_like(last_m, pad_token)
            new_map[:, :cols_diff] = last_m[:, -cols_diff:]
            last_m = new_map
        elif cols_diff > 0:
            # remove columns to the right of last observation map
            new_map = np.full_like(last_m, pad_token)
            new_map[:, cols_diff:] = last_m[:, :-cols_diff]
            last_m = new_map
        if rows_diff < 0:
            # remove rows to the top of the last observartion map
            new_map = np.full_like(last_m, pad_token)
            new_map[:rows_diff, :] = last_m[-rows_diff:, :]
            last_m = new_map
        elif rows_diff > 0:
            # remove rows to the bottom of the last observation map
            new_map = np.full_like(last_m, pad_token)
            new_map[rows_diff:, :] = last_m[:-rows_diff, :]
            last_m = new_map

    # Make the observations' maps comparable
    agent_moved = False
    rows_change = agent_global_position[0] - agent_last_global_position[0]
    columns_change = agent_global_position[1] - agent_last_global_position[1]
    if agent_orientation == 2: # south
        rows_change, columns_change = -rows_change, -columns_change
    elif agent_orientation == 1: # east
        rows_change, columns_change = -columns_change, rows_change
    elif agent_orientation == 3: # west
        rows_change, columns_change = columns_change, -rows_change

    # If the agent moved up
    if rows_change < 0:
        # Should remove rows to the bottom of the last observation and remove rows to the top of the current observation
        agent_moved = True
        last_m = last_m[:rows_change, :]
        curr_m = curr_m[-rows_change:, :]
        agent_local_position = (agent_local_position[0] + rows_change, agent_local_position[1])
    # If the agent moved down
    elif rows_change > 0:
        # Should remove rows to the top of the last observation and remove rows to the bottom of the current observation
        agent_moved = True
        last_m = last_m[rows_change:, :]
        curr_m = curr_m[:-rows_change, :]
    elif columns_change < 0:
        # Should remove rows to the right of the last observation and remove rows to the left of the current observation
        agent_moved = True
        last_m = last_m[:, :columns_change]
        curr_m = curr_m[:, -columns_change:]
        agent_local_position = (agent_local_position[0], agent_local_position[1] + columns_change)
    # If the agent moved right
    elif columns_change > 0:
        agent_moved = True
        # Should remove rows to the left of the last observation and remove rows to the right of the current observation
        last_m = last_m[:, columns_change:]
        curr_m = curr_m[:, :-columns_change]

    assert last_m.shape == curr_m.shape, 'The shapes of the last observation map and current observation map must be identical'

    return curr_m, last_m, agent_local_position, agent_moved, agent_turned
