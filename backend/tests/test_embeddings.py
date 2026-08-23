"""Tests for the embeddings module."""

import pytest
from app.embeddings import embed, cosine_similarity, warm_up, _embed_cached


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


# --- Formula correctness with synthetic vectors ------------------------------
# These don't call embed() at all: they check the cosine_similarity() math
# itself against known values, independent of the model's actual behavior.

def test_cosine_similarity_orthogonal_vectors_is_zero():
    """Perpendicular vectors share no direction."""
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_cosine_similarity_opposite_vectors_is_negative_one():
    assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)


def test_cosine_similarity_identical_synthetic_vectors_is_one():
    assert cosine_similarity([3.0, 4.0], [3.0, 4.0]) == pytest.approx(1.0)


def test_cosine_similarity_zero_vector_returns_zero_not_a_crash():
    """A zero vector would divide by zero in the raw dot/(norm*norm) formula;
    the function guards against this rather than raising or returning NaN."""
    assert cosine_similarity([0.0, 0.0, 0.0], [1.0, 2.0, 3.0]) == 0.0
    assert cosine_similarity([0.0, 0.0], [0.0, 0.0]) == 0.0


def test_cosine_similarity_dimension_mismatch_raises():
    with pytest.raises(ValueError):
        cosine_similarity([1.0, 0.0], [1.0, 0.0, 0.0])


# --- embed() edge cases -------------------------------------------------------


def test_embed_empty_string_does_not_crash():
    """matching.py's score_text() calls embed() unconditionally on
    `title + " " + description`. This codebase has already found real blank
    -field bugs elsewhere (color, location matching), so it's worth
    confirming an empty string doesn't crash the embedding path too."""
    embedding = embed("")
    assert isinstance(embedding, list)
    assert len(embedding) > 0


def test_embed_different_texts_produce_same_length_vectors():
    """cosine_similarity() assumes both vectors share a dimension -- confirm
    that holds for texts of very different lengths, not just near-duplicates."""
    short_embedding = embed("a")
    long_embedding = embed(LOST_BACKPACK)
    assert len(short_embedding) == len(long_embedding)


def test_embed_caches_repeated_calls():
    """GET /reports/{id}/matches calls score_text() once per candidate, and
    score_text() re-embeds the fixed anchor report's own text every time
    even though it never changes across the loop. embed() memoizes by text
    so a repeated identical string is served from cache instead of paying
    for another model inference."""
    _embed_cached.cache_clear()

    embed(LOST_BACKPACK)
    embed(LOST_BACKPACK)  # identical text again -> should hit the cache
    embed(FOUND_BACKPACK)  # different text -> should miss

    info = _embed_cached.cache_info()
    assert info.hits == 1
    assert info.misses == 2


def test_embed_cache_returns_independent_list_objects():
    """embed()'s contract is a fresh list[float] each call -- callers must
    not be able to corrupt the cache by mutating a returned list in place."""
    first = embed(LOST_BACKPACK)
    second = embed(LOST_BACKPACK)
    assert first == second
    assert first is not second
    first.append(999.0)
    assert embed(LOST_BACKPACK) == second


def test_warm_up_loads_the_model_without_error():
    """warm_up() runs from the app's startup lifespan (main.py) so the
    ~130MB first-run download happens at startup, not mid-request. It had no
    direct test coverage before -- confirm it succeeds and leaves the model
    usable afterward."""
    warm_up()
    embedding = embed(LOST_BACKPACK)
    assert len(embedding) > 0
