# Backend - Multilingual AI Intelligence Platform

FastAPI backend for the Multilingual AI Intelligence Platform with RAG, sentiment analysis, and tone adjustment capabilities.

## Features

- **RAG (Retrieval-Augmented Generation)**: Query documents using LangChain and Qdrant
- **Sentiment Analysis**: ML-based sentiment classification
- **Tone Adjustment**: Convert text to warm, culturally South Asian conversational style
- **Document Ingestion**: Upload and embed PDF, TXT, and CSV files
- **Health Check**: API health monitoring

## Tech Stack

- Python 3.11
- FastAPI
- LangChain
- Qdrant Cloud (vector database)
- Groq API (LLM)
- Transformers (Hugging Face) for embeddings
- scikit-learn (ML models)

## Setup

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the `backend` directory:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=2048

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu

QDRANT_URL=https://a460876d-78ac-4688-a859-20262c43a57b.us-east4-0.gcp.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=multilingual_docs

RAG_TOP_K=4
RAG_MIN_SCORE=0.3

SENTIMENT_MODEL_PATH=./app/models/sentiment_model.pkl

MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200

LOG_LEVEL=INFO
LOG_FORMAT=json
```

5. Train the sentiment model:
```bash
python training/train_sentiment.py
```

6. Create necessary directories:
```bash
mkdir -p app/models
mkdir -p app/data/multilingual_docs
```

## Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## API Endpoints

### Health Check
- `GET /health` - Check API health

### RAG
- `POST /api/v1/rag/query` - Query documents using RAG
  ```json
  {
    "query": "who built taj mahal?",
    "lang": "en"
  }
  ```

### ML
- `POST /api/v1/ml/sentiment` - Analyze sentiment
  ```json
  {
    "text": "yeh movie bohot zabardast thi!"
  }
  ```

### Tone
- `POST /api/v1/tone/adjust` - Adjust text tone
  ```json
  {
    "text": "please join the call"
  }
  ```

### Admin
- `POST /api/v1/admin/embed` - Upload and embed document
  - Form data with `file` field (PDF, TXT, or CSV)

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/                 # API routers
│   │   ├── rag.py
│   │   ├── ml.py
│   │   ├── tone.py
│   │   ├── admin.py
│   │   └── health.py
│   ├── core/                # Core modules
│   │   ├── llm_groq.py
│   │   ├── embeddings.py
│   │   ├── vectorstore.py
│   │   ├── rag_pipeline.py
│   │   ├── config.py
│   │   └── logging.py
│   ├── data/
│   │   └── multilingual_docs/
│   ├── models/
│   │   └── sentiment_model.pkl
│   └── utils/
│       ├── chunker.py
│       └── text_cleaning.py
├── training/
│   ├── train_sentiment.py
│   └── dataset.csv
├── requirements.txt
└── README.md
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
isort app/
```

## Environment Variables

See `.env` file template above. Key variables:
- `GROQ_API_KEY`: Required for LLM functionality
- `QDRANT_URL`: Qdrant Cloud URL
- `QDRANT_API_KEY`: Qdrant Cloud API key
- `SENTIMENT_MODEL_PATH`: Path to trained sentiment model

## Notes

- The sentiment model is trained using the dataset in `training/dataset.csv`
- Qdrant Cloud stores embeddings in the cloud
- Document chunks are stored with metadata for source tracking
- All API responses follow consistent error handling patterns

