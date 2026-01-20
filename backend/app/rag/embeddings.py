"""
Embedding service using sentence-transformers.
Provides vector embeddings for document chunks.
"""

from typing import List

from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config import get_settings
from app.utils import logger


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers."""
    
    _instance = None
    _embeddings = None
    
    def __new__(cls):
        """Singleton pattern to reuse embedding model."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize embedding model if not already loaded."""
        if self._embeddings is None:
            self._load_model()
    
    def _load_model(self) -> None:
        """Load the embedding model."""
        settings = get_settings()
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        
        self._embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        
        logger.info("Embedding model loaded successfully")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        return self._embeddings.embed_query(text)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        return self._embeddings.embed_documents(texts)
    
    @property
    def embeddings(self) -> HuggingFaceEmbeddings:
        """Get the underlying LangChain embeddings object."""
        return self._embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embedding vectors."""
        # Embed a sample text to get dimension
        sample_embedding = self.embed_text("sample")
        return len(sample_embedding)


def get_embedding_service() -> EmbeddingService:
    """Get the singleton embedding service instance."""
    return EmbeddingService()
