# Frontend Web - Multilingual AI Intelligence Platform

Next.js 14 web application for the Multilingual AI Intelligence Platform.

## Features

- **RAG Chat**: Interactive chat interface for querying documents
- **Sentiment Analysis**: Analyze sentiment of text with visual feedback
- **Tone Adjuster**: Convert text to warm, culturally South Asian conversational style
- **Document Upload**: Upload and embed PDF, TXT, and CSV files

## Tech Stack

- Next.js 14 (App Router)
- React 18
- TailwindCSS
- React Query (TanStack Query)
- Axios

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. Navigate to the frontend-web directory:
```bash
cd frontend-web
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file (optional):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

The application will be available at http://localhost:3000

## Project Structure

```
frontend-web/
├── app/
│   ├── chat/
│   │   └── page.jsx          # RAG chat interface
│   ├── sentiment/
│   │   └── page.jsx          # Sentiment analysis page
│   ├── tone/
│   │   └── page.jsx          # Tone adjustment page
│   ├── admin/
│   │   └── upload/
│   │       └── page.jsx      # Document upload page
│   ├── layout.js             # Root layout
│   ├── page.js               # Home page
│   └── globals.css           # Global styles
├── lib/
│   └── api.js                # API client
├── components/               # Reusable components (if any)
├── package.json
├── tailwind.config.js
└── README.md
```

## Pages

### `/` - Home
Landing page with links to all features.

### `/chat` - RAG Chat
- Query documents using natural language
- Language selection
- Chat history
- Source citations
- Confidence scores

### `/sentiment` - Sentiment Analysis
- Text input
- Sentiment label (positive/negative/neutral)
- Confidence score visualization

### `/tone` - Tone Adjuster
- Text input
- Warm, culturally South Asian conversational output
- Side-by-side comparison

### `/admin/upload` - Document Upload
- File upload (PDF, TXT, CSV)
- Drag and drop support
- Upload status and results
- Chunks indexed count

## API Integration

The frontend communicates with the backend API through the `lib/api.js` client:

- `ragAPI.query(query, lang)` - RAG queries
- `mlAPI.sentiment(text)` - Sentiment analysis
- `toneAPI.adjust(text)` - Tone adjustment
- `adminAPI.embed(file)` - Document upload

## Development

### Build for Production

```bash
npm run build
npm start
```

### Linting

```bash
npm run lint
```

## Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

## Notes

- Ensure the backend server is running before using the frontend
- All API calls use React Query for caching and state management
- TailwindCSS is used for all styling
- The app uses Next.js App Router (not Pages Router)

