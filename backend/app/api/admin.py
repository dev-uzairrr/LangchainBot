"""
Admin API endpoints for document management.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
import uuid
import os
import logging
from typing import List

from app.core.config import settings
from app.core.vectorstore import vector_store
from app.utils.chunker import text_chunker
import PyPDF2
import csv
import io

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


class EmbedResponse(BaseModel):
    """Response model for document embedding."""
    doc_id: str = Field(..., description="Document ID")
    chunks_indexed: int = Field(..., description="Number of chunks indexed")


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file."""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}", exc_info=True)
        raise


def extract_text_from_csv(file_content: bytes) -> str:
    """Extract text from CSV file."""
    try:
        csv_file = io.StringIO(file_content.decode('utf-8'))
        reader = csv.reader(csv_file)
        text = ""
        for row in reader:
            text += " ".join(row) + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from CSV: {str(e)}", exc_info=True)
        raise


def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT file."""
    try:
        return file_content.decode('utf-8')
    except UnicodeDecodeError:
        # Try with different encoding
        return file_content.decode('latin-1')


@router.post("/embed", response_model=EmbedResponse)
async def embed_document(file: UploadFile = File(...)):
    """
    Upload and embed a document (PDF, TXT, or CSV).
    
    Args:
        file: Uploaded file
        
    Returns:
        Document ID and number of chunks indexed
    """
    try:
        # Validate file type
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.SUPPORTED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: {settings.SUPPORTED_FILE_TYPES}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Extract text based on file type
        if file_ext == ".pdf":
            text = extract_text_from_pdf(file_content)
        elif file_ext == ".csv":
            text = extract_text_from_csv(file_content)
        elif file_ext == ".txt":
            text = extract_text_from_txt(file_content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="File appears to be empty or could not extract text")
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Chunk text
        chunks = text_chunker.chunk_text(text)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="Could not create chunks from document")
        
        # Prepare metadata
        metadatas = [
            {
                "doc_id": doc_id,
                "filename": file.filename,
                "file_type": file_ext,
                "chunk_index": i,
            }
            for i in range(len(chunks))
        ]
        
        # Add to vector store
        chunk_ids = vector_store.add_documents(
            texts=chunks,
            metadatas=metadatas,
            doc_id=doc_id,
        )
        
        logger.info(f"Embedded document {doc_id} with {len(chunks)} chunks")
        
        return EmbedResponse(
            doc_id=doc_id,
            chunks_indexed=len(chunks)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in document embedding endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

