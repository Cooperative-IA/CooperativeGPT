import os
import logging

import chromadb
import uuid
from chromadb.utils import embedding_functions

from utils.time import str_to_timestamp
from utils.logging import CustomAdapter
from utils.llm import CustomEmbeddingFunction

class LongTermMemory:
    """Class for long term memory. Memories are stored in the chromadb database.
    """

    def __init__(self, agent_name: str, data_folder: str):
        """Initializes the long term memory.

        Args:
            agent_name (str): Name of the agent.
            data_folder (str): Path to data folder.
        """
        db_path = os.path.join(data_folder, agent_name, "long_term_memory.db")
        self.chroma_client = chromadb.PersistentClient(path=db_path)

        self.logger = logging.getLogger(__name__)
        self.logger = CustomAdapter(self.logger)

        self.name = agent_name

        # Delete collection if it already exists
        if agent_name in [c.name for c in self.chroma_client.list_collections()]:
            self.chroma_client.delete_collection(agent_name)

        # Use a custom model to create the embeddings
        openai_ef = CustomEmbeddingFunction()

        self.collection = self.chroma_client.create_collection(agent_name, embedding_function=openai_ef)

    def add_memory(self, memory: str | list[str], created_at: str | list[str], poignancy: int | list[int], additional_metadata: dict | list[dict] = None):
        """Adds a memory to the long term memory.

        Args:
            memory (str | list[str]): Memory or memories to add.
            created_at (str | list[str]): Date when the memory was created.
            poignancy (str | list[str]): Poignancy of the memory.
            additional_metadata (dict | list[dict], optional): Addictional metadata for the memory or memories. Defaults to None.
        """

        # Create metadata
        if isinstance(memory, list):
            # Check if created_at and poignancy are lists. If they are, they must have the same length as memory
            if (isinstance(created_at, list) or isinstance(poignancy, list)) and (len(memory) != len(created_at) or len(memory) != len(poignancy)):
                self.logger.error(f"If memory is a list, created_at and poignancy must be lists with the same length or single values. Memory(len): {len(memory)}, created_at(len): {len(created_at)}, poignancy(len): {len(poignancy)}")
                raise ValueError(f"If memory is a list, created_at and poignancy must be lists with the same length or single values. Memory(len): {len(memory)}, created_at(len): {len(created_at)}, poignancy(len): {len(poignancy)}")
            # If created_at and poignancy are not lists, create lists with the same value for all memories
            if isinstance(created_at, str):
                created_at = [created_at for _ in range(len(memory))]
            if not isinstance(poignancy, list):
                poignancy = [poignancy for _ in range(len(memory))]

            # Check if additional_metadata is a list. If it is, it must have the same length as memory
            if isinstance(additional_metadata, list) and len(memory) != len(additional_metadata):
                self.logger.error(f"If memory is a list, additional_metadata must be a list with the same length or a single value. Memory(len): {len(memory)}, additional_metadata(len): {len(additional_metadata)}")
                raise ValueError(f"If memory is a list, additional_metadata must be a list with the same length or a single value. Memory(len): {len(memory)}, additional_metadata(len): {len(additional_metadata)}")
            # If additional_metadata is not a list, create a list with the same value for all memories
            elif isinstance(additional_metadata, dict):
                additional_metadata = [additional_metadata for _ in range(len(memory))]
            # If additional_metadata is None, create an empty list
            elif additional_metadata is None:
                additional_metadata = [{} for _ in range(len(memory))]

            # Create metadata for each memory
            metadata = [{"created_at": c, "poignancy": p, **additional_metadata[i], "timestamp": str_to_timestamp(c)} for i, (c, p) in enumerate(zip(created_at, poignancy))]
        else:
            metadata = additional_metadata if additional_metadata else {}
            metadata["created_at"] = created_at
            metadata["poignancy"] = poignancy
            metadata["timestamp"] = str_to_timestamp(created_at)


        self.logger.info(f"Adding memory to long term memory, Metadata: {metadata}. Memory: {memory}")
        # Check if memory is a list
        if isinstance(memory, list):
            self.collection.add(documents=memory, metadatas=metadata, ids=[str(uuid.uuid4()) for _ in range(len(memory))])
        else:
            self.collection.add(documents=[memory], metadatas=[metadata], ids=[str(uuid.uuid4())])

    def get_relevant_memories(self, query: str, n_results: int = 10, return_metadata: bool = False, filter = None) -> list[str] | tuple[list[str], list[dict]]:
        """Gets relevant memories from the long term memory.

        Args:
            query (str): Query to search for.
            n_results (int, optional): Number of results to return. Defaults to 10.
            return_metadata (bool, optional): Whether to return the metadata of the memories. Defaults to False.
            filter (dict, optional):  A dictionary with the metadata to filter the memories. Defaults to None. This filter must be specified as the "where" filter for the query as defined for chromadb: https://docs.trychroma.com/usage-guide#using-where-filters.

        Returns:
            list[str]: List of relevant memories.
        """
        results = self.collection.query(query_texts=[query], n_results=n_results, where=filter)

        # Formats the results to list of strings
        memories = results['documents'][0] if results['documents'] else []
        if return_metadata:
            return memories, results['metadatas'][0] if results['metadatas'] else []
        
        return memories
    
    def get_memories(self, limit: int = 50, filter: dict = None, include_embeddings : bool = False, reversed_order = False) -> dict:
        """Gets memories from the long term memory and return them sorted in descending order.

        Args:
            limit (int, optional): Number of results to return. Defaults to 50.
            filter (dict, optional):  A dictionary with the metadata to filter the memories. Defaults to None. This filter must be specified as the "where" filter for the query as defined for chromadb: https://docs.trychroma.com/usage-guide#using-where-filters.
            include_embeddings (bool, optional): Whether to include the embeddings in the results. Defaults to False.
            reversed_order (bool, optional): The most recent memories are returned, but from the oldest to the most recent. Defaults to False.

        Returns:
            dict: List of memories. The memories are returned as a dictionary with the following structure: {"ids": list[str], "documents": list[str], "metadatas": list[dict], "embeddings": list[list[float]]}
        """

        if include_embeddings:
            results = self.collection.get(where=filter, include=['documents', 'metadatas', 'embeddings'])
        else:
            results = self.collection.get(where=filter, include=['documents', 'metadatas'])
        
        # Reverse the order of the results and slice them to the limit
        results['ids'] = results['ids'][::-1][:limit]
        results['documents'] = results['documents'][::-1][:limit]
        results['metadatas'] = results['metadatas'][::-1][:limit]
        results['embeddings'] = results['embeddings'][::-1][:limit] if include_embeddings else None

        if reversed_order:
            results['ids'] = results['ids'][::-1]
            results['documents'] = results['documents'][::-1]
            results['metadatas'] = results['metadatas'][::-1]
            results['embeddings'] = results['embeddings'][::-1] if include_embeddings else None
            
        return results
    
    def create_embedding(self, text: str) -> list[float]:
        """Creates an embedding for the given text.

        Args:
            text (str): Text to create the embedding for.

        Returns:
            list[float]: Embedding for the text.
        """
        return self.collection._embedding_function([text])[0]
    
    
    def load_memories_from_scene(self, scene_path: str, agent_name:str) -> None:
        """Loads memories from a scene file.

        Args:
            scene_path (str): Path to the scene file.
            agent_name (str): Name of the agent.
        """
        source_db_path = os.path.join(scene_path, "ltm_database", agent_name, "long_term_memory.db")

        # If the source database does not exist, log a warning and return 
        if not os.path.exists(source_db_path):
            self.logger.warning(f"Could not find the long term memory database at {source_db_path}")
            return
        chroma_scene_client = chromadb.PersistentClient(path=source_db_path)
        source_collection = chroma_scene_client.get_collection(agent_name)
        source_data = source_collection.get()
        self.collection.add(documents=source_data['documents'], metadatas=source_data['metadatas'], ids=source_data['ids'])
