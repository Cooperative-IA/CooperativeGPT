import logging
import os
from queue import Queue
from utils.route_plan import get_shortest_valid_route
import re
from utils.queue_utils import *

realMap = [
    "WWWWWWWWWWWWWWWWWWWWWWWW",
    "WAAA    A      A    AAAW",
    "WAA    AAA    AAA    AAW",
    "WA    AAGAA  AAAAA    AW",
    "W      AAA    AAA      W",
    "W       A      A       W",
    "W  A                A  W",
    "W AAA  Q        Q  AAA W",
    "WAAAAA            AAAAAW",
    "W AAA              AAA W",
    "W  A                A  W",
    "W                      W",
    "W                      W",
    "W                      W",
    "W  PPPPPPPPPPPPPPPPPP  W",
    "W PPPPPPPPPPPPPPPPPPPP W",
    "WPPPPPPPPPPPPPPPPPPPPPPW",
    "WWWWWWWWWWWWWWWWWWWWWWWW"
] # DELETE THIS MAP



class SpatialMemory:
    """
    Class for the spacial memory. Memories are stored in a dictionary.
    """

    def __init__ (self, initial_pos:tuple, real_map: list[str] = realMap) -> None:
        """
        Initializes the spacial memory.
        """
        self.logger = logging.getLogger(__name__)
        self.realMap = real_map
        #self.exploredMap = ["$"*mapSize[1] for _ in range(mapSize[0])]
        self.exploredMap = real_map # CHANGE THIS TO LINE ABOVE
        self.position = initial_pos
        self.orientation = 0
        self.mapSize = (len(real_map), len(real_map[0]))

    def updatePosition(self, new_position: tuple, orientation:int) -> None:
        """
        Updates the current position of the agent.
        """
        self.position = new_position
        self.orientation = orientation


    def updateExploredMap(self, pos: tuple) -> None:
        """
        Updates the map with a new object.
        """
        self.exploredMap[pos[0]][pos[1]] = self.realMap[pos[0]][pos[1]]



    def find_route_to_position(self, position_end: tuple) -> Queue(str):
        """
        Finds the shortest route to a position.
        """
        route = get_shortest_valid_route(self.exploredMap, self.position, position_end, invalid_symbols=['W','$'])
        return queue_from_list(route)
    


    def get_steps_sequence(self, current_action) -> Queue(str):
        """
        Returns a new steps sequence for the current action.

        Args:
            current_action (str): Current action of the agent.

        Returns:
            Queue(str): Steps sequence for the current action.
        """

        if current_action.startswith(('grab ', 'go to ')):
            end_position = self.get_position_from_action(current_action)
            sequence_steps = self.find_route_to_position(end_position)
            logging.info(f' grabbing an apple, the steps sequence is: {list(sequence_steps.queue)}')

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
        position_str = re.search(r'\((.*?)\)', action).group(1)
        # Splits the substring into a tuple
        position = tuple(map(int, position_str.split(',')))
        return position