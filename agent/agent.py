import logging
from datetime import datetime
from queue import Queue
import copy
from typing import Union, Literal

from agent.memory_structures.long_term_memory import LongTermMemory
from agent.memory_structures.short_term_memory import ShortTermMemory
from agent.memory_structures.spatial_memory import SpatialMemory
from agent.cognitive_modules.perceive import should_react, update_known_agents, create_memory
from agent.cognitive_modules.plan import plan
from agent.cognitive_modules.reflect import reflect_questions
from agent.cognitive_modules.reflect import reflect_insights
from agent.cognitive_modules.act import actions_sequence
from agent.cooperative_modules.understanding import update_understanding
from utils.queue_utils import list_from_queue
from utils.logging import CustomAdapter
from utils.time import str_to_timestamp

# Define a custom type to determine the congnitive modules to use
Mode = Union[Literal['normal'], Literal['cooperative']]

class Agent:
    """Agent class.
    """

    def __init__(self, name: str, data_folder: str, agent_context_file: str, world_context_file: str, scenario_info:dict, att_bandwidth: int = 10, reflection_umbral: int = 10, mode: Mode = 'normal', understanding_umbral = 30) -> None:
        """Initializes the agent.

        Args:
            name (str): Name of the agent.
            data_folder (str): Path to the data folder.
            agent_context_file (str): Path to the json agent context file. Initial info about the agent.
            world_context_file (str): Path to the text world context file. Info about the world that the agent have access to.
            scenario_info (dict): Dictionary with the scenario info. Contains the scenario map and the scenario obstacles.
            att_bandwidth (int, optional): Attention bandwidth. The attention bandwidth is the number of observations that the agent can attend to at the same time. Defaults to 10.
            reflection_umbral (int, optional): Reflection umbral. The reflection umbral is the number of poignancy that the agent needs to accumulate to reflect on its observations. Defaults to 30.
            understanding_umbral (int, optional): Understanding umbral. The understanding umbral is the number of poignancy that the agent needs to accumulate to update its understanding (only the poignancy of reflections are taken in account). Defaults to 6.
        """
        self.logger = logging.getLogger(__name__)
        self.logger = CustomAdapter(self.logger)

        self.name = name
        self.mode = mode
        self.att_bandwidth = att_bandwidth
        self.reflection_umbral = reflection_umbral
        self.observations_poignancy = 10
        self.ltm = LongTermMemory(agent_name=name, data_folder=data_folder)
        self.stm = ShortTermMemory(data_folder=data_folder, agent_context_file=agent_context_file, world_context_file=world_context_file)
        self.spatial_memory = SpatialMemory(scenario_map=scenario_info['scenario_map'], scenario_obstacles=scenario_info['scenario_obstacles'])
        self.att_bandwidth = att_bandwidth
        self.understanding_umbral = understanding_umbral
        self.stm.add_memory(memory = self.name, key = 'name')
        
        # Initialize steps sequence in empty queue
        self.stm.add_memory(memory=Queue(), key='current_steps_sequence')
        self.stm.add_memory(memory=scenario_info['valid_actions'], key='valid_actions')



    def move(self, observations: list[str], agent_current_scene:dict, changes_in_state: list[tuple[str, str]], game_time: str, agent_reward: float = 0, agent_is_out:bool = False) -> Queue:
        """Use all the congnitive sequence of the agent to decide an action to take

        Args:
            observations (list[str]): List of observations of the environment.
            agent_current_scene (dict): Dictionary with the current scene of the agent. It contains the agent position, orientation and the scene description.
                -> global_position (tuple): Current position of the agent in the global map.
                -> orientation (int): Current orientation of the agent. 0: North, 1: East, 2: South, 3: West.
                -> observation (str): ascii representation of the scene.
            changes_in_state (list[tuple[str, str]]): List of changes in the state of the environment and its game time.
            game_time (str): Current game time.
            agent_reward (float, optional): Current reward of the agent. Defaults to 0.
            agent_is_out (bool, optional): True if the agent is out of the scenario (was taken), False otherwise. Defaults to False.

        Returns:
            Queue: Steps sequence for the current action.
        """
        if self.mode == 'cooperative':
            return self.move_cooperative(observations, agent_current_scene, changes_in_state, game_time, agent_reward, agent_is_out)

        #Updates the position of the agent in the spatial memory 
        self.spatial_memory.update_current_scene(agent_current_scene['global_position'], agent_current_scene['orientation'],\
                                                    agent_current_scene['observation'])
        react, filtered_observations, state_changes = self.perceive(observations, changes_in_state, game_time, agent_reward)
        if react:
            self.plan()
            self.generate_new_actions()
        
        self.reflect(filtered_observations)

        if not agent_is_out:
            step_actions = self.get_actions_to_execute(filtered_observations)
        else :
            step_actions = Queue()
            
        return step_actions
    
    def move_cooperative(self, observations: list[str], agent_current_scene:dict, changes_in_state: list[tuple[str, str]], game_time: str, reward: float, agent_is_out:bool = False) -> Queue:
        """Use all the congnitive sequence (including the cooperative modules) of the agent to decide an action to take

        Args:
            observations (list[str]): List of observations of the environment.
            agent_current_scene (dict): Dictionary with the current scene of the agent. It contains the agent position, orientation and the scene description.
                -> global_position (tuple): Current position of the agent in the global map.
                -> orientation (int): Current orientation of the agent. 0: North, 1: East, 2: South, 3: West.
                -> observation (str): ascii representation of the scene.
            changes_in_state (list[tuple[str, str]]): List of changes in the state of the environment and its game time.
            game_time (str): Current game time.
            reward (float): Current reward of the agent.
            agent_is_out (bool, optional): True if the agent is out of the scenario (was taken), False otherwise. Defaults to False.

        Returns:
            Queue: Steps sequence for the current action.
        """

        #Updates the position of the agent in the spatial memory 
        self.spatial_memory.update_current_scene(agent_current_scene['global_position'], agent_current_scene['orientation'],\
                                                    agent_current_scene['observation'])
        react, filtered_observations, state_changes = self.perceive(observations, changes_in_state, game_time, reward)

        self.reflect(filtered_observations)

        self.understand(filtered_observations)

        if react:
            self.plan()
            self.generate_new_actions()
        

        if not agent_is_out:
            step_actions = self.get_actions_to_execute(filtered_observations)
        else :
            step_actions = Queue()
            
        return step_actions

    def perceive(self, observations: list[str], changes_in_state: list[tuple[str, str]], game_time: str, reward: float) -> tuple[bool, list[str], list[str]]:
        """Perceives the environment and stores the observation in the long term memory. Decide if the agent should react to the observation.
        It also filters the observations to only store the closest ones, and asign a poignancy to the observations.
        Game time is also stored in the short term memory.
        Args:
            observations (list[str]): List of observations of the environment.
            game_time (str): Current game time.
            reward (float): Current reward of the agent.
        
        Returns:
            tuple[bool, list[str], list[str]]: Tuple with True if the agent should react to the observation, False otherwise, the filtered observations and the changes in the state of the environment.
        """

        # Add the game time to the short term memory
        self.stm.add_memory(game_time, 'game_time')
        # Observations are filtered to only store the closest ones. The att_bandwidth defines the number of observations that the agent can attend to at the same time
        sorted_observations = self.spatial_memory.sort_observations_by_distance(observations)
        observations = sorted_observations[:self.att_bandwidth]

        # Update the agent known agents
        update_known_agents(observations, self.stm)

        action_executed = self.stm.get_memory('current_action')
        # Parse the changes in the state of the environment observed by the agent
        changes = []
        for change, obs_time in changes_in_state:
            changes.append(f'{change} At {obs_time}')

        # Create a memory from the observations, the changes in the state of the environment and the reward, and add it to the long term memory
        memory = create_memory(self.name, game_time, action_executed, changes, reward, observations)
        self.ltm.add_memory(memory, game_time, self.observations_poignancy, {'type': 'perception'})

        current_observation = '\n'.join(observations)
        self.stm.add_memory(current_observation, 'current_observation')

        # Decide if the agent should react to the observation
        current_plan = self.stm.get_memory('current_plan')
        world_context = self.stm.get_memory('world_context')
        actions_sequence = list_from_queue(copy.copy(self.stm.get_memory('actions_sequence')))
        react, reasoning = should_react(self.name, world_context, observations, current_plan, actions_sequence, changes, game_time)
        self.stm.add_memory(reasoning, 'reason_to_react')
        self.logger.info(f'{self.name} should react to the observation: {react}')
        return react, observations, changes
    
    def plan(self,) -> None:
        """Plans the next actions of the agent and its main goals.
        """

        current_observation = self.stm.get_memory('current_observation') or 'None'
        current_plan = self.stm.get_memory('current_plan')
        world_context = self.stm.get_memory('world_context')
        reflections = self.ltm.get_memories(limit=10, filter={'type': 'reflection'})['documents']
        reflections = '\n'.join(reflections) if len(reflections) > 0 else 'None'
        reason_to_react = self.stm.get_memory('reason_to_react')
        assert reason_to_react is not None, 'Reason to react is None. This should not happen because the agent only plans if it should react to the observation'

        new_plan, new_goals = plan(self.name, world_context, current_observation, current_plan, reflections, reason_to_react)
        self.logger.info(f'{self.name} new plan: {new_plan}, new goals: {new_goals}')
        if new_plan is None or new_goals is None:
            self.logger.warn(f'{self.name} could not generate a new plan or new goals')

        # Update the short term memory
        self.stm.add_memory(new_plan, 'current_plan')
        self.stm.add_memory(new_goals, 'current_goals')


    def reflect(self, filtered_observations:list[str]) -> None:
        """Reflects on the agent's observations and stores the insights reflections in the long term memory.

        Args:
            filtered_observations (list[str]): List of filtered observations.
            state_changes (list[str]): List of changes in the state of the environment.
        """
        # Extract the relevant memories, game time and world context from the short term memory
        game_time = self.stm.get_memory('game_time')
        # Decide if the agent should reflect on the observations
        poignancy_of_current_observations = self.observations_poignancy
        accumulated_poignancy = (self.stm.get_memory('accumulated_poignancy') or 0) + poignancy_of_current_observations
        if accumulated_poignancy < self.reflection_umbral:
            self.stm.add_memory(accumulated_poignancy, 'accumulated_poignancy')
            self.logger.info(f'{self.name} should not reflect on the observations. Accumulated poignancy: {accumulated_poignancy}')
            return
        
        # Reset the accumulated poignancy
        self.stm.add_memory(0, 'accumulated_poignancy')

        # Get observations to reflect on
        last_reflection = self.stm.get_memory('last_reflection')
        filter = {'$and': [{'type': 'perception'}, {'timestamp': {'$gt': str_to_timestamp(last_reflection, self.ltm.date_format)}}]}
        if last_reflection is None:
            filter = {'type': 'perception'}
        filtered_observations = self.ltm.get_memories(filter=filter)

        observations_str = '\n'.join(filtered_observations['documents'])

        world_context = self.stm.get_memory('world_context')

        # Get the relevant questions
        relevant_questions = reflect_questions(self.name, world_context, observations_str)
        self.logger.info(f'{self.name} relevant questions: {relevant_questions}')
        # Get the relevant memories for each question, relevant memories is a list of lists
        relevant_memories_list = [] 
        for question in relevant_questions:
            retrieved_memories = self.ltm.get_relevant_memories(query=question, n_results=3, return_metadata=True)
            retrieved_memories = '\n'.join(retrieved_memories[0])
            # adds the retrieved memories to the relevant memories list
            relevant_memories_list.append(retrieved_memories)
        
        # Convert the relevant memories list to a list of strings
        self.logger.info(f'{self.name} relevant memories: {relevant_memories_list}')
        # Get the insights reflections
        reflections = reflect_insights(self.name, world_context, relevant_memories_list, relevant_questions)
        self.logger.info(f'{self.name} reflections: {reflections}')
        # Add the reflections to the long term memory, checks if the reflection  is not empty
        for reflection in reflections:
            if reflection:
                self.ltm.add_memory(f'{reflection} Reflection made at {game_time}.', game_time, self.observations_poignancy, {'type': 'reflection'})
        
        # Add the last reflection to the short term memory
        self.stm.add_memory(game_time, 'last_reflection')
  


    def generate_new_actions(self) -> None:
        """
        Acts in the environment given the observations, the current plan and the current goals.
        Stores the actions sequence in the short term memory.
        """
        world_context = self.stm.get_memory('world_context')
        current_plan = self.stm.get_memory('current_plan')
        valid_actions = self.stm.get_memory('valid_actions') 
        observations = self.stm.get_memory('current_observation') or 'None'
        current_goals = self.stm.get_memory('current_goals')
        reflections = self.ltm.get_memories(limit=10, filter={'type': 'reflection'})['documents']
        reflections = '\n'.join(reflections) if len(reflections) > 0 else 'None'
        # Generate new actions sequence and add it to the short term memory
        actions_sequence_queue = actions_sequence(self.name, world_context, current_plan, reflections, observations, self.spatial_memory.position, valid_actions, current_goals)
        self.logger.info(f'{self.name} generated new actions sequence: {actions_sequence_queue.queue}')
        
        self.stm.add_memory(actions_sequence_queue, 'actions_sequence')
        self.stm.add_memory(Queue(), 'current_steps_sequence') # Initialize steps sequence in empty queue




    def get_actions_to_execute(self, filtered_observations: list[str]) -> Queue:
        """
        Executes the current actions of the agent. 
        If the current gameloop is empty, it generates a new one.

        Args:
            filtered_observations (list[str]): List of filtered observations.
            
        Returns:
            Queue: Steps sequence for the current action.
        """

        if self.stm.get_memory('current_steps_sequence').empty():
            # If the current gameloop is empty, we need to generate a new one

            # If the actions sequence is empty, we generate actions sequence
            if self.stm.get_memory('actions_sequence').empty():
                self.generate_new_actions()

            # We get next action from the actions sequence
            current_action = self.stm.get_memory('actions_sequence').get()
            self.stm.add_memory(current_action, 'current_action')
            
            # Now defines a gameloop for the current action
            steps_sequence = self.spatial_memory.get_steps_sequence(current_action = current_action)
            self.stm.add_memory(steps_sequence, 'current_steps_sequence')
           

       
        # We check if after the previous step the gameloop is still empty, if it is, we generate a new one,
        # all the process above is repeated until we get a gameloop that is not empty
        # If actions sequence were all invalid, we send an explore sequence
        while self.stm.get_memory('current_steps_sequence').empty() :
            if self.stm.get_memory('actions_sequence').empty():
                self.logger.warn(f'{self.name} current gameloop is empty and there are no more actions to execute, agent will explore')
                steps_sequence = self.spatial_memory.generate_explore_sequence()
                self.stm.add_memory(steps_sequence, 'current_steps_sequence')
                break 
            self.logger.warn(f'{self.name} current gameloop is empty, getting the next action')
            current_action = self.stm.get_memory('actions_sequence').get()
            self.stm.add_memory(current_action, 'current_action')
            steps_sequence = self.spatial_memory.get_steps_sequence(current_action = current_action)
            self.stm.add_memory(steps_sequence, 'current_steps_sequence')
            self.logger.info(f'{self.name} is {current_action}, the steps sequence  is: {list(steps_sequence.queue)}')
    
        agent_steps = self.stm.get_memory('current_steps_sequence')
        
        self.logger.info(f'{self.name} is executing the action: {self.stm.get_memory("current_action")} with the steps sequence {agent_steps.queue}')

        return agent_steps
    
    def understand(self, observations: list[str]):
        """
        Improves the agent's understanding of the world and of other agents.

        Args:
            observations (list[str]): List of observations of the environment.
        
        Returns:
            None
        """
        update_understanding(observations, self, self.stm.get_memory('game_time'), understanding_umbral = self.understanding_umbral)