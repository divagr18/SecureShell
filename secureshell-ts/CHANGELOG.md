# Changelog

All notable changes to SecureShell TypeScript SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-30

### Added
- Initial release of SecureShell TypeScript SDK
- Core security features:
  - AI-powered gatekeeper for command evaluation
  - Risk classification (GREEN, YELLOW, RED)
  - Sandbox validation for path restrictions  
  - Audit logging with JSONL format
  - Command execution with timeout support
- 7 LLM provider integrations:
  - OpenAI (GPT-4, GPT-4o, etc.)
  - Anthropic (Claude)
  - Google Gemini
  - DeepSeek
  - Groq
  - Ollama (local)
  - LlamaCpp (local)
- Platform-aware command evaluation:
  - Automatic OS detection (Windows, macOS, Linux)
  - Platform-specific gatekeeper guidance
  - Blocks incompatible commands (e.g., Unix commands on Windows)
  - Agent self-correction on command denial
- Integration support:
  - LangChain tool integration
  - LangGraph workflow support
  - MCP (Model Context Protocol) server
- Security templates:
  - Paranoid (maximum security)
  - Production (balanced)
  - Development (flexible)
  - CI/CD (automation-friendly)
- Configuration options:
  - YAML configuration file support
  - Environment variable override
  - Programmatic configuration
  - Allowlist/blocklist for commands
- Comprehensive examples:
  - Provider examples for all 7 LLMs
  - Integration demos (LangChain, LangGraph, MCP)
  - Feature demonstrations
- Full TypeScript support with type definitions
- Dual-format distribution (CommonJS and ESM)

### Security
- Gatekeeper prevents injection attacks through structured prompts
- Risk-based command classification
- Configurable security profiles
- Audit trail for all command executions
