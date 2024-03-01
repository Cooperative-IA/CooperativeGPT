import json

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


def extract_players(players_context:list[str]) -> list[dict]:
    """Extracts the players names from the players context list.
    Read each player context file as json and extract the player name

    Args:
        players_context (list[str]): List with the players context. Each element is a .json directory with the player context.

    Returns:
        list[dict]: List with the info of the players.
    """
    return [json.load(open(player_context)) for player_context in players_context]