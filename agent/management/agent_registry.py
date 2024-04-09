from agent.agent import Agent

class AgentRegistry:
    """
    A registry for agents.
    """
    def __init__(self, players:list[str]):
        """
        Constructor for the AgentRegistry class.
        """
        self.agents = {}
        self.agent_id_to_name = {str(agent_id):agent_name for agent_id, agent_name in enumerate(players)}
        print(self.agent_id_to_name)

    def register_agent(self, agent:Agent):
        """
        Registers an agent in the registry.
        """
        self.agents[agent.name] = agent

    def get_agents(self, names:list[str]) -> dict[str, Agent]:
        """
        Returns a list of agents given their names.
        """
        return {name:self.agents[name] for name in names}

    def get_all_agents(self) -> dict[str, Agent]:
        """
        Returns a list of all agents.
        """
        return self.agents
