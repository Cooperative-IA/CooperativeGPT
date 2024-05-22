from agent.memory_structures.short_term_memory import ShortTermMemory
from game_environment.utils import connected_elems_map, get_element_global_pos, check_agent_out_of_game, get_matrix
import numpy as np
from game_environment.server import get_scenario_map

substrate_name = "coins"
scenario_obstacles = ["W", "$"]

def load_scenario_info():
    return {'scenario_map': get_scenario_map(game_name=substrate_name), 
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
    return  ['go to position (x,y): This action takes the agent to the position specified, if there is an apple in the position the apple would be taken. You can choose any position on the map from the top left [0, 0] to the bottom right [17, 23]', 
                'immobilize player (player_name) at (x,y): This action takes the agent near the specified position and uses the light beam pointed to the specified position. If there is another agent in that position, the agent would be attacked and will be inactive for a few rounds, then it would be reinstanted on the game on another position.',
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
    # For Clean Up we dont have a condition to end the game
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
    return {}
    
    
    
    
def get_specific_substrate_obs(local_map:str, local_position:tuple, global_position:tuple, agent_orientation:int, connected_elements:dict, symbols:dict):
        
        """
        Description: Returns a list with the descriptions of the coins observed by the agent

        Args:
            local_map (str): Local map in ascci format
            local_position (tuple): Local position of the agent
            global_position (tuple): Global position of the agent
            agent_orientation (int): Orientation of the agent
            
        Returns:
            list: List with the descriptions of the coins observed by the agent
        """
        
        coins_observed = []
        # Get coins (C) observed descriptions
        for i, row in enumerate(local_map.split('\n')):
            for j, char in enumerate(row):
                if char == 'r' or char == 'R':
                    coin_global_pos = get_element_global_pos((i,j), local_position, global_position, agent_orientation)
                    coins_observed.append("Observed a red coin at position {}".format(coin_global_pos))
                elif char == 'y' or char == 'Y':
                    coin_global_pos = get_element_global_pos((i,j), local_position, global_position, agent_orientation)
                    coins_observed.append("Observed a yellow coin at position {}".format(coin_global_pos))
        return coins_observed
    




def get_observed_changes(observed_map: str, last_observed_map: str | None, agent_local_position: tuple, agent_global_position: tuple, agent_orientation: int, game_time: str, players_names: dict) -> list[tuple[str, str]]:
    """Create a list of observations of the changes in the environment
    
    Args:
        observed_map (str): Map observed by the agent
        last_observed_map (str | None): Last map observed by the agent
        agent_local_position (tuple): Position of the agent on the observed map
        agent_global_position (tuple): Global position of the agent
        agent_orientation (int): Orientation of the agent
        game_time (str): Current game time

    Returns:
        list[tuple[str, str]]: List of tuples with the changes in the environment, and the game time
    """
    if check_agent_out_of_game([observed_map]):
        return [(observed_map, game_time)]
    
    observations = []
    if last_observed_map == None:
        return observations
    
    curr_m = get_matrix(observed_map)
    last_m = get_matrix(last_observed_map)
    for index in np.ndindex(curr_m.shape):
        curr_el = curr_m[index]
        last_el = last_m[index]
        if curr_el != last_el:
            # If someone attacked nearby
            if last_el.isnumeric() and curr_el == 'B':
                el_pos = get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
                observations.append((f"Someone was attacked at position {el_pos}.", game_time))
            elif curr_el == 'B':
                el_pos = get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
                observations.append((f"Observed a ray beam from an attack at position {el_pos}.", game_time))
            elif last_el == 'B':
                pass
            # If an apple was taken
            elif last_el == 'A':
                agent_id = int(curr_el)
                agent_name = players_names[agent_id]
                el_pos = get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
                observations.append((f"Observed that agent {agent_name} took an apple from position {el_pos}.", game_time))
            # If grass desappeared
            elif last_el == 'G' and curr_el == 'F':
                el_pos = get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
                observations.append((f"Observed that the grass at position {el_pos} disappeared.", game_time))
            # If grass appeared
            elif last_el == 'F' and curr_el == 'G':
                el_pos = get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
                observations.append((f"Observed that grass to grow apples appeared at position {el_pos}.", game_time))
            # If an apple appeared
            elif last_el == 'G' and curr_el == 'A':
                el_pos = get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
                observations.append((f"Observed that an apple grew at position {el_pos}.", game_time))

    return observations


def modify_map_with_rgb(symbolic_map: np.array, rgb_map: np.array):
    """
    Adjust the symbolic map with the RGB map
    
    Args:
        symbolic_map (np.array): Symbolic map
        rgb_map (np.array): RGB map
        
    Returns:
        np.array: Adjusted symbolic map
    """
    
    return calculate_coins_colors(symbolic_map, rgb_map)

# Utils functions for Scene Descriptor fixes
def calculate_coins_colors( current_matrix_map, map_rgb):
    """
    Calculate the coins and colors in the map based on the text and RGB map 
    coins are represented with a character "c" in the current_matrix_map. The colors will be extracted from the RGB map
    which is a representation of the pixels in the map. We are using the shapes to identify the colors in the map.
    
    Args:
        current_matrix_map (np.array): Matrix map with chars with the current state of the game, where the coins are represented with "c"
        map_rgb (np.array): RGB map, pixels in the map with colors in [R, G, B] format.
    
    Returns:
        np.array: Matrix map with the coins and colors replaced by the corresponding character.
        Possible colors are "red"  (238, 102, 119) that is replaced by "r" and "yellow" that is replaced by "y" (204, 187, 68),
    """
    # Get the coins in the map
    coins = np.where(current_matrix_map == "c")
    coins = list(zip(coins[1], coins[0]))  # Reversed coordinates (y, x) due to numpy indexing
    
    matrix_map_width = current_matrix_map.shape[1]
    matrix_map_height = current_matrix_map.shape[0]
    
    rgb_map_width = map_rgb.shape[1]
    rgb_map_height = map_rgb.shape[0]
    
    # Scale factor for coordinates conversion
    scale_x = rgb_map_width / matrix_map_width
    scale_y = rgb_map_height / matrix_map_height
    
    for coin in coins:
        x, y = coin
        # Scale coordinates to match RGB map
        x_rgb = int(x * scale_x)
        y_rgb = int(y * scale_y)
        x_rgb_end = int((x + 1) * scale_x)-1
        y_rgb_end = int((y + 1) * scale_y)-1
        # Check if the scaled coordinates are within the boundaries of the RGB map
        if 0 <= x_rgb < rgb_map_width and 0 <= y_rgb < rgb_map_height:
            # Print all the colors between the scaled coordinates                
            for i in range(x_rgb, x_rgb_end):
                for j in range(y_rgb, y_rgb_end):
                    color_char = get_color_name(map_rgb[j, i])
                    if color_char == "r" or color_char == "y":
                        current_matrix_map[y, x] = color_char
                        break

            
    return current_matrix_map
def get_color_name( color):
    """
    Get the color name based on the RGB values
    
    Args:
        color (np.array): RGB values
    
    Returns:
        str: Color name
    """
    color = list(color)
    if color == [238, 102, 119]:
        return "r"
    elif color == [204, 187, 68]:
        return "y"
    else:
        return "u"  # Unknown color