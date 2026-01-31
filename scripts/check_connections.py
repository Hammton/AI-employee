from composio import Composio
import os
from dotenv import load_dotenv

load_dotenv()

client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

try:
    response = client.connected_accounts.list()
    if hasattr(response, 'items'):
        for item in response.items:
            print(f"--- Item ---")
            print(f"Dir: {[x for x in dir(item) if not x.startswith('_')]}")
            # Try to print everything
            print(f"Dump: {item}")
except Exception as e:
    print(e)
