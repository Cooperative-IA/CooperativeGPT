# Copyright 2020 DeepMind Technologies Limited.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""A simple human player for testing a Melting Pot level.

Use `WASD` keys to move the character around.
Use `Q and E` to turn the character.
Use `SPACE` to fire the zapper.
Use `TAB` to switch between players.
"""
import threading
import collections
import enum
import time
import logging

from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple
import dm_env

from ml_collections import config_dict
import numpy as np
import pygame

import dmlab2d
from game_environment.recorder.recorder import Recorder
from meltingpot.python.utils.substrates import builder
from game_environment.scene_descriptor.scene_descriptor import SceneDescriptor
from game_environment.scene_descriptor.observations_generator import ObservationsGenerator

import sys
import ast

WHITE = (255, 255, 255)

MOVEMENT_MAP = {
    'NONE': 0,
    'FORWARD': 1,
    'RIGHT': 2,
    'BACKWARD': 3,
    'LEFT': 4,
}

EnvBuilder = Callable[..., dmlab2d.Environment]  # Only supporting kwargs.

ActionMap = Mapping[str, Callable[[], int]]


class RenderType(enum.Enum):
    NONE = 0
    PYGAME = 1


def get_random_direction() -> int:
    """Gets a random direction."""
    return np.random.choice(list(MOVEMENT_MAP.values()))


def get_random_turn() -> int:
    """Gets a random turn."""
    return np.random.choice([-1, 0, 1])


def get_random_fire() -> int:
    """Gets a random fire."""
    return np.random.choice([0, 1])


def get_direction_pressed() -> int:
    """Gets direction pressed."""
    key_pressed = pygame.key.get_pressed()
    if key_pressed[pygame.K_UP] or key_pressed[pygame.K_w]:
        return MOVEMENT_MAP['FORWARD']
    if key_pressed[pygame.K_RIGHT] or key_pressed[pygame.K_d]:
        return MOVEMENT_MAP['RIGHT']
    if key_pressed[pygame.K_DOWN] or key_pressed[pygame.K_s]:
        return MOVEMENT_MAP['BACKWARD']
    if key_pressed[pygame.K_LEFT] or key_pressed[pygame.K_a]:
        return MOVEMENT_MAP['LEFT']
    return MOVEMENT_MAP['NONE']


def get_turn_pressed() -> int:
    """Calculates turn increment."""
    key_pressed = pygame.key.get_pressed()
    if key_pressed[pygame.K_DELETE] or key_pressed[pygame.K_q]:
        return -1
    if key_pressed[pygame.K_PAGEDOWN] or key_pressed[pygame.K_e]:
        return 1
    return 0


def get_space_key_pressed() -> int:
    return 1 if pygame.key.get_pressed()[pygame.K_SPACE] else 0


def get_key_number_pressed() -> int:
    number_keys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                   pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]
    for num in range(len(number_keys)):
        if pygame.key.get_pressed()[number_keys[num]]:
            return num
    return -1


def get_key_number_one_pressed() -> int:
    return 1 if pygame.key.get_pressed()[pygame.K_1] else 0


def get_key_number_two_pressed() -> int:
    return 1 if pygame.key.get_pressed()[pygame.K_2] else 0


def get_key_number_three_pressed() -> int:
    return 1 if pygame.key.get_pressed()[pygame.K_3] else 0


def get_key_number_four_pressed() -> int:
    return 1 if pygame.key.get_pressed()[pygame.K_4] else 0


def get_key_number_five_pressed() -> int:
    return 1 if pygame.key.get_pressed()[pygame.K_5] else 0


def get_left_control_pressed() -> int:
    return 1 if pygame.key.get_pressed()[pygame.K_LCTRL] else 0


def get_left_shift_pressed() -> int:
    return 1 if pygame.key.get_pressed()[pygame.K_LSHIFT] else 0


def get_right_shift_pressed() -> int:
    return 1 if pygame.key.get_pressed()[pygame.K_RSHIFT] else 0


def get_key_c_pressed() -> int:
    return 1 if pygame.key.get_pressed()[pygame.K_c] else 0


def get_key_z_pressed() -> int:
    return 1 if pygame.key.get_pressed()[pygame.K_z] else 0


def get_key_x_pressed() -> int:
    return 1 if pygame.key.get_pressed()[pygame.K_x] else 0


def _split_key(key: str) -> Tuple[str, str]:
    """Splits the key into player index and name."""
    return tuple(key.split('.', maxsplit=1))


def _get_rewards(timestep: dm_env.TimeStep) -> Mapping[str, float]:
    """Gets the list of rewards, one for each player."""
    rewards = {}
    for key in timestep.observation.keys():
        if key.endswith('.REWARD'):
            player_prefix, name = _split_key(key)
            if name == 'REWARD':
                rewards[player_prefix] = timestep.observation[key]
    return rewards


class ActionReader(object):
    """Convert keyboard actions to environment actions."""

    def __init__(self, env: dmlab2d.Environment, action_map: ActionMap):
        # Actions are named "<player_prefix>.<action_name>"
        self._action_map = action_map
        self._action_spec = env.action_spec()
        assert isinstance(self._action_spec, dict)
        self._action_names = set()
        for action_key in self._action_spec.keys():
            _, action_name = _split_key(action_key)
            self._action_names.add(action_name)

    def step(self, player_prefix: str) -> Mapping[str, int]:
        """Update the actions of player `player_prefix`."""
        actions = {action_key: 0 for action_key in self._action_spec.keys()}
        for action_name in self._action_names:
            actions[f'{player_prefix}.{action_name}'] = self._action_map[
                action_name]()
        return actions


    def various_agents_step(self, new_action_map, player_prefixes)-> Mapping[str, int]:
        """Update the actions of player `player_prefix`."""
        #print("--------------------NEW ACTION MAP-------------\n", new_action_map)
        actions = {action_key: 0 for action_key in self._action_spec.keys()}
        for i, player_prefix in enumerate(player_prefixes):
            for action_name in self._action_names:
                actions[f'{player_prefix}.{action_name}'] = new_action_map[i][ action_name]
        return actions
    
logger = logging.getLogger(__name__)

class Game:
    """Run multiplayer environment, with per player rendering and actions. This class is used to run the game Commons Harvest Open from Meltingpot."""

    def __init__(self,
                 render_observation: str,
            config_overrides: Dict[str, Any],
            action_map: ActionMap,
            full_config: config_dict.ConfigDict,
            game_ascii_map: str,
            interactive: RenderType = RenderType.PYGAME,
            screen_width: int = 800,
            screen_height: int = 600,
            fps: int = 8,
            verbose_fn: Optional[Callable[[dm_env.TimeStep, int, int], None]] = None,
            text_display_fn: Optional[Callable[[dm_env.TimeStep, int], str]] = None,
            text_font_size: int = 36,
            text_x_pos: int = 20,
            text_y_pos: int = 20,
            text_color: Tuple[int, ...] = WHITE,
            env_builder: EnvBuilder = builder.builder,
            print_events: Optional[bool] = False,
            player_prefixes: Optional[Sequence[str]] = None,
            default_observation: str = 'WORLD.RGB',
            reset_env_when_done: bool = False,
            initial_player_index: int = 0,
            record: bool = False,):
        """Run multiplayer environment, with per player rendering and actions.

        This function initialises a Melting Pot environment with the given
        configuration (including possible config overrides), and optionally launches
        the episode as an interactive game using pygame.  The controls are described
        in the action_map, whose keys correspond to discrete actions of the
        environment.

        Args:
        render_observation: A string consisting of the observation name to render.
            Usually 'RGB' for the third person world view.
        config_overrides: A dictionary of settings to override from the original
            `full_config.lab2d_settings`. Typically these are used to set the number
            of players.
        action_map: A dictionary of (discrete) action names to functions that detect
            the keys that correspond to its possible action values.  For example,
            for movement, we might want to have WASD navigation tied to the 'move'
            action name using `get_direction_pressed`.  See examples in the various
            play_*.py scripts.
        full_config: The full configuration for the Melting Pot environment.  These
            usually come from meltingpot/python/configs/environments.
        game_ascii_map: The ascii map of the game.
        interactive: A RenderType representing whether the episode should be run
            with PyGame, or without any interface.  Setting interactive to false
            enables running e.g. a random agent via the action_map returning actions
            without polling PyGame (or any human input).  Non interactive runs
            ignore the screen_width, screen_height and fps parameters.
        screen_width: Width, in pixels, of the window to render the game.
        screen_height: Height, in pixels, of the window to render the game.
        fps: Frames per second of the game.
        verbose_fn: An optional function that will be executed for every step of
            the environment.  It receives the environment timestep, a player index
            (will be called for every index), and the current player index. This is
            typically used to print extra information that would be useful for
            debugging a running episode.
        text_display_fn: An optional function for displaying text on screen. It
            receives the environment and the player index, and returns a string to
            display on the pygame screen.
        text_font_size: the font size of onscreen text (from `text_display_fn`)
        text_x_pos: the x position of onscreen text (from `text_display_fn`)
        text_y_pos: the x position of onscreen text (from `text_display_fn`)
        text_color: RGB color of onscreen text (from `text_display_fn`)
        env_builder: The environment builder function to use. By default it is
            meltingpot.builder.
        print_events: An optional bool that if enabled will print events captured
            from the dmlab2d events API on any timestep where they occur.
        player_prefixes: If given, use these as the prefixes of player actions.
            Pressing TAB will cycle through these. If not given, use the standard
            ('1', '2', ..., numPlayers).
        default_observation: Default observation to render if 'render_observation'
            or '{player_prefix}.{render_observation}' is not found in the dict.
        reset_env_when_done: if True, reset the environment once the episode has
            terminated; useful for playing multiple episodes in a row. Note this
            will cause this function to loop infinitely.
        initial_player_index: Initial index of the player to play as. Defaults to 0.
            (Players are always switchable via the tab key.)
        """
        # Update the config with the overrides.
        full_config.lab2d_settings.update(config_overrides)
        # Create a descriptor to get the raw observations from the game environment
        descriptor = SceneDescriptor(full_config)

        # Define the player ids
        if player_prefixes is None:
            player_count = full_config.lab2d_settings.get('numPlayers', 1)
            # By default, we use lua indices (which start at 1) as player prefixes.
            player_prefixes = [f'{i + 1}' for i in range(player_count)]
        else:
            player_count = len(player_prefixes)
        logger.info(f'Running an episode with {player_count} players: {player_prefixes}.')
        
        # Create the game environment
        env = env_builder(**full_config)

        # Check that the number of player prefixes matches the number of players.
        if len(player_prefixes) != player_count:
            logger.error('Player prefixes, when specified, must be of the same length as the number of players.')
            raise ValueError('Player prefixes, when specified, must be of the same '
                                'length as the number of players.')
        
        # Reset the game environment
        timestep = env.reset()

        # Set the initial player index
        player_index = initial_player_index

        # Create a dictionary to store the score of each player
        score = collections.defaultdict(float)

        # Set the pygame variables
        if interactive == RenderType.PYGAME:
            pygame.init()
            pygame.display.set_caption('Melting Pot: {}'.format(
                full_config.lab2d_settings.levelName))
            font = pygame.font.SysFont(None, text_font_size)

        scale = 1
        observation_spec = env.observation_spec()
        if render_observation in observation_spec:
            obs_spec = observation_spec[render_observation]
        elif f'1.{render_observation}' in observation_spec:
            # This assumes all players have the same observation, which is true for
            # MeltingPot environments.
            obs_spec = observation_spec[f'1.{render_observation}']
        else:
            # Falls back to 'default_observation.'
            obs_spec = observation_spec[default_observation]

        observation_shape = obs_spec.shape
        observation_height = observation_shape[0]
        observation_width = observation_shape[1]
        scale = min(screen_height // observation_height,
                    screen_width // observation_width)
        if interactive == RenderType.PYGAME:
            game_display = pygame.display.set_mode(
                (observation_width * scale, observation_height * scale))
            clock = pygame.time.Clock()

        # Create the game recorder
        if record:
            game_recorder = Recorder("logs", full_config)
            record_counter = 0

        self.env = env
        self.pygame = pygame
        if record:
            self.game_recorder = game_recorder
            self.record_counter = record_counter
        else:
            self.game_recorder = None
            self.record_counter = None

        self.first_move = True
        self.interactive = interactive
        self.player_prefixes = player_prefixes
        self.player_index = player_index
        self.player_count = player_count
        self.action_map = action_map
        self.descriptor = descriptor
        self.timestep = timestep
        self.reset_env_when_done = reset_env_when_done
        self.verbose_fn = verbose_fn
        self.text_display_fn = text_display_fn
        self.font = font
        self.text_font_size = text_font_size
        self.text_x_pos = text_x_pos
        self.text_y_pos = text_y_pos
        self.text_color = text_color
        self.print_events = print_events
        self.default_observation = default_observation
        self.score = score
        self.render_observation = render_observation
        self.scale = scale
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fps = fps
        self.game_display = game_display
        self.clock = clock
        self.record = record
        self.observationsGenerator = ObservationsGenerator(game_ascii_map, player_prefixes)

    def end_game(self):
        """Ends the game. This function is called when the game is finished."""
        self.env.close()
        self.env = None
        self.pygame.quit()
        self.pygame = None
        if self.record:
            self.game_recorder.save_log()

        for prefix in self.player_prefixes:
            logger.info('Player %s: score is %g' % (prefix, self.score[prefix]))

    def step(self, actions) -> dict[int, list[str]] | None:
        """Run one step of the game.
        
        Args:
            actions: A dictionary of actions for each player.
        Returns:
            A dictionary with the observations of each player.
        """
        stop = False

        # Check for pygame controls
        if self.interactive == RenderType.PYGAME:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stop = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        self.player_index = (self.player_index + 1) % self.player_count
                    break
        player_prefix = self.player_prefixes[self.player_index] if self.player_prefixes else ''

        if stop:
            return None

        # Get the raw observations from the environment
        description = self.descriptor.describe_scene(self.timestep)
        
        if not self.first_move:
            # TODO: Execute the actions
            # Get the next action map
            # next_action_map = await action_planner.transform_obs_into_actions(str(description))
            pass
        else:
            self.first_move = False
        
        # Compute next timestep
        # new_actions = action_reader.various_agents_step(next_action_map, player_prefixes)
        #print("LLM ACTIONS\n ", new_actions)

        # Execute the old actions map
        # timestep = env.step(new_actions)
        ## --------- END OF OUR CODE ---------

        # Record the game
        if self.record:
            if self.record_counter % 5 == 0:
                self.game_recorder.record(self.timestep, description)
            self.record_counter += 1

        # Check if the game is finished
        if self.timestep.step_type == dm_env.StepType.LAST:
            if self.reset_env_when_done:
                self.timestep = self.env.reset()
            else:
                return None

        # Get the rewards
        rewards = _get_rewards(self.timestep)
        reward = rewards[str(self.player_index + 1)]
        for i, prefix in enumerate(self.player_prefixes):
            if self.verbose_fn:
                self.verbose_fn(self.timestep, i, self.player_index)
            self.score[prefix] += reward
            if i == self.player_index and reward != 0:
                logger.info(f'Player {prefix} Score: {self.score[prefix]}')

        # Print events if applicable
        if self.print_events and hasattr(self.env, 'events'):
            events = self.env.events()
            # Only print events on timesteps when there are events to print.
            if events:
                logger.info('Env events: %s', events)

        # pygame display
        if self.interactive == RenderType.PYGAME:
            # show visual observation
            if self.render_observation in self.timestep.observation:
                obs = self.timestep.observation[self.render_observation]
            elif f'{player_prefix}.{self.render_observation}' in self.timestep.observation:
                obs = self.timestep.observation[f'{player_prefix}.{self.render_observation}']
            else:
                # Fall back to default_observation.
                obs = self.timestep.observation[self.default_observation]
            obs = np.transpose(obs, (1, 0, 2))  # PyGame is column major!

            surface = pygame.surfarray.make_surface(obs)
            rect = surface.get_rect()

            surf = pygame.transform.scale(
                surface, (rect[2] * self.scale, rect[3] * self.scale))
            self.game_display.blit(surf, dest=(0, 0))

            # show text
            if self.text_display_fn:
                if self.player_count == 1:
                    text_str = self.text_display_fn(self.timestep, 0)
                else:
                    text_str = self.text_display_fn(self.timestep, self.player_index)
                img = self.font.render(text_str, True, self.text_color)
                self.game_display.blit(img, (self.text_x_pos, self.text_y_pos))

            # tick
            pygame.display.update()
            self.clock.tick(self.fps)

        # Return the observations of each player
        return self.observationsGenerator.get_all_observations_descriptions(str(description).strip())
