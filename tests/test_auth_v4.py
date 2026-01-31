from composio import Composio
import os
from dotenv import load_dotenv

load_dotenv()

client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

# Method 3: Direct slug usage
print("Trying with auth_config_id='googlecalendar'")
try:
    res = client.connected_accounts.initiate(
        user_id="default_user",
        auth_config_id="googlecalendar"
    )
    print(f"Result: {res}")
    if hasattr(res, 'redirect_url'):
        print(f"URL: {res.redirect_url}")
except Exception as e:
    print(f"Error: {e}")

# Method 4: List integrations/auth_configs?
print("\nListing auth configs (integrations)...")
try:
    # client.apps? client.integrations? client.toolkits?
    # client.toolkits.list() we used before
    toolkits = client.toolkits.list()
    for tk in toolkits:
        # Check if tk has auth_config_id or similar
        # Expected: tk.slug == 'googlecalendar'
        if tk.slug == 'googlecalendar' or tk.slug == 'GOOGLECALENDAR':
             print(f"Found toolkit: {tk}")
             print(f"Dir: {dir(tk)}")
except Exception as e:
    print(f"Error listing toolkits: {e}")
