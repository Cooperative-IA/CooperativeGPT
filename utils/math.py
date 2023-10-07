import numpy as np

def normalize_values(values: list[float]) -> list[float]:
    """Normalize the values between 0 and 1.

    Args:
        values (list[float]): List of values to normalize.

    Returns:
        list[float]: List of normalized values.
    """
    range_ = max(values) - min(values)

    if range_ == 0:
       return [0 for _ in values]

    normalized_values = [(v - min(values)) / range_ for v in values]

    return normalized_values

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate the cosine similarity between two vectors.

    Args:
        a (list[float]): First vector.
        b (list[float]): Second vector.

    Returns:
        float: Cosine similarity between the two vectors.
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))