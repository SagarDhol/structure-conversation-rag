"""
FAISS Vector Store with persistence and metadata support.
Provides document storage and retrieval functionality.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional, Tuple

from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.config import get_settings
from app.rag.embeddings import get_embedding_service
from app.schemas.document import DocumentMetadata
from app.utils import ensure_directory, logger


class VectorStoreService:
    """Service for managing FAISS vector store with persistence."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        """Singleton pattern for vector store."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize vector store if not already done."""
        if not self._initialized:
            self._initialize()
    
    def _initialize(self) -> None:
        """Initialize the vector store."""
        settings = get_settings()
        self._store_path = Path(settings.vector_store_path)
        self._metadata_path = self._store_path / "metadata.json"
        self._embedding_service = get_embedding_service()
        self._vector_store: Optional[FAISS] = None
        self._document_metadata: Dict[str, DocumentMetadata] = {}
        
        ensure_directory(str(self._store_path))
        self._load_store()
        self._initialized = True
    
    def _load_store(self) -> None:
        """Load existing vector store from disk."""
        index_path = self._store_path / "index.faiss"
        
        if index_path.exists():
            try:
                logger.info(f"Loading vector store from {self._store_path}")
                self._vector_store = FAISS.load_local(
                    str(self._store_path),
                    self._embedding_service.embeddings,
                    allow_dangerous_deserialization=True
                )
                self._load_metadata()
                logger.info(f"Vector store loaded with {len(self._document_metadata)} documents")
            except Exception as e:
                logger.error(f"Failed to load vector store: {e}")
                self._create_new_store()
        else:
            logger.info("No existing vector store found, creating new one")
            self._create_new_store()
    
    def _create_new_store(self) -> None:
        """Create a new empty vector store."""
        # FAISS requires at least one document to initialize
        # We'll create it on first document add
        self._vector_store = None
        self._document_metadata = {}
    
    def _load_metadata(self) -> None:
        """Load document metadata from disk."""
        if self._metadata_path.exists():
            try:
                with open(self._metadata_path, "r") as f:
                    data = json.load(f)
                    self._document_metadata = {
                        doc_id: DocumentMetadata(**meta)
                        for doc_id, meta in data.items()
                    }
            except Exception as e:
                logger.error(f"Failed to load metadata: {e}")
                self._document_metadata = {}
    
    def _save_metadata(self) -> None:
        """Save document metadata to disk."""
        try:
            with open(self._metadata_path, "w") as f:
                data = {
                    doc_id: meta.model_dump(mode="json")
                    for doc_id, meta in self._document_metadata.items()
                }
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def _save_store(self) -> None:
        """Persist vector store to disk."""
        if self._vector_store is not None:
            try:
                self._vector_store.save_local(str(self._store_path))
                self._save_metadata()
                logger.info("Vector store saved to disk")
            except Exception as e:
                logger.error(f"Failed to save vector store: {e}")
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        document_metadata: DocumentMetadata
    ) -> List[str]:
        """
        Add document chunks to the vector store.
        
        Args:
            texts: List of text chunks
            metadatas: List of metadata dicts for each chunk
            document_metadata: Metadata for the parent document
            
        Returns:
            List of chunk IDs
        """
        documents = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(texts, metadatas)
        ]
        
        if self._vector_store is None:
            # Initialize with first batch
            self._vector_store = FAISS.from_documents(
                documents,
                self._embedding_service.embeddings
            )
        else:
            self._vector_store.add_documents(documents)
        
        # Store document metadata
        self._document_metadata[document_metadata.document_id] = document_metadata
        
        # Persist changes
        self._save_store()
        
        chunk_ids = [meta.get("chunk_id", f"chunk_{i}") for i, meta in enumerate(metadatas)]
        logger.info(f"Added {len(texts)} chunks for document {document_metadata.document_id}")
        
        return chunk_ids
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and its chunks from the vector store.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        if document_id not in self._document_metadata:
            logger.warning(f"Document {document_id} not found")
            return False
        
        if self._vector_store is not None:
            # Get all document IDs to delete
            docs_to_delete = []
            docstore = self._vector_store.docstore
            
            for doc_id in list(docstore._dict.keys()):
                doc = docstore._dict.get(doc_id)
                if doc and doc.metadata.get("document_id") == document_id:
                    docs_to_delete.append(doc_id)
            
            if docs_to_delete:
                self._vector_store.delete(docs_to_delete)
        
        # Remove metadata
        del self._document_metadata[document_id]
        
        # Persist changes
        self._save_store()
        
        logger.info(f"Deleted document {document_id}")
        return True
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            k: Number of results to return
            score_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of (Document, score) tuples
        """
        if self._vector_store is None:
            logger.info("Vector store is empty")
            return []
        
        settings = get_settings()
        threshold = score_threshold or settings.retrieval_score_threshold
        
        results = self._vector_store.similarity_search_with_score(query, k=k)
        
        # FAISS returns distance (lower is better), convert to similarity
        # Normalize scores - FAISS distance can vary, we'll use a heuristic
        filtered_results = []
        for doc, distance in results:
            # Convert L2 distance to similarity score (0-1)
            # This is a heuristic that works well for normalized embeddings
            similarity = 1 / (1 + distance)
            
            if similarity >= threshold:
                filtered_results.append((doc, similarity))
        
        logger.info(f"Found {len(filtered_results)} results above threshold {threshold}")
        return filtered_results
    
    def get_all_documents(self) -> List[DocumentMetadata]:
        """Get metadata for all documents."""
        return list(self._document_metadata.values())
    
    def get_document(self, document_id: str) -> Optional[DocumentMetadata]:
        """Get metadata for a specific document."""
        return self._document_metadata.get(document_id)
    
    def is_ready(self) -> bool:
        """Check if vector store is initialized and ready."""
        return self._initialized
    
    def clear(self) -> None:
        """Clear all documents from the vector store."""
        self._vector_store = None
        self._document_metadata = {}
        
        # Remove persisted files
        for file in self._store_path.glob("*"):
            if file.is_file():
                file.unlink()
        
        logger.info("Vector store cleared")


def get_vector_store() -> VectorStoreService:
    """Get the singleton vector store instance."""
    return VectorStoreService()
