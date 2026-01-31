from composio import Composio
import os
from dotenv import load_dotenv

load_dotenv()

try:
    client = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))
    
    # Try different toolkit names
    candidates = ["BROWSER", "SYSTEMBROWSER", "WEB_BROWSER"]
    
    for toolkit in candidates:
        print(f"Testing toolkit: {toolkit}")
        try:
            tools = client.tools.get(
                user_id="default_user",
                toolkits=[toolkit]
            )
            print(f"  ✓ Found {len(tools)} tools: {[t.name for t in tools[:3]]}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")

except Exception as e:
    print(f"Init failed: {e}")
