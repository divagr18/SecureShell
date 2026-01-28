"""
LangGraph Integration Example
------------------------------
Demonstrates using SecureShell with LangGraph agent.

Prerequisites:
    pip install langgraph langchain-openai

Usage:
    export OPENAI_API_KEY=sk-...
    python examples/langgraph_example.py
"""
import asyncio
import os
from typing import TypedDict

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from secureshell import SecureShell
from secureshell.providers.openai import OpenAI
from secureshell.integrations.langchain import create_secureshell_tool


class AgentState(TypedDict):
    """State for the agent workflow."""
    messages: list
    iterations: int


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        return print("❌ Set OPENAI_API_KEY")
    
    print("🚀 LangGraph Agent + SecureShell Demo\n")
    
    # Setup SecureShell
    shell = SecureShell(
        provider=OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4.1-mini"
        )
    )
    shell.config.debug_mode = True
    
    # Create tool
    tool = create_secureshell_tool(shell)
    tools = [tool]
    
    print(f"📋 Tools: {[t.name for t in tools]}\n")
    
    # Setup LLM with tools
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
    llm_with_tools = llm.bind_tools(tools)
    
    # Define agent node
    async def agent_node(state: AgentState) -> AgentState:
        """Agent decision node."""
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {
            "messages": messages + [response],
            "iterations": state["iterations"] + 1
        }
    
    # Define tool execution node
    async def tool_node(state: AgentState) -> AgentState:
        """Execute tools."""
        messages = state["messages"]
        last_message = messages[-1]
        
        tool_results = []
        for tool_call in last_message.tool_calls:
            # Execute tool
            result = await tool._arun(
                command=tool_call["args"]["command"],
                reasoning=tool_call["args"]["reasoning"]
            )
            
            # Create tool message
            tool_results.append(
                ToolMessage(
                    content=result,
                    tool_call_id=tool_call["id"]
                )
            )
        
        return {
            "messages": messages + tool_results,
            "iterations": state["iterations"]
        }
    
    # Define conditional edge
    def should_continue(state: AgentState) -> str:
        """Decide whether to continue or end."""
        last_message = state["messages"][-1]
        
        # If no tool calls or max iterations, end
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return "end"
        if state["iterations"] >= 5:
            return "end"
        
        return "continue"
    
    # Build graph
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END
        }
    )
    
    workflow.add_edge("tools", "agent")
    
    app = workflow.compile()
    
    # Run agent
    print("💬 User: List all Python files in the current directory\n")
    
    result = await app.ainvoke({
        "messages": [
            HumanMessage(content="List all Python files in the current directory")
        ],
        "iterations": 0
    })
    
    # Get final response
    final_message = result["messages"][-1]
    if isinstance(final_message, AIMessage):
        print(f"\n🤖 Agent: {final_message.content}\n")
    
    print(f"Total iterations: {result['iterations']}")
    
    await shell.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
