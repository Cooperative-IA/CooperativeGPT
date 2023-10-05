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
        self.mapSize = (len(real_map), len(real_map[0]))

    def updatePosition(self, new_position: tuple) -> None:
        """
        Updates the current position of the agent.
        """
        self.position = new_position


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
    


    def get_steps_sequence(self, current_action) -> int:
        """
        Returns a new se
        """

        if current_action.startswith('grab apple'):
            end_position = self.get_position_from_action(current_action)
            gameloop = self.find_route_to_position(end_position)
            logging.info(f' grabbing an apple, the steps sequence is: {list(gameloop.queue)}')

            return gameloop
        
        else: # DELETE THIS ELSE
            end_position = (12,8)
            gameloop = self.find_route_to_position(end_position)
            logging.info(f'NOT an apple, the sequence  is: {list(gameloop.queue)}')  
            return gameloop
        
        return new_empty_queue() # DELETE THIS LINE




