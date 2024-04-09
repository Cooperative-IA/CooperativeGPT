class CommunicationMode:

    class Who:
        ALL = "ALL"
        LLM = "LLM"
        NEAR = "NEAR"
        KNOWN = "KNOWN"

    class What:
        ALL = "ALL"
        LLM = "LLM"
        IMPORTANT = "IMPORTANT"

def whom_to_communicate(sender_agent, agent_registry, who_mode:str) -> list[str]:
    """
    Description: Returns the list of the names of the agents with whom the agent should communicate given the communication mode

    Args:
        sender_agent (Agent): Agent that wants to communicate
        agent_registry (AgentRegistry): Registry of agents
        who_mode (str): Communication mode (who?)
    """
    if who_mode == CommunicationMode.Who.ALL:
        return [name_ for name_ in agent_registry.get_all_agents().keys() if name_ != sender_agent.name]
    elif who_mode == CommunicationMode.Who.KNOWN:
        #TODO: Known agents are not consistent with NEAR agents seen before (becasue of the attention bandwith)
        return sender_agent.stm.get_known_agents()
    elif who_mode == CommunicationMode.Who.NEAR:
        return [agent_registry.agent_id_to_name[id_agent] for id_agent in sender_agent.spatial_memory.near_agents]
    #TODO: Implement LLM decision
    #elif mode == CommunicationMode.Who.LLM:
    #    pass

def what_to_communicate(sender_agent, what_mode:str) -> list[str]:
    """
    Description: Returns the list of the type of observations that the agent should communicate given the communication mode

    Args:
        sender_agent (Agent): Agent that wants to communicate
        what_mode (str): Communication mode (what?)
    """
    if what_mode == CommunicationMode.What.ALL:
        return ["A", "G", "W", "F"]
    elif what_mode == CommunicationMode.What.IMPORTANT:
        return ["A", "G"]
    #TODO: Implement LLM decision
    #elif what_mode == CommunicationMode.What.LLM:
    #    pass

def communicate_observations(sender_agent_name:str, receiver_agent_name:str, agent_registry, what_mode:str) -> None:
    """
    Description: Communicates the observations between two agents given the communication mode

    Args:
        sender_agent_name (str): Name of the sender agent
        receiver_agent_name (str): Name of the receiver agent
        agent_registry (AgentRegistry): Registry of agents
        what_mode (str): Communication mode (what?)
    """
    sender_agent = agent_registry.get_agents([sender_agent_name])[sender_agent_name]
    agent_receiver = agent_registry.get_agents([receiver_agent_name])[receiver_agent_name]

    sender_agent_known_map = sender_agent.spatial_memory.known_map
    agent_receiver_known_map = agent_receiver.spatial_memory.known_map

    rows, cols = len(sender_agent.spatial_memory.known_map), len(sender_agent.spatial_memory.known_map[0])

    for x in range(rows):
        for y in range(cols):

            if agent_receiver_known_map[x][y] in what_to_communicate(sender_agent, what_mode):
                sender_agent.spatial_memory.update_pixel_if_newer(x, y, agent_receiver_known_map[x][y], agent_receiver.spatial_memory.timestamp_map[x][y])

            if sender_agent_known_map[x][y] in what_to_communicate(agent_receiver, what_mode):
                agent_receiver.spatial_memory.update_pixel_if_newer(x, y, sender_agent_known_map[x][y], sender_agent.spatial_memory.timestamp_map[x][y])

