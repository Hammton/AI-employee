"""Check Gmail with Composio v0.5.51 (working version)"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio_langchain import ComposioToolSet, App
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

print("=" * 60)
print("CHECKING GMAIL WITH COMPOSIO v0.5.51")
print("=" * 60)

# Setup toolset with entity
ENTITY_ID = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"

toolset = ComposioToolSet(
    api_key=os.getenv("COMPOSIO_API_KEY"),
    entity_id=ENTITY_ID
)

# Get Gmail tools
print("\nFetching Gmail tools...")
tools = toolset.get_tools(apps=[App.GMAIL])
print(f"✅ Got {len(tools)} Gmail tools\n")

for i, tool in enumerate(tools[:5], 1):
    print(f"{i}. {tool.name}")

# Create agent
llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL"),
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful email assistant."
)

print("\n✅ Agent created!")
print("\nAsking agent to check emails...\n")
print("=" * 60)

result = agent.invoke({"messages": [{"role": "user", "content": "Check my latest 3 emails and summarize them"}]})

print("\n" + "=" * 60)
print("RESPONSE:")
print("=" * 60)
print(f"\n{result['messages'][-1].content}\n")
print("=" * 60)
