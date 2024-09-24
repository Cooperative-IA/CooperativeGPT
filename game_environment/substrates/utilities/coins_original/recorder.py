import os
import json
import numpy as np

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
    
    if not hasattr(record_obj, 'collected_coins_object'):
            record_obj.collected_coins_object = {agent:{'red_coins':0,  'yellow_coins':0} for agent in record_obj.player_names}
            
    for agent, description in description.items():
        if description["effective_zap"]:
            record_obj.effective_attack_object[agent]['effective_attack'] += 1
    
    
    if not hasattr(record_obj, 'previous_map'):
        record_obj.previous_map = None

        
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
    
    # Create the attack_object if it does not exist
    if not hasattr(record_obj, 'attack_object'):
        record_obj.attack_object = {agent:{'decide_to_attack': 0} for agent in record_obj.player_names}

    if current_actions_map is None:
        return

    for agent in current_actions_map:
        #TODO ADJUST THIS FILE IF NECESSARY 
        agent_id = record_obj.agents_ids[agent]
        agent_position = get_local_position_of_element(current_map, agent_id)
        if agent_position is None or previous_map is None:
            continue
        
        # Check if the agent decided to attack
        if current_actions_map:
            did_attack = current_actions_map[agent]['fireZap'] # This is a boolean (1 or 0)
            if did_attack:
                record_obj.attack_object[agent]['decide_to_attack'] += 1

    record_obj.previous_map = previous_map

def record_elements_status(record_obj, initial_map: list[list[str]], current_map: list[list[str]]):
    """
    Record the game state after the agents took the actions

    Args:
        record_obj (Recorder): Recorder object
        initial_map (str): Initial map, it means the map before the agents took any action
        current_map (list[list[str]]): Current map, it means the map after the agents took the actions
    """
    previous_map = record_obj.previous_map
    for agent in record_obj.player_names:
        agent_id = record_obj.agents_ids[agent]
        agent_position = get_local_position_of_element(current_map, agent_id)
        if agent_position is None or previous_map is None:
            continue
        
        # Here we check events related to coins
        # Check if the agent collected a coin
        if previous_map[agent_position[0]][agent_position[1]] == 'y':
            record_obj.collected_coins_object[agent]['yellow_coins'] += 1
            
        elif previous_map[agent_position[0]][agent_position[1]] == 'r':
            record_obj.collected_coins_object[agent]['red_coins'] += 1

def record_action(record_obj, **kwargs):
    """
    Record the actions of the agents

    Args:
        record_obj (Recorder): Recorder object
    """
    player = kwargs['player']
    curr_action = kwargs['curr_action']

    # Create the actions_taken object if it does not exist
    if not hasattr(record_obj, 'actions_taken'):
        record_obj.actions_taken = {agent: {} for agent in record_obj.player_names}

    # Parse the action
    if 'go to position' in curr_action:
        curr_action = 'go to'
    elif 'immobilize' in curr_action:
        curr_action = 'immobilize'
    record_obj.actions_taken[player][curr_action] = record_obj.actions_taken[player].get(curr_action, 0) + 1

def save_custom_indicators(record_obj, **kwargs):
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

    # Number of coins collected
    collected_coins = {agent: record_obj.collected_coins_object[agent] for agent in record_obj.collected_coins_object}
    
    

    custom_indicators = {
        'times_decide_to_attack': times_decide_to_attack,
        'effective_attack': effective_attack,
        'collected_coins': collected_coins,
        'actions_taken': record_obj.actions_taken
    }

    with open(os.path.join(record_obj.log_path, "custom_indicators.json"), "w") as f:
        json.dump(custom_indicators, f)