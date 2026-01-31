"""Check ALL connections to find Google Docs"""
import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

def check_all_connections():
    """Check all connected accounts"""
    print("\n" + "=" * 70)
    print("CHECKING ALL CONNECTIONS")
    print("=" * 70)
    
    composio_client = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))
    
    try:
        print("\nFetching ALL connected accounts...")
        connected_accounts = composio_client.connected_accounts.list()
        
        print(f"\nFound {len(connected_accounts.items)} total accounts")
        
        # Group by toolkit
        by_toolkit = {}
        for account in connected_accounts.items:
            toolkit_slug = getattr(account.toolkit, 'slug', 'unknown') if hasattr(account, 'toolkit') and account.toolkit else 'unknown'
            if toolkit_slug not in by_toolkit:
                by_toolkit[toolkit_slug] = []
            by_toolkit[toolkit_slug].append(account)
        
        print(f"\nToolkits found: {list(by_toolkit.keys())}")
        
        # Show Google Docs connections
        if 'googledocs' in by_toolkit:
            print(f"\n{'=' * 70}")
            print("GOOGLE DOCS CONNECTIONS:")
            print(f"{'=' * 70}")
            for account in by_toolkit['googledocs']:
                print(f"\n   Account ID: {account.id}")
                print(f"   Entity ID: {account.entity_id if hasattr(account, 'entity_id') else 'N/A'}")
                print(f"   Status: {account.status}")
        else:
            print(f"\n❌ NO GOOGLE DOCS CONNECTIONS FOUND")
        
        # Show all ACTIVE connections
        print(f"\n{'=' * 70}")
        print("ALL ACTIVE CONNECTIONS:")
        print(f"{'=' * 70}")
        for toolkit_slug, accounts in by_toolkit.items():
            active_accounts = [a for a in accounts if a.status == "ACTIVE"]
            if active_accounts:
                print(f"\n{toolkit_slug.upper()}: {len(active_accounts)} active")
                for account in active_accounts:
                    entity_id = account.entity_id if hasattr(account, 'entity_id') else 'N/A'
                    print(f"   - Entity: {entity_id}, Account: {account.id}")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_all_connections()
