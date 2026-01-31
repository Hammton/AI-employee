"""Try experimental API"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio

ENTITY_ID = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
session = composio.create(user_id=ENTITY_ID)

print("Checking session.experimental...\n")
print(f"Experimental methods: {[x for x in dir(session.experimental) if not x.startswith('_')]}\n")

# Try to get tools with experimental
try:
    exp_tools = session.experimental.tools(toolkits=["gmail"])
    print(f"✅ Got {len(exp_tools)} tools from experimental")
    for i, tool in enumerate(exp_tools[:5], 1):
        print(f"{i}. {tool.get('function', {}).get('name')}")
except Exception as e:
    print(f"❌ Experimental failed: {e}")

# Try direct toolkit access
print("\nTrying direct toolkit methods...")
print(f"Session methods: {[x for x in dir(session) if not x.startswith('_')]}")
