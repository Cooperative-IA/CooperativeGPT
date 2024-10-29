import os
import re
from llm import LLMModels
from utils.time import str_to_timestamp
from utils.llm import extract_answers, extract_text, extract_tags
from agent.memory_structures.long_term_memory import LongTermMemory

def update_understanding(current_observations: list[str], agent, game_time: str, understanding_umbral = 30, prompts_folder = "base_prompts_v0") -> None:
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
    last_timestamp = str_to_timestamp(last_understanding_update)
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
    prompt_path = os.path.join(prompts_folder, 'understanding.txt')
    try:
        response = llm.completion(prompt=prompt_path, inputs=[agent.name, world_understanding, knowledge_about_agents, observations, other_agents_prompt, remaining_doubts_info, memories_about_other_agents])
        answers = extract_answers(response)
    except ValueError as e:
        if str(e) == 'Prompt is too long':
            llm = LLMModels().get_longer_context_fallback()
            response = llm.completion(prompt=prompt_path, inputs=[agent.name, world_understanding, knowledge_about_agents, observations, other_agents_prompt, remaining_doubts_info, memories_about_other_agents])
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

def update_understanding_2(current_observations: list[str], agent, game_time: str, last_reward, reward, state_changes: list[str], understanding_umbral = 30, prompts_folder = "base_prompts_v0"):
    """Updates the agent understanding about the world and the other agents. Updates the understanding only if the accumulated poignancy of the recent reflections is greater than the umbral, or 
    if the agent has no understanding about the world yet, in that case the current observations are used instead of the reflections.

    Args:
        current_observations (list[str]): List of the current observations.
        agent (Agent): Agent to update the understanding.
        game_time (str): Current game time.
        understanding_umbral (int, optional): Minimum poignancy to update the understanding (only reflections are taken in account). Defaults to 6.
    """
    # Decide if the understanding should be updated
    last_world_representation = agent.stm.get_memory('world_representation')
    last_understanding_update = agent.stm.get_memory('understanding_updated_on')
    if current_observations:
        current_observations = '\n'.join(current_observations)
    else:
        current_observations = 'You cannot see anything within your vision range.'
    llm = LLMModels().get_main_model()
    prompt_wr_path = os.path.join(prompts_folder, 'world_representation.txt')
    response = llm.completion(prompt=prompt_wr_path, inputs=[current_observations])
    current_world_representation = str(extract_answers(response))
    agent.stm.add_memory(current_world_representation, 'world_representation')
        
    # Update the understanding

    # Prompt the language model
    action = agent.stm.get_memory('current_action') or 'No action executed yet.'
    state_changes = '\n'.join(state_changes) if state_changes else 'There were no changes observed.'
    if last_world_representation is not None:
        last_world_rules = agent.stm.get_memory('world_rules') or ''
        prompt_rules_path = os.path.join(prompts_folder, 'world_rules.txt')
        try:
            world_rules = llm.completion(prompt=prompt_rules_path, inputs=[last_understanding_update, last_world_representation, agent.name, last_reward, action, state_changes, game_time, reward, current_world_representation, last_world_rules])
        except ValueError as e:
            if str(e) == 'Prompt is too long':
                llm = LLMModels().get_longer_context_fallback()
                world_rules = llm.completion(prompt=prompt_rules_path, inputs=[last_understanding_update, last_world_representation, agent.name, last_reward, action, state_changes, game_time, reward, current_world_representation, last_world_rules])
            else:
                raise e
        agent.stm.add_memory(world_rules, 'world_rules')
        agent.stm.add_memory(f'{current_world_representation}\n{world_rules}', 'world_context')
    else:
        agent.stm.add_memory(current_world_representation, 'world_context')

    # Update the time of the understanding update
    agent.stm.add_memory(game_time, 'understanding_updated_on')


