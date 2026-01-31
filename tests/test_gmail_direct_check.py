"""Test Gmail connection check directly"""
import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

def test_gmail_connection():
    """Test Gmail connection check"""
    print("\n" + "=" * 70)
    print("TESTING GMAIL CONNECTION CHECK")
    print("=" * 70)
    
    user_id = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"
    print(f"\nUser: {user_id}")
    
    # Create Composio client
    print("\n1. Creating Composio client...")
    composio = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))
    print("   OK Client created")
    
    # List connected accounts
    print("\n2. Listing connected accounts...")
    try:
        connected_accounts = composio.connected_accounts.list(user_ids=[user_id])
        
        print(f"   Found {len(connected_accounts.items)} connected accounts:")
        for account in connected_accounts.items:
            toolkit_slug = getattr(account.toolkit, 'slug', 'unknown') if hasattr(account, 'toolkit') and account.toolkit else 'unknown'
            print(f"   - {toolkit_slug}: status={account.status}, id={account.id}")
            
            # Check if it's Gmail
            if 'gmail' in toolkit_slug.lower() or 'google' in toolkit_slug.lower():
                print(f"     ✅ FOUND GMAIL CONNECTION!")
                print(f"     Toolkit slug: {toolkit_slug}")
                print(f"     Status: {account.status}")
                
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    # Try different name variations
    print("\n3. Testing name variations...")
    variations = ['gmail', 'googlemail', 'google_mail', 'GMAIL', 'GOOGLEMAIL']
    
    for name in variations:
        slug = name.lower().replace(" ", "").replace("_", "")
        print(f"\n   Testing '{name}' -> slug '{slug}':")
        
        # Check if any account matches
        try:
            connected_accounts = composio.connected_accounts.list(user_ids=[user_id])
            found = False
            for account in connected_accounts.items:
                if account.status == "ACTIVE":
                    toolkit_slug = getattr(account.toolkit, 'slug', '').lower() if hasattr(account, 'toolkit') and account.toolkit else ''
                    if toolkit_slug == slug or slug in toolkit_slug or toolkit_slug in slug:
                        print(f"     ✅ MATCH: {toolkit_slug}")
                        found = True
                        break
            
            if not found:
                print(f"     ❌ No match")
        except Exception as e:
            print(f"     ERROR: {e}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_gmail_connection()
