"""Check Asana connection details"""
import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

def check_asana():
    """Check Asana connection for the user"""
    print("\n" + "=" * 70)
    print("CHECKING ASANA CONNECTION")
    print("=" * 70)
    
    composio_client = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))
    
    user_id = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"
    print(f"\nUser ID: {user_id}")
    
    # Check all connections for this user
    print("\n1. Checking connections for this user...")
    try:
        connections = composio_client.connected_accounts.list(user_ids=[user_id])
        
        print(f"\n   Found {len(connections.items)} connection(s):")
        for conn in connections.items:
            toolkit = getattr(conn, 'toolkit', None)
            toolkit_slug = getattr(toolkit, 'slug', 'unknown') if toolkit else 'unknown'
            print(f"   - {toolkit_slug}: {conn.status} (ID: {conn.id})")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Check ALL connections (without user filter)
    print("\n2. Checking ALL Asana connections in account...")
    try:
        all_connections = composio_client.connected_accounts.list()
        
        asana_connections = [c for c in all_connections.items 
                            if hasattr(c, 'toolkit') and c.toolkit 
                            and getattr(c.toolkit, 'slug', '').lower() == 'asana']
        
        print(f"\n   Found {len(asana_connections)} Asana connection(s) total:")
        for conn in asana_connections:
            # Try different ways to get entity_id
            entity_id = getattr(conn, 'entity_id', None)
            if not entity_id:
                entity_id = getattr(conn, 'entityId', None)
            if not entity_id:
                entity_id = getattr(conn, 'user_id', None)
            if not entity_id:
                entity_id = getattr(conn, 'userId', None)
            
            print(f"   - Entity: {entity_id or 'unknown'}")
            print(f"     Status: {conn.status}")
            print(f"     ID: {conn.id}")
            print(f"     All attributes: {dir(conn)}")
            print()
            
    except Exception as e:
        print(f"   Error: {e}")
    
    print("=" * 70)

if __name__ == "__main__":
    check_asana()
