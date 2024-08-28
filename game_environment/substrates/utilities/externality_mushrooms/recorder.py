import os
import json

from game_environment.utils import connected_elems_map, get_local_position_of_element
from utils.math import manhattan_distance


def record(record_obj, timestep, description: dict):
    """
    Record the game state from the scene descriptor

    Args:
        record_obj (Recorder): Recorder object
        timestep: Timestep of the game
        description (dict): Description of the game
    """
    # Keep track of how many times the agent effectively attacked
    if not hasattr(record_obj, 'effective_attack_object'):
        record_obj.effective_attack_object = {agent:{'effective_attack': 0} for agent in record_obj.player_names}
    
    if not hasattr(record_obj, 'collected_mushrooms_object'):
        record_obj.collected_mushrooms_object = {agent:{'purple_mushrooms':0,  'blue_mushrooms':0,  'green_mushrooms':0,  'orange_mushrooms':0, } for agent in record_obj.player_names}
        
    for agent, description in description.items():
        if description["effective_zap"]:
            record_obj.effective_attack_object[agent]['effective_attack'] += 1

def record_game_state_before_actions(record_obj, initial_map: list[list[str]], current_map: list[list[str]], current_actions_map: dict, scene_description: dict, previous_map: list[list[str]]):
    """
    Record the game state before the agents take any action

    Args:
        record_obj (Recorder): Recorder object
        initial_map (str): Initial map
        current_map (list[list[str]]): Current map
        current_actions_map (dict): Actions to take for each agent
        scene_description (dict): State description for each agent
        previous_map (list[list[str]]): Previous map in list of lists
    """
    
    # Create the last_apple_object if it does not exist
    
    # Create the attack_object if it does not exist
    if not hasattr(record_obj, 'attack_object'):
        record_obj.attack_object = {agent:{'decide_to_attack': 0} for agent in record_obj.player_names}

    if current_actions_map is None:
        return
    
    mushrooms_dict = {
        'F': 'purple_mushrooms',
        'H': 'green_mushrooms',
        'Z': 'blue_mushrooms',
        'N': 'orange_mushrooms'
    }
    for agent in current_actions_map:
        #TODO ADJUST THIS FILE IF NECESSARY 
        agent_id = record_obj.agents_ids[agent]
        agent_position = get_local_position_of_element(current_map, agent_id)
        if agent_position is None or previous_map is None:
            continue
        
        # Check if agent collected mushrooms
        prev_el = previous_map[agent_position[0]][agent_position[1]]
        if prev_el in mushrooms_dict:
            record_obj.collected_mushrooms_object[agent][mushrooms_dict[prev_el]] += 1
        
        # Check if the agent decided to attack
        if current_actions_map:
            did_attack = current_actions_map[agent]['fireZap'] # This is a boolean (1 or 0)
            if did_attack:
                record_obj.attack_object[agent]['decide_to_attack'] += 1

def record_elements_status(record_obj, initial_map: list[list[str]], current_map: list[list[str]]):
    """
    Record the game state after the agents took the actions

    Args:
        record_obj (Recorder): Recorder object
        initial_map (str): Initial map, it means the map before the agents took any action
        current_map (list[list[str]]): Current map, it means the map after the agents took the actions
    """
    # This function can not allow yet the recording of the mushrooms due to the arguments it does not receives, that record_before_actions does receive 
    # TODO: Add parameters to this function (thus to all other recorder.py files) that allow to record the mushrooms
    pass  

def save_custom_indicators(record_obj):
    """
    Save the custom indicators for the substrate

    Args:
        record_obj (Recorder): Recorder object
    """
    # Create a json file with the custom indicators


    # Number of times the agent decided to attack
    times_decide_to_attack = {agent: record_obj.attack_object[agent]['decide_to_attack'] for agent in record_obj.attack_object}

    # Number of times the agent effectively attacked
    effective_attack = {agent: record_obj.effective_attack_object[agent]['effective_attack'] for agent in record_obj.effective_attack_object}

    collected_mushrooms = {agent: record_obj.collected_mushrooms_object[agent] for agent in record_obj.collected_mushrooms_object}

    custom_indicators = {
        'times_decide_to_attack': times_decide_to_attack,
        'effective_attack': effective_attack,
        'collected_mushrooms': collected_mushrooms
    }

    with open(os.path.join(record_obj.log_path, "custom_indicators.json"), "w") as f:
        json.dump(custom_indicators, f)