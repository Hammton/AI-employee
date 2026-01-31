"""Test using LangchainProvider properly"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio
from composio_langchain import LangchainProvider

ENTITY_ID = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

# Create provider
provider = LangchainProvider(composio=composio)

print("Checking provider methods...\n")
print(f"Provider methods: {[x for x in dir(provider) if not x.startswith('_')]}\n")

# Check if provider has a way to get tools for specific toolkit
print("Trying to get tools via provider...\n")

# The provider might need to be used differently
# Let's check the runtime
print(f"Provider runtime: {provider.runtime}")
print(f"Runtime type: {type(provider.runtime)}")
print(f"Runtime methods: {[x for x in dir(provider.runtime) if not x.startswith('_')]}\n")

# Try to get tools from runtime
try:
    # Maybe runtime has tools method
    if hasattr(provider.runtime, 'get_tools'):
        tools = provider.runtime.get_tools(entity_id=ENTITY_ID, toolkits=["gmail"])
        print(f"✅ Got {len(tools)} tools")
    else:
        print("No get_tools on runtime")
except Exception as e:
    print(f"❌ Error: {e}")
