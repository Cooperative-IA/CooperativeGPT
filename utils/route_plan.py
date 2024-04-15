


from collections import deque
def get_shortest_valid_route(matrix: list[list[str]], start: tuple[int, int], end: tuple[int, int], 
                             invalid_symbols: list[str] = ['W','$'], orientation:int = 0):
    """Gets the shortest valid route between two points in a matrix.

    Args:
        matrix (list[list[str]]): Matrix.
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

from collections import deque
import heapq  # Se utiliza para la cola de prioridades en la búsqueda de Dijkstra

def get_shortest_valid_route_snowartz(matrix: list[list[str]], start: tuple[int, int], end: tuple[int, int], 
                             invalid_symbols: list[str] = ['W', '$'], optional_obstacles: list[str] = [], 
                             orientation: int = 0, reach_end: bool = True) -> list[str]:
    dx = [-1, 0, 1, 0]
    dy = [0, 1, 0, -1]
    directions = ['move up', 'move right', 'move down', 'move left']
    orientation = 1 if orientation == 3 else 3 if orientation == 1 else orientation
    directions = directions[orientation:] + directions[:orientation]
    
    def is_valid(x, y, avoid_optionals=True):
        if 0 <= x < len(matrix) and 0 <= y < len(matrix[0]):
            if matrix[x][y] in invalid_symbols or (avoid_optionals and matrix[x][y] in optional_obstacles):
                return False
            return True
        return False

    def get_cost(x, y):
        return 10 if matrix[x][y] in optional_obstacles else 1  # Costo más alto para los obstáculos opcionales

    def dijkstra(start, end, avoid_optionals):
        pq = []  # Cola de prioridades para Dijkstra
        heapq.heappush(pq, (0, 0, start))  # (costo, distancia al destino, punto)
        prev = {start: None}
        costs = {start: 0}
        closest_point = start
        closest_path_cost = float('inf')

        while pq:
            cost, _, (x, y) = heapq.heappop(pq)
            
            # Actualizar el punto más cercano si es necesario
            distance_to_end = abs(end[0] - x) + abs(end[1] - y)
            if distance_to_end < abs(end[0] - closest_point[0]) + abs(end[1] - closest_point[1]) or \
               (distance_to_end == abs(end[0] - closest_point[0]) + abs(end[1] - closest_point[1]) and cost < closest_path_cost):
                closest_point = (x, y)
                closest_path_cost = cost

            if (x, y) == end:  # Si se alcanza el destino, detener la búsqueda
                break

            for d in range(4):
                nx, ny = x + dx[d], y + dy[d]
                if is_valid(nx, ny, avoid_optionals):
                    next_cost = cost + get_cost(nx, ny)
                    next_distance_to_end = abs(end[0] - nx) + abs(end[1] - ny)
                    if (nx, ny) not in costs or next_cost < costs[(nx, ny)]:
                        costs[(nx, ny)] = next_cost
                        heapq.heappush(pq, (next_cost, next_distance_to_end, (nx, ny)))
                        prev[(nx, ny)] = (x, y, directions[d])

        path = []
        at = closest_point
        while at != start:
            if at not in prev:
                return []  # No hay ruta válida
            x, y, d = prev[at]
            path.append(d)
            at = (x, y)
        path.reverse()
        return path, end in costs

    # Primero intenta encontrar una ruta evitando todos los obstáculos
    path, reached_end = dijkstra(start, end, avoid_optionals=True)
    if not reached_end:
        if reach_end:
            # Si reach_end es True y el destino no se alcanzó, intenta de nuevo sin evitar los obstáculos opcionales
            path, _ = dijkstra(start, end, avoid_optionals=False)
        # Si reach_end es False, ya se tiene la ruta más corta al punto más cercano

    return path