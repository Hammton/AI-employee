"""Debug Gmail check with streaming"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

USER_ID = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
session = composio.create(user_id=USER_ID)
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
    system_prompt="You are a helpful assistant. Use COMPOSIO_SEARCH_TOOLS to find Gmail tools, then use them to check emails."
)

print("Streaming agent execution...\n")
print("=" * 60)

query = "Check my Gmail emails"

for chunk in agent.stream({"messages": [{"role": "user", "content": query}]}, stream_mode="updates"):
    for node, updates in chunk.items():
        print(f"\n[{node.upper()}]")
        if 'messages' in updates:
            for msg in updates['messages']:
                msg_type = getattr(msg, 'type', 'unknown')
                
                if msg_type == 'ai':
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        print("  Tool calls:")
                        for tc in msg.tool_calls:
                            print(f"    - {tc.get('name')}")
                            print(f"      Args: {tc.get('args')}")
                    if hasattr(msg, 'content') and msg.content:
                        print(f"  Content: {msg.content}")
                        
                elif msg_type == 'tool':
                    tool_name = getattr(msg, 'name', 'unknown')
                    content = str(msg.content)[:200]
                    print(f"  Tool: {tool_name}")
                    print(f"  Result: {content}...")

print("\n" + "=" * 60)
