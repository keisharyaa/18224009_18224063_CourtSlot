from contextlib import asynccontextmanager
import sqlite3

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from .public import PartnerError, error_response, router as public_router
from .internal import router as internal_router

from .db import connection, initialize


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize()
    yield


app = FastAPI(title="CourtSlot Core API", version="0.1.0", lifespan=lifespan)
app.include_router(public_router)
app.include_router(internal_router)


@app.exception_handler(sqlite3.Error)
def database_error_handler(request: Request, exc: sqlite3.Error):
    if request.url.path.startswith("/api/public/"):
        return error_response(PartnerError(503, "SOURCE_UNAVAILABLE", "Sumber data sementara tidak tersedia."))
    raise exc


@app.exception_handler(PartnerError)
def partner_error_handler(request: Request, exc: PartnerError):
    return error_response(exc)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api/public/"):
        return error_response(PartnerError(400, "INVALID_REQUEST", "Parameter permintaan tidak valid."))
    from fastapi.exception_handlers import request_validation_exception_handler
    return await request_validation_exception_handler(request, exc)


@app.get("/api/health", tags=["system"])
def health():
    with connection() as db:
        db.execute("SELECT 1").fetchone()
    return {"status": "ok"}
