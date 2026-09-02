import json
import psycopg
import os
from pathlib import Path
from dotenv import load_dotenv
from app.embeddings_local import embed_text

load_dotenv()

POSTS_FILE = Path("data/posts.json")


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

if __name__ == "__main__":
    seed_posts()