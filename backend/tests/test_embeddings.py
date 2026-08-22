"""Tests for the embeddings module."""

import pytest
from app.embeddings import embed, cosine_similarity


# Exact strings from the assessment brief
LOST_BACKPACK = "Black backpack containing a laptop charger. Lost around the library on Monday afternoon."
FOUND_BACKPACK = "Dark-colored backpack found near the library entrance Monday evening."
FOUND_EARBUD_CASE = "Found a dark wireless earbud case beside the coffee shop."


def test_identical_text_similarity():
    """Identical text should have cosine similarity > 0.99."""
    embedding = embed(LOST_BACKPACK)
    similarity = cosine_similarity(embedding, embedding)
    print(f"\nIdentical text cosine similarity: {similarity}")
    assert similarity > 0.99


def test_related_vs_unrelated_similarity():
    """Related pair should score higher than unrelated pair."""
    lost_emb = embed(LOST_BACKPACK)
    found_backpack_emb = embed(FOUND_BACKPACK)
    found_earbud_emb = embed(FOUND_EARBUD_CASE)

    related_similarity = cosine_similarity(lost_emb, found_backpack_emb)
    unrelated_similarity = cosine_similarity(lost_emb, found_earbud_emb)

    print(f"Related pair (LOST vs FOUND_BACKPACK) cosine similarity: {related_similarity}")
    print(f"Unrelated pair (LOST vs FOUND_EARBUD_CASE) cosine similarity: {unrelated_similarity}")

    assert related_similarity > unrelated_similarity


def test_embed_returns_list_of_floats():
    """embed() should return a list of floats."""
    embedding = embed(LOST_BACKPACK)
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)


def test_cosine_similarity_returns_float():
    """cosine_similarity() should return a float."""
    emb1 = embed(LOST_BACKPACK)
    emb2 = embed(FOUND_BACKPACK)
    similarity = cosine_similarity(emb1, emb2)
    assert isinstance(similarity, float)


def test_cosine_similarity_same_vector_is_one():
    """Cosine similarity of a vector with itself should be 1.0 (or very close)."""
    emb = embed(LOST_BACKPACK)
    similarity = cosine_similarity(emb, emb)
    assert 0.99 < similarity <= 1.01  # Allow for floating point precision
