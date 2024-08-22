import os
from typing import Mapping
import cv2
from datetime import datetime
import shutil
import numpy as np
from skimage import io
from skimage.transform import resize
from game_environment.recorder import recreate_simulation
from game_environment.utils import parse_string_to_matrix, matrix_to_string, connected_elems_map
import importlib
from utils.files import create_directory_if_not_exists

class Recorder:

    def __init__(self, log_path, init_timestamp, substrate_config, substrate_name, player_names):
        self.substrate_name = substrate_name
        self.substrate_config = substrate_config
        self.n_players = self.substrate_config.lab2d_settings.numPlayers
        self.experiment_id = init_timestamp
        self.log_path = os.path.join(log_path, str(self.experiment_id))
        self.step = 0
        self.create_log_tree()
        self.player_names = player_names
        self.agents_ids = {name: str(agent_id) for agent_id, name in enumerate(player_names)}

        # Import custom recorder functions for the substrate
        # Try to import the custom recorder functions for the substrate
        try:
            custom_recorder_module = importlib.import_module(f"game_environment.substrates.{substrate_name}_utilities.recorder")
            self._record = custom_recorder_module.record if hasattr(custom_recorder_module, 'record') else None
            self._record_game_state_before_actions = custom_recorder_module.record_game_state_before_actions if hasattr(custom_recorder_module, 'record_game_state_before_actions') else None
            self._record_elements_status = custom_recorder_module.record_elements_status if hasattr(custom_recorder_module, 'record_elements_status') else None
            self._save_custom_indicators = custom_recorder_module.save_custom_indicators if hasattr(custom_recorder_module, 'save_custom_indicators') else None
        except ModuleNotFoundError:
            pass

    def create_log_tree(self):
        create_directory_if_not_exists(self.log_path)
        self.create_or_replace_directory(os.path.join(self.log_path, "world"))
        for player_id in range(self.n_players):
            self.create_or_replace_directory(os.path.join(self.log_path, str(player_id)))

    def record(self, timestep, description):
        world_view = timestep.observation["WORLD.RGB"]
        world_path = os.path.join(self.log_path, "world", f"{self.step}.png")
        self.save_image(world_view, world_path)

        for player_id, name in enumerate(self.player_names):
            agent_observation = timestep.observation[f"{player_id + 1}.RGB"]
            description_image = self.add_description(description[name])
            agent_observation = resize(agent_observation, (description_image.shape[0], description_image.shape[1]), anti_aliasing=True)
            agent_observation = (agent_observation * 255).astype(np.uint8)
            agent_observation = np.hstack([agent_observation, description_image])
            avatar_path = os.path.join(self.log_path, str(player_id), f"{self.step}.png")
            self.save_image(agent_observation, avatar_path)

        self.step += 1

        if self._record:
            self._record(self, timestep, description)

    def record_rewards(self, rewards: Mapping[str, float])->None:
        #Writes the rewards to a file
        with open(os.path.join(self.log_path, "rewards_history.txt"), "a") as f:
            rewards = {i: int(rr) for i, rr in enumerate(list(rewards.values()))}
            f.write(f"{self.step}: {rewards}\n")

    def record_scene_tracking(self, time:datetime, current_map: list[list[str]], agents_status=None) -> None:
        #Writes the map to a file
        with open(os.path.join(self.log_path, "scene_track.txt"), "a") as f:
            scene_dict = {'step':self.step,  'memory_time': str(time), 'current_map': matrix_to_string(current_map), 'agents_status': agents_status}
            f.write(f"{scene_dict}\n")

    def record_elements_status(self, initial_map, current_map):
        """
        Record some elements status of the map

        Args:
            initial_map (str): Initial map
            current_map (list[list[str]]): Current map
        """
        if self._record_elements_status:
            self._record_elements_status(self, initial_map, current_map)
        elif self.substrate_name == 'clean_up':
            apples = 0
            dirt = 0

            for row in current_map:
                for elem in row:
                    if elem == 'A':
                        apples += 1
                    elif elem == 'D':
                        dirt += 1
            
            with open(os.path.join(self.log_path, "apples_history.txt"), "a") as f:
                f.write(f"{self.step}: A_{apples} - D_{dirt}\n ")

    def record_game_state_before_actions(self, initial_map: list[list[str]], current_map: list[list[str]], current_actions_map: dict, scene_description: dict):
        """
        Record the game state before the agents take any action

        Args:
            initial_map (list[list[str]]): Initial map
            current_map (list[list[str]]): Current map
            current_actions_map (dict): Actions that the agents are going to take
            scene_description (dict): Current state of the game before any actions are taken
        """
        if self._record_game_state_before_actions:
            self._record_game_state_before_actions(self, initial_map, current_map, current_actions_map, scene_description)

    def save_log(self):
        recreate_simulation.recreate_records(record_path=self.log_path, players=self.substrate_config.player_names, is_focal_player=self.substrate_config.is_focal_player)
        if self._save_custom_indicators:
            self._save_custom_indicators(self)

    @staticmethod
    def save_image(image, path):
        io.imsave(path, image)

        
    def add_description(self, description):
        canvas = np.ones((600, 600, 3), dtype=np.uint8) * 255
        sub_str = "You were attacked by agent "
        observation = description["observation"]
        other_agents = description.get("agents_in_observation", {})
        if sub_str in observation:
            murder = observation.replace(sub_str, "")
            self.put_text_on_image(canvas, sub_str, x=20, y=20)
            self.put_text_on_image(canvas, murder, x=20, y=40)
        else:
            lines = observation.split("\n")
            y = 30
            for line in lines:
                x = 10
                for char in line:
                    self.put_text_on_image(canvas, char, x=x, y=y)
                    x += 50
                y += 40
            for agent_id, name in other_agents.items():
                self.put_text_on_image(canvas, f"{agent_id}: {name}", x=10, y=y)
                y += 40
        return canvas

    @staticmethod
    def put_text_on_image(image, text, x, y):
        cv2.putText(image, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, 2)

    @staticmethod
    def create_or_replace_directory(directory_path):
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)
        os.makedirs(directory_path)
