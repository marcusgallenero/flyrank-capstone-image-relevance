from app.guard import check_mismatch_guard, SIMILARITY_THRESHOLD, CONFIDENCE_THRESHOLD


def test_wolf_image_rejected_for_fox_post():
    """from EVIDENCE.md: a wolf image must never be suggested for a fox post"""
    wolf_image = {"subject": "wolf", "confidence": 0.99}
    passed, reason = check_mismatch_guard(
        wolf_image, post_subject="red fox", similarity=0.9
    )
    assert passed is False
    assert reason == "Image subject does not match post topic"


def test_subject_match_passes_first_check():
    """Same subject shouldn't be rejected by  subject check"""
    image = {"subject": "red fox", "confidence": 0.99}
    passed, reason = check_mismatch_guard(image, post_subject="red fox", similarity=0.9)
    assert passed is True
    assert reason is None


def test_low_similarity_rejected_when_subject_matches():
    """Same subject but similarity below threshold should be rejected"""
    image = {"subject": "red fox", "confidence": 0.99}
    passed, reason = check_mismatch_guard(
        image, post_subject="red fox", similarity=SIMILARITY_THRESHOLD - 0.01
    )
    assert passed is False
    assert reason == "Image content isn't similar enough to the post"


def test_similarity_at_threshold_passes():
    """Similarity equal to threshold should pass"""
    image = {"subject": "red fox", "confidence": 0.99}
    passed, reason = check_mismatch_guard(
        image, post_subject="red fox", similarity=SIMILARITY_THRESHOLD
    )
    assert passed is True
    assert reason is None


def test_low_confidence_rejected_when_subject_and_similarity_pass():
    """Same subject and good similarity, but confidence below threshold should be rejected"""
    image = {"subject": "red fox", "confidence": CONFIDENCE_THRESHOLD - 0.01}
    passed, reason = check_mismatch_guard(image, post_subject="red fox", similarity=0.9)
    assert passed is False
    assert reason == "Vision model wasn't confident enough about this image"


def test_confidence_at_threshold_passes():
    """Confidence equal to threshold should pass"""
    image = {"subject": "red fox", "confidence": CONFIDENCE_THRESHOLD}
    passed, reason = check_mismatch_guard(image, post_subject="red fox", similarity=0.9)
    assert passed is True
    assert reason is None


def test_all_checks_pass():
    """Matching subject, high similarity, high confidence should pass with no reason"""
    image = {"subject": "moose", "confidence": 0.98}
    passed, reason = check_mismatch_guard(image, post_subject="moose", similarity=0.7)
    assert passed is True
    assert reason is None
