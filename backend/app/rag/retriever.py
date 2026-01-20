"""
Retriever for semantic search with context building.
Handles document retrieval and relevance filtering.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from langchain_core.documents import Document

from app.config import get_settings
from app.rag.vector_store import get_vector_store
from app.schemas.response import SourceReference
from app.utils import logger, truncate_text


@dataclass
class RetrievalResult:
    """Result from retrieval operation."""
    context: str
    sources: List[SourceReference]
    has_relevant_content: bool
    top_score: float


class RetrieverService:
    """Service for retrieving relevant document chunks."""
    
    def __init__(self):
        """Initialize retriever with vector store."""
        self._vector_store = get_vector_store()
        self._settings = get_settings()
    
    def retrieve(
        self,
        query: str,
        k: Optional[int] = None,
        score_threshold: Optional[float] = None
    ) -> RetrievalResult:
        """
        Retrieve relevant document chunks for a query.
        
        Args:
            query: User query text
            k: Number of chunks to retrieve (defaults to config)
            score_threshold: Minimum similarity score (defaults to config)
            
        Returns:
            RetrievalResult with context, sources, and relevance flag
        """
        k = k or self._settings.retrieval_top_k
        score_threshold = score_threshold or self._settings.retrieval_score_threshold
        
        logger.info(f"Retrieving top-{k} chunks for query: {query[:100]}...")
        
        results = self._vector_store.similarity_search(
            query,
            k=k,
            score_threshold=score_threshold
        )
        
        if not results:
            logger.info("No relevant documents found")
            return RetrievalResult(
                context="",
                sources=[],
                has_relevant_content=False,
                top_score=0.0
            )
        
        # Build context and sources
        context_parts = []
        sources = []
        top_score = 0.0
        
        for doc, score in results:
            top_score = max(top_score, score)
            
            # Add to context
            context_parts.append(doc.page_content)
            
            # Create source reference
            source = SourceReference(
                document=doc.metadata.get("filename", "Unknown"),
                chunk_id=doc.metadata.get("chunk_id", "unknown"),
                content_preview=truncate_text(doc.page_content, 150)
            )
            sources.append(source)
        
        context = "\n\n---\n\n".join(context_parts)
        
        logger.info(f"Retrieved {len(results)} chunks, top score: {top_score:.3f}")
        
        return RetrievalResult(
            context=context,
            sources=sources,
            has_relevant_content=True,
            top_score=top_score
        )
    
    def retrieve_with_history(
        self,
        query: str,
        conversation_context: str,
        k: Optional[int] = None
    ) -> RetrievalResult:
        """
        Retrieve documents using query enhanced with conversation context.
        
        Args:
            query: Current user query
            conversation_context: Recent conversation history
            k: Number of chunks to retrieve
            
        Returns:
            RetrievalResult with context, sources, and relevance flag
        """
        # Combine query with conversation context for better retrieval
        enhanced_query = query
        
        if conversation_context:
            # Use conversation context to enhance the query
            # This helps with follow-up questions like "tell me more" or "give me counts"
            enhanced_query = f"Context: {conversation_context}\n\nQuestion: {query}"
        
        return self.retrieve(enhanced_query, k=k)


def get_retriever() -> RetrieverService:
    """Get a new retriever service instance."""
    return RetrieverService()
