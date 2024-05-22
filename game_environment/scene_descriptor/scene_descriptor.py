import re
import numpy as np
import logging
from game_environment.utils import parse_string_to_matrix, matrix_to_string
from utils.logging import CustomAdapter

logger = logging.getLogger(__name__)
logger = CustomAdapter(logger)

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
        self.last_partial_observation = None
        self.agents_in_observation = None
        self.murder = None
        self.avatar_state = 1
        self.just_died = False
        self.just_revived = False


    def set_agents_in_observation(self, agents):
        self.agents_in_observation = agents

    def set_state(self, avatar_state):
        # If the avatar has reappear, set the just_revived flag and reset the murderer name
        if avatar_state == 1 and self.avatar_state == 0:
            self.murder = None
            self.just_revived = True
        # If the avatar just died, set the just_died attribute
        elif avatar_state == 0 and self.avatar_state == 1:
            self. just_died = True
        else:
            self.just_died = False
            self.just_revived = False
        self.avatar_state = avatar_state

    def set_murder(self, murder):
        self.murder = murder

    def set_partial_observation(self, partial_observation):
        self.partial_observation = partial_observation

    def set_last_partial_observation(self, partial_observation):
        self.last_partial_observation = partial_observation

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
    
    def __str__(self):
        return (f"Avatar(name={self.name}, view={self.avatar_view}, position={self.position}, "
                f"orientation={self.orientation}, reward={self.reward}, "
                f"partial_observation={self.partial_observation}, "
                f"agents_in_observation={self.agents_in_observation}, murder={self.murder}, "
                f"state={self.avatar_state})")


class SceneDescriptor:

    def __init__(self, substrate_config):
        self.substrate_config = substrate_config
        self.n_players = substrate_config.lab2d_settings.numPlayers
        self.avatars = self.get_avatars(substrate_config.player_names)
        self.last_map = None # Map of the inmediately last step
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
        self.compute_partial_observations(map, self.last_map)

        self.last_map = map

        result = {}
        for avatar_id, avatar in self.avatars.items():
            logger.info(f"Avatar {avatar_id} is in position {avatar.position}")
            result[avatar.name] = {"observation": avatar.partial_observation,
                                 "agents_in_observation": avatar.agents_in_observation,
                                 "global_position": avatar.position,
                                 "orientation": int(avatar.orientation),
                                 "last_observation": avatar.last_partial_observation,
                                 "effective_zap": avatar.name in [a.murder for a in self.avatars.values() if a.just_died],
                                }
        return result, map

    def parse_zaps(self, zaps):
        for victim_index, row in enumerate(zaps):
            for murder_index, value in enumerate(row):
                murder_name = self.avatars[murder_index].name
                if value > 0:
                    self.avatars[victim_index].set_murder(murder_name)

    def compute_partial_observations(self, map, last_map):
        for avatar_id, avatar in self.avatars.items():
            if avatar.avatar_state == 0:
                if avatar.just_died:
                    obs_text = f"There are no observations: You were attacked by agent {avatar.murder} and currently you're out of the game."
                else:
                    obs_text = "There are no observations: you're out of the game."
                avatar.set_partial_observation(obs_text)
                avatar.set_agents_in_observation({})
            else:
                min_padding = max(avatar.avatar_view.values())
                padded_map = self.pad_matrix_to_square(map, min_padding)
                padded_map = np.rot90(padded_map, k=int(avatar.orientation))
                observation, agents_in_observation = self.crop_observation(padded_map, avatar_id, avatar.avatar_view)
                avatar.set_partial_observation(observation)
                avatar.set_agents_in_observation(agents_in_observation)

                # Get the past observations of the observed map to calculate state changes
                if last_map is not None and not avatar.just_revived:
                    last_padded_map = self.pad_matrix_to_square(last_map, min_padding)
                    last_padded_map = np.rot90(last_padded_map, k=int(avatar.orientation))
                    last_observation, _ = self.crop_observation(last_padded_map, avatar_id, avatar.avatar_view)
                    avatar.set_last_partial_observation(last_observation)
                # If the avatar just revived, set the last observation to None
                elif last_map is not None and avatar.just_revived:
                    avatar.set_last_partial_observation(None)

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
    def calculate_coins_colors(self, current_matrix_map, map_rgb):
        """
        Calculate the coins and colors in the map based on the text and RGB map 
        coins are represented with a character "c" in the current_matrix_map. The colors will be extracted from the RGB map
        which is a representation of the pixels in the map. We are using the shapes to identify the colors in the map.
        
        Args:
            current_matrix_map (np.array): Matrix map with chars with the current state of the game, where the coins are represented with "c"
            map_rgb (np.array): RGB map, pixels in the map with colors in [R, G, B] format.
        
        Returns:
            np.array: Matrix map with the coins and colors replaced by the corresponding character.
            Possible colors are "red"  (238, 102, 119) that is replaced by "r" and "yellow" that is replaced by "y" (204, 187, 68),
        """
        # Get the coins in the map
        coins = np.where(current_matrix_map == "c")
        coins = list(zip(coins[1], coins[0]))  # Reversed coordinates (y, x) due to numpy indexing
        
        matrix_map_width = current_matrix_map.shape[1]
        matrix_map_height = current_matrix_map.shape[0]
        
        rgb_map_width = map_rgb.shape[1]
        rgb_map_height = map_rgb.shape[0]
        
        # Scale factor for coordinates conversion
        scale_x = rgb_map_width / matrix_map_width
        scale_y = rgb_map_height / matrix_map_height
        
        for coin in coins:
            x, y = coin
            # Scale coordinates to match RGB map
            x_rgb = int(x * scale_x)
            y_rgb = int(y * scale_y)
            x_rgb_end = int((x + 1) * scale_x)-1
            y_rgb_end = int((y + 1) * scale_y)-1
            # Check if the scaled coordinates are within the boundaries of the RGB map
            if 0 <= x_rgb < rgb_map_width and 0 <= y_rgb < rgb_map_height:
                # Print all the colors between the scaled coordinates                
                for i in range(x_rgb, x_rgb_end):
                    for j in range(y_rgb, y_rgb_end):
                        color_char = self.get_color_name(map_rgb[j, i])
                        if color_char == "r" or color_char == "y":
                            current_matrix_map[y, x] = color_char
                            break

                
        return current_matrix_map
    def get_color_name(self, color):
        """
        Get the color name based on the RGB values
        
        Args:
            color (np.array): RGB values
        
        Returns:
            str: Color name
        """
        color = list(color)
        if color == [238, 102, 119]:
            return "r"
        elif color == [204, 187, 68]:
            return "y"
        else:
            return "u"  # Unknown color
    def parse_timestep(self, timestep):
        
        map = timestep.observation["GLOBAL.TEXT"].item().decode("utf-8")
        map = parse_string_to_matrix(map)
        zaps = timestep.observation["WORLD.WHO_ZAPPED_WHO"]
        
        states = timestep.observation["WORLD.AVATAR_STATES"]
        map = self.calculate_coins_colors(map, timestep.observation["WORLD.RGB"])
        for avatar_id, avatar in self.avatars.items():
            _id = avatar_id + 1
            position = timestep.observation[f"{_id}.POSITION"]
            if states[avatar_id]: # Only include the avatar in the map if it is alive
                map[position[1], position[0]] = avatar_id
            avatar.set_position(position[1], position[0])
            avatar.set_orientation(timestep.observation[f"{_id}.ORIENTATION"])
            avatar.set_reward(timestep.observation[f"{_id}.REWARD"])
            avatar.set_state(states[avatar_id])

        return map, zaps
    
