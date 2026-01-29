"""
LangChain Integration Example
------------------------------
Demonstrates using SecureShell as a LangChain tool.

Prerequisites:
    pip install langchain langchain-openai

Usage:
    export OPENAI_API_KEY=sk-...
    python cookbook/langchain_example.py
"""
import asyncio
import os

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from secureshell import SecureShell
from secureshell.providers.openai import OpenAI
from secureshell.integrations.langchain import create_secureshell_tool


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        return print("❌ Set OPENAI_API_KEY")
    
    print("🚀 LangChain + SecureShell Demo\n")
    
    # Setup SecureShell
    shell = SecureShell(
        provider=OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4.1-mini"
        )
    )
    shell.config.debug_mode = True
    
    # Create LangChain tool
    tool = create_secureshell_tool(shell)
    tools = [tool]
    
    print(f"📋 Tools: {[t.name for t in tools]}\n")
    
    # Setup LangChain agent
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use the shell tool to execute commands."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # Run agent
    print("💬 User: List all Python files in the current directory\n")
    
    result = await agent_executor.ainvoke({
        "input": "List all Python files in the current directory"
    })
    
    print(f"\n🤖 Agent: {result['output']}\n")
    
    await shell.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
