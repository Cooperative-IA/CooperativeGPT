import re
import numpy as np
import logging
from game_environment.utils import parse_string_to_matrix, matrix_to_string

logger = logging.getLogger(__name__)

class Avatar:
    def __init__(self, name:str, avatar_config):
        """
        Avatar class to store information about the player in the game

        Args:
            name (str): Name of the player
            avatar_config (dict): Avatar configuration
        """
        self.name = name
        self.avatar_component = list(filter(lambda component: component["component"] == "Avatar",
                                            avatar_config["components"]))[0]
        self.avatar_view = self.avatar_component["kwargs"]["view"]

        self.position = None
        self.orientation = None
        self.reward = None
        self.partial_observation = None
        self.agents_in_observation = None
        self.murder = None
        self.avatar_state = 1

    def set_agents_in_observation(self, agents):
        self.agents_in_observation = agents

    def set_state(self, avatar_state):
        if avatar_state == 1 and self.avatar_state == 0:
            self.murder = None
        self.avatar_state = avatar_state

    def set_murder(self, murder):
        self.murder = murder

    def set_partial_observation(self, partial_observation):
        self.partial_observation = partial_observation

    def set_position(self, x, y):
        self.position = (x, y)

    def set_orientation(self, orientation):
        self.orientation = orientation

    def set_reward(self, reward):
        self.reward = reward

    def reset_observation_variables(self):
        self.position = None
        self.orientation = None
        self.reward = None
        self.partial_observation = None
        self.agents_in_observation = None


class SceneDescriptor:

    def __init__(self, substrate_config):
        self.substrate_config = substrate_config
        self.n_players = substrate_config.lab2d_settings.numPlayers
        self.avatars = self.get_avatars(substrate_config.player_names)
        for avatar_id, avatar in self.avatars.items():
            logger.info(f"{avatar.name} is player {avatar_id}")

    def get_avatars(self, names):
        avatars = {}
        for i, config in enumerate(self.substrate_config.lab2d_settings.simulation.gameObjects):
            avatars[i] = Avatar(names[i], config)
        return avatars

    def describe_scene(self, timestep):
        self.reset_population()
        map, zaps = self.parse_timestep(timestep)
        self.parse_zaps(zaps)
        self.compute_partial_observations(map)

        result = {}
        for avatar_id, avatar in self.avatars.items():
            logger.info(f"Avatar {avatar_id} is in position {avatar.position}")
            result[avatar_id] = {"observation": avatar.partial_observation,
                                 "agents_in_observation": avatar.agents_in_observation,
                                 "global_position": avatar.position,
                                 "orientation": int(avatar.orientation)}
        return result

    def parse_zaps(self, zaps):
        for victim_index, row in enumerate(zaps):
            for murder_index, value in enumerate(row):
                murder_name = self.avatars[murder_index].name
                if value > 0:
                    self.avatars[victim_index].set_murder(murder_name)

    def compute_partial_observations(self, map):
        for avatar_id, avatar in self.avatars.items():
            if avatar.avatar_state == 0:
                obs_text = f"You were taken out of the game by {avatar.murder}"
                avatar.set_partial_observation(obs_text)
            else:
                min_padding = max(avatar.avatar_view.values())
                padded_map = self.pad_matrix_to_square(map, min_padding)
                padded_map = np.rot90(padded_map, k=int(avatar.orientation))
                observation, agents_in_observation = self.crop_observation(padded_map, avatar_id, avatar.avatar_view)
                avatar.set_partial_observation(observation)
                avatar.set_agents_in_observation(agents_in_observation)

    def crop_observation(self, map, avatar_id, avatar_view):
        # get avatar position in matrix
        avatar_pos = np.where(map == str(avatar_id))
        avatar_pos = list(zip(avatar_pos[1], avatar_pos[0]))[0]
        upper_bound = avatar_pos[1] - avatar_view.get("forward")
        left_bound = avatar_pos[0] - avatar_view.get("left")
        lower_bound = avatar_pos[1] + avatar_view.get("backward") + 1
        right_bound = avatar_pos[0] + avatar_view.get("right") + 1
        observation = matrix_to_string(map[upper_bound:lower_bound, left_bound:right_bound])
        observation = observation.replace(str(avatar_id), "#")
        agents_in_observation = self.get_agents_in_observation(observation)
        return observation, agents_in_observation

    def get_agents_in_observation(self, observation):
        digits_list = []
        pattern = r'\d+'

        for string in observation:
            digits = re.findall(pattern, string)
            digits_list.extend(digits)

        agents = {}
        for digit in digits_list:
            agents[digit] = self.avatars[int(digit)].name

        return agents


    @staticmethod
    def pad_matrix_to_square(matrix, min_padding, padding_char="-"):
        num_rows, num_cols = matrix.shape

        max_dim = max(num_rows, num_cols)
        padding_needed = max_dim - min(num_rows, num_cols)
        total_padding = max(padding_needed, min_padding)

        new_dim = max_dim + 2 * total_padding

        padded_matrix = np.full((new_dim, new_dim), padding_char, dtype=matrix.dtype)

        start_row = total_padding
        start_col = total_padding
        padded_matrix[start_row:start_row + num_rows, start_col:start_col + num_cols] = matrix

        return padded_matrix

    def reset_population(self):
        for avatar_id, avatar in self.avatars.items():
            avatar.reset_observation_variables()

    def parse_timestep(self, timestep):
        map = timestep.observation["GLOBAL.TEXT"].item().decode("utf-8")
        map = parse_string_to_matrix(map)
        zaps = timestep.observation["WORLD.WHO_ZAPPED_WHO"]
        states = timestep.observation["WORLD.AVATAR_STATES"]
        for avatar_id, avatar in self.avatars.items():
            _id = avatar_id + 1
            position = timestep.observation[f"{_id}.POSITION"]
            map[position[1], position[0]] = avatar_id
            avatar.set_position(position[1], position[0])
            avatar.set_orientation(timestep.observation[f"{_id}.ORIENTATION"])
            avatar.set_reward(timestep.observation[f"{_id}.REWARD"])
            avatar.set_state(states[avatar_id])

        return map, zaps