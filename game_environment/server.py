from copy import deepcopy
import json
import ast
import sys
import argparse
import logging

from absl import app
from absl import flags
from ml_collections import config_dict
from game_environment.substrates.installer import install_substrate
from game_environment.playing_utils import level_playing_utils as level_playing_utils
from game_environment.bots import get_bots_for_scenario, Bot
from utils.logging import CustomAdapter
from typing import Dict, Any
import importlib
import os

# Import functions 
def import_game(substrate_name:str):
    """
    Import the game module from the game_environment/substrates/python folder
    Args:
        substrate_name: Name of the game to import
    Returns:
        The game module
    """
    game_module_path = f'game_environment.substrates.python.{substrate_name}'
    game_module = importlib.import_module(game_module_path)
    return game_module


# Global variables
ASCII_MAP = None
game = None
FLAGS = flags.FLAGS

flags.DEFINE_integer('screen_width', 800,
                     'Width, in pixels, of the game screen')
flags.DEFINE_integer('screen_height', 600,
                     'Height, in pixels, of the game screen')
flags.DEFINE_integer('frames_per_second', 8, 'Frames per second of the game')
flags.DEFINE_string('observation', 'RGB', 'Name of the observation to render')
flags.DEFINE_bool('verbose', False, 'Whether we want verbose output')
flags.DEFINE_bool('display_text', False,
                  'Whether we to display a debug text message')
flags.DEFINE_string('text_message', 'This page intentionally left blank',
                    'Text to display if `display_text` is `True`')

logger = logging.getLogger(__name__)
logger = CustomAdapter(logger)

def read_action_map ():
    for line in sys.stdin:
        return ast.literal_eval(line.strip())
    

def get_current_direction(agent_id):
    readed_action_map = read_action_map()
    return readed_action_map[agent_id]['move']

def get_current_turn(agent_id):
    readed_action_map = read_action_map()
    return readed_action_map[agent_id]['turn']

def get_current_fire(agent_id):
    readed_action_map = read_action_map()
    return readed_action_map[agent_id]['fireZap']


_ACTION_MAP = {
    0:{
    'move': level_playing_utils.get_direction_pressed,
    'turn': level_playing_utils.get_turn_pressed,
    'fireZap': level_playing_utils.get_space_key_pressed
    },
    1:{
    'move': level_playing_utils.get_random_direction,
    'turn': level_playing_utils.get_random_turn,
    'fireZap': level_playing_utils.get_random_fire 
    },    
    2:{
    'move': level_playing_utils.get_random_direction,
    'turn': level_playing_utils.get_random_turn,
    'fireZap': level_playing_utils.get_random_fire 
    }
}


def verbose_fn(unused_timestep, unused_player_index: int) -> None:
    pass

def run_episode(game_name: str, record: bool, players: list[str], init_timestamp:str, scenario: str = None):
    """Create the simulation environment and run an episode of the game
    Args:
        game_name: Name of the game to run, the name must match a folder in game_environment/substrates/python
        record: Whether to record the game. 
        players: List with the player names to run the game with
        scenario: Name of the scenario to run, the must be one of the predefined scenarios for the chosen game
        
    Returns:
        A game environment
    """

    # Install the substrate in the meltingpot library
    install_substrate(game_name)
    observation = "WORLD.RGB"
    config_overrides = {}
    verbose = False
    print_events = False

    # If a scenario is provided, get the bots from the scenario
    bots = None
    bots_policy_names = []
    is_focal_player = [True for _ in players]
    if scenario:
        bots_policy_names = get_bots_for_scenario(scenario)
        bots_names = [f'bot_{i+1}' for i in range(len(bots_policy_names))]
        players.extend(bots_names)
        is_focal_player.extend([False for _ in bots_names])

    # Get the initial game configuration
    env_config = game.get_config(players)

    # Initialize the bots if there are any
    if len(bots_policy_names):
        bots = [Bot(policy_name, name, players.index(name)+1, env_config.action_set) for i, (policy_name, name) in enumerate(zip(bots_policy_names, bots_names))]

    # Set the game configuration
    with config_dict.ConfigDict(env_config).unlocked() as env_config:
        env_config.lab2d_settings = game.build(env_config)
        env_config.is_focal_player = is_focal_player
    
    config_overrides = change_avatars_appearance(env_config.lab2d_settings, is_focal_player)

    # Create the game environment and run the episode
    game_env = level_playing_utils.Game(observation,
        config_overrides,
        _ACTION_MAP,
        env_config, 
        interactive=level_playing_utils.RenderType.PYGAME,
        player_prefixes=players,
        game_ascii_map=ASCII_MAP,
        init_timestamp=init_timestamp,
        verbose_fn=verbose_fn if verbose else None,
        print_events=print_events, 
        record=record,
        bots=bots,
        substrate_name=game_name,
        )
    return game_env


def start_server(players: list[str],init_timestamp: str,  game_name: str = "commons_harvest_language", record: bool = False, scenario: str = None):
    """Start the game simulation server
    Args:
        players: List with the player names to run the game with
        game_name: Name of the game to run, the name must match a folder in game_environment/substrates/python
        record: Whether to record the game
        scenario: Name of the scenario to run, the must be one of the predefined scenarios for the chosen game
    
    Returns:
        A game environment
    """
    #global ASCII_MAP
    global game
    #Imports the game module
    game = import_game(game_name)

    return run_episode(game_name, record, players, init_timestamp, scenario)

def get_scenario_map  (game_name:str)-> str:
    """Get the scenario map from the game environment
    Returns:
        A string of the scenario map, rows are separed by '\n'
    """
    global ASCII_MAP
    ASCII_MAP = import_game(game_name).ASCII_MAP
    #return import_game(game_name).ASCII_MAP
    return ASCII_MAP

def default_agent_actions_map():
    """
    Description: Returns the base action map for the agent
    Retrieves the action map from the game environment
    """
    return deepcopy(game.NOOP)

def change_avatars_appearance(lab2d_settings: Dict[str, Any],is_focal_player: list[bool]):    

    """
    Change the avatars appearance in the game environment
    """
    new_color =  (0, 0, 0, 255)  # Example new color
    game_objects = lab2d_settings['simulation']['gameObjects']

    for i in range(len(is_focal_player)):
        if not is_focal_player[i]:

           
            components = game_objects[i]['components']   
            # Find the Appearance component
            for j, component in enumerate(components):
                if component.get('component') == 'Appearance':
                    # Override the first color ('!')
                    component['kwargs']['palettes'][0]['!'] = new_color
                    component['kwargs']['palettes'][0]['#'] = new_color
                    component['kwargs']['palettes'][0]['%'] = new_color
                    component['kwargs']['palettes'][0]['&'] = new_color
                    components[j] = component
                    break
            game_objects[i]['components'] = components   
    
    overrided_configs = {'simulation':lab2d_settings['simulation']}
    overrided_configs['simulation']['gameObjects'] = game_objects
    
    return overrided_configs
    

