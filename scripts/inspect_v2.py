from composio import Composio
import os
from dotenv import load_dotenv

load_dotenv()

client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

print(f"Client: {dir(client)}")

# Check for get_integration or get_toolkit
if hasattr(client, 'get_integration'):
    print("Has get_integration")
    try:
         integ = client.get_integration("googlecalendar")
         print(f"Integration methods: {dir(integ)}")
    except Exception as e:
         print(f"get_integration failed: {e}")

if hasattr(client, 'get_toolkit'):
    print("Has get_toolkit")
