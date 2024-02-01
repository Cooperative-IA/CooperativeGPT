import logging
import os

from utils.files import load_agent_context, load_world_context
from utils.logging import CustomAdapter

class ShortTermMemory:
    """Class for yhe short term memory. Memories are stored in a dictionary.
    """

    def __init__(self,data_folder: str = None, agent_context_file: str = None, world_context_file: str = None) ->  None:
        """Initializes the short term memory.

        Args:
            data_folder (str, optional): Path to the data folder. The data folder should have an agents_context folder with the agent context files.
            agent_context_file (str, optional): Path to the json agent context file. Initial info about the agent. All the keys in the json file will be added to the short term memory.
            world_context_file (str, optional): Path to the text world context file. Info about the world that the agent have access to. The world context will be added to the short term memory with the key 'world_context'.
        """
        self.logger = logging.getLogger(__name__)
        self.logger = CustomAdapter(self.logger)
        self.memory = {}

        if agent_context_file is not None:
            agent_context_file = os.path.join(data_folder, 'agents_context', agent_context_file)
            self.memory = load_agent_context(agent_context_file)

        if world_context_file is not None:
            world_context_file = os.path.join(data_folder, 'agents_context', world_context_file)
            self.memory['world_context'] = load_world_context(world_context_file)

    def add_memory(self, memory: str, key: str) -> None:
        """Adds a memory to the short term memory.

        Args:
            memory (str): Memory to add.
            key (str): Key to access the memory.
        """
        self.logger.info(f"Adding memory to short term memory, Key: {key}. Memory: {memory}")
        self.memory[key] = memory

    def get_memory(self, key: str) -> str:
        """Gets a memory from the short term memory.

        Args:
            key (str): Key to access the memory.

        Returns:
            str or None: Memory if it exists, None otherwise.
        """
        return self.memory.get(key, None)

    def get_known_agents(self) -> set[str]:
        """Gets the known agents from the short term memory.

        Returns:
            set[str]: Set of known agents.
        """
        return self.memory.get('known_agents', set())

    def set_known_agents(self, known_agents: set[str]) -> None:
        """Sets the known agents in the short term memory.

        Args:
            known_agents (set[str]): Set of known agents.
        """
        self.add_memory(known_agents, 'known_agents')
