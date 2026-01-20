'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import styles from './ChatWindow.module.css';
import MessageBubble from './MessageBubble';
import ModelSelector from './ModelSelector';
import { streamChat, clearSession, generateSessionId, Source, StreamChunk } from '../services/api';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    sources?: Source[];
    confidence?: number;
    isStreaming?: boolean;
}

export default function ChatWindow() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [provider, setProvider] = useState('openai');
    const [model, setModel] = useState('gpt-3.5-turbo');
    const [sessionId, setSessionId] = useState<string>('');
    const [error, setError] = useState<string | null>(null);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        setSessionId(generateSessionId());
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSubmit = useCallback(async (e: React.FormEvent) => {
        e.preventDefault();

        const trimmedInput = input.trim();
        if (!trimmedInput || isLoading) return;

        setError(null);
        setInput('');

        // Add user message
        const userMessage: Message = {
            id: `user-${Date.now()}`,
            role: 'user',
            content: trimmedInput,
        };

        setMessages((prev) => [...prev, userMessage]);
        setIsLoading(true);

        // Add placeholder for assistant
        const assistantId = `assistant-${Date.now()}`;
        const assistantMessage: Message = {
            id: assistantId,
            role: 'assistant',
            content: '',
            isStreaming: true,
        };

        setMessages((prev) => [...prev, assistantMessage]);

        try {
            let fullContent = '';
            let sources: Source[] = [];
            let confidence = 0;

            for await (const chunk of streamChat(trimmedInput, sessionId, provider, model)) {
                if (chunk.type === 'token' && chunk.content) {
                    fullContent += chunk.content;
                    setMessages((prev) =>
                        prev.map((msg) =>
                            msg.id === assistantId
                                ? { ...msg, content: fullContent }
                                : msg
                        )
                    );
                } else if (chunk.type === 'sources' && chunk.sources) {
                    sources = chunk.sources;
                } else if (chunk.type === 'done' && chunk.confidence !== undefined) {
                    confidence = chunk.confidence;
                } else if (chunk.type === 'error') {
                    throw new Error(chunk.error || 'Stream error');
                }
            }

            // Finalize message
            setMessages((prev) =>
                prev.map((msg) =>
                    msg.id === assistantId
                        ? { ...msg, content: fullContent, sources, confidence, isStreaming: false }
                        : msg
                )
            );
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'An error occurred';
            setError(errorMessage);

            // Update assistant message with error
            setMessages((prev) =>
                prev.map((msg) =>
                    msg.id === assistantId
                        ? { ...msg, content: `Error: ${errorMessage}`, isStreaming: false }
                        : msg
                )
            );
        } finally {
            setIsLoading(false);
        }
    }, [input, isLoading, sessionId, provider, model]);

    const handleClearChat = async () => {
        try {
            await clearSession(sessionId);
            setMessages([]);
            setSessionId(generateSessionId());
            setError(null);
        } catch (err) {
            setError('Failed to clear session');
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.title}>Conversational RAG</h1>
                <div className={styles.controls}>
                    <ModelSelector
                        provider={provider}
                        model={model}
                        onProviderChange={setProvider}
                        onModelChange={setModel}
                    />
                    <button
                        className={styles.clearButton}
                        onClick={handleClearChat}
                        disabled={isLoading}
                    >
                        Clear Chat
                    </button>
                </div>
            </div>

            {error && (
                <div className={styles.error}>
                    {error}
                    <button onClick={() => setError(null)}>×</button>
                </div>
            )}

            <div className={styles.messages}>
                {messages.length === 0 && (
                    <div className={styles.empty}>
                        <div className={styles.emptyIcon}>💬</div>
                        <p>Start a conversation by asking a question about your documents.</p>
                        <p className={styles.hint}>
                            Upload documents on the <a href="/documents">Documents</a> page first.
                        </p>
                    </div>
                )}

                {messages.map((msg) => (
                    <MessageBubble
                        key={msg.id}
                        role={msg.role}
                        content={msg.content}
                        sources={msg.sources}
                        confidence={msg.confidence}
                        isStreaming={msg.isStreaming}
                    />
                ))}

                <div ref={messagesEndRef} />
            </div>

            <form className={styles.inputForm} onSubmit={handleSubmit}>
                <textarea
                    ref={inputRef}
                    className={styles.textarea}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask a question about your documents..."
                    disabled={isLoading}
                    rows={1}
                />
                <button
                    type="submit"
                    className={styles.sendButton}
                    disabled={isLoading || !input.trim()}
                >
                    {isLoading ? (
                        <span className={styles.spinner} />
                    ) : (
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                        </svg>
                    )}
                </button>
            </form>
        </div>
    );
}
