import os
import logging

import chromadb
import uuid
from chromadb.utils import embedding_functions

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

        # Delete collection if it already exists
        if agent_name in [c.name for c in self.chroma_client.list_collections()]:
            self.chroma_client.delete_collection(agent_name)

        # Use OpenAI to create the embeddings
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("AZURE_OPENAI_KEY_GPT3"),
                api_base=os.getenv("AZURE_OPENAI_ENDPOINT_GPT3"),
                api_type=os.getenv("OPENAI_API_TYPE"),
                api_version=os.getenv("OPENAI_API_VERSION"),
                model_name=os.getenv("TEXT_EMMBEDDING_MODEL_ID")
            )

        self.collection = self.chroma_client.create_collection(agent_name, embedding_function=openai_ef)

    def add_memory(self, memory: str | list[str], created_at: str | list[str], poignancy: str | list[str], additional_metadata: dict | list[dict] = None):
        """Adds a memory to the long term memory.

        Args:
            memory (str | list[str]): Memory or memories to add.
            created_at (str | list[str]): Date when the memory was created.
            poignancy (str | list[str]): Poignancy of the memory.
            additional_metadata (dict | list[dict], optional): Addictional metadata for the memory or memories. Defaults to None.
        """

        # Create metadata
        if isinstance(memory, list):
            metadata = [{"created_at": c, "poignancy": p, **additional_metadata[i]} for i, (c, p) in enumerate(zip(created_at, poignancy))]
        else:
            metadata = additional_metadata if additional_metadata else {}
            metadata["created_at"] = created_at
            metadata["poignancy"] = poignancy


        self.logger.info(f"Adding memory to long term memory, Metadata: {metadata}. Memory: {memory}")
        # Check if memory is a list
        if isinstance(memory, list):
            self.collection.add(documents=memory, metadatas=metadata, ids=[str(uuid.uuid4()) for _ in range(len(memory))])
        else:
            self.collection.add(documents=[memory], metadatas=[metadata], ids=[str(uuid.uuid4())])

    def get_relevant_memories(self, query: str, n_results: int = 10):
        """Gets relevant memories from the long term memory.

        Args:
            query (str): Query to search for.
            n_results (int, optional): Number of results to return. Defaults to 10.

        Returns:
            list[str]: List of relevant memories.
        """
        results = self.collection.query(query_texts=[query], n_results=n_results)
        # Formats the results to list of strings
        results = [r[0] for r in results['documents'] if r]
        return results
    
    def get_memories(self, limit: int = 50, filter: dict = None) -> dict:
        """Gets memories from the long term memory.

        Args:
            limit (int, optional): Number of results to return. Defaults to 50.
            filter (dict, optional):  A dictionary with the metadata to filter the memories. Defaults to None. This filter must be specified as the "where" filter for the query as defined for chromadb: https://docs.trychroma.com/usage-guide#using-where-filters.

        Returns:
            dict: List of memories. The memories are returned as a dictionary with the following structure: {"ids": list[str], "documents": list[str], "metadatas": list[dict], "embeddings": list[list[float]]}
        """
        results = self.collection.get(limit=limit, where=filter, include=['documents', 'metadatas', 'embeddings'])
        return results
    
    def create_embedding(self, text: str) -> list[float]:
        """Creates an embedding for the given text.

        Args:
            text (str): Text to create the embedding for.

        Returns:
            list[float]: Embedding for the text.
        """
        return self.collection._embedding_function([text])[0]