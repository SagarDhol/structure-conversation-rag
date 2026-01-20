# Conversational RAG Backend

Production-ready FastAPI backend for Retrieval Augmented Generation with streaming support.

## Features

- 🔍 **RAG Pipeline**: FAISS vector store with sentence-transformers embeddings
- 💬 **Streaming Chat**: Server-Sent Events for token-by-token responses
- 🧠 **Conversation Memory**: Session-based context for follow-up questions
- 🔄 **Model Switching**: Support for OpenAI and Ollama providers
- 📄 **Document Management**: Upload, list, and delete documents
- ✅ **No Hallucination**: Strict responses based only on document content

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

Required for OpenAI:
```
OPENAI_API_KEY=your-api-key-here
```

For Ollama (local):
```
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_LLM_PROVIDER=ollama
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Chat
- `POST /api/chat` - Streaming chat (SSE)
- `POST /api/chat/sync` - Non-streaming chat

### Documents
- `POST /api/ingest` - Upload document
- `GET /api/documents` - List documents
- `DELETE /api/documents/{id}` - Delete document

### Session
- `POST /api/session/clear` - Clear session memory
- `GET /api/sessions` - List active sessions
- `DELETE /api/sessions` - Clear all sessions

### Utility
- `GET /health` - Health check
- `GET /api/model` - Current model info

## Documentation

Visit `/docs` for interactive Swagger UI documentation.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama server URL |
| `DEFAULT_LLM_PROVIDER` | openai | Default provider |
| `VECTOR_STORE_PATH` | ./vector_store | FAISS index location |
| `RETRIEVAL_TOP_K` | 5 | Number of chunks to retrieve |
| `RETRIEVAL_SCORE_THRESHOLD` | 0.3 | Minimum similarity score |
