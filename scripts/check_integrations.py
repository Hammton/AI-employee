from composio import Composio
import os
from dotenv import load_dotenv

load_dotenv()

client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

# Check integrations
print("Available client attributes:")
attrs = [x for x in dir(client) if not x.startswith('_')]
print(attrs)

# Try to find googlecalendar integration
if hasattr(client, 'integrations'):
    print("\nHas integrations")
    try:
        # Maybe list all integrations?
        integs = client.integrations.list()
        print(f"Type: {type(integs)}")
    except Exception as e:
        print(f"List failed: {e}")
