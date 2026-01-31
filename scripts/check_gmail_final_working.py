"""Check Gmail with Composio v0.11.0 - Using correct import"""
import os
from dotenv import load_dotenv

load_dotenv()

# Use the new composio package (not composio-core)
from composio import Composio
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

print("=" * 60)
print("CHECKING GMAIL WITH COMPOSIO v0.11.0")
print("=" * 60)

# Your entity ID
ENTITY_ID = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"

# Initialize Composio (new API)
composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

# Get Gmail tools for this user
print("\nFetching Gmail tools...")
tools = composio.tools.get(
    user_id=ENTITY_ID,
    toolkits=["gmail"],
    limit=10
)

print(f"✅ Got {len(tools)} Gmail tools\n")

# Show tools
for i, tool in enumerate(tools[:5], 1):
    tool_name = tool.get('function', {}).get('name', 'Unknown')
    print(f"{i}. {tool_name}")

# Create LLM
llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL"),
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
)

# Create agent
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful email assistant."
)

print("\n✅ Agent created!")
print("\nAsking agent to check emails...\n")
print("=" * 60)

# Ask to check emails
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Check my latest 3 emails and tell me who they're from"
    }]
})

print("\n" + "=" * 60)
print("RESPONSE:")
print("=" * 60)
print(f"\n{result['messages'][-1].content}\n")
print("=" * 60)
