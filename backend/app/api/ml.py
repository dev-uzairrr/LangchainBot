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
            import numpy as np
            
            # Preprocess text
            processed_text = preprocess_for_sentiment(text)
            
            # Vectorize
            if self.vectorizer:
                text_vector = self.vectorizer.transform([processed_text])
            else:
                # If no vectorizer, use simple features
                text_vector = [[len(processed_text), processed_text.count('!')]]
            
            # Get probabilities for all classes
            probabilities = self.model.predict_proba(text_vector)[0]
            
            # Get the index of the class with highest probability
            max_prob_idx = int(np.argmax(probabilities))
            
            # Get the label from model classes
            if hasattr(self.model, 'classes_') and len(self.model.classes_) > 0:
                if 0 <= max_prob_idx < len(self.model.classes_):
                    label = self.model.classes_[max_prob_idx]
                else:
                    # Fallback: use direct prediction
                    prediction = self.model.predict(text_vector)
                    if isinstance(prediction, np.ndarray) and prediction.size > 0:
                        label = str(prediction[0])
                    else:
                        label = str(prediction) if not isinstance(prediction, np.ndarray) else "neutral"
            else:
                # Fallback: use direct prediction
                prediction = self.model.predict(text_vector)
                if isinstance(prediction, np.ndarray) and prediction.size > 0:
                    label = str(prediction[0])
                else:
                    label = str(prediction) if not isinstance(prediction, np.ndarray) else "neutral"
            
            # Get score (max probability)
            score = float(np.max(probabilities))
            
            # Normalize label to lowercase
            label = str(label).lower().strip()
            
            # Validate label
            valid_labels = ['positive', 'negative', 'neutral']
            if label not in valid_labels:
                logger.warning(f"Invalid label '{label}' predicted, using fallback")
                return self._fallback_sentiment(text)
            
            return {
                "label": label,
                "score": round(score, 2)
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment prediction: {str(e)}", exc_info=True)
            return self._fallback_sentiment(text)
    
    def _fallback_sentiment(self, text: str) -> dict:
        """Fallback sentiment analysis using simple rules."""
        text_lower = text.lower()
        
        # Expanded word lists
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'best', 'awesome', 
            'fantastic', 'brilliant', 'outstanding', 'perfect', 'superb', 'marvelous', 'delightful',
            'zabardast', 'acha', 'bohot acha', 'maza aya', 'impressed', 'satisfied', 'happy',
            'pleased', 'enjoyed', 'recommend', 'exceeded', 'loved', 'adore', 'fantastic'
        ]
        negative_words = [
            'bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disappointing', 'poor',
            'waste', 'disgusting', 'annoying', 'frustrated', 'angry', 'upset', 'disappointed',
            'bekar', 'pasand nahi', 'kharab', 'ganda', 'bura', 'worst', 'hated', 'avoid',
            'never', 'regret', 'disgusted', 'furious', 'miserable'
        ]
        
        # Count positive and negative words
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        # Check for exclamation marks and intensity
        exclamation_count = text.count('!')
        if exclamation_count > 0:
            if pos_count > 0:
                pos_count += 1
            elif neg_count > 0:
                neg_count += 1
        
        # Determine sentiment
        if pos_count > neg_count:
            confidence = min(0.7 + (pos_count - neg_count) * 0.1, 0.95)
            return {"label": "positive", "score": round(confidence, 2)}
        elif neg_count > pos_count:
            confidence = min(0.7 + (neg_count - pos_count) * 0.1, 0.95)
            return {"label": "negative", "score": round(confidence, 2)}
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

