"""Schemas package initialization."""

from app.schemas.document import (
    ChunkMetadata,
    DocumentDeleteResponse,
    DocumentListResponse,
    DocumentMetadata,
    DocumentUploadResponse,
)
from app.schemas.request import (
    ChatRequest,
    ClearSessionRequest,
    ModelSwitchRequest,
)
from app.schemas.response import (
    ChatResponse,
    HealthResponse,
    ModelInfoResponse,
    SessionResponse,
    SourceReference,
    StreamChunk,
)

__all__ = [
    # Request schemas
    "ChatRequest",
    "ClearSessionRequest",
    "ModelSwitchRequest",
    # Response schemas
    "ChatResponse",
    "HealthResponse",
    "ModelInfoResponse",
    "SessionResponse",
    "SourceReference",
    "StreamChunk",
    # Document schemas
    "ChunkMetadata",
    "DocumentDeleteResponse",
    "DocumentListResponse",
    "DocumentMetadata",
    "DocumentUploadResponse",
]
