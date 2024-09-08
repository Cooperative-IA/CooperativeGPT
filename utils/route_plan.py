


from collections import deque
from typing import Dict

def shortest_valid_route(matrix: list[list[str]], start: tuple[int, int], end: tuple[int, int],
                            scenario_obstacles: Dict[str, list], orientation:int = 0):
    """ 
    This function will do a call to the function get_shortest_valid_route with the same parameters,
    but at the first time it will send the parameter invalid_symbols as a list of the combination of the two lists 
    in scenario_obstacles (impassable_obstacles + passable_obstacles). 
    If the first call returns an empty list, it will return the result of the second call with the parameter invalid_symbols
    as only the list of impassable_obstacles.
    
    Args:
        matrix (list[list[str]]): Matrix.
        start (tuple[int, int]): Start point.
        end (tuple[int, int]): End point.
        invalid_symbols (Dict[str, list]): Invalid symbols. Contains two lists, impassable_obstacles and passable_obstacles.
        orientation (int, optional): Orientation of the agent. 0: North, 1: East, 2: South, 3: West. Defaults to 0.
    Returns:
        list[str]: Shortest valid route.
    """
    invalid_symbols = scenario_obstacles['impassable_obstacles'] + scenario_obstacles['passable_obstacles']
    route = get_shortest_valid_route(matrix, start, end, invalid_symbols, orientation)
    if route:
        return route
    else:
        possible_route = get_shortest_valid_route(matrix, start, end, scenario_obstacles['impassable_obstacles'], orientation)
        # Now, by using the possible_route, we will make inverse moves since the end_position, to try to find a valid route by calling
        # with both lists of invalid_symbols. If we find a valid route, we will return it.
        # If we don't find a valid route, we will return the possible_route.
        # At the end, we will append the removed moves from the possible_route to the final route.
        if possible_route:
            #Iterates the possible_route in reverse order
            new_end_position = end
            final_movements_to_add = []
            for  move in  possible_route[::-1]:
                new_end_position = inverse_move_in_grid(new_end_position, move, orientation)
                #Append it at the beginning of the list
                final_movements_to_add.insert(0, move)
                route = get_shortest_valid_route(matrix, start, new_end_position, invalid_symbols, orientation)
                if route:
                    return route + final_movements_to_add
        return possible_route

def get_shortest_valid_route(matrix: list[list[str]], start: tuple[int, int], end: tuple[int, int], 
                             invalid_symbols: list[str], orientation:int = 0):
    """Gets the shortest valid route between two points in a matrix.

    Args:
        matrix (list[list[str]]): Matrix.
        start (tuple[int, int]): Start point.
        end (tuple[int, int]): End point.
        invalid_symbols (list[str]): Invalid symbols.
        orientation (int, optional): Orientation of the agent. 0: North, 1: East, 2: South, 3: West. Defaults to 0.

    Returns:
        list[str]: Shortest valid route.
    """
    dx = [-1, 0, 1, 0]
    dy = [0, 1, 0, -1]
    directions = ['move up', 'move right', 'move down', 'move left']
    #Rotate directions according to the orientation of the agent
    orientation = 1 if orientation == 3 else 3 if orientation == 1 else orientation # Changes 1 to 3 and 3 to 1 (right and left)
    directions = directions[orientation:] + directions[:orientation]
    
    def bfs(start, end):
        visited = [[False for _ in range(len(matrix[0]))] for _ in range(len(matrix))]
        prev = [[None for _ in range(len(matrix[0]))] for _ in range(len(matrix))]
        
        queue = deque([start])
        visited[start[0]][start[1]] = True
        
        while queue:
            x, y = queue.popleft()
            
            for d in range(4):
                nx, ny = x + dx[d], y + dy[d]
                
                if 0 <= nx < len(matrix) and 0 <= ny < len(matrix[0]) and not visited[nx][ny]:
                    if matrix[nx][ny] not in invalid_symbols:
                        queue.append((nx, ny))
                        visited[nx][ny] = True
                        prev[nx][ny] = (x, y, directions[d])
        
        path = []
        at = end
        while at != start:
            if prev[at[0]][at[1]] is None:
                return []  # No hay camino
            x, y, d = prev[at[0]][at[1]]
            path.append(d)
            at = (x, y)
        path.reverse()
        
        return path

    return bfs(start, end)


def inverse_move_in_grid(end_position: tuple[int, int], move: str, orientation:int):
    """Gets the inverse move in a grid.

    Args:
        end_position (tuple[int, int]): End position.
        move (str): Move.

    Returns:
        tuple[int, int]: Inverse move.
    """
    dx = [1, 0, -1, 0]
    dy = [0, -1, 0, 1]    
    
    directions = ['move up', 'move right', 'move down', 'move left']
    #Rotate directions according to the orientation of the agent
    orientation = 1 if orientation == 3 else 3 if orientation == 1 else orientation # Changes 1 to 3 and 3 to 1 (right and left)
    directions = directions[orientation:] + directions[:orientation]
    
    d = directions.index(move)
    return end_position[0] + dx[d], end_position[1] + dy[d]