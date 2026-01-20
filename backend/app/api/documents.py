"""
Document management API endpoints.
Handles listing, retrieving, and deleting documents.
"""

from fastapi import APIRouter, HTTPException

from app.rag import get_vector_store
from app.schemas import (
    DocumentDeleteResponse,
    DocumentListResponse,
    DocumentMetadata,
)
from app.utils import logger

router = APIRouter(prefix="/api", tags=["documents"])


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents() -> DocumentListResponse:
    """
    List all ingested documents with their metadata.
    """
    vector_store = get_vector_store()
    documents = vector_store.get_all_documents()
    
    logger.info(f"Listed {len(documents)} documents")
    
    return DocumentListResponse(
        documents=documents,
        total_count=len(documents)
    )


@router.get("/documents/{document_id}", response_model=DocumentMetadata)
async def get_document(document_id: str) -> DocumentMetadata:
    """
    Get metadata for a specific document.
    """
    vector_store = get_vector_store()
    document = vector_store.get_document(document_id)
    
    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"Document not found: {document_id}"
        )
    
    return document


@router.delete("/documents/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: str) -> DocumentDeleteResponse:
    """
    Delete a document and its chunks from the vector store.
    """
    vector_store = get_vector_store()
    
    # Check if document exists
    document = vector_store.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=404,
            detail=f"Document not found: {document_id}"
        )
    
    # Delete document
    success = vector_store.delete_document(document_id)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {document_id}"
        )
    
    logger.info(f"Deleted document: {document_id}")
    
    return DocumentDeleteResponse(
        document_id=document_id,
        message=f"Document '{document.filename}' deleted successfully"
    )


@router.delete("/documents", response_model=dict)
async def delete_all_documents() -> dict:
    """
    Delete all documents from the vector store.
    Use with caution!
    """
    vector_store = get_vector_store()
    documents = vector_store.get_all_documents()
    count = len(documents)
    
    vector_store.clear()
    
    logger.info(f"Deleted all {count} documents")
    
    return {
        "message": f"Deleted {count} documents",
        "deleted_count": count
    }
