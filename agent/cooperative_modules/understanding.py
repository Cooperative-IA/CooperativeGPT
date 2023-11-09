from llm import LLMModels
from utils.time import str_to_timestamp
from utils.llm import extract_answers

def update_understanding(current_observations: list[str], agent, game_time: str, understanding_umbral = 30):
    """Updates the agent understanding about the world and the other agents. Updates the understanding only if the accumulated poignancy of the recent reflections is greater than the umbral, or 
    if the agent has no understanding about the world yet, in that case the current observations are used instead of the reflections.

    Args:
        current_observations (list[str]): List of the current observations.
        agent (Agent): Agent to update the understanding.
        game_time (str): Current game time.
        understanding_umbral (int, optional): Minimum poignancy to update the understanding (only reflections are taken in account). Defaults to 6.
    """
    # Decide if the understanding should be updated
    world_understanding = agent.stm.get_memory('world_context')
    last_understanding_update = agent.stm.get_memory('understanding_updated_on')
    last_timestamp = str_to_timestamp(last_understanding_update, agent.ltm.date_format)
    recent_reflections = agent.ltm.get_memories(filter={'$and': [{'type': 'reflection'}, {'timestamp': {'$gt': last_timestamp}}]})
    accumulated_poignancy = sum([reflection['poignancy'] for reflection in recent_reflections['metadatas']])
    if world_understanding is not None and accumulated_poignancy < understanding_umbral:
        return
        
    # Update the understanding

    # Create the agent knowledge about the other agents
    knowledge_about_agents = []
    memories_about_other_agents = ''
    known_agents = agent.stm.get_known_agents()
    for agent_name in known_agents:
        agent_knowledge = agent.stm.get_memory(f'knowledge_about_{agent_name}')
        memories_about_agent = agent.ltm.get_relevant_memories(query=agent_name, n_results=5)
        if memories_about_agent:
            memories_about_agent = '\n'.join(memories_about_agent)
            memories_about_other_agents += f"Memories related to {agent_name}:\n{memories_about_agent}"
        if agent_knowledge is not None:
            knowledge_about_agents.append(f"{agent_name}'s agent understanding: {agent_knowledge}")
    knowledge_about_agents = '\n'.join(knowledge_about_agents)

    # Condition a part of the prompt on the known agents to update the understanding about them
    other_agents_prompt = '\n'.join([f'"{agent_name}_knowledge": string, \\\\ Updates {agent.name}\'s understanding of {agent_name} preferences or behavior adding its past knowledge and the new insights' for agent_name in known_agents])

    observations = '\n'.join(current_observations)
    if recent_reflections:
        observations = '\n'.join(recent_reflections['documents'])

    # Use the remaining doubts
    remaining_doubts = agent.stm.get_memory('remaining_doubts')
    remaining_doubts_info = ""
    if remaining_doubts is not None:
        relevant_memories = agent.ltm.get_relevant_memories(query=remaining_doubts, n_results=10, filter={'type': 'reflection'})
        if relevant_memories:
            relevant_memories = '\n'.join(relevant_memories)
            remaining_doubts_info = f"These are the remaining doubts: {remaining_doubts}. Here are some reflections that may help to solve them:\n{relevant_memories}"
        relevant_memories = agent.ltm.get_relevant_memories(query=remaining_doubts, n_results=10, filter={'type': 'perception'})
        if relevant_memories:
            relevant_memories = '\n'.join(relevant_memories)
            remaining_doubts_info += f"\nAnd here are some observations that provide valuable information:\n{relevant_memories}"
    else:
        recent_observations = agent.ltm.get_memories(limit=10, filter={'$and': [{'type': 'perception'}, {'timestamp': {'$gt': last_timestamp}}]})
        if recent_observations['documents']:
            recent_observations = '\n'.join(recent_observations['documents'])
            remaining_doubts_info = f'Here are some recent observations:\n{recent_observations}'


    # Prompt the language model
    llm = LLMModels().get_main_model()
    try:
        response = llm.completion(prompt='understanding.txt', inputs=[agent.name, world_understanding, knowledge_about_agents, observations, other_agents_prompt, remaining_doubts_info, memories_about_other_agents])
        answers = extract_answers(response)
    except ValueError as e:
        if str(e) == 'Prompt is too long':
            llm = LLMModels().get_longer_context_fallback()
            response = llm.completion(prompt='understanding.txt', inputs=[agent.name, world_understanding, knowledge_about_agents, observations, other_agents_prompt, remaining_doubts_info, memories_about_other_agents])
            answers = extract_answers(response)
        else:
            raise e

    # Update the agent understanding
    world_understanding = answers.get('World_knowledge', None)
    if world_understanding is not None:
        agent.stm.add_memory(str(world_understanding), 'world_context')
    for agent_name in known_agents:
        agent_knowledge = answers.get(f'{agent_name}_knowledge', None)
        if agent_knowledge is not None:
            agent.stm.add_memory(str(agent_knowledge), f'knowledge_about_{agent_name}')
    doubts = answers.get('Remaining_doubts', None)
    if doubts is not None:
        agent.stm.add_memory(str(doubts), 'remaining_doubts')

    # Update the time of the understanding update
    agent.stm.add_memory(game_time, 'understanding_updated_on')