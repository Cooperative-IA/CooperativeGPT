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


def extract_players(players_context:list[str]) -> list[str]:
    """Extracts the players names from the players context list.
    Read each player context file as json and extract the player name

    Args:
        players_context (list[str]): List with the players context. Each element is a .json directory with the player context.

    Returns:
        list[str]: List with the players names.
    """
    return [json.load(open(player_context))['name'] for player_context in players_context]


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
            
    
    