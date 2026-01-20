"""
Document schemas for the RAG API.
Defines Pydantic models for document and chunk metadata.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    """Metadata for a document chunk."""
    
    chunk_id: str = Field(
        ...,
        description="Unique chunk identifier"
    )
    document_id: str = Field(
        ...,
        description="Parent document identifier"
    )
    chunk_index: int = Field(
        ...,
        ge=0,
        description="Index of chunk within document"
    )
    start_char: Optional[int] = Field(
        default=None,
        description="Start character position in original document"
    )
    end_char: Optional[int] = Field(
        default=None,
        description="End character position in original document"
    )
    content: str = Field(
        ...,
        description="Chunk text content"
    )


class DocumentMetadata(BaseModel):
    """Metadata for an ingested document."""
    
    document_id: str = Field(
        ...,
        description="Unique document identifier"
    )
    filename: str = Field(
        ...,
        description="Original filename"
    )
    file_type: str = Field(
        ...,
        description="File type (pdf, txt, docx)"
    )
    file_size: int = Field(
        ...,
        ge=0,
        description="File size in bytes"
    )
    chunk_count: int = Field(
        ...,
        ge=0,
        description="Number of chunks created"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Ingestion timestamp"
    )
    content_hash: Optional[str] = Field(
        default=None,
        description="SHA-256 hash of file content"
    )
    status: str = Field(
        default="indexed",
        description="Document status (indexed, pending, error)"
    )


class DocumentListResponse(BaseModel):
    """Response for listing documents."""
    
    documents: List[DocumentMetadata] = Field(
        default_factory=list,
        description="List of document metadata"
    )
    total_count: int = Field(
        default=0,
        description="Total number of documents"
    )


class DocumentUploadResponse(BaseModel):
    """Response after document upload."""
    
    document_id: str = Field(
        ...,
        description="Assigned document ID"
    )
    filename: str = Field(
        ...,
        description="Original filename"
    )
    chunk_count: int = Field(
        ...,
        description="Number of chunks created"
    )
    message: str = Field(
        default="Document uploaded and indexed successfully"
    )
    success: bool = True


class DocumentDeleteResponse(BaseModel):
    """Response after document deletion."""
    
    document_id: str = Field(
        ...,
        description="Deleted document ID"
    )
    message: str = Field(
        default="Document deleted successfully"
    )
    success: bool = True
