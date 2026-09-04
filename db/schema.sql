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