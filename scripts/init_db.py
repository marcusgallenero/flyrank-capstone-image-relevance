import os
import psycopg
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SCHEMA_FILE = Path("db/schema.sql")


def init_db():
    """Run schema file against database to create all tables"""
    with open(SCHEMA_FILE, "r") as f:
        schema_sql = f.read()

    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    with conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
    print("Schema created successfully")

if __name__ == "__main__":
    init_db()