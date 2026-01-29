/**
 * Additional OpenAI-compatible providers for SecureShell TypeScript SDK
 * DeepSeek, Groq, Ollama, LlamaCpp all use OpenAI-compatible API
 */

import { OpenAIProvider } from './openai';

/**
 * DeepSeek Provider (OpenAI-compatible)
 */
export class DeepSeekProvider extends OpenAIProvider {
    constructor(options: { apiKey: string; model?: string }) {
        super({
            apiKey: options.apiKey,
            model: options.model || 'deepseek-chat',
            baseURL: 'https://api.deepseek.com/v1'
        });
    }

    get providerName(): string {
        return 'deepseek';
    }
}

/**
 * Groq Provider (OpenAI-compatible)
 */
export class GroqProvider extends OpenAIProvider {
    constructor(options: { apiKey: string; model?: string }) {
        super({
            apiKey: options.apiKey,
            model: options.model || 'llama-3.3-70b-versatile',
            baseURL: 'https://api.groq.com/openai/v1'
        });
    }

    get providerName(): string {
        return 'groq';
    }
}

/**
 * Ollama Provider (OpenAI-compatible, local)
 */
export class OllamaProvider extends OpenAIProvider {
    constructor(options: { apiKey?: string; model?: string; baseURL?: string }) {
        super({
            apiKey: options.apiKey || 'ollama', // Ollama doesn't require real API key
            model: options.model || 'qwen2.5:14b',
            baseURL: options.baseURL || 'http://localhost:11434/v1'
        });
    }

    get providerName(): string {
        return 'ollama';
    }
}

/**
 * LlamaCpp Provider (OpenAI-compatible, local)
 */
export class LlamaCppProvider extends OpenAIProvider {
    constructor(options: { apiKey?: string; model?: string; baseURL?: string }) {
        super({
            apiKey: options.apiKey || 'llamacpp', // llama.cpp doesn't require real API key
            model: options.model || 'gpt-3.5-turbo', // llama.cpp uses generic model name
            baseURL: options.baseURL || 'http://localhost:8080/v1'
        });
    }

    get providerName(): string {
        return 'llamacpp';
    }
}
