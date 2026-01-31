
import os
import sys
from dotenv import load_dotenv
load_dotenv()

from composio_langchain import ComposioToolSet, App
import logging

logging.basicConfig(level=logging.INFO)

print("Testing Composio Tool Connection...")
api_key = os.getenv("COMPOSIO_API_KEY")
print(f"Key: {api_key[:5]}...")

try:
    toolset = ComposioToolSet(api_key=api_key)
    print("Instance created.")
    
    print("Fetching GMAIL tools...")
    tools = toolset.get_tools(apps=[App.GMAIL])
    print(f"✅ Success! Got {len(tools)} tools.")
    for t in tools[:3]:
        print(f" - {t.name}")

except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
