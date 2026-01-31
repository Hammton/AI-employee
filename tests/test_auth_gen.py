from composio import Composio
import os
from dotenv import load_dotenv

load_dotenv()

client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
ENTITY_ID = "default_user"

print(f"Testing Auth for Google Calendar for entity: {ENTITY_ID}")

try:
    # Method 1: The one currently in kernel.py (likely old)
    # session = client.create(user_id=ENTITY_ID) 
    # This might not exist on the new client or works differently.
    pass
except Exception as e:
    print(f"Method 1 failed: {e}")

try:
    # Method 2: Using the Entity object (New SDK style)
    entity = client.get_entity(id=ENTITY_ID)
    print("Got entity")
    
    # Try to initiate connection
    # Note: The specific method name might vary. Common ones: initiate_connection, execute_action(auth)
    # Let's inspect tools first? No, we need auth.
    
    # Let's try to get a connection request
    # Based on Composio docs, it might be:
    # connection = entity.initiate_connection(app_name="gmail")
    
    integration = client.get_integration("googlecalendar")
    print("Got integration object")
    
    # Looking for how to connect.
    # Often it is client.connected_accounts.initiate(integration_id=..., entity_id=...)
    
    # Let's try resolving the user first
    # entity = client.users.get(id=ENTITY_ID) # if users exists
    
    # Let's try the most direct internal method for testing
    req = entity.initiate_connection(app_name="googlecalendar")
    print(f"Auth URL: {req.redirectUrl}")

except Exception as e:
    print(f"Method 2 failed: {e}")
    # inspect entity
    try:
        if 'entity' in locals():
            print(f"Entity dir: {[x for x in dir(entity) if not x.startswith('_')]}")
    except:
        pass
