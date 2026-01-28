"""
LangGraph Integration for SecureShell
--------------------------------------
Provides nodes and utilities for integrating SecureShell into LangGraph workflows.
"""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from secureshell import SecureShell
from secureshell.models import ExecutionResult


class ShellState(TypedDict):
    """State for shell execution workflow."""
    command: str
    reasoning: str
    result: dict
    success: bool
    messages: list


async def execute_shell_node(state: ShellState, shell: SecureShell) -> ShellState:
    """
    LangGraph node for executing shell commands via SecureShell.
    
    Args:
        state: Current graph state
        shell: SecureShell instance
        
    Returns:
        Updated state with execution result
    """
    command = state.get("command", "")
    reasoning = state.get("reasoning", "")
    
    result = await shell.execute(command=command, reasoning=reasoning)
    
    # Update state
    state["result"] = {
        "success": result.success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "denial_reason": result.denial_reason
    }
    state["success"] = result.success
    
    # Add to messages if present
    if "messages" in state:
        state["messages"].append({
            "role": "tool",
            "content": result.stdout if result.success else result.denial_reason
        })
    
    return state


def create_shell_node(shell: SecureShell):
    """
    Create a LangGraph node function for SecureShell.
    
    Args:
        shell: Configured SecureShell instance
        
    Returns:
        Node function ready to use in LangGraph
        
    Example:
        >>> from langgraph.graph import StateGraph
        >>> from secureshell import SecureShell
        >>> from secureshell.providers.openai import OpenAI
        >>> from secureshell.integrations.langgraph import create_shell_node, ShellState
        >>> 
        >>> shell = SecureShell(provider=OpenAI(api_key="..."))
        >>> shell_node = create_shell_node(shell)
        >>> 
        >>> # Create graph
        >>> workflow = StateGraph(ShellState)
        >>> workflow.add_node("execute", shell_node)
        >>> workflow.set_entry_point("execute")
        >>> workflow.add_edge("execute", END)
        >>> 
        >>> app = workflow.compile()
        >>> result = await app.ainvoke({
        ...     "command": "ls -la",
        ...     "reasoning": "List directory contents"
        ... })
    """
    async def node_fn(state: ShellState) -> ShellState:
        return await execute_shell_node(state, shell)
    
    return node_fn


def should_retry(state: ShellState) -> str:
    """
    Conditional edge for retry logic.
    
    Returns:
        "retry" if execution failed, "end" if successful
    """
    return "end" if state.get("success", False) else "retry"


def create_shell_workflow(shell: SecureShell) -> StateGraph:
    """
    Create a complete LangGraph workflow with SecureShell.
    
    Args:
        shell: Configured SecureShell instance
        
    Returns:
        Compiled LangGraph workflow
        
    Example:
        >>> shell = SecureShell(provider=OpenAI(api_key="..."))
        >>> workflow = create_shell_workflow(shell)
        >>> result = await workflow.ainvoke({
        ...     "command": "echo test",
        ...     "reasoning": "Testing"
        ... })
    """
    workflow = StateGraph(ShellState)
    
    # Add nodes
    shell_node = create_shell_node(shell)
    workflow.add_node("execute", shell_node)
    
    # Set entry point
    workflow.set_entry_point("execute")
    
    # Add edge to end
    workflow.add_edge("execute", END)
    
    return workflow.compile()
