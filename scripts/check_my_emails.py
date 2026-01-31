"""Check Gmail with correct entity_id"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

print("=" * 60)
print("CHECKING YOUR GMAIL")
print("=" * 60)

# Use the correct entity_id from your Gmail connection
ENTITY_ID = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
session = composio.create(user_id=ENTITY_ID)
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
    system_prompt="You are a helpful email assistant with access to Gmail tools."
)

print(f"\n✅ Agent ready")
print(f"   Entity: {ENTITY_ID}")
print(f"   Tools: {len(tools)}\n")

# Ask to check emails
query = "Check my latest 3 Gmail emails and tell me who they're from and what they're about."

print(f"Query: {query}\n")
print("=" * 60)

result = agent.invoke({"messages": [{"role": "user", "content": query}]})

print("\n" + "=" * 60)
print("RESPONSE:")
print("=" * 60)
print(f"\n{result['messages'][-1].content}\n")
print("=" * 60)
