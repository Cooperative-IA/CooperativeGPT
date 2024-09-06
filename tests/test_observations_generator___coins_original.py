from importlib import import_module
from utils.files import get_players_contexts
from game_environment.scene_descriptor.observations_generator import ObservationsGenerator
from game_environment.substrates.python.coins_original import ASCII_MAP
from game_environment.utils import connected_elems_map, get_element_global_pos
substrate_utils = import_module(f'game_environment.substrates.utilities.{"coins_original"}.substrate_utils')

players = ['Juan', 'Laura']
obs_gen = ObservationsGenerator(ASCII_MAP, players, 'coins_original')
orientation_map = {0: 'North', 1: 'East', 2: 'South', 3: 'West'}
players_context = get_players_contexts("data/defined_experiments/coins_original/agents_context/no_bio_2p")
scenario_info = substrate_utils.load_scenario_info(players_context)
def test_get_element_global_pos():
    self_global_pos = (10, 5)

    # Test case 1: agent_orientation = 0
    el_local_pos = (5, 3)
    self_local_pos = (0, 3)
    agent_orientation = 0
    expected_output = [15, 5]
    element_global_pos = get_element_global_pos(el_local_pos, self_local_pos, self_global_pos, agent_orientation)
    assert element_global_pos == expected_output, f'Expected {expected_output}, got {element_global_pos}.Failed with agent_orientation = {agent_orientation}: {orientation_map[agent_orientation]}'

    # Test case 2: agent_orientation = 1
    el_local_pos = (0, 0)
    self_local_pos = (0, 5)
    agent_orientation = 1
    expected_output = [5, 5]
    element_global_pos = get_element_global_pos(el_local_pos, self_local_pos, self_global_pos, agent_orientation)
    assert element_global_pos == expected_output, f'Expected {expected_output}, got {element_global_pos}.Failed with agent_orientation = {agent_orientation}: {orientation_map[agent_orientation]}'

    # Test case 3: agent_orientation = 2
    el_local_pos = (2, 3)
    self_local_pos = (7, 3)
    agent_orientation = 2
    expected_output = [15, 5]
    element_global_pos = get_element_global_pos(el_local_pos, self_local_pos, self_global_pos, agent_orientation)
    assert element_global_pos == expected_output, f'Expected {expected_output}, got {element_global_pos}.Failed with agent_orientation = {agent_orientation}: {orientation_map[agent_orientation]}'

    # Test case 4: agent_orientation = 3
    el_local_pos = (7, 9)
    self_local_pos = (7, 4)
    agent_orientation = 3
    expected_output = [5, 5]
    element_global_pos = get_element_global_pos(el_local_pos, self_local_pos, self_global_pos, agent_orientation)
    assert element_global_pos == expected_output, f'Expected {expected_output}, got {element_global_pos}.Failed with agent_orientation = {agent_orientation}: {orientation_map[agent_orientation]}'

    el_local_pos = (1, 9)
    self_local_pos = (9, 5)
    self_global_pos = (7, 21)
    agent_orientation = 3
    expected_output = [3, 13]
    element_global_pos = get_element_global_pos(el_local_pos, self_local_pos, self_global_pos, agent_orientation)
    assert element_global_pos == expected_output, f'Expected {expected_output}, got {element_global_pos}.Failed with agent_orientation = {agent_orientation}: {orientation_map[agent_orientation]}'

    print("All test cases pass")
    
