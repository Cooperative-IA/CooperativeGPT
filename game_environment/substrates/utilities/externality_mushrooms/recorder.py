import os
import json
import re

from game_environment.utils import connected_elems_map, get_local_position_of_element
from utils.math import manhattan_distance
from utils.time import str_to_timestamp


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
    
    for agent in current_actions_map:
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

def record_observations(record_obj, **kwargs):
    """
    Record the observations of the agents

    Args:
        record_obj (Recorder): Recorder object
    """
    player= kwargs['player']
    observations = kwargs['observations']
    changes = kwargs['changes']

    # Create mushroom_consumption object if it does not exist
    if not hasattr(record_obj, 'mushroom_consumption'):
        record_obj.mushroom_consumption = {agent:{'red':0,  'blue':0,  'green':0,  'orange':0, } for agent in record_obj.player_names}

    # Create mushroom_consumption_by_step object if it does not exist
    if not hasattr(record_obj, 'mushroom_consumption_by_step'):
        record_obj.mushroom_consumption_by_step = {}

    # Check if the agent consumed a mushroom
    # The changes are in the form of 'I took a/an <mushroom_type>'
    pattern = re.compile(r'I took a(n)? (\w+)')
    for change, game_time in changes:
        match = pattern.match(change)
        if match:
            mushroom_type = match.group(2)
            step = str_to_timestamp(game_time)
            record_obj.mushroom_consumption[player][mushroom_type] += 1

            if not step in record_obj.mushroom_consumption_by_step:
                record_obj.mushroom_consumption_by_step[step] = {}

            if not hasattr(record_obj.mushroom_consumption_by_step[step], player):
                record_obj.mushroom_consumption_by_step[step][player] = {}

            record_obj.mushroom_consumption_by_step[step][player][mushroom_type] = 1

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

    mushrooms_consumption = record_obj.mushroom_consumption

    # Calculate time spent digesting mushrooms
    total_steps = kwargs['game_steps']
    digesting_time_by_mushroom = {
        'red': 0,
        'blue': 15,
        'green': 10,
        'orange': 15
    }
    digesting_time = {agent: sum([mushrooms_consumption[agent][mushroom] * digesting_time_by_mushroom[mushroom] for mushroom in mushrooms_consumption[agent]])/total_steps for agent in mushrooms_consumption}

    custom_indicators = {
        'times_decide_to_attack': times_decide_to_attack,
        'effective_attack': effective_attack,
        'mushrooms_consumption': mushrooms_consumption,
        'digesting_spent_time': digesting_time,
        'actions_taken': record_obj.actions_taken,
        'mushroom_consumption_by_step': record_obj.mushroom_consumption_by_step
    }

    with open(os.path.join(record_obj.log_path, "custom_indicators.json"), "w") as f:
        json.dump(custom_indicators, f)