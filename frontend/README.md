# Conversational RAG Frontend

Next.js frontend for the Conversational RAG System with Google Dark Theme.

## Features

- 💬 **Streaming Chat**: Real-time token-by-token message display
- 📄 **Document Management**: Upload, list, and delete documents
- 🔄 **Model Switching**: Toggle between OpenAI and Ollama providers
- 🎨 **Google Dark Theme**: Premium dark mode UI

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `.env.local` file:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Pages

- **/** - Chat interface with streaming responses
- **/documents** - Document upload and management

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | http://localhost:8000 | Backend API URL |

## Building for Production

```bash
npm run build
npm start
```
