from game_environment.recorder.recorder import Recorder
from game_environment.substrates.commons_harvest_open_utilities.recorder import get_nearest_apple, is_apple_the_last_of_tree, record_game_state_before_actions, record_elements_status

def test_get_nearest_apple():
    # Test 1: Find the only apple in the map
    game_map = [
        ['0', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'A', 'F', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'F', 'F', 'F']
    ]
    position = (0, 0)
    nearest_apple, distance = get_nearest_apple(game_map, position)
    assert nearest_apple == [2, 2], "The nearest apple should be at position [2, 2]"

    # Test 2: Find the nearest apple
    game_map = [
        ['0', 'A', 'F', 'F', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'A', 'F', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'F', 'F', 'F']
    ]
    position = (0, 0)
    nearest_apple, distance = get_nearest_apple(game_map, position)
    assert nearest_apple == [0, 1], "The nearest apple should be at position [0, 1]"

    # Test 3: There are no apples
    game_map = [
        ['0', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'G', 'G', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'F', 'F', 'F']
    ]
    position = (0, 0)
    nearest_apple, distance = get_nearest_apple(game_map, position)
    assert nearest_apple == None, "The nearest apple should be None"

    # Test 4: Find the nearest apple in a real scenario
    game_map = [
        ['A', 'F', 'F', 'F', 'F'],
        ['G', 'G', 'G', 'F', 'F'],
        ['F', 'A', 'G', 'F', '0'],
        ['F', 'F', 'G', 'F', 'G'],
        ['F', 'F', 'F', 'G', 'A']
    ]
    position = (2, 4)
    nearest_apple, distance = get_nearest_apple(game_map, position)
    assert nearest_apple == [4, 4], "The nearest apple should be at position [4, 4]"

