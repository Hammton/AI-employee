"""
Debug connections to see all available attributes
"""

import os
from dotenv import load_dotenv
from kernel import AgentKernel

load_dotenv()

def debug_connections():
    """Debug connection objects to see all attributes."""
    print("\n" + "=" * 70)
    print("🔬 DEBUGGING CONNECTIONS")
    print("=" * 70)
    
    user_id = "+254708235245@c.us"
    print(f"\n👤 User: {user_id}")
    
    kernel = AgentKernel(user_id=user_id)
    kernel.setup()
    
    print("\n📋 Connected Accounts Details:")
    try:
        connected_accounts = kernel.composio_client.connected_accounts.list(
            user_ids=[user_id]
        )
        
        for i, account in enumerate(connected_accounts.items, 1):
            print(f"\n🔗 Account #{i}:")
            print(f"   ID: {account.id}")
            print(f"   Status: {account.status}")
            
            # Print ALL attributes
            print(f"\n   All attributes:")
            for attr in dir(account):
                if not attr.startswith('_'):
                    try:
                        value = getattr(account, attr)
                        if not callable(value):
                            print(f"      • {attr}: {value}")
                    except:
                        pass
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    debug_connections()
