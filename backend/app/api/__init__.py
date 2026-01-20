"""API package initialization."""

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.ingest import router as ingest_router

__all__ = [
    "chat_router",
    "documents_router",
    "ingest_router",
]
