"""Check Gmail emails with connected account"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

print("=" * 60)
print("CHECKING GMAIL EMAILS")
print("=" * 60)

# Setup with your connected account
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
    system_prompt="You are a helpful email assistant. Use available tools to help users with their emails."
)

print(f"\n✅ Agent ready with {len(tools)} tools")
print(f"   Using entity: test_user\n")

# Ask to check emails
query = "Please check my latest 5 Gmail emails and summarize them for me."

print(f"Query: {query}\n")
print("=" * 60)
print("AGENT WORKING...")
print("=" * 60)

# Stream to see progress
for chunk in agent.stream({"messages": [{"role": "user", "content": query}]}, stream_mode="updates"):
    for node, updates in chunk.items():
        if node == "model":
            if 'messages' in updates:
                for msg in updates['messages']:
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tc in msg.tool_calls:
                            print(f"\n🔧 Calling tool: {tc.get('name')}")
        elif node == "tools":
            if 'messages' in updates:
                for msg in updates['messages']:
                    if hasattr(msg, 'name'):
                        print(f"✅ {msg.name} completed")

# Get final result
result = agent.invoke({"messages": [{"role": "user", "content": query}]})
final_response = result['messages'][-1].content

print("\n" + "=" * 60)
print("FINAL RESPONSE:")
print("=" * 60)
print(f"\n{final_response}\n")
print("=" * 60)
