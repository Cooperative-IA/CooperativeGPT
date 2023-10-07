import logging
from datetime import datetime
from queue import Queue

from agent.memory_structures.long_term_memory import LongTermMemory
from agent.memory_structures.short_term_memory import ShortTermMemory
from agent.memory_structures.spatial_memory import SpatialMemory
from agent.cognitive_modules.perceive import should_react
from agent.cognitive_modules.plan import plan
from agent.cognitive_modules.reflect import reflect_questions
from agent.cognitive_modules.reflect import reflect_insights
from agent.cognitive_modules.act import actions_sequence

class Agent:
    """Agent class.
    """

    def __init__(self, name: str, data_folder: str, agent_context_file: str, world_context_file: str, scenario_info:dict, att_bandwidth: int = 10) -> None:
        """Initializes the agent.

        Args:
            name (str): Name of the agent.
            data_folder (str): Path to the data folder.
            agent_context_file (str): Path to the json agent context file. Initial info about the agent.
            world_context_file (str): Path to the text world context file. Info about the world that the agent have access to.
            scenario_info (dict): Dictionary with the scenario info. Contains the scenario map and the scenario obstacles.
            att_bandwidth (int, optional): Attention bandwidth. The attention bandwidth is the number of observations that the agent can attend to at the same time. Defaults to 10.
        """
        self.logger = logging.getLogger(__name__)

        self.name = name
        self.ltm = LongTermMemory(agent_name=name, data_folder=data_folder)
        self.stm = ShortTermMemory(data_folder=data_folder, agent_context_file=agent_context_file, world_context_file=world_context_file)
        self.spatial_memory = SpatialMemory(scenario_map=scenario_info['scenario_map'], scenario_obstacles=scenario_info['scenario_obstacles'])
        self.att_bandwidth = att_bandwidth
        self.stm.add_memory(memory = self.name, key = 'name')
        
        # Initialize steps sequence in empty queue
        self.stm.add_memory(memory=Queue(), key='current_steps_sequence')
        self.stm.add_memory(memory=scenario_info['valid_actions'], key='valid_actions')



    def move(self, observations: list[str], agent_position: tuple, agent_orientation: int, game_time: str) -> str:
        """Use all the congnitive sequence of the agent to decide an action to take

        Args:
            observations (list[str]): List of observations of the environment.
            agent_position (tuple): Current position of the agent.
            agent_orientation (int): Current orientation of the agent. 0: North, 1: East, 2: South, 3: West.
            game_time (str): Current game time.

        Returns:
            str: Action to take.
        """
        #Updates the position of the agent in the spatial memory 
        self.spatial_memory.updatePosition(agent_position, agent_orientation)
        react = self.perceive(observations, game_time)

        if react:
            self.plan()
            self.generate_new_actions(observations)
        
        self.reflect(observations)

        step_action = self.get_actions_to_execute()

        return step_action

    def perceive(self, observations: list[str], game_time: str) -> None:
        """Perceives the environment and stores the observation in the long term memory. Decide if the agent should react to the observation.
        It also filters the observations to only store the closest ones, and asign a poignancy to the observations.

        Args:
            observations (list[str]): List of observations of the environment.
            game_time (str): Current game time.
        
        Returns:
            bool: True if the agent should react to the observation, False otherwise.
        """

        # Observations are filtered to only store the closest ones. The att_bandwidth defines the number of observations that the agent can attend to at the same time
        sorted_observations = self.spatial_memory.sort_observations_by_distance(observations)
        observations = sorted_observations[:self.att_bandwidth]
        
        # Open AI Only allows 16 observations per request
        batch_size = 16
        for i in range(0, len(observations), batch_size):
            batch = observations[i:i+batch_size]
            self.ltm.add_memory(batch, game_time, 1, {'type': 'perception'}) # For now we set the poignancy to 1 to all observations

        current_observation = ', '.join(observations)
        self.stm.add_memory(current_observation, 'current_observation')

        # Decide if the agent should react to the observation
        current_plan = self.stm.get_memory('current_plan')
        world_context = self.stm.get_memory('world_context')
        react = should_react(self.name, world_context, observations, current_plan)
        self.logger.info(f'{self.name} should react to the observation: {react}')
        return react
    
    def plan(self,) -> None:
        """Plans the next actions of the agent and its main goals.
        """

        current_observation = self.stm.get_memory('current_observation')
        current_plan = self.stm.get_memory('current_plan')
        world_context = self.stm.get_memory('world_context')
        new_plan, new_goals = plan(self.name, world_context, current_observation, current_plan)
        self.logger.info(f'{self.name} new plan: {new_plan}, new goals: {new_goals}')

        # Update the short term memory
        self.stm.add_memory(new_plan, 'current_plan')
        self.stm.add_memory(new_goals, 'current_goals')


    def reflect(self, observations:list[str]) -> None:
        """Reflects on the agent's observations and stores the insights reflections in the long term memory.

        Args:
            observations (list[str]): List of observations of the environment.
        """
        observations_str = '\n'.join(observations)

        world_context = self.stm.get_memory('world_context')
        relevant_questions = reflect_questions(self.name, world_context, observations_str)
        self.logger.info(f'{self.name} relevant questions: {relevant_questions}')
        
        relevant_memories = []
        for question in relevant_questions:
            retrieved_memories = self.ltm.get_relevant_memories(query=question, n_results=5)
            # adds the retrieved memories to the relevant memories, checks for duplicates
            relevant_memories = list(set(relevant_memories + retrieved_memories))
            
        self.logger.info(f'{self.name} relevant memories: {relevant_memories}')
        
        relevant_memories_str = '\n'.join([str(memory) for memory in relevant_memories])
        reflections = reflect_insights(self.name, world_context, relevant_memories_str)
        self.logger.info(f'{self.name} reflections: {reflections}')
        self.ltm.add_memory(reflections, [{'type': 'reflection', 'agent': self.name}]*len(reflections))
  


    def generate_new_actions(self, observations: list[str]) -> list[str]:
        """Acts in the environment given the observations.

        Args:
            observations (list[str]): Observations of the environment.

        Returns:
            list[str]: Actions to take.
        """
        world_context = self.stm.get_memory('world_context')
        current_plan = self.stm.get_memory('current_plan')
        valid_actions = self.stm.get_memory('valid_actions') 
        memory_statements = self.ltm.get_relevant_memories(query=self.name, n_results=10)
        # Generate new actions sequence and add it to the short term memory
        actions_sequence_queue = actions_sequence(self.name, world_context, current_plan, memory_statements, observations, valid_actions)
        self.logger.info(f'{self.name} generated new actions sequence: {actions_sequence_queue.queue}')
        
        self.stm.add_memory(actions_sequence_queue, 'actions_sequence')




    def get_actions_to_execute(self) -> None:
        """
        Executes the current actions of the agent. 

        Returns:
            str: Next action step to execute.
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
            logging.info(f'{self.name} is grabbing an apple, the steps sequence  is: {list(steps_sequence.queue)}')
           

       
        # We execute the current action
        if self.stm.get_memory('current_steps_sequence').empty():
            logging.warn(f'{self.name} current gameloop is empty, but it should not be.')
            raise Exception(f'{self.name} current gameloop is empty, but it should not be.')
    
        agent_step = self.stm.get_memory('current_steps_sequence').get()
        
        self.logger.info(f'{self.name} is executing the action: {self.stm.get_memory("current_action")} with the gameloop { self.stm.get_memory("current_steps_sequence").queue}\
                          and the next instant step is {agent_step}. Remaining actions: {self.stm.get_memory("actions_sequence").queue}')
        return agent_step
    