"""
Request schemas for the RAG API.
Defines Pydantic models for all incoming request payloads.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's chat message"
    )
    session_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Session ID for conversation tracking"
    )
    provider: Optional[Literal["openai", "ollama"]] = Field(
        default=None,
        description="LLM provider to use (defaults to config)"
    )
    model: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Specific model to use (defaults to config)"
    )
    
    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        """Ensure message is not just whitespace."""
        if not v.strip():
            raise ValueError("Message cannot be empty or whitespace only")
        return v.strip()
    
    @field_validator("session_id")
    @classmethod
    def session_id_valid(cls, v: str) -> str:
        """Ensure session_id is valid."""
        if not v.strip():
            raise ValueError("Session ID cannot be empty")
        return v.strip()


class ClearSessionRequest(BaseModel):
    """Request model for clearing session memory."""
    
    session_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Session ID to clear"
    )


class ModelSwitchRequest(BaseModel):
    """Request model for switching LLM provider/model."""
    
    provider: Literal["openai", "ollama"] = Field(
        ...,
        description="LLM provider"
    )
    model: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Model name"
    )
    
    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str, info) -> str:
        """Validate model matches provider."""
        provider = info.data.get("provider")
        openai_models = ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
        ollama_models = ["llama3", "llama3.1", "mistral", "mixtral", "codellama"]
        
        if provider == "openai" and v not in openai_models:
            # Allow custom OpenAI model names
            pass
        elif provider == "ollama" and v not in ollama_models:
            # Allow custom Ollama model names
            pass
        
        return v
