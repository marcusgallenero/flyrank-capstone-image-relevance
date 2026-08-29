import os
import mimetypes
import logging
from google import genai
from google.genai import types
from app.schemas import Metadata

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Standard pricing per 1M tokens, gemini 3.5-flash-lite in USD
# https://ai.google.dev/gemini-api/docs/pricing#gemini-3.5-flash-lite
INPUT_COST = 0.30
OUTPUT_COST = 2.50

logger = logging.getLogger("vision_costs")


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

    _log_cost(image_path, response)
    return response.parsed


def _log_cost(image_path: str, response) -> None:
    """Estimate and log the cost of one gemini call, based on token usage"""
    usage = response.usage_metadata
    input_tokens = usage.prompt_token_count
    output_tokens = usage.candidate_token_count

    cost = (input_tokens / 1_000_000 * INPUT_COST) + (
        output_tokens / 1_000_000 * OUTPUT_COST
    )

    logger.info(
        f"{image_path}: {input_tokens} in / {output_tokens} out tokens\n Estimated: ${cost:.6f}"
    )


if __name__ == "__main__":
    result = tag_image("data/images/bear/bear_01.jpg")
    print(result)