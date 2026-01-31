from composio import Composio
import os
import inspect
from dotenv import load_dotenv

load_dotenv()

client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

try:
    print("Signature of initiate:")
    print(inspect.signature(client.connected_accounts.initiate))
except Exception as e:
    print(f"Could not get signature: {e}")

print("\nTrying with integration_id...")
try:
    res = client.connected_accounts.initiate(
        integration_id="googlecalendar",
        entity_id="default_user"
    )
    print(f"Result: {res}")
    print(f"Dir Res: {dir(res)}")
    if hasattr(res, 'redirect_url'):
        print(f"URL: {res.redirect_url}")
except Exception as e:
    print(f"Error with integration_id: {e}")
