"""Test Gmail connection with Composio"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

print("=" * 60)
print("GMAIL CONNECTION TEST")
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
    system_prompt="You are a helpful assistant. When asked to connect to services, use COMPOSIO_SEARCH_TOOLS first to find available tools, then COMPOSIO_MANAGE_CONNECTIONS to create connections."
)

print(f"\n✅ Agent ready with {len(tools)} tools\n")

# Ask agent to search for Gmail tools
print("Asking agent to search for Gmail tools and connect...\n")
print("=" * 60)

query = """
I need to check my Gmail emails. Please:
1. First search for Gmail tools using COMPOSIO_SEARCH_TOOLS
2. Then help me connect to Gmail using COMPOSIO_MANAGE_CONNECTIONS
"""

result = agent.invoke({"messages": [{"role": "user", "content": query}]})

print("\n" + "=" * 60)
print("AGENT RESPONSE:")
print("=" * 60)

# Show all messages to see tool calls
messages = result['messages']
for i, msg in enumerate(messages):
    msg_type = getattr(msg, 'type', 'unknown')
    
    if msg_type == 'human':
        print(f"\n[USER]")
        print(msg.content)
    elif msg_type == 'ai':
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            print(f"\n[AI - CALLING TOOLS]")
            for tc in msg.tool_calls:
                print(f"  Tool: {tc.get('name', 'unknown')}")
                print(f"  Args: {tc.get('args', {})}")
        if hasattr(msg, 'content') and msg.content:
            print(f"\n[AI - RESPONSE]")
            print(msg.content)
    elif msg_type == 'tool':
        print(f"\n[TOOL RESULT - {getattr(msg, 'name', 'unknown')}]")
        content = msg.content
        if len(content) > 500:
            print(content[:500] + "...")
        else:
            print(content)

print("\n" + "=" * 60)
print("\n💡 Look for a connection URL in the response above.")
print("   Click it to authorize Gmail access, then you can check emails!")
