

import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import logging
from utils.logging import CustomAdapter
import random
from matplotlib.ticker import MaxNLocator

logger = logging.getLogger(__name__)
logger = CustomAdapter(logger)

def read_rewards_from_file(file_path:str)-> tuple[dict, dict, list[str]]:
    """
    Read the rewards history file and returns a dictionary with the total reward and the individual reward for each step.
    Args:
        file_path: the path to the rewards history file.

    Returns:
        total_rewards: a dictionary that maps the step number with the total reward for that step.
        individual_rewards: a dictionary that maps the step number with the individual reward for each agent for that step.
        players_index: a list with the ids of the players.
    """
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        logger.error("File with the rewards history not found: %s", file_path)
        return {}, {}
            
    rewards_per_step = {}

    for line in lines:
        step, rewards_str = line.strip().split(':')[0], line[line.find(':')+1:]
        rewards_dict = eval(rewards_str.strip())
        rewards_per_step[step] = rewards_dict

    players_index = rewards_per_step['1'].keys()
    
    individual_rewards = {'1': rewards_per_step['1']}
    for step in range(2, len(rewards_per_step)):
        # Suma del anterior con el actual
        individual_rewards[str(step)] = {key: individual_rewards[str(step-1)][key] + rewards_per_step[str(step)][key] for key in players_index}


    total_rewards = {'1': sum(rewards_per_step['1'].values())}
    for step in range(2, len(rewards_per_step)):
        # Suma del anterior con el actual
        total_rewards[str(step)] = sum(individual_rewards[str(step)].values())
    
    return total_rewards, individual_rewards, players_index

def generate_video_from_images(image_folder:str, video_name:str, rewards:dict, players_index:list[str], round_map:dict, output_resolution:tuple, duration:float=0.2)->None:

    """
    Generate a video from a set of images.

    Parameters:
    - image_folder: the path to the folder containing the images.
    - video_name: the name (including path) of the video file to be created.
    - duration: the duration each image will be displayed in seconds.
    """

    # Obteniendo las imágenes de la carpeta
    images = [img for img in os.listdir(image_folder) if img.endswith(".png") or img.endswith(".jpg")]
    images.sort(key=lambda x: int(x.split('.')[0]))  # Asumiendo que el nombre del archivo es el "step" y no tiene puntos adicionales
    

    out = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'DIVX'), 1/duration, output_resolution)

    for i in range(len(images)):
        img_path = os.path.join(image_folder, images[i])
        img = cv2.imread(img_path)
        img_resized = cv2.resize(img, output_resolution, interpolation=cv2.INTER_NEAREST)  # Redimensiona la imagen a la resolución deseada

        # Añadiendo el texto a la imagen
        step = images[i].split('.')[0]
        reward = rewards.get(step, 0)
        per_capita_reward = reward / len(players_index)
        img_with_text = add_text_to_image(img_resized, round_map[str(int(step))], step, per_capita_reward)

        out.write(img_with_text)

    out.release()


def add_text_to_image (img:np.ndarray, round:str, step:str, reward_per_capita:float)->np.ndarray:
    """
    Adds text to the image.

    Args:
    - img: the image to which the text will be added.
    - round: the round number.
    - step: the step number.
    - reward_per_capita: the reward per capita for the current round.

    Returns:
    - img: the image with the text added.
    """

    height, _, _ = img.shape
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = f"Round: {round} - Step: {step} - Reward per capita: {reward_per_capita:,.2f}"
    cv2.putText(img, text, (12, int(height * 0.035)), font, 1, (255,255,255), 2, cv2.LINE_AA)
    return img

def read_rounds_history(file_path:str, image_folder:str):
    """
    Reads the rounds history file and returns a dictionary that maps the step number with the round number.
    
    Args:
        file_path: the path to the rounds history file.

    Returns:
        round_map: a dictionary that maps the step number with the round number.
    """
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        logger.warning("File with the steps history not found: %s", file_path)
        lines =  []
     
    # Obteniendo las imágenes de la carpeta
    images = [img for img in os.listdir(image_folder) if img.endswith(".png") or img.endswith(".jpg")]
    images.sort(key=lambda x: int(x.split('.')[0]))  # Asumiendo que el nombre del archivo es el "step" y no tiene puntos adicionales
    max_image_step = int(images[-1][:-4])
    
    round_map = {}
    for line in lines:
        round, step = line.strip().split(' ')
        round_map[step] = round
    max_step = len(images) - 1

    if max_image_step != max_step:
        round_map[str(max_image_step)] = str(int(round_map[str(max_step)]) + 1)
        max_step = max_image_step

    round_map['0'] = '0'
    for step in range(1, max_step+1):
        if str(step) not in round_map.keys():
            round_map[str(step)] = round_map[str(step-1)]
    return round_map

def generate_random_color():
    r = random.random()
    g = random.random()
    b = random.random()
    return (r, g, b)

def generate_rewards_plot (individual_rewards:dict, round_map:dict, record_folder:str, players: list[str], is_focal_player: list[bool])->None:
    # Uses round map to evaluate only the steps that are part of a round from individual rewards
    steps = list(individual_rewards.keys())
    steps = [int(s) for s in steps]
    num_players = len(players)
    num_focal_players = sum(is_focal_player)

    focal_per_capita_reward = [sum([r for i, r in enumerate(val.values()) if is_focal_player[i]])/num_focal_players for val in individual_rewards.values()]
    individual_rewards = [np.array(list(val.values())) for val in individual_rewards.values()]

    # Transform to numpy array
    individual_rewards = np.array(individual_rewards)

    # Graph
    plt.figure(figsize=(12, 6))
    # Vector of colors for each individual
    colors = [generate_random_color() for _ in range(num_players)]
    for i, name in enumerate(players):
        plt.plot(steps, individual_rewards[:, i], label=name, linewidth=2, linestyle="--", color=colors[i])
    plt.plot(steps, focal_per_capita_reward, label="Focal per capita reward", linewidth=2.5, linestyle="-", color="orange")
    plt.xticks(steps, rotation=90, ha='right')
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))

    plt.xlabel("Steps")
    plt.ylabel("Reward")
    plt.title("Individual reward vs Focal per capita mean reward")
    plt.legend()
    plt.grid(True)
    plt.savefig(record_folder + '/rewards_plot.png')



def recreate_records(record_path:str, players: list[str], is_focal_player: list[bool], image_folder:str = 'world', video_name:str = 'output_video.avi', output_resolution:tuple = (1600, 1200), rounds_file:str = 'steps_history.txt', rewards_file:str = 'rewards_history.txt')->None:
    """
    Recreates the simulation from the given record folder.

    Args:
    - record_folder: the path to the record folder.
    - image_folder: the path to the folder containing the images.
    - video_name: the name (including path) of the video file to be created.
    - output_resolution: the resolution of the output video.
    """
    rounds_path = os.path.join(record_path, rounds_file)
    rewards_path = os.path.join(record_path, rewards_file)
    image_path = os.path.join(record_path, image_folder)
    video_path = os.path.join(record_path, video_name)

    total_rewards, individual_rewards, players_index = read_rewards_from_file(rewards_path)
    round_map = read_rounds_history(rounds_path, image_path)
    generate_video_from_images(image_path, video_path, total_rewards, players_index, round_map, output_resolution, 0.2)
    generate_rewards_plot( individual_rewards, round_map, record_path, players, is_focal_player)