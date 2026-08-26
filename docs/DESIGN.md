# Design Document

## Image Metadata Schema

```Python
from pydantic import BaseModel, Field

class Metadata(BaseModel):
    subject: str									# main entity in the image
    category: str									# broad grouping/type of subject
    attributes: list[str]							# descriptive traits or details
    caption: str									# readable image description
    confidence: float = Field(ge=0.0, le=1.0)		# model certainty's score from 0-1
```

## Matching Strategy

For each post, compute the cosine similarity between the post's embedding and every image's caption embedding. Cosine similarity measures how closely two embeddings point in the same direction, which captures semantic closeness regardless of exact wording.

**Example:** *Red Fox* and *Vulpes vulpes* associated together despite having different words.

```LaTeX
cosine_similarity = (A · B) / (|A| × |B|)
```

Rank images by similarity score, display top 5 highest images per blog.

## Mismatch Guard

Before a ranked image is suggested, it must pass **three** checks, in order. The first check it fails determines the rejection reason. Checks after  that point are never evaluated.

| # | Check                | Rejects When                      | Reason Shown                                            |
| - | -------------------- | --------------------------------- | ------------------------------------------------------- |
| 1 | Subject Match        | `image.subject != post.subject` | "Image subject does not match post topic"               |
| 2 | Similarity Threshold | `similarity < sim_threshold`    | "Image content isn't similar enough to the post"        |
| 3 | Confidence Threshold | `confidence < con_threshold`    | "Vision model wasn't confident enough about this image" |

An image that passes is accepted and returned as the suggestion. If no image passes, the post gets `no confident match` with the reason from the top-ranked candidate's failed check.

## Database Design

```SQL
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
  suggestion_id INT REFERENCES suggestions(id),
  decision TEXT NOT NULL CHECK (decision IN ('approved', 'rejected')),
  reviewed_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_suggestions_post_id ON Suggestions(post_id);
CREATE INDEX idx_suggestions_image_id ON Suggestions(image_id);
CREATE INDEX idx_image_embeddings_image_id ON image_embeddings(image_id);
CREATE INDEX idx_post_embeddings_post_id ON post_embeddings(post_id);
CREATE INDEX idx_review_decisions_suggestion_id ON review_decisions(suggestion_id);
```

## Dataset

50 images across 5 animal categories, gathered from Pexels via a script `fetch_dataset.py` to create a fully reproducible project.

**Categories:** Moose, Bear, Red Fox, Wolf, Dog (10 images of each)

**Source:** Pexels API (free tier, and licensed for reuse); see [Pexels License](https://www.pexels.com/license/)

**Reproduction:** run `scripts/fetch_dataset.py` with a valid`PEXELS_API_KEY` in `.env`. Images are saved to `data/images/<category>/`
