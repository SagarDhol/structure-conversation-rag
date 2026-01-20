# Conversational RAG System

A production-ready Retrieval Augmented Generation system with streaming chat, conversation memory, and document management.

## 🎯 Features

- **RAG Pipeline**: FAISS vector store with semantic search
- **Conversation Memory**: Session-based multi-turn context
- **Streaming Chat**: Token-by-token SSE responses
- **Model Switching**: OpenAI and Ollama support
- **No Hallucination**: Strict answers from documents only
- **Document CRUD**: Upload, list, and delete documents

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Chat Window │  │  Documents  │  │    Model Selector       │  │
│  │  (SSE/Stream)│  │   Upload    │  │  (OpenAI / Ollama)      │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
└─────────┼────────────────┼─────────────────────┼────────────────┘
          │                │                     │
          ▼                ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    API LAYER                             │    │
│  │  /api/chat (SSE)  │  /api/ingest  │  /api/documents     │    │
│  └─────────┬──────────────┬─────────────────┬──────────────┘    │
│            │              │                 │                    │
│  ┌─────────▼──────────────▼─────────────────▼──────────────┐    │
│  │                   CORE SERVICES                          │    │
│  │  ┌───────────┐  ┌────────────┐  ┌──────────────────┐    │    │
│  │  │ Retriever │  │  Embeddings │  │ Conversation     │    │    │
│  │  │  (Top-K)  │  │  (MiniLM)   │  │ Memory (Session) │    │    │
│  │  └─────┬─────┘  └──────┬─────┘  └────────┬─────────┘    │    │
│  │        │               │                 │               │    │
│  │  ┌─────▼───────────────▼─────────────────▼─────────┐    │    │
│  │  │              FAISS Vector Store                  │    │    │
│  │  │          (Persistent, Local Storage)             │    │    │
│  │  └─────────────────────────────────────────────────┘    │    │
│  │                                                          │    │
│  │  ┌───────────────────────────────────────────────────┐  │    │
│  │  │              LLM PROVIDERS                         │  │    │
│  │  │   ┌─────────────┐         ┌──────────────────┐    │  │    │
│  │  │   │   OpenAI    │         │     Ollama       │    │  │    │
│  │  │   │ (gpt-4/3.5) │         │ (llama3/mistral) │    │  │    │
│  │  │   └─────────────┘         └──────────────────┘    │  │    │
│  │  └───────────────────────────────────────────────────┘  │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

## 🔄 RAG Flow

```
User Query → Retriever (FAISS) → Score Filtering → Context Building
                                                          ↓
Response ← LLM (OpenAI/Ollama) ← Prompt (Context + History) ←
```

1. **Query Enhancement**: Combine with conversation history
2. **Retrieval**: Semantic search in FAISS (top-k with score threshold)
3. **Context Building**: Inject relevant chunks into prompt
4. **Generation**: Stream response from LLM
5. **Memory Update**: Store turn for follow-up context

## 🧠 Memory Flow

```
Session A: [Q1 → A1] → [Q2 → A2] → [Q3 → A3]
Session B: [Q1 → A1] → [Q2 → A2]

Follow-up: "Tell me more" → Uses previous Q/A for context
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key OR Ollama running locally

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Run
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/chat` | POST | Streaming chat (SSE) |
| `/api/chat/sync` | POST | Non-streaming chat |
| `/api/ingest` | POST | Upload document |
| `/api/documents` | GET | List documents |
| `/api/documents/{id}` | DELETE | Delete document |
| `/api/session/clear` | POST | Clear session memory |
| `/api/model` | GET | Get model info |

## 🔧 Environment Variables

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama URL |
| `DEFAULT_LLM_PROVIDER` | openai | Default provider |
| `RETRIEVAL_TOP_K` | 5 | Chunks to retrieve |
| `RETRIEVAL_SCORE_THRESHOLD` | 0.3 | Minimum score |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | http://localhost:8000 | Backend URL |

## 🛡️ Hallucination Prevention

When no relevant documents are found:
```json
{
  "answer": "I do not have knowledge of this based on the uploaded documents.",
  "sources": [],
  "confidence": 0.0
}
```

## 📮 Postman

Import `postman/conversational-rag.postman_collection.json` for all API endpoints.

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── llm/          # LLM providers
│   │   ├── memory/       # Conversation memory
│   │   ├── rag/          # RAG pipeline
│   │   ├── schemas/      # Pydantic models
│   │   ├── config.py     # Settings
│   │   ├── main.py       # FastAPI app
│   │   └── utils.py      # Utilities
│   └── requirements.txt
├── frontend/
│   ├── src/app/
│   │   ├── components/   # React components
│   │   ├── documents/    # Documents page
│   │   ├── services/     # API client
│   │   └── page.tsx      # Chat page
│   └── styles/           # CSS
└── postman/              # API collection
```

## 📄 License

MIT
