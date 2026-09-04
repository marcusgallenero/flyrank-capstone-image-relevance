SIMILARITY_THRESHOLD = 0.45
CONFIDENCE_THRESHOLD = 0.85


def check_mismatch_guard(image: dict, post_subject: str, similarity: float):
    """
    Run the three checks from mismatch guard in docs/DESIGN.md on one image candidate.
    Determine rejection reason from first failed check.
    """
    if image['subject'] != post_subject:
        return False, "Image subject does not match post topic"

    if similarity < SIMILARITY_THRESHOLD:
        return False, "Image content isn't similar enough to the post"

    if image['confidence'] < CONFIDENCE_THRESHOLD:
        return False, "Vision model wasn't confident enough about this image"

    return True, None