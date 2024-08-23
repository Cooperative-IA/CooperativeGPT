import logging
from queue import Queue
import random
from utils.route_plan import get_shortest_valid_route
import re
from utils.queue_utils import queue_from_list, new_empty_queue
from utils.math import manhattan_distance
from utils.logging import CustomAdapter

class SpatialMemory:
    """
    Class for the spacial memory. Memories are stored in a dictionary.
    """

    def __init__ (self, scenario_map: str, scenario_obstacles: list[str] = ['W']  ) -> None:
        """
        Initializes the spacial memory.

        Args:
            scenario_map (str): Real map of the environment, in ascci format, rows separated by '\n'. 
            scenario_obstacles (list[str], optional): Obstacles of the scenario. Defaults to ['W'] for Walls.
        """
        self.logger = logging.getLogger(__name__)
        self.logger = CustomAdapter(self.logger)
        self.scenario_map = scenario_map.split('\n')[1:-1]
        self.position = (-1,-1) # Inits the position of the agent
        self.orientation = 0
        self.current_observed_map = None
        self.mapSize = (len(self.scenario_map), len(self.scenario_map[0]))
        self.scenario_obstacles = scenario_obstacles 
        self.explored_map = ["?"*self.mapSize[1] for _ in range(self.mapSize[0])]
        
    def update_current_scene(self, new_position: tuple, orientation:int, current_observed_map:str) -> None:
        """
        Updates the spatial information of the agent.

        Args:
            new_position (tuple): New position of the agent.
            orientation (int): New orientation of the agent.
            current_observed_map (str): Current observed map.

        """
        
        self.position = new_position
        self.orientation = orientation
        self.current_observed_map = current_observed_map
        
        # By using the current observed map, we can update the explored map
        self.update_explored_map()


    def update_explored_map(self) -> None:
        """
        Updates the map with a new current map.
        """
        for i, row in enumerate(self.current_observed_map.split('\n')):
            for j, element in enumerate(row):
                if element != '-':
                    try:
                        global_position = self.get_global_position((i,j), self.get_local_self_position())
                        if self.explored_map[global_position[0]][global_position[1]] == '?':
                            # Replaces the char of the string global_position[0] at that is in the list of strings
                            self.explored_map[global_position[0]] = self.explored_map[global_position[0]][:global_position[1]] + element + self.explored_map[global_position[0]][global_position[1]+1:]

                    except:
                        self.logger.error(f'Error updating the explored map with the element {element} {(i,j)} at position {global_position}')
                        continue
    def get_percentage_explored(self) -> float:
        """
        Returns the percentage of the map that has been explored.

        Returns:
            float: Percentage of the map that has been explored.
        """
        n_explored = sum([row.count('?') for row in self.explored_map])
        percentage = (1 - n_explored / (self.mapSize[0] * self.mapSize[1])) * 100
        return float("{:.2f}".format(percentage))

    def find_route_to_position(self, position_end: tuple, orientation:int, return_list: bool = False, include_last_pos=True ) -> Queue[str] | list[str]:
        """
        Finds the shortest route to a position.

        Args:
            position_end (tuple): End position of the route.
            orientation (int): Orientation of the agent. 0: North, 1: East, 2: South, 3: West.
            return_list (bool, optional): If True, returns a list instead of a queue. Defaults to False.
            include_last_pos (bool, optional): If True, includes the last position of the route. Defaults to True.
            
        Returns:
            Queue(str): Steps sequence for the route.
        """
        self.logger.info(f'Finding route from {self.scenario_map} to {position_end}')
        # If the position is the same as the current one, return an empty queue
        if self.position == position_end:
            return queue_from_list(['stay put'])
        route = get_shortest_valid_route(self.scenario_map, self.position, position_end, invalid_symbols=self.scenario_obstacles, orientation=orientation)


        if not include_last_pos and len(route) > 0:
            route = route[:-2] + route[-1:]
        
        # Adds a change on orientation on the last step of the route
        if len(route) > 0:
            new_orientation = 'turn '+ route[-1].split(' ')[1]
            # If the new orientation is the same as the current one, we do not need to change it, if down we need to turn twice
            if new_orientation == 'turn down':
                route.append('turn right')
                route.append('turn right')
            else: 
                route.append(new_orientation)


        if return_list:
            return route
        return queue_from_list(route)
    
    def is_position_valid(self, position: tuple) -> bool:
        """
        Checks if a position is valid.

        Args:
            position (tuple): Position to check.

        Returns:
            bool: True if the position is valid, False otherwise.
        """
        if position[0] < 0 or position[0] >= self.mapSize[0] or position[1] < 0 or position[1] >= self.mapSize[1]:
            return False
        
        if self.scenario_map[position[0]][position[1]] in self.scenario_obstacles:
            return False
        
        return True
        



    def get_steps_sequence(self, current_action) -> Queue[str]:
        """
        Returns a new steps sequence for the current action.

        Args:
            current_action (str): Current action of the agent.

        Returns:
            Queue(str): Steps sequence for the current action.
        """

        sequence_steps = new_empty_queue()

        if current_action.startswith(('grab ')) or current_action.startswith(('consume ')) or "go to " in current_action:
            end_position = self.get_position_from_action(current_action)
            sequence_steps = self.find_route_to_position(end_position, self.orientation) 

        elif current_action.startswith('attack ') or current_action.startswith('immobilize '):
            agent2attack_pos = self.get_position_from_action(current_action)
            sequence_steps = self.find_route_to_position(agent2attack_pos, self.orientation, include_last_pos=False)
            sequence_steps.put('attack')

        elif current_action.startswith('clean '):
            dirt_pos = self.get_position_from_action(current_action)
            sequence_steps = self.find_route_to_position(dirt_pos, self.orientation, include_last_pos=False)
            sequence_steps.put('clean')

        elif current_action.startswith('explore'):
            explore_pos = self.get_position_from_action(current_action)
            if not self.is_position_valid(explore_pos):
                explore_pos = None
            sequence_steps = self.generate_explore_sequence(explore_pos)
            
        elif current_action.startswith('avoid consuming') or current_action.startswith('stay put'):
            sequence_steps.put('stay put')
    
        self.logger.info(f'The steps sequence is: {list(sequence_steps.queue)}')
        return sequence_steps
        




    def get_position_from_action(self, action: str) -> tuple:
        """
        Returns the position of the object in the action.

        Args:
            action (str): Action of the agent.

        Returns:
            tuple: Position of the object in the action.
        """
        # Finds the substring "(x,y)" in the action string
        try :
            pattern = r'\((\d+),\s*(\d+)\)|\[(\d+),\s*(\d+)\]'
            matches = re.findall(pattern, action)
            for match in matches:
                x, y = match[0] or match[2], match[1] or match[3]
            
            return  (int(x), int(y))
        except :
            self.logger.error(f'Action {action} does not contain a position')
            return (-1,-1)
        
    
    def sort_observations_by_distance(self, observations: list[str]) -> list[str]:
        """
        Sorts the observations by distance to the agent in ascending order.

        Args:
            observations (list[str]): List of observations.

        Returns:
            list[str]: Sorted list of observations.
        """

        observations_positions = [self.get_position_from_action(observation) for observation in observations]
        observations_distances = [manhattan_distance(self.position, position) for position in observations_positions]

        return sorted(observations, key=lambda x: observations_distances[observations.index(x)])
    
    def get_global_position(self, local_dest_pos: tuple[int, int], local_self_pos: tuple[int, int]) -> tuple[int, int]:
        """Get the global position of an element given its local position on the observed map.

        Args:
            local_dest_pos (tuple[int, int]): Local position of the destination on the observed map.
            local_self_pos (tuple[int, int]): Local position of the agent on the observed map.

        Returns:
            tuple[int, int]: Global position of the element.
        """
        # North
        if self.orientation == 0:
            element_global = (local_dest_pos[0] - local_self_pos[0]) + self.position[0],\
                                (local_dest_pos[1] - local_self_pos[1]) + self.position[1]
        # East
        elif self.orientation == 1:
            element_global = (local_dest_pos[1] - local_self_pos[1]) + self.position[0],\
                             -1 * (local_dest_pos[0] - local_self_pos[0]) + self.position[1]
        # South
        elif self.orientation == 2:
            element_global = -1 * (local_dest_pos[0] - local_self_pos[0]) + self.position[0],\
                             -1 * (local_dest_pos[1] - local_self_pos[1]) + self.position[1]
        # West
        elif self.orientation == 3:
            element_global =  -1 * (local_dest_pos[1] - local_self_pos[1]) + self.position[0],\
                                (local_dest_pos[0] - local_self_pos[0])+ self.position[1]

        return element_global
    
    def get_local_self_position(self) -> tuple[int, int]:
        """Get the local position of the agent on the observed map. Yhe agent is represented as # on the observed map.

        Returns:
            tuple[int, int]: Local position of the agent on the observed map.
        """
        # TODO  retrieve from the map initial config.
        #observed_map = self.current_observed_map.split('\n')[1:-1]
        #for i, row in enumerate(observed_map):
        #    if '#' in row:
        #        return (i, row.index('#'))
        return (9,5)

    def generate_explore_sequence(self, position: str = None) -> Queue[str]:
        """
        Generates a sequence of steps to explore the map.
        Takes a random position from the current_observed map
        then finds the shortest route to that position and returns the steps sequence.

        Args:
            position (str, optional): Position to explore. Defaults to None.

        Returns:
            Queue[str]: Sequence of steps to explore the map.
        """
        if position is not None:
            destination = position
        else:
            # Take a random position from the current_observed map
            current_map_matrix = self.current_observed_map.split('\n')

            # Finds the bounds of the current observed map
            # TODO change that function to utils module
            min_row, min_col, max_row, max_col = self.get_bounds_current_map(current_map_matrix)
            random_row = random.randint(min_row, max_row)
            random_col = random.randint(min_col, max_col)
            # Is the destination a valid position? '-' means that the position does not exist on the map
            while current_map_matrix[random_row][random_col] in ['W', '$', '-', '#']:
                random_row = random.randint(min_row, max_row)
                random_col = random.randint(min_col, max_col)
            
            # Get the global position of the destination
            agent_local_pos = self.get_local_self_position()
            destination = self.get_global_position((random_row, random_col), agent_local_pos)

        # Finds the shortest route to that position
        self.logger.info(f"Finding route to {destination} from {self.position} with orientation {self.orientation} using the map {self.scenario_map}")
        sequence_steps = self.find_route_to_position(destination, self.orientation)
        if sequence_steps.qsize() < 1:
            self.logger.error(f'Could not find a route from {position} to the destination {destination}')
            return new_empty_queue()

                
        self.logger.info(f'The steps sequence is: {list(sequence_steps.queue)}')

        return sequence_steps


    def get_bounds_current_map(self, current_map_matrix : list[str]) -> tuple[int, int, int, int]:
        """
        Finds the bounds of the current observed map.
        
        Args:
            current_map_matrix (list[str]): Current observed map.
        
        Returns:
            tuple[int, int, int, int]: Bounds of the current observed map.
        """

        found_row_min, found_col_min = False, False 
        min_row, min_col = 0, 0
        max_row, max_col  =  len(current_map_matrix) - 1, len(current_map_matrix[0]) - 1
        for i in range(len(current_map_matrix)):
            row = current_map_matrix[i]
            if row == '-'*len(row):
                if not found_row_min:
                    min_row += 1
                else: 
                    max_row = i
                    break
            elif not found_col_min:
                found_row_min = True
                found_col_max = False
                # Now we need to find the min and max col               
                for j in range(len(row)):
                    if row[j] == '-':
                        if not found_col_min:
                            min_col += 1
                        elif not found_col_max:
                            max_col = j
                            found_col_max = True
                    else:
                        found_col_min = True
        return min_row, min_col, max_row, max_col
    
    def get_orientation_name(self) -> str:
        """
        Returns the name of the current orientation of the agent.

        Returns:
            str: Name of the orientation.
        """
        orientation = self.orientation
        
        if orientation == 0:
            return 'North'
        elif orientation == 1:
            return 'East'
        elif orientation == 2:
            return 'South'
        elif orientation == 3:
            return 'West'
        else:
            raise Exception(f'Orientation {orientation} is not valid')
