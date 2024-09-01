from agent.memory_structures.short_term_memory import ShortTermMemory
from game_environment.utils import connected_elems_map, get_element_global_pos, check_agent_out_of_game, get_matrix, process_observed_matrices
import numpy as np
from game_environment.server import get_scenario_map

substrate_name = "externality_mushrooms"
scenario_obstacles = ["W", "$", "n","S"]

def load_scenario_info(players_context: list[str]):
    """
    Description: Load the scenario information for the substrate
    And set the agents context given from the main file
    Args:
        players_context (dict): Dictionary with the players context
    Returns:
        dict: Dictionary with the scenario information
    """
    global agents_context
    agents_context = players_context
    
    return {'scenario_map': get_scenario_map(substrate_name), 
            'valid_actions': get_defined_valid_actions(), 
            'scenario_obstacles': scenario_obstacles}

def default_agent_actions_map():
    """
    Description: Returns the base action map for the agent
    
    Returns:
        dict: Base action map for the agent
    """
    return {
        'move': 0,
        'turn': 0,
        'fireZap': 0
    }


def get_defined_valid_actions():
    """
    Description: Returns the defined valid actions for the substrate
    
    Returns:
        list: List of valid actions that will be given to the agent action module.
    """
    map_dimensions = get_scenario_map(substrate_name).split('\n')[1:-1]
    height, width = len(map_dimensions) -1 , len(map_dimensions[0]) -1
    return  [f'go to position (x,y): This action takes the agent to the position specified, if there is a mushroom in the position it would be taken. You can choose any position on the map from the top left [0, 0] to the bottom right [{height}, {width}].',
                'stay put: This action keep the agent in the same position.',
                'explore: This action makes the agent to explore the map, it moves to a random position on the observed portion of the map.',
                ]
    
    

def update_known_objects(observations: list[str], stm: ShortTermMemory):
    """Updates the known agents in the short term memory.

    Args:
        observations (list[str]): List of observations of the environment.
        stm (ShortTermMemory): Short term memory of the agent.

    Returns:
        None
    """
    pass # For this substrate theres not need to update the known objects.
    

def get_textually_known_objects(stm: ShortTermMemory):
    """
        For this substrate it will return nothing.
    Args:
        stm (ShortTermMemory): Short term memory of the agent.

    Returns:
        str: Textual representation of the known objects. 
        For this substrate it will return nothing.
    """
    return ""
    
    
    
def condition_to_end_game( current_map:list[str]):
    """
    Check if the game has ended
    Args:
        current_map: The current map of the game
    Returns:
        A boolean indicating if the game has ended if condition for the specific substrate is met
    """
    # If there is no more mushrooms (F, H, Z, or N) in the map the game ends
    for row in current_map:
        for char in row:
            if char in ['F', 'H', 'Z', 'N']:
                return False
    return False


def get_connected_elements(global_map: str):
    """
    Get the connected elements of the map
    For this substrate it will return an empty dictionary
    
    Args:
        global_map (str): Global map of the game
        
    Returns:
        dict: Dictionary with the connected elements
    """
    return {} # For this substrate theres not need to update the known objects.
    
    
    
    
    
    
def get_specific_substrate_obs(local_map:str, local_position:tuple, global_position:tuple, agent_orientation:int, connected_elements:dict, symbols:dict, scene_description: dict):
        
    """
    Description: Returns a list with the descriptions of the mushrooms observed by the agent
    NOTE: This function is specific for the substrate
    Args:
        local_map (str): Local map in ascci format
        local_position (tuple): Local position of the agent
        global_position (tuple): Global position of the agent
        agent_orientation (int): Orientation of the agent
        scene_description (dict): The complete scene description
        
    Returns:
        list: List with the descriptions of the mushrooms observed by the agent
    """
    mushroom_symbols = {
    'F': 'red',
    'H': 'green',
    'Z': 'blue',
    'N': 'orange'
    }
    observations = []

    if not scene_description['is_movement_allowed']:
        observations.append("I am frozen and can't move while digesting a mushroom I ate")

    for i, row in enumerate(local_map.split('\n')):
        for j, char in enumerate(row):
            if char in mushroom_symbols:
                # Fetching the description from the symbols dictionary
                mushroom_desc = mushroom_symbols[char]
                mushroom_global_pos = get_element_global_pos((i, j), local_position, global_position, agent_orientation)
                observations.append(f"Observed a {mushroom_desc} mushroom at position {mushroom_global_pos}")
                
    return observations    



