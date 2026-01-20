'use client';

import React, { useState } from 'react';
import styles from './DocumentTable.module.css';
import { DocumentMetadata, deleteDocument } from '../services/api';

interface DocumentTableProps {
    documents: DocumentMetadata[];
    onDocumentDeleted: (documentId: string) => void;
    onError: (error: string) => void;
}

function formatFileSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}

function getFileIcon(fileType: string): string {
    switch (fileType) {
        case 'pdf':
            return '📄';
        case 'txt':
            return '📝';
        case 'docx':
            return '📃';
        default:
            return '📁';
    }
}

export default function DocumentTable({
    documents,
    onDocumentDeleted,
    onError,
}: DocumentTableProps) {
    const [deletingId, setDeletingId] = useState<string | null>(null);

    const handleDelete = async (documentId: string) => {
        if (!confirm('Are you sure you want to delete this document?')) {
            return;
        }

        setDeletingId(documentId);

        try {
            await deleteDocument(documentId);
            onDocumentDeleted(documentId);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Delete failed';
            onError(message);
        } finally {
            setDeletingId(null);
        }
    };

    if (documents.length === 0) {
        return (
            <div className={styles.empty}>
                <div className={styles.emptyIcon}>📂</div>
                <p>No documents uploaded yet.</p>
                <p className={styles.hint}>Upload a document above to get started.</p>
            </div>
        );
    }

    return (
        <div className={styles.tableContainer}>
            <table className={styles.table}>
                <thead>
                    <tr>
                        <th>Document</th>
                        <th>Type</th>
                        <th>Size</th>
                        <th>Chunks</th>
                        <th>Uploaded</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {documents.map((doc) => (
                        <tr key={doc.document_id}>
                            <td className={styles.filename}>
                                <span className={styles.icon}>{getFileIcon(doc.file_type)}</span>
                                {doc.filename}
                            </td>
                            <td>
                                <span className={styles.badge}>{doc.file_type.toUpperCase()}</span>
                            </td>
                            <td>{formatFileSize(doc.file_size)}</td>
                            <td>{doc.chunk_count}</td>
                            <td>{formatDate(doc.created_at)}</td>
                            <td>
                                <span className={`${styles.status} ${styles[doc.status]}`}>
                                    {doc.status}
                                </span>
                            </td>
                            <td>
                                <button
                                    className={styles.deleteButton}
                                    onClick={() => handleDelete(doc.document_id)}
                                    disabled={deletingId === doc.document_id}
                                >
                                    {deletingId === doc.document_id ? (
                                        <span className={styles.spinner} />
                                    ) : (
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                                            <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" />
                                        </svg>
                                    )}
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
