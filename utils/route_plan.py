


from collections import deque
def get_shortest_valid_route(matriz: list[list[str]], start: tuple[int, int], end: tuple[int, int], 
                             invalid_symbols: list[str] = ['W','$'], orientation:int = 0):
    """Gets the shortest valid route between two points in a matrix.

    Args:
        matriz (list[list[str]]): Matrix.
        start (tuple[int, int]): Start point.
        end (tuple[int, int]): End point.
        invalid_symbols (list[str], optional): Invalid symbols. Defaults to ['W','$'].
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
        visited = [[False for _ in range(len(matriz[0]))] for _ in range(len(matriz))]
        prev = [[None for _ in range(len(matriz[0]))] for _ in range(len(matriz))]
        
        queue = deque([start])
        visited[start[0]][start[1]] = True
        
        while queue:
            x, y = queue.popleft()
            
            for d in range(4):
                nx, ny = x + dx[d], y + dy[d]
                
                if 0 <= nx < len(matriz) and 0 <= ny < len(matriz[0]) and not visited[nx][ny]:
                    if matriz[nx][ny] not in invalid_symbols:
                        queue.append((nx, ny))
                        visited[nx][ny] = True
                        prev[nx][ny] = (x, y, directions[d])
        
        path = []
        at = end
        while at != start:
            if prev[at[0]][at[1]] is None:
                return None  # No hay camino
            x, y, d = prev[at[0]][at[1]]
            path.append(d)
            at = (x, y)
        path.reverse()
        
        return path

    return bfs(start, end)
