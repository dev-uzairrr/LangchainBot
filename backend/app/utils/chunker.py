"""
Text chunking utilities for document processing.
"""
import logging
from typing import List

from app.core.config import settings

logger = logging.getLogger(__name__)


class TextChunker:
    """Chunk text into smaller pieces for embedding."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size or settings.MAX_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        # Simple character-based chunking
        # For production, consider using more sophisticated methods
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Calculate end position
            end = start + self.chunk_size
            
            # If not the last chunk, try to break at sentence boundary
            if end < text_length:
                # Look for sentence endings near the chunk boundary
                for break_char in ['. ', '.\n', '! ', '!\n', '? ', '?\n', '\n\n']:
                    last_break = text.rfind(break_char, start, end)
                    if last_break != -1:
                        end = last_break + len(break_char)
                        break
            
            # Extract chunk
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position (with overlap)
            start = end - self.chunk_overlap
            if start >= text_length:
                break
        
        logger.info(f"Chunked text into {len(chunks)} chunks")
        return chunks
    
    def chunk_documents(self, texts: List[str]) -> List[str]:
        """
        Chunk multiple documents.
        
        Args:
            texts: List of texts to chunk
            
        Returns:
            List of all chunks
        """
        all_chunks = []
        for text in texts:
            chunks = self.chunk_text(text)
            all_chunks.extend(chunks)
        
        return all_chunks


# Global instance
text_chunker = TextChunker()

