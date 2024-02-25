import os
import json

from game_environment.utils import connected_elems_map
from utils.math import manhattan_distance

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

def get_nearest_apple(game_map: list[list[str]], position: tuple[int, int]) -> tuple[int, int]:
    """
    Get the nearest apple position

    Args:
        map (list[list[str]]): Map of the game
        position (tuple[int, int]): Position of the agent or reference position in the map

    Returns:
        tuple[tuple[int, int], int]: Nearest apple position and its distance. If there are no apples, return None, float('inf')
    """
    groups = connected_elems_map(game_map, ['A'])
    nearest_apple = None
    nearest_distance = float('inf')
    for group in groups.values():
        for apple in group['elements']:
            distance = manhattan_distance(apple, position)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_apple = apple

    return nearest_apple, nearest_distance

def is_apple_the_last_of_tree(game_map: list[list[str]], apple_position: tuple[int, int], agent_ids: list[str]) -> tuple[int, int]:
    """
    Evaluate if the apple is the last of the tree

    Args:
        game_map (list[list[str]]): Map of the game
        apple_position (tuple[int, int]): Position of the apple
        agent_ids (list[str]): List of agents ids

    Returns:
        bool: True if the apple is the last of the tree, False otherwise
    """
    groups = connected_elems_map(game_map, ['A', '#', 'G'] + agent_ids)
    for group in groups.values():
        apples = []

        # We only want to consider the tree that contains the apple
        if list(apple_position) not in group['elements']:
            continue

        for elem in group['elements']:
            element = game_map[elem[0]][elem[1]]
            if element == 'A':
                apples.append(elem)
        
        if len(apples) == 1:
            return True
        
    return False

def record_game_state_before_actions(record_obj, initial_map: list[list[str]], current_map: list[list[str]], agents_observing: list[str], current_actions_map: dict):
    """
    Record the game state before the agents take any action

    Args:
        record_obj (Recorder): Recorder object
        initial_map (str): Initial map
        current_map (list[list[str]]): Current map
        agents_observing (list[str]): Agents that are not going to take any action
    """
    # Create the last_apple_object if it does not exist
    if not hasattr(record_obj, 'last_apple_object'):
        record_obj.last_apple_object = {agent:{'scenario_seen': 0, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0} for agent in record_obj.player_names}

    # Create the attack_object if it does not exist
    if not hasattr(record_obj, 'attack_object'):
        record_obj.attack_object = {agent:{'decide_to_attack': 0} for agent in record_obj.player_names}

    # Get the agents that are taking actions
    agents_taking_actions = [agent for agent in record_obj.player_names if agent not in agents_observing]

    for agent in agents_taking_actions:
        agent_id = record_obj.agents_ids[agent]
        agent_position = get_local_position_of_element(current_map, agent_id)

        # Check if is the last apple scenario
        nearest_apple, distance = get_nearest_apple(current_map, agent_position)

        is_last = is_apple_the_last_of_tree(current_map, nearest_apple, agents_observing)
        if is_last:
            # Update the last_apple_object
            record_obj.last_apple_object[agent]['scenario_seen'] += 1
            record_obj.last_apple_object[agent]['last_apple_pos'] = nearest_apple # If last_apple_pos is set, then after taking the action we can check if the apple is still there
            record_obj.last_apple_object[agent]['distance'] = distance

        # Check if the agent decided to attack
        if current_actions_map:
            did_attack = current_actions_map[agent]['fireZap'] # This is a boolean (1 or 0)
            if did_attack:
                record_obj.attack_object[agent]['decide_to_attack'] += 1

def record_elements_status(record_obj, initial_map: list[list[str]], current_map: list[list[str]], agents_observing: list[str]):
    """
    Record the game state after the agents took the actions

    Args:
        record_obj (Recorder): Recorder object
        initial_map (str): Initial map
        current_map (list[list[str]]): Current map
        agents_observing (list[str]): Agents that are not going to take any action
    """
    # Transform list map to string map
    connected_elements = connected_elems_map(initial_map, ['A'])

    trees = {}

    for elem_key in connected_elements:
        elements = connected_elements[elem_key]['elements']
        if len(elements) > 1:
            apples_count = len([elem for elem in elements if current_map[elem[0]][elem[1]] == 'A'])
            trees[elem_key] = apples_count

    with open(os.path.join(record_obj.log_path, "trees_history.txt"), "a") as f:
        f.write(f"{record_obj.step}: {trees}\n")

    # Check if the last apple was taken or if the agent moved towards the last apple
    if hasattr(record_obj, 'last_apple_object'):
        for agent in record_obj.last_apple_object:
            if agent in agents_observing:
                continue

            if record_obj.last_apple_object[agent]['last_apple_pos'] is not None:
                # Check if the agent moved towards the last apple
                agent_position = get_local_position_of_element(current_map, record_obj.agents_ids[agent])
                new_distance = manhattan_distance(agent_position, record_obj.last_apple_object[agent]['last_apple_pos'])
                if new_distance < record_obj.last_apple_object[agent]['distance']:
                    record_obj.last_apple_object[agent]['move_towards_last_apple'] += 1
                # Check if the agent took the last apple
                if current_map[record_obj.last_apple_object[agent]['last_apple_pos'][0]][record_obj.last_apple_object[agent]['last_apple_pos'][1]] == record_obj.agents_ids[agent]:
                    record_obj.last_apple_object[agent]['took_last_apple'] += 1

                # Reset the last_apple information
                record_obj.last_apple_object[agent]['last_apple_pos'] = None
                record_obj.last_apple_object[agent]['distance'] = 0

def save_custom_indicators(record_obj):
    """
    Save the custom indicators for the substrate

    Args:
        record_obj (Recorder): Recorder object
    """
    # Create a json file with the custom indicators
    # Percentage of times the agent moved towards the last apple
    portion_move_towards_last_apple = {}
    for agent in record_obj.last_apple_object:
        if record_obj.last_apple_object[agent]['scenario_seen'] == 0:
            portion_move_towards_last_apple[agent] = 0
        else:
            portion_move_towards_last_apple[agent] = record_obj.last_apple_object[agent]['move_towards_last_apple'] / record_obj.last_apple_object[agent]['scenario_seen']
        
    # Number of times the agent took the last apple
    times_took_last_apple = {agent: record_obj.last_apple_object[agent]['took_last_apple'] for agent in record_obj.last_apple_object}

    # Number of times the agent decided to attack
    times_decide_to_attack = {agent: record_obj.attack_object[agent]['decide_to_attack'] for agent in record_obj.attack_object}

    custom_indicators = {
        'portion_move_towards_last_apple': portion_move_towards_last_apple,
        'times_took_last_apple': times_took_last_apple,
        'times_decide_to_attack': times_decide_to_attack
    }

    with open(os.path.join(record_obj.log_path, "custom_indicators.json"), "w") as f:
        json.dump(custom_indicators, f)