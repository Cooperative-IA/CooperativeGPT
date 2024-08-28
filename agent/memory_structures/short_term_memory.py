import logging
import os

from utils.files import load_world_context
from utils.logging import CustomAdapter

class ShortTermMemory:
    """Class for yhe short term memory. Memories are stored in a dictionary.
    """

    def __init__(self, agent_context: dict = None, world_context_file: str = None) ->  None:
        """Initializes the short term memory.

        Args:
            agent_context_file (dict, optional): Json agent context file. Initial info about the agent. All the keys in the json file will be added to the short term memory.
            world_context_file (str, optional): Path to the text world context file. Info about the world that the agent have access to. The world context will be added to the short term memory with the key 'world_context'.
        """
        self.logger = logging.getLogger(__name__)
        self.logger = CustomAdapter(self.logger)
        self.memory = {}

        if agent_context is not None:
            self.memory = agent_context

        if world_context_file is not None:
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
    
    def get_memories(self) -> dict:
        """Gets all the memories from the short term memory.

        Returns:
            dict: All the memories.
        """
        return self.memory

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


    def get_known_objects_by_key(self, object_key:str) -> set[str]:
        """Gets the known objects from the short term memory.
        Allows to get objects like known trees, known sectors, etc.
        
        Returns:
            set[str]: Set of known objects.
        """
        return self.memory.get(object_key, set())
    
    def set_known_objects_by_key(self, known_objects: set[str], object_key:str) -> None:
        """Sets the known objects in the short term memory.
        It lets set objects like known trees, known sectors, etc.
        Args:
            known_objects (set[str]): Set of known objects.
        """
        self.add_memory(known_objects, object_key)
        
        
      
    
    def load_memories_from_scene(self, scene_path: str, agent_name:str) -> None:
        """Loads memories from a scene file.

        Args:
            scene_path (str): Path to the scene file.
            agent_name (str): Name of the agent.
        """
        source_stm_path = os.path.join(scene_path, "short_term_memories.txt")
        
        #Read the file and load the memories
        scene_memories = eval(open(source_stm_path).read())
        agent_memory = scene_memories.get(agent_name, self.memory)
        self.memory = agent_memory
        logging.info(f"Loaded memories from scene for agent {agent_name}. Memories: {agent_memory}")