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