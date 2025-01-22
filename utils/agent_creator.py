from agent.agent import Agent
from agent.human_agent_v2 import HumanAgentV2
from agent.human_agent__arrows_mov import HumanAgentArrowsMov

def agentCreator(is_human_player:bool, *args, **kwargs) -> Agent | HumanAgentV2|HumanAgentArrowsMov:
    """
    Function to create different types of agents.

    Args:
        is_human_player (bool): True if the agent is a human player, False otherwise.
        Optional args and kwargs to pass to the determined agent constructor.
    """

    if is_human_player:
        if "mode" in kwargs:
            del kwargs["mode"]
        return HumanAgentArrowsMov(*args, **kwargs)
    else:
        return Agent(*args, **kwargs)