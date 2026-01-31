"""Find the correct way to generate Composio auth URLs"""
from composio import Composio
import os
from dotenv import load_dotenv

load_dotenv()

client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

print("Exploring Composio API for auth URL generation...\n")

# Check if there's an integrations API
if hasattr(client, 'integrations'):
    print("✓ Has 'integrations' attribute")
    print(f"  Methods: {[x for x in dir(client.integrations) if not x.startswith('_')]}")
    
    try:
        # Try to get a specific integration
        integ = client.integrations.get(integration_id="GOOGLECALENDAR")
        print(f"\n✓ Got integration: {type(integ)}")
        print(f"  Attributes: {[x for x in dir(integ) if not x.startswith('_')]}")
    except Exception as e:
        print(f"\n✗ integrations.get failed: {e}")

# Check connected_accounts for other methods
if hasattr(client, 'connected_accounts'):
    print("\n✓ Has 'connected_accounts' attribute")
    methods = [x for x in dir(client.connected_accounts) if not x.startswith('_') and callable(getattr(client.connected_accounts, x))]
    print(f"  Methods: {methods}")
    
    # Look for any 'get_url' or 'generate' methods
    url_methods = [m for m in methods if 'url' in m.lower() or 'link' in m.lower() or 'auth' in m.lower()]
    if url_methods:
        print(f"  URL-related methods: {url_methods}")

# Check if there's an apps or toolkits method that gives us connection info
if hasattr(client, 'apps'):
    print("\n✓ Has 'apps' attribute")
    print(f"  Methods: {[x for x in dir(client.apps) if not x.startswith('_')]}")
