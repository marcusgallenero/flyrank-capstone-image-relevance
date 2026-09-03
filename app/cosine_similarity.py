import numpy as np

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity ((A · B) / (|A| x |B|)) between two vectors"""
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    result = dot_product / (norm_a * norm_b)
    return result