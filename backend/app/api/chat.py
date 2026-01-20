"""
Chat API endpoint with streaming SSE responses.
Handles RAG-based conversational queries.
"""

import json
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.llm import get_llm_provider
from app.memory import get_memory_manager
from app.rag import get_retriever
from app.schemas import ChatRequest, ChatResponse, SourceReference, StreamChunk
from app.utils import logger

router = APIRouter(prefix="/api", tags=["chat"])


async def generate_sse_response(
    request: ChatRequest
) -> AsyncGenerator[str, None]:
    """
    Generate Server-Sent Events for streaming chat response.
    
    Args:
        request: Chat request with message and session_id
        
    Yields:
        SSE formatted strings
    """
    settings = get_settings()
    memory_manager = get_memory_manager()
    retriever = get_retriever()
    
    try:
        # Get conversation context
        conversation_context = memory_manager.get_recent_context(request.session_id)
        conversation_history = memory_manager.get_history(request.session_id)
        
        # Retrieve relevant documents with context enhancement
        retrieval_result = retriever.retrieve_with_history(
            query=request.message,
            conversation_context=conversation_context
        )
        
        # Check if we have relevant content
        if not retrieval_result.has_relevant_content:
            # No relevant documents - send the standard no-knowledge response
            no_knowledge = "I do not have knowledge of this based on the uploaded documents."
            
            # Stream the no-knowledge message
            for word in no_knowledge.split():
                chunk = StreamChunk(type="token", content=word + " ")
                yield f"data: {chunk.model_dump_json()}\n\n"
            
            # Send empty sources
            sources_chunk = StreamChunk(type="sources", sources=[])
            yield f"data: {sources_chunk.model_dump_json()}\n\n"
            
            # Send done with zero confidence
            done_chunk = StreamChunk(type="done", confidence=0.0)
            yield f"data: {done_chunk.model_dump_json()}\n\n"
            
            # Add to memory (even no-knowledge responses)
            memory_manager.add_turn(
                request.session_id,
                request.message,
                no_knowledge
            )
            
            return
        
        # Get LLM provider
        provider = request.provider or settings.default_llm_provider
        model = request.model
        llm = get_llm_provider(provider=provider, model=model)
        
        # Generate streaming response
        full_response = ""
        
        async for token in llm.generate_stream(
            query=request.message,
            context=retrieval_result.context,
            conversation_history=conversation_history
        ):
            full_response += token
            chunk = StreamChunk(type="token", content=token)
            yield f"data: {chunk.model_dump_json()}\n\n"
        
        # Send sources
        sources_chunk = StreamChunk(
            type="sources",
            sources=retrieval_result.sources
        )
        yield f"data: {sources_chunk.model_dump_json()}\n\n"
        
        # Send done with confidence
        done_chunk = StreamChunk(
            type="done",
            confidence=retrieval_result.top_score
        )
        yield f"data: {done_chunk.model_dump_json()}\n\n"
        
        # Add turn to memory
        memory_manager.add_turn(
            request.session_id,
            request.message,
            full_response
        )
        
        logger.info(f"Completed streaming response for session {request.session_id}")
        
    except Exception as e:
        logger.error(f"Error in chat stream: {e}")
        error_chunk = StreamChunk(type="error", error=str(e))
        yield f"data: {error_chunk.model_dump_json()}\n\n"


@router.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    """
    Chat endpoint with streaming SSE response.
    
    Retrieves relevant documents, generates response using LLM,
    and streams tokens back to the client.
    """
    logger.info(f"Chat request from session {request.session_id}: {request.message[:50]}...")
    
    return StreamingResponse(
        generate_sse_response(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/chat/sync", response_model=ChatResponse)
async def chat_sync(request: ChatRequest) -> ChatResponse:
    """
    Non-streaming chat endpoint for testing/simple clients.
    """
    settings = get_settings()
    memory_manager = get_memory_manager()
    retriever = get_retriever()
    
    # Get conversation context
    conversation_context = memory_manager.get_recent_context(request.session_id)
    conversation_history = memory_manager.get_history(request.session_id)
    
    # Retrieve relevant documents
    retrieval_result = retriever.retrieve_with_history(
        query=request.message,
        conversation_context=conversation_context
    )
    
    # Check if we have relevant content
    if not retrieval_result.has_relevant_content:
        return ChatResponse.no_knowledge_response()
    
    # Get LLM provider
    provider = request.provider or settings.default_llm_provider
    model = request.model
    llm = get_llm_provider(provider=provider, model=model)
    
    # Generate response
    response = await llm.generate(
        query=request.message,
        context=retrieval_result.context,
        conversation_history=conversation_history
    )
    
    # Add turn to memory
    memory_manager.add_turn(
        request.session_id,
        request.message,
        response
    )
    
    return ChatResponse(
        answer=response,
        sources=retrieval_result.sources,
        confidence=retrieval_result.top_score
    )
