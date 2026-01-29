/**
 * Model Context Protocol (MCP) Integration Example
 * 
 * Demonstrates how to create an MCP server that exposes SecureShell
 * as a tool for Claude Desktop and other MCP clients.
 * 
 * Usage:
 *   export OPENAI_API_KEY=sk-...
 *   npx tsx examples/secureshell-ts/mcp_server.ts
 */

import 'dotenv/config';
import { SecureShell, OpenAIProvider, createSecureShellMCPTool } from 'secureshell-ts';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

// Initialize SecureShell with debug mode (logs to stderr for MCP)
const shell = new SecureShell({
    provider: new OpenAIProvider({
        apiKey: process.env.OPENAI_API_KEY!,
        model: 'gpt-4.1-mini'
    }),
    template: 'development',
    config: { debugMode: true }  // Enable debug logging
});

// Create MCP server
const server = new Server(
    {
        name: 'secureshell-mcp',
        version: '0.1.0',
    },
    {
        capabilities: {
            tools: {},
        },
    }
);

// Get tool definition from SDK
const shellTool = createSecureShellMCPTool(shell);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [
            {
                name: shellTool.name,
                description: shellTool.description,
                inputSchema: shellTool.inputSchema
            }
        ]
    };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    if (request.params.name === 'execute_shell_command') {
        const { command, reasoning } = request.params.arguments as {
            command: string;
            reasoning: string;
        };

        return shellTool.executor({ command, reasoning });
    }

    throw new Error(`Unknown tool: ${request.params.name}`);
});

// Start server
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error('✅ SecureShell MCP server running on stdio');
}

main().catch(console.error);
