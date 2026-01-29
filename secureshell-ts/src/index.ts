/**
 * Main exports for SecureShell TypeScript SDK
 */

export { SecureShell } from './SecureShell';

// Core types
export {
    RiskTier,
    GatekeeperDecision,
    ExecutionResult,
    GatekeeperResponse,
    SecurityContext,
    SecureShellConfig,
    SecurityTemplate
} from './models/types';

// Providers
export {
    BaseLLMProvider,
    OpenAIProvider,
    OpenAITools,
    AnthropicProvider,
    AnthropicTools,
    GeminiProvider,
    GeminiTools,
    DeepSeekProvider,
    GroqProvider,
    OllamaProvider,
    LlamaCppProvider
} from './providers';

// Templates
export { getTemplate, listTemplates, TEMPLATES } from './config/templates';

// Config
export { loadConfig } from './config/loader';

// Integrations
export { createSecureShellTool } from './integrations/langchain';
export { createSecureShellMCPTool } from './integrations/mcp';
