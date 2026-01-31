
import os
from dotenv import load_dotenv
from composio import Composio
from composio_langchain import ComposioToolSet, App

load_dotenv()
api_key = os.getenv("COMPOSIO_API_KEY")

print("--- Inspecting Composio Client ---")
client = Composio(api_key=api_key)
print(f"Client attributes: {[x for x in dir(client) if not x.startswith('_')]}")

print("\n--- Testing ComposioToolSet (LangChain) ---")
try:
    toolset = ComposioToolSet(api_key=api_key)
    print("Toolset created.")
    
    # Try fetching GMAIL tools
    print("Fetching GMAIL tools...")
    tools = toolset.get_tools(apps=[App.GMAIL])
    print(f"✅ Success! Found {len(tools)} tools.")
    
except Exception as e:
    print(f"❌ Error with ToolSet: {e}")

print("\n--- Inspecting App Enum ---")
count = 0
for x in dir(App):
    if not x.startswith('_') and x.isupper():
        count += 1
print(f"Found {count} apps in App enum.")
