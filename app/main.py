from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from psycopg import AsyncConnection
from app.db import pool, get_connection
from app.cosine_similarity import cosine_similarity
from app.guard import check_mismatch_guard
from app.schemas import ImageCreate, ImageOut, PostCreate, PostOut
from app.embeddings_local import embed_text


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


@app.post("/images", response_model=ImageOut, status_code=201)
async def create_image(
    image: ImageCreate, conn: AsyncConnection = Depends(get_connection)
):
    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO images (subject, category, attributes, caption, confidence, file_path)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                image.subject,
                image.category,
                image.attributes,
                image.caption,
                image.confidence,
                image.file_path,
            ),
        )
        image_id = (await cur.fetchone())[0]

        vector = embed_text(image.caption)
        await cur.execute(
            "INSERT INTO image_embeddings (image_id, vector) VALUES (%s, %s)",
            (image_id, vector),
        )
    return ImageOut(id=image_id, **image.model_dump())


@app.get("/images", response_model=list[ImageOut])
async def list_images(
    limit: int = 50,
    offset: int = 0,
    conn: AsyncConnection = Depends(get_connection),
):
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT id, subject, category, attributes, caption, confidence, file_path
            FROM images
            ORDER BY id
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )
        rows = await cur.fetchall()
        return [
            ImageOut(
                id=r[0],
                subject=r[1],
                category=r[2],
                attributes=r[3],
                caption=r[4],
                confidence=r[5],
                file_path=r[6],
            )
            for r in rows
        ]


@app.post("/posts", response_model=PostOut, status_code=201)
async def create_post(
    post: PostCreate, conn: AsyncConnection = Depends(get_connection)
):
    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO posts (subject, title, body) 
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (post.subject, post.title, post.body),
        )
        post_id = (await cur.fetchone())[0]

        vector = embed_text(post.body)
        await cur.execute(
            "INSERT INTO post_embeddings (post_id, vector) VALUES (%s, %s)",
            (post_id, vector),
        )
    return PostOut(id=post_id, **post.model_dump())


@app.get("/posts", response_model=list[PostOut])
async def list_posts(
    limit: int = 50, offset: int = 0, conn: AsyncConnection = Depends(get_connection)
):
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT id, subject, title, body 
            FROM posts ORDER BY id
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )
        rows = await cur.fetchall()

    return [
        PostOut(
            id=r[0],
            subject=r[1],
            title=r[2],
            body=r[3],
        )
        for r in rows
    ]


@app.get("/posts/{post_id}/suggestions")
async def get_suggestions(
    post_id: int, conn: AsyncConnection = Depends(get_connection)
):
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT vector, subject 
            FROM post_embeddings pe 
            JOIN posts p ON p.id = pe.post_id WHERE pe.post_id = %s
            """,
            (post_id,),
        )
        row = await cur.fetchone()
        if row is None:
            raise HTTPException(
                status_code=404, detail="Post not found or not embedded"
            )
        post_vector, post_subject = row

        await cur.execute("""
            SELECT i.id, i.file_path, i.caption, i.subject, i.confidence, ie.vector
            FROM image_embeddings ie
            JOIN images i ON i.id = ie.image_id
            """)
        rows = await cur.fetchall()

    scored = [
        {
            "image_id": r[0],
            "file_path": r[1],
            "caption": r[2],
            "subject": r[3],
            "confidence": r[4],
            "similarity": cosine_similarity(post_vector, r[5]),
        }
        for r in rows
    ]
    scored.sort(key=lambda x: x["similarity"], reverse=True)

    # Walk ranked candidates until one clears guard
    for candidate in scored:
        passed, _ = check_mismatch_guard(
            candidate, post_subject, candidate["similarity"]
        )
        if passed:
            return {"post_id": post_id, "result": "match", "suggestion": candidate}

    # Nothing passed, report via top ranked candidates failure reason
    top = scored[0]
    _, top_reason = check_mismatch_guard(top, post_subject, top["similarity"])
    return {
        "post_id": post_id,
        "result": "no confident match",
        "reason": top_reason,
        "top_candidate": top,
    }
