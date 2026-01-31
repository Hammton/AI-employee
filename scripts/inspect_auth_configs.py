from composio import Composio
import os
from dotenv import load_dotenv

load_dotenv()

client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

print("Checking for auth_configs attribute...")
if hasattr(client, 'auth_configs'):
    print("Has auth_configs")
    print(f"Methods: {[x for x in dir(client.auth_configs) if not x.startswith('_')]}")
    
    try:
        # Try to list auth configs
        configs = client.auth_configs.list()
        print(f"\nFound {len(configs.items) if hasattr(configs, 'items') else 'unknown'} auth configs")
        
        # Look for googlecalendar
        for config in (configs.items if hasattr(configs, 'items') else configs):
            print(f"\nConfig ID: {config.id if hasattr(config, 'id') else 'unknown'}")
            if hasattr(config, 'app_name'):
                print(f"  App: {config.app_name}")
            if hasattr(config, 'integration_id'):
                print(f"  Integration: {config.integration_id}")
            # Check all attributes
            attrs = [x for x in dir(config) if not x.startswith('_')]
            print(f"  Attrs: {attrs}")
    except Exception as e:
        print(f"Error listing: {e}")
else:
    print("No auth_configs attribute")
    print(f"Available: {[x for x in dir(client) if not x.startswith('_')]}")
