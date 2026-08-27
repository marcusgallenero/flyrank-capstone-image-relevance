import os
import mimetypes
from google import genai
from google.genai import types
from app.schemas import Metadata

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def tag_image(image_path: str) -> Metadata:
    """Send a local image to Gemini and get back structured tags"""
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    mime_type, _ = mimetypes.guess_type(image_path)

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        # Input image and prompt to model
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            "Analyze this wildlife photo and produce structured tags.",
        ],
        # Establish output format
        config={"response_mime_type": "application/json", "response_schema": Metadata},
    )

    return response.parsed


if __name__ == "__main__":
    result = tag_image("data/images/bear/bear_01.jpg")
    print(result)
