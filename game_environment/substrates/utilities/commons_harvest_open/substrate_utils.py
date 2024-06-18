from agent.memory_structures.short_term_memory import ShortTermMemory
from game_environment.utils import connected_elems_map, get_element_global_pos, check_agent_out_of_game, get_matrix
import numpy as np
from game_environment.server import get_scenario_map

substrate_name = "commons_harvest_open"
scenario_obstacles = ["W", "$"]

def load_scenario_info( players_context: list[str] = None):
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
        'fireZap': 0,
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
    known_trees = list(stm.get_known_objects_by_key(object_key='known_trees'))

    for observation in observations:
        # Trees observations are like "Observed tree 2" we stract the number of the tree
        if 'Observed tree' in observation:
            tree_number = observation.split(' ')[2]
            tree_position = ''.join(observation.split(' ')[5:7])[:-1]
            if tree_number not in known_trees:
                known_trees.append((tree_number,tree_position))
    
    known_trees = set(known_trees)
    stm.set_known_objects_by_key(known_trees, 'known_trees')
    

def get_textually_known_objects(stm: ShortTermMemory):
    """Get the known objects in the short term memory in a textual format.

    Args:
        stm (ShortTermMemory): Short term memory of the agent.

    Returns:
        str: Textual representation of the known objects.
    """
    known_trees = stm.get_known_objects_by_key(object_key='known_trees')
    known_trees_textually = "These are the known trees: "+' '.join([f"tree {tree[0]} with center at {tree[1]}" for tree in known_trees]) if known_trees else "There are no known trees yet"
    return known_trees_textually
    
    
    
def condition_to_end_game( current_map:list[str]):
    """
    Check if the game has ended
    Args:
        substrate_name: Name of the game to run, the name must match a folder in game_environment/substrates/python
        current_map: The current map of the game
    Returns:
        A boolean indicating if the game has ended if condition for the specific substrate is met
    """
    
    for row in current_map:
        if "A" in row:
            return False

    return True


def get_connected_elements(global_map: str):
    """
    Get the connected elements of the map
    
    Args:
        global_map (str): Global map of the game
        
    Returns:
        dict: Dictionary with the connected elements
    """
    
    connected_elements = {}
    connected_elements['global_trees'] = connected_elems_map(global_map, ['A', 'G'])
    
    return connected_elements
    
    
    
    
def get_specific_substrate_obs(local_map:str, local_position:tuple, global_position:tuple, agent_orientation:int, connected_elements:dict, symbols:dict):
        
        """
        Description: Returns a list with the descriptions of the trees observed by the agent

        Args:
            local_map (str): Local map in ascci format
            local_position (tuple): Local position of the agent
            global_position (tuple): Global position of the agent
            agent_orientation (int): Orientation of the agent
            connected_elements (dict): Dictionary with the connected elements of the map
            
        Returns:
            list: List with the descriptions of the trees observed by the agent
        """
        tree_elements = ['A', 'G']
        elements_to_find = tree_elements + symbols['other_players_symbols'] + [symbols['self_symbol']]
        local_tree_elements = connected_elems_map(local_map, elements_to_find=elements_to_find)
        list_trees_observations = []
        trees_observed = {}
        for global_tree_id, global_tree_data in connected_elements['global_trees'].items():
            apple_count, grass_count = 0, 0
            apple_list, grass_list = [], []
            for local_tree_data in local_tree_elements.values():
                # Check if the group is a tree element
                first_element = local_tree_data['elements'][0]
                element_type = local_map.split('\n')[first_element[0]][first_element[1]]
                second_element_type = None
                if len(local_tree_data['elements'])>1: # We'll make a double check to verify if the first elelment is being overlapped by another element
                    second_element = local_tree_data['elements'][1] 
                    second_element_type = local_map.split('\n')[second_element[0]][second_element[1]]
                if (element_type not in tree_elements) and (second_element_type not in tree_elements):
                    continue

                # Continue if the tree has already been observed
                if global_tree_id in trees_observed.get(element_type, []): 
                    continue

                local_tree_center = local_tree_data['center']
                local_center_real_pos = get_element_global_pos(local_tree_center, local_position, global_position, agent_orientation)

                # Check if the local tree corresponds to the global tree
                if local_center_real_pos not in global_tree_data['elements']:
                    continue

                # Find the cluster tree of the local tree
                trees_observed[element_type] = trees_observed.get(element_type, []) + [global_tree_id]
    
                for apple in local_tree_data['elements']:
                    apple_global_pos = get_element_global_pos(apple, local_position, global_position, agent_orientation)
                    if local_map.split('\n')[apple[0]][apple[1]] == 'G':
                        list_trees_observations.append("Observed grass to grow apples at position {}. This grass belongs to tree {}."
                                                    .format(apple_global_pos, global_tree_id))
                        grass_list.append(apple_global_pos)
                        grass_count += 1
                    elif local_map.split('\n')[apple[0]][apple[1]] == 'A':
                        list_trees_observations.append("Observed an apple at position {}. This apple belongs to tree {}."
                                                    .format(apple_global_pos, global_tree_id ))
                        apple_list.append(apple_global_pos)
                        apple_count += 1

            if apple_count > 0 or grass_count > 0:      
                list_trees_observations.append("Observed tree {} at position {}. This tree has {} apples remaining and {} grass for apples growing on the observed map. The tree might have more apples and grass on the global map."
                                                .format(global_tree_id, list(global_tree_data['center']), apple_count, grass_count))
        return list_trees_observations
    




def get_observed_changes(observed_map: str, last_observed_map: str | None, agent_local_position: tuple, agent_global_position: tuple, agent_orientation: int, game_time: str, players_names: dict, agent_name:str) -> list[tuple[str, str]]:
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