def update_understanding_3(current_observations: list[str], agent, game_time: str, last_reward, reward, state_changes: list[str], understanding_umbral = 30, prompts_folder = "base_prompts_v0"):
    """Updates the agent understanding about the world and the other agents. Updates the understanding only if the accumulated poignancy of the recent reflections is greater than the umbral, or 
    if the agent has no understanding about the world yet, in that case the current observations are used instead of the reflections.

    Args:
        current_observations (list[str]): List of the current observations.
        agent (Agent): Agent to update the understanding.
        game_time (str): Current game time.
        understanding_umbral (int, optional): Minimum poignancy to update the understanding (only reflections are taken in account). Defaults to 6.
    """
    # Decide if the understanding should be updated
    last_world_representation = agent.stm.get_memory('world_representation')
    last_understanding_update = agent.stm.get_memory('understanding_updated_on')
    last_position = agent.stm.get_memory('last_position')
    if current_observations:
        current_observations = '\n'.join(current_observations)
    else:
        current_observations = 'You cannot see anything within your vision range.'
    current_world_representation = current_observations
    agent.stm.add_memory(current_world_representation, 'world_representation')
        
    # Update the understanding

    # Prompt the language model
    action = agent.stm.get_memory('current_action') or 'No action executed yet.'
    state_changes = '\n'.join(state_changes) if state_changes else 'There were no changes observed.'
    current_position = agent.stm.get_memory('current_position')
    llm = LLMModels().get_main_model()
    if last_world_representation is not None:
        last_world_rules = agent.stm.get_memory('world_rules') or ''
        prompt_rules_path = os.path.join(prompts_folder, 'world_rules.txt')
        if last_world_rules:
            last_world_rules = f'The previous knowledge of the world:\n{last_world_rules}'
        try:
            response = llm.completion(prompt=prompt_rules_path, inputs=[last_understanding_update, last_world_representation, agent.name, last_reward, action, state_changes, game_time, reward, current_world_representation, last_world_rules, last_position, current_position])
        except ValueError as e:
            if str(e) == 'Prompt is too long':
                llm = LLMModels().get_longer_context_fallback()
                response = llm.completion(prompt=prompt_rules_path, inputs=[last_understanding_update, last_world_representation, agent.name, last_reward, action, state_changes, game_time, reward, current_world_representation, last_world_rules, current_position, last_position, current_position])
            else:
                raise e
        world_rules = extract_text(response)
        agent.stm.add_memory(world_rules, 'world_rules')
        agent.stm.add_memory(world_rules, 'world_context')
    else:
        agent.stm.add_memory('No current knowledge of the world yet.', 'world_context')

    # Update the time of the understanding update
    agent.stm.add_memory(game_time, 'understanding_updated_on')

def update_understanding_4(current_observations: list[str], agent, game_time: str, last_reward, reward, state_changes: list[str], understanding_umbral = 30, prompts_folder = "base_prompts_v0"):
    """Updates the agent understanding about the world and the other agents. Updates the understanding only if the accumulated poignancy of the recent reflections is greater than the umbral, or 
    if the agent has no understanding about the world yet, in that case the current observations are used instead of the reflections.

    Args:
        current_observations (list[str]): List of the current observations.
        agent (Agent): Agent to update the understanding.
        game_time (str): Current game time.
        understanding_umbral (int, optional): Minimum poignancy to update the understanding (only reflections are taken in account). Defaults to 6.
    """
    # Decide if the understanding should be updated
    # last_world_representation = agent.stm.get_memory('world_representation')
    # last_understanding_update = agent.stm.get_memory('understanding_updated_on')
    # last_position = agent.stm.get_memory('last_position')


    if current_observations:
        current_observations = '\n'.join(current_observations)
    else:
        current_observations = 'You cannot see anything within your vision range.'
        
    # Get the most recent observations
    previous_observations = agent.ltm.get_memories(limit=6, reversed_order=True, filter={'$and': [{'type': 'perception'}, {'created_at': {'$ne': game_time}}]})
    previous_observations = '\n'.join([f'<observation>\n{observation}\n<\observation>' for observation in previous_observations['documents']]) if previous_observations['documents'] else '<observation>\nThere are no previous observations yet.\n<\observation>'
    # Get the last changes observed
    action = agent.stm.get_memory('current_action') or 'No action executed yet.'
    previous_changes = f'I took the action "{action}" in my last turn. Since then, the following changes in the environment were observed:\n'
    previous_changes += '\n'.join(state_changes) if state_changes else 'There were no changes observed.'
    previous_observations += f'<observation>\n{previous_changes}\n<\observation>'
    # Get the current state
    reward = agent.stm.get_memory('current_reward')
    position = list(agent.stm.get_memory('current_position'))
    orientation = agent.stm.get_memory('current_orientation')
    current_state = f'Now it\'s {game_time} and the reward obtained by me is {reward}. I am at the position {position} looking to the {orientation}.\nI can observe the following:'
    current_state += f'\n{current_observations}'

    # Prompt the language model
    world_rules = agent.stm.get_memory('world_rules')
    number_of_rules = len(world_rules) if world_rules else 0
    world_hypotheses = agent.stm.get_memory('world_hypotheses') or {}
    world_hypotheses = [item['value'] for item in world_hypotheses.values()]
    world_rules = '\n'.join([f'<{i+1}>{rule}<\{i+1}>' for i, rule in enumerate(world_rules)]) if world_rules else None
    world_hypotheses = '\n'.join([f'<{i+1+number_of_rules}>{hypothesis}<\{i+1+number_of_rules}>' for i, hypothesis in enumerate(world_hypotheses)]) if world_hypotheses else None

    llm = LLMModels().get_best_model()
    prompt_path = os.path.join(prompts_folder, 'world_understanding.txt')
    try:
        response = llm.completion(prompt=prompt_path, inputs=[world_rules, world_hypotheses, previous_observations, current_state, game_time])
    except ValueError as e:
        if str(e) == 'Prompt is too long':
            llm = LLMModels().get_longer_context_fallback()
            response = llm.completion(prompt=prompt_path, inputs=[world_rules, world_hypotheses, previous_observations, current_state, game_time])
        else:
            raise e
    answers = extract_tags(response)

    # Convert the hypotheses that were used to explain the world into theories if they meet an umbral of usage.
    used_rules = answers.get('used_knowledge', None)
    total_rules = hypotheses_to_theories(used_rules, agent)

    # Extract the new hypotheses
    new_hypotheses = answers.get('new_world_knowledge', None)
    total_hypotheses = save_new_hypotheses(new_hypotheses, agent)

    # Save the new world context
    total_rules = '\n'.join(total_rules) if total_rules else 'There are no rules yet.'
    total_hypotheses = '\n'.join(total_hypotheses) if total_hypotheses else 'There are no hypotheses yet.'
    predictions = answers.get('future_observations', 'No future predictions yet.')
    world_context = f'\n{total_rules}\nHypotheses about the world:\n{total_hypotheses}\nFuture predictions of the world state:\n{predictions}'
    agent.stm.add_memory(world_context, 'world_context')

    # Update the time of the understanding update
    agent.stm.add_memory(game_time, 'understanding_updated_on')

