"""Generate Gmail connection URL"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio

print("=" * 60)
print("GMAIL CONNECTION URL GENERATOR")
print("=" * 60)

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

print("\nGenerating Gmail connection URL...\n")

try:
    # Try to initiate connection
    connection_request = composio.connected_accounts.initiate(
        integration_id="gmail",
        entity_id="test_user"
    )
    
    print("✅ Connection URL generated!\n")
    print("=" * 60)
    print("CLICK THIS LINK TO CONNECT GMAIL:")
    print("=" * 60)
    print(f"\n{connection_request.redirectUrl}\n")
    print("=" * 60)
    print("\nAfter connecting, run your agent again to check emails!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTrying alternative method...")
    
    try:
        # Alternative: Check if there's a different API
        print("\nChecking available methods...")
        methods = [x for x in dir(composio.connected_accounts) if not x.startswith('_')]
        print(f"Available methods: {methods}")
        
    except Exception as e2:
        print(f"❌ Also failed: {e2}")
        print("\n💡 Please use Composio Dashboard:")
        print("   https://platform.composio.dev")
