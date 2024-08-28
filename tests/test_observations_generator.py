from game_environment.scene_descriptor.observations_generator import ObservationsGenerator
from game_environment.substrates.python.commons_harvest_open import ASCII_MAP
from game_environment.utils import connected_elems_map, get_element_global_pos

players = ['agent1', 'agent2', 'agent3']
obs_gen = ObservationsGenerator(ASCII_MAP, players, 'commons_harvest_open')
orientation_map = {0: 'North', 1: 'East', 2: 'South', 3: 'West'}

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
    
def test_connected_elems_map():
    # Test case 1: Single element
    observed_map = "A"
    elements_to_find = ["A"]
    expected_output = {1: {'center': (0, 0), 'elements': [[0, 0]]}}
    assert connected_elems_map(observed_map, elements_to_find) == expected_output, f"Failed for a single element"

    # Test case 2: A single connected component
    observed_map = "AB\nBA"
    elements_to_find = ["A", "B"]
    expected_output = {1: {'center': (0, 0), 'elements': [[0, 0], [0, 1], [1, 0], [1, 1]]}} # All elements are connected
    elements_found = connected_elems_map(observed_map, elements_to_find)
    assert elements_found == expected_output, f"Expected {expected_output}, got {elements_found}. Failed for a single connected component"

    # Test case 3: Multiple connected components
    observed_map = [
        "-AA---",
        "GA----",
        "----AG",
        "----GA",
        ]
    observed_map = "\n".join(observed_map)
    elements_to_find = ["A", "G"]
    expected_output = {1: {'center': (0, 1), 'elements': [[0, 1], [0, 2], [1, 0], [1, 1]]}, 2: {'center': (2, 4), 'elements': [[2, 4], [2, 5], [3, 4], [3, 5]]}}
    elements_found = connected_elems_map(observed_map, elements_to_find)
    assert elements_found == expected_output, f"Expected {expected_output}, got {elements_found}. Failed for multiple connected components"


    # Test case 4: No elements found
    observed_map = "AB\nCD"
    elements_to_find = ["E"]
    expected_output = {}
    elements_found = connected_elems_map(observed_map, elements_to_find)
    assert elements_found == expected_output, f"Expected {expected_output}, got {elements_found}. Failed for multiple connected components"

    print("All test cases pass")