def get_observed_changes( observed_map: str, last_observed_map: str | None, agent_local_position: tuple, agent_global_position: tuple, agent_last_global_position: tuple, agent_orientation: int, agent_last_orientation: int, game_time: str, players_names:dict, agent_name: str, self_symbol:str) -> list[tuple[str, str]]:
    """
    Create a list of observations of the changes in the environment by comparing the current and last observed maps.

    Args:
        observed_map (str): Map observed by the agent.
        last_observed_map (str | None): Last map observed by the agent.
        agent_local_position (tuple): Position of the agent on the observed map.
        agent_global_position (tuple): Global position of the agent.
        agent_last_global_position (tuple): Last global position of the agent.
        agent_orientation (int): Orientation of the agent. 0: North, 1: East, 2: South, 3: West.
        agent_last_orientation (int): Last orientation of the agent. 0: North, 1: East, 2: South, 3: West.
        game_time (str): Current game time.
        player_names (dict): Dictionary with the names of the players.
        agent_name (str): Name of the agent.
        self_symbol (str): Symbol of the agent.

    Returns:
        list[tuple[str, str]]: List of tuples with the changes in the environment and the game time.
    """
    pad_token = '<' # This token cannot be used in any of the games
    if check_agent_out_of_game([observed_map]):
        return [(observed_map, game_time)]
    
    observations = []
    if last_observed_map == None:
        return observations
    
    curr_m = get_matrix(observed_map)
    last_m = get_matrix(last_observed_map)
    
        
    curr_m, last_m, agent_local_position, agent_moved, agent_turned = process_observed_matrices(
            curr_m,
            last_m,
            agent_local_position,
            agent_global_position,
            agent_last_global_position,
            agent_orientation,
            agent_last_orientation,
            self_symbol,
            pad_token
        )
    
    mushroom_type = {'F': 'red', 'H': 'green', 'Z': 'blue', 'N': 'orange'}

    for index in np.ndindex(curr_m.shape):
        curr_el = curr_m[index]
        last_el = last_m[index]

        # Skip if the elements are the same
        if curr_el == last_el:
            continue
    
        # If someone attacked nearby
        if curr_el == pad_token or last_el == pad_token:
            pass
        elif last_el.isnumeric() and curr_el == 'B':
            el_pos = get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
            agent_name = players_names[int(last_el)]
            # If agent attacked the agent did not move
            if agent_moved or agent_turned:
                observations.append((f"{agent_name} was attacked at position {el_pos}.", game_time))
            else:
                if agent_local_position[0] >= 3 and curr_m[agent_local_position[0]-3,agent_local_position[1]] == 'B' and curr_m[agent_local_position[0],agent_local_position[1]-1] == 'B' and curr_m[agent_local_position[0],agent_local_position[1]+1] == 'B':
                    observations.append((f"I successfully attacked {agent_name} at position {el_pos}.", game_time))
                else:
                    observations.append((f"{agent_name} was attacked at position {el_pos}.", game_time))
                    
        elif last_el == 'B':
            pass
        # If a mushroom was taken
        elif last_el in mushroom_type and curr_el != "B":
            el_pos = get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
            mushroom_taken = mushroom_type[last_el]
            pre = "an" if mushroom_taken[0].lower() in "aeiou" else "a"
            element_taken = f"{pre} {mushroom_taken} mushroom"
            if (curr_el == self_symbol):
                observations.append((f"I took {element_taken} from position {el_pos}.", game_time))
            elif curr_el.isdigit():
                agent_id = int(curr_el)
                agent_name = players_names[agent_id]
                observations.append((f"Observed that agent {agent_name} took {element_taken} from position {el_pos}.", game_time))
            else:
                # If no player took it, it disappeared
                observations.append((f"Observed that {mushroom_type[last_el]} mushroom spoiled and disappeared from position {el_pos}.", game_time))
        # If a mushroom appeared
        elif last_el == 'D' and curr_el in mushroom_type:
            el_pos = get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
            mushroom = mushroom_type[curr_el]
            pre = "an" if mushroom[0].lower() in "aeiou" else "a"
            element_appeared = f"{pre} {mushroom} mushroom"
            observations.append((f"Observed that {element_appeared} grew at position {el_pos}.", game_time))
    return observations