/**
 * MCP Agent Demo - AI Agent using SecureShell via MCP
 * 
 * Demonstrates an AI agent using the MCP server to execute commands.
 * Debug mode handles all logging automatically.
 * 
 * Usage:
 *   export OPENAI_API_KEY=sk-...
 *   npx tsx mcp_client_demo.ts
 */

import 'dotenv/config';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import OpenAI from 'openai';

async function main() {
    if (!process.env.OPENAI_API_KEY) {
        console.error('❌ Set OPENAI_API_KEY');
        return;
    }

    // Connect to MCP server
    const transport = new StdioClientTransport({
        command: 'npx',
        args: ['tsx', 'mcp_server.ts'],
        env: { ...process.env }
    });

    const mcpClient = new Client({
        name: 'secureshell-agent',
        version: '0.1.0'
    }, { capabilities: {} });

    await mcpClient.connect(transport);

    // Get MCP tools
    const mcpTools = await mcpClient.listTools();

    // Convert to OpenAI tool format
    const tools: OpenAI.Chat.Completions.ChatCompletionTool[] = mcpTools.tools.map(tool => ({
        type: 'function',
        function: {
            name: tool.name,
            description: tool.description,
            parameters: tool.inputSchema
        }
    }));

    // Initialize OpenAI agent
    const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

    const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
        {
            role: 'user',
            content: 'List the files in the current directory, then read the package.json file and tell me the project name.'
        }
    ];

    console.log('🤖 Agent task: List files and read package.json\n');

    // Agent loop
    for (let turn = 0; turn < 5; turn++) {
        const response = await openai.chat.completions.create({
            model: 'gpt-4o-mini',
            messages: messages,
            tools: tools
        });

        const message = response.choices[0].message;
        messages.push(message);

        if (message.tool_calls) {
            console.log(`\nTurn ${turn + 1}: Agent calling ${message.tool_calls.length} tool(s)...`);

            for (const toolCall of message.tool_calls) {
                if (toolCall.type === 'function') {
                    const args = JSON.parse(toolCall.function.arguments);
                    console.log(`  Tool: ${toolCall.function.name}`);
                    console.log(`  Args: ${JSON.stringify(args)}`);

                    // Call MCP server
                    const result = await mcpClient.callTool({
                        name: toolCall.function.name,
                        arguments: args
                    });

                    messages.push({
                        role: 'tool',
                        tool_call_id: toolCall.id,
                        content: (result.content[0] as any).text
                    });
                }
            }
        } else if (message.content) {
            console.log(`\n✅ Agent response: ${message.content}\n`);
            break;
        }
    }

    await mcpClient.close();
}

main().catch(console.error);
