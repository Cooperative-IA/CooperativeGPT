from game_environment.scene_descriptor.observations_generator import ObservationsGenerator
from CooperativeGPT.game_environment.substrates.python.commons_harvest_open import ASCII_MAP
from agent.memory_structures.spatial_memory import SpatialMemory

spatial_memory = SpatialMemory(ASCII_MAP)
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

    print("All test cases pass")