import logging
import traceback
from datetime import datetime
import numpy as np

from agent.agent import Agent
from utils.files import load_config
from utils.math import normalize_values, cosine_similarity
from utils.logger_singleton import LoggerSingleton

logger_instance = LoggerSingleton()

logger = logging.getLogger(__name__)

def retrieve_relevant_memories(agent: Agent, query: str, max_memories: int = 10, metadata_filter: dict = None) -> list[str]:
    """
    Retrieve the most relevant memories for the given query. Calculate a relevancy score for each memory and return the top N memories.
    The relevancy score is calculated with the following formula:
    score = w1 * recency * w2 * poignancy * w3 * similarity
    
    Args:
        agent (Agent): The agent that is retrieving the memories.
        query (str): The query to retrieve memories for.
        max_memories (int, optional): The maximum number of memories to retrieve. Defaults to 10.
        metadata_filter (dict, optional): A dictionary with the metadata to filter the memories. Defaults to None. This filter must be specified as the "where" filter for the query as defined for chromadb: https://docs.trychroma.com/usage-guide#using-where-filters.

    Returns:
        list[str]: A list of memories.
    """

    # Weights for the rececny, poignancy and similarity factors
    factor_weights = [1, 1, 1]

    # Get the memories from the database
    memories = agent.ltm.get_memories(limit=100, filter=metadata_filter, include_embeddings=True)
    # Create a list of memories with the following structure: (memory, recency, poignancy, similarity)
    try:
        memories = [[m[0], m[1]['created_at'], m[1]['poignancy'], m[2]] for m in zip(memories['documents'], memories['metadatas'], memories['embeddings'])]
    except TypeError:
        logger.error('The database should return a list for the documents, metadatas and embeddings keys. Check the database. The database returned: documents: %s, metadatas: %s, emebeddings: %s', type(memories['documents']), type(memories['metadatas']), type(memories['embeddings']))
    except KeyError:
        logger.error('Each memory should have a created_at and poignancy metadata. Error traceback: %s', traceback.format_exc())

    # Sort the memories by created_at
    date_format = load_config()['date_format']
    memories.sort(key=lambda x: datetime.strptime(x[1], date_format), reverse=True)

    memories_text = [m[0] for m in memories]

    # Calculate the recency factor
    recency_scores = get_recency_scores(memories, date_format)
    # Calculate the poignancy factor
    poignancy_scores = get_poignancy_scores(memories)
    # Calculate the similarity factor
    similarity_scores = get_similarity_scores(agent, memories, query)

    # Calculate the relevancy score for each memory
    relevancy_scores = [factor_weights[0] * recency_scores[i] + factor_weights[1] * poignancy_scores[i] + factor_weights[2] * similarity_scores[i] for i in range(len(memories))]
    # Sort the memories by relevancy score
    memories_text = sorted(memories_text, key=lambda x: relevancy_scores[memories_text.index(x)], reverse=True)

    # Return the top N memories
    return memories_text[:max_memories]


def get_recency_scores(memories: list[list], date_format: str) -> list[float]:
    """Calculate the recency score for each memory. The recency score is calculated with the following formula:
    recency_score = 0.99 ^ (hours since last memory)

    Args:
        memories (list[list]): List of memories with the following structure: (memory, recency, poignancy, similarity) ordered by recency.
        date_format (str): Format of the date in the memories.

    Returns:
        list[float]: List of recency scores.
    """
    # Get the created_at date of each memory
    mem_dates = [m[1] for m in memories]
    # Get last memory date
    last_date = datetime.strptime(mem_dates[0], date_format)
    # Calculate the hours since the last memory
    hours_since_last_memory = [int((last_date - datetime.strptime(mem_date, date_format)).total_seconds() / 3600) for mem_date in mem_dates]
    # Calculate the recency score for each memory
    recency_scores = [0.99 ** h for h in hours_since_last_memory]

    return recency_scores

def get_poignancy_scores(memories: list[list]) -> list[float]:
    """Calculate the poignancy score for each memory. The poignancy score is normalized between 0 and 1.

    Args:
        memories (list[list]): List of memories with the following structure: (memory, recency, poignancy, similarity) ordered by recency.

    Returns:
        list[float]: List of poignancy scores.
    """
    # Get the poignancy of each memory
    poignancies = [m[2] for m in memories]
    # Normalize the poignancies between 0 and 1
    poignancy_scores = normalize_values(poignancies)

    return poignancy_scores

def get_similarity_scores(agent: Agent, memories: list[list], query: str) -> list[float]:
    """Calculate the similarity score for each memory. The similarity score is normalized between 0 and 1.

    Args:
        agent (Agent): The agent that is retrieving the memories.
        memories (list[list]): List of memories with the following structure: (memory, recency, poignancy, similarity) ordered by recency.
        query (str): The query to retrieve memories for.

    Returns:
        list[float]: List of similarity scores.
    """
    # Get the embeddings of each memory
    embeddings = [m[3] for m in memories]
    # Create the embedding for the query
    query_embedding = agent.ltm.create_embedding(query)
    # Calculate the similarity between the query and each memory
    similarities = [cosine_similarity(query_embedding, embedding) for embedding in embeddings]
    # Normalize the similarities between 0 and 1
    similarity_scores = normalize_values(similarities)

    return similarity_scores
    
