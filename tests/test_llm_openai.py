from dotenv import load_dotenv

from llm import LLMModels

# load environment variables
load_dotenv(override=True)

llm = LLMModels()
embedding_model = llm.get_embedding_model()

def test_get_embedding():
    # Test that the embedding return a list of floats
    text = "This is a test"
    embedding = embedding_model.get_embedding(text)
    assert isinstance(embedding, list), "The embedding is not a list"
    assert all(isinstance(e, float) for e in embedding), "The embedding is not a list of floats"

    # Test that length of the embedding is correct
    assert len(embedding) == embedding_model.embedding_dimensions, f"The length of the embedding is not {embedding_model.embedding_dimensions}"

    # Test that the embedding is not all zeros
    assert not all(e == 0 for e in embedding), "The embedding is all zeros"

    # Test that the cost and the number of tokens are updated
    costs = embedding_model.cost_manager.get_costs()
    tokens = embedding_model.cost_manager.get_tokens()
    assert costs["prompt_cost"] > 0, "The prompt cost is 0"
    assert costs["total_cost"] > 0, "The total cost is 0"
    assert tokens["prompt_tokens"] > 0, "The prompt tokens are 0"
    assert tokens["total_tokens"] > 0, "The total tokens are 0"

def test_get_embeddings():
    # Test that the embeddings return a list of lists of floats
    texts = ["This is a test", "This is another test"]
    embeddings = embedding_model.get_embeddings(texts)
    assert isinstance(embeddings, list), "The embeddings are not a list"