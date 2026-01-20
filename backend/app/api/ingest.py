"""
Document ingestion API endpoint.
Handles file uploads, text extraction, chunking, and vector storage.
"""

import io
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings
from app.rag import get_vector_store
from app.schemas import DocumentMetadata, DocumentUploadResponse
from app.utils import (
    compute_file_hash,
    ensure_directory,
    generate_chunk_id,
    generate_document_id,
    get_file_extension,
    logger,
    sanitize_filename,
)

router = APIRouter(prefix="/api", tags=["ingest"])


def extract_text_from_txt(content: bytes) -> str:
    """Extract text from TXT file."""
    return content.decode("utf-8", errors="ignore")


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF file using pypdf."""
    try:
        from pypdf import PdfReader
        
        reader = PdfReader(io.BytesIO(content))
        text_parts = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        return "\n\n".join(text_parts)
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PDF parsing requires pypdf. Install with: pip install pypdf"
        )
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")


def extract_text_from_docx(content: bytes) -> str:
    """Extract text from DOCX file using python-docx."""
    try:
        from docx import Document
        
        doc = Document(io.BytesIO(content))
        text_parts = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        return "\n\n".join(text_parts)
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="DOCX parsing requires python-docx. Install with: pip install python-docx"
        )
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to parse DOCX: {str(e)}")


def extract_text(content: bytes, file_type: str) -> str:
    """
    Extract text from file based on type.
    
    Args:
        content: File content bytes
        file_type: File extension (pdf, txt, docx)
        
    Returns:
        Extracted text content
    """
    extractors = {
        "txt": extract_text_from_txt,
        "pdf": extract_text_from_pdf,
        "docx": extract_text_from_docx,
    }
    
    extractor = extractors.get(file_type)
    if not extractor:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_type}"
        )
    
    return extractor(content)


def chunk_text(text: str) -> List[dict]:
    """
    Split text into chunks using recursive character splitting.
    
    Args:
        text: Full document text
        
    Returns:
        List of chunk dicts with content and metadata
    """
    settings = get_settings()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = splitter.split_text(text)
    
    return [{"content": chunk, "index": i} for i, chunk in enumerate(chunks)]


@router.post("/ingest", response_model=DocumentUploadResponse)
async def ingest_document(
    file: UploadFile = File(..., description="Document file (PDF, TXT, or DOCX)")
) -> DocumentUploadResponse:
    """
    Upload and ingest a document into the vector store.
    
    Accepts PDF, TXT, or DOCX files. Extracts text, chunks it,
    generates embeddings, and stores in FAISS.
    """
    settings = get_settings()
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_type = get_file_extension(file.filename)
    
    if file_type not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_type}. Allowed: {settings.allowed_extensions}"
        )
    
    # Read file content
    content = await file.read()
    
    if len(content) > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_file_size // (1024*1024)}MB"
        )
    
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    logger.info(f"Processing file: {file.filename} ({len(content)} bytes)")
    
    # Generate document ID
    content_hash = compute_file_hash(content)
    document_id = generate_document_id(file.filename, content_hash)
    
    # Extract text
    text = extract_text(content, file_type)
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text content extracted from file")
    
    logger.info(f"Extracted {len(text)} characters from {file.filename}")
    
    # Chunk the text
    chunks = chunk_text(text)
    
    if not chunks:
        raise HTTPException(status_code=400, detail="Failed to create chunks from document")
    
    logger.info(f"Created {len(chunks)} chunks from {file.filename}")
    
    # Prepare texts and metadata for vector store
    texts = [chunk["content"] for chunk in chunks]
    metadatas = [
        {
            "document_id": document_id,
            "chunk_id": generate_chunk_id(document_id, chunk["index"]),
            "chunk_index": chunk["index"],
            "filename": sanitize_filename(file.filename),
            "file_type": file_type,
        }
        for chunk in chunks
    ]
    
    # Create document metadata
    doc_metadata = DocumentMetadata(
        document_id=document_id,
        filename=sanitize_filename(file.filename),
        file_type=file_type,
        file_size=len(content),
        chunk_count=len(chunks),
        content_hash=content_hash,
        status="indexed"
    )
    
    # Store in vector store
    vector_store = get_vector_store()
    vector_store.add_documents(texts, metadatas, doc_metadata)
    
    logger.info(f"Successfully ingested document: {document_id}")
    
    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        chunk_count=len(chunks),
        message=f"Document '{file.filename}' uploaded and indexed successfully with {len(chunks)} chunks"
    )


@router.post("/ingest/batch")
async def ingest_batch(
    files: List[UploadFile] = File(..., description="Multiple document files")
) -> dict:
    """
    Upload and ingest multiple documents.
    """
    results = []
    errors = []
    
    for file in files:
        try:
            result = await ingest_document(file)
            results.append(result.model_dump())
        except HTTPException as e:
            errors.append({
                "filename": file.filename,
                "error": e.detail
            })
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "success_count": len(results),
        "error_count": len(errors),
        "results": results,
        "errors": errors
    }
