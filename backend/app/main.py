from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import connection, initialize


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize()
    yield


app = FastAPI(title="CourtSlot Core API", version="0.1.0", lifespan=lifespan)


@app.get("/api/health", tags=["system"])
def health():
    with connection() as db:
        db.execute("SELECT 1").fetchone()
    return {"status": "ok"}
