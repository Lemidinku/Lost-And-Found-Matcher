"""Text embeddings module using fastembed."""

import math
from fastembed import TextEmbedding


# Module-level singleton: model loaded once
_embedding_model = None


def _get_model() -> TextEmbedding:
    """Get or initialize the embedding model (singleton)."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return _embedding_model


def warm_up() -> None:
    """Force the embedding model to load (and download, on first run).

    Called from the app's startup lifespan so the one-time ~130MB
    HuggingFace download happens while `uvicorn` is starting up, not mid
    -request the first time a user clicks a report's matches.
    """
    _get_model()


def embed(text: str) -> list[float]:
    """
    Embed text using fastembed.

    Args:
        text: The text to embed.

    Returns:
        A list of floats representing the embedding.
    """
    model = _get_model()
    # fastembed.embed() returns an iterable of numpy arrays
    # We convert the first (and only) result to a plain list of floats
    embeddings = list(model.embed(text))
    if not embeddings:
        raise ValueError("Failed to generate embedding")
    # Convert numpy array to list[float]
    return embeddings[0].tolist()


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Compute cosine similarity between two embedding vectors.

    Uses the formula: dot(a, b) / (norm(a) * norm(b))
    This is correct regardless of whether vectors are pre-normalized.

    Args:
        a: First embedding vector.
        b: Second embedding vector.

    Returns:
        The cosine similarity as a float between -1 and 1.
    """
    if len(a) != len(b):
        raise ValueError("Embeddings must have the same dimension")

    # Compute dot product
    dot_product = sum(x * y for x, y in zip(a, b))

    # Compute norms
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    # Avoid division by zero
    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)
