"""Test calling Composio tools directly"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

from composio import Composio

print("Testing direct tool execution...\n")

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
session = composio.create(user_id="test_user")

print(f"Session ID: {session.session_id}\n")

# Try to execute COMPOSIO_SEARCH_TOOLS directly
print("Calling COMPOSIO_SEARCH_TOOLS for Gmail...")

try:
    # The tool expects specific format
    result = session.execute_tool(
        tool_name="COMPOSIO_SEARCH_TOOLS",
        params={
            "queries": [{"use_case": "read gmail emails"}],
            "session": {"generate_id": False, "session_id": session.session_id}
        }
    )
    
    print("✅ Tool executed!")
    print(f"\nResult type: {type(result)}")
    print(f"\nResult:")
    print(json.dumps(result, indent=2) if isinstance(result, dict) else result)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
