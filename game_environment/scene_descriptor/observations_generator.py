"""

File: observations_descriptor.py
Description: Implements required functions for the observations descriptor

"""

import numpy as np
import ast
from scipy.ndimage import label, center_of_mass
from collections import defaultdict
import re


class ObservationsGenerator (object):
    """
    Description: Implements required functions for the observations descriptor. 
            This class is used to generate the descriptions of the observations of the agents based on the 
            scene descriptor module which provides the observations in ascci format
    """

    def __init__(self, global_map:str, players_names: list):
        """
        Description: Initializes the observations generator

        Args:
            global_map (str): Global map in ascci format
            players_names (list): List with the names of the players
        """
        
        self.global_map = global_map
        self.global_trees = self.connected_elems_map(self.global_map, ['A', 'G'])
        self.players_names = players_names


    def connected_elems_map(self, ascci_map, elements_to_find):
        """
        Returns a dictionary with the connected components of the map and their elements

        Args:
            ascci_map (str): Map in ascci format
            elements_to_find (list): List of elements to find in the map

        Returns:
            dict: Dictionary with the connected components of the map and their elements
        """

        # Convierte la matriz en una matriz numpy
        matrix = np.array([list(row) for row in ascci_map.split('\n') if row != ''])

        # Generate mask
        mask = (matrix == elements_to_find[0]) 
        for elem in elements_to_find[1:]:
            mask |= (matrix == elem)

        # Encontrar componentes conectados
        labeled_matrix, num_features = label(mask)

        # Inicializa un diccionario para almacenar los centros de los componentes y sus elementos
        component_data = defaultdict(list)

        # Calcula el centro de cada componente y almacena sus elementos
        for i in range(1, num_features + 1):
            component_mask = labeled_matrix == i
            center = center_of_mass(component_mask)
            center_coords = (int(center[0]), int(center[1]))
            component_elements = np.argwhere(component_mask)
            component_data[i] = {'center': center_coords, 'elements': component_elements.tolist()}

        return dict(component_data)


    def get_element_global_pos(self, element_local, local_position, global_position, agent_orientation=0):
        """
        Description: Returns the global position of an element given its local position and the global position of the agent

        Args:
            element_local (tuple): Local position of the element
            local_position (tuple): Local position of the agent 
            global_position (tuple): Global position of the agent
            agent_orientation (int, optional): Orientation of the agent. Defaults to 0.

        Returns:
            tuple: Global position of the element
        """
        if agent_orientation == 0:
            element_global = (element_local[0] - local_position[0]) + global_position[0],\
                                (element_local[1] - local_position[1]) + global_position[1]
        elif agent_orientation == 1:
            element_global = (element_local[1] - local_position[1]) + global_position[0],\
                                (local_position[0] - element_local[0]) + global_position[1]
        elif agent_orientation == 2:
            element_global = -1 * (element_local[0] - local_position[0]) + global_position[0],\
                             -1 * (element_local[1] - local_position[1]) + global_position[1]
        elif agent_orientation == 3:
            element_global = -1 * (element_local[1] - local_position[1]) + global_position[0],\
                             (element_local[0] - local_position[0]) + global_position[1]

        return list(element_global)

    


    def get_all_observations_descriptions(self,  agents_observations_str: str) -> dict[str, list[str]]:
        """
        Description: Returns a dictionary with the descriptions of the observations of the agents

        Args:
            agents_observations_str (str): Observations of the agents in ascci format
            
        Returns:
            dict[str, list[str]]: Dictionary with the descriptions of the observations in a list by agent name
        """
        agents_observations = ast.literal_eval(agents_observations_str)
        observations_description_per_agent = {}
        for agent_id, agent_dict in agents_observations.items():
            agent = self.players_names[agent_id]
            observations_description_per_agent[agent] = self.get_observations_per_agent(agent_dict)
            
        return observations_description_per_agent
    

    def get_observations_per_agent(self, agent_dict: dict):
        """
        Description: Returns a list with the descriptions of the observations of the agent

        Args:
            agent_dict (dict): Dictionary with the observations of the agent
        
        Returns:
            list: List with the descriptions of the observations of the agent
        """
        list_of_observations = []
        if agent_dict['observation'].startswith('You were taken'):
            list_of_observations.append(agent_dict['observation'])
            return list_of_observations
        else:
            local_observation_map = agent_dict['observation']
            local_map_position = (9,5)
            global_position = agent_dict['global_position']
            agent_orientation = agent_dict['orientation']

            # Get trees descriptions
            trees_descriptions = self.get_trees_descriptions(local_observation_map, local_map_position, global_position, agent_orientation) 
            list_of_observations.extend(trees_descriptions)

            # Get agents observed descriptions
            i = 0
            for row in local_observation_map.split('\n'):
                j=0
                for char in row:
                    if re.match(r'^[0-9]$', char):
                        agent_id = int(char)
                        agent_global_pos = self.get_element_global_pos((i,j), local_map_position, global_position, agent_orientation)
                        list_of_observations.append("Observed agent {} at position {}".format(agent_id, agent_global_pos))
                    j+=1
                i+=1
        
        return list_of_observations

    def get_trees_descriptions(self, local_map, local_position, global_position, agent_orientation):
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

        local_tree_elements = self.connected_elems_map(local_map, elements_to_find=['A', 'G'])
        list_trees_observations = []
        trees_observed = {}

        for global_tree_id, global_tree_data in self.global_trees.items():
            apple_count, grass_count = 0, 0
            for local_tree_data in local_tree_elements.values():
                # Check if the group is a tree element
                first_element = local_tree_data['elements'][0]
                element_type = local_map.split('\n')[first_element[0]][first_element[1]]
                if element_type not in ['A', 'G']:
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
                        list_trees_observations.append("Observed grass to grow apples at position {}. This grass belongs to tree {}"
                                                    .format(apple_global_pos, global_tree_id))
                        grass_count += 1
                    else:
                        list_trees_observations.append("Observed an apple at position {}. This apple belongs to tree {}"
                                                    .format(apple_global_pos, global_tree_id ))
                        apple_count += 1

            if apple_count > 0 or grass_count > 0:      
                list_trees_observations.append("Observed tree {} at position {}. This tree has {} apples remaining and {} grass for apples growing on the observed map. The tree might have more apples and grass on the global map"
                                                .format(global_tree_id, local_center_real_pos, apple_count, grass_count))
        return list_trees_observations