def test_get_observed_agents():
    observed_map = 'FFy\nFFF\n0FF\nyFF\nr#F\nrFr'
    local_map_position = (4,1)
    global_position = (7, 21)
    agent_orientation = 0
    expected_output = ['Observed agent Juan at position [5, 20].']
    agents_observed = obs_gen.get_agents_observed(observed_map, local_map_position, global_position, agent_orientation)
    assert sorted(agents_observed) == sorted(expected_output), f"Expected {expected_output}, got {agents_observed}."

    observed_map = 'yFFFF1\nFFFF#G\nFFFyyy'
    local_map_position = (1,4)
    global_position = (7, 21)
    agent_orientation = 1
    expected_output = ['Observed agent Laura at position [8, 22].']
    agents_observed = obs_gen.get_agents_observed(observed_map, local_map_position, global_position, agent_orientation)
    assert sorted(agents_observed) == sorted(expected_output), f"Expected {expected_output}, got {agents_observed}."

    observed_map = 'ryr\nF#1\nFFy\nFFF\nFFF\nrFF'
    local_map_position = (1,1)
    global_position = (7, 21)
    agent_orientation = 2
    expected_output = ['Observed agent Laura at position [7, 20].']
    agents_observed = obs_gen.get_agents_observed(observed_map, local_map_position, global_position, agent_orientation)
    assert sorted(agents_observed) == sorted(expected_output), f"Expected {expected_output}, got {agents_observed}."

    observed_map = 'ryrFFF\n0#FFFF\nyFFFFy'
    local_map_position = (1,1)
    global_position = (7, 21)
    agent_orientation = 3
    expected_output = ['Observed agent Juan at position [8, 21].']
    agents_observed = obs_gen.get_agents_observed(observed_map, local_map_position, global_position, agent_orientation)
    assert sorted(agents_observed) == sorted(expected_output), f"Expected {expected_output}, got {agents_observed}."

def test_get_observed_changes():
    game_time = '2021-09-30 12:00:00'
    observed_map      = 'FFF\nF#F\n1yF'
    last_observed_map = 'FFF\nF#F\nryF'
    agent_orientation = 0
    local_position = (1,1)
    global_position = (5, 5)
    expected_output = [('Observed that agent Laura from red team took a red coin from position [6, 4].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, global_position, agent_orientation, agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    observed_map      = 'FFF\nF#F\n0yF'
    last_observed_map = 'FFF\nF#F\nyyF'
    agent_orientation = 0
    local_position = (1,1)
    global_position = (5, 5)
    expected_output = [('Observed that agent Juan from yellow team took a yellow coin from position [6, 4].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, global_position, agent_orientation, agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    observed_map      = 'FFF\nF#F\nFyF'
    last_observed_map = 'FFF\nF#F\nyyF'
    agent_orientation = 0
    local_position = (1,1)
    global_position = (5, 5)
    expected_output = [('Observed that yellow coin disappeared at position [6, 4].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, global_position, agent_orientation, agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    observed_map = 'FFF\nF#F\nyFF'
    last_observed_map = 'FFF\nF#F\nFFF'
    agent_orientation = 0
    local_position = (1,1)
    global_position = (5, 5)
    expected_output = [("Observed that yellow coin appeared at position [6, 4].", game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, global_position, agent_orientation, agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Observed red coin disappeared
    observed_map = 'FFF\nF#F\nFFF'
    last_observed_map = 'FFF\nF#F\nrFF'
    agent_orientation = 0
    local_position = (1,1)
    global_position = (5, 5)
    expected_output = [("Observed that red coin disappeared at position [6, 4].", game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, global_position, agent_orientation, agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."
    
    # Observed red coin appeared
    observed_map = 'FFF\nF#F\nrFF'
    last_observed_map = 'FFF\nF#F\nFFF'
    agent_orientation = 0
    local_position = (1,1)
    global_position = (5, 5)
    expected_output = [("Observed that red coin appeared at position [6, 4].", game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, global_position, agent_orientation, agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."
    

# Tests to verify that changes in state are detected correctly while the agent is moving over the map
def test_get_observed_changes_while_moving():
    # Detect that the agent took an apple
    game_time = '2021-09-30 12:00:00'
    observed_map = 'FFA\nr#r\nFFF'
    last_observed_map = 'rrr\nF#F\nFFF'
    agent_orientation = 0
    last_agent_orientation = 0
    local_position = (1,1)
    global_position = (4, 5)
    last_global_position = (5, 5)
    expected_output = [("I took a red coin at position [4, 5].", game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, last_global_position, agent_orientation, last_agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Detect that another agent took an apple
    game_time = '2021-09-30 12:00:00'
    observed_map = 'FFy\nr#1\nFFF'
    last_observed_map = 'rry\nF#F\nFFF'
    agent_orientation = 0
    last_agent_orientation = 0
    local_position = (1,1)
    global_position = (4, 5)
    last_global_position = (5, 5)
    expected_output = [('I took a red coin at position [4, 5].', game_time), ('Observed that agent Laura from red team took a yellow coin from position [4, 6].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, last_global_position, agent_orientation, last_agent_orientation, game_time,"Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."
