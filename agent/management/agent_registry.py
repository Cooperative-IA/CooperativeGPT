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
        self.agents_turn = []
        self.agent_id_to_name = {str(agent_id):agent_name for agent_id, agent_name in enumerate(players)}
        self.agent_name_to_id = {agent_name:str(agent_id) for agent_id, agent_name in enumerate(players)}

    def register_agent(self, agent:Agent):
        """
        Registers an agent in the registry.
        """
        self.agents[agent.name] = agent
        self.agents_turn.append(agent.name)

    def get_agents(self, names:list[str]) -> dict[str, Agent]:
        """
        Returns a list of agents given their names.
        """
        return {name:self.agents[name] for name in names}
    
    def get_agent_turn(self, agent_name:str) -> int:
        """
        Returns the turn of the agent.
        """
        return self.agents_turn.index(agent_name)

    def get_all_agents(self) -> dict[str, Agent]:
        """
        Returns a list of all agents.
        """
        return self.agents