def test_get_trees_descriptions():
    observed_map = 'FFA\nFFF\nFFF\nAFF\nA#F\nAGA'
    local_map_position = (4,1)
    global_position = (7, 21)
    agent_orientation = 0
    expected_output = ['Observed an apple at position [8, 20]. This apple belongs to tree 6.', 'Observed an apple at position [7, 20]. This apple belongs to tree 6.', 'Observed an apple at position [6, 20]. This apple belongs to tree 6.', 'Observed grass to grow apples at position [8, 21]. This grass belongs to tree 6.', 'Observed an apple at position [8, 22]. This apple belongs to tree 6.', 'Observed tree 6 at position [8, 20]. This tree has 4 apples remaining and 1 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.', 'Observed an apple at position [3, 22]. This apple belongs to tree 4.', 'Observed tree 4 at position [1, 21]. This tree has 1 apples remaining and 0 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.']
    connected_elems = obs_gen.connected_elments 
    symbols = {'self_symbol': obs_gen.self_symbol, 'other_players_symbols': obs_gen.other_players_symbols }
    trees_descriptions = obs_gen.get_specific_substrate_observations(observed_map, local_map_position, global_position, agent_orientation, connected_elems, symbols)
    assert sorted(trees_descriptions) == sorted(expected_output), f"Expected {expected_output}, got {trees_descriptions}."

    observed_map = 'AFFFFA\nFFFF#G\nFFFAAA'
    local_map_position = (1,4)
    global_position = (7, 21)
    agent_orientation = 1
    expected_output = ['Observed an apple at position [8, 20]. This apple belongs to tree 6.', 'Observed an apple at position [7, 20]. This apple belongs to tree 6.', 'Observed an apple at position [6, 20]. This apple belongs to tree 6.', 'Observed grass to grow apples at position [8, 21]. This grass belongs to tree 6.', 'Observed an apple at position [8, 22]. This apple belongs to tree 6.', 'Observed tree 6 at position [8, 20]. This tree has 4 apples remaining and 1 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.', 'Observed an apple at position [3, 22]. This apple belongs to tree 4.', 'Observed tree 4 at position [1, 21]. This tree has 1 apples remaining and 0 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.']
    connected_elems = obs_gen.connected_elments 
    symbols = {'self_symbol': obs_gen.self_symbol, 'other_players_symbols': obs_gen.other_players_symbols }
    trees_descriptions = obs_gen.get_specific_substrate_observations(observed_map, local_map_position, global_position, agent_orientation, connected_elems, symbols)
    assert sorted(trees_descriptions) == sorted(expected_output), f"Expected {expected_output}, got {trees_descriptions}."

    observed_map = 'AGA\nF#A\nFFA\nFFF\nFFF\nAFF'
    local_map_position = (1,1)
    global_position = (7, 21)
    agent_orientation = 2
    expected_output = ['Observed an apple at position [8, 20]. This apple belongs to tree 6.', 'Observed an apple at position [7, 20]. This apple belongs to tree 6.', 'Observed an apple at position [6, 20]. This apple belongs to tree 6.', 'Observed grass to grow apples at position [8, 21]. This grass belongs to tree 6.', 'Observed an apple at position [8, 22]. This apple belongs to tree 6.', 'Observed tree 6 at position [8, 20]. This tree has 4 apples remaining and 1 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.', 'Observed an apple at position [3, 22]. This apple belongs to tree 4.', 'Observed tree 4 at position [1, 21]. This tree has 1 apples remaining and 0 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.']
    connected_elems = obs_gen.connected_elments 
    symbols = {'self_symbol': obs_gen.self_symbol, 'other_players_symbols': obs_gen.other_players_symbols }
    trees_descriptions = obs_gen.get_specific_substrate_observations(observed_map, local_map_position, global_position, agent_orientation, connected_elems, symbols)
    assert sorted(trees_descriptions) == sorted(expected_output), f"Expected {expected_output}, got {trees_descriptions}."

    observed_map = 'AAAFFF\nG#FFFF\nAFFFFA'
    local_map_position = (1,1)
    global_position = (7, 21)
    agent_orientation = 3
    expected_output = ['Observed an apple at position [8, 20]. This apple belongs to tree 6.', 'Observed an apple at position [7, 20]. This apple belongs to tree 6.', 'Observed an apple at position [6, 20]. This apple belongs to tree 6.', 'Observed grass to grow apples at position [8, 21]. This grass belongs to tree 6.', 'Observed an apple at position [8, 22]. This apple belongs to tree 6.', 'Observed tree 6 at position [8, 20]. This tree has 4 apples remaining and 1 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.', 'Observed an apple at position [3, 22]. This apple belongs to tree 4.', 'Observed tree 4 at position [1, 21]. This tree has 1 apples remaining and 0 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.']
    connected_elems = obs_gen.connected_elments 
    symbols = {'self_symbol': obs_gen.self_symbol, 'other_players_symbols': obs_gen.other_players_symbols }
    trees_descriptions = obs_gen.get_specific_substrate_observations(observed_map, local_map_position, global_position, agent_orientation, connected_elems, symbols)
    assert sorted(trees_descriptions) == sorted(expected_output), f"Expected {expected_output}, got {trees_descriptions}."

    # When the agent is in a tree and might interrupt the connected components observed
    observed_map = '-----------\n-----------\n-----------\n-----------\n-----------\n-----------\n-----------\nWWWWWWWWWWW\nFFFFFAFFFFA\nFFFFA#AFFFF\nAFFAAAAAFFF'
    local_map_position = (9,5)
    global_position = (2, 15)
    agent_orientation = 0
    expected_output = [
    'Observed an apple at position [3, 10]. This apple belongs to tree 2.', 
    'Observed tree 2 at position [3, 8]. This tree has 1 apples remaining and 0 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.', 
    'Observed an apple at position [1, 15]. This apple belongs to tree 3.', 
    'Observed an apple at position [2, 14]. This apple belongs to tree 3.', 
    'Observed an apple at position [2, 16]. This apple belongs to tree 3.', 
    'Observed an apple at position [3, 13]. This apple belongs to tree 3.', 
    'Observed an apple at position [3, 14]. This apple belongs to tree 3.', 
    'Observed an apple at position [3, 15]. This apple belongs to tree 3.', 
    'Observed an apple at position [3, 16]. This apple belongs to tree 3.', 
    'Observed an apple at position [3, 17]. This apple belongs to tree 3.', 
    'Observed tree 3 at position [3, 15]. This tree has 8 apples remaining and 0 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.', 
    'Observed an apple at position [1, 20]. This apple belongs to tree 4.', 
    'Observed tree 4 at position [1, 21]. This tree has 1 apples remaining and 0 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.'
    ]
    connected_elems = obs_gen.connected_elments 
    symbols = {'self_symbol': obs_gen.self_symbol, 'other_players_symbols': obs_gen.other_players_symbols }
    trees_descriptions = obs_gen.get_specific_substrate_observations(observed_map, local_map_position, global_position, agent_orientation, connected_elems, symbols)
    assert sorted(trees_descriptions) == sorted(expected_output), f"Expected {expected_output}, got {trees_descriptions}."

    # When another agent is in a tree and might interrupt the connected components observed
    observed_map = '-----------\n-----------\n-----------\n-----------\n-----------\n-----------\n-----------\nWWWWWWWWWWW\nFFFFFAFFFFA\nFFFFA#2FFFF\nAFFAAAAAFFF'
    local_map_position = (9,5)
    global_position = (2, 15)
    agent_orientation = 0
    expected_output = [
    'Observed an apple at position [3, 10]. This apple belongs to tree 2.', 
    'Observed tree 2 at position [3, 8]. This tree has 1 apples remaining and 0 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.', 
    'Observed an apple at position [1, 15]. This apple belongs to tree 3.', 
    'Observed an apple at position [2, 14]. This apple belongs to tree 3.',
    'Observed an apple at position [3, 13]. This apple belongs to tree 3.', 
    'Observed an apple at position [3, 14]. This apple belongs to tree 3.', 
    'Observed an apple at position [3, 15]. This apple belongs to tree 3.', 
    'Observed an apple at position [3, 16]. This apple belongs to tree 3.', 
    'Observed an apple at position [3, 17]. This apple belongs to tree 3.', 
    'Observed tree 3 at position [3, 15]. This tree has 7 apples remaining and 0 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.', 
    'Observed an apple at position [1, 20]. This apple belongs to tree 4.', 
    'Observed tree 4 at position [1, 21]. This tree has 1 apples remaining and 0 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.'
    ]
    connected_elems = obs_gen.connected_elments 
    symbols = {'self_symbol': obs_gen.self_symbol, 'other_players_symbols': obs_gen.other_players_symbols }
    trees_descriptions = obs_gen.get_specific_substrate_observations(observed_map, local_map_position, global_position, agent_orientation, connected_elems, symbols)
    assert sorted(trees_descriptions) == sorted(expected_output), f"Expected {expected_output}, got {trees_descriptions}."

    # When agent is on a corner 
    observed_map = '-----------\n-----------\n-----------\n-----------\n-----------\n-----------\n-----------\n-----------\n----WWWWWWW\n----W#AAFFF\n----WGAFFFF'
    local_map_position = (9,5)
    global_position = (1, 22)
    agent_orientation = 1
    expected_output = [
        'Observed an apple at position [2, 21]. This apple belongs to tree 4.',
        'Observed an apple at position [2, 22]. This apple belongs to tree 4.',
        'Observed an apple at position [3, 22]. This apple belongs to tree 4.',
        'Observed grass to grow apples at position [1, 21]. This grass belongs to tree 4.',
        'Observed tree 4 at position [1, 21]. This tree has 3 apples remaining and 1 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.',
        ]
    connected_elems = obs_gen.connected_elments 
    symbols = {'self_symbol': obs_gen.self_symbol, 'other_players_symbols': obs_gen.other_players_symbols }
    trees_descriptions = obs_gen.get_specific_substrate_observations(observed_map, local_map_position, global_position, agent_orientation, connected_elems, symbols)
    assert sorted(trees_descriptions) == sorted(expected_output), f"Expected {expected_output}, got {trees_descriptions}."

    # Detect that someone was attacked by other agent
    observed_map = '-WFFFFFFFFF\n-WFFFFFFFFF\n-WFFFFFFFFF\n-WFFFFFFFFF\n-WFFFFFFFFF\n-WFFFFFFFFF\n-WFFFFFFFFF\n-WFFFFFFFFF\n-WFFFFFFFFF\n-WFFF#FFFFA\n-WFFFF2FFAA'
    agent_orientation = 3
    local_map_position = (9,5)
    global_position = (13, 18)
    expected_output = [
        'Observed an apple at position [8, 18]. This apple belongs to tree 6.',
        'Observed an apple at position [9, 19]. This apple belongs to tree 6.',
        'Observed an apple at position [8, 19]. This apple belongs to tree 6.',
        'Observed tree 6 at position [8, 20]. This tree has 3 apples remaining and 0 grass for apples growing on the observed map. The tree might have more apples and grass on the global map.']
    connected_elems = obs_gen.connected_elments 
    symbols = {'self_symbol': obs_gen.self_symbol, 'other_players_symbols': obs_gen.other_players_symbols }
    observed_changes = obs_gen.get_specific_substrate_observations(observed_map, local_map_position, global_position, agent_orientation, connected_elems, symbols)
    print(f"Params: {observed_map, local_map_position, global_position, agent_orientation, connected_elems, symbols}")
    print(f"Expected: {expected_output}")
    print(f"Observed: {observed_changes}")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."
  
