"""Inspect the structure of connected account objects"""
import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

def inspect_accounts():
    """Inspect account object structure"""
    print("\n" + "=" * 70)
    print("INSPECTING ACCOUNT STRUCTURE")
    print("=" * 70)
    
    composio_client = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))
    
    try:
        connected_accounts = composio_client.connected_accounts.list()
        
        if connected_accounts.items:
            account = connected_accounts.items[0]
            print(f"\nFirst account attributes:")
            print(f"   Type: {type(account)}")
            print(f"   Dir: {[attr for attr in dir(account) if not attr.startswith('_')]}")
            
            # Try to access various attributes
            attrs_to_check = ['id', 'entity_id', 'entityId', 'user_id', 'userId', 'status', 'toolkit', 'app_name', 'appName']
            print(f"\nAttribute values:")
            for attr in attrs_to_check:
                try:
                    value = getattr(account, attr, 'NOT_FOUND')
                    print(f"   {attr}: {value}")
                except Exception as e:
                    print(f"   {attr}: ERROR - {e}")
            
            # Check if it's a dict-like object
            if hasattr(account, '__dict__'):
                print(f"\n__dict__: {account.__dict__}")
            
            # Try to convert to dict
            try:
                if hasattr(account, 'model_dump'):
                    print(f"\nmodel_dump(): {account.model_dump()}")
                elif hasattr(account, 'dict'):
                    print(f"\ndict(): {account.dict()}")
            except Exception as e:
                print(f"\nCouldn't convert to dict: {e}")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_accounts()
