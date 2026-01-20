/**
 * API Service Layer
 * Typed methods for all backend API endpoints
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
export interface Source {
    document: string;
    chunk_id: string;
    content_preview?: string;
}

export interface ChatResponse {
    answer: string;
    sources: Source[];
    confidence: number;
}

export interface StreamChunk {
    type: 'token' | 'sources' | 'done' | 'error';
    content?: string;
    sources?: Source[];
    confidence?: number;
    error?: string;
}

export interface DocumentMetadata {
    document_id: string;
    filename: string;
    file_type: string;
    file_size: number;
    chunk_count: number;
    created_at: string;
    status: string;
}

export interface DocumentListResponse {
    documents: DocumentMetadata[];
    total_count: number;
}

export interface UploadResponse {
    document_id: string;
    filename: string;
    chunk_count: number;
    message: string;
    success: boolean;
}

export interface ModelInfo {
    provider: string;
    model: string;
    available_providers: string[];
    available_models: Record<string, string[]>;
}

export interface HealthResponse {
    status: string;
    version: string;
    vector_store_ready: boolean;
}

// API Methods

/**
 * Health check
 */
export async function checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
        throw new Error('Health check failed');
    }
    return response.json();
}

/**
 * Send chat message (streaming)
 */
export async function* streamChat(
    message: string,
    sessionId: string,
    provider?: string,
    model?: string
): AsyncGenerator<StreamChunk> {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message,
            session_id: sessionId,
            provider,
            model,
        }),
    });

    if (!response.ok) {
        throw new Error(`Chat request failed: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
        throw new Error('Failed to get response reader');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = line.slice(6).trim();
                if (data) {
                    try {
                        const chunk: StreamChunk = JSON.parse(data);
                        yield chunk;
                    } catch (e) {
                        console.error('Failed to parse SSE data:', data);
                    }
                }
            }
        }
    }
}

/**
 * Send chat message (non-streaming)
 */
export async function sendChat(
    message: string,
    sessionId: string,
    provider?: string,
    model?: string
): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/api/chat/sync`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message,
            session_id: sessionId,
            provider,
            model,
        }),
    });

    if (!response.ok) {
        throw new Error(`Chat request failed: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Upload document
 */
export async function uploadDocument(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/ingest`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
}

/**
 * List all documents
 */
export async function listDocuments(): Promise<DocumentListResponse> {
    const response = await fetch(`${API_BASE_URL}/api/documents`);

    if (!response.ok) {
        throw new Error('Failed to fetch documents');
    }

    return response.json();
}

/**
 * Delete document
 */
export async function deleteDocument(documentId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/documents/${documentId}`, {
        method: 'DELETE',
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || 'Delete failed');
    }
}

/**
 * Clear session memory
 */
export async function clearSession(sessionId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/session/clear`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
    });

    if (!response.ok) {
        throw new Error('Failed to clear session');
    }
}

/**
 * Get model info
 */
export async function getModelInfo(): Promise<ModelInfo> {
    const response = await fetch(`${API_BASE_URL}/api/model`);

    if (!response.ok) {
        throw new Error('Failed to fetch model info');
    }

    return response.json();
}

/**
 * Generate session ID
 */
export function generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
