# Image Relevance

AI Image Understanding & Content Matching Engine. Tags images with a vision model, matches them to blog posts by meaning, and rejects bad matches with an explanation

## Architecture

`TODO: Architecture Diagram`

## Setup

`TODO: Run steps `

## Evaluation

**Top-1 Prediction: 6/7 (85.71%):** Measured against a manually labeled evaluation set `data/eval_labels.json`, which was computed via `scripts/evaluate.py`. For each post, the script checks whether the single highest similarity image matches a manually confirmed "correct" image_id for that post.

The one miss is the deliberately off-topic post included to test the mismatch guard. Therefore, since it has no genuinely correct image, its top ranked prediction is always counted as incorrect by design. Excluding that case, precision on subject-matched posts is 6/6 or 100%.

To run it yourself, run this (bash):

```
docker compose exec server python -m scripts.evaluate
```

## Testing

Automated tests to cover schema validation, mismatch guard rejection, and cosine similarity logic.

To run it yourself, run this (bash):

```
docker compose exec server python -m pytest tests/ -v
```

## Limitations

**Gemini API Free Tier:** The vision pipeline, `app/vision.py` and `app/batch.py` is fully implemented with retries and rate-limit pacing to stay under the 15RPM range for 3.5 Flash-Lite. However, the Gemini API Free Tier is simply not sufficient to run the vision model on each of the 50 images in the dataset, and funding will be required to run. A cost tracking infrastructure has been implemented in `app/vision.py`, however it has not been verified against a Gemini API call. The same problem is present with Gemini embedding.

My workaround was to pre-generate Metadata via Gemini Chat, and thus pasting in the given data into `data/metadata.json`, and will later be called. I also used a local embedder: `sentence-transformers` to embed images while keeping everything free.

**Local Embeddings Model:** The local embedding model `all-MiniLM-L6-v6` does not support semantic matching. This was proven by `tests/test_semantic_matching`, where *"Red Fox"* and *"Goldfish"* matched closer than *"Red Fox"* and *"Vulpes vulpes."* However, proper semanic matching would be most likely be possible with Gemini's `gemini-embedding-002` model.
