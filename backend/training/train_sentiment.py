"""
Training script for sentiment analysis model.
"""
import os
import sys
import pickle
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_and_prepare_data(csv_path: str):
    """
    Load and prepare training data.
    
    Args:
        csv_path: Path to CSV file with columns: text, label
        
    Returns:
        X (texts), y (labels)
    """
    try:
        # Read CSV with proper quoting to handle commas in text fields
        df = pd.read_csv(csv_path, quotechar='"', escapechar='\\')
        logger.info(f"Loaded {len(df)} samples from {csv_path}")
        
        # Check required columns
        if 'text' not in df.columns or 'label' not in df.columns:
            raise ValueError("CSV must have 'text' and 'label' columns")
        
        # Clean data
        df = df.dropna(subset=['text', 'label'])
        
        # Normalize labels
        df['label'] = df['label'].str.lower().str.strip()
        
        # Filter valid labels
        valid_labels = ['positive', 'negative', 'neutral']
        df = df[df['label'].isin(valid_labels)]
        
        X = df['text'].values
        y = df['label'].values
        
        logger.info(f"Prepared {len(X)} samples")
        logger.info(f"Label distribution:\n{df['label'].value_counts()}")
        
        return X, y
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}", exc_info=True)
        raise


def train_model(X_train, y_train, X_val, y_val):
    """
    Train sentiment classification model.
    
    Args:
        X_train: Training texts
        y_train: Training labels
        X_val: Validation texts
        y_val: Validation labels
        
    Returns:
        Trained model and vectorizer
    """
    try:
        logger.info("Vectorizing texts...")
        # TF-IDF vectorization
        vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            stop_words='english'
        )
        
        X_train_vec = vectorizer.fit_transform(X_train)
        X_val_vec = vectorizer.transform(X_val)
        
        logger.info(f"Vectorization complete. Features: {X_train_vec.shape[1]}")
        
        # Train Logistic Regression model
        logger.info("Training Logistic Regression model...")
        model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced'
        )
        
        model.fit(X_train_vec, y_train)
        
        # Evaluate
        y_pred = model.predict(X_val_vec)
        accuracy = accuracy_score(y_val, y_pred)
        
        logger.info(f"Validation Accuracy: {accuracy:.4f}")
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_val, y_pred))
        
        return model, vectorizer
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}", exc_info=True)
        raise


def save_model(model, vectorizer, output_path: str):
    """
    Save trained model and vectorizer.
    
    Args:
        model: Trained model
        vectorizer: Fitted vectorizer
        output_path: Path to save model
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save model and vectorizer
        model_data = {
            'model': model,
            'vectorizer': vectorizer,
        }
        
        with open(output_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}", exc_info=True)
        raise


def main():
    """Main training function."""
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "dataset_2.csv")
    model_path = os.path.join(script_dir, "..", "app", "models", "sentiment_model.pkl")
    
    # Check if dataset exists
    if not os.path.exists(csv_path):
        logger.warning(f"Dataset not found at {csv_path}")
        logger.info("Creating sample dataset...")
        
        # Create sample dataset
        sample_data = {
            'text': [
                'This movie is amazing! I loved it.',
                'Terrible experience, very disappointed.',
                'It was okay, nothing special.',
                'Great product, highly recommend!',
                'Worst service ever, avoid this place.',
                'The food was decent, could be better.',
                'Excellent quality, worth every penny.',
                'Poor quality, not worth buying.',
                'Average product, meets expectations.',
                'Outstanding performance, exceeded expectations!',
            ],
            'label': [
                'positive', 'negative', 'neutral',
                'positive', 'negative', 'neutral',
                'positive', 'negative', 'neutral', 'positive'
            ]
        }
        
        df = pd.DataFrame(sample_data)
        df.to_csv(csv_path, index=False)
        logger.info(f"Sample dataset created at {csv_path}")
    
    # Load data
    X, y = load_and_prepare_data(csv_path)
    
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train model
    model, vectorizer = train_model(X_train, y_train, X_val, y_val)
    
    # Save model
    save_model(model, vectorizer, model_path)
    
    logger.info("Training complete!")


if __name__ == "__main__":
    main()

