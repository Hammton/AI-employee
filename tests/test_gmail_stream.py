"""Test Gmail connection with streaming to see all steps"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

print("=" * 60)
print("GMAIL CONNECTION TEST (STREAMING)")
print("=" * 60)

# Setup
composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
session = composio.create(user_id="test_user")
tools = session.tools()

llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL"),
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful assistant. When asked to connect to services, use COMPOSIO_SEARCH_TOOLS first, then COMPOSIO_MANAGE_CONNECTIONS."
)

print(f"\n✅ Agent ready\n")

query = "I need to check my Gmail. Please search for Gmail tools and help me connect."

print(f"Query: {query}\n")
print("=" * 60)
print("STREAMING AGENT EXECUTION:")
print("=" * 60)

# Stream to see each step
for chunk in agent.stream({"messages": [{"role": "user", "content": query}]}, stream_mode="updates"):
    for node, updates in chunk.items():
        print(f"\n[{node.upper()}]")
        if 'messages' in updates:
            for msg in updates['messages']:
                msg_type = getattr(msg, 'type', 'unknown')
                
                if msg_type == 'ai':
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tc in msg.tool_calls:
                            print(f"  🔧 Calling: {tc.get('name')}")
                    if hasattr(msg, 'content') and msg.content:
                        print(f"  💬 {msg.content[:200]}")
                        
                elif msg_type == 'tool':
                    tool_name = getattr(msg, 'name', 'unknown')
                    content = msg.content
                    print(f"  ✅ {tool_name} result:")
                    if len(content) > 300:
                        print(f"     {content[:300]}...")
                    else:
                        print(f"     {content}")

print("\n" + "=" * 60)
print("💡 Look for connection URLs or Gmail tool information above")
