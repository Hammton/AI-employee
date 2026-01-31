"""Check what apps are actually connected for the user"""
import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

def check_connections():
    """Check connected apps for user"""
    print("\n" + "=" * 70)
    print("CHECKING USER CONNECTIONS")
    print("=" * 70)
    
    composio_client = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))
    user_id = "+254708235245@c.us"
    
    print(f"\nUser: {user_id}")
    
    try:
        print("\nFetching connected accounts...")
        connected_accounts = composio_client.connected_accounts.list(
            user_ids=[user_id]
        )
        
        print(f"\nFound {len(connected_accounts.items)} accounts:")
        
        for account in connected_accounts.items:
            toolkit_slug = getattr(account.toolkit, 'slug', 'unknown') if hasattr(account, 'toolkit') and account.toolkit else 'unknown'
            print(f"\n   Account ID: {account.id}")
            print(f"   Toolkit: {toolkit_slug}")
            print(f"   Status: {account.status}")
            
            if account.status == "ACTIVE":
                print(f"   ✅ ACTIVE - should be auto-loaded")
            else:
                print(f"   ❌ {account.status} - will not be auto-loaded")
        
        # Get unique ACTIVE toolkit slugs
        active_slugs = set()
        for account in connected_accounts.items:
            if account.status == "ACTIVE" and hasattr(account, 'toolkit') and account.toolkit:
                toolkit_slug = getattr(account.toolkit, 'slug', '').upper()
                if toolkit_slug:
                    active_slugs.add(toolkit_slug)
        
        print(f"\n{'=' * 70}")
        print(f"ACTIVE TOOLKITS TO AUTO-LOAD: {list(active_slugs)}")
        print(f"{'=' * 70}")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_connections()
