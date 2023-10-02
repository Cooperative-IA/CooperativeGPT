import os
import cv2
import time
import shutil
import numpy as np
from skimage import io
from skimage.transform import resize


class Recorder:

    def __init__(self, log_path, substrate_config):
        self.substrate_config = substrate_config
        self.n_players = self.substrate_config.lab2d_settings.numPlayers
        self.experiment_id = int((time.time() % 1000) * 1000)
        self.log_path = os.path.join(log_path, str(self.experiment_id))
        self.step = 0
        self.logs = {}
        self.create_log_tree()

    def create_log_tree(self):
        self.create_or_replace_directory(self.log_path)
        self.create_or_replace_directory(os.path.join(self.log_path, "world"))
        self.logs["world"] = []
        self.logs["avatars"] = {}
        for player_id in range(self.n_players):
            self.logs["avatars"][player_id] = []
            self.create_or_replace_directory(os.path.join(self.log_path, str(player_id)))

    def record(self, timestep, description):
        world_view = timestep.observation["WORLD.RGB"]
        self.logs["world"].append(world_view)
        for player_id in range(self.n_players):
            agent_observation = timestep.observation[f"{player_id + 1}.RGB"]
            description_image = self.add_description(description[player_id])
            agent_observation = resize(agent_observation, (description_image.shape[0], description_image.shape[1]),
                                       anti_aliasing=True)
            agent_observation = (agent_observation * 255).astype(np.uint8)
            agent_observation = np.hstack([agent_observation, description_image])
            self.logs["avatars"][player_id].append(agent_observation)
        self.step += 1

    def save_log(self):

        self.save_images(self.logs["world"], os.path.join(self.log_path, "world"))
        for avatar_id, avatar_images in self.logs["avatars"].items():
            self.save_images(avatar_images, os.path.join(self.log_path, str(avatar_id)))

    @staticmethod
    def save_images(images, path):
        for i, image in enumerate(images):
            io.imsave(os.path.join(path, f"{i}.png"), image)

    def add_description(self, description):
        canvas = np.ones((600, 600, 3), dtype=np.uint8) * 255
        sub_str = "You were taken out of the game by "
        observation = description["observation"]
        other_agents = description["agents_in_observation"]
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
