from composio import Composio
import os
from dotenv import load_dotenv

load_dotenv()

client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

print("Client Dir:")
print([x for x in dir(client) if not x.startswith('_')])

# Check for 'users' or 'entities'
if hasattr(client, 'users'):
    print("Has 'users'")
if hasattr(client, 'entities'):
    print("Has 'entities'")
