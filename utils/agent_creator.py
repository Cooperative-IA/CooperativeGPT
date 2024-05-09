from agent.agent import Agent
from agent.human_agent import HumanAgent

def agentCreator(is_human_player:bool, *args, **kwargs) -> Agent | HumanAgent:
    """
    Function to create different types of agents.

    Args:
        is_human_player (bool): True if the agent is a human player, False otherwise.
        Optional args and kwargs to pass to the determined agent constructor.
    """

    if is_human_player:
        if "mode" in kwargs:
            del kwargs["mode"]
        return HumanAgent(*args, **kwargs)
    else:
        return Agent(*args, **kwargs)