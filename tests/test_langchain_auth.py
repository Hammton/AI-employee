from composio_langchain import ComposioToolSet, App
import os
from dotenv import load_dotenv

load_dotenv()

toolset = ComposioToolSet(api_key=os.getenv("COMPOSIO_API_KEY"))

print("Testing ComposioToolSet auth url generation...")
try:
    # Look for auth methods
    print(f"Dir: {[x for x in dir(toolset) if not x.startswith('_')]}")

    # Sometimes it's toolset.client.connected_accounts.initiate(...)
    # Or get_auth_url(...)
except Exception as e:
    print(e)
