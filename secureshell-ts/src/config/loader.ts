/**
 * Configuration loader for SecureShell TypeScript SDK
 * Loads from environment variables and YAML file
 */

import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';
import * as os from 'os';
import { SecureShellConfig } from '../models/types';

/**
 * Default configuration values
 */
const DEFAULT_CONFIG: SecureShellConfig = {
    appName: 'SecureShell',
    environment: 'production',
    debugMode: false,
    provider: 'openai',
    defaultTimeoutSeconds: 300,
    maxOutputBytes: 1_000_000,
    auditLogPath: 'secureshell_audit.jsonl',
    auditQueueSize: 1000,
    allowlist: [],
    blocklist: [],
    osInfo: undefined
};

/**
 * Load configuration from environment variables and YAML file
 */
export function loadConfig(configPath?: string): SecureShellConfig {
    const config: SecureShellConfig = { ...DEFAULT_CONFIG };

    // Load from environment variables (with SECURESHELL_ prefix)
    if (process.env.SECURESHELL_DEBUG_MODE) {
        config.debugMode = process.env.SECURESHELL_DEBUG_MODE === 'true';
    }

    if (process.env.SECURESHELL_PROVIDER) {
        config.provider = process.env.SECURESHELL_PROVIDER;
    }

    // API Keys
    config.openaiApiKey = process.env.SECURESHELL_OPENAI_API_KEY || process.env.OPENAI_API_KEY;
    config.anthropicApiKey = process.env.SECURESHELL_ANTHROPIC_API_KEY || process.env.ANTHROPIC_API_KEY;
    config.geminiApiKey = process.env.SECURESHELL_GEMINI_API_KEY || process.env.GEMINI_API_KEY;
    config.groqApiKey = process.env.SECURESHELL_GROQ_API_KEY || process.env.GROQ_API_KEY;
    config.deepseekApiKey = process.env.SECURESHELL_DEEPSEEK_API_KEY || process.env.DEEPSEEK_API_KEY;

    if (process.env.SECURESHELL_DEFAULT_TIMEOUT_SECONDS) {
        config.defaultTimeoutSeconds = parseInt(process.env.SECURESHELL_DEFAULT_TIMEOUT_SECONDS, 10);
    }

    if (process.env.SECURESHELL_OS_INFO) {
        config.osInfo = process.env.SECURESHELL_OS_INFO;
    }

    // Load from YAML file
    const yamlPath = configPath || path.join(process.cwd(), 'secureshell.yaml');

    if (fs.existsSync(yamlPath)) {
        try {
            const yamlContent = fs.readFileSync(yamlPath, 'utf8');
            const yamlData = yaml.load(yamlContent) as any;

            if (yamlData.allowlist && Array.isArray(yamlData.allowlist)) {
                config.allowlist = yamlData.allowlist;
            }

            if (yamlData.blocklist && Array.isArray(yamlData.blocklist)) {
                config.blocklist = yamlData.blocklist;
            }

            if (yamlData.os_info) {
                config.osInfo = yamlData.os_info;
            }

            if (yamlData.debug_mode !== undefined) {
                config.debugMode = yamlData.debug_mode;
            }

        } catch (error) {
            console.warn(`⚠️  Failed to load ${yamlPath}:`, error);
        }
    }

    // Auto-detect OS if not set
    if (!config.osInfo) {
        const platform = os.platform();
        const release = os.release();
        config.osInfo = `${config.environment} ${platform} ${release}`;
    }

    return config;
}

/**
 * Debug print configuration
 */
export function debugConfig(config: SecureShellConfig): void {
    if (config.debugMode) {
        console.log('[SecureShell Config]', {
            provider: config.provider,
            osInfo: config.osInfo,
            allowlist: config.allowlist,
            blocklist: config.blocklist,
            hasOpenAIKey: !!config.openaiApiKey,
            hasAnthropicKey: !!config.anthropicApiKey,
            hasGeminiKey: !!config.geminiApiKey
        });
    }
}
