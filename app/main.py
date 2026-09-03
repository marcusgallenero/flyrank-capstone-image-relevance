from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from psycopg import AsyncConnection
from app.db import pool, get_connection
from app.cosine_similarity import cosine_similarity


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Open the connection pool at startup and close it at shutdown."""
    await pool.open()
    yield
    await pool.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {
        "name": "AI Image Understanding & Content Matching Engine",
        "version": "1.0",
    }


@app.get("/health")
def get_health():
    return {"status": "ok"}


@app.get("/posts/{post_id}/suggestions")
async def get_suggestions(
    post_id: int, conn: AsyncConnection = Depends(get_connection)
):
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT vector FROM post_embeddings WHERE post_id = %s", (post_id,)
        )
        row = await cur.fetchone()
        if row is None:
            raise HTTPException(
                status_code=404, detail="Post not found or not embedded"
            )
        post_vector = row[0]

        await cur.execute("""
            SELECT i.id, i.file_path, i.caption, ie.vector
            FROM image_embeddings ie
            JOIN images i ON i.id = ie.image_id
            """)
        rows = await cur.fetchall()

    scored = [
        {
            "image_id": r[0],
            "file_path": r[1],
            "caption": r[2],
            "similarity": cosine_similarity(post_vector, r[3]),
        }
        for r in rows
    ]
    scored.sort(key=lambda x: x['similarity'], reverse=True)

    return {"post_id": post_id, "suggestions": scored[:5]}