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

**What I Changed:** Generated 50 images' metadata manually via Gemini Chat, storing that metadata in `app/metadata.json`,
