from app.embeddings_local import embed_text
from app.cosine_similarity import cosine_similarity

SEMANTIC_THRESHOLD = 0.45


def test_scientific_name():
    """'Red fox' and 'vulpes vulpes' should be recognized as semantically close"""
    vec_common_name = embed_text("A red fox in the forest")
    vec_scientific_name = embed_text("Vulpes vulpes in the forest")

    similarity = cosine_similarity(vec_common_name, vec_scientific_name)

    assert similarity > SEMANTIC_THRESHOLD


def test_unrelated_concepts():
    """Two different wording but same meaning phrases should score higher than unrelated topics"""
    vec_fox = embed_text("Red Fox")
    vec_scientific = embed_text("Vulpes vulpes")
    vec_unrelated = embed_text("Goldfish")

    fox_sim = cosine_similarity(vec_fox, vec_scientific)
    unrelated_sim = cosine_similarity(vec_fox, vec_unrelated)

    assert fox_sim > unrelated_sim