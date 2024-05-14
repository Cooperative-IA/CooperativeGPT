import logging
import os

from utils.files import load_agent_context, load_world_context
from utils.logging import CustomAdapter

class ShortTermMemory:
    """Class for yhe short term memory. Memories are stored in a dictionary.
    """

    def __init__(self, agent_name, agent_context_file: str = None, world_context_file: str = None) ->  None:
        """Initializes the short term memory.

        Args:
            agent_context_file (str, optional): Path to the json agent context file. Initial info about the agent. All the keys in the json file will be added to the short term memory.
            world_context_file (str, optional): Path to the text world context file. Info about the world that the agent have access to. The world context will be added to the short term memory with the key 'world_context'.
        """
        self.logger = logging.getLogger(__name__)
        self.logger = CustomAdapter(self.logger)
        self.memory = {}
        self.last_observations = []
        self.name = agent_name


        if agent_context_file is not None:
            self.memory = load_agent_context(agent_context_file)

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

    def check_known_observation(self, observation: str) -> bool:
        if observation not in self.last_observations:
            self.last_observations.append(observation)
            return True
        return False
        
    def clear_last_observations(self) -> None:
        self.last_observations = []

    def add_known_agent_interaction(self, rounds_count, agent, interaction, info) -> None:
        if self.check_known_observation(str(rounds_count)+agent + interaction + info):
            agent_interactions = self.memory.setdefault("known_agent_interactions", {}).setdefault(agent, {})
            if interaction == "ate_apple":
                agent_interactions["apples_eaten"] = agent_interactions.get("apples_eaten", 0) + 1
            elif interaction == "attacks_made":
                agent_interactions["attacks_made"] = agent_interactions.get("attacks_made", 0) + 1
            elif interaction == "attacks_received":
                agent_interactions["attacks_received"] = agent_interactions.get("attacks_received", 0) + 1
            return True
        return False

    def get_known_agent_interactions(self, agent) -> dict:
        """Gets the known agent interactions from the short term memory.

        Returns:
            dict: Dictionary of known agent interactions.
        """
        return self.memory.get("known_agent_interactions", {}).get(agent, {})
    

    def describe_known_agents_interactions(self):
        data = self.memory.get("known_agent_interactions", None)
        if data is None:
            return []
        descriptions = []
        for name, actions in data.items():
            if name == self.name:
                parts = []
                if 'apples_eaten' in actions:
                    parts.append(f"you have eaten {actions['apples_eaten']} apples")
                if 'attacks_made' in actions:
                    parts.append(f"you have made {actions['attacks_made']} attacks")
                if 'attacks_received' in actions:
                    parts.append(f"you have received {actions['attacks_received']} attacks")
                descriptions.append(f"So far, {', and '.join(parts)}")
            else:
                parts = []
                if 'apples_eaten' in actions:
                    parts.append(f"has eaten {actions['apples_eaten']} apples")
                if 'attacks_made' in actions:
                    parts.append(f"has made {actions['attacks_made']} attacks")
                if 'attacks_received' in actions:
                    parts.append(f"has received {actions['attacks_received']} attacks")
                descriptions.append(f"So far, {name} {', and '.join(parts)}")
        return descriptions
    
    def get_current_agreements(self) -> dict:
        return self.memory.get("current_agreements", {})
    
    def create_agreement(self, agent:str, agreement: str) -> None:
        self.memory.setdefault("current_agreements", {})[agent] = agreement

    def modify_agreement(self, agent:str, agreement: str) -> None:
        self.memory.setdefault("current_agreements", {})[agent] = agreement

    def revoke_agreement(self, agent:str) -> None:
        self.memory.get("current_agreements", {}).pop(agent, None)

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