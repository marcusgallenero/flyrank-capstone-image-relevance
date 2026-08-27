import os
from psycopg_pool import AsyncConnectionPool

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("DATABASE_URL not set in .env")

pool = AsyncConnectionPool(conninfo=DB_URL, open=False)


async def get_connection():
    """Connect to the database and yield a connection from the pool"""
    async with pool.connection() as conn:
        yield conn
