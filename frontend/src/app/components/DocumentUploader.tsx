'use client';

import React, { useRef, useState, useCallback } from 'react';
import styles from './DocumentUploader.module.css';
import { uploadDocument, UploadResponse } from '../services/api';

interface DocumentUploaderProps {
    onUploadSuccess: (response: UploadResponse) => void;
    onUploadError: (error: string) => void;
}

const ACCEPTED_TYPES = ['.pdf', '.txt', '.docx'];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export default function DocumentUploader({
    onUploadSuccess,
    onUploadError,
}: DocumentUploaderProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const validateFile = (file: File): string | null => {
        const extension = `.${file.name.split('.').pop()?.toLowerCase()}`;

        if (!ACCEPTED_TYPES.includes(extension)) {
            return `Invalid file type. Accepted: ${ACCEPTED_TYPES.join(', ')}`;
        }

        if (file.size > MAX_FILE_SIZE) {
            return `File too large. Maximum size: ${MAX_FILE_SIZE / (1024 * 1024)}MB`;
        }

        return null;
    };

    const handleUpload = useCallback(async (file: File) => {
        const error = validateFile(file);
        if (error) {
            onUploadError(error);
            return;
        }

        setIsUploading(true);
        setUploadProgress(`Uploading ${file.name}...`);

        try {
            const response = await uploadDocument(file);
            onUploadSuccess(response);
            setUploadProgress(null);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Upload failed';
            onUploadError(message);
            setUploadProgress(null);
        } finally {
            setIsUploading(false);
        }
    }, [onUploadSuccess, onUploadError]);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            handleUpload(files[0]);
        }
        // Reset input
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            handleUpload(files[0]);
        }
    };

    const handleClick = () => {
        fileInputRef.current?.click();
    };

    return (
        <div
            className={`${styles.dropzone} ${isDragging ? styles.dragging : ''} ${isUploading ? styles.uploading : ''
                }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleClick}
        >
            <input
                ref={fileInputRef}
                type="file"
                className={styles.input}
                accept={ACCEPTED_TYPES.join(',')}
                onChange={handleFileSelect}
                disabled={isUploading}
            />

            {isUploading ? (
                <div className={styles.uploadingState}>
                    <div className={styles.spinner} />
                    <p>{uploadProgress}</p>
                </div>
            ) : (
                <>
                    <div className={styles.icon}>
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z" />
                        </svg>
                    </div>
                    <p className={styles.text}>
                        <span className={styles.highlight}>Click to upload</span> or drag and drop
                    </p>
                    <p className={styles.hint}>PDF, TXT, or DOCX (max 10MB)</p>
                </>
            )}
        </div>
    );
}
