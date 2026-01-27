"""
Integration helper for OpenAI Function Calling.
"""
from typing import Dict, Any, List

class OpenAIToolGenerator:
    """
    Generates OpenAI-compatible tool definitions for SecureShell.
    """
    @staticmethod
    def get_tool_definition() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "execute_shell_command",
                "description": "Execute a shell command safely. You MUST provide clear reasoning.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The shell command to execute"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Detailed explanation of why this command is necessary",
                            "minLength": 10
                        }
                    },
                    "required": ["command", "reasoning"]
                }
            }
        }