def test_get_observed_agents():
    observed_map = 'FFA\nFFF\n0FF\nAFF\nA#F\nAGA'
    local_map_position = (4,1)
    global_position = (7, 21)
    agent_orientation = 0
    expected_output = ['Observed agent agent1 at position [5, 20].']
    agents_observed = obs_gen.get_agents_observed(observed_map, local_map_position, global_position, agent_orientation)
    assert sorted(agents_observed) == sorted(expected_output), f"Expected {expected_output}, got {agents_observed}."

    observed_map = 'AFFFF2\nFFFF#G\nFFFAAA'
    local_map_position = (1,4)
    global_position = (7, 21)
    agent_orientation = 1
    expected_output = ['Observed agent agent3 at position [8, 22].']
    agents_observed = obs_gen.get_agents_observed(observed_map, local_map_position, global_position, agent_orientation)
    assert sorted(agents_observed) == sorted(expected_output), f"Expected {expected_output}, got {agents_observed}."

    observed_map = 'AGA\nF#1\nFFA\nFFF\nFFF\nAFF'
    local_map_position = (1,1)
    global_position = (7, 21)
    agent_orientation = 2
    expected_output = ['Observed agent agent2 at position [7, 20].']
    agents_observed = obs_gen.get_agents_observed(observed_map, local_map_position, global_position, agent_orientation)
    assert sorted(agents_observed) == sorted(expected_output), f"Expected {expected_output}, got {agents_observed}."

    observed_map = 'AAAFFF\n0#FFFF\nAFFFFA'
    local_map_position = (1,1)
    global_position = (7, 21)
    agent_orientation = 3
    expected_output = ['Observed agent agent1 at position [8, 21].']
    agents_observed = obs_gen.get_agents_observed(observed_map, local_map_position, global_position, agent_orientation)
    assert sorted(agents_observed) == sorted(expected_output), f"Expected {expected_output}, got {agents_observed}."

