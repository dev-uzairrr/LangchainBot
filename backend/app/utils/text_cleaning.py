"""
Text cleaning and preprocessing utilities.
"""
import re
import logging
from typing import List

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Raw text input
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:\-\']', '', text)
    
    # Trim
    text = text.strip()
    
    return text


def normalize_text(text: str) -> str:
    """
    Normalize text for ML models.
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Basic normalization
    text = text.lower().strip()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def preprocess_for_sentiment(text: str) -> str:
    """
    Preprocess text specifically for sentiment analysis.
    
    Args:
        text: Input text
        
    Returns:
        Preprocessed text
    """
    # Normalize
    text = normalize_text(text)
    
    # Remove numbers (optional - depends on model)
    # text = re.sub(r'\d+', '', text)
    
    return text

