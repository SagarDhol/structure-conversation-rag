"""
FastAPI Application Entry Point.
Main application with routers, CORS, and utility endpoints.
"""

from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat_router, documents_router, ingest_router
from app.config import get_settings
from app.llm import get_llm_provider
from app.memory import get_memory_manager
from app.rag import get_vector_store
from app.schemas import (
    ClearSessionRequest,
    HealthResponse,
    ModelInfoResponse,
    ModelSwitchRequest,
    SessionResponse,
)
from app.utils import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Conversational RAG API...")
    settings = get_settings()
    
    # Initialize vector store
    vector_store = get_vector_store()
    logger.info(f"Vector store ready: {vector_store.is_ready()}")
    
    # Initialize memory manager
    memory_manager = get_memory_manager()
    logger.info("Memory manager initialized")
    
    logger.info(f"Default LLM provider: {settings.default_llm_provider}")
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Conversational RAG API...")


# Create FastAPI app
app = FastAPI(
    title="Conversational RAG API",
    description="Production-ready Retrieval Augmented Generation API with streaming support",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(ingest_router)
app.include_router(documents_router)


@app.get("/health", response_model=HealthResponse, tags=["utility"])
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    vector_store = get_vector_store()
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        vector_store_ready=vector_store.is_ready()
    )


@app.get("/", tags=["utility"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Conversational RAG API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.post("/api/session/clear", response_model=SessionResponse, tags=["session"])
async def clear_session(request: ClearSessionRequest) -> SessionResponse:
    """Clear conversation memory for a specific session."""
    memory_manager = get_memory_manager()
    existed = memory_manager.clear_session(request.session_id)
    
    if existed:
        return SessionResponse(
            session_id=request.session_id,
            message="Session memory cleared successfully"
        )
    else:
        return SessionResponse(
            session_id=request.session_id,
            message="Session did not exist (nothing to clear)",
            success=True
        )


@app.delete("/api/sessions", tags=["session"])
async def clear_all_sessions() -> dict:
    """Clear all session memories."""
    memory_manager = get_memory_manager()
    count = memory_manager.clear_all()
    return {
        "message": f"Cleared {count} sessions",
        "cleared_count": count
    }


@app.get("/api/sessions", tags=["session"])
async def list_sessions() -> dict:
    """List all active session IDs."""
    memory_manager = get_memory_manager()
    sessions = memory_manager.list_sessions()
    return {
        "sessions": sessions,
        "count": len(sessions)
    }


@app.get("/api/model", response_model=ModelInfoResponse, tags=["model"])
async def get_model_info() -> ModelInfoResponse:
    """Get current model configuration and available options."""
    settings = get_settings()
    return ModelInfoResponse(
        provider=settings.default_llm_provider,
        model=(
            settings.default_openai_model 
            if settings.default_llm_provider == "openai" 
            else settings.default_ollama_model
        )
    )


@app.post("/api/model/validate", tags=["model"])
async def validate_model(request: ModelSwitchRequest) -> dict:
    """
    Validate that a provider/model combination is available.
    Note: Actual model switching is done per-request via the chat endpoint.
    """
    try:
        # Try to initialize the provider
        llm = get_llm_provider(provider=request.provider, model=request.model)
        return {
            "valid": True,
            "provider": request.provider,
            "model": request.model,
            "message": "Provider and model are valid"
        }
    except Exception as e:
        return {
            "valid": False,
            "provider": request.provider,
            "model": request.model,
            "message": str(e)
        }


# App init for package
__all__ = ["app"]
