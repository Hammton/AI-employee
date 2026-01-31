"""Test link with app slug as auth_config_id"""
from composio import Composio
import os
from dotenv import load_dotenv

load_dotenv()

client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

print("Testing link with different auth_config_id formats\n")

test_ids = [
    "googlecalendar",
    "GOOGLECALENDAR",
    "google_calendar",
]

for test_id in test_ids:
    print(f"\nTrying auth_config_id='{test_id}'...")
    try:
        result = client.connected_accounts.link(
            user_id="default_user",
            auth_config_id=test_id
        )
        print(f"  ✓ Success!")
        print(f"  Type: {type(result)}")
        
        # Try to get URL
        attrs = [x for x in dir(result) if not x.startswith('_')]
        print(f"  Attributes: {attrs}")
        
        # Check common URL attributes
        for attr in ['url', 'link', 'redirect_url', 'connection_url', 'auth_url']:
            if hasattr(result, attr):
                val = getattr(result, attr)
                print(f"  ✓ {attr}: {val}")
                break
        else:
            print(f"  Full object: {result}")
            
        break  # Stop on first success
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
