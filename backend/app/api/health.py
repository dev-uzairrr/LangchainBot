"""
Health check API endpoints.
"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str


@router.get("", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return HealthResponse(status="ok")

