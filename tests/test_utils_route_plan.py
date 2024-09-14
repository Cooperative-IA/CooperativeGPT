from utils.route_plan import get_shortest_valid_route

def test_get_shortest_valid_route_no_obstacles():
    matrix = [
        ['.', '.', '.'],
        ['.', '.', '.'],
        ['.', '.', '.']
    ]
    start = (0, 0)
    end = (2, 2)
    invalid_symbols = []
    expected_route = ['move right', 'move right', 'move down', 'move down']
    assert get_shortest_valid_route(matrix, start, end, invalid_symbols) == expected_route

def test_get_shortest_valid_route_with_obstacles():
    matrix = [
        ['.', 'X', '.'],
        ['.', 'X', '.'],
        ['.', '.', '.']
    ]
    start = (0, 0)
    end = (2, 2)
    invalid_symbols = ['X']
    expected_route = ['move down', 'move down', 'move right', 'move right']
    assert get_shortest_valid_route(matrix, start, end, invalid_symbols) == expected_route

def test_get_shortest_valid_route_no_path():
    matrix = [
        ['.', 'X', '.'],
        ['.', 'X', '.'],
        ['.', 'X', '.']
    ]
    start = (0, 0)
    end = (2, 2)
    invalid_symbols = ['X']
    expected_route = []
    assert get_shortest_valid_route(matrix, start, end, invalid_symbols) == expected_route

def test_get_shortest_valid_route_with_orientation():
    matrix = [
        ['.', '.', '.'],
        ['.', '.', '.'],
        ['.', '.', '.']
    ]
    start = (0, 0)
    end = (2, 2)
    invalid_symbols = []
    orientation = 1  # East
    expected_route = ['move up', 'move up', 'move right', 'move right']
    assert get_shortest_valid_route(matrix, start, end, invalid_symbols, orientation) == expected_route

def test_get_shortest_valid_route_with_passable_obstacles():
    matrix = [
        ['.', 'P', '.'],
        ['.', 'P', '.'],
        ['.', '.', '.']
    ]
    start = (0, 0)
    end = (2, 2)
    invalid_symbols = ['X']
    expected_route = ['move right', 'move right', 'move down', 'move down']
    assert get_shortest_valid_route(matrix, start, end, invalid_symbols) == expected_route

def test_get_shortest_valid_route_when_destination_is_an_obstacle():
    matrix = [
        ['.', 'P', '.'],
        ['.', 'P', '.'],
        ['.', '.', 'X']
    ]
    start = (0, 0)
    end = (2, 2)
    invalid_symbols = ['X']
    expected_route = ['move right', 'move right', 'move down', 'move down']
    assert get_shortest_valid_route(matrix, start, end, invalid_symbols) == expected_route