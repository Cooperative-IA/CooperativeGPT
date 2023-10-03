import logging
from datetime import datetime

from agent.memory_structures.long_term_memory import LongTermMemory
from agent.memory_structures.short_term_memory import ShortTermMemory
from agent.cognitive_modules.perceive import should_react

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

    def move(self, observation: str) -> str:
        """Use all the congnitive sequence of the agent to decide an action to take

        Args:
            observation (str): Observation of the environment.

        Returns:
            str: Action to take.
        """
        self.perceive(observation)

    def perceive(self, observation: str) -> None:
        """Perceives the environment and stores the observation in the long term memory.

        Args:
            perception (str): Perception of the environment.
        """
        
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        self.ltm.add_memory(observation, {'type': 'perception', 'agent': self.name, 'timestamp': timestamp})

        # Decide if the agent should react to the observation
        current_plan = self.stm.get_memory('current_plan')
        react = should_react(self.name, observation, current_plan)
        self.logger.info(f'{self.name} should react to the observation: {react}')
