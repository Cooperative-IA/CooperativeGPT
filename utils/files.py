import json
import os


def load_agent_context(agent_context_file: str) -> dict:
    """Loads the agent context from a json file.

    Args:
        agent_context_file (str): Path to the json agent context file.

    Returns:
        dict: Dictionary with the agent context.
    """
    with open(agent_context_file, "r") as file:
        agent_context = json.load(file)
    return agent_context

def load_world_context(world_context_file: str) -> str:
    """Loads the world context from a text file.

    Args:
        world_context_file (str): Path to the text world context file.

    Returns:
        str: String with the world context.
    """
    with open(world_context_file, "r", encoding="utf-8", errors='replace') as file:
        world_context = file.read().strip()
    return world_context

def load_config() -> dict:
    """Loads the global config file.

    Returns:
        dict: Dictionary with the config file.
    """

    with open("config/config.json") as json_file:
        config_file = json.load(json_file)
    return config_file

def get_players_context_paths(agents_bio_dir: str) -> list[str]:
    """
    Get the paths of the players context files from the agents bio directory.
    The players context files are the .json files that contain the players context.
    
    Args:
        agents_bio_dir (str): Path to the agents bio directory.
        
    Returns:
        list[str]: List with the paths of the players context files. 
    """
    
    paths_list = [os.path.abspath(os.path.join(agents_bio_dir, player_file)) for player_file in os.listdir(agents_bio_dir)]
    
    # Sort the list by the player's id, ids is in string, "agent_1", "agent_2", etc. This list only contain .jsons files names. Data shoud be evaluated to sort.
    evaluated_data = [json.load(open(player_context)) for player_context in paths_list]
    
    # Now we zip the evaluated data with the paths_list and sort the zipped list by the player's id
    paths_list = [path for _, path in sorted(zip(evaluated_data, paths_list), key=lambda x: x[0]["id"])]
    
    return paths_list
    

def extract_players(players_context:list[str]) -> list[str]:
    """Extracts the players names from the players context list.
    Read each player context file as json and extract the player name

    Args:
        players_context (list[str]): List with the players context. Each element is a .json directory with the player context.

    Returns:
        list[str]: List with the players names.
    """
    list_of_players = [json.load(open(player_context)) for player_context in players_context]
    # Sort the list by the player's id, ids is in string, "agent_1", "agent_2", etc
    #list_of_players.sort(key=lambda x: x["id"])
    # Return the names of the players
    return  [player["name"] for player in list_of_players]


def persist_short_term_memories(memories:dict, rounds_count:int, steps_count:int, log_timestamp:str):
    """
    Saves the short term memories of the agents to a file.
    First creates the file if it doesn't exist, then appends the memories to the file.
    By appending a line with {"rounds_count": rounds_count, "steps_count": steps_count, "memories": memories} to the file.
    Memories dict is a dict with the agent name as key and the agent short term memories as value.

    Args:
        memories (dict): Dictionary with the short term memories of the agents.
        rounds_count (int): Number of rounds.
        steps_count (int): Number of steps.
    """

    log_folder = f"logs/{log_timestamp}"
    file_path = f"{log_folder}/short_term_memories.txt"

    os.makedirs(log_folder, exist_ok=True)

    for agent_name in memories.keys():
        memories[agent_name]['current_steps_sequence'] = ""
        memories[agent_name]['actions_sequence'] = ""

    # Open the file in append+read mode
    with open(file_path, "a+") as file:
        # Move the file pointer to the beginning of the file to read its content
        file.seek(0)
        previous_memories = file.read()
        dict_to_write = {"rounds_count": rounds_count, "steps_count": steps_count, "memories": memories}

        if previous_memories:
            file.write("\n")
        # Write (or append) the new dictionary to the file
        file.write(str(dict_to_write))



@staticmethod
def create_directory_if_not_exists(directory_path:str):
    """
    Creates a directory if it doesn't exist.

    Args:
        directory_path (str): Path to the directory.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
