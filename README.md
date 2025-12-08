# Multilingual AI Intelligence Platform

A full-stack AI-powered platform with RAG (Retrieval-Augmented Generation), sentiment analysis, and tone adjustment capabilities. Built with FastAPI and Next.js.

## 🚀 Features

- **RAG Chat**: Query documents using AI-powered retrieval with LangChain and Qdrant
- **Sentiment Analysis**: ML-based sentiment classification (positive/negative/neutral)
- **Tone Adjustment**: Convert text to warm, culturally South Asian conversational style
- **Document Ingestion**: Upload and embed PDF, TXT, and CSV files

## 🏗️ Architecture

```
LangchainBot/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routers
│   │   ├── core/        # Core modules (LLM, embeddings, RAG)
│   │   ├── utils/       # Utilities
│   │   └── models/      # ML models
│   └── training/        # Training scripts
└── frontend-web/        # Next.js web application
    └── app/            # App Router pages
```

## 🛠️ Tech Stack

### Backend
- Python 3.11
- FastAPI
- LangChain
- Qdrant Cloud (vector database)
- Groq API (LLM: llama-3.1-8b-instant)
- Transformers (Hugging Face) for embeddings
- scikit-learn (ML models)

### Frontend Web
- Next.js 14 (App Router)
- React 18
- TailwindCSS
- React Query (TanStack Query)
- Axios

## 📦 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Groq API key ([Get one here](https://console.groq.com/))

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
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

5. Train sentiment model:
```bash
python training/train_sentiment.py
```

6. Create necessary directories:
```bash
mkdir -p app/models
mkdir -p app/data/multilingual_docs
```

7. Start backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API will be available at: http://localhost:8000
API Docs: http://localhost:8000/docs

### Frontend Web Setup

1. Navigate to frontend-web directory:
```bash
cd frontend-web
```

2. Install dependencies:
```bash
npm install
```

3. (Optional) Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start development server:
```bash
npm run dev
```

Web app will be available at: http://localhost:3000

## 📚 API Endpoints

### Health
- `GET /health` - Health check

### RAG
- `POST /api/v1/rag/query` - Query documents
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

## 🎯 Usage Examples

### Upload a Document

1. Go to `/admin/upload` in the web app
2. Upload a PDF, TXT, or CSV file
3. Wait for processing (chunks will be indexed)

### Query Documents

1. Go to `/chat` in the web app
2. Enter a question about your uploaded documents
3. Get AI-powered answers with source citations

### Analyze Sentiment

1. Go to `/sentiment` in the web app
2. Enter text to analyze
3. Get sentiment label and confidence score

### Adjust Tone

1. Go to `/tone` in the web app
2. Enter text to adjust
3. Get warm, culturally South Asian conversational output

## 📖 Documentation

- [Backend README](./backend/README.md)
- [Frontend Web README](./frontend-web/README.md)

## 🔧 Development

### Backend Development

```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend Web Development

```bash
cd frontend-web
npm run dev
```

## 🧪 Training ML Models

The sentiment model can be retrained with custom data:

```bash
cd backend
python training/train_sentiment.py
```

Update `training/dataset.csv` with your training data (columns: `text`, `label`).

## 📝 Environment Variables

### Backend
- `GROQ_API_KEY` (required): Groq API key for LLM
- `QDRANT_URL` (required): Qdrant Cloud URL
- `QDRANT_API_KEY` (required): Qdrant Cloud API key
- `SENTIMENT_MODEL_PATH`: Path to sentiment model

### Frontend Web
- `NEXT_PUBLIC_API_URL`: Backend API URL

## 🚨 Troubleshooting

### Backend Issues

- **Qdrant connection errors**: Verify `QDRANT_URL` and `QDRANT_API_KEY` are correct
- **Model not found**: Run `python training/train_sentiment.py`
- **Groq API errors**: Verify API key in `.env`

### Frontend Web Issues

- **API connection errors**: Check `NEXT_PUBLIC_API_URL` and ensure backend is running
- **Build errors**: Clear `.next` directory and rebuild

## 📄 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

This is an MVP project. Feel free to extend and improve it!

## 📧 Support

For issues and questions, please check the individual README files in each directory.

