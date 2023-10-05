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
from agent.cognitive_modules.act import *

class Agent:
    """Agent class.
    """

    def __init__(self, name: str, data_folder: str, agent_context_file: str, world_context_file: str, map_info:dict) -> None:
        """Initializes the agent.

        Args:
            name (str): Name of the agent.
            data_folder (str): Path to the data folder.
            agent_context_file (str): Path to the json agent context file. Initial info about the agent.
            world_context_file (str): Path to the text world context file. Info about the world that the agent have access to.
        """
        self.logger = logging.getLogger(__name__)

        self.name = name
        self.ltm = LongTermMemory(agent_name=name, data_folder=data_folder)
        self.stm = ShortTermMemory(data_folder=data_folder, agent_context_file=agent_context_file, world_context_file=world_context_file)
        self.spatial_memory = SpatialMemory(initial_pos=map_info['initial_pos'])
        self.stm.add_memory(memory = self.name, key = 'name')
        
        # Initialize steps sequence in empty queue
        self.stm.add_memory(memory=Queue(), key='current_steps_sequence')

        ## TODO REMOVE THIS FROM HERE
        valid_actions = ['grab apple (x,y)', 'attack player (player_name)', 'go to the tree (treeId)']
        self.stm.add_memory(memory=valid_actions, key='valid_actions')

    def move(self, current_observations: str) -> str:
        """Use all the congnitive sequence of the agent to decide an action to take

        Args:
            observation (str): Observation of the environment.

        Returns:
            str: Action to take.
        """

        observation = "\n".join(current_observations)
        react = self.perceive(observation)

        if react:
            self.plan()
            self.generate_new_actions(current_observations)
        
        self.reflect(observation)

        self.execute_current_actions()

    def perceive(self, observation: str) -> None:
        """Perceives the environment and stores the observation in the long term memory. Decide if the agent should react to the observation.

        Args:
            perception (str): Perception of the environment.
        
        Returns:
            bool: True if the agent should react to the observation, False otherwise.
        """
        
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        self.ltm.add_memory(observation, {'type': 'perception', 'agent': self.name, 'timestamp': timestamp})
        self.stm.add_memory(observation, 'current_observation')

        # Decide if the agent should react to the observation
        current_plan = self.stm.get_memory('current_plan')
        world_context = self.stm.get_memory('world_context')
        react = should_react(self.name, world_context, observation, current_plan)
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


    def reflect(self, observations:str) -> None:
        """Reflects on the agent's observations and stores the insights reflections in the long term memory.
        """
        
        world_context = self.stm.get_memory('world_context')
        relevant_questions = reflect_questions(self.name, world_context, observations)
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




    def execute_current_actions(self) -> None:
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
    