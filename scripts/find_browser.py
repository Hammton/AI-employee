from composio import Composio
import os
from dotenv import load_dotenv

load_dotenv()

client = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))

try:
    toolkits = client.toolkits.list()
    print(f"Total toolkits: {len(toolkits.items)}")
    
    # Filter for browser/web related
    for tk in toolkits.items:
        name = tk.slug.upper()
        if "BROWSER" in name or "WEB" in name or "SEARCH" in name:
            print(f"Candidate: {name}")
            
except Exception as e:
    print(f"Error: {e}")
