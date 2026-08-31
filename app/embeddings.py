import os
from google import genai
from google.genai.types import EmbedContentConfig

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    """Get semantic embedding vector for a piece of text"""
    response = client.models.embed_content(
        model = "gemini-embedding-001",
        contents=text,
        config = EmbedContentConfig(task_type=task_type),
    )
    return response.embeddings[0].values

if __name__ == "__main__":
    vector = embed_text("A brown bear rests on the ground near a fallen log in a forest")
    print(f"Vector length: {len(vector)}")
    print(vector[5])