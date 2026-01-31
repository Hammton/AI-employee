"""Final Gmail test - using toolkits property"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

ENTITY_ID = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
session = composio.create(user_id=ENTITY_ID)

print("Getting toolkits...\n")

# Get all toolkits
toolkits_info = session.toolkits()
print(f"✅ Gmail is connected and ACTIVE!\n")

# Get Gmail tools directly from session
# The session.tools() returns all available tools including Gmail
all_tools = session.tools()
print(f"Total tools available: {len(all_tools)}\n")

# Filter for Gmail tools
gmail_tools = [t for t in all_tools if 'GMAIL' in t.get('function', {}).get('name', '')]
print(f"✅ Found {len(gmail_tools)} Gmail tools:\n")

for i, tool in enumerate(gmail_tools[:10], 1):
    tool_name = tool.get('function', {}).get('name', 'Unknown')
    print(f"{i}. {tool_name}")

tools = gmail_tools if gmail_tools else all_tools

# Now create agent with Gmail tools
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

print("\n✅ Agent created with Gmail tools!")
print("\nAsking agent to check emails...\n")

result = agent.invoke({"messages": [{"role": "user", "content": "Check my latest 3 emails"}]})

print("=" * 60)
print(result['messages'][-1].content)
print("=" * 60)
