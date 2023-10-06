import logging
import os
from queue import Queue
from utils.route_plan import get_shortest_valid_route
import re
from utils.queue_utils import queue_from_list, new_empty_queue


class SpatialMemory:
    """
    Class for the spacial memory. Memories are stored in a dictionary.
    """

    def __init__ (self, scenario_map: list[str], scenario_obstacles: list[str] = ['W']  ) -> None:
        """
        Initializes the spacial memory.

        Args:
            scenario_map (str, optional): Real map of the environment, in ascci format, rows separated by '\n'. 
            scenario_obstacles (list[str], optional): Obstacles of the scenario. Defaults to ['W'] for Walls.
        """
        self.logger = logging.getLogger(__name__)
        self.scenario_map = scenario_map.split('\n')[1:-1]
        #self.exploredMap = ["$"*mapSize[1] for _ in range(mapSize[0])]
        self.explored_map = self.scenario_map # CHANGE THIS TO LINE ABOVE
        print(self.explored_map)
        self.position = (-1,-1) # Inits the position of the agent
        self.orientation = 0
        self.mapSize = (len(self.scenario_map), len(self.scenario_map[0]))
        self.scenario_obstacles = scenario_obstacles 

    def updatePosition(self, new_position: tuple, orientation:int) -> None:
        """
        Updates the current position of the agent.

        Args:
            new_position (tuple): New position of the agent.
            orientation (int): New orientation of the agent.
        """
        self.position = new_position
        self.orientation = orientation


    def updateExploredMap(self, pos: tuple) -> None:
        """
        Updates the map with a new object.

        Args:
            pos (tuple): Position of the new object.
        """
        self.explored_map[pos[0]][pos[1]] = self.scenario_map[pos[0]][pos[1]]



    def find_route_to_position(self, position_end: tuple, orientation:int) -> Queue(str):
        """
        Finds the shortest route to a position.

        Args:
            position_end (tuple): End position of the route.
            orientation (int): Orientation of the agent. 0: North, 1: East, 2: South, 3: West.

        Returns:
            Queue(str): Steps sequence for the route.
        """
        logging.info(f'Finding route from {self.position} to {position_end}')
        route = get_shortest_valid_route(self.explored_map, self.position, position_end, invalid_symbols=self.scenario_obstacles, orientation=orientation)
        return queue_from_list(route)
    


    def get_steps_sequence(self, current_action) -> Queue(str):
        """
        Returns a new steps sequence for the current action.

        Args:
            current_action (str): Current action of the agent.

        Returns:
            Queue(str): Steps sequence for the current action.
        """

        if current_action.startswith(('grab ', 'go to ')): # TODO : Change this according to the valid actions.
            end_position = self.get_position_from_action(current_action)
            sequence_steps = self.find_route_to_position(end_position, self.orientation)
            logging.info(f'The steps sequence is: {list(sequence_steps.queue)}')

            return sequence_steps
        
        elif current_action.startswith('attack '):
            sequence_steps = new_empty_queue()
            sequence_steps.put('attack')
            return sequence_steps
        
        return new_empty_queue() # DELETE THIS LINE




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
        except AttributeError:
            logging.error(f'Action {action} does not contain a position')
            raise ValueError(f'Action {action} does not contain a position')
        
        return  (int(x), int(y))