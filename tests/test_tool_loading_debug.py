"""Debug tool loading with detailed logging"""
import os
import logging
from dotenv import load_dotenv
from composio import Composio
from composio_langchain import LangchainProvider

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

def test_tool_loading():
    """Test tool loading with debug output"""
    print("\n" + "=" * 70)
    print("DEBUGGING TOOL LOADING")
    print("=" * 70)
    
    user_id = "86152916787450@lid"
    print(f"\nUser: {user_id}")
    
    # Create Composio client
    print("\n1. Creating Composio client...")
    composio_client = Composio(
        api_key=os.environ.get("COMPOSIO_API_KEY"),
        provider=LangchainProvider()
    )
    
    # Try to get Google Docs tools
    print("\n2. Attempting to get GOOGLEDOCS toolkit tools...")
    try:
        tools = composio_client.tools.get(
            user_id=user_id,
            toolkits=["GOOGLEDOCS"]
        )
        print(f"   [OK] Success! Got {len(tools)} tools")
        for tool in tools[:5]:
            tool_name = tool.name if hasattr(tool, 'name') else str(tool)
            print(f"      - {tool_name}")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Try individual tools
    print("\n3. Attempting to get individual GOOGLEDOCS tools...")
    individual_tools = [
        'GOOGLEDOCS_CREATE_DOCUMENT',
        'GOOGLEDOCS_GET_DOCUMENT',
        'GOOGLEDOCS_LIST_DOCUMENTS',
    ]
    
    for tool_name in individual_tools:
        try:
            tools = composio_client.tools.get(
                user_id=user_id,
                tools=[tool_name]
            )
            if tools:
                print(f"   [OK] {tool_name} - SUCCESS")
            else:
                print(f"   [WARN] {tool_name} - No tools returned")
        except Exception as e:
            print(f"   [ERROR] {tool_name} - ERROR: {e}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_tool_loading()
