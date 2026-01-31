"""Get Gmail-specific tools"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio

ENTITY_ID = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

print("Getting tools for Gmail toolkit...\n")

# Create session and request Gmail tools specifically
session = composio.create(user_id=ENTITY_ID)

# Get tools with toolkit filter
tools = session.tools(toolkits=["gmail"])

print(f"✅ Got {len(tools)} Gmail tools:\n")

for i, tool in enumerate(tools[:10], 1):
    tool_name = tool.get('function', {}).get('name', 'Unknown')
    tool_desc = tool.get('function', {}).get('description', '')[:100]
    print(f"{i}. {tool_name}")
    print(f"   {tool_desc}...\n")
