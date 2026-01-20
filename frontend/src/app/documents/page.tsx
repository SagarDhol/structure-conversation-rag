'use client';

import React, { useState, useEffect, useCallback } from 'react';
import styles from './page.module.css';
import DocumentUploader from '../components/DocumentUploader';
import DocumentTable from '../components/DocumentTable';
import { DocumentMetadata, listDocuments, UploadResponse } from '../services/api';

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const fetchDocuments = useCallback(async () => {
        try {
            setIsLoading(true);
            const response = await listDocuments();
            setDocuments(response.documents);
        } catch (err) {
            setError('Failed to load documents');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchDocuments();
    }, [fetchDocuments]);

    const handleUploadSuccess = (response: UploadResponse) => {
        setSuccess(`"${response.filename}" uploaded successfully with ${response.chunk_count} chunks`);
        setError(null);
        fetchDocuments();

        // Clear success message after 5 seconds
        setTimeout(() => setSuccess(null), 5000);
    };

    const handleUploadError = (errorMessage: string) => {
        setError(errorMessage);
        setSuccess(null);
    };

    const handleDocumentDeleted = (documentId: string) => {
        setDocuments((prev) => prev.filter((doc) => doc.document_id !== documentId));
        setSuccess('Document deleted successfully');
        setTimeout(() => setSuccess(null), 3000);
    };

    const handleTableError = (errorMessage: string) => {
        setError(errorMessage);
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1 className={styles.title}>Documents</h1>
                <p className={styles.subtitle}>
                    Upload and manage documents for the RAG knowledge base
                </p>
            </div>

            {error && (
                <div className={styles.alert + ' ' + styles.error}>
                    {error}
                    <button onClick={() => setError(null)}>×</button>
                </div>
            )}

            {success && (
                <div className={styles.alert + ' ' + styles.success}>
                    {success}
                    <button onClick={() => setSuccess(null)}>×</button>
                </div>
            )}

            <section className={styles.section}>
                <h2 className={styles.sectionTitle}>Upload Document</h2>
                <DocumentUploader
                    onUploadSuccess={handleUploadSuccess}
                    onUploadError={handleUploadError}
                />
            </section>

            <section className={styles.section}>
                <div className={styles.sectionHeader}>
                    <h2 className={styles.sectionTitle}>Uploaded Documents</h2>
                    <span className={styles.count}>{documents.length} documents</span>
                </div>

                {isLoading ? (
                    <div className={styles.loading}>
                        <div className={styles.spinner} />
                        <span>Loading documents...</span>
                    </div>
                ) : (
                    <DocumentTable
                        documents={documents}
                        onDocumentDeleted={handleDocumentDeleted}
                        onError={handleTableError}
                    />
                )}
            </section>
        </div>
    );
}
