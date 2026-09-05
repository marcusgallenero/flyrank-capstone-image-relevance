import pytest
from pydantic import ValidationError
from app.schemas import Metadata, ImageCreate, PostCreate, ReviewCreate


def test_metadata_valid_confidence():
    """Confidence within [0.0, 1.0] should be accepted"""
    m = Metadata(
        subject="fox",
        category="mammal",
        attributes=["red"],
        caption="a fox",
        confidence=0.5,
    )
    assert m.confidence == 0.5


def test_metadata_confidence_lower_bound():
    """0.0 is a valid confidence (inclusive lower bound)"""
    m = Metadata(
        subject="fox",
        category="mammal",
        attributes=["red"],
        caption="a fox",
        confidence=0.0,
    )
    assert m.confidence == 0.0


def test_metadata_confidence_upper_bound():
    """1.0 is a valid confidence (inclusive upper bound)"""
    m = Metadata(
        subject="fox",
        category="mammal",
        attributes=["red"],
        caption="a fox",
        confidence=1.0,
    )
    assert m.confidence == 1.0


def test_metadata_confidence_above_limit():
    """Confidence over 1.0 should raise a validation error"""
    with pytest.raises(ValidationError):
        Metadata(
            subject="fox",
            category="mammal",
            attributes=["red"],
            caption="a fox",
            confidence=1.5,
        )


def test_metadata_confidence_below_limit():
    """Negative confidence should raise a validation error"""
    with pytest.raises(ValidationError):
        Metadata(
            subject="fox",
            category="mammal",
            attributes=["red"],
            caption="a fox",
            confidence=-0.1,
        )


def test_image_create_requires_file_path():
    """ImageCreate extends Metadata and must also require file_path"""
    with pytest.raises(ValidationError):
        ImageCreate(
            subject="fox",
            category="mammal",
            attributes=["red"],
            caption="a fox",
            confidence=0.9,
        )  # file_path missing


def test_post_create_requires_all_fields():
    """PostCreate must require subject, title, and body"""
    with pytest.raises(ValidationError):
        PostCreate(subject="fox", title="A Fox")  # body missing


def test_review_create_accepts_valid_decision():
    r = ReviewCreate(decision="approved")
    assert r.decision == "approved"


def test_review_create_rejects_invalid_decision():
    """Only 'approved' or 'rejected' are valid decisions"""
    with pytest.raises(ValidationError):
        ReviewCreate(decision="maybe")
