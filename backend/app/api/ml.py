"""
ML API endpoints for sentiment analysis.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import pickle
import os
import logging

from app.core.config import settings
from app.utils.text_cleaning import preprocess_for_sentiment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["ML"])


class SentimentRequest(BaseModel):
    """Request model for sentiment analysis."""
    text: str = Field(..., description="Text to analyze")


class SentimentResponse(BaseModel):
    """Response model for sentiment analysis."""
    label: str = Field(..., description="Sentiment label (positive/negative/neutral)")
    score: float = Field(..., description="Confidence score (0-1)")


class SentimentModel:
    """Wrapper for sentiment model."""
    
    def __init__(self):
        """Load sentiment model."""
        self.model = None
        self.vectorizer = None
        self.load_model()
    
    def load_model(self):
        """Load the trained sentiment model."""
        try:
            model_path = settings.SENTIMENT_MODEL_PATH
            if not os.path.exists(model_path):
                logger.warning(f"Sentiment model not found at {model_path}. Using fallback.")
                self.model = None
                return
            
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
                self.model = model_data.get('model')
                self.vectorizer = model_data.get('vectorizer')
            
            logger.info("Sentiment model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading sentiment model: {str(e)}", exc_info=True)
            self.model = None
    
    def predict(self, text: str) -> dict:
        """
        Predict sentiment for text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with label and score
        """
        if self.model is None:
            # Fallback: simple rule-based sentiment
            return self._fallback_sentiment(text)
        
        try:
            # Preprocess text
            processed_text = preprocess_for_sentiment(text)
            
            # Vectorize
            if self.vectorizer:
                text_vector = self.vectorizer.transform([processed_text])
            else:
                # If no vectorizer, use simple features
                text_vector = [[len(processed_text), processed_text.count('!')]]
            
            # Predict
            prediction_array = self.model.predict(text_vector)
            probabilities = self.model.predict_proba(text_vector)[0]
            
            # Extract prediction value - handle numpy array properly
            import numpy as np
            if isinstance(prediction_array, np.ndarray):
                prediction_idx = int(prediction_array[0]) if prediction_array.size > 0 else 0
            elif hasattr(prediction_array, '__len__') and len(prediction_array) > 0:
                prediction_idx = int(prediction_array[0])
            else:
                prediction_idx = int(prediction_array)
            
            # Get label using probabilities (more reliable)
            if hasattr(self.model, 'classes_'):
                # Use argmax on probabilities to get the most likely class
                max_prob_idx = int(np.argmax(probabilities))
                if 0 <= max_prob_idx < len(self.model.classes_):
                    label = self.model.classes_[max_prob_idx]
                else:
                    # Fallback to prediction index
                    if 0 <= prediction_idx < len(self.model.classes_):
                        label = self.model.classes_[prediction_idx]
                    else:
                        label = "neutral"
            else:
                label = "positive" if prediction_idx == 1 else "negative"
            
            # Get score (max probability)
            score = float(np.max(probabilities))
            
            return {
                "label": str(label).lower(),
                "score": round(score, 2)
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment prediction: {str(e)}", exc_info=True)
            return self._fallback_sentiment(text)
    
    def _fallback_sentiment(self, text: str) -> dict:
        """Fallback sentiment analysis using simple rules."""
        text_lower = text.lower()
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'best', 'awesome', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disappointing']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return {"label": "positive", "score": 0.7}
        elif neg_count > pos_count:
            return {"label": "negative", "score": 0.7}
        else:
            return {"label": "neutral", "score": 0.5}


# Global sentiment model instance
sentiment_model = SentimentModel()


@router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """
    Analyze sentiment of text.
    
    Args:
        request: Sentiment analysis request
        
    Returns:
        Sentiment analysis result
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        result = sentiment_model.predict(request.text)
        return SentimentResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")

