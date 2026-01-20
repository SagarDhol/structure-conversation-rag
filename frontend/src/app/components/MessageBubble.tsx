'use client';

import React from 'react';
import styles from './MessageBubble.module.css';
import { Source } from '../services/api';

interface MessageBubbleProps {
    role: 'user' | 'assistant';
    content: string;
    sources?: Source[];
    confidence?: number;
    isStreaming?: boolean;
}

export default function MessageBubble({
    role,
    content,
    sources,
    confidence,
    isStreaming = false,
}: MessageBubbleProps) {
    return (
        <div className={`${styles.bubble} ${styles[role]}`}>
            <div className={styles.header}>
                <span className={styles.role}>
                    {role === 'user' ? 'You' : 'Assistant'}
                </span>
                {confidence !== undefined && confidence > 0 && (
                    <span className={styles.confidence}>
                        {Math.round(confidence * 100)}% confidence
                    </span>
                )}
            </div>

            <div className={styles.content}>
                {content}
                {isStreaming && <span className={styles.cursor}>▊</span>}
            </div>

            {sources && sources.length > 0 && (
                <div className={styles.sources}>
                    <div className={styles.sourcesHeader}>Sources:</div>
                    <ul className={styles.sourcesList}>
                        {sources.map((source, index) => (
                            <li key={index} className={styles.sourceItem}>
                                <span className={styles.sourceDoc}>{source.document}</span>
                                <span className={styles.sourceChunk}>({source.chunk_id})</span>
                                {source.content_preview && (
                                    <span className={styles.sourcePreview}>
                                        {source.content_preview}
                                    </span>
                                )}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}
