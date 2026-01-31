from composio import Composio
import os
from dotenv import load_dotenv

load_dotenv()

client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

print("Testing connected_accounts.initiate...")
try:
    # Attempt to initiate connection
    # Usually takes integration_id/app_name and user_uuid/entity_id
    # We want to use 'default_user' as our entity
    
    # Check initiate signature or try calling it
    if hasattr(client.connected_accounts, 'initiate'):
        res = client.connected_accounts.initiate(
            app="googlecalendar",
            entity_id="default_user"  # or user_uuid
            # redirect_url might be optional
        )
        print(f"Result: {res}")
        if hasattr(res, 'redirect_url'):
            print(f"URL: {res.redirect_url}")
    else:
        print("No initiate method on connected_accounts")
        print(dir(client.connected_accounts))

except Exception as e:
    print(f"Error: {e}")
