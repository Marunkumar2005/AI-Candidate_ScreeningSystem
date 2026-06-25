# AI Interview System — PGAGI Assignment

RAG-powered candidate screening system that dynamically generates interview questions based on the candidate's resume and selected job role.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                     │
│  HomePage → InterviewPage → SummaryPage                 │
│  Zustand state · Axios API calls · React Router         │
└─────────────────────┬───────────────────────────────────┘
                      │ REST API
┌─────────────────────▼───────────────────────────────────┐
│                   BACKEND (FastAPI)                      │
│  /api/resume  →  Resume parsing + extraction            │
│  /api/sessions → Session lifecycle management           │
│  /api/questions → Answer submission + evaluation        │
└─────────────┬──────────────────────┬────────────────────┘
              │                      │
    ┌─────────▼──────┐    ┌──────────▼─────────┐
    │   SQLite DB    │    │   ChromaDB (Vector) │
    │  Sessions      │    │  Role-specific      │
    │  Questions     │    │  knowledge chunks   │
    │  Summaries     │    │  (embeddings)       │
    └────────────────┘    └────────────────────┘
              │
    ┌─────────▼──────────┐
    │   OpenAI API       │
    │  - Resume parsing  │
    │  - Q generation    │
    │  - Answer eval     │
    │  - Summary gen     │
    └────────────────────┘
```

---

## System Flow

1. **Candidate uploads resume** (PDF or text) and selects target role
2. **Resume Parsing**: Extract skills, technologies, experience using GPT-3.5 (fallback: regex)
3. **RAG Query Construction**: Build embedding query from candidate profile
4. **Knowledge Retrieval**: ChromaDB retrieves relevant chunks from role-specific knowledge base
5. **Question Generation**: GPT-3.5 generates contextual questions using retrieved chunks + candidate profile
6. **Interactive Interview**: Candidate answers; AI evaluates each response in real time
7. **Session Summary**: GPT-3.5 generates overall assessment, strengths, improvements, and hiring recommendation

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API key (optional — fallback questions work without it)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the server
uvicorn app.main:app --reload --port 8000
```

Backend runs at: http://localhost:8000
API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at: http://localhost:3000

---

## Key Design Decisions

### RAG Pipeline
- **Chunking**: Role-specific knowledge base divided into ~800-token semantic chunks
- **Embeddings**: ChromaDB's default embedding function (sentence-transformers compatible)
- **Retrieval**: Top-4 most similar chunks retrieved per query
- **Grounding**: Retrieved context is injected directly into question generation prompt

### Why SQLite?
- Zero-config for quick setup; swap to PostgreSQL by changing `DATABASE_URL` in `.env`

### Why ChromaDB?
- Persistent local vector store; no external service needed
- Graceful fallback if unavailable

### Fallback Behavior
- No OpenAI key? → Uses curated fallback questions per role
- No ChromaDB? → Uses in-memory role knowledge dictionary

### Session Management
- Each interview = one `Session` row with linked `Question` rows
- Answers stored per question with AI score + feedback
- `SessionSummary` generated on completion

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check + config status |
| POST | `/api/resume/upload` | Upload PDF/TXT resume |
| POST | `/api/resume/parse-text` | Parse pasted resume text |
| POST | `/api/sessions/create` | Create session + generate questions |
| GET | `/api/sessions/{id}` | Get session with all questions |
| POST | `/api/sessions/{id}/complete` | Complete session + generate summary |
| GET | `/api/sessions/{id}/summary` | Get full summary |
| POST | `/api/questions/{id}/answer` | Submit answer + get evaluation |
| POST | `/api/questions/generate-more` | Add 2 more questions |

---

## Project Structure

```
rag-interview-system/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers
│   │   ├── core/         # Config, settings
│   │   ├── db/           # SQLAlchemy setup
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   │   ├── resume_service.py   # PDF parsing + extraction
│   │   │   ├── rag_service.py      # ChromaDB + retrieval
│   │   │   └── question_service.py # Q generation + evaluation
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── pages/        # HomePage, InterviewPage, SummaryPage
    │   ├── components/   # Layout
    │   ├── store/        # Zustand state
    │   └── utils/        # API client
    ├── package.json
    └── vite.config.js
```
