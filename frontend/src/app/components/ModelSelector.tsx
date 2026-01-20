'use client';

import React from 'react';
import styles from './ModelSelector.module.css';

interface ModelSelectorProps {
    provider: string;
    model: string;
    onProviderChange: (provider: string) => void;
    onModelChange: (model: string) => void;
}

const MODELS: Record<string, string[]> = {
    openai: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
    ollama: ['llama3', 'llama3.1', 'mistral', 'mixtral'],
};

export default function ModelSelector({
    provider,
    model,
    onProviderChange,
    onModelChange,
}: ModelSelectorProps) {
    const availableModels = MODELS[provider] || [];

    const handleProviderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const newProvider = e.target.value;
        onProviderChange(newProvider);
        // Reset to first model of new provider
        const models = MODELS[newProvider] || [];
        if (models.length > 0) {
            onModelChange(models[0]);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.field}>
                <label className={styles.label}>Provider</label>
                <select
                    className={styles.select}
                    value={provider}
                    onChange={handleProviderChange}
                >
                    <option value="openai">OpenAI</option>
                    <option value="ollama">Ollama</option>
                </select>
            </div>

            <div className={styles.field}>
                <label className={styles.label}>Model</label>
                <select
                    className={styles.select}
                    value={model}
                    onChange={(e) => onModelChange(e.target.value)}
                >
                    {availableModels.map((m) => (
                        <option key={m} value={m}>
                            {m}
                        </option>
                    ))}
                </select>
            </div>
        </div>
    );
}
