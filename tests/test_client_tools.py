"""Try getting tools via client instead of session"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio

ENTITY_ID = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

print("Checking composio.client methods...\n")
client_methods = [x for x in dir(composio.client) if not x.startswith('_')]
print(f"Client methods: {client_methods}\n")

# Try to get actions/tools
print("Trying composio.client.tools...")
tools_api = composio.client.tools
print(f"Tools API methods: {[x for x in dir(tools_api) if not x.startswith('_')]}\n")

# Try to list Gmail tools
try:
    # Try without arguments first
    all_tools_list = tools_api.list()
    print(f"✅ Got tools: {len(all_tools_list.items)}\n")
    
    # Filter for Gmail
    gmail_tools = [t for t in all_tools_list.items if 'gmail' in t.name.lower()]
    print(f"Gmail tools: {len(gmail_tools)}\n")
    
    for i, tool in enumerate(gmail_tools[:10], 1):
        print(f"{i}. {tool.name}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
