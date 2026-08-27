from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import pool


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
        "version": "1.0"
    }


@app.get("/health")
def get_health():
    return {"status": "ok"}
