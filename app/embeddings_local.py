from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str) -> list[float]:
    """Get semantic embedding vector for text"""
    vector = _model.encode(text)
    return vector.tolist()

if __name__ == "__main__":
    vector = embed_text("A brown bear rests on the ground near a fallen log in the forest")
    print(f"Vector Length: {len(vector)}")
    print(vector[:5])