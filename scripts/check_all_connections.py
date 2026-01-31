"""
Check all connections for a user to see what's actually connected
"""

import os
from dotenv import load_dotenv
from kernel import AgentKernel

load_dotenv()

def check_all_connections():
    """Check all connections for the user."""
    print("\n" + "=" * 70)
    print("🔍 CHECKING ALL CONNECTIONS")
    print("=" * 70)
    
    user_id = "+254708235245@c.us"
    print(f"\n👤 User: {user_id}")
    
    # Create kernel
    kernel = AgentKernel(user_id=user_id)
    kernel.setup()
    
    print("\n1️⃣ Checking via session.toolkits()...")
    try:
        toolkits = kernel.composio_session.toolkits()
        
        if not toolkits.items:
            print("   ❌ No toolkits found")
        else:
            print(f"   ✅ Found {len(toolkits.items)} toolkit(s):")
            
            for i, toolkit in enumerate(toolkits.items, 1):
                print(f"\n   📦 Toolkit #{i}:")
                print(f"      • Name: {toolkit.name}")
                
                if hasattr(toolkit, 'connection') and toolkit.connection:
                    is_active = getattr(toolkit.connection, 'is_active', False)
                    print(f"      • Is Active: {is_active}")
                    
                    if hasattr(toolkit.connection, 'connected_account'):
                        account = toolkit.connection.connected_account
                        account_id = getattr(account, 'id', 'N/A')
                        print(f"      • Account ID: {account_id}")
                else:
                    print(f"      • Connection: None")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n2️⃣ Checking via connected_accounts.list()...")
    try:
        connected_accounts = kernel.composio_client.connected_accounts.list(
            user_ids=[user_id]
        )
        
        if not connected_accounts.items:
            print("   ❌ No connected accounts found")
        else:
            print(f"   ✅ Found {len(connected_accounts.items)} account(s):")
            
            for i, account in enumerate(connected_accounts.items, 1):
                print(f"\n   🔗 Account #{i}:")
                print(f"      • ID: {account.id}")
                print(f"      • Status: {account.status}")
                
                # Try to get app name
                if hasattr(account, 'app'):
                    print(f"      • App: {account.app}")
                if hasattr(account, 'appName'):
                    print(f"      • App Name: {account.appName}")
                if hasattr(account, 'integration'):
                    print(f"      • Integration: {account.integration}")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3️⃣ Testing specific apps...")
    test_apps = ["asana", "gmail", "googlecalendar", "slack", "github"]
    
    for app in test_apps:
        is_connected = kernel.check_connection(app)
        status = "✅ Connected" if is_connected else "❌ Not Connected"
        print(f"   {status}: {app}")
    
    print("\n" + "=" * 70)
    print("✅ Connection check complete!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        check_all_connections()
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        import traceback
        traceback.print_exc()
