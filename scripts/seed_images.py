import json
import psycopg
import os
from pathlib import Path
from dotenv import load_dotenv
from app.embeddings_local import embed_text

load_dotenv()

METADATA_FILE = Path("data/metadata.json")
IMAGES_DIR = Path("data/images")


def seed_images():
    """
    For each entry in metadata.json:
    1. Insert a row into `images`
    2. Embed caption
    3. insert vector into `image_embeddings,` with new image's id
    """

    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)

    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    with conn:
        with conn.cursor() as cur:
            for relative_path, entry in metadata.items():
                file_path = str(IMAGES_DIR / relative_path)


                # Insert new image row, return generated primary key
                cur.execute(
                    """
                    INSERT INTO images (subject, category, attributes, caption, confidence, file_path)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        entry["subject"],
                        entry["category"],
                        entry["attributes"],
                        entry["caption"],
                        entry["confidence"],
                        file_path,
                    ),
                )
                image_id = cur.fetchone()[0]

                # Embed caption and store vector 
                vector = embed_text(entry["caption"])
                cur.execute(
                    "INSERT INTO image_embeddings (image_id, vector) VALUES (%s, %s)",
                    (image_id, vector)
                )
                print(f"Seeded image_id = {image_id}: {relative_path}")

    print("Done.")

if __name__ == "__main__":
    seed_images()