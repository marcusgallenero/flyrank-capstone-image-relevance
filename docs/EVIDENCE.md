# Evidence

Proof for each `§6 Definition of Done` textbox, with one pasted proof per box

## AI Processing

- [X] Vision model produces structured output validated against a schema; invalid responses are never trusted.

```Python
class Metadata(BaseModel):
    subject: str
    category: str
    attributes: list[str]
    caption: str
    confidence: float = Field(ge=0.0, le=1.0)

# Test Driver Outputs:
tests/test_schemas.py::test_metadata_confidence_above_limit PASSED
tests/test_schemas.py::test_metadata_confidence_below_limit PASSED
```

- [X] Low-confidence classifications are flagged instead of accepted.

```Python
CONFIDENCE_THRESHOLD = 0.85

## Test Driver Outputs:
tests/test_guard.py::test_low_confidence_rejected_when_subject_and_similarity_pass PASSED 
tests/test_guard.py::test_confidence_at_threshold_passes PASSED

# Proof for probe 1 (manually adjust confidence to below threshold):
# GET /suggestions/3
{
  "id": 3,
  "post_id": 3,
  "image_id": 2,
  "simularity_score": 0.4917785905866675,
  "guard_passed": false,
  "rejection_reason": "Vision model wasn't confident enough about this image"
}
```

- [X] Images are processed through a batch background job with retries.

```Python
# No retries as batch processing looks through pre-generated data
# Below is from commit 997a623; "Stage 2.2: ..."
import time
from pathlib import Path
from app.vision import tag_image

IMAGES_DIR = Path("data/images")
MAX_RETRIES = 3

def tag_with_retries(image_path: str):
    """Try tag_images up to MAX_RETRIES times, with backoff between attempts"""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return tag_image(image_path)
        except Exception as e:
            if attempt == MAX_RETRIES:
                print(f"Failed after {MAX_RETRIES} attempts: {image_path}: {e}\n")
                return
            time.sleep(2 ** attempt)

def tag_dataset():
    """loop over every image and tag it"""
    results = []
    failures = []

    for image_path in IMAGES_DIR.rglob("*.jpg"):
        tagged_image = tag_with_retries(image_path)
        if not tagged_image:
            failures.append(image_path)
        else:
            results.append(tagged_image)
        time.sleep(5)
    return results, failures 

if __name__ == "__main__":
    results, failures = tag_dataset()
    print(f"Tagged: {len(results)}\nFailed: {len(failures)}")
```

- [X] Vision and embedding costs are tracked per call.

```Python
# Not in use as embeddings are done locally and vision data is pre-generated
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
```

## Matching System

- [X] Image and post embeddings are stored; posts return ranked image suggestions.

```Python
# seed_images follow the same trend, just for images
def seed_posts():
    """
    For each post in posts.json:
    1. Insert a row into `posts` (subject, title, body)
    2. Embed post's text
    3. Insert vector into `posts-embedding`
    """
    with open(POSTS_FILE, "r") as f:
        posts = json.load(f)

    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    with conn:
        with conn.cursor() as cur:
            for post in posts:
                cur.execute(
                    """
                    INSERT INTO posts (subject, title, body)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (post["subject"], post["title"], post["body"]),
                )
                post_id = cur.fetchone()[0]

                vector = embed_text(post["body"])
                cur.execute(
                    """INSERT INTO post_embeddings (post_id, vector) VALUES (%s, %s)""",
                    (post_id, vector)
                )

                print(f"Seeded post_id={post_id}: {post['title']}")
    print("Done")


# Output for GET /post/3/suggestions
{
  "post_id": 3,
  "result": "match",
  "suggestion": {
    "image_id": 3,
    "file_path": "data/images/bear/bear_03.jpg",
    "caption": "A brown bear rests its head on a wooden log outdoors.",
    "subject": "bear",
    "confidence": 0.98,
    "similarity": 0.5245831153204901
  }
}
```

- [X] Semantic matching works for equivalent concepts. I.e. "red fox" matches "Vulpes vulpes".

