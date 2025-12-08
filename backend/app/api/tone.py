"""
Tone adjustment API endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging

from app.core.llm_groq import groq_llm

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tone", tags=["Tone"])


class ToneAdjustRequest(BaseModel):
    """Request model for tone adjustment."""
    text: str = Field(..., description="Text to adjust")


class ToneAdjustResponse(BaseModel):
    """Response model for tone adjustment."""
    adjusted: str = Field(..., description="Text with adjusted tone")


@router.post("/adjust", response_model=ToneAdjustResponse)
async def adjust_tone(request: ToneAdjustRequest):
    """
    Adjust text tone to be culturally warm (South Asian conversational style).
    
    Args:
        request: Tone adjustment request
        
    Returns:
        Adjusted text with warm, conversational tone
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        system_prompt = """You are a tone adjustment assistant that converts formal or neutral English text into a warm, culturally South Asian conversational style. 
        
Your task is to make the text sound friendly, warm, and conversational while maintaining the original meaning. Use natural South Asian English expressions like "yaar", "bro", "dear", etc. where appropriate, but keep it professional and not overly casual.

Examples:
- "Please join the call" → "Please join the call yaar, we're starting in 2 mins."
- "Thank you for your help" → "Thanks a lot for your help, really appreciate it!"
- "Can you send the file?" → "Could you send the file please? Would be great!"

Keep the core message intact, just make it warmer and more conversational."""
        
        prompt = f"""Adjust the tone of this text to be warm and culturally South Asian conversational style:

Text: {request.text}

Adjusted text:"""
        
        adjusted_text = await groq_llm.chat_completion_async(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8,  # Slightly higher for creativity
        )
        
        return ToneAdjustResponse(adjusted=adjusted_text.strip())
        
    except Exception as e:
        logger.error(f"Error in tone adjustment endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error adjusting tone: {str(e)}")

