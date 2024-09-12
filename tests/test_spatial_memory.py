from game_environment.scene_descriptor.observations_generator import ObservationsGenerator
from game_environment.substrates.python.commons_harvest_open import ASCII_MAP
from agent.memory_structures.spatial_memory import SpatialMemory
from unittest.mock import patch

spatial_memory = SpatialMemory(ASCII_MAP, '0')
orientation_map = {0: 'North', 1: 'East', 2: 'South', 3: 'West'}

def test_get_global_position():
    spatial_memory.position = (10, 5)

    # Test case 1: agent_orientation = 0
    el_local_pos = (5, 3)
    self_local_pos = (0, 3)
    spatial_memory.orientation = 0
    expected_output = (15, 5)
    element_global_pos = spatial_memory.get_global_position(el_local_pos, self_local_pos)
    assert element_global_pos == expected_output, f'Expected {expected_output}, got {element_global_pos}.Failed with agent_orientation = {spatial_memory.orientation}: {orientation_map[spatial_memory.orientation]}'

    # Test case 2: agent_orientation = 1
    el_local_pos = (0, 0)
    self_local_pos = (0, 5)
    spatial_memory.orientation = 1
    expected_output = (5, 5)
    element_global_pos = spatial_memory.get_global_position(el_local_pos, self_local_pos)
    assert element_global_pos == expected_output, f'Expected {expected_output}, got {element_global_pos}.Failed with agent_orientation = {spatial_memory.orientation}: {orientation_map[spatial_memory.orientation]}'

    # Test case 3: agent_orientation = 2
    el_local_pos = (2, 3)
    self_local_pos = (7, 3)
    spatial_memory.orientation = 2
    expected_output = (15, 5)
    element_global_pos = spatial_memory.get_global_position(el_local_pos, self_local_pos)
    assert element_global_pos == expected_output, f'Expected {expected_output}, got {element_global_pos}.Failed with agent_orientation = {spatial_memory.orientation}: {orientation_map[spatial_memory.orientation]}'

    # Test case 4: agent_orientation = 3
    el_local_pos = (7, 9)
    self_local_pos = (7, 4)
    spatial_memory.orientation = 3
    expected_output = (5, 5)
    element_global_pos = spatial_memory.get_global_position(el_local_pos, self_local_pos)
    assert element_global_pos == expected_output, f'Expected {expected_output}, got {element_global_pos}.Failed with agent_orientation = {spatial_memory.orientation}: {orientation_map[spatial_memory.orientation]}'

    el_local_pos = (1, 9)
    self_local_pos = (9, 5)
    spatial_memory.position = (7, 21)
    spatial_memory.orientation = 3
    expected_output = (3, 13)
    element_global_pos = spatial_memory.get_global_position(el_local_pos, self_local_pos)
    assert element_global_pos == expected_output, f'Expected {expected_output}, got {element_global_pos}.Failed with agent_orientation = {spatial_memory.orientation}: {orientation_map[spatial_memory.orientation]}'

    # Test case 4: agent_orientation = 3 and the global pos of a wall
    el_local_pos = (7, 0)
    self_local_pos = (9, 5)
    spatial_memory.position = (15, 15)
    spatial_memory.orientation = 2
    expected_output = (17,20)
    element_global_pos = spatial_memory.get_global_position(el_local_pos, self_local_pos)
    assert  element_global_pos == expected_output, f'Expected {expected_output}, got {element_global_pos}.Failed with agent_orientation = {spatial_memory.orientation}: {orientation_map[spatial_memory.orientation]}'

@patch('agent.memory_structures.spatial_memory.shortest_valid_route')
def test_find_route_to_position(mock_shortest_valid_route):
    spatial_memory.position = (1, 1)
    spatial_memory.orientation = 0


    # Test case 1: Position is the same as the current one
    result = spatial_memory.find_route_to_position("WWWW\nW..W\nW..W\nWWWW", (1, 1), 0)
    assert list(result.queue) == ['stay put'], f'Expected ["stay put"], got {list(result.queue)}'

    # Test case 2: Normal route
    mock_shortest_valid_route.return_value = ['move down', 'move right']
    result = spatial_memory.find_route_to_position("WWWW\nW..W\nW..W\nWWWW", (2, 2), 0)
    expected_route = ['move down', 'move right', 'turn right']
    assert list(result.queue) == expected_route, f'Expected {expected_route}, got {list(result.queue)}'

    # Test case 3: End should end facing north, but it is already facing north. So, it should just move up without turning
    spatial_memory.position = (2, 1)
    mock_shortest_valid_route.return_value = ['move up']
    result = spatial_memory.find_route_to_position("WWWW\nW..W\nW..W\nWWWW", (1, 1), 0)
    expected_route = ['move up']
    assert list(result.queue) == expected_route, f'Expected {expected_route}, got {list(result.queue)}'