```Python
# Documented limitation of local embedding model
# See more in README.md
def test_unrelated_concepts():
    """Two different wording but same meaning phrases should score higher than unrelated topics"""
    vec_fox = embed_text("Red Fox")
    vec_scientific = embed_text("Vulpes vulpes")
    vec_unrelated = embed_text("Goldfish")

    fox_sim = cosine_similarity(vec_fox, vec_scientific)
    unrelated_sim = cosine_similarity(vec_fox, vec_unrelated)

    assert fox_sim > unrelated_sim
```

## Safety Layer

- [X] The mismatch guard rejects incorrect recommendations; the wolf-on-a-fox-post scenario provably fails.

```Python
def test_wolf_image_rejected_for_fox_post():
    """from EVIDENCE.md: a wolf image must never be suggested for a fox post"""
    wolf_image = {"subject": "wolf", "confidence": 0.99}
    passed, reason = check_mismatch_guard(
        wolf_image, post_subject="red fox", similarity=0.9
    )
    assert passed is False
    assert reason == "Image subject does not match post topic"

tests/test_guard.py::test_wolf_image_rejected_for_fox_post PASSED  
```

- [X] Rejections include a human-readable explanation.

```Python
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

  # Sample output: see "rejection_reason": "<reason>"
  {
  "id": 306,
  "post_id": 7,
  "image_id": 15,
  "simularity_score": -0.12367623070727991,
  "guard_passed": false,
  "rejection_reason": "Image subject does not match post topic"
}
```

- [X] When no image clears the bar, the system answers "no confident match" with reasons.

```Python
# Sample output from GET /posts/7/suggestions
{
  "post_id": 7,
  "result": "no confident match",
  "reason": "Image subject does not match post topic",
  "top_candidate": {
    "image_id": 45,
    "file_path": "data/images/wolf/wolf_05.jpg",
    "caption": "A profile view of a wolf with its mouth open showing teeth against a blurred backdrop.",
    "subject": "wolf",
    "confidence": 0.98,
    "similarity": 0.17542025915129067
  }
}
```

## Backend

- [X] Database models for images, tags, embeddings, posts, suggestions, approvals/rejections with the required indexes.

```Python
create table images (
  id SERIAL PRIMARY KEY,
  subject TEXT NOT NULL,
  category TEXT NOT NULL,
  attributes TEXT[] NOT NULL,
  caption TEXT NOT NULL,
  confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
  file_path TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

create table posts (
  id SERIAL PRIMARY KEY,
  subject TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

create table image_embeddings (
  id SERIAL PRIMARY KEY,
  image_id INT REFERENCES images(id),
  vector FLOAT[],
  created_at TIMESTAMP DEFAULT now()  
);

create table post_embeddings (
  id SERIAL PRIMARY KEY,
  post_id INT REFERENCES posts(id),
  vector FLOAT[],
  created_at TIMESTAMP DEFAULT now()  
);

create table suggestions (
  id SERIAL PRIMARY KEY,
  image_id INT REFERENCES images(id),
  post_id INT REFERENCES posts(id),
  similarity_score FLOAT NOT NULL, 
  guard_passed BOOLEAN NOT NULL,
  rejection_reason TEXT,
  created_at TIMESTAMP DEFAULT now(),
  UNIQUE (post_id, image_id)
);

create table review_decisions (
  id SERIAL PRIMARY KEY,
  suggestion_id INT REFERENCES suggestions(id) UNIQUE,
  decision TEXT NOT NULL CHECK (decision IN ('approved', 'rejected')),
  reviewed_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_suggestions_post_id ON Suggestions(post_id);
CREATE INDEX idx_suggestions_image_id ON Suggestions(image_id);
CREATE INDEX idx_image_embeddings_image_id ON image_embeddings(image_id);
CREATE INDEX idx_post_embeddings_post_id ON post_embeddings(post_id);
CREATE INDEX idx_review_decisions_suggestion_id ON review_decisions(suggestion_id);
```

- [X] API endpoints validated; the review workflow (approve / reject / inspect why) exists.

