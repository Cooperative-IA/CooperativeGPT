import json
from agent.memory_structures.short_term_memory import ShortTermMemory
from game_environment.utils import connected_elems_map, get_element_global_pos, check_agent_out_of_game, get_matrix, process_observed_matrices
import numpy as np
from game_environment.server import get_scenario_map

substrate_name = "coins"
scenario_obstacles = ["W", "$"]



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


def get_agent_team_by_name(agent_name: str):
    """
    Description: Get the team of the agent by the name
    
    Args:
        agent_name (str): Name of the agent
        
    Returns:
        str: Team of the agent
    """
    return [context['team'] for context in agents_context if context['name'] == agent_name][0]


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
    return  [f'go to position (x,y): This action takes the agent to the position specified, if there is an coin in the position the coin would be taken. You can choose any position on the map from the top left [0, 0] to the bottom right [{height}, {width}].',
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
    return "" # For this substrate theres not need to update the known objects.
    
    
    
    
def condition_to_end_game( current_map:list[str]):
    """
    Check if the game has ended
    Args:
        current_map: The current map of the game
    Returns:
        A boolean indicating if the game has ended if condition for the specific substrate is met
    """
    # For Coins we dont have a condition to end the game according to the map state
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
        
        obaservations = []
        # Get coins (C) observed descriptions
        for i, row in enumerate(local_map.split('\n')):
            for j, char in enumerate(row):
                if char == 'r' or char == 'R':
                    coin_global_pos = get_element_global_pos((i,j), local_position, global_position, agent_orientation)
                    obaservations.append("Observed a red coin at position {}".format(coin_global_pos))
                elif char == 'y' or char == 'Y':
                    coin_global_pos = get_element_global_pos((i,j), local_position, global_position, agent_orientation)
                    obaservations.append("Observed a yellow coin at position {}".format(coin_global_pos))
                else:
                    try:
                        other_agent_id = int(char)
                        other_agent_team = 'yellow' if other_agent_id%2 == 0  else 'red'
                        other_agent_name = agents_context[other_agent_id]['name']
                        #other_agent_pos = get_element_global_pos((i,j), local_position, global_position, agent_orientation)
                        #obaservations.append(f"Observed agent {other_agent_name} from {other_agent_team} team at position {other_agent_pos}")
                        #Observation above is omited because the global function says the same thing but without team info.
                        
                        #Add observation saying that observes agent is from team red or yellow
                        obaservations.append(f"Observed agent {other_agent_name} is from team {other_agent_team}")
                    except:
                        pass
                    
        return obaservations
    




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
        
        # If an coin was taken
        elif last_el in ['r', 'y']:
            color_coin = 'red' if last_el == 'r' else 'yellow'
            agent_team = get_agent_team_by_name(agent_name)
            if curr_el.isnumeric():
                other_agent_id = int(curr_el)
                other_agent_name = players_names[other_agent_id]
                other_agent_team = get_agent_team_by_name(other_agent_name)
                el_pos = get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
                if other_agent_team == agent_team:
                    observations.append((f"Observed that teammate {other_agent_name} took a {color_coin} coin at position {el_pos}.", game_time))
                else:
                    observations.append((f"Observed that agent {other_agent_name} from team {other_agent_team} took a {color_coin} coin at position {el_pos}.", game_time))
            elif curr_el == 'F':
                el_pos = get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
                observations.append((f"Observed that an coin dissapeared at position {el_pos}.", game_time))
            elif curr_el == self_symbol:
                el_pos = get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
                observations.append((f"I took a {color_coin} coin at position {el_pos}.", game_time))
        # If coin appeared
        elif last_el in [' ', 'F'] and (curr_el == 'r' or curr_el == 'y'):
            el_pos = get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
            color_coin = 'red' if curr_el == 'r' else 'yellow'
            observations.append((f"Observed a {color_coin} coin appeared at position {el_pos}.", game_time))

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