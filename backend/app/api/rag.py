"""
RAG API endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.core.rag_pipeline import rag_pipeline
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])


class RAGQueryRequest(BaseModel):
    """Request model for RAG query."""
    query: str = Field(..., description="User query")
    lang: str = Field(default="en", description="Language code")


class RAGQueryResponse(BaseModel):
    """Response model for RAG query."""
    answer: str = Field(..., description="Generated answer")
    sources: list = Field(..., description="List of source document IDs")
    confidence: float = Field(..., description="Confidence score (0-1)")


@router.post("/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest):
    """
    Process a RAG query.
    
    Args:
        request: Query request with query text and language
        
    Returns:
        RAG response with answer, sources, and confidence
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        result = await rag_pipeline.rag_query(
            query=request.query,
            lang=request.lang
        )
        
        return RAGQueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in RAG query endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

