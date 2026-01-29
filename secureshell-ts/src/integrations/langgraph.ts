/**
 * LangGraph Integration for SecureShell TypeScript SDK
 * 
 * Provides utility functions to create LangGraph-compatible tools from SecureShell instances.
 * LangGraph uses standard LangChain tools, so this re-exports the LangChain tool creator.
 */

export { createSecureShellTool } from './langchain';
