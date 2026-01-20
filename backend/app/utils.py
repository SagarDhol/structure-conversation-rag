"""
Utility functions for the RAG application.
Provides logging, file handling, and ID generation.
"""

import hashlib
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure and return the application logger.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("rag_app")
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper()))
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


# Global logger instance
logger = setup_logging()


def generate_document_id(filename: str, content_hash: Optional[str] = None) -> str:
    """
    Generate a unique document ID based on filename and optional content hash.
    
    Args:
        filename: Original filename
        content_hash: Optional hash of file content for deduplication
    
    Returns:
        Unique document ID string
    """
    if content_hash:
        return f"doc_{content_hash[:8]}_{uuid.uuid4().hex[:8]}"
    return f"doc_{uuid.uuid4().hex}"


def generate_chunk_id(document_id: str, chunk_index: int) -> str:
    """
    Generate a unique chunk ID.
    
    Args:
        document_id: Parent document ID
        chunk_index: Index of chunk within document
    
    Returns:
        Unique chunk ID string
    """
    return f"{document_id}_chunk_{chunk_index:04d}"


def generate_session_id() -> str:
    """
    Generate a unique session ID for conversation tracking.
    
    Returns:
        Unique session ID string
    """
    return f"session_{uuid.uuid4().hex}"


def compute_file_hash(file_content: bytes) -> str:
    """
    Compute SHA-256 hash of file content.
    
    Args:
        file_content: Raw file bytes
    
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(file_content).hexdigest()


def ensure_directory(path: str) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
    
    Returns:
        Path object for the directory
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_file_extension(filename: str) -> str:
    """
    Extract file extension from filename.
    
    Args:
        filename: Original filename
    
    Returns:
        Lowercase file extension without dot
    """
    return Path(filename).suffix.lower().lstrip(".")


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime as ISO string.
    
    Args:
        dt: Datetime object (defaults to now)
    
    Returns:
        ISO formatted timestamp string
    """
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat() + "Z"


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to append if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing unsafe characters.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    return filename.strip()