def hypotheses_to_theories(used_rules: str | None, agent) -> list[str]:
    """Converts the hypotheses that were used to explain the world into theories if they meet an umbral of usage.

    Args:
        used_rules (str): Rules used. A string with the id of the rules separated by commas.
        agent (Agent): Agent to update the understanding.

    Returns:
        list[str]: List of the current theories.
    """
    world_rules = agent.stm.get_memory('world_rules') or []

    if used_rules is None or used_rules == 'None':
        return world_rules
    used_rules = [id.strip() for id in used_rules.split(',')]
    hypotheses = agent.stm.get_memory('world_hypotheses')
    if hypotheses is None:
        return world_rules
    
    new_rules = []
    
    # Update the usage of the hypotheses
    for id in used_rules:
        # Only update the usage of the hypothesis if it exists
        hypothesis = hypotheses.get(id, None)
        if hypothesis is None:
            continue
        hypothesis['usage'] += 1

        # Convert the hypothesis into a theory if it meets the umbral
        if hypothesis['usage'] >= 2: # TODO: Move the umbral
            new_rules.append(hypothesis['value'])
            del hypotheses[id]

    # Add the new rules to the world rules
    world_rules += new_rules
    agent.stm.add_memory(world_rules, 'world_rules')

    return world_rules

def save_new_hypotheses(hypotheses: str | None, agent) -> list[str]:
    """Saves the new hypotheses.

    Args:
        hypotheses (str): New hypotheses. A string with the hypotheses in numbered XML tags.
        agent (Agent): Agent to update the understanding.

    Returns:
        list[str]: List of the current hypotheses.
    """
    world_hypotheses = agent.stm.get_memory('world_hypotheses') or {}
    if hypotheses is not None and hypotheses != 'None':
        hypotheses = extract_tags(hypotheses)
        current_id = len(world_hypotheses.keys())
        hypotheses = {str(current_id + i + 1): {'value': hypothesis, 'usage': 0} for i, hypothesis in enumerate(hypotheses.values())}
        world_hypotheses.update(hypotheses)
        agent.stm.add_memory(world_hypotheses, 'world_hypotheses')

    return [item['value'] for item in world_hypotheses.values()]

def analyze_consequences(ltm: LongTermMemory, action_options: list[str], prompts_folder: str) -> list[str]:
    """Analyzes the consequences of the possible actions.

    Args:
        ltm (LongTermMemory): Long term memory.
        action_options (list[str]): List of the possible actions.

    Returns:
        list[str]: List of the consequences of the possible actions.
    """
    # Retrieve the the 3 most recent memories of the agent
    recent_memories = ltm.get_memories(limit=3, reversed_order=True, filter={'type': 'perception'})['documents']
    recent_memories = '\n'.join(recent_memories)

    llm = LLMModels().get_causal_model()
    prompt_path = os.path.join(prompts_folder, 'consequences.txt')

    inputs = []
    for action in action_options:
        inputs.append([recent_memories, action])

    consequences = llm.batch_completion(prompt=prompt_path, inputs=inputs)

    return consequences