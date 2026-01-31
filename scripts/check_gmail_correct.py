"""Check Gmail with Composio v0.7.21 - Correct API"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

print("=" * 60)
print("CHECKING GMAIL - CORRECT API")
print("=" * 60)

# Your entity ID from the connected account
ENTITY_ID = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"

# Initialize Composio
composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

# Get entity (user session)
print("\nGetting entity...")
entity = composio.get_entity(id=ENTITY_ID)

# Get Gmail connection
print("Getting Gmail connection...")
connection = entity.get_connection(app="gmail")
print(f"Connection ID: {connection.id}")
print(f"Connection status: {connection.status}")

# Get tools from composio.apps
print("\nFetching Gmail tools...")
from composio.client.enums import App
tools = composio.apps.get_tools(apps=[App.GMAIL], entity_id=ENTITY_ID)

print(f"✅ Got {len(tools)} Gmail tools\n")

# Show first few tools
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
        "content": "Check my latest 3 emails and tell me who they're from and what they're about"
    }]
})

print("\n" + "=" * 60)
print("RESPONSE:")
print("=" * 60)
print(f"\n{result['messages'][-1].content}\n")
print("=" * 60)
