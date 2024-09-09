import logging
from queue import Queue
from typing import Union, Literal

from agent.memory_structures.short_term_memory import ShortTermMemory
from agent.memory_structures.spatial_memory import SpatialMemory
from agent.cognitive_modules.act import actions_sequence
from utils.logging import CustomAdapter

# Define a custom type to determine the congnitive modules to use
Mode = Union[Literal['normal'], Literal['cooperative']]

class CoTAgent:
    """Agent class.
    """

    def __init__(self, name: str, agent_context: dict, world_context_file: str, scenario_info:dict, recorder_obj = None, agent_id = "") -> None:
        """Initializes the agent.

        Args:
            name (str): Name of the agent.
            agent_context (dict): Initial info about the agent.
            world_context_file (str): Path to the text world context file. Info about the world that the agent have access to.
            scenario_info (dict): Dictionary with the scenario info. Contains the scenario map and the scenario obstacles.
            substrate_name (str, optional): Name of the substrate. Defaults to "commons_harvest_open".
            recorder_obj (Recorder, optional): Recorder object to record indicators of the game. Defaults to None.
        """
        self.logger = logging.getLogger(__name__)
        self.logger = CustomAdapter(self.logger)
        self.recorder = recorder_obj

        self.name = name
        self.stm = ShortTermMemory( agent_context=agent_context, world_context_file=world_context_file)
        self.spatial_memory = SpatialMemory(scenario_map=scenario_info['scenario_map'], agent_id=agent_id, scenario_obstacles=scenario_info['scenario_obstacles'])
        self.prompts_folder = 'cot_agent_prompts'
        self.stm.add_memory(memory = self.name, key = 'name')
        
        # Initialize steps sequence in empty queue
        self.stm.add_memory(memory=Queue(), key='current_steps_sequence')
        self.stm.add_memory(memory=scenario_info['valid_actions'], key='valid_actions')

    def move(self, observations: list[str], agent_current_scene:dict, changes_in_state: list[tuple[str, str]], current_global_map: list[list[str]], game_time: str, agent_reward: float = 0, agent_is_out:bool = False) -> Queue:
        """Use all the congnitive sequence of the agent to decide an action to take

        Args:
            observations (list[str]): List of observations of the environment.
            agent_current_scene (dict): Dictionary with the current scene of the agent. It contains the agent position, orientation and the scene description.
                -> global_position (tuple): Current position of the agent in the global map.
                -> orientation (int): Current orientation of the agent. 0: North, 1: East, 2: South, 3: West.
                -> observation (str): ascii representation of the scene.
            changes_in_state (list[tuple[str, str]]): List of changes in the state of the environment and its game time.
            current_global_map (list[list[str]]): Current global map of the game.
            game_time (str): Current game time.
            agent_reward (float, optional): Current reward of the agent. Defaults to 0.
            agent_is_out (bool, optional): True if the agent is out of the scenario (was taken), False otherwise. Defaults to False.

        Returns:
            action to execute: Low level action to execute.
        """
        # If the agent is out of the game, it does not take any action
        if agent_is_out:
            self.logger.info(f'{self.name} is out of the game, skipping its turn.')
            return None

        #Updates the position of the agent in the spatial memory 
        self.spatial_memory.update_current_scene(agent_current_scene['global_position'], agent_current_scene['orientation'],\
                                                    agent_current_scene['observation'], current_global_map)
        self.stm.add_memory(observations, 'current_observation')
        changes = []
        for change, obs_time in changes_in_state:
            changes.append(f'{change} At {obs_time}')
        self.stm.add_memory(changes, 'changes_in_state')

        if not agent_current_scene['is_movement_allowed']:
            self.logger.info(f'{self.name} is frozen and cannot move.')
            return None
        
        step_action = self.get_actions_to_execute(current_global_map)
            
        return step_action
    
    def generate_new_actions(self) -> None:
        """
        Acts in the environment given the observations, the current plan and the current goals.
        Stores the actions sequence in the short term memory.
        """
        world_context = self.stm.get_memory('world_context')
        valid_actions = self.stm.get_memory('valid_actions') 
        observations = self.stm.get_memory('current_observation')
        current_position = self.spatial_memory.position
        
        # Generate new actions sequence and add it to the short term memory
        actions_sequence_queue = actions_sequence(self.name, world_context, None, None, observations,
                                                  current_position, valid_actions, None, None, self.prompts_folder,
                                                  None, None, self.stm)
        self.logger.info(f'{self.name} generated new actions sequence: {actions_sequence_queue.queue}')
        
        self.stm.add_memory(actions_sequence_queue, 'actions_sequence')
        self.stm.add_memory(Queue(), 'current_steps_sequence') # Initialize steps sequence in empty queue

    def get_actions_to_execute(self, current_global_map: list[list[str]]) -> Queue:
        """
        Executes the current actions of the agent. 
        If the current gameloop is empty, it generates a new one.
            
        Returns:
            Step to take: low level action to execute.
        """

        if not self.stm.get_memory('current_steps_sequence') or self.stm.get_memory('current_steps_sequence').empty():
            # If the current gameloop is empty, we need to generate a new one

            # If the actions sequence is empty, we generate actions sequence
            if not self.stm.get_memory('actions_sequence') or self.stm.get_memory('actions_sequence').empty():
                self.generate_new_actions()

            # We get next action from the actions sequence
            current_action = self.stm.get_memory('actions_sequence').get()
            self.stm.add_memory(current_action, 'current_action')
            if self.recorder:
                self.recorder.record_action(player=self.name, curr_action=current_action)
            
            # Now defines a gameloop for the current action
            steps_sequence = self.spatial_memory.get_steps_sequence(current_global_map, current_action)
            self.stm.add_memory(steps_sequence, 'current_steps_sequence')
       
        # We check if after the previous step the gameloop is still empty, if it is, we generate a new one,
        # all the process above is repeated until we get a gameloop that is not empty
        # If actions sequence were all invalid, we send an explore sequence
        while self.stm.get_memory('current_steps_sequence').empty():
            if self.stm.get_memory('actions_sequence').empty():
                self.logger.warn(f'{self.name} current gameloop is empty and there are no more actions to execute, agent will explore')
                steps_sequence = self.spatial_memory.generate_explore_sequence()
                self.stm.add_memory(steps_sequence, 'current_steps_sequence')
                break 
            self.logger.warn(f'{self.name} current gameloop is empty, getting the next action')
            current_action = self.stm.get_memory('actions_sequence').get()
            self.stm.add_memory(current_action, 'current_action')
            if self.recorder:
                self.recorder.record_action(player=self.name, curr_action=current_action)
            steps_sequence = self.spatial_memory.get_steps_sequence(current_global_map, current_action)
            self.stm.add_memory(steps_sequence, 'current_steps_sequence')
            self.logger.info(f'{self.name} is {current_action}, the steps sequence  is: {list(steps_sequence.queue)}')
    
        agent_steps = self.stm.get_memory('current_steps_sequence')
        self.logger.info(f'{self.name} is executing the action: {self.stm.get_memory("current_action")} with the steps sequence {agent_steps.queue}')
        step_to_take = agent_steps.get()
        self.stm.add_memory(step_to_take, 'step_to_take')

        return step_to_take