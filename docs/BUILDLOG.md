# Build Log

A log of where AI helped throughtout the project

## Pexels Scraper Script

**Where AI Helped:** General outline of code, and final revisions.

**Where it was Wrong:** In revising my code, I was told to write

```Python
with open(save_path, 'w') as f: # Error in this line (line 34 in script)
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
```

**What I Changed:**

This piece became:

```Python
with open(save_path, 'wb') as f: # Changed to 'wb' because we are writing a .jpg file
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
```

## Gemini Vision Tagging

**Where AI Helped:** Inital structure for calling Gemini with image input and Pydantic structured output.

**Where it was Wrong:** The original version encoded the image mime type, causing errors with pngs

```Python
types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
```

**What I Changed:** Now the mime type is detected from original file

```Python
mime_type, _ = mimetypes.guess_type(image_path)...
types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
```

## Batch Tagging via API

**Where AI Helped:** Design pregenerated metadata after hitting limitations with Gemini Free Tier.

**Where it Was Wrong:** Said that we ran into errors because of surpassing the 15 requests per minute allowed by Gemini 3.5-flash-lite.

**What I Changed:** Generated 50 images' metadata manually via Gemini Chat, storing that metadata in `app/metadata.json`

## Gemini Embeddings


```json
{
  "post_id": 8,
  "result": "no confident match",
  "reason": "Image content isn't similar enough to the post",
  "top_candidate": {
    "image_id": 34,
    "file_path": "data/images/red_fox/red_fox_04.jpg",
    "caption": "A close-up portrait of a red fox looking directly at the camera.",
    "subject": "red fox",
    "confidence": 0.99,
    "similarity": 0.47109292584964546
  }
```

## Local Embedding

**Where AI Helped:** Diagnosed a `PermissionError` when `sentence-transformers` tried to download it's model file inside the Docker container

**Where it was Wrong:** The Dockerfile's non-root `appuser` is created with `--home "/nonexistent"` as a security hardening measure. `sentence-transformers` defaults to caching its downloaded model under the user's home directory (`~/.cache/huggingface`), which resolved to `/nonexistent/.cache/` which does not exist.

**What I changed:** Add a cache directory before switching to the non-root user:

```Dockerfile
ENV HF_HOME=/app/.cache/huggingface
RUN mkdir -p /app/.cache/huggingface && chown -R appuser:appuser /app/.cache
```

Also added a HF_TOKEN in `.env` to speed up model download speed

## Similarity Ranking & Mismatch Guard

**Where AI Helped:** Structured the `/posts/{post_id}/suggestions` endpoint by joining post/image embeddings via SQL and applying mismatch guard

**Where it was Wrong:** Multiple syntax errors in code, for example: capturing `reason` inside ranking loop but never used it:

```Python
for candidate in scored:
	passed, reason = check_mismatch_guard(
    	candidate, post_subject, candidate["similarity"]
    )
    if passed:
    	return {"post_id": post_id, "result": "match", "suggestion": candidate}
```

**What I changed:** Fix syntax errors; for this particular case, replace `reason` with `_` for readability

## Images/Posts Endpoints

**Where AI Helped:** Structured POST/GET endpoints for `/images` and `/posts`

**Where it Was Wrong:** Multiple syntax errors, for example: 

```PostgreSQL
INSERT INTO images (subject, category, attributes, caption, confidence, file_path)
VALUES (%s)
```

**What I Changed:** Fix syntax error, for this example: 

```PostgreSQL
INSERT INTO images (subject, category, attributes, caption, confidence, file_path)
VALUES (%s, %s, %s, %s, %s, %s)
RETURNING id
```
