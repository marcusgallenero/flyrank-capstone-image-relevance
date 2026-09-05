import pytest
from app.cosine_similarity import cosine_similarity


def test_identical_vectors():
    """Identical vectors should point in the direction: similarity = 1.0"""
    a = [1.0, 2.0, 3.0]
    result = cosine_similarity(a, a)
    assert result == pytest.approx(1.0)


def test_orthogonal_vectors():
    """Perpendicular vectors share no directional overlap: similarity = 0.0"""
    a = [1.0, 0.0]
    b = [0.0, 1.0]
    result = cosine_similarity(a, b)
    assert result == pytest.approx(0.0)


def test_opposite_vectors():
    """Vectors pointing in exactly opposite directions: similarity = -1.0"""
    a = [1.0, 0.0]
    b = [-1.0, 0.0]
    result = cosine_similarity(a, b)
    assert result == pytest.approx(-1.0)


def test_scaled_vectors():
    """For cosine sim. direction matters, not magnitude"""
    a = [1.0, 2.0]
    b = [2.0, 4.0]  # same direction, but scaled
    result = cosine_similarity(a, b)
    assert result == pytest.approx(1.0)