def test_is_apple_the_last_of_tree():
    # Test 1: The apple is the last of the tree
    game_map = [
        ['0', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'A', 'F', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'F', 'F', 'F']
    ]
    apple_position = (2, 2)
    agent_ids = ['0', '1', '2']
    is_last = is_apple_the_last_of_tree(game_map, apple_position, agent_ids)
    assert is_last == True, "The apple should be the last of the tree"

    # Test 2: The apple is not the last of the tree
    game_map = [
        ['0', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'A', 'A', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'F', 'F', 'F']
    ]
    apple_position = (2, 2)
    agent_ids = ['0', '1', '2']
    is_last = is_apple_the_last_of_tree(game_map, apple_position, agent_ids)
    assert is_last == False, "The apple should not be the last of the tree"

    # Test 3: There are no apples
    game_map = [
        ['0', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'G', 'G', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', 'F', 'F', 'F']
    ]
    apple_position = (0, 0)
    agent_ids = ['0', '1', '2']
    is_last = is_apple_the_last_of_tree(game_map, apple_position, agent_ids)
    assert is_last == False, "The apple should not be the last of the tree"

    # Test 4: The apple is the last of the tree in a real scenario
    game_map = [
        ['A', 'G', 'F', 'F', 'F'],
        ['G', '1', 'F', 'F', 'F'],
        ['0', 'G', 'F', 'F', 'F'],
        ['A', 'F', 'F', 'F', 'G'],
        ['F', 'F', 'F', 'G', 'A']
    ]
    apple_position = (0, 0)
    agent_ids = ['0', '1', '2']
    is_last = is_apple_the_last_of_tree(game_map, apple_position, agent_ids)
    assert is_last == False, "The apple should not be the last of the tree"

def test_record_game_state_before_actions():
    class RecorderMock:
        def __init__(self, names):
            self.player_names = names
            self.agents_ids = {name: str(agent_id) for agent_id, name in enumerate(names)}
    record_obj = RecorderMock(['Ma', 'Mi', 'Mo'])
    action_map = {
        'Ma': {'move': 0, 'turn': 0, 'fireZap': 1},
        'Mi': {'move': 0, 'turn': 0, 'fireZap': 0},
        'Mo': {'move': 0, 'turn': 0, 'fireZap': 0},
    }
    # Test 1: Record the game state before the agents take any action
    current_map = [
        ['0', 'F', 'G', 'A', 'G'],
        ['F', 'F', 'G', 'G', 'F'],
        ['F', 'F', 'F', '2', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', '1', 'A', 'G']
    ]
    agents_observing = ['Mi', 'Mo']
    record_game_state_before_actions(record_obj, None, current_map, agents_observing, action_map)
    # The record object should have the last_apple_object attribute
    assert hasattr(record_obj, 'last_apple_object'), "The record object should have the last_apple_object attribute"
    # The record object should have the last_apple_object attribute with the right values for each agent
    assert record_obj.last_apple_object == {'Ma': {'scenario_seen': 1, 'took_last_apple': 0, 'last_apple_pos': [0, 3], 'distance': 3, 'move_towards_last_apple': 0}, 'Mi': {'scenario_seen': 0, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0}, 'Mo': {'scenario_seen': 0, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0}}, "The last_apple_object attribute should have the right values for each agent"

    # Test 2: Record that the agent decided to attack
    assert hasattr(record_obj, 'attack_object'), "The record object should have the attack_object attribute"
    assert record_obj.attack_object == {'Ma': {'decide_to_attack': 1}, 'Mi': {'decide_to_attack': 0}, 'Mo': {'decide_to_attack': 0}}, "The attack_object attribute should have the right values for each agent"

def test_record_elements_status(mocker):
    class RecorderMock:
        def __init__(self, names, last_apple_object):
            self.player_names = names
            self.agents_ids = {name: str(agent_id) for agent_id, name in enumerate(names)}
            self.last_apple_object = last_apple_object
            self.log_path = ''
            self.step = 1

    mocker.patch('builtins.open') # Mock the open function to do not create a file

    # Test 1: Move towards the last apple
    last_apple_object = {'Ma': {'scenario_seen': 1, 'took_last_apple': 0, 'last_apple_pos': [0, 3], 'distance': 3, 'move_towards_last_apple': 0}, 'Mi': {'scenario_seen': 0, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0}, 'Mo': {'scenario_seen': 0, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0}}
    record_obj = RecorderMock(['Ma', 'Mi', 'Mo'], last_apple_object)
    current_map = [
        ['F', '0', 'G', 'A', 'G'],
        ['F', 'F', 'G', 'G', 'F'],
        ['F', 'F', 'F', '2', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', '1', 'A', 'G']
    ]
    agents_observing = ['Mi', 'Mo']
    record_elements_status(record_obj, None, current_map, agents_observing)
    # The record object should have the last_apple_object attribute with the right values for each agent
    assert record_obj.last_apple_object == {'Ma': {'scenario_seen': 1, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 1}, 'Mi': {'scenario_seen': 0, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0}, 'Mo': {'scenario_seen': 0, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0}}, "The last_apple_object attribute should have the right values for each agent"

    # Test 2: Take the last apple
    last_apple_object = {'Ma': {'scenario_seen': 3, 'took_last_apple': 0, 'last_apple_pos': [0, 3], 'distance': 1, 'move_towards_last_apple': 2}, 'Mi': {'scenario_seen': 0, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0}, 'Mo': {'scenario_seen': 0, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0}}
    record_obj = RecorderMock(['Ma', 'Mi', 'Mo'], last_apple_object)
    current_map = [
        ['F', 'F', 'F', '0', 'G'],
        ['F', 'F', 'G', 'G', 'F'],
        ['F', 'F', 'F', '2', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', '1', 'A', 'G']
    ]
    agents_observing = ['Mi', 'Mo']
    record_elements_status(record_obj, None, current_map, agents_observing)
    # The record object should have the last_apple_object attribute with the right values for each agent
    assert record_obj.last_apple_object == {'Ma': {'scenario_seen': 3, 'took_last_apple': 1, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 3}, 'Mi': {'scenario_seen': 0, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0}, 'Mo': {'scenario_seen': 0, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0}}, "The last_apple_object attribute should have the right values for each agent"

    # Test 3: Move away from the last apple
    last_apple_object = {'Ma': {'scenario_seen': 1, 'took_last_apple': 0, 'last_apple_pos': [0, 3], 'distance': 3, 'move_towards_last_apple': 0}, 'Mi': {'scenario_seen': 0, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0}, 'Mo': {'scenario_seen': 0, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0}}
    record_obj = RecorderMock(['Ma', 'Mi', 'Mo'], last_apple_object)
    current_map = [
        ['F', 'F', 'G', 'A', 'G'],
        ['0', 'F', 'G', 'G', 'F'],
        ['F', 'F', 'F', '2', 'F'],
        ['F', 'F', 'F', 'F', 'F'],
        ['F', 'F', '1', 'A', 'G']
    ]
    agents_observing = ['Mi', 'Mo']
    record_elements_status(record_obj, None, current_map, agents_observing)
    # The record object should have the last_apple_object attribute with the right values for each agent
    assert record_obj.last_apple_object == {'Ma': {'scenario_seen': 1, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0}, 'Mi': {'scenario_seen': 0, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0}, 'Mo': {'scenario_seen': 0, 'took_last_apple': 0, 'last_apple_pos': None, 'distance': 0, 'move_towards_last_apple': 0}}, "The last_apple_object attribute should have the right values for each agent"