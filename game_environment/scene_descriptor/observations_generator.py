"""

File: observations_descriptor.py
Description: Implements required functions for the observations descriptor

"""

from importlib import import_module
import numpy as np
import ast
from scipy.ndimage import label, center_of_mass
from collections import defaultdict
import re
from game_environment.utils import connected_elems_map, check_agent_out_of_game, get_element_global_pos, get_matrix, number_to_words


import logging
from utils.logging import CustomAdapter

logger = logging.getLogger(__name__)
logger = CustomAdapter(logger)


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
        self.substrate_utils_module = import_module(f'game_environment.substrates.{substrate_name}_utilities.substrate_utils')

        self.connected_elments = self.substrate_utils_module.get_connected_elements(global_map)


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


        logger.info(f' Observations descriptions for all agents: {observations_description_per_agent} \n')
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
            list_of_observations.append(str(agent_dict['observation'] + ' At position {}'.format(agent_dict['global_position'])))
            return list_of_observations
        elif agent_dict['observation'].startswith('There are no observations: you\'re out of the game'):
            list_of_observations.append(str(agent_dict['observation']))
            return list_of_observations
        else:
            local_observation_map = agent_dict['observation']
            last_observation_map =  agent_dict['last_observation']
            local_map_position = (9,5)
            global_position = agent_dict['global_position']
            agent_orientation = agent_dict['orientation']
            symbols = {'self_symbol': self.self_symbol, 'other_players_symbols': self.other_players_symbols }

            substrate_items_descriptions = self.get_specific_substrate_observations(local_observation_map, local_map_position, global_position, agent_orientation, self.connected_elments, symbols)
            list_of_observations.extend(substrate_items_descriptions)

            # Get agents observed descriptions for structured elements in the substrate map
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
            observed_changes = self.get_observed_changes(local_observation_map, last_observation_map, local_map_position, global_position, agent_orientation, game_time)
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
                    agent_global_pos = get_element_global_pos((i,j), local_map_position, global_position, agent_orientation)
                    agents_observed.append("Observed agent {} at position {}.".format(agent_name, agent_global_pos))
                j+=1
            i+=1

        return agents_observed


    def get_specific_substrate_observations (self, local_observation_map: str, local_map_position: tuple, global_position: tuple, agent_orientation: int, connected_elments: dict, symbols: dict) -> list[str]:
        """
        Calls the specific substrate observation function of the substrate utilities module

        Args:
            local_observation_map (str): Local map in ascci format
            local_map_position (tuple): Local position of the agent in the observed window
            global_position (tuple): Global position of the agent
            agent_orientation (int): Orientation of the agent
            connected_elments (dict): Connected elements of the map
            symbols (dict): Symbols used in the map

        Returns:
            list[str]: List with the descriptions of the specific substrate observations
        """

        return self.substrate_utils_module.get_specific_substrate_obs(local_observation_map, local_map_position, global_position, agent_orientation, connected_elments, symbols)

    def get_observed_changes(self, observed_map: str, last_observed_map: str | None, agent_local_position: tuple, agent_global_position: tuple, agent_orientation: int, game_time: str) -> list[tuple[str, str]]:
        """Calls the specific substrate observation function of the substrate utilities module
            It creates a list of tuples with the changes in the environment and the game time

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

        return self.substrate_utils_module.get_observed_changes(observed_map, last_observed_map, agent_local_position, agent_global_position, agent_orientation, game_time, self.players_names)
