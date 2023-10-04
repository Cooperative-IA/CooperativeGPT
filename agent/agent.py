import logging
from datetime import datetime

from agent.memory_structures.long_term_memory import LongTermMemory
from agent.memory_structures.short_term_memory import ShortTermMemory
from agent.cognitive_modules.perceive import should_react
from agent.cognitive_modules.plan import plan
from agent.cognitive_modules.reflect import reflect_questions
from agent.cognitive_modules.reflect import reflect_insights

class Agent:
    """Agent class.
    """

    def __init__(self, name: str, data_folder: str, agent_context_file: str, world_context_file: str) -> None:
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
        self.stm.add_memory(memory = self.name, key = 'name')

    def move(self, observation: str) -> str:
        """Use all the congnitive sequence of the agent to decide an action to take

        Args:
            observation (str): Observation of the environment.

        Returns:
            str: Action to take.
        """
        react = self.perceive(observation)

        if react:
            self.plan()
            self.reflect(observation)

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
  


