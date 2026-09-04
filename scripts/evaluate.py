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