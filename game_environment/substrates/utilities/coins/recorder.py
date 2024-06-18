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
    
    if not hasattr(record_obj, 'collected_coins_object'):
            record_obj.collected_coins_object = {agent:{'red_coins':0,  'yellow_coins':0} for agent in record_obj.player_names}
            
    for agent, description in description.items():
        if description["effective_zap"]:
            record_obj.effective_attack_object[agent]['effective_attack'] += 1
        
        
        

def record_game_state_before_actions(record_obj, initial_map: list[list[str]], current_map: list[list[str]], agents_observing: list[str], current_actions_map: dict, previous_map: list[list[str]]):
    """
    Record the game state before the agents take any action

    Args:
        record_obj (Recorder): Recorder object
        initial_map (str): Initial map
        current_map (list[list[str]]): Current map
        agents_observing (list[str]): Agents that are not going to take any action
    """
    
    # Create the attack_object if it does not exist
    if not hasattr(record_obj, 'attack_object'):
        record_obj.attack_object = {agent:{'decide_to_attack': 0} for agent in record_obj.player_names}

    #if not hasattr(record_obj, 'collected_coins_object'):
    #    record_obj.collected_coins_object = {agent:{'red_coins':0,  'yellow_coins':0} for agent in record_obj.player_names}
        
    # Get the agents that are taking actions
    agents_taking_actions = [agent for agent in record_obj.player_names if agent not in agents_observing]

    for agent in agents_taking_actions:
        agent_id = record_obj.agents_ids[agent]
        agent_position = get_local_position_of_element(current_map, agent_id)
        if agent_position is None or previous_map is None:
            continue
        
        # Check if the agent collected a coin
        if previous_map[agent_position[0]][agent_position[1]] == 'y':
            record_obj.collected_coins_object[agent]['yellow_coins'] += 1
            
        elif previous_map[agent_position[0]][agent_position[1]] == 'r':
            record_obj.collected_coins_object[agent]['red_coins'] += 1

        
        # Check if the agent decided to attack
        if current_actions_map:
            did_attack = current_actions_map[agent]['fireZap'] # This is a boolean (1 or 0)
            if did_attack:
                record_obj.attack_object[agent]['decide_to_attack'] += 1


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

    # Number of coins collected
    collected_coins = {agent: record_obj.collected_coins_object[agent] for agent in record_obj.collected_coins_object}
    
    

    custom_indicators = {
        'times_decide_to_attack': times_decide_to_attack,
        'effective_attack': effective_attack,
        'collected_coins': collected_coins
    }

    with open(os.path.join(record_obj.log_path, "custom_indicators.json"), "w") as f:
        json.dump(custom_indicators, f)