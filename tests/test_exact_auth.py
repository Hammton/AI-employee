from composio import Composio
import os
from dotenv import load_dotenv
import traceback

load_dotenv()

client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

app_name = "Google Calendar"
slug = app_name.lower().replace(" ", "")
print(f"Testing auth for: {slug}")

try:
    if hasattr(client, 'connected_accounts'):
        print("Has connected_accounts")
        
        connection_request = client.connected_accounts.initiate(
            user_id="default_user",
            auth_config_id=slug
        )
        print(f"Got connection_request: {type(connection_request)}")
        print(f"Dir: {[x for x in dir(connection_request) if not x.startswith('_')]}")
        
        if hasattr(connection_request, 'redirect_url'):
            print(f"redirect_url: {connection_request.redirect_url}")
        else:
            print("No redirect_url attribute")
            print(f"Full object: {connection_request}")
    else:
        print("No connected_accounts attribute")
        
except Exception as e:
    print(f"Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
