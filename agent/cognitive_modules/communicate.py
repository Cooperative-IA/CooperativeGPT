import os
import re

from llm import LLMModels
from utils.utils_llm import extract_answers

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

def what_to_communicate(sender_agent, agent_registry, what_mode:str) -> list[str]:
    """
    Description: Returns the list of the type of observations that the agent should communicate given the communication mode

    Args:
        sender_agent (Agent): Agent that wants to communicate
        what_mode (str): Communication mode (what?)
    """
    if what_mode == CommunicationMode.What.ALL:
        return ["A", "G", "W", "F"]+[str(i) for i in range(len(agent_registry.get_all_agents()))]
    elif what_mode == CommunicationMode.What.IMPORTANT:
        return ["A", "G"]
    #TODO: Implement LLM decision
    #elif what_mode == CommunicationMode.What.LLM:
    #    pass

def communicate_environment_observations_to_agent(sender_agent_name:str, receiver_agent_name:str, agent_registry, what_mode:str) -> None:
    """
    Description: Communicates the observations between two agents given the communication mode

    Args:
        sender_agent_name (str): Name of the sender agent
        receiver_agent_name (str): Name of the receiver agent
        agent_registry (AgentRegistry): Registry of agents
        what_mode (str): Communication mode (what?)
    """
    sender_agent = agent_registry.get_agents([sender_agent_name])[sender_agent_name]
    receiver_agent = agent_registry.get_agents([receiver_agent_name])[receiver_agent_name]

    sender_agent_known_map = sender_agent.spatial_memory.known_map
    receiver_agent_known_map = receiver_agent.spatial_memory.known_map

    rows, cols = len(sender_agent.spatial_memory.known_map), len(sender_agent.spatial_memory.known_map[0])

    for x in range(rows):
        for y in range(cols):

            if receiver_agent_known_map[x][y] in what_to_communicate(sender_agent, agent_registry, what_mode):
                sender_agent.spatial_memory.update_pixel_if_newer(x, y, receiver_agent_known_map[x][y], receiver_agent.spatial_memory.timestamp_map[x][y])

            if sender_agent_known_map[x][y] in what_to_communicate(receiver_agent, agent_registry, what_mode):
                receiver_agent.spatial_memory.update_pixel_if_newer(x, y, sender_agent_known_map[x][y], sender_agent.spatial_memory.timestamp_map[x][y])

def communicate_observed_actions_to_agent(sender_agent_name:str, receiver_agent_name:str, agent_registry, observations:list[str], state_changes:list[str], game_time, rounds_count, poignancy) -> None:
    receiver_agent = agent_registry.get_agents([receiver_agent_name])[receiver_agent_name]

    for observation in observations:
        if "You were attacked" in observation:
            agent_name_match = re.search(r"attacked by agent (.*?) and currently", observation).group(1)
            if receiver_agent_name != agent_name_match:
                if receiver_agent.stm.add_known_agent_interaction(rounds_count, sender_agent_name, "attacks_received", agent_name_match):
                    receiver_agent.stm.add_known_agent_interaction(rounds_count, agent_name_match, "attacks_made", sender_agent_name)
                    receiver_agent.ltm.add_memory(f'Agent {sender_agent_name} told me that he was attacked by {agent_name_match} at round {rounds_count}', game_time, poignancy, {'type': 'observation'})

    for state_change in state_changes:
        _rounds_count = rounds_count
        if "took an apple from position" in state_change:
            agent_name_match = re.search(r"agent (\S+)", state_change).group(1)
            if receiver_agent_name != agent_name_match:
                apple_position = "".join(re.search(r'\[(\d+),\s*(\d+)\]', state_change).groups())
                if agent_registry.get_agent_turn(sender_agent_name) < agent_registry.get_agent_turn(receiver_agent_name):
                    _rounds_count -= 1
                if receiver_agent.stm.add_known_agent_interaction(_rounds_count, agent_name_match, "ate_apple", apple_position):
                    receiver_agent.ltm.add_memory(f'Agent {sender_agent_name} told me that {agent_name_match} ate an apple at round {rounds_count}', game_time, poignancy, {'type': 'observation'})

def communicate_own_actions_to_agent(sender_agent_name:str, receiver_agent_name:str, agent_registry, actions:list[str], rounds_count, game_time, poignancy) -> None:
    receiver_agent = agent_registry.get_agents([receiver_agent_name])[receiver_agent_name]

    for action in actions:
        if "attacked" in action.lower():
            agent_name_match = re.search(r"agent (\S+)", action).group(1)
            if receiver_agent.stm.add_known_agent_interaction(rounds_count, sender_agent_name, "attacks_made", agent_name_match):
                receiver_agent.stm.add_known_agent_interaction(rounds_count, agent_name_match, "attacks_received", sender_agent_name)
                receiver_agent.ltm.add_memory(f'Agent {sender_agent_name} told me that he attacked {agent_name_match} at round {rounds_count}', game_time, poignancy, {'type': 'observation'})
        elif "ate" in action.lower():
            apple_position = "".join(re.search(r'\[(\d+),\s*(\d+)\]', action).groups())
            if receiver_agent.stm.add_known_agent_interaction(rounds_count, sender_agent_name, "ate_apple", apple_position):
                receiver_agent.ltm.add_memory(f'Agent {sender_agent_name} told me that he ate an apple at round {rounds_count}', game_time, poignancy, {'type': 'observation'})

def communicate_reflection_to_agent(sender_agent_name:str, receiver_agent_name:str, agent_registry, reflection:str, game_time:str, rounds_count:str, poignancy:int) -> None:
    receiver_agent = agent_registry.get_agents([receiver_agent_name])[receiver_agent_name]
    receiver_agent.ltm.add_memory(f'Reflection communicated by {sender_agent_name} at round {rounds_count}:{reflection}', game_time, poignancy, {'type': 'reflection'})


def get_agents_to_communicate_reflection(name:str, reflections: list, world_context: str, agent_bio: str, current_plan:str, agents_memories: dict, prompts_folder = "base_prompts_v0"):


    agents_memories_str = ""
    for agent in agents_memories:
        agents_memories_str += f"This is what currently I know about {agent} Agent: {', '.join(agents_memories[agent])}\n"
    reflections_str = ".\n".join(reflections)
    llm = LLMModels().get_main_model()
    prompt_path = os.path.join(prompts_folder, 'whom_to_communicate.txt')
    try:
        response = llm.completion(prompt=prompt_path, inputs=[name, reflections_str, world_context, current_plan, agent_bio, agents_memories_str, ", ".join(list(agents_memories.keys()))])
        agents_dict = extract_answers(response)
        return agents_dict
    except ValueError as e:
        if str(e) == 'Prompt is too long':
            llm = LLMModels().get_longer_context_fallback()
            response = llm.completion(prompt=prompt_path, inputs=[name, reflections_str, world_context, current_plan, agent_bio, agents_memories_str, ", ".join(list(agents_memories.keys()))])
            agents_dict = extract_answers(response)
        else:
            raise e
        return agents_dict
