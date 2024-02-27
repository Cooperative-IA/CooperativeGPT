"""

File: observations_descriptor.py
Description: Implements required functions for the observations descriptor

"""

import numpy as np
import ast
from scipy.ndimage import label, center_of_mass
from collections import defaultdict
import re
from game_environment.utils import connected_elems_map
import inflect 


class ObservationsGenerator (object):
    """
    Description: Implements required functions for the observations descriptor. 
            This class is used to generate the descriptions of the observations of the agents based on the 
            scene descriptor module which provides the observations in ascci format
    """

    def __init__(self, global_map:str, players_names: list, substrate_name:str):
        """
        Description: Initializes the observations generator

        Args:
            global_map (str): Global map in ascci format
            players_names (list): List with the names of the players
            substrate_name (str): Name of the substrate
        """
        
        self.global_map = global_map
        self.players_names = players_names
        self.self_symbol = '#'
        self.other_players_symbols = [str(i) for i in range(len(players_names))]
        self.observed_changes = {name: [] for name in players_names}
        self.substrate_name = substrate_name

        if self.substrate_name == 'commons_harvest_open':
            self.global_trees = connected_elems_map(self.global_map, ['A', 'G'])
        elif self.substrate_name == 'clean_up':
            self.river_bank =  connected_elems_map(self.global_map, ['=','+']) # Chars that represent the river bank
            self.apple_field_edge = connected_elems_map(self.global_map, ['^','T']) # Chars that represent the apple field edge


    def get_element_global_pos(self, el_local_pos, self_local_pos, self_global_pos, agent_orientation=0) -> list[int]:
        """
        Description: Returns the global position of an element given its local position and the global position of the agent

        Args:
            el_local_pos (tuple): Local position of the element
            self_local_pos (tuple): Local position of the agent 
            self_global_pos (tuple): Global position of the agent
            agent_orientation (int, optional): Orientation of the agent. Defaults to 0.

        Returns:
            list[int]: Global position of the element
        """
        element_global = []
        if agent_orientation == 0:
            element_global = (el_local_pos[0] - self_local_pos[0]) + self_global_pos[0],\
                                (el_local_pos[1] - self_local_pos[1]) + self_global_pos[1]
        elif agent_orientation == 1:
            element_global = (el_local_pos[1] - self_local_pos[1]) + self_global_pos[0],\
                               -1 * (el_local_pos[0] - self_local_pos[0]) + self_global_pos[1]
        elif agent_orientation == 2:
            element_global = -1 * (el_local_pos[0] - self_local_pos[0]) + self_global_pos[0],\
                                -1 * (el_local_pos[1] - self_local_pos[1]) + self_global_pos[1]
        elif agent_orientation == 3:
            element_global = -1 * (el_local_pos[1] - self_local_pos[1]) + self_global_pos[0],\
                                (el_local_pos[0] - self_local_pos[0]) + self_global_pos[1]
        return list(element_global)

    


    def get_all_observations_descriptions(self,  agents_observations_str: str) -> dict[str, list[str]]:
        """
        Description: Returns a dictionary with the descriptions of the observations of the agents

        Args:
            agents_observations_str (str): Observations of the agents in ascci format
            agents_observing (list[str]): List of the agents that are observing and didn't take an action
            
        Returns:
            dict[str, list[str]]: Dictionary with the descriptions of the observations in a list by agent name
        """
        agents_observations = ast.literal_eval(agents_observations_str)
        observations_description_per_agent = {}
        for agent_name, agent_dict in agents_observations.items():
            observations_description_per_agent[agent_name] = self.get_observations_per_agent(agent_dict, agent_name, True)
            
        return observations_description_per_agent
    

    def get_observations_per_agent(self, agent_dict: dict, agent_name: str, is_observing: bool) -> list[str]:
        """
        Description: Returns a list with the descriptions of the observations of the agent

        Args:
            agent_dict (dict): Dictionary with the observations of the agent
            agent_name (str): Name of the agent
            is_observing (bool): True if the agent is observing, False otherwise
        
        Returns:
            list: List with the descriptions of the observations of the agent
        """
        list_of_observations = []
        if agent_dict['observation'].startswith('There are no observations: You were attacked'):
            list_of_observations.append(str(agent_dict['observation'] + ' at position {}'.format(agent_dict['global_position'])))
            return list_of_observations
        else:
            local_observation_map = agent_dict['observation']
            last_observation_map =  agent_dict['last_observation']
            local_map_position = (9,5)
            global_position = agent_dict['global_position']
            agent_orientation = agent_dict['orientation']


            if self.substrate_name == 'commons_harvest_open':
                # Get trees descriptions
                trees_descriptions = self.get_trees_descriptions(local_observation_map, local_map_position, global_position, agent_orientation) 
                list_of_observations.extend(trees_descriptions)
            elif self.substrate_name == 'clean_up':
                # Get objects of clean up descriptions
                items_descriptions = self.get_clean_up_descriptions(local_observation_map, local_map_position, global_position, agent_orientation)
                list_of_observations.extend(items_descriptions)

            # Get agents observed descriptions
            agents_observed = self.get_agents_observed(local_observation_map, local_map_position, global_position, agent_orientation)
            list_of_observations.extend(agents_observed)
        
        return list_of_observations
    
    def update_state_changes(self, scene_description: dict, agents_observing: list[str], game_time: str):
        """Update the state changes of the agents

        Args:
            scene_description (dict): Scene description of the agents
            agents_observing (list[str]): List of the agents that are observing and didn't take an action
        """
        for agent_name in agents_observing:
            agent_dict = scene_description[agent_name]
            local_observation_map = agent_dict['observation']
            last_observation_map =  agent_dict['last_observation']
            local_map_position = (9,5)
            global_position = agent_dict['global_position']
            agent_orientation = agent_dict['orientation']

            # Get observed changes in the environment. If the agent is observing, the changes are stored in the observed_changes dictionary
            try:
                observed_changes = self.get_observed_changes(local_observation_map, last_observation_map, local_map_position, global_position, agent_orientation, game_time)
            except:
                observed_changes = [] # If the agent is out of the game, there is an error. Pass no observed changes
            self.observed_changes[agent_name].extend(observed_changes)
    
    def get_observed_changes_per_agent(self, agent_name: str) -> list[tuple[str, str]]:
        """
        Description: Returns a list with the descriptions of the observed changes of the agent

        Args:
            agent_name (str): Name of the agent
        
        Returns:
            list: List of tuples with the descriptions of the observed changes of the agent and the game time
        """
        observations = self.observed_changes[agent_name]
        self.observed_changes[agent_name] = []
        return observations
    
    def get_agents_observed(self, local_observation_map: str, local_map_position: tuple, global_position: tuple, agent_orientation: int) -> list[str]:
        """
        Returns a list with the descriptions of the agents observed by the agent

        Args:
            local_observation_map (str): Local map in ascci format
            local_map_position (tuple): Local position of the agent in the observed window
            global_position (tuple): Global position of the agent
            agent_orientation (int): Orientation of the agent

        Returns:
            list[str]: List with the descriptions of the agents observed by the agent
        """

        agents_observed = []

        i = 0
        for row in local_observation_map.split('\n'):
            j=0
            for char in row:
                if re.match(r'^[0-9]$', char):
                    agent_id = int(char)
                    agent_name = self.players_names[agent_id]
                    agent_global_pos = self.get_element_global_pos((i,j), local_map_position, global_position, agent_orientation)
                    agents_observed.append("Observed agent {} at position {}.".format(agent_name, agent_global_pos))
                j+=1
            i+=1

        return agents_observed

    def get_trees_descriptions(self, local_map:str, local_position:tuple, global_position:tuple, agent_orientation:int):
        """
        Description: Returns a list with the descriptions of the trees observed by the agent

        Args:
            local_map (str): Local map in ascci format
            local_position (tuple): Local position of the agent
            global_position (tuple): Global position of the agent
            agent_orientation (int): Orientation of the agent
            
        Returns:
            list: List with the descriptions of the trees observed by the agent
        """
        tree_elements = ['A', 'G']
        elements_to_find = tree_elements + self.other_players_symbols + [self.self_symbol]
        local_tree_elements = connected_elems_map(local_map, elements_to_find=elements_to_find)
        list_trees_observations = []
        trees_observed = {}
        for global_tree_id, global_tree_data in self.global_trees.items():
            apple_count, grass_count = 0, 0
            apple_list, grass_list = [], []
            for local_tree_data in local_tree_elements.values():
                # Check if the group is a tree element
                first_element = local_tree_data['elements'][0]
                element_type = local_map.split('\n')[first_element[0]][first_element[1]]
                second_element_type = None
                if len(local_tree_data['elements'])>1: # We'll make a double check to verify if the first elelment is being overlapped by another element
                    second_element = local_tree_data['elements'][1] 
                    second_element_type = local_map.split('\n')[second_element[0]][second_element[1]]
                if (element_type not in tree_elements) and (second_element_type not in tree_elements):
                    continue

                # Continue if the tree has already been observed
                if global_tree_id in trees_observed.get(element_type, []): 
                    continue

                local_tree_center = local_tree_data['center']
                local_center_real_pos = self.get_element_global_pos(local_tree_center, local_position, global_position, agent_orientation)

                # Check if the local tree corresponds to the global tree
                if local_center_real_pos not in global_tree_data['elements']:
                    continue

                # Find the cluster tree of the local tree
                trees_observed[element_type] = trees_observed.get(element_type, []) + [global_tree_id]
    
                for apple in local_tree_data['elements']:
                    apple_global_pos = self.get_element_global_pos(apple, local_position, global_position, agent_orientation)
                    if local_map.split('\n')[apple[0]][apple[1]] == 'G':
                        list_trees_observations.append("Observed grass to grow apples at position {}. This grass belongs to tree {}."
                                                    .format(apple_global_pos, global_tree_id))
                        grass_list.append(apple_global_pos)
                        grass_count += 1
                    elif local_map.split('\n')[apple[0]][apple[1]] == 'A':
                        list_trees_observations.append("Observed an apple at position {}. This apple belongs to tree {}."
                                                    .format(apple_global_pos, global_tree_id ))
                        apple_list.append(apple_global_pos)
                        apple_count += 1

            if apple_count > 0 or grass_count > 0:      
                list_trees_observations.append("Observed tree {} at position {}. This tree has {} apples remaining and {} grass for apples growing on the observed map. The tree might have more apples and grass on the global map."
                                                .format(global_tree_id, list(global_tree_data['center']), apple_count, grass_count))
        return list_trees_observations
    
    def get_matrix(self, map) -> np.array:
        """Convert a map in ascci format to a matrix

        Args:
            map (str): Map in ascci format

        Returns:
            np.array: Map in matrix format
        """
        return np.array([[l for l in row] for row in map.split('\n')])

    def get_observed_changes(self, observed_map: str, last_observed_map: str | None, agent_local_position: tuple, agent_global_position: tuple, agent_orientation: int, game_time: str) -> list[tuple[str, str]]:
        """Create a list of observations of the changes in the environment
        
        Args:
            observed_map (str): Map observed by the agent
            last_observed_map (str | None): Last map observed by the agent
            agent_local_position (tuple): Position of the agent on the observed map
            agent_global_position (tuple): Global position of the agent
            agent_orientation (int): Orientation of the agent
            game_time (str): Current game time

        Returns:
            list[tuple[str, str]]: List of tuples with the changes in the environment, and the game time
        """
        observations = []
        if last_observed_map == None:
            return observations
        
        curr_m = self.get_matrix(observed_map)
        last_m = self.get_matrix(last_observed_map)
        for index in np.ndindex(curr_m.shape):
            curr_el = curr_m[index]
            last_el = last_m[index]
            if curr_el != last_el:
                # If an apple was taken
                if last_el == 'A':
                    agent_id = int(curr_el)
                    agent_name = self.players_names[agent_id]
                    el_pos = self.get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
                    observations.append((f"Observed that agent {agent_name} took an apple from position {el_pos}.", game_time))
                # If grass desappeared
                elif last_el == 'G' and curr_el == 'F':
                    el_pos = self.get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
                    observations.append((f"Observed that the grass at position {el_pos} disappeared.", game_time))
                # If grass appeared
                elif last_el == 'F' and curr_el == 'G':
                    el_pos = self.get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
                    observations.append((f"Observed that grass to grow apples appeared at position {el_pos}.", game_time))
                # If an apple appeared
                elif last_el == 'G' and curr_el == 'A':
                    el_pos = self.get_element_global_pos(index, agent_local_position, agent_global_position, agent_orientation)
                    observations.append((f"Observed that an apple grew at position {el_pos}.", game_time))

        return observations


    def get_clean_up_descriptions (self, local_map:str, local_position:tuple, global_position:tuple, agent_orientation:int):
        """
        Description: Returns a list with the descriptions of the objects observed by the agent

        Args:
            local_map (str): Local map in ascci format
            local_position (tuple): Local position of the agent
            global_position (tuple): Global position of the agent
            agent_orientation (int): Orientation of the agent
            
        Returns:
            list: List with the descriptions of the objects observed by the agent
        """
        
        items_observed = []
        # Get apples (A) and dirt (D) observed descriptions
        for i, row in enumerate(local_map.split('\n')):
            for j, char in enumerate(row):
                if char == 'A':
                    apple_global_pos = self.get_element_global_pos((i,j), local_position, global_position, agent_orientation)
                    items_observed.append("Observed an apple at position {}".format(apple_global_pos))

                elif char == 'D':
                    dirt_global_pos = self.get_element_global_pos((i,j), local_position, global_position, agent_orientation)
                    items_observed.append("Observed dirt on the river at position {}".format(dirt_global_pos))

                for elm in self.river_bank.values():
                    if (i,j) in elm['elements']:
                        river_bank_global_pos = self.get_element_global_pos((i,j), local_position, global_position, agent_orientation)
                        items_observed.append("Observed river bank at position {}".format(river_bank_global_pos))
                
                for elm in self.apple_field_edge.values():
                    if (i,j) in elm['elements']:
                        apple_field_edge_global_pos = self.get_element_global_pos((i,j), local_position, global_position, agent_orientation)
                        items_observed.append("Observed apple field edge at position {}".format(apple_field_edge_global_pos))

        return items_observed

    @staticmethod
    def number_to_words(number):
        """
        Description: Returns the number in words
        
        Args:
            number (int): Number to convert to words
        Returns:
            str: Number in words
        """
        p = inflect.engine()
        words = p.number_to_words(number)
        return words
