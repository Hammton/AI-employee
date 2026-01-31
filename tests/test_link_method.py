"""Test the connected_accounts.link method"""
from composio import Composio
import os
from dotenv import load_dotenv
import inspect

load_dotenv()

client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

print("Testing connected_accounts.link method\n")

# Get the signature
try:
    sig = inspect.signature(client.connected_accounts.link)
    print(f"Signature: {sig}")
except Exception as e:
    print(f"Could not get signature: {e}")

# Try calling it
print("\nTrying to call link...")
try:
    result = client.connected_accounts.link(
        integration_id="GOOGLECALENDAR",
        user_id="default_user"
    )
    print(f"✓ Success!")
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    
    # Check for URL attribute
    if hasattr(result, 'url'):
        print(f"\n✓ URL: {result.url}")
    elif hasattr(result, 'link'):
        print(f"\n✓ Link: {result.link}")
    elif hasattr(result, 'redirect_url'):
        print(f"\n✓ Redirect URL: {result.redirect_url}")
    else:
        attrs = [x for x in dir(result) if not x.startswith('_')]
        print(f"\nAttributes: {attrs}")
        
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()
