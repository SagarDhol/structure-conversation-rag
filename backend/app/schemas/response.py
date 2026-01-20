"""
Response schemas for the RAG API.
Defines Pydantic models for all outgoing response payloads.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    """Reference to source document and chunk."""
    
    document: str = Field(
        ...,
        description="Source document filename or ID"
    )
    chunk_id: str = Field(
        ...,
        description="Chunk identifier within document"
    )
    content_preview: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Preview of chunk content"
    )


class ChatResponse(BaseModel):
    """Structured response from chat endpoint (non-streaming)."""
    
    answer: str = Field(
        ...,
        description="Generated answer text"
    )
    sources: List[SourceReference] = Field(
        default_factory=list,
        description="Source references for the answer"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0 to 1.0)"
    )

    @classmethod
    def no_knowledge_response(cls) -> "ChatResponse":
        """Create standard response when no relevant knowledge is found."""
        return cls(
            answer="I do not have knowledge of this based on the uploaded documents.",
            sources=[],
            confidence=0.0
        )


class StreamChunk(BaseModel):
    """Single chunk in streaming response."""
    
    type: str = Field(
        ...,
        description="Chunk type: 'token', 'sources', 'done', 'error'"
    )
    content: Optional[str] = Field(
        default=None,
        description="Token content for type='token'"
    )
    sources: Optional[List[SourceReference]] = Field(
        default=None,
        description="Source references for type='sources'"
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score for type='done'"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message for type='error'"
    )


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(default="healthy")
    version: str = Field(default="1.0.0")
    vector_store_ready: bool = Field(default=False)


class SessionResponse(BaseModel):
    """Response for session operations."""
    
    session_id: str
    message: str
    success: bool = True


class ModelInfoResponse(BaseModel):
    """Response with current model information."""
    
    provider: str
    model: str
    available_providers: List[str] = ["openai", "ollama"]
    available_models: dict = Field(default_factory=lambda: {
        "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        "ollama": ["llama3", "llama3.1", "mistral", "mixtral"]
    })
