import logging
from datetime import datetime

from agent.memory_structures.long_term_memory import LongTermMemory
from agent.memory_structures.short_term_memory import ShortTermMemory
from agent.cognitive_modules.perceive import should_react
from agent.cognitive_modules.plan import plan

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
        self.stm.add_memory(self.name, 'name')

    def move(self, observations: list[str]) -> str:
        """Use all the congnitive sequence of the agent to decide an action to take

        Args:
            observations (list[str]): List of observations of the environment.

        Returns:
            str: Action to take.
        """
        react = self.perceive(observations)

        if react:
            self.plan()

    def perceive(self, observations: list[str]) -> None:
        """Perceives the environment and stores the observation in the long term memory. Decide if the agent should react to the observation.

        Args:
            observations (list[str]): List of observations of the environment.
        
        Returns:
            bool: True if the agent should react to the observation, False otherwise.
        """
        
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        self.ltm.add_memory(observations, [{'type': 'perception', 'agent': self.name, 'timestamp': timestamp}] * len(observations))
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