def test_get_observed_changes():
    game_time = '2021-09-30 12:00:00'
    observed_map = 'AAA\nF#F\n2AF'
    last_observed_map = 'AAA\nF#F\nAAF'
    agent_orientation = 0
    local_position = (1,1)
    global_position = (5, 5)
    expected_output = [('Observed that agent agent3 took an apple from position [6, 4].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, global_position, agent_orientation, agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    observed_map = 'AAA\nF#F\nAAF'
    last_observed_map = 'AAA\nF#F\nGAF'
    agent_orientation = 0
    local_position = (1,1)
    global_position = (5, 5)
    expected_output = [('Observed that an apple grew at position [6, 4].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, global_position, agent_orientation, agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    observed_map = 'AAA\nF#F\nFAF'
    last_observed_map = 'AAA\nF#F\nGAF'
    agent_orientation = 0
    local_position = (1,1)
    global_position = (5, 5)
    expected_output = [('Observed that the grass at position [6, 4] disappeared.', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, global_position, agent_orientation, agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    observed_map = 'AAA\nF#F\nGAF'
    last_observed_map = 'AAA\nF#F\nFAF'
    agent_orientation = 0
    local_position = (1,1)
    global_position = (5, 5)
    expected_output = [('Observed that grass to grow apples appeared at position [6, 4].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, global_position, agent_orientation, agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    observed_map = 'AAA\nF#F\n2FF'
    last_observed_map = 'AAA\nF#F\nAGF'
    agent_orientation = 0
    local_position = (1,1)
    global_position = (5, 5)
    expected_output = [('Observed that agent agent3 took an apple from position [6, 4].', game_time), ('Observed that the grass at position [6, 5] disappeared.', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, global_position, agent_orientation, agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Detect that the attack was effective
    observed_map = 'FBF\nBBB\nBBB\nB#B\nFAF'
    last_observed_map = 'FFF\nFFF\nA1A\nF#F\nFAF'
    agent_orientation = 0
    local_position = (3,1)
    global_position = (5, 5)
    expected_output = [('I successfully attacked agent2 at position [4, 5].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, global_position, agent_orientation, agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Detect that someone was attacked by other agent
    observed_map = 'BFF\nFFF\nAFA\nF#F\nFAF'
    last_observed_map = '1FF\nFFF\nAFA\nF#F\nFAF'
    agent_orientation = 0
    local_position = (3,1)
    global_position = (5, 5)
    expected_output = [('agent2 was attacked at position [2, 4].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, global_position, agent_orientation, agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."


# Tests to verify that changes in state are detected correctly while the agent is moving over the map
def test_get_observed_changes_while_moving():
    # Detect that the agent took an apple
    game_time = '2021-09-30 12:00:00'
    observed_map = 'FFA\nA#A\nFFF'
    last_observed_map = 'AAA\nF#F\nAAF'
    agent_orientation = 0
    last_agent_orientation = 0
    local_position = (1,1)
    global_position = (4, 5)
    last_global_position = (5, 5)
    expected_output = [('I took an apple from position [4, 5].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, last_global_position, agent_orientation, last_agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Detect that another agent took an apple
    game_time = '2021-09-30 12:00:00'
    observed_map = 'FFA\nA#2\nFFF'
    last_observed_map = 'AAA\nF#F\nAAF'
    agent_orientation = 0
    last_agent_orientation = 0
    local_position = (1,1)
    global_position = (4, 5)
    last_global_position = (5, 5)
    expected_output = [('I took an apple from position [4, 5].', game_time), ('Observed that agent agent3 took an apple from position [4, 6].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, last_global_position, agent_orientation, last_agent_orientation, game_time,"Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Detect a change even if the agent changed orientation
    game_time = '2021-09-30 12:00:00'
    observed_map = 'AGF\nAAF\nF#F\nFFF'
    last_observed_map = 'AAA\nFFA\nF#G\nFFF'
    agent_orientation = 0
    last_agent_orientation = 3
    local_position = (2,1)
    global_position = (6, 7)
    last_global_position = (6, 7)
    expected_output = [('Observed that an apple grew at position [5, 7].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, last_global_position, agent_orientation, last_agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Detect a change even if the agent changed orientation
    game_time = '2021-09-30 12:00:00'
    observed_map = 'BBB\nBBG\nG#G\nFFF'
    last_observed_map = 'AAF\nFG2\nF#F\nFGG'
    agent_orientation = 2
    last_agent_orientation = 1
    local_position = (2,1)
    global_position = (10, 10)
    last_global_position = (10, 10)
    expected_output = [('agent3 was attacked at position [11, 11].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, last_global_position, agent_orientation, last_agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Detect a change even if the agent changed orientation and the observation window is square
    game_time = '2021-09-30 12:00:00'
    observed_map = 'BBBF\nBBGF\nG#GG\nFFFA'
    last_observed_map = 'AAFA\nFG2A\nF#FG\nFGGF'
    agent_orientation = 2
    last_agent_orientation = 1
    local_position = (2,1)
    global_position = (10, 10)
    last_global_position = (10, 10)
    expected_output = [('agent3 was attacked at position [11, 11].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, last_global_position, agent_orientation, last_agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Detect a change even if the agent changed orientation and the observation window is square
    game_time = '2021-09-30 12:00:00'
    observed_map = 'AGAF\nFFFA\nG#GA\nGFBB'
    last_observed_map = 'AAFA\nFG2A\nF#FG\nFGGF'
    agent_orientation = 0
    last_agent_orientation = 1
    local_position = (2,1)
    global_position = (10, 10)
    last_global_position = (10, 10)
    expected_output = [('agent3 was attacked at position [11, 11].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, last_global_position, agent_orientation, last_agent_orientation, game_time,  "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Detect a change even if the agent changed orientation and the observation window is square
    game_time = '2021-09-30 12:00:00'
    observed_map = 'AGAF\nAFAG\nG#GG\nAF1A'
    last_observed_map = 'AFGA\n1FAG\nG#GG\nGFA2'
    agent_orientation = 1
    last_agent_orientation = 3
    local_position = (2,1)
    global_position = (10, 10)
    last_global_position = (10, 10)
    expected_output = [('Observed that an apple grew at position [11, 11].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, last_global_position, agent_orientation, last_agent_orientation, game_time,  "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Detect a change even if the agent changed orientation and the observation window is square
    game_time = '2021-09-30 12:00:00'
    observed_map = 'AFGG\nGF#1\nAAFF\nAGGG'
    last_observed_map = 'GFFG\nA1#F\nAGGF\nFAAG'
    agent_orientation = 2
    last_agent_orientation = 0
    local_position = (1,2)
    global_position = (10, 10)
    last_global_position = (10, 10)
    expected_output = [('Observed that an apple grew at position [9, 11].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, last_global_position, agent_orientation, last_agent_orientation, game_time,  "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Detect no changes if there aren't any
    game_time = '2021-09-30 12:00:00'
    observed_map = 'WWWWWWWWWWW\nFFFFFFFFFFF\nFFFFFFFFFFF\nFFFFFFFFFFF\nFFFFFFFFFFF\nFFFFFFFFFFF\nFFFFFFFFFFF\nFFFFFFFFFAF\nFFFFFFFFAAA\nFFFFF#FAAAA\nFFFFFFFFAAA'
    last_observed_map = 'FFFFFFFFFFF\nFFFFFFFFFFF\nFFFFFFFFFFF\nFFFFFFFFFFF\nFFFFFFFFFFF\nFFFFFFFFFFF\nFFFFFFFFFAF\nFFFFFFFFAAA\nFFFFFFFAAAA\nFFFFF#FFAAA\nFFFFFFFFFAF'
    agent_orientation = 2
    last_agent_orientation = 2
    local_position = (9, 5)
    global_position = (8, 7)
    last_global_position = (7, 7)
    expected_output = []
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, last_global_position, agent_orientation, last_agent_orientation, game_time,  "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Detect no changes if there aren't any
    game_time = '2021-09-30 12:00:00'
    observed_map = '-----------\n-----------\nWWWWWWWWWWW\nAAAFFFFAFFF\nAAFFFFAAAFF\nAFFFFAAAAAF\nFFFFFFAAAFF\nFFFFFFFAFFF\nFFAFFFFFFFF\nFAAAF#FFFFF\nAAAAAFFFFFF'
    last_observed_map = '-----------\n-----------\nWWWWWWWWWWW\nAAFFFFAFFFF\nAFFFFAAAFFF\nFFFFAAAAAFF\nFFFFFAAAFFF\nFFFFFFAFFFF\nFAFFFFFFFFF\nAAAFF#FFFFF\nAAAAFFFFFFF'
    agent_orientation = 1
    last_agent_orientation = 1
    local_position = (9, 5)
    global_position = (6, 16)
    last_global_position = (7, 16)
    expected_output = []
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, last_global_position, agent_orientation, last_agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Detect a change while moving up when looking to the west
    game_time = '2021-09-30 12:00:00'
    observed_map = 'AAA\nAA1\nFAF\nF#F\nFFF'
    last_observed_map = 'AAA\nFAF\nFFF\nF#F\nFFF'
    agent_orientation = 3
    last_agent_orientation = 3
    local_position = (3, 1)
    global_position = (15, 4)
    last_global_position = (15, 5)
    expected_output = [('Observed that agent agent2 took an apple from position [14, 2].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, last_global_position, agent_orientation, last_agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Detect a change while moving right when looking to the east
    game_time = '2021-09-30 12:00:00'
    observed_map = 'AAA\nAFF\n#FF\nAAG'
    last_observed_map = 'GAA\nFGF\n#FF\nFAA'
    agent_orientation = 1
    last_agent_orientation = 1
    local_position = (2, 0)
    global_position = (12, 7)
    last_global_position = (11, 7)
    expected_output = [('Observed that an apple grew at position [12, 8].', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, last_global_position, agent_orientation, last_agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."

    # Detect a change while moving left when looking to the south
    game_time = '2021-09-30 12:00:00'
    observed_map = 'AFF\nG#G\nFFF\nGFF'
    last_observed_map = 'FFA\nG#F\nFFF\nGFF'
    agent_orientation = 2
    last_agent_orientation = 2
    local_position = (1, 1)
    global_position = (12, 15)
    last_global_position = (12, 14)
    expected_output = [('Observed that the grass at position [10, 15] disappeared.', game_time)]
    observed_changes = obs_gen.get_observed_changes(observed_map, last_observed_map, local_position, global_position, last_global_position, agent_orientation, last_agent_orientation, game_time, "Juan")
    assert sorted(observed_changes) == sorted(expected_output), f"Expected {expected_output}, got {observed_changes}."