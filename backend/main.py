
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.logging import setup_logging
from backend.database.connection import (
    init_db,
    check_database_connection
)

from backend.api import (
    auth,
    queries,
    cases,
    workflows,
    reviews,
    documents,
    reports
)

setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting Clinical Evidence AI.")

    init_db()

    if not check_database_connection():
        raise RuntimeError(
            "Database connection failed."
        )

    logger.info("Database initialized.")

    yield

    logger.info("Clinical Evidence AI shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Multi-agent clinical evidence research "
        "and decision-support application."
    ),
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


app.include_router(auth.router)
app.include_router(queries.router)
app.include_router(cases.router)
app.include_router(workflows.router)
app.include_router(reviews.router)
app.include_router(documents.router)
app.include_router(reports.router)


@app.get("/", tags=["System"])
def root():

    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "documentation": "/docs",
        "disclaimer": (
            "Clinical research assistance only. "
            "Not a replacement for professional clinical judgment."
        )
    }


@app.get("/health", tags=["System"])
def health():

    database_ok = check_database_connection()

    return {
        "status": "healthy" if database_ok else "degraded",
        "database": (
            "connected" if database_ok else "disconnected"
        ),
        "model": {
            "provider": "gemini",
            "configured": bool(settings.GEMINI_API_KEY)
        }
    }
