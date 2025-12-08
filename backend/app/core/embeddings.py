"""
Embeddings generation using Hugging Face transformers.
"""
import logging
import torch
from typing import List
from transformers import AutoTokenizer, AutoModel
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingsGenerator:
    """Generate embeddings using Hugging Face transformers."""
    
    def __init__(self):
        """Initialize embeddings generator."""
        self.model = None
        self.tokenizer = None
        self.device = settings.EMBEDDING_DEVICE
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = None
        self._ensure_model_loaded()
    
    def _ensure_model_loaded(self):
        """Ensure the embeddings model is loaded."""
        if self.model is not None:
            return
        
        try:
            logger.info(f"Loading embeddings model: {self.model_name}")
            logger.info(f"Model cache directory: /Users/apple/.cache/huggingface/transformers")
            
            # Determine device
            if self.device == "cuda" and torch.cuda.is_available():
                device = "cuda"
                logger.info("Using CUDA device")
            else:
                device = "cpu"
                logger.info("Using CPU device")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(device)
            self.model.eval()
            
            # Get embedding dimension
            with torch.no_grad():
                # Create a dummy input to get the output dimension
                dummy_input = self.tokenizer("test", return_tensors="pt", padding=True, truncation=True)
                dummy_input = {k: v.to(device) for k, v in dummy_input.items()}
                output = self.model(**dummy_input)
                # Use mean pooling to get embedding dimension
                embeddings = output.last_hidden_state.mean(dim=1)
                self.dimension = embeddings.shape[1]
            
            logger.info(f"Embeddings model loaded successfully. Dimension: {self.dimension}")
            logger.info("Model will be reused from cache on subsequent loads")
            
        except Exception as e:
            logger.error(f"Error loading embeddings model: {str(e)}", exc_info=True)
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        return self.embed_documents([text])[0]
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        try:
            # Tokenize
            encoded = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=512
            )
            
            # Move to device
            device = next(self.model.parameters()).device
            encoded = {k: v.to(device) for k, v in encoded.items()}
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**encoded)
                # Use mean pooling
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            # Convert to list of lists
            embeddings_list = embeddings.cpu().numpy().tolist()
            
            return embeddings_list
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}", exc_info=True)
            raise


# Global instance
embeddings_generator = EmbeddingsGenerator()