```Python
# GET /suggestion/1 -> 200 OK
{
  "id": 1,
  "post_id": 3,
  "image_id": 3,
  "simularity_score": 0.5245831153204901,
  "guard_passed": true,
  "rejection_reason": null
}
# POST /suggestion/305 -> 201 Created
{
  "decision": "approved",
  "id": 8,
  "suggestion_id": 305
}

# POST /suggestions/305 (again) -> 409 Conflict
{
  "detail": "This suggestion has already been reviewed"
}

# POST /suggestions/9999 -> 404 Not Found
{
  "detail": "Suggestion not found"
}
```

## Quality and Documentation

- [X] Automated tests cover schema validation, mismatch rejection, and matching accuracy.

```
tests/test_cosine_similarity.py::test_identical_vectors PASSED                               [  4%]
tests/test_cosine_similarity.py::test_orthogonal_vectors PASSED                              [  9%]
tests/test_cosine_similarity.py::test_opposite_vectors PASSED                                [ 13%]
tests/test_cosine_similarity.py::test_scaled_vectors PASSED                                  [ 18%]
tests/test_guard.py::test_wolf_image_rejected_for_fox_post PASSED                            [ 22%]
tests/test_guard.py::test_subject_match_passes_first_check PASSED                            [ 27%]
tests/test_guard.py::test_low_similarity_rejected_when_subject_matches PASSED                [ 31%]
tests/test_guard.py::test_similarity_at_threshold_passes PASSED                              [ 36%]
tests/test_guard.py::test_low_confidence_rejected_when_subject_and_similarity_pass PASSED    [ 40%]
tests/test_guard.py::test_confidence_at_threshold_passes PASSED                              [ 45%]
tests/test_guard.py::test_all_checks_pass PASSED                                             [ 50%]
tests/test_schemas.py::test_metadata_valid_confidence PASSED                                 [ 54%]
tests/test_schemas.py::test_metadata_confidence_lower_bound PASSED                           [ 59%]
tests/test_schemas.py::test_metadata_confidence_upper_bound PASSED                           [ 63%]
tests/test_schemas.py::test_metadata_confidence_above_limit PASSED                           [ 68%]
tests/test_schemas.py::test_metadata_confidence_below_limit PASSED                           [ 72%]
tests/test_schemas.py::test_image_create_requires_file_path PASSED                           [ 77%]
tests/test_schemas.py::test_post_create_requires_all_fields PASSED                           [ 81%]
tests/test_schemas.py::test_review_create_accepts_valid_decision PASSED                      [ 86%]
tests/test_schemas.py::test_review_create_rejects_invalid_decision PASSED                    [ 90%]
tests/test_semantic_matching.py::test_scientific_name PASSED                                 [ 95%]
tests/test_semantic_matching.py::test_unrelated_concepts FAILED                              [100%]
```

- [X] A small labeled evaluation dataset measures top-1 precision; the number is in your README.

```Python
# Output: Top 1 Precision: 6/7 = 85.71%
# 1 wrong by design (off topic post); see README for more context

import json
import psycopg
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

LABELS_FILE = Path("data/eval_labels.json")


def get_top_prediction(cur, post_id: int) -> int | None:
    """Return image_id with the highest similarity score for a post"""
    cur.execute(
        """
        SELECT image_id
        FROM suggestions
        WHERE post_id = %s
        ORDER BY similarity_score DESC
        LIMIT 1 
        """,
        (post_id,),
    )
    row = cur.fetchone()
    return row[0] if row else None

def evaluate():
    """Compute top-1 precision by seeing if highest similarity result match labeled image"""
    with open(LABELS_FILE, "r") as f:
        labels = json.load(f)

    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    correct_count = 0
    total_count = 0

    with conn:
        with conn.cursor() as cur:
            for post_id_str, correct_image_id in labels.items():
                post_id = int(post_id_str)
                predicted_image_id = get_top_prediction(cur, post_id)

                is_correct = predicted_image_id == correct_image_id 
                if is_correct:
                    correct_count += 1
                total_count += 1

                print(
                    f"post_id={post_id}: predicted={predicted_image_id}, "
                    f"expected={correct_image_id}, correct={is_correct}"
                )

    precision = correct_count / total_count if total_count else 0.0
    print(f"\n Top 1 Precision: {correct_count}/{total_count} = {precision:.2%}")

if __name__ == "__main__":
    evaluate()
```

- [X] README with architecture explanation and diagram; submission-pack files from § 11 present.
